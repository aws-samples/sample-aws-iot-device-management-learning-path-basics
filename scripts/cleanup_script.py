#!/usr/bin/env python3

import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock, Semaphore

import boto3
from botocore.exceptions import ClientError
from colorama import Fore, Style, init

# Add i18n to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "i18n"))

from language_selector import get_language
from loader import load_messages

# Initialize colorama
init()

# Global variables for i18n
USER_LANG = "en"
messages = {}


class IoTCleanupBoto3:
    def __init__(self):
        self.region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        self.account_id = None
        self.debug_mode = False

        # AWS clients
        self.iot_client = None
        self.iot_data_client = None
        self.s3_client = None
        self.iam_client = None
        self.sts_client = None

        # Cleanup options will be populated with localized messages

        # Rate limiting semaphores for AWS API limits
        self.thing_deletion_semaphore = Semaphore(80)  # 100 TPS limit, use 80 for safety
        self.static_group_deletion_semaphore = Semaphore(80)  # 100 TPS limit for static groups
        self.dynamic_group_deletion_semaphore = Semaphore(4)  # 5 TPS limit for dynamic groups, use 4 for safety
        self.package_semaphore = Semaphore(8)  # 10 TPS limit for packages
        self.thing_type_semaphore = Semaphore(8)  # 10 TPS limit for thing types

        # Progress tracking
        self.progress_lock = Lock()
        self.deleted_count = 0

    def get_message(self, key, *args):
        """Get localized message with optional formatting"""
        # Handle nested keys like 'warnings.debug_warning'
        if "." in key:
            keys = key.split(".")
            msg = messages
            for k in keys:
                if isinstance(msg, dict) and k in msg:
                    msg = msg[k]
                else:
                    msg = key  # Fallback to key if not found
                    break
        else:
            msg = messages.get(key, key)

        if args and isinstance(msg, str):
            return msg.format(*args)
        return msg

    def safe_api_call(self, func, operation_name, resource_name, debug=False, **kwargs):
        """Safely execute AWS API call with error handling and optional debug info"""
        try:
            if debug or self.debug_mode:
                print(f"\n{self.get_message('debug.debug_operation', operation_name, resource_name)}")
                print(f"{self.get_message('debug.api_call', func.__name__)}")
                print(f"{self.get_message('debug.input_params')}")
                print(json.dumps(kwargs, indent=2, default=str))

            response = func(**kwargs)

            if debug or self.debug_mode:
                print(f"{self.get_message('debug.api_response')}")
                print(json.dumps(response, indent=2, default=str))

            time.sleep(0.01)  # Rate limiting  # nosemgrep: arbitrary-sleep
            return response
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code in ["ResourceNotFoundException", "ResourceNotFound", "NoSuchBucket", "NoSuchEntity"]:
                if debug or self.debug_mode:
                    print(f"{self.get_message('debug.resource_not_found', resource_name)}")
                return None
            else:
                if debug or self.debug_mode:
                    print(f"❌ Error in {operation_name} {resource_name}: {e.response['Error']['Message']}")
                    print(f"{self.get_message('debug.full_error')}")
                    print(json.dumps(e.response, indent=2, default=str))
            time.sleep(0.01)  # nosemgrep: arbitrary-sleep
            return None
        except Exception as e:
            if debug or self.debug_mode:
                print(f"❌ Error: {str(e)}")
                import traceback

                print(f"{self.get_message('debug.full_traceback')}")
                traceback.print_exc()
            time.sleep(0.01)  # nosemgrep: arbitrary-sleep
            return None

    def initialize_clients(self):
        """Initialize AWS clients"""
        try:
            self.iot_client = boto3.client("iot", region_name=self.region)
            self.s3_client = boto3.client("s3", region_name=self.region)
            self.iam_client = boto3.client("iam", region_name=self.region)
            self.sts_client = boto3.client("sts", region_name=self.region)

            # Get account ID
            identity = self.sts_client.get_caller_identity()
            self.account_id = identity["Account"]

            # Get IoT Data endpoint
            endpoint_response = self.iot_client.describe_endpoint(endpointType="iot:Data-ATS")
            data_endpoint = endpoint_response["endpointAddress"]

            # Initialize IoT Data client with endpoint
            self.iot_data_client = boto3.client("iot-data", region_name=self.region, endpoint_url=f"https://{data_endpoint}")

            if self.debug_mode:
                print(f"{self.get_message('status.clients_initialized')}")
                print(f"{self.get_message('status.iot_service', self.iot_client.meta.service_model.service_name)}")
                print(f"{self.get_message('status.data_endpoint', data_endpoint)}")

            return True
        except Exception as e:
            print(f"{self.get_message('errors.client_init_error', str(e))}")
            return False

    def print_header(self):
        print(f"{Fore.CYAN}{self.get_message('title')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('separator')}{Style.RESET_ALL}")

        print(f"{Fore.YELLOW}{self.get_message('learning_goal')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('learning_description')}{Style.RESET_ALL}\n")

        # Initialize clients and display info
        if not self.initialize_clients():
            sys.exit(1)

        print(f"{Fore.CYAN}{self.get_message('region_label')} {Fore.GREEN}{self.region}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('account_id_label')} {Fore.GREEN}{self.account_id}{Style.RESET_ALL}\n")

    def get_debug_mode(self):
        """Ask user for debug mode"""
        print(f"{Fore.RED}{self.get_message('warnings.debug_warning')}{Style.RESET_ALL}")
        choice = input(f"{Fore.YELLOW}{self.get_message('prompts.debug_mode')}{Style.RESET_ALL}").strip().lower()
        self.debug_mode = choice in ["y", "yes"]

        if self.debug_mode:
            print(f"{Fore.GREEN}{self.get_message('status.debug_enabled')}{Style.RESET_ALL}\n")

    def get_cleanup_choice(self):
        """Get cleanup option from user"""
        print(f"{Fore.YELLOW}{self.get_message('ui.cleanup_menu')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('ui.all_resources')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('ui.things_only')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('ui.groups_only')}{Style.RESET_ALL}")

        while True:
            try:
                choice = int(input(f"{Fore.YELLOW}{self.get_message('prompts.cleanup_choice')}{Style.RESET_ALL}"))
                if 1 <= choice <= 3:
                    return choice
                print(f"{Fore.RED}{self.get_message('errors.invalid_choice')}{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED}{self.get_message('errors.invalid_number')}{Style.RESET_ALL}")
            except KeyboardInterrupt:
                print(f"\n\n{Fore.YELLOW}{self.get_message('ui.cancelled')}{Style.RESET_ALL}")
                sys.exit(0)

    def confirm_deletion(self, choice):
        """Confirm deletion with user"""
        print(f"\n{Fore.RED}{self.get_message('warnings.deletion_warning')}{Style.RESET_ALL}")
        if choice == 1:
            option_text = self.get_message("ui.all_resources")[3:]  # Remove "1. " prefix
        elif choice == 2:
            option_text = self.get_message("ui.things_only")[3:]  # Remove "2. " prefix
        else:
            option_text = self.get_message("ui.groups_only")[3:]  # Remove "3. " prefix
        print(f"{Fore.YELLOW}{option_text}{Style.RESET_ALL}")

        confirm = input(f"\n{Fore.YELLOW}{self.get_message('prompts.confirm_deletion')}{Style.RESET_ALL}")
        return confirm == "DELETE"

    def delete_single_thing(self, thing_name, index, total):
        """Delete a single IoT thing with its shadows and principals"""
        with self.thing_deletion_semaphore:
            try:
                # Delete classic shadow first
                try:
                    self.safe_api_call(
                        self.iot_data_client.delete_thing_shadow,
                        "Thing Shadow Delete",
                        f"{thing_name} (classic)",
                        debug=False,
                        thingName=thing_name,
                    )
                except (ClientError, Exception):
                    pass  # Shadow might not exist

                # Delete $package shadow
                try:
                    self.safe_api_call(
                        self.iot_data_client.delete_thing_shadow,
                        "Thing Shadow Delete",
                        f"{thing_name} ($package)",
                        debug=False,
                        thingName=thing_name,
                        shadowName="$package",
                    )
                except (ClientError, Exception):
                    pass  # Shadow might not exist

                # Detach all principals from thing
                principals_response = self.safe_api_call(
                    self.iot_client.list_thing_principals,
                    "Thing Principals List",
                    thing_name,
                    debug=False,
                    thingName=thing_name,
                )

                if principals_response:
                    principals = principals_response.get("principals", [])
                    for principal in principals:
                        self.safe_api_call(
                            self.iot_client.detach_thing_principal,
                            "Thing Principal Detach",
                            f"{thing_name} from {principal}",
                            debug=False,
                            thingName=thing_name,
                            principal=principal,
                        )

                # Delete the thing (AWS automatically removes from all groups)
                delete_response = self.safe_api_call(
                    self.iot_client.delete_thing, "Thing Delete", thing_name, debug=self.debug_mode, thingName=thing_name
                )

                if delete_response is not None:
                    with self.progress_lock:
                        self.deleted_count += 1
                        print(
                            f"{Fore.GREEN}{self.get_message('status.thing_deleted', self.deleted_count, total, thing_name)}{Style.RESET_ALL}"
                        )
                    return True
                else:
                    print(f"{Fore.RED}{self.get_message('errors.failed_delete_thing', thing_name)}{Style.RESET_ALL}")
                    return False

            except Exception as e:
                print(f"{Fore.RED}{self.get_message('errors.error_deleting_thing', thing_name, str(e))}{Style.RESET_ALL}")
                return False

            time.sleep(0.0125)  # AWS API rate limiting: 80 TPS for things  # nosemgrep: arbitrary-sleep

    def delete_things(self):
        """Delete all IoT things in parallel"""
        print(f"{Fore.BLUE}{self.get_message('status.scanning_things')}{Style.RESET_ALL}")

        # List all things
        all_things = []
        paginator = self.iot_client.get_paginator("list_things")

        for page in paginator.paginate():
            things = page.get("things", [])
            thing_names = [thing["thingName"] for thing in things]
            all_things.extend(thing_names)

        if not all_things:
            print(f"{Fore.YELLOW}{self.get_message('results.no_things')}{Style.RESET_ALL}")
            return

        print(f"{Fore.GREEN}{self.get_message('results.found_things', len(all_things))}{Style.RESET_ALL}")
        print(f"{Fore.BLUE}{self.get_message('status.deleting_things')}{Style.RESET_ALL}")

        self.deleted_count = 0  # Reset counter

        if self.debug_mode:
            print(f"{Fore.BLUE}{self.get_message('status.processing_sequential', 'things')}{Style.RESET_ALL}")
            success_count = 0
            for i, thing_name in enumerate(all_things, 1):
                if self.delete_single_thing(thing_name, i, len(all_things)):
                    success_count += 1
        else:
            with ThreadPoolExecutor(max_workers=80) as executor:
                futures = [
                    executor.submit(self.delete_single_thing, thing_name, i, len(all_things))
                    for i, thing_name in enumerate(all_things, 1)
                ]

                success_count = sum(1 for future in as_completed(futures) if future.result())

        print(
            f"{Fore.CYAN}{self.get_message('status.completion_summary', 'AWS IoT Things', success_count, len(all_things))}{Style.RESET_ALL}"
        )

    def delete_single_thing_group(self, group_name, index, total):
        """Delete a single thing group (handles both static and dynamic groups)"""
        try:
            # First, check if it's a dynamic thing group by getting its info
            if self.debug_mode:
                print(f"{Fore.CYAN}{self.get_message('status.checking_group_type', group_name)}{Style.RESET_ALL}")

            describe_response = self.safe_api_call(
                self.iot_client.describe_thing_group,
                "Thing Group Describe",
                group_name,
                debug=False,
                thingGroupName=group_name,
            )

            if not describe_response:
                print(f"{Fore.RED}❌ Failed to describe thing group: {group_name}{Style.RESET_ALL}")
                return False

            # Check if this is a dynamic thing group by looking for queryString
            query_string = describe_response.get("queryString")

            if query_string:
                # This is a dynamic thing group - use 5 TPS limit
                with self.dynamic_group_deletion_semaphore:
                    if self.debug_mode:
                        print(f"{Fore.CYAN}{self.get_message('status.dynamic_group_detected', query_string)}{Style.RESET_ALL}")

                    delete_response = self.safe_api_call(
                        self.iot_client.delete_dynamic_thing_group,
                        "Dynamic Thing Group Delete",
                        group_name,
                        debug=self.debug_mode,
                        thingGroupName=group_name,
                    )

                    if delete_response is not None:
                        with self.progress_lock:
                            self.deleted_count += 1
                            print(
                                f"{Fore.GREEN}{self.get_message('status.group_deleted_dynamic', self.deleted_count, total, group_name)}{Style.RESET_ALL}"
                            )
                        return True
                    else:
                        print(
                            f"{Fore.RED}{self.get_message('errors.failed_delete_group_dynamic', group_name)}{Style.RESET_ALL}"
                        )
                        return False

                    time.sleep(0.25)  # AWS API rate limiting: 4 TPS for dynamic groups  # nosemgrep: arbitrary-sleep

            else:
                # This is a static thing group - use 100 TPS limit
                with self.static_group_deletion_semaphore:
                    if self.debug_mode:
                        print(f"{Fore.CYAN}{self.get_message('status.static_group_detected')}{Style.RESET_ALL}")

                    delete_response = self.safe_api_call(
                        self.iot_client.delete_thing_group,
                        "Thing Group Delete",
                        group_name,
                        debug=self.debug_mode,
                        thingGroupName=group_name,
                    )

                    if delete_response is not None:
                        with self.progress_lock:
                            self.deleted_count += 1
                            print(
                                f"{Fore.GREEN}{self.get_message('status.group_deleted_static', self.deleted_count, total, group_name)}{Style.RESET_ALL}"
                            )
                        return True
                    else:
                        print(
                            f"{Fore.RED}{self.get_message('errors.failed_delete_group_static', group_name)}{Style.RESET_ALL}"
                        )
                        return False

                    time.sleep(0.0125)  # AWS API rate limiting: 80 TPS for static groups  # nosemgrep: arbitrary-sleep

        except Exception as e:
            print(f"{Fore.RED}{self.get_message('errors.error_deleting_group', group_name, str(e))}{Style.RESET_ALL}")
            return False

    def delete_thing_groups(self):
        """Delete all thing groups in parallel"""
        print(f"{Fore.BLUE}{self.get_message('status.scanning_groups')}{Style.RESET_ALL}")

        # List all thing groups
        all_groups = []
        paginator = self.iot_client.get_paginator("list_thing_groups")

        for page in paginator.paginate():
            groups = page.get("thingGroups", [])
            group_names = [group["groupName"] for group in groups]
            all_groups.extend(group_names)

        if not all_groups:
            print(f"{Fore.YELLOW}{self.get_message('results.no_groups')}{Style.RESET_ALL}")
            return

        print(f"{Fore.GREEN}{self.get_message('results.found_groups', len(all_groups))}{Style.RESET_ALL}")
        print(f"{Fore.BLUE}{self.get_message('status.deleting_groups')}{Style.RESET_ALL}")

        self.deleted_count = 0  # Reset counter

        if self.debug_mode:
            print(f"{Fore.BLUE}{self.get_message('status.processing_sequential', 'groups')}{Style.RESET_ALL}")
            success_count = 0
            for i, group_name in enumerate(all_groups, 1):
                if self.delete_single_thing_group(group_name, i, len(all_groups)):
                    success_count += 1
        else:
            with ThreadPoolExecutor(max_workers=min(80, len(all_groups))) as executor:
                futures = [
                    executor.submit(self.delete_single_thing_group, group_name, i, len(all_groups))
                    for i, group_name in enumerate(all_groups, 1)
                ]

                success_count = sum(1 for future in as_completed(futures) if future.result())

        print(
            f"{Fore.CYAN}{self.get_message('status.completion_summary', 'AWS IoT Thing Groups', success_count, len(all_groups))}{Style.RESET_ALL}"
        )

    def deprecate_single_thing_type(self, type_name, index, total):
        """Deprecate a single thing type"""
        with self.thing_type_semaphore:
            try:
                deprecate_response = self.safe_api_call(
                    self.iot_client.deprecate_thing_type,
                    "Thing Type Deprecate",
                    type_name,
                    debug=self.debug_mode,
                    thingTypeName=type_name,
                )

                if deprecate_response is not None:
                    with self.progress_lock:
                        self.deleted_count += 1
                        print(
                            f"{Fore.YELLOW}{self.get_message('status.type_deprecated', self.deleted_count, total, type_name)}{Style.RESET_ALL}"
                        )
                    return True
                else:
                    print(f"{Fore.YELLOW}{self.get_message('errors.type_already_deprecated', type_name)}{Style.RESET_ALL}")
                    return False
            except Exception as e:
                print(f"{Fore.RED}{self.get_message('errors.error_deprecating_type', type_name, str(e))}{Style.RESET_ALL}")
                return False

    def delete_single_thing_type(self, type_name, index, total):
        """Delete a single thing type"""
        with self.thing_type_semaphore:
            try:
                delete_response = self.safe_api_call(
                    self.iot_client.delete_thing_type,
                    "Thing Type Delete",
                    type_name,
                    debug=self.debug_mode,
                    thingTypeName=type_name,
                )

                if delete_response is not None:
                    with self.progress_lock:
                        self.deleted_count += 1
                        print(
                            f"{Fore.GREEN}{self.get_message('status.type_deleted', self.deleted_count, total, type_name)}{Style.RESET_ALL}"
                        )
                    return True
                else:
                    print(f"{Fore.RED}{self.get_message('errors.failed_delete_type', type_name)}{Style.RESET_ALL}")
                    return False
            except Exception as e:
                print(f"{Fore.RED}{self.get_message('errors.error_deleting_type', type_name, str(e))}{Style.RESET_ALL}")
                return False

    def delete_thing_types(self):
        """Delete all thing types in parallel"""
        print(f"{Fore.BLUE}{self.get_message('status.scanning_types')}{Style.RESET_ALL}")

        # List all thing types
        all_types = []
        paginator = self.iot_client.get_paginator("list_thing_types")

        for page in paginator.paginate():
            types = page.get("thingTypes", [])
            type_names = [thing_type["thingTypeName"] for thing_type in types]
            all_types.extend(type_names)

        if not all_types:
            print(f"{Fore.YELLOW}{self.get_message('results.no_types')}{Style.RESET_ALL}")
            return

        print(f"{Fore.GREEN}{self.get_message('results.found_types', len(all_types))}{Style.RESET_ALL}")

        # Deprecate thing types first in parallel
        print(f"{Fore.BLUE}{self.get_message('status.deprecating_types')}{Style.RESET_ALL}")

        self.deleted_count = 0  # Reset counter

        if self.debug_mode:
            print(f"{Fore.BLUE}{self.get_message('status.processing_sequential', 'types')}{Style.RESET_ALL}")
            deprecate_success = 0
            for i, type_name in enumerate(all_types, 1):
                if self.deprecate_single_thing_type(type_name, i, len(all_types)):
                    deprecate_success += 1
        else:
            with ThreadPoolExecutor(max_workers=8) as executor:
                deprecate_futures = [
                    executor.submit(self.deprecate_single_thing_type, type_name, i, len(all_types))
                    for i, type_name in enumerate(all_types, 1)
                ]

                deprecate_success = sum(1 for future in as_completed(deprecate_futures) if future.result())

        print(
            f"{Fore.CYAN}{self.get_message('status.completion_summary', 'AWS IoT Thing Types deprecation', deprecate_success, len(all_types))}{Style.RESET_ALL}"
        )

        # Wait 5 minutes before deletion
        print(f"{Fore.YELLOW}{self.get_message('status.waiting_types')}{Style.RESET_ALL}")
        for remaining in range(300, 0, -30):
            mins, secs = divmod(remaining, 60)
            print(f"{Fore.CYAN}{self.get_message('status.time_remaining', mins, secs)}{Style.RESET_ALL}")
            time.sleep(30)  # AWS thing type deletion wait period  # nosemgrep: arbitrary-sleep

        # Delete thing types in parallel
        print(f"{Fore.BLUE}{self.get_message('status.deleting_types')}{Style.RESET_ALL}")

        self.deleted_count = 0  # Reset counter

        if self.debug_mode:
            print(f"{Fore.BLUE}{self.get_message('status.processing_sequential', 'types')}{Style.RESET_ALL}")
            delete_success = 0
            for i, type_name in enumerate(all_types, 1):
                if self.delete_single_thing_type(type_name, i, len(all_types)):
                    delete_success += 1
        else:
            with ThreadPoolExecutor(max_workers=8) as executor:
                delete_futures = [
                    executor.submit(self.delete_single_thing_type, type_name, i, len(all_types))
                    for i, type_name in enumerate(all_types, 1)
                ]

                delete_success = sum(1 for future in as_completed(delete_futures) if future.result())

        print(
            f"{Fore.CYAN}{self.get_message('status.completion_summary', 'AWS IoT Thing Types deletion', delete_success, len(all_types))}{Style.RESET_ALL}"
        )

    def delete_single_package(self, package_name, index, total):
        """Delete a single IoT package and its versions"""
        with self.package_semaphore:
            try:
                # Delete package versions first
                versions_response = self.safe_api_call(
                    self.iot_client.list_package_versions,
                    "Package Versions List",
                    package_name,
                    debug=False,
                    packageName=package_name,
                )

                if versions_response:
                    versions = versions_response.get("packageVersionSummaries", [])
                    for version in versions:
                        version_name = version.get("versionName")
                        if version_name:
                            self.safe_api_call(
                                self.iot_client.delete_package_version,
                                "Package Version Delete",
                                f"{package_name} v{version_name}",
                                debug=False,
                                packageName=package_name,
                                versionName=version_name,
                            )

                # Delete the package
                delete_response = self.safe_api_call(
                    self.iot_client.delete_package,
                    "Package Delete",
                    package_name,
                    debug=self.debug_mode,
                    packageName=package_name,
                )

                if delete_response is not None:
                    with self.progress_lock:
                        self.deleted_count += 1
                        print(
                            f"{Fore.GREEN}{self.get_message('status.package_deleted', self.deleted_count, total, package_name)}{Style.RESET_ALL}"
                        )
                    return True
                else:
                    print(f"{Fore.RED}{self.get_message('errors.failed_delete_package', package_name)}{Style.RESET_ALL}")
                    return False

            except Exception as e:
                print(f"{Fore.RED}{self.get_message('errors.error_deleting_package', package_name, str(e))}{Style.RESET_ALL}")
                return False

            time.sleep(0.125)  # AWS API rate limiting: 8 TPS for packages  # nosemgrep: arbitrary-sleep

    def delete_packages(self):
        """Delete IoT software packages in parallel"""
        print(f"{Fore.BLUE}{self.get_message('status.scanning_packages')}{Style.RESET_ALL}")

        # List all packages
        all_packages = []
        paginator = self.iot_client.get_paginator("list_packages")

        for page in paginator.paginate():
            packages = page.get("packageSummaries", [])
            package_names = [package["packageName"] for package in packages]
            all_packages.extend(package_names)

        if not all_packages:
            print(f"{Fore.YELLOW}{self.get_message('results.no_packages')}{Style.RESET_ALL}")
            return

        print(f"{Fore.GREEN}{self.get_message('results.found_packages', len(all_packages))}{Style.RESET_ALL}")
        print(f"{Fore.BLUE}{self.get_message('status.deleting_packages')}{Style.RESET_ALL}")

        self.deleted_count = 0  # Reset counter

        if self.debug_mode:
            print(f"{Fore.BLUE}{self.get_message('status.processing_sequential', 'packages')}{Style.RESET_ALL}")
            success_count = 0
            for i, package_name in enumerate(all_packages, 1):
                if self.delete_single_package(package_name, i, len(all_packages)):
                    success_count += 1
        else:
            with ThreadPoolExecutor(max_workers=8) as executor:
                futures = [
                    executor.submit(self.delete_single_package, package_name, i, len(all_packages))
                    for i, package_name in enumerate(all_packages, 1)
                ]

                success_count = sum(1 for future in as_completed(futures) if future.result())

        print(
            f"{Fore.CYAN}{self.get_message('status.completion_summary', 'AWS IoT Software Packages', success_count, len(all_packages))}{Style.RESET_ALL}"
        )

    def delete_single_s3_bucket(self, bucket_name, index, total):
        """Delete a single Amazon S3 bucket with all versions and delete markers"""
        print(f"{Fore.BLUE}{self.get_message('status.processing_bucket', index, total, bucket_name)}{Style.RESET_ALL}")

        try:
            # First, delete all object versions and delete markers
            print(f"  {self.get_message('status.deleting_versions')}")

            # List all object versions
            paginator = self.s3_client.get_paginator("list_object_versions")

            for page in paginator.paginate(Bucket=bucket_name):
                # Delete all versions
                versions = page.get("Versions", [])
                if versions:
                    print(f"    {self.get_message('status.deleting_versions_batch', len(versions))}")
                    delete_keys = [{"Key": obj["Key"], "VersionId": obj["VersionId"]} for obj in versions]

                    # Delete in batches of 1000 (AWS limit)
                    for i in range(0, len(delete_keys), 1000):
                        batch = delete_keys[i : i + 1000]
                        self.safe_api_call(
                            self.s3_client.delete_objects,
                            "S3 Objects Delete",
                            f"{bucket_name} versions batch",
                            debug=False,
                            Bucket=bucket_name,
                            Delete={"Objects": batch},
                        )

                # Delete all delete markers
                delete_markers = page.get("DeleteMarkers", [])
                if delete_markers:
                    print(f"    {self.get_message('status.deleting_markers_batch', len(delete_markers))}")
                    delete_keys = [{"Key": obj["Key"], "VersionId": obj["VersionId"]} for obj in delete_markers]

                    # Delete in batches of 1000 (AWS limit)
                    for i in range(0, len(delete_keys), 1000):
                        batch = delete_keys[i : i + 1000]
                        self.safe_api_call(
                            self.s3_client.delete_objects,
                            "S3 Objects Delete",
                            f"{bucket_name} delete markers batch",
                            debug=False,
                            Bucket=bucket_name,
                            Delete={"Objects": batch},
                        )

            # Delete bucket
            print(f"  {self.get_message('status.deleting_bucket')}")
            delete_response = self.safe_api_call(
                self.s3_client.delete_bucket, "S3 Bucket Delete", bucket_name, debug=self.debug_mode, Bucket=bucket_name
            )

            if delete_response is not None:
                with self.progress_lock:
                    self.deleted_count += 1
                    print(
                        f"{Fore.GREEN}{self.get_message('status.bucket_deleted', self.deleted_count, total, bucket_name)}{Style.RESET_ALL}"
                    )
                return True
            else:
                print(f"{Fore.RED}{self.get_message('errors.failed_delete_bucket', bucket_name)}{Style.RESET_ALL}")
                return False

        except Exception as e:
            print(f"{Fore.RED}{self.get_message('errors.failed_delete_bucket', bucket_name)}{Style.RESET_ALL}")
            print(f"  Error: {str(e)}")
            if self.debug_mode:
                import traceback

                traceback.print_exc()
            return False

    def delete_s3_buckets(self):
        """Delete Amazon S3 buckets with iot-firmware prefix for current region only"""
        print(f"{Fore.BLUE}{self.get_message('status.scanning_buckets')}{Style.RESET_ALL}")

        # List all buckets and filter for iot-firmware buckets in current region
        buckets_response = self.safe_api_call(
            self.s3_client.list_buckets, "S3 Buckets List", "all buckets", debug=self.debug_mode
        )

        if not buckets_response:
            print(f"{Fore.RED}{self.get_message('errors.failed_list_buckets')}{Style.RESET_ALL}")
            return

        all_buckets = buckets_response.get("Buckets", [])
        iot_buckets = [bucket["Name"] for bucket in all_buckets if bucket["Name"].startswith(f"iot-firmware-{self.region}")]

        if not iot_buckets:
            print(f"{Fore.YELLOW}{self.get_message('results.no_buckets', self.region)}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{self.get_message('results.bucket_tip')}{Style.RESET_ALL}")
            return

        print(f"{Fore.GREEN}{self.get_message('results.found_buckets', len(iot_buckets))}{Style.RESET_ALL}")
        print(f"{Fore.BLUE}{self.get_message('status.deleting_buckets')}{Style.RESET_ALL}")

        self.deleted_count = 0  # Reset counter

        if self.debug_mode:
            print(f"{Fore.BLUE}{self.get_message('status.processing_sequential', 'buckets')}{Style.RESET_ALL}")
            success_count = 0
            for i, bucket_name in enumerate(iot_buckets, 1):
                if self.delete_single_s3_bucket(bucket_name, i, len(iot_buckets)):
                    success_count += 1
        else:
            with ThreadPoolExecutor(max_workers=min(10, len(iot_buckets))) as executor:
                futures = [
                    executor.submit(self.delete_single_s3_bucket, bucket_name, i, len(iot_buckets))
                    for i, bucket_name in enumerate(iot_buckets, 1)
                ]

                success_count = sum(1 for future in as_completed(futures) if future.result())

        print(
            f"{Fore.CYAN}{self.get_message('status.completion_summary', 'Amazon S3 buckets', success_count, len(iot_buckets))}{Style.RESET_ALL}"
        )

    def delete_iot_jobs_role(self):
        """Delete IoT Jobs IAM role"""
        print(f"{Fore.BLUE}{self.get_message('status.deleting_iot_roles')}{Style.RESET_ALL}")

        # Try both old and new role naming patterns
        role_names = [
            "IoTJobsRole",  # Legacy name
            f"IoTJobsRole-{self.region}-{self.account_id[:8]}",  # New configurable name
        ]

        for role_name in role_names:
            # Delete inline policy first
            self.safe_api_call(
                self.iam_client.delete_role_policy,
                "IAM Role Policy Delete",
                f"{role_name}/IoTJobsS3Policy",
                debug=self.debug_mode,
                RoleName=role_name,
                PolicyName="IoTJobsS3Policy",
            )

            # Delete role
            delete_response = self.safe_api_call(
                self.iam_client.delete_role, "IAM Role Delete", role_name, debug=self.debug_mode, RoleName=role_name
            )

        if delete_response is not None:
            print(f"{Fore.GREEN}{self.get_message('status.iot_role_deleted')}{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}{self.get_message('errors.iot_role_not_exist')}{Style.RESET_ALL}")

    def disable_package_configuration(self):
        """Disable global package configuration for automated shadow updates"""
        print(f"{Fore.BLUE}{self.get_message('status.disabling_package_config')}{Style.RESET_ALL}")

        config_response = self.safe_api_call(
            self.iot_client.update_package_configuration,
            "Package Configuration Update",
            "disable version updates",
            debug=self.debug_mode,
            versionUpdateByJobsConfig={"enabled": False},
        )

        if config_response is not None:
            print(f"{Fore.GREEN}{self.get_message('status.package_config_disabled')}{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}{self.get_message('errors.package_config_failed')}{Style.RESET_ALL}")

    def delete_package_config_role(self):
        """Delete package configuration IAM role"""
        print(f"{Fore.BLUE}{self.get_message('status.deleting_package_roles')}{Style.RESET_ALL}")

        # Try both old and new role naming patterns
        role_names = [
            "IoTPackageConfigRole",  # Legacy name
            f"IoTPackageConfigRole-{self.region}-{self.account_id[:8]}",  # New configurable name
        ]

        for role_name in role_names:
            # Delete inline policy first
            self.safe_api_call(
                self.iam_client.delete_role_policy,
                "IAM Role Policy Delete",
                f"{role_name}/PackageConfigPolicy",
                debug=self.debug_mode,
                RoleName=role_name,
                PolicyName="PackageConfigPolicy",
            )

            # Delete role
            delete_response = self.safe_api_call(
                self.iam_client.delete_role, "IAM Role Delete", role_name, debug=self.debug_mode, RoleName=role_name
            )

        if delete_response is not None:
            print(f"{Fore.GREEN}{self.get_message('status.package_role_deleted')}{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}{self.get_message('errors.package_role_not_exist')}{Style.RESET_ALL}")

    def delete_jobs(self):
        """Delete all IoT jobs in parallel"""
        print(f"{Fore.BLUE}{self.get_message('status.scanning_jobs')}{Style.RESET_ALL}")

        # Get all jobs (IN_PROGRESS, COMPLETED, CANCELED, etc.)
        statuses = ["IN_PROGRESS", "COMPLETED", "CANCELED", "DELETION_IN_PROGRESS", "SCHEDULED"]
        all_jobs = set()  # Use set to avoid duplicates

        for status in statuses:
            paginator = self.iot_client.get_paginator("list_jobs")
            for page in paginator.paginate(status=status):
                jobs = page.get("jobs", [])
                job_ids = [job["jobId"] for job in jobs]
                all_jobs.update(job_ids)  # Use update for set

        all_jobs = list(all_jobs)  # Convert back to list

        if not all_jobs:
            print(f"{Fore.YELLOW}{self.get_message('results.no_jobs')}{Style.RESET_ALL}")
            return

        print(f"{Fore.GREEN}{self.get_message('results.found_jobs', len(all_jobs))}{Style.RESET_ALL}")

        # Process jobs in parallel for better performance
        def delete_single_job(job_id, index, total):
            try:
                print(f"{Fore.BLUE}{self.get_message('status.processing_job', index, total, job_id)}{Style.RESET_ALL}")

                # Get job status
                job_response = self.safe_api_call(
                    self.iot_client.describe_job, "Job Describe", job_id, debug=False, jobId=job_id
                )

                if job_response:
                    job_status = job_response.get("job", {}).get("status", "UNKNOWN")

                    # Cancel job if not completed/canceled
                    if job_status in ["IN_PROGRESS", "SCHEDULED"]:
                        print(f"  {self.get_message('status.cancelling_job', job_status)}")
                        self.safe_api_call(self.iot_client.cancel_job, "Job Cancel", job_id, debug=False, jobId=job_id)
                        # Brief wait for cancellation to propagate
                        time.sleep(5)  # nosemgrep: arbitrary-sleep

                    # Delete job with force flag  # nosemgrep: arbitrary-sleep
                    print(f"  {self.get_message('status.deleting_job', job_id)}")
                    delete_response = self.safe_api_call(
                        self.iot_client.delete_job, "Job Delete", job_id, debug=self.debug_mode, jobId=job_id, force=True
                    )

                    if delete_response is not None:
                        print(f"{Fore.GREEN}{self.get_message('status.job_deleted')}{Style.RESET_ALL}")
                        return True
                    else:
                        print(f"{Fore.RED}{self.get_message('errors.failed_delete_job')}{Style.RESET_ALL}")
                        return False
                return False
            except Exception as e:
                print(f"{Fore.RED}{self.get_message('errors.error_deleting_job', job_id, str(e))}{Style.RESET_ALL}")
                return False

        if self.debug_mode:
            success_count = 0
            for i, job_id in enumerate(all_jobs, 1):
                if delete_single_job(job_id, i, len(all_jobs)):
                    success_count += 1
        else:
            with ThreadPoolExecutor(max_workers=min(10, len(all_jobs))) as executor:
                futures = [
                    executor.submit(delete_single_job, job_id, i, len(all_jobs)) for i, job_id in enumerate(all_jobs, 1)
                ]
                success_count = sum(1 for future in as_completed(futures) if future.result())

        print(
            f"{Fore.CYAN}{self.get_message('status.completion_summary', 'AWS IoT Jobs', success_count, len(all_jobs))}{Style.RESET_ALL}"
        )

    def disable_fleet_indexing(self):
        """Disable Fleet Indexing"""
        print(f"{Fore.BLUE}{self.get_message('status.disabling_fleet_indexing')}{Style.RESET_ALL}")

        indexing_response = self.safe_api_call(
            self.iot_client.update_indexing_configuration,
            "Indexing Configuration Update",
            "disable fleet indexing",
            debug=self.debug_mode,
            thingIndexingConfiguration={"thingIndexingMode": "OFF"},
            thingGroupIndexingConfiguration={"thingGroupIndexingMode": "OFF"},
        )

        if indexing_response is not None:
            print(f"{Fore.GREEN}{self.get_message('status.fleet_indexing_disabled')}{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}{self.get_message('errors.fleet_indexing_failed')}{Style.RESET_ALL}")

    def run(self):
        """Main execution flow"""
        self.print_header()

        # Get debug mode preference
        self.get_debug_mode()

        choice = self.get_cleanup_choice()

        if not self.confirm_deletion(choice):
            print(f"{Fore.YELLOW}{self.get_message('errors.cleanup_cancelled')}{Style.RESET_ALL}")
            sys.exit(0)

        print(f"\n{Fore.RED}{self.get_message('warnings.starting_cleanup')}{Style.RESET_ALL}\n")

        start_time = time.time()

        if choice == 1:  # ALL resources
            self.delete_things()
            self.delete_thing_groups()
            self.delete_jobs()
            self.delete_packages()
            self.delete_s3_buckets()
            self.disable_package_configuration()
            self.delete_iot_jobs_role()
            self.delete_package_config_role()
            self.disable_fleet_indexing()
            self.delete_thing_types()  # Move to last - takes 5+ minutes
        elif choice == 2:  # Things only
            self.delete_things()
        elif choice == 3:  # Thing Groups only
            self.delete_thing_groups()

        end_time = time.time()
        duration = end_time - start_time

        print(f"\n{Fore.GREEN}{self.get_message('status.cleanup_completed')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('status.execution_time', duration)}{Style.RESET_ALL}")


if __name__ == "__main__":
    # Get user's preferred language
    USER_LANG = get_language()

    # Load messages for this script and language
    messages = load_messages("cleanup_script", USER_LANG)

    cleanup = IoTCleanupBoto3()
    try:
        cleanup.run()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}{cleanup.get_message('ui.cancelled')}{Style.RESET_ALL}")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n{Fore.RED}{cleanup.get_message('errors.cleanup_failed', str(e))}{Style.RESET_ALL}")
        sys.exit(1)
