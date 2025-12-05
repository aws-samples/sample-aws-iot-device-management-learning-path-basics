#!/usr/bin/env python3

import argparse
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock, Semaphore

import boto3
from botocore.exceptions import ClientError
from colorama import Fore, Style, init

# Add repository root and i18n to path
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)
sys.path.append(os.path.join(repo_root, "i18n"))

from language_selector import get_language
from loader import load_messages

# Import new cleanup modules from iot_helpers package
from iot_helpers.cleanup.resource_identifier import ResourceIdentifier
from iot_helpers.utils.dependency_handler import DependencyHandler
from iot_helpers.cleanup.deletion_engine import DeletionEngine
from iot_helpers.cleanup.reporter import CleanupReporter
from iot_helpers.utils.naming_conventions import validate_thing_prefix

# Initialize colorama
init()

# Global variables for i18n
USER_LANG = "en"
messages = {}


class IoTCleanupBoto3:
    def __init__(self, things_prefix="Vehicle-VIN-", dry_run=False):
        self.region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        self.account_id = None
        self.debug_mode = False
        self.things_prefix = things_prefix
        self.dry_run = dry_run

        # AWS clients
        self.iot_client = None
        self.iot_data_client = None
        self.s3_client = None
        self.iam_client = None
        self.sts_client = None

        # New module instances (initialized after clients are ready)
        self.resource_identifier = None
        self.dependency_handler = None
        self.deletion_engine = None
        self.cleanup_reporter = None

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

            # Initialize new module instances now that clients are ready
            self.resource_identifier = ResourceIdentifier(
                iot_client=self.iot_client, s3_client=self.s3_client, iam_client=self.iam_client, debug_mode=self.debug_mode
            )

            self.dependency_handler = DependencyHandler(
                iot_client=self.iot_client,
                s3_client=self.s3_client,
                iam_client=self.iam_client,
                language=USER_LANG,
                debug_mode=self.debug_mode,
            )

            clients_dict = {
                "iot": self.iot_client,
                "iot_data": self.iot_data_client,
                "s3": self.s3_client,
                "iam": self.iam_client,
            }

            self.deletion_engine = DeletionEngine(clients=clients_dict, debug_mode=self.debug_mode, dry_run=self.dry_run)

            self.cleanup_reporter = CleanupReporter(language=USER_LANG)

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
            
            # Update debug mode in all modules
            if self.resource_identifier:
                self.resource_identifier.debug_mode = True
            if self.dependency_handler:
                self.dependency_handler.debug_mode = True
            if self.deletion_engine:
                self.deletion_engine.debug_mode = True

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



    def delete_things(self):
        """Delete all IoT things using new deletion engine"""
        print(f"{Fore.BLUE}{self.get_message('status.scanning_things')}{Style.RESET_ALL}")

        # List all things
        all_things = []
        paginator = self.iot_client.get_paginator("list_things")

        for page in paginator.paginate():
            things = page.get("things", [])
            all_things.extend(things)

        if not all_things:
            print(f"{Fore.YELLOW}{self.get_message('results.no_things')}{Style.RESET_ALL}")
            return {}

        print(f"{Fore.GREEN}{self.get_message('status.found_total_things', len(all_things))}{Style.RESET_ALL}")
        
        if self.dry_run:
            print(f"{Fore.YELLOW}{self.get_message('status.dry_run_things')}{Style.RESET_ALL}")
        
        print(f"{Fore.BLUE}{self.get_message('status.filtering_things')}{Style.RESET_ALL}")

        # Use deletion engine with resource identifier
        stats = self.deletion_engine.delete_resources(
            resources=all_things,
            resource_type="thing",
            identifier=self.resource_identifier,
            dependency_handler=self.dependency_handler,
            custom_prefix=self.things_prefix,
        )

        workshop_things = stats['deleted'] + stats['failed']
        print(
            f"{Fore.CYAN}{self.get_message('status.processed_things', workshop_things, stats['deleted'], stats['failed'])}{Style.RESET_ALL}"
        )
        
        if stats['skipped'] > 0:
            print(f"{Fore.YELLOW}{self.get_message('status.skipped_things', stats['skipped'])}{Style.RESET_ALL}")
        
        return stats



    def delete_thing_groups(self):
        """Delete all thing groups using new deletion engine"""
        print(f"{Fore.BLUE}{self.get_message('status.scanning_groups')}{Style.RESET_ALL}")

        # List all thing groups (both static and dynamic)
        # AWS list_thing_groups returns ALL groups including dynamic ones
        all_groups = []
        
        # Use non-paginated call first to get all groups (including dynamic)
        try:
            response = self.iot_client.list_thing_groups(maxResults=250)
            groups = response.get("thingGroups", [])
            all_groups.extend(groups)
            
            # Handle pagination if there are more groups
            next_token = response.get("nextToken")
            while next_token:
                response = self.iot_client.list_thing_groups(maxResults=250, nextToken=next_token)
                groups = response.get("thingGroups", [])
                all_groups.extend(groups)
                next_token = response.get("nextToken")
                
        except Exception as e:
            if self.debug_mode:
                print(f"[DEBUG] Error listing thing groups: {str(e)}")
            # Fall back to paginator
            paginator = self.iot_client.get_paginator("list_thing_groups")
            for page in paginator.paginate():
                groups = page.get("thingGroups", [])
                all_groups.extend(groups)

        if not all_groups:
            print(f"{Fore.YELLOW}{self.get_message('results.no_groups')}{Style.RESET_ALL}")
            return {}

        if self.debug_mode:
            print(f"[DEBUG] Raw groups from API: {[g.get('groupName') for g in all_groups]}")

        print(f"{Fore.GREEN}{self.get_message('status.found_total_groups', len(all_groups))}{Style.RESET_ALL}")
        
        if self.dry_run:
            print(f"{Fore.YELLOW}{self.get_message('status.dry_run_groups')}{Style.RESET_ALL}")
        
        print(f"{Fore.BLUE}{self.get_message('status.filtering_groups')}{Style.RESET_ALL}")

        # Use deletion engine with resource identifier
        stats = self.deletion_engine.delete_resources(
            resources=all_groups,
            resource_type="thing-group",
            identifier=self.resource_identifier,
            dependency_handler=self.dependency_handler,
        )

        workshop_groups = stats['deleted'] + stats['failed']
        print(
            f"{Fore.CYAN}{self.get_message('status.processed_groups', workshop_groups, stats['deleted'], stats['failed'])}{Style.RESET_ALL}"
        )
        
        if stats['skipped'] > 0:
            print(f"{Fore.YELLOW}{self.get_message('status.skipped_groups', stats['skipped'])}{Style.RESET_ALL}")
        
        return stats



    def delete_thing_types(self):
        """Delete all thing types using new deletion engine (with deprecation and wait)"""
        print(f"{Fore.BLUE}{self.get_message('status.scanning_types')}{Style.RESET_ALL}")

        # List all thing types
        all_types = []
        paginator = self.iot_client.get_paginator("list_thing_types")

        for page in paginator.paginate():
            types = page.get("thingTypes", [])
            all_types.extend(types)

        if not all_types:
            print(f"{Fore.YELLOW}{self.get_message('results.no_types')}{Style.RESET_ALL}")
            return {}

        print(f"{Fore.GREEN}{self.get_message('results.found_types', len(all_types))}{Style.RESET_ALL}")

        # First, identify which thing types are workshop resources
        print(f"{Fore.BLUE}{self.get_message('status.identifying_types')}{Style.RESET_ALL}")
        workshop_types = []
        
        for thing_type in all_types:
            is_workshop, identification_method = self.resource_identifier.identify_resource(
                thing_type, "thing-type", None
            )
            
            if is_workshop:
                workshop_types.append(thing_type)
                if self.debug_mode:
                    type_name = thing_type.get("thingTypeName")
                    print(f"[DEBUG] Identified workshop thing type: {type_name} (method: {identification_method})")
        
        if not workshop_types:
            print(f"{Fore.YELLOW}{self.get_message('status.no_workshop_types')}{Style.RESET_ALL}")
            return {
                "total": len(all_types),
                "deleted": 0,
                "skipped": len(all_types),
                "failed": 0,
                "skipped_resources": [t.get("thingTypeName") for t in all_types]
            }
        
        print(f"{Fore.GREEN}{self.get_message('status.found_workshop_types', len(workshop_types), len(all_types))}{Style.RESET_ALL}")
        
        if self.dry_run:
            print(f"{Fore.YELLOW}{self.get_message('status.dry_run_types', len(workshop_types))}{Style.RESET_ALL}")
            for thing_type in workshop_types:
                type_name = thing_type.get("thingTypeName")
                print(f"{Fore.CYAN}  - {type_name}{Style.RESET_ALL}")
            
            return {
                "total": len(all_types),
                "deleted": 0,
                "skipped": len(all_types) - len(workshop_types),
                "failed": 0,
                "skipped_resources": [t.get("thingTypeName") for t in all_types if t not in workshop_types]
            }

        # Deprecate ONLY workshop thing types
        print(f"{Fore.BLUE}{self.get_message('status.deprecating_types')}{Style.RESET_ALL}")
        deprecated_count = 0
        
        for thing_type in workshop_types:
            type_name = thing_type.get("thingTypeName")
            if type_name:
                result = self.safe_api_call(
                    self.iot_client.deprecate_thing_type,
                    "Thing Type Deprecate",
                    type_name,
                    debug=self.debug_mode,
                    thingTypeName=type_name,
                )
                if result is not None:
                    deprecated_count += 1

        print(f"{Fore.CYAN}{self.get_message('status.deprecated_types', deprecated_count)}{Style.RESET_ALL}")

        # Wait 5 minutes before deletion (AWS requirement)
        print(f"{Fore.YELLOW}{self.get_message('status.waiting_types')}{Style.RESET_ALL}")
        for remaining in range(300, 0, -30):
            mins, secs = divmod(remaining, 60)
            print(f"{Fore.CYAN}{self.get_message('status.time_remaining', mins, secs)}{Style.RESET_ALL}")
            time.sleep(30)  # AWS thing type deletion wait period  # nosemgrep: arbitrary-sleep

        # Delete thing types using deletion engine
        print(f"{Fore.BLUE}{self.get_message('status.deleting_types')}{Style.RESET_ALL}")

        stats = self.deletion_engine.delete_resources(
            resources=workshop_types,  # Only delete workshop types
            resource_type="thing-type",
            identifier=self.resource_identifier,
            dependency_handler=self.dependency_handler,
        )
        
        # Adjust stats to account for all types scanned
        stats['total'] = len(all_types)
        stats['skipped'] = len(all_types) - len(workshop_types)
        stats['skipped_resources'] = [t.get("thingTypeName") for t in all_types if t not in workshop_types]

        print(
            f"{Fore.CYAN}{self.get_message('status.completion_summary', 'AWS IoT Thing Types', stats['deleted'], len(workshop_types))}{Style.RESET_ALL}"
        )
        
        if stats['skipped'] > 0:
            print(f"{Fore.YELLOW}{self.get_message('status.skipped_types', stats['skipped'])}{Style.RESET_ALL}")
        
        return stats



    def delete_packages(self):
        """Delete IoT software packages using new deletion engine"""
        print(f"{Fore.BLUE}{self.get_message('status.scanning_packages')}{Style.RESET_ALL}")

        # List all packages
        all_packages = []
        paginator = self.iot_client.get_paginator("list_packages")

        for page in paginator.paginate():
            packages = page.get("packageSummaries", [])
            all_packages.extend(packages)

        if not all_packages:
            print(f"{Fore.YELLOW}{self.get_message('results.no_packages')}{Style.RESET_ALL}")
            return {}

        print(f"{Fore.GREEN}{self.get_message('status.found_total_packages', len(all_packages))}{Style.RESET_ALL}")
        
        if self.dry_run:
            print(f"{Fore.YELLOW}{self.get_message('status.dry_run_packages')}{Style.RESET_ALL}")
        
        print(f"{Fore.BLUE}{self.get_message('status.filtering_packages')}{Style.RESET_ALL}")

        # Use deletion engine with resource identifier
        stats = self.deletion_engine.delete_resources(
            resources=all_packages,
            resource_type="package",
            identifier=self.resource_identifier,
            dependency_handler=self.dependency_handler,
        )

        workshop_packages = stats['deleted'] + stats['failed']
        print(
            f"{Fore.CYAN}{self.get_message('status.processed_packages', workshop_packages, stats['deleted'], stats['failed'])}{Style.RESET_ALL}"
        )
        
        if stats['skipped'] > 0:
            print(f"{Fore.YELLOW}{self.get_message('status.skipped_packages', stats['skipped'])}{Style.RESET_ALL}")
        
        return stats



    def delete_s3_buckets(self):
        """Delete Amazon S3 buckets using new deletion engine"""
        print(f"{Fore.BLUE}{self.get_message('status.scanning_buckets')}{Style.RESET_ALL}")

        # List all buckets and filter for iot-firmware buckets in current region
        buckets_response = self.safe_api_call(
            self.s3_client.list_buckets, "S3 Buckets List", "all buckets", debug=self.debug_mode
        )

        if not buckets_response:
            print(f"{Fore.RED}{self.get_message('errors.failed_list_buckets')}{Style.RESET_ALL}")
            return {}

        all_buckets = buckets_response.get("Buckets", [])
        iot_buckets = [bucket for bucket in all_buckets if bucket["Name"].startswith(f"iot-firmware-{self.region}")]

        if not iot_buckets:
            print(f"{Fore.YELLOW}{self.get_message('results.no_buckets', self.region)}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{self.get_message('results.bucket_tip')}{Style.RESET_ALL}")
            return {}

        print(f"{Fore.GREEN}{self.get_message('results.found_buckets', len(iot_buckets))}{Style.RESET_ALL}")
        
        if self.dry_run:
            print(f"{Fore.YELLOW}{self.get_message('status.dry_run_buckets')}{Style.RESET_ALL}")
        
        print(f"{Fore.BLUE}{self.get_message('status.deleting_buckets')}{Style.RESET_ALL}")

        # Use deletion engine with resource identifier
        stats = self.deletion_engine.delete_resources(
            resources=iot_buckets,
            resource_type="s3-bucket",
            identifier=self.resource_identifier,
            dependency_handler=self.dependency_handler,
        )

        print(
            f"{Fore.CYAN}{self.get_message('status.completion_summary', 'Amazon S3 buckets', stats['deleted'], stats['total'])}{Style.RESET_ALL}"
        )
        
        if stats['skipped'] > 0:
            print(f"{Fore.YELLOW}{self.get_message('status.skipped_buckets', stats['skipped'])}{Style.RESET_ALL}")
        
        return stats

    def delete_iot_jobs_role(self):
        """Delete IoT Jobs IAM role using new deletion engine"""
        print(f"{Fore.BLUE}{self.get_message('status.deleting_iot_roles')}{Style.RESET_ALL}")

        # Try both old and new role naming patterns
        role_names = [
            {"RoleName": "IoTJobsRole"},  # Legacy name
            {"RoleName": f"IoTJobsRole-{self.region}-{self.account_id[:8]}"},  # New configurable name
        ]

        if self.dry_run:
            print(f"{Fore.YELLOW}{self.get_message('status.dry_run_roles')}{Style.RESET_ALL}")

        # Use deletion engine with resource identifier
        stats = self.deletion_engine.delete_resources(
            resources=role_names,
            resource_type="iam-role",
            identifier=self.resource_identifier,
            dependency_handler=self.dependency_handler,
        )

        if stats['deleted'] > 0:
            print(f"{Fore.GREEN}{self.get_message('status.iot_role_deleted')}{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}{self.get_message('errors.iot_role_not_exist')}{Style.RESET_ALL}")
        
        return stats

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
        """Delete package configuration IAM role using new deletion engine"""
        print(f"{Fore.BLUE}{self.get_message('status.deleting_package_roles')}{Style.RESET_ALL}")

        # Try both old and new role naming patterns
        role_names = [
            {"RoleName": "IoTPackageConfigRole"},  # Legacy name
            {"RoleName": f"IoTPackageConfigRole-{self.region}-{self.account_id[:8]}"},  # New configurable name
        ]

        if self.dry_run:
            print(f"{Fore.YELLOW}{self.get_message('status.dry_run_roles')}{Style.RESET_ALL}")

        # Use deletion engine with resource identifier
        stats = self.deletion_engine.delete_resources(
            resources=role_names,
            resource_type="iam-role",
            identifier=self.resource_identifier,
            dependency_handler=self.dependency_handler,
        )

        if stats['deleted'] > 0:
            print(f"{Fore.GREEN}{self.get_message('status.package_role_deleted')}{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}{self.get_message('errors.package_role_not_exist')}{Style.RESET_ALL}")
        
        return stats

    def delete_commands(self):
        """Delete all IoT commands using new deletion engine"""
        print(f"{Fore.BLUE}{self.get_message('status.scanning_commands')}{Style.RESET_ALL}")

        # List all commands
        all_commands = []
        try:
            # Note: AWS IoT Commands API may vary by region/availability
            # Using list_commands if available
            paginator = self.iot_client.get_paginator("list_commands")
            for page in paginator.paginate():
                commands = page.get("commands", [])
                all_commands.extend(commands)
        except (ClientError, AttributeError) as e:
            # Commands API might not be available in all regions or accounts
            if self.debug_mode:
                print(f"{Fore.YELLOW}Commands API not available or no commands found: {str(e)}{Style.RESET_ALL}")
            return {}

        if not all_commands:
            print(f"{Fore.YELLOW}{self.get_message('results.no_commands')}{Style.RESET_ALL}")
            return {}

        print(f"{Fore.GREEN}{self.get_message('status.found_total_commands', len(all_commands))}{Style.RESET_ALL}")
        
        if self.dry_run:
            print(f"{Fore.YELLOW}{self.get_message('status.dry_run_commands')}{Style.RESET_ALL}")
        
        print(f"{Fore.BLUE}{self.get_message('status.filtering_commands')}{Style.RESET_ALL}")

        # Use deletion engine with resource identifier
        stats = self.deletion_engine.delete_resources(
            resources=all_commands,
            resource_type="command",
            identifier=self.resource_identifier,
            dependency_handler=self.dependency_handler,
        )

        workshop_commands = stats['deleted'] + stats['failed']
        print(
            f"{Fore.CYAN}{self.get_message('status.processed_commands', workshop_commands, stats['deleted'], stats['failed'])}{Style.RESET_ALL}"
        )
        
        if stats['skipped'] > 0:
            print(f"{Fore.YELLOW}{self.get_message('status.skipped_commands', stats['skipped'])}{Style.RESET_ALL}")
        
        return stats

    def delete_jobs(self):
        """Delete all IoT jobs using new deletion engine"""
        print(f"{Fore.BLUE}{self.get_message('status.scanning_jobs')}{Style.RESET_ALL}")

        # Get all jobs (IN_PROGRESS, COMPLETED, CANCELED, etc.)
        statuses = ["IN_PROGRESS", "COMPLETED", "CANCELED", "DELETION_IN_PROGRESS", "SCHEDULED"]
        all_jobs = []
        seen_job_ids = set()  # Track unique job IDs

        for status in statuses:
            paginator = self.iot_client.get_paginator("list_jobs")
            for page in paginator.paginate(status=status):
                jobs = page.get("jobs", [])
                for job in jobs:
                    if job["jobId"] not in seen_job_ids:
                        all_jobs.append(job)
                        seen_job_ids.add(job["jobId"])

        if not all_jobs:
            print(f"{Fore.YELLOW}{self.get_message('results.no_jobs')}{Style.RESET_ALL}")
            return {}

        print(f"{Fore.GREEN}{self.get_message('status.found_total_jobs', len(all_jobs))}{Style.RESET_ALL}")
        
        if self.dry_run:
            print(f"{Fore.YELLOW}{self.get_message('status.dry_run_jobs')}{Style.RESET_ALL}")
        
        print(f"{Fore.BLUE}{self.get_message('status.filtering_jobs')}{Style.RESET_ALL}")

        # Use deletion engine with resource identifier
        stats = self.deletion_engine.delete_resources(
            resources=all_jobs,
            resource_type="job",
            identifier=self.resource_identifier,
            dependency_handler=self.dependency_handler,
        )

        workshop_jobs = stats['deleted'] + stats['failed']
        print(
            f"{Fore.CYAN}{self.get_message('status.processed_jobs', workshop_jobs, stats['deleted'], stats['failed'])}{Style.RESET_ALL}"
        )
        
        if stats['skipped'] > 0:
            print(f"{Fore.YELLOW}{self.get_message('status.skipped_jobs', stats['skipped'])}{Style.RESET_ALL}")
        
        return stats

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

        if self.dry_run:
            print(f"{Fore.YELLOW}{'='*60}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}DRY RUN MODE - No resources will be deleted{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}{'='*60}{Style.RESET_ALL}\n")

        start_time = time.time()

        # Collect statistics from all deletion operations
        all_stats = {}

        if choice == 1:  # ALL resources
            all_stats['things'] = self.delete_things()
            all_stats['thing_groups'] = self.delete_thing_groups()
            all_stats['commands'] = self.delete_commands()
            all_stats['jobs'] = self.delete_jobs()
            all_stats['packages'] = self.delete_packages()
            all_stats['s3_buckets'] = self.delete_s3_buckets()
            self.disable_package_configuration()
            all_stats['iot_jobs_role'] = self.delete_iot_jobs_role()
            all_stats['package_config_role'] = self.delete_package_config_role()
            self.disable_fleet_indexing()
            all_stats['thing_types'] = self.delete_thing_types()  # Move to last - takes 5+ minutes
        elif choice == 2:  # Things only
            all_stats['things'] = self.delete_things()
        elif choice == 3:  # Thing Groups only
            all_stats['thing_groups'] = self.delete_thing_groups()

        end_time = time.time()
        duration = end_time - start_time

        # Use cleanup reporter for summary
        print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        self.cleanup_reporter.report_summary(all_stats, dry_run=self.dry_run)
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")

        print(f"\n{Fore.GREEN}{self.get_message('status.cleanup_completed')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('status.execution_time', duration)}{Style.RESET_ALL}")


