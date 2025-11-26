#!/usr/bin/env python3

import json
import os
import sys
import time
from threading import Semaphore

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


class IoTJobCreator:
    def __init__(self):
        self.region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        self.account_id = None
        self.debug_mode = False
        self.job_config = {}
        self.iot_client = None
        self.sts_client = None

        # Rate limiting semaphore
        self.api_semaphore = Semaphore(10)

    def get_message(self, key, *args):
        """Get localized message with optional formatting"""
        # Handle dot notation for nested keys
        keys = key.split('.')
        msg = messages
        for k in keys:
            if isinstance(msg, dict) and k in msg:
                msg = msg[k]
            else:
                msg = key  # Fallback to key if not found
                break
        
        if args and isinstance(msg, str):
            return msg.format(*args)
        return msg

    def safe_api_call(self, func, operation_name, resource_name, debug=False, **kwargs):
        """Safely execute AWS API call with error handling and optional debug info"""
        try:
            if debug or self.debug_mode:
                print(f"\n{self.get_message('debug.debug_operation', operation_name, resource_name)}")
                print(f"{self.get_message('debug.api_call', func.__name__)}")
                print(self.get_message('debug.input_params'))
                print(json.dumps(kwargs, indent=2, default=str))

            response = func(**kwargs)

            if debug or self.debug_mode:
                print(self.get_message('debug.api_response'))
                print(json.dumps(response, indent=2, default=str))

            time.sleep(0.1)  # Rate limiting  # nosemgrep: arbitrary-sleep
            return response
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code in ["ResourceNotFoundException", "ResourceNotFound"]:
                if debug or self.debug_mode:
                    print(f"{self.get_message('debug.resource_not_found', resource_name)}")
                return None
            else:
                print(f"{self.get_message('errors.api_error', operation_name, resource_name, e.response['Error']['Message'])}")
                if debug or self.debug_mode:
                    print(self.get_message('debug.full_error'))
                    print(json.dumps(e.response, indent=2, default=str))
            time.sleep(0.1)  # nosemgrep: arbitrary-sleep
            return None
        except Exception as e:
            print(f"{self.get_message('errors.general_error', str(e))}")
            if debug or self.debug_mode:
                import traceback

                print(self.get_message('debug.full_traceback'))
                traceback.print_exc()
            time.sleep(0.1)  # nosemgrep: arbitrary-sleep
            return None

    def initialize_clients(self):
        """Initialize AWS clients"""
        try:
            self.iot_client = boto3.client("iot", region_name=self.region)
            self.sts_client = boto3.client("sts", region_name=self.region)

            # Get account ID
            identity = self.sts_client.get_caller_identity()
            self.account_id = identity["Account"]

            if self.debug_mode:
                print(self.get_message('status.clients_initialized'))
                print(f"{self.get_message('status.iot_service', self.iot_client.meta.service_model.service_name)}")
                print(f"{self.get_message('status.api_version', self.iot_client.meta.service_model.api_version)}")

            return True
        except Exception as e:
            print(f"{self.get_message('errors.client_init_error', str(e))}")
            return False

    def print_header(self):
        print(f"{Fore.CYAN}{self.get_message('title')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('separator')}{Style.RESET_ALL}")

        # Initialize clients and display info
        if not self.initialize_clients():
            sys.exit(1)

        print(f"{Fore.BLUE}{self.get_message('aws_config')}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{self.get_message('account_id_label', self.account_id)}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{self.get_message('region_label', self.region)}{Style.RESET_ALL}")
        print()

        print(f"{Fore.YELLOW}{self.get_message('learning_goal')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('learning_description')}{Style.RESET_ALL}\n")

    def get_debug_mode(self):
        """Ask user for debug mode"""
        print(
            f"{Fore.RED}{self.get_message('warnings.debug_warning')}{Style.RESET_ALL}"
        )
        choice = (
            input(f"{Fore.YELLOW}{self.get_message('prompts.debug_mode')}{Style.RESET_ALL}")
            .strip()
            .lower()
        )
        self.debug_mode = choice in ["y", "yes"]

        if self.debug_mode:
            print(f"{Fore.GREEN}{self.get_message('status.debug_enabled')}{Style.RESET_ALL}\n")

    def get_thing_groups(self):
        """Get available thing groups using efficient pagination"""
        print(f"{Fore.BLUE}{self.get_message('status.scanning_groups')}{Style.RESET_ALL}")

        group_names = []
        paginator = self.iot_client.get_paginator("list_thing_groups")

        try:
            for page in paginator.paginate():
                groups = page.get("thingGroups", [])
                page_group_names = [group.get("groupName") for group in groups if group.get("groupName")]
                group_names.extend(page_group_names)
        except Exception as e:
            print(f"{Fore.RED}{self.get_message('errors.failed_list_groups', str(e))}{Style.RESET_ALL}")
            return []

        if group_names:
            print(f"{Fore.GREEN}{self.get_message('ui.available_groups')}{Style.RESET_ALL}")
            for i, group_name in enumerate(group_names, 1):
                print(f"{Fore.CYAN}{i}. {group_name}{Style.RESET_ALL}")

        return group_names

    def get_packages(self):
        """Get available IoT packages"""
        print(f"{Fore.BLUE}{self.get_message('status.scanning_packages')}{Style.RESET_ALL}")

        response = self.safe_api_call(self.iot_client.list_packages, "Package List", "all packages", debug=self.debug_mode)

        if not response:
            print(f"{Fore.RED}{self.get_message('errors.failed_list_packages')}{Style.RESET_ALL}")
            return []

        packages = response.get("packageSummaries", [])
        valid_packages = [pkg for pkg in packages if pkg.get("packageName")]
        package_names = [pkg.get("packageName") for pkg in valid_packages]

        if package_names:
            print(f"{Fore.GREEN}{self.get_message('ui.available_packages')}{Style.RESET_ALL}")
            for i, pkg in enumerate(valid_packages, 1):
                pkg_name = pkg.get("packageName")
                created_date = pkg.get("creationDate", "Unknown")
                print(f"{Fore.CYAN}{i}. {pkg_name} {self.get_message('results.created_date', created_date)}{Style.RESET_ALL}")

        return package_names

    def select_thing_groups(self, available_groups):
        """Let user select thing groups (single number or comma-separated list)"""
        if not available_groups:
            print(f"{Fore.RED}{self.get_message('errors.no_groups_available')}{Style.RESET_ALL}")
            return []

        print(f"\n{Fore.YELLOW}{self.get_message('ui.available_groups')}{Style.RESET_ALL}")
        for i, group in enumerate(available_groups, 1):
            print(f"{Fore.CYAN}{i}. {group}{Style.RESET_ALL}")

        print(f"\n{Fore.CYAN}{self.get_message('ui.selection_options')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('ui.single_number')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('ui.comma_separated')}{Style.RESET_ALL}")

        while True:
            user_input = input(f"{Fore.YELLOW}{self.get_message('prompts.select_thing_groups')}{Style.RESET_ALL}").strip()

            try:
                # Parse comma-separated or single number
                if "," in user_input:
                    choices = [int(x.strip()) for x in user_input.split(",")]
                else:
                    choices = [int(user_input)]

                # Validate all choices
                invalid_choices = [c for c in choices if c < 1 or c > len(available_groups)]

                if invalid_choices:
                    print(
                        f"{Fore.RED}{self.get_message('errors.invalid_choices', ', '.join(map(str, invalid_choices)), len(available_groups))}{Style.RESET_ALL}"
                    )
                    continue

                # Return selected groups
                selected_groups = [available_groups[c - 1] for c in choices]
                return selected_groups

            except ValueError:
                print(f"{Fore.RED}{self.get_message('errors.invalid_comma_numbers')}{Style.RESET_ALL}")

    def select_package(self, available_packages):
        """Let user select a package"""
        if not available_packages:
            print(f"{Fore.RED}{self.get_message('errors.no_packages_available')}{Style.RESET_ALL}")
            return None

        print(f"\n{Fore.YELLOW}{self.get_message('ui.available_packages')}{Style.RESET_ALL}")
        for i, package in enumerate(available_packages, 1):
            print(f"{Fore.CYAN}{i}. {package}{Style.RESET_ALL}")

        while True:
            try:
                choice = int(input(f"{Fore.YELLOW}{self.get_message('prompts.select_package', len(available_packages))}{Style.RESET_ALL}"))
                if 1 <= choice <= len(available_packages):
                    return available_packages[choice - 1]
                print(f"{Fore.RED}{self.get_message('errors.invalid_package_choice', len(available_packages))}{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED}{self.get_message('errors.invalid_number')}{Style.RESET_ALL}")

    def get_package_version(self, package_name):
        """Get package version from user and return version info with ARN"""
        print(f"\n{Fore.BLUE}{self.get_message('status.getting_versions', Fore.YELLOW + package_name + Style.RESET_ALL)}")

        versions_response = self.safe_api_call(
            self.iot_client.list_package_versions,
            "Package Versions",
            package_name,
            debug=self.debug_mode,
            packageName=package_name,
        )

        if versions_response:
            versions = versions_response.get("packageVersionSummaries", [])
            if versions:
                print(f"{Fore.GREEN}{self.get_message('ui.available_versions')}{Style.RESET_ALL}")
                for version in versions:
                    version_name = version.get("versionName", "N/A")
                    status = version.get("status", "N/A")
                    created_date = version.get("creationDate", "N/A")
                    status_color = Fore.GREEN if status == self.get_message('results.published') else Fore.YELLOW
                    print(f"{Fore.CYAN}• {version_name} - {status_color}{status}{Style.RESET_ALL} {self.get_message('results.created_date', created_date)}")

        while True:
            version = input(f"{Fore.YELLOW}{self.get_message('prompts.enter_version')}{Style.RESET_ALL}").strip()

            if not version:
                print(f"{Fore.RED}{self.get_message('errors.no_version')}{Style.RESET_ALL}")
                continue

            # Validate version exists if we have version data
            if versions_response and versions:
                available_versions = [v.get("versionName") for v in versions if v.get("versionName")]
                if version not in available_versions:
                    print(
                        f"{Fore.RED}{self.get_message('errors.version_not_found', version, ', '.join(available_versions))}{Style.RESET_ALL}"
                    )
                    continue

            break

        # Format the package version ARN
        package_arn = f"arn:aws:iot:{self.region}:{self.account_id}:package/{package_name}/version/{version}"

        return {"version": version, "arn": package_arn}

    def get_job_type(self):
        """Let user select job type"""
        print(f"\n{Fore.BLUE}{self.get_message('ui.job_type_menu')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('ui.ota_option')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('ui.custom_option')}{Style.RESET_ALL}")

        while True:
            try:
                choice = int(input(f"{Fore.YELLOW}{self.get_message('prompts.job_type_choice')}{Style.RESET_ALL}"))
                if 1 <= choice <= 2:
                    job_types = ["ota", "custom"]
                    return job_types[choice - 1]
                print(f"{Fore.RED}{self.get_message('errors.invalid_choice')}{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED}{self.get_message('errors.invalid_number')}{Style.RESET_ALL}")

    def get_job_id(self, job_type, package_name=None, version_name=None):
        """Get job ID from user or generate one"""
        timestamp = int(time.time())

        if job_type == "ota" and package_name and version_name:
            clean_version = version_name.replace(".", "")
            suggested_id = f"upgrade{package_name.capitalize()}{clean_version}_{timestamp}"
        else:
            suggested_id = f"{job_type}Job_{timestamp}"

        print(f"\n{Fore.YELLOW}{self.get_message('ui.job_id_config')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('ui.suggested_label', suggested_id)}{Style.RESET_ALL}")

        custom_id = input(f"{Fore.YELLOW}{self.get_message('prompts.custom_job_id')}{Style.RESET_ALL}").strip()
        return custom_id if custom_id else suggested_id

    def get_rollout_config(self):
        """Configure job rollout settings"""
        self.educational_pause(
            self.get_message('learning.rollout_config_title'),
            self.get_message('learning.rollout_config_description'),
        )

        print(f"\n{Fore.BLUE}{self.get_message('ui.rollout_config')}{Style.RESET_ALL}")

        use_rollout = input(f"{Fore.YELLOW}{self.get_message('prompts.configure_rollout')}{Style.RESET_ALL}").strip().lower()
        if use_rollout not in ["y", "yes"]:
            return None

        print(f"\n{Fore.CYAN}{self.get_message('ui.rollout_options')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('ui.simple_rate')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('ui.exponential_rollout')}{Style.RESET_ALL}")

        choice = input(f"{Fore.YELLOW}{self.get_message('prompts.rollout_type')}{Style.RESET_ALL}").strip()

        if choice == "1":
            try:
                max_per_min = int(input(f"{Fore.YELLOW}{self.get_message('prompts.max_per_minute')}{Style.RESET_ALL}") or "50")
            except ValueError:
                max_per_min = 50
            return {"maximumPerMinute": max_per_min}

        elif choice == "2":
            try:
                base_rate = int(input(f"{Fore.YELLOW}{self.get_message('prompts.base_rate')}{Style.RESET_ALL}") or "10")
            except ValueError:
                base_rate = 10
            try:
                increment_input = input(f"{Fore.YELLOW}{self.get_message('prompts.increment_factor')}{Style.RESET_ALL}") or "2.0"
                if increment_input.lower() in ["nan", "inf", "-inf"]:
                    increment_factor = 2.0
                else:
                    increment_factor = float(increment_input)
            except ValueError:
                increment_factor = 2.0
            try:
                notify_threshold = int(input(f"{Fore.YELLOW}{self.get_message('prompts.notify_threshold')}{Style.RESET_ALL}") or "10")
            except ValueError:
                notify_threshold = 10
            try:
                success_threshold = int(input(f"{Fore.YELLOW}{self.get_message('prompts.success_threshold')}{Style.RESET_ALL}") or "5")
            except ValueError:
                success_threshold = 5

            return {
                "exponentialRate": {
                    "baseRatePerMinute": base_rate,
                    "incrementFactor": increment_factor,
                    "rateIncreaseCriteria": {
                        "numberOfNotifiedThings": notify_threshold,
                        "numberOfSucceededThings": success_threshold,
                    },
                }
            }

        return None

    def get_job_executions_config(self):
        """Configure job execution settings (rollout rate)"""
        self.educational_pause(
            self.get_message('learning.execution_rate_title'),
            self.get_message('learning.execution_rate_description'),
        )

        print(f"\n{Fore.BLUE}{self.get_message('ui.execution_config')}{Style.RESET_ALL}")

        use_config = input(f"{Fore.YELLOW}{self.get_message('prompts.configure_execution')}{Style.RESET_ALL}").strip().lower()
        if use_config not in ["y", "yes"]:
            return None

        try:
            max_per_min = int(input(f"{Fore.YELLOW}{self.get_message('prompts.max_executions')}{Style.RESET_ALL}") or "100")
        except ValueError:
            max_per_min = 100

        use_exponential = input(f"{Fore.YELLOW}{self.get_message('prompts.use_exponential')}{Style.RESET_ALL}").strip().lower()

        config = {"maxExecutionsPerMin": max_per_min}

        if use_exponential in ["y", "yes"]:
            try:
                base_rate = int(input(f"{Fore.YELLOW}{self.get_message('prompts.base_execution_rate')}{Style.RESET_ALL}") or "10")
            except ValueError:
                base_rate = 10
            try:
                increment_input = input(f"{Fore.YELLOW}{self.get_message('prompts.execution_increment')}{Style.RESET_ALL}") or "1.5"
                if increment_input.lower() in ["nan", "inf", "-inf"]:
                    increment_factor = 1.5
                else:
                    increment_factor = float(increment_input)
            except ValueError:
                increment_factor = 1.5

            config["exponentialRate"] = {"baseRatePerMinute": base_rate, "incrementFactor": increment_factor}

        return config

    def get_abort_config(self):
        """Configure job abort criteria"""
        self.educational_pause(
            self.get_message('learning.abort_config_title'),
            self.get_message('learning.abort_config_description'),
        )

        print(f"\n{Fore.BLUE}{self.get_message('ui.abort_config')}{Style.RESET_ALL}")

        use_abort = input(f"{Fore.YELLOW}{self.get_message('prompts.configure_abort')}{Style.RESET_ALL}").strip().lower()
        if use_abort not in ["y", "yes"]:
            return None

        try:
            threshold_input = input(f"{Fore.YELLOW}{self.get_message('prompts.failure_threshold')}{Style.RESET_ALL}") or "10.0"
            if threshold_input.lower() in ["nan", "inf", "-inf"]:
                failure_threshold = 10.0
            else:
                failure_threshold = float(threshold_input)
        except ValueError:
            failure_threshold = 10.0
        try:
            min_executions = int(input(f"{Fore.YELLOW}{self.get_message('prompts.min_executions')}{Style.RESET_ALL}") or "5")
        except ValueError:
            min_executions = 5

        print(f"\n{Fore.CYAN}{self.get_message('ui.failure_types')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('ui.failed_type')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('ui.rejected_type')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('ui.timeout_type')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('ui.all_type')}{Style.RESET_ALL}")

        failure_choice = input(f"{Fore.YELLOW}{self.get_message('prompts.failure_type')}{Style.RESET_ALL}").strip()
        failure_types = ["FAILED", "REJECTED", "TIMED_OUT", "ALL"]
        failure_type = failure_types[int(failure_choice) - 1] if failure_choice in ["1", "2", "3", "4"] else "FAILED"

        return {
            "criteriaList": [
                {
                    "failureType": failure_type,
                    "action": "CANCEL",
                    "thresholdPercentage": failure_threshold,
                    "minNumberOfExecutedThings": min_executions,
                }
            ]
        }

    def get_timeout_config(self):
        """Configure job timeout settings"""
        self.educational_pause(
            self.get_message('learning.timeout_config_title'),
            self.get_message('learning.timeout_config_description'),
        )

        print(f"\n{Fore.BLUE}{self.get_message('ui.timeout_config')}{Style.RESET_ALL}")

        use_timeout = input(f"{Fore.YELLOW}{self.get_message('prompts.configure_timeout')}{Style.RESET_ALL}").strip().lower()
        if use_timeout not in ["y", "yes"]:
            return None

        try:
            timeout_minutes = int(input(f"{Fore.YELLOW}{self.get_message('prompts.timeout_minutes')}{Style.RESET_ALL}") or "60")
        except ValueError:
            timeout_minutes = 60
        return {"inProgressTimeoutInMinutes": timeout_minutes}

    def get_target_selection(self):
        """Configure target selection type"""
        self.educational_pause(
            self.get_message('learning.target_selection_title'),
            self.get_message('learning.target_selection_description'),
        )

        print(f"\n{Fore.BLUE}{self.get_message('ui.target_selection_menu')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('ui.continuous_option')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('ui.snapshot_option')}{Style.RESET_ALL}")

        choice = input(f"{Fore.YELLOW}{self.get_message('prompts.target_selection')}{Style.RESET_ALL}").strip()
        return "CONTINUOUS" if choice == "1" else "SNAPSHOT"

    def create_custom_job_document(self):
        """Create custom job document"""
        print(f"\n{Fore.BLUE}{self.get_message('ui.custom_job_doc')}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{self.get_message('prompts.custom_json')}{Style.RESET_ALL}")

        custom_json = input().strip()

        if custom_json:
            try:
                return json.loads(custom_json)
            except json.JSONDecodeError:
                print(f"{Fore.RED}{self.get_message('errors.invalid_json')}{Style.RESET_ALL}")

        # Template
        operation = input(f"{Fore.YELLOW}{self.get_message('prompts.operation_name')}{Style.RESET_ALL}") or "customOperation"

        return {
            "operation": operation,
            "parameters": {"customParam1": "value1", "customParam2": "value2"},
            "metadata": {"version": "1.0.0", "description": "Custom job operation"},
        }

    def create_job_document(self, package_name, version_name):
        """Create job document with AWS IoT presigned URL placeholders"""
        job_document = {
            "ota": {
                "packages": {
                    package_name: {
                        "attributes": f"${{aws:iot:package:{package_name}:version:{version_name}:attributes}}",
                        "artifact": {
                            "s3PresignedUrl": f"${{aws:iot:package:{package_name}:version:{version_name}:artifact:s3-presigned-url}}"
                        },
                    }
                }
            }
        }

        return job_document

    def create_job(self, job_id, thing_groups, job_document, job_type, package_version_info=None):
        """Create the IoT job with comprehensive configuration"""
        print(f"\n{Fore.BLUE}{self.get_message('status.creating_job')}{Style.RESET_ALL}")

        # Create ARNs for all selected groups
        target_arns = [f"arn:aws:iot:{self.region}:{self.account_id}:thinggroup/{group}" for group in thing_groups]

        # Build job configuration
        job_config = {
            "jobId": job_id,
            "targets": target_arns,
            "document": json.dumps(job_document),
            "description": self.job_config.get("description", f"{job_type.upper()} job for {', '.join(thing_groups)}"),
            "targetSelection": self.job_config.get("targetSelection", "CONTINUOUS"),
        }

        # Add optional configurations
        if self.job_config.get("rolloutConfig"):
            job_config["jobExecutionsRolloutConfig"] = self.job_config["rolloutConfig"]

        if self.job_config.get("executionsConfig"):
            # jobExecutionsRetryConfig only accepts criteriaList
            retry_config = self.job_config["executionsConfig"]
            if "maxExecutionsPerMin" in retry_config or "exponentialRate" in retry_config:
                # These belong in jobExecutionsRolloutConfig
                if "jobExecutionsRolloutConfig" not in job_config:
                    job_config["jobExecutionsRolloutConfig"] = {}
                if "maxExecutionsPerMin" in retry_config:
                    job_config["jobExecutionsRolloutConfig"]["maximumPerMinute"] = retry_config["maxExecutionsPerMin"]
                if "exponentialRate" in retry_config:
                    job_config["jobExecutionsRolloutConfig"]["exponentialRate"] = retry_config["exponentialRate"]

        if self.job_config.get("abortConfig"):
            job_config["abortConfig"] = self.job_config["abortConfig"]

        if self.job_config.get("timeoutConfig"):
            job_config["timeoutConfig"] = self.job_config["timeoutConfig"]

        # Add package version for OTA jobs
        if job_type == "ota" and package_version_info:
            job_config["destinationPackageVersions"] = [package_version_info["arn"]]
            job_config["presignedUrlConfig"] = {
                "roleArn": f"arn:aws:iam::{self.account_id}:role/IoTJobsRole-{self.region}-{self.account_id[:8]}",
                "expiresInSec": 3600,
            }

        # Create the job
        response = self.safe_api_call(self.iot_client.create_job, "IoT Job", job_id, debug=self.debug_mode, **job_config)

        if response:
            print(f"{Fore.GREEN}{self.get_message('status.job_created')}{Style.RESET_ALL}")

            # Display job details
            print(f"\n{Fore.CYAN}{self.get_message('ui.job_details')}{Style.RESET_ALL}")
            print(f"{Fore.GREEN}{self.get_message('ui.job_id_label', response.get('jobId', 'N/A'))}{Style.RESET_ALL}")
            print(f"{Fore.GREEN}{self.get_message('ui.job_arn', response.get('jobArn', 'N/A'))}{Style.RESET_ALL}")
            print(f"{Fore.GREEN}{self.get_message('ui.target_groups', ', '.join(thing_groups))}{Style.RESET_ALL}")
            print(f"{Fore.GREEN}{self.get_message('ui.job_type_label', job_type.upper())}{Style.RESET_ALL}")
            if package_version_info:
                print(f"{Fore.GREEN}{self.get_message('ui.package_arn', package_version_info['arn'])}{Style.RESET_ALL}")

            return True
        else:
            print(f"{Fore.RED}{self.get_message('errors.failed_create_job')}{Style.RESET_ALL}")
            return False

    def educational_pause(self, title, description):
        """Pause execution with educational content"""
        print(f"\n{Fore.YELLOW}📚 LEARNING MOMENT: {title}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{description}{Style.RESET_ALL}")
        input(f"\n{Fore.GREEN}{self.get_message('prompts.press_enter')}{Style.RESET_ALL}")
        print()

    def run(self):
        """Main execution flow"""
        self.print_header()

        # Get debug mode preference
        self.get_debug_mode()

        # Step 1: Resource Discovery
        self.educational_pause(
            self.get_message('learning.resource_discovery_title'),
            self.get_message('learning.resource_discovery_description'),
        )

        # Get available resources
        thing_groups = self.get_thing_groups()
        packages = self.get_packages()

        if not thing_groups:
            print(f"{Fore.RED}{self.get_message('errors.no_groups_run_provision')}{Style.RESET_ALL}")
            sys.exit(1)

        # Packages are only required for OTA jobs
        print(f"{Fore.CYAN}{self.get_message('status.found_resources', len(thing_groups), len(packages))}{Style.RESET_ALL}")

        # Step 2: Job Type Selection
        self.educational_pause(
            self.get_message('learning.job_type_title'),
            self.get_message('learning.job_type_description'),
        )

        # Get job type
        job_type = self.get_job_type()

        # Step 3: Target and Configuration
        self.educational_pause(
            self.get_message('learning.target_config_title'),
            self.get_message('learning.target_config_description', job_type.upper()),
        )

        # Get target groups
        selected_groups = self.select_thing_groups(thing_groups)
        if not selected_groups:
            print(f"{Fore.RED}{self.get_message('errors.no_groups_selected')}{Style.RESET_ALL}")
            sys.exit(1)

        # Ask about advanced features
        use_advanced = (
            input(f"{Fore.YELLOW}{self.get_message('prompts.configure_advanced')}{Style.RESET_ALL}")
            .strip()
            .lower()
        )

        if use_advanced in ["y", "yes"]:
            # Configure advanced job settings with learning moments
            self.job_config["targetSelection"] = self.get_target_selection()
            self.job_config["rolloutConfig"] = self.get_rollout_config()
            self.job_config["executionsConfig"] = self.get_job_executions_config()
            self.job_config["abortConfig"] = self.get_abort_config()
            self.job_config["timeoutConfig"] = self.get_timeout_config()
        else:
            # Use defaults
            self.job_config["targetSelection"] = "CONTINUOUS"
            print(f"{Fore.GREEN}{self.get_message('status.using_defaults')}{Style.RESET_ALL}")

        # Get job description
        default_desc = f"{job_type.upper()} job for {', '.join(selected_groups)}"
        custom_desc = input(f"{Fore.YELLOW}{self.get_message('prompts.job_description', default_desc)}{Style.RESET_ALL}").strip()
        self.job_config["description"] = custom_desc if custom_desc else default_desc

        # Job-specific configuration
        package_version_info = None
        selected_package = None
        if job_type == "ota":
            if not packages:
                print(f"{Fore.RED}{self.get_message('errors.no_packages_for_ota')}{Style.RESET_ALL}")
                sys.exit(1)

            selected_package = self.select_package(packages)
            package_version_info = self.get_package_version(selected_package)
            if not package_version_info:
                print(f"{Fore.RED}{self.get_message('errors.failed_version_info')}{Style.RESET_ALL}")
                sys.exit(1)
            job_document = self.create_job_document(selected_package, package_version_info["version"])
            job_id = self.get_job_id(job_type, selected_package, package_version_info["version"])

        elif job_type == "custom":
            job_document = self.create_custom_job_document()
            job_id = self.get_job_id(job_type)

        # Step 4: Job Creation
        self.educational_pause(
            self.get_message('learning.job_creation_title'),
            self.get_message('learning.job_creation_description', job_type.upper(), len(selected_groups)),
        )

        # Display final configuration
        print(f"\n{Fore.CYAN}{self.get_message('ui.final_config')}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{self.get_message('ui.job_id_label', job_id)}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{self.get_message('ui.job_type_label', job_type.upper())}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{self.get_message('ui.thing_groups_label', ', '.join(selected_groups))}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{self.get_message('ui.target_selection_label', self.job_config['targetSelection'])}{Style.RESET_ALL}")

        if package_version_info:
            print(f"{Fore.GREEN}{self.get_message('ui.package_label', selected_package, package_version_info['version'])}{Style.RESET_ALL}")

        print(f"\n{Fore.CYAN}{self.get_message('ui.job_document')}{Style.RESET_ALL}")
        print(json.dumps(job_document, indent=2))

        # Show advanced configurations if set
        if any(self.job_config.get(key) for key in ["rolloutConfig", "executionsConfig", "abortConfig", "timeoutConfig"]):
            print(f"\n{Fore.CYAN}{self.get_message('ui.advanced_configs')}{Style.RESET_ALL}")
            for key, value in self.job_config.items():
                if value and key not in ["targetSelection", "description"]:
                    print(f"{Fore.YELLOW}{key}: {json.dumps(value, indent=2)}{Style.RESET_ALL}")

        # Create the job
        success = self.create_job(job_id, selected_groups, job_document, job_type, package_version_info)

        if success:
            print(f"\n{Fore.GREEN}{self.get_message('status.creation_completed')}{Style.RESET_ALL}")
            if job_type == "ota":
                print(f"{Fore.CYAN}{self.get_message('results.use_simulate')}{Style.RESET_ALL}")
            else:
                print(f"{Fore.CYAN}{self.get_message('results.use_explore')}{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.RED}{self.get_message('status.creation_failed')}{Style.RESET_ALL}")
            sys.exit(1)


if __name__ == "__main__":
    # Initialize language
    USER_LANG = get_language()
    messages = load_messages("create_job", USER_LANG)
    
    job_creator = IoTJobCreator()
    try:
        job_creator.run()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}{job_creator.get_message('ui.cancelled')}{Style.RESET_ALL}")
        sys.exit(0)
