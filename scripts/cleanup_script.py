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

# Initialize colorama
init()


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

        self.cleanup_options = {
            1: "ALL resources (AWS IoT Things, AWS IoT Thing Groups, AWS IoT Thing Types, AWS IoT Software Packages, Amazon S3 Buckets, AWS Identity and Access Management (IAM) Roles)",
            2: "AWS IoT Things only",
            3: "AWS IoT Thing Groups only",
        }

        # Rate limiting semaphores for AWS API limits
        self.thing_deletion_semaphore = Semaphore(80)  # 100 TPS limit, use 80 for safety
        self.static_group_deletion_semaphore = Semaphore(80)  # 100 TPS limit for static groups
        self.dynamic_group_deletion_semaphore = Semaphore(4)  # 5 TPS limit for dynamic groups, use 4 for safety
        self.package_semaphore = Semaphore(8)  # 10 TPS limit for packages
        self.thing_type_semaphore = Semaphore(8)  # 10 TPS limit for thing types

        # Progress tracking
        self.progress_lock = Lock()
        self.deleted_count = 0

    def safe_api_call(self, func, operation_name, resource_name, debug=False, **kwargs):
        """Safely execute AWS API call with error handling and optional debug info"""
        try:
            if debug or self.debug_mode:
                print(f"\n🔍 DEBUG: {operation_name}: {resource_name}")
                print(f"📤 API Call: {func.__name__}")
                print("📥 Input Parameters:")
                print(json.dumps(kwargs, indent=2, default=str))

            response = func(**kwargs)

            if debug or self.debug_mode:
                print("📤 API Response:")
                print(json.dumps(response, indent=2, default=str))

            time.sleep(0.01)  # Rate limiting  # nosemgrep: arbitrary-sleep
            return response
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code in ["ResourceNotFoundException", "ResourceNotFound", "NoSuchBucket", "NoSuchEntity"]:
                if debug or self.debug_mode:
                    print(f"📝 Resource not found: {resource_name}")
                return None
            else:
                if debug or self.debug_mode:
                    print(f"❌ Error in {operation_name} {resource_name}: {e.response['Error']['Message']}")
                    print("🔍 DEBUG: Full error response:")
                    print(json.dumps(e.response, indent=2, default=str))
            time.sleep(0.01)  # nosemgrep: arbitrary-sleep
            return None
        except Exception as e:
            if debug or self.debug_mode:
                print(f"❌ Error: {str(e)}")
                import traceback

                print("🔍 DEBUG: Full traceback:")
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
                print("🔍 DEBUG: Client configuration:")
                print(f"   IoT Service: {self.iot_client.meta.service_model.service_name}")
                print(f"   Data Endpoint: {data_endpoint}")

            return True
        except Exception as e:
            print(f"❌ Error initializing AWS clients: {str(e)}")
            return False

    def print_header(self):
        print(f"{Fore.CYAN}🧹 AWS IoT Cleanup Script (Boto3){Style.RESET_ALL}")
        print(f"{Fore.CYAN}==================================={Style.RESET_ALL}")

        print(f"{Fore.YELLOW}📚 LEARNING GOAL:{Style.RESET_ALL}")
        print(
            f"{Fore.CYAN}This script demonstrates proper AWS IoT Core resource cleanup and lifecycle management.{Style.RESET_ALL}"
        )
        print(
            f"{Fore.CYAN}It shows how to safely delete AWS IoT resources in the correct order, handle dependencies{Style.RESET_ALL}"
        )
        print(
            f"{Fore.CYAN}between services, and avoid orphaned resources. Understanding cleanup is crucial for{Style.RESET_ALL}"
        )
        print(f"{Fore.CYAN}cost management and maintaining a clean AWS environment. This script handles both{Style.RESET_ALL}")
        print(
            f"{Fore.CYAN}Vehicle-VIN-* things and Fleet-based thing groups from the aligned naming convention.{Style.RESET_ALL}\n"
        )

        # Initialize clients and display info
        if not self.initialize_clients():
            sys.exit(1)

        print(f"{Fore.CYAN}📍 Region: {Fore.GREEN}{self.region}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}🆔 Account ID: {Fore.GREEN}{self.account_id}{Style.RESET_ALL}\n")

    def get_debug_mode(self):
        """Ask user for debug mode"""
        print(
            f"{Fore.RED}⚠️  WARNING: Debug mode exposes sensitive information (ARNs, account IDs, API responses){Style.RESET_ALL}"
        )
        choice = (
            input(f"{Fore.YELLOW}🔧 Enable debug mode (show all API calls and responses)? [y/N]: {Style.RESET_ALL}")
            .strip()
            .lower()
        )
        self.debug_mode = choice in ["y", "yes"]

        if self.debug_mode:
            print(f"{Fore.GREEN}✅ Debug mode enabled{Style.RESET_ALL}\n")

    def get_cleanup_choice(self):
        """Get cleanup option from user"""
        print(f"{Fore.YELLOW}🎯 Select cleanup option:{Style.RESET_ALL}")
        for num, description in self.cleanup_options.items():
            print(f"{Fore.CYAN}{num}. {description}{Style.RESET_ALL}")

        while True:
            try:
                choice = int(input(f"{Fore.YELLOW}Enter choice [1-3]: {Style.RESET_ALL}"))
                if 1 <= choice <= 3:
                    return choice
                print(f"{Fore.RED}❌ Invalid choice. Please enter 1-3{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED}❌ Please enter a valid number{Style.RESET_ALL}")
            except KeyboardInterrupt:
                print(f"\n\n{Fore.YELLOW}👋 Cleanup cancelled by user. Goodbye!{Style.RESET_ALL}")
                sys.exit(0)

    def confirm_deletion(self, choice):
        """Confirm deletion with user"""
        print(f"\n{Fore.RED}⚠️  WARNING: This will permanently delete:{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{self.cleanup_options[choice]}{Style.RESET_ALL}")

        confirm = input(f"\n{Fore.YELLOW}Type 'DELETE' to confirm: {Style.RESET_ALL}")
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
                            f"{Fore.GREEN}✅ [{self.deleted_count}/{total}] Deleted thing, shadows, and principals: {Fore.YELLOW}{thing_name}{Style.RESET_ALL}"
                        )
                    return True
                else:
                    print(f"{Fore.RED}❌ Failed to delete thing {thing_name}{Style.RESET_ALL}")
                    return False

            except Exception as e:
                print(f"{Fore.RED}❌ Error deleting thing {thing_name}: {str(e)}{Style.RESET_ALL}")
                return False

            time.sleep(0.0125)  # AWS API rate limiting: 80 TPS for things  # nosemgrep: arbitrary-sleep

    def delete_things(self):
        """Delete all IoT things in parallel"""
        print(f"{Fore.BLUE}🔍 Scanning for AWS IoT Things...{Style.RESET_ALL}")

        # List all things
        all_things = []
        paginator = self.iot_client.get_paginator("list_things")

        for page in paginator.paginate():
            things = page.get("things", [])
            thing_names = [thing["thingName"] for thing in things]
            all_things.extend(thing_names)

        if not all_things:
            print(f"{Fore.YELLOW}ℹ️  No AWS IoT Things found to delete{Style.RESET_ALL}")
            return

        print(f"{Fore.GREEN}📊 Found {len(all_things)} AWS IoT Things to delete{Style.RESET_ALL}")
        print(f"{Fore.BLUE}🚀 Deleting AWS IoT Things in parallel (80 TPS)...{Style.RESET_ALL}")

        self.deleted_count = 0  # Reset counter

        if self.debug_mode:
            print(f"{Fore.BLUE}🔧 Processing things sequentially (debug mode)...{Style.RESET_ALL}")
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
            f"{Fore.CYAN}📊 AWS IoT Things deletion completed: {success_count}/{len(all_things)} successful{Style.RESET_ALL}"
        )

    def delete_single_thing_group(self, group_name, index, total):
        """Delete a single thing group (handles both static and dynamic groups)"""
        try:
            # First, check if it's a dynamic thing group by getting its info
            if self.debug_mode:
                print(f"{Fore.CYAN}🔧 DEBUG - Checking group type: {group_name}{Style.RESET_ALL}")

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
                        print(f"{Fore.CYAN}🔧 DEBUG - Dynamic group detected with query: {query_string}{Style.RESET_ALL}")

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
                                f"{Fore.GREEN}✅ [{self.deleted_count}/{total}] Deleted dynamic thing group: {Fore.YELLOW}{group_name}{Style.RESET_ALL}"
                            )
                        return True
                    else:
                        print(f"{Fore.RED}❌ Failed to delete dynamic thing group: {group_name}{Style.RESET_ALL}")
                        return False

                    time.sleep(0.25)  # AWS API rate limiting: 4 TPS for dynamic groups  # nosemgrep: arbitrary-sleep

            else:
                # This is a static thing group - use 100 TPS limit
                with self.static_group_deletion_semaphore:
                    if self.debug_mode:
                        print(f"{Fore.CYAN}🔧 DEBUG - Static group detected (no queryString){Style.RESET_ALL}")

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
                                f"{Fore.GREEN}✅ [{self.deleted_count}/{total}] Deleted static thing group: {Fore.YELLOW}{group_name}{Style.RESET_ALL}"
                            )
                        return True
                    else:
                        print(f"{Fore.RED}❌ Failed to delete static thing group: {group_name}{Style.RESET_ALL}")
                        return False

                    time.sleep(0.0125)  # AWS API rate limiting: 80 TPS for static groups  # nosemgrep: arbitrary-sleep

        except Exception as e:
            print(f"{Fore.RED}❌ Error deleting thing group {group_name}: {str(e)}{Style.RESET_ALL}")
            return False

    def delete_thing_groups(self):
        """Delete all thing groups in parallel"""
        print(f"{Fore.BLUE}🔍 Scanning for AWS IoT Thing Groups...{Style.RESET_ALL}")

        # List all thing groups
        all_groups = []
        paginator = self.iot_client.get_paginator("list_thing_groups")

        for page in paginator.paginate():
            groups = page.get("thingGroups", [])
            group_names = [group["groupName"] for group in groups]
            all_groups.extend(group_names)

        if not all_groups:
            print(f"{Fore.YELLOW}ℹ️  No AWS IoT Thing Groups found to delete{Style.RESET_ALL}")
            return

        print(f"{Fore.GREEN}📊 Found {len(all_groups)} AWS IoT Thing Groups to delete{Style.RESET_ALL}")
        print(f"{Fore.BLUE}🚀 Deleting AWS IoT Thing Groups in parallel (80 TPS)...{Style.RESET_ALL}")

        self.deleted_count = 0  # Reset counter

        if self.debug_mode:
            print(f"{Fore.BLUE}🔧 Processing groups sequentially (debug mode)...{Style.RESET_ALL}")
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
            f"{Fore.CYAN}📊 AWS IoT Thing Groups deletion completed: {success_count}/{len(all_groups)} successful{Style.RESET_ALL}"
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
                            f"{Fore.YELLOW}⏸️  [{self.deleted_count}/{total}] Deprecated thing type: {Fore.YELLOW}{type_name}{Style.RESET_ALL}"
                        )
                    return True
                else:
                    print(f"{Fore.YELLOW}⚠️  Thing type might already be deprecated: {type_name}{Style.RESET_ALL}")
                    return False
            except Exception as e:
                print(f"{Fore.RED}❌ Error deprecating thing type {type_name}: {str(e)}{Style.RESET_ALL}")
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
                            f"{Fore.GREEN}✅ [{self.deleted_count}/{total}] Deleted thing type: {Fore.YELLOW}{type_name}{Style.RESET_ALL}"
                        )
                    return True
                else:
                    print(f"{Fore.RED}❌ Failed to delete thing type: {type_name}{Style.RESET_ALL}")
                    return False
            except Exception as e:
                print(f"{Fore.RED}❌ Error deleting thing type {type_name}: {str(e)}{Style.RESET_ALL}")
                return False

    def delete_thing_types(self):
        """Delete all thing types in parallel"""
        print(f"{Fore.BLUE}🔍 Scanning for AWS IoT Thing Types...{Style.RESET_ALL}")

        # List all thing types
        all_types = []
        paginator = self.iot_client.get_paginator("list_thing_types")

        for page in paginator.paginate():
            types = page.get("thingTypes", [])
            type_names = [thing_type["thingTypeName"] for thing_type in types]
            all_types.extend(type_names)

        if not all_types:
            print(f"{Fore.YELLOW}ℹ️  No AWS IoT Thing Types found to delete{Style.RESET_ALL}")
            return

        print(f"{Fore.GREEN}📊 Found {len(all_types)} AWS IoT Thing Types to delete{Style.RESET_ALL}")

        # Deprecate thing types first in parallel
        print(f"{Fore.BLUE}🚀 Deprecating AWS IoT Thing Types in parallel...{Style.RESET_ALL}")

        self.deleted_count = 0  # Reset counter

        if self.debug_mode:
            print(f"{Fore.BLUE}🔧 Processing types sequentially (debug mode)...{Style.RESET_ALL}")
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
            f"{Fore.CYAN}📊 AWS IoT Thing Types deprecation completed: {deprecate_success}/{len(all_types)} successful{Style.RESET_ALL}"
        )

        # Wait 5 minutes before deletion
        print(f"{Fore.YELLOW}⏰ Waiting 5 minutes before deleting AWS IoT Thing Types...{Style.RESET_ALL}")
        for remaining in range(300, 0, -30):
            mins, secs = divmod(remaining, 60)
            print(f"{Fore.CYAN}⏳ Time remaining: {mins:02d}:{secs:02d}{Style.RESET_ALL}")
            time.sleep(30)  # AWS thing type deletion wait period  # nosemgrep: arbitrary-sleep

        # Delete thing types in parallel
        print(f"{Fore.BLUE}🚀 Deleting AWS IoT Thing Types in parallel...{Style.RESET_ALL}")

        self.deleted_count = 0  # Reset counter

        if self.debug_mode:
            print(f"{Fore.BLUE}🔧 Processing types sequentially (debug mode)...{Style.RESET_ALL}")
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
            f"{Fore.CYAN}📊 AWS IoT Thing Types deletion completed: {delete_success}/{len(all_types)} successful{Style.RESET_ALL}"
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
                            f"{Fore.GREEN}✅ [{self.deleted_count}/{total}] Deleted package: {Fore.YELLOW}{package_name}{Style.RESET_ALL}"
                        )
                    return True
                else:
                    print(f"{Fore.RED}❌ Failed to delete package: {package_name}{Style.RESET_ALL}")
                    return False

            except Exception as e:
                print(f"{Fore.RED}❌ Error deleting package {package_name}: {str(e)}{Style.RESET_ALL}")
                return False

            time.sleep(0.125)  # AWS API rate limiting: 8 TPS for packages  # nosemgrep: arbitrary-sleep

    def delete_packages(self):
        """Delete IoT software packages in parallel"""
        print(f"{Fore.BLUE}🔍 Scanning for AWS IoT Software Packages...{Style.RESET_ALL}")

        # List all packages
        all_packages = []
        paginator = self.iot_client.get_paginator("list_packages")

        for page in paginator.paginate():
            packages = page.get("packageSummaries", [])
            package_names = [package["packageName"] for package in packages]
            all_packages.extend(package_names)

        if not all_packages:
            print(f"{Fore.YELLOW}ℹ️  No AWS IoT Software Packages found to delete{Style.RESET_ALL}")
            return

        print(f"{Fore.GREEN}📊 Found {len(all_packages)} AWS IoT Software Packages to delete{Style.RESET_ALL}")
        print(f"{Fore.BLUE}🚀 Deleting AWS IoT Software Packages in parallel (8 TPS)...{Style.RESET_ALL}")

        self.deleted_count = 0  # Reset counter

        if self.debug_mode:
            print(f"{Fore.BLUE}🔧 Processing packages sequentially (debug mode)...{Style.RESET_ALL}")
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
            f"{Fore.CYAN}📊 AWS IoT Software Packages deletion completed: {success_count}/{len(all_packages)} successful{Style.RESET_ALL}"
        )

    def delete_single_s3_bucket(self, bucket_name, index, total):
        """Delete a single Amazon S3 bucket with all versions and delete markers"""
        print(f"{Fore.BLUE}🪣 [{index}/{total}] Processing Amazon S3 bucket: {Fore.YELLOW}{bucket_name}{Style.RESET_ALL}")

        try:
            # First, delete all object versions and delete markers
            print("  🗑️  Deleting all object versions and delete markers...")

            # List all object versions
            paginator = self.s3_client.get_paginator("list_object_versions")

            for page in paginator.paginate(Bucket=bucket_name):
                # Delete all versions
                versions = page.get("Versions", [])
                if versions:
                    print(f"    🔄 Deleting {len(versions)} object versions...")
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
                    print(f"    🔄 Deleting {len(delete_markers)} delete markers...")
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
            print("  🗑️  Deleting bucket...")
            delete_response = self.safe_api_call(
                self.s3_client.delete_bucket, "S3 Bucket Delete", bucket_name, debug=self.debug_mode, Bucket=bucket_name
            )

            if delete_response is not None:
                with self.progress_lock:
                    self.deleted_count += 1
                    print(
                        f"{Fore.GREEN}✅ [{self.deleted_count}/{total}] Deleted Amazon S3 bucket: {Fore.YELLOW}{bucket_name}{Style.RESET_ALL}"
                    )
                return True
            else:
                print(f"{Fore.RED}❌ Failed to delete Amazon S3 bucket: {bucket_name}{Style.RESET_ALL}")
                return False

        except Exception as e:
            print(f"{Fore.RED}❌ Failed to delete Amazon S3 bucket: {bucket_name}{Style.RESET_ALL}")
            print(f"  Error: {str(e)}")
            if self.debug_mode:
                import traceback

                traceback.print_exc()
            return False

    def delete_s3_buckets(self):
        """Delete Amazon S3 buckets with iot-firmware prefix for current region only"""
        print(f"{Fore.BLUE}🔍 Scanning for IoT firmware Amazon S3 buckets in current region...{Style.RESET_ALL}")

        # List all buckets and filter for iot-firmware buckets in current region
        buckets_response = self.safe_api_call(
            self.s3_client.list_buckets, "S3 Buckets List", "all buckets", debug=self.debug_mode
        )

        if not buckets_response:
            print(f"{Fore.RED}❌ Failed to list S3 buckets{Style.RESET_ALL}")
            return

        all_buckets = buckets_response.get("Buckets", [])
        iot_buckets = [bucket["Name"] for bucket in all_buckets if bucket["Name"].startswith(f"iot-firmware-{self.region}")]

        if not iot_buckets:
            print(f"{Fore.YELLOW}ℹ️  No IoT firmware buckets found for region {self.region}{Style.RESET_ALL}")
            print(
                f"{Fore.CYAN}💡 Tip: If your buckets are in a different region, set AWS_DEFAULT_REGION environment variable{Style.RESET_ALL}"
            )
            return

        print(f"{Fore.GREEN}📊 Found {len(iot_buckets)} buckets to delete{Style.RESET_ALL}")
        print(f"{Fore.BLUE}🚀 Deleting Amazon S3 buckets in parallel...{Style.RESET_ALL}")

        self.deleted_count = 0  # Reset counter

        if self.debug_mode:
            print(f"{Fore.BLUE}🔧 Processing buckets sequentially (debug mode)...{Style.RESET_ALL}")
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
            f"{Fore.CYAN}📊 Amazon S3 buckets deletion completed: {success_count}/{len(iot_buckets)} successful{Style.RESET_ALL}"
        )

    def delete_iot_jobs_role(self):
        """Delete IoT Jobs IAM role"""
        print(f"{Fore.BLUE}🔍 Deleting AWS IoT Jobs AWS Identity and Access Management (IAM) roles...{Style.RESET_ALL}")

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
            print(f"{Fore.GREEN}✅ AWS IoT Jobs role deleted successfully{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}⚠️  AWS IoT Jobs role might not exist or failed to delete{Style.RESET_ALL}")

    def disable_package_configuration(self):
        """Disable global package configuration for automated shadow updates"""
        print(f"{Fore.BLUE}📦 Disabling AWS IoT Software Package Catalog global configuration...{Style.RESET_ALL}")

        config_response = self.safe_api_call(
            self.iot_client.update_package_configuration,
            "Package Configuration Update",
            "disable version updates",
            debug=self.debug_mode,
            versionUpdateByJobsConfig={"enabled": False},
        )

        if config_response is not None:
            print(f"{Fore.GREEN}✅ AWS IoT Software Package Catalog global configuration disabled{Style.RESET_ALL}")
        else:
            print(
                f"{Fore.YELLOW}⚠️  AWS IoT Software Package Catalog configuration might already be disabled or failed to update{Style.RESET_ALL}"
            )

    def delete_package_config_role(self):
        """Delete package configuration IAM role"""
        print(
            f"{Fore.BLUE}🔍 Deleting AWS IoT Software Package Catalog configuration AWS Identity and Access Management (IAM) roles...{Style.RESET_ALL}"
        )

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
            print(f"{Fore.GREEN}✅ AWS IoT Software Package Catalog config role deleted successfully{Style.RESET_ALL}")
        else:
            print(
                f"{Fore.YELLOW}⚠️  AWS IoT Software Package Catalog config role might not exist or failed to delete{Style.RESET_ALL}"
            )

    def delete_jobs(self):
        """Delete all IoT jobs in parallel"""
        print(f"{Fore.BLUE}🔍 Scanning for AWS IoT Jobs...{Style.RESET_ALL}")

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
            print(f"{Fore.YELLOW}ℹ️  No AWS IoT Jobs found to delete{Style.RESET_ALL}")
            return

        print(f"{Fore.GREEN}📊 Found {len(all_jobs)} AWS IoT Jobs to delete{Style.RESET_ALL}")

        # Process jobs in parallel for better performance
        def delete_single_job(job_id, index, total):
            try:
                print(f"{Fore.BLUE}[{index}/{total}] Processing job: {Fore.YELLOW}{job_id}{Style.RESET_ALL}")

                # Get job status
                job_response = self.safe_api_call(
                    self.iot_client.describe_job, "Job Describe", job_id, debug=False, jobId=job_id
                )

                if job_response:
                    job_status = job_response.get("job", {}).get("status", "UNKNOWN")

                    # Cancel job if not completed/canceled
                    if job_status in ["IN_PROGRESS", "SCHEDULED"]:
                        print(f"  ⏹️  Cancelling job (status: {job_status})...")
                        self.safe_api_call(self.iot_client.cancel_job, "Job Cancel", job_id, debug=False, jobId=job_id)
                        # Brief wait for cancellation to propagate
                        time.sleep(5)  # nosemgrep: arbitrary-sleep

                    # Delete job with force flag  # nosemgrep: arbitrary-sleep
                    print(f"  🗑️  Deleting job: {job_id}")
                    delete_response = self.safe_api_call(
                        self.iot_client.delete_job, "Job Delete", job_id, debug=self.debug_mode, jobId=job_id, force=True
                    )

                    if delete_response is not None:
                        print(f"{Fore.GREEN}✅ Job deleted successfully{Style.RESET_ALL}")
                        return True
                    else:
                        print(f"{Fore.RED}❌ Failed to delete job{Style.RESET_ALL}")
                        return False
                return False
            except Exception as e:
                print(f"{Fore.RED}❌ Error deleting job {job_id}: {str(e)}{Style.RESET_ALL}")
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

        print(f"{Fore.CYAN}📊 AWS IoT Jobs deletion completed: {success_count}/{len(all_jobs)} successful{Style.RESET_ALL}")

    def disable_fleet_indexing(self):
        """Disable Fleet Indexing"""
        print(f"{Fore.BLUE}🔍 Disabling AWS IoT Fleet Indexing...{Style.RESET_ALL}")

        indexing_response = self.safe_api_call(
            self.iot_client.update_indexing_configuration,
            "Indexing Configuration Update",
            "disable fleet indexing",
            debug=self.debug_mode,
            thingIndexingConfiguration={"thingIndexingMode": "OFF"},
            thingGroupIndexingConfiguration={"thingGroupIndexingMode": "OFF"},
        )

        if indexing_response is not None:
            print(f"{Fore.GREEN}✅ AWS IoT Fleet Indexing disabled successfully{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}⚠️  AWS IoT Fleet Indexing might already be disabled or failed to update{Style.RESET_ALL}")

    def run(self):
        """Main execution flow"""
        self.print_header()

        # Get debug mode preference
        self.get_debug_mode()

        choice = self.get_cleanup_choice()

        if not self.confirm_deletion(choice):
            print(f"{Fore.YELLOW}❌ Cleanup cancelled by user{Style.RESET_ALL}")
            sys.exit(0)

        print(f"\n{Fore.RED}🚨 Starting cleanup process...{Style.RESET_ALL}\n")

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

        print(f"\n{Fore.GREEN}🎉 Cleanup completed successfully!{Style.RESET_ALL}")
        print(f"{Fore.CYAN}⏱️  Total execution time: {duration:.2f} seconds{Style.RESET_ALL}")


if __name__ == "__main__":
    cleanup = IoTCleanupBoto3()
    try:
        cleanup.run()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}👋 Cleanup cancelled by user. Goodbye!{Style.RESET_ALL}")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n{Fore.RED}❌ Cleanup failed with error: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)