if __name__ == "__main__":
    # Get user's preferred language
    USER_LANG = get_language()

    # Load messages for this script and language
    messages = load_messages("cleanup_script", USER_LANG)

    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Clean up AWS IoT Device Management workshop resources")
    parser.add_argument(
        "--things-prefix",
        type=str,
        default="Vehicle-VIN-",
        help="Prefix used for thing names (default: Vehicle-VIN-). Must be alphanumeric with hyphens, underscores, or colons, max 20 characters.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Preview which resources would be deleted without actually deleting them",
    )
    args = parser.parse_args()

    # Validate things prefix
    if not validate_thing_prefix(args.things_prefix):
        print(f"{Fore.RED}Error: Invalid thing prefix '{args.things_prefix}'{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Thing prefix must:{Style.RESET_ALL}")
        print(f"  - Contain only alphanumeric characters, hyphens, underscores, or colons")
        print(f"  - Be no longer than 20 characters")
        print(f"  - Not be empty")
        sys.exit(1)

    cleanup = IoTCleanupBoto3(things_prefix=args.things_prefix, dry_run=args.dry_run)
    try:
        cleanup.run()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}{cleanup.get_message('ui.cancelled')}{Style.RESET_ALL}")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n{Fore.RED}{cleanup.get_message('errors.cleanup_failed', str(e))}{Style.RESET_ALL}")
        sys.exit(1)
