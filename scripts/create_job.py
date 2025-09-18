#!/usr/bin/env python3

import json
import os
import sys
import time
from threading import Semaphore

import boto3
from botocore.exceptions import ClientError
from colorama import Fore, Style, init

# Initialize colorama
init()


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

            time.sleep(0.1)  # Rate limiting  # nosemgrep: arbitrary-sleep
            return response
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code in ["ResourceNotFoundException", "ResourceNotFound"]:
                if debug or self.debug_mode:
                    print(f"📝 Resource not found: {resource_name}")
                return None
            else:
                print(f"❌ Error in {operation_name} {resource_name}: {e.response['Error']['Message']}")
                if debug or self.debug_mode:
                    print("🔍 DEBUG: Full error response:")
                    print(json.dumps(e.response, indent=2, default=str))
            time.sleep(0.1)  # nosemgrep: arbitrary-sleep
            return None
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            if debug or self.debug_mode:
                import traceback

                print("🔍 DEBUG: Full traceback:")
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
                print("🔍 DEBUG: Client configuration:")
                print(f"   IoT Service: {self.iot_client.meta.service_model.service_name}")
                print(f"   API Version: {self.iot_client.meta.service_model.api_version}")

            return True
        except Exception as e:
            print(f"❌ Error initializing AWS clients: {str(e)}")
            return False

    def print_header(self):
        print(f"{Fore.CYAN}🚀 AWS IoT Job Creator (Boto3){Style.RESET_ALL}")
        print(f"{Fore.CYAN}=============================={Style.RESET_ALL}")

        # Initialize clients and display info
        if not self.initialize_clients():
            sys.exit(1)

        print(f"{Fore.BLUE}📍 AWS Configuration:{Style.RESET_ALL}")
        print(f"{Fore.GREEN}   Account ID: {self.account_id}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}   Region: {self.region}{Style.RESET_ALL}")
        print()

        print(f"{Fore.YELLOW}📚 LEARNING GOAL:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}This script demonstrates AWS IoT Job creation with two main job types:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}• OTA firmware updates with Software Package Catalog integration{Style.RESET_ALL}")
        print(f"{Fore.CYAN}• Custom job documents for any device operation{Style.RESET_ALL}")
        print(f"{Fore.CYAN}• Advanced configurations: rollout, retry, abort, and timeout settings{Style.RESET_ALL}\n")

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

    def get_thing_groups(self):
        """Get available thing groups using efficient pagination"""
        print(f"{Fore.BLUE}🔍 Scanning for thing groups...{Style.RESET_ALL}")

        group_names = []
        paginator = self.iot_client.get_paginator("list_thing_groups")

        try:
            for page in paginator.paginate():
                groups = page.get("thingGroups", [])
                page_group_names = [group.get("groupName") for group in groups if group.get("groupName")]
                group_names.extend(page_group_names)
        except Exception as e:
            print(f"{Fore.RED}❌ Failed to list thing groups: {str(e)}{Style.RESET_ALL}")
            return []

        if group_names:
            print(f"{Fore.GREEN}📋 Available Thing Groups:{Style.RESET_ALL}")
            for i, group_name in enumerate(group_names, 1):
                print(f"{Fore.CYAN}{i}. {group_name}{Style.RESET_ALL}")

        return group_names

    def get_packages(self):
        """Get available IoT packages"""
        print(f"{Fore.BLUE}🔍 Scanning for IoT packages...{Style.RESET_ALL}")

        response = self.safe_api_call(self.iot_client.list_packages, "Package List", "all packages", debug=self.debug_mode)

        if not response:
            print(f"{Fore.RED}❌ Failed to list packages{Style.RESET_ALL}")
            return []

        packages = response.get("packageSummaries", [])
        valid_packages = [pkg for pkg in packages if pkg.get("packageName")]
        package_names = [pkg.get("packageName") for pkg in valid_packages]

        if package_names:
            print(f"{Fore.GREEN}📦 Available Packages:{Style.RESET_ALL}")
            for i, pkg in enumerate(valid_packages, 1):
                pkg_name = pkg.get("packageName")
                created_date = pkg.get("creationDate", "Unknown")
                print(f"{Fore.CYAN}{i}. {pkg_name} (Created: {created_date}){Style.RESET_ALL}")

        return package_names

    def select_thing_groups(self, available_groups):
        """Let user select thing groups (single number or comma-separated list)"""
        if not available_groups:
            print(f"{Fore.RED}❌ No thing groups available{Style.RESET_ALL}")
            return []

        print(f"\n{Fore.YELLOW}📝 Available thing groups:{Style.RESET_ALL}")
        for i, group in enumerate(available_groups, 1):
            print(f"{Fore.CYAN}{i}. {group}{Style.RESET_ALL}")

        print(f"\n{Fore.CYAN}Options:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}1. Enter a single number (e.g., 3){Style.RESET_ALL}")
        print(f"{Fore.CYAN}2. Enter comma-separated numbers (e.g., 1,3,5){Style.RESET_ALL}")

        while True:
            user_input = input(f"{Fore.YELLOW}Select thing group(s): {Style.RESET_ALL}").strip()

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
                        f"{Fore.RED}❌ Invalid choices: {', '.join(map(str, invalid_choices))}. Please enter numbers between 1-{len(available_groups)}{Style.RESET_ALL}"
                    )
                    continue

                # Return selected groups
                selected_groups = [available_groups[c - 1] for c in choices]
                return selected_groups

            except ValueError:
                print(f"{Fore.RED}❌ Please enter valid numbers separated by commas{Style.RESET_ALL}")

    def select_package(self, available_packages):
        """Let user select a package"""
        if not available_packages:
            print(f"{Fore.RED}❌ No packages available{Style.RESET_ALL}")
            return None

        print(f"\n{Fore.YELLOW}📦 Available packages:{Style.RESET_ALL}")
        for i, package in enumerate(available_packages, 1):
            print(f"{Fore.CYAN}{i}. {package}{Style.RESET_ALL}")

        while True:
            try:
                choice = int(input(f"{Fore.YELLOW}Select package [1-{len(available_packages)}]: {Style.RESET_ALL}"))
                if 1 <= choice <= len(available_packages):
                    return available_packages[choice - 1]
                print(f"{Fore.RED}❌ Invalid choice. Please enter 1-{len(available_packages)}{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED}❌ Please enter a valid number{Style.RESET_ALL}")

    def get_package_version(self, package_name):
        """Get package version from user and return version info with ARN"""
        print(f"\n{Fore.BLUE}🔍 Getting versions for package: {Fore.YELLOW}{package_name}{Style.RESET_ALL}")

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
                print(f"{Fore.GREEN}📋 Available Versions:{Style.RESET_ALL}")
                for version in versions:
                    version_name = version.get("versionName", "N/A")
                    status = version.get("status", "N/A")
                    created_date = version.get("creationDate", "N/A")
                    status_color = Fore.GREEN if status == "PUBLISHED" else Fore.YELLOW
                    print(f"{Fore.CYAN}• {version_name} - {status_color}{status}{Style.RESET_ALL} (Created: {created_date})")

        while True:
            version = input(f"{Fore.YELLOW}📝 Enter package version: {Style.RESET_ALL}").strip()

            if not version:
                print(f"{Fore.RED}❌ No version provided{Style.RESET_ALL}")
                continue

            # Validate version exists if we have version data
            if versions_response and versions:
                available_versions = [v.get("versionName") for v in versions if v.get("versionName")]
                if version not in available_versions:
                    print(
                        f"{Fore.RED}❌ Version '{version}' not found. Available versions: {', '.join(available_versions)}{Style.RESET_ALL}"
                    )
                    continue

            break

        # Format the package version ARN
        package_arn = f"arn:aws:iot:{self.region}:{self.account_id}:package/{package_name}/version/{version}"

        return {"version": version, "arn": package_arn}

    def get_job_type(self):
        """Let user select job type"""
        print(f"\n{Fore.BLUE}🎯 Select Job Type:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}1. OTA Firmware Update (Software Package Catalog){Style.RESET_ALL}")
        print(f"{Fore.CYAN}2. Custom Job Document{Style.RESET_ALL}")

        while True:
            try:
                choice = int(input(f"{Fore.YELLOW}Enter choice [1-2]: {Style.RESET_ALL}"))
                if 1 <= choice <= 2:
                    job_types = ["ota", "custom"]
                    return job_types[choice - 1]
                print(f"{Fore.RED}❌ Invalid choice. Please enter 1-2{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED}❌ Please enter a valid number{Style.RESET_ALL}")

    def get_job_id(self, job_type, package_name=None, version_name=None):
        """Get job ID from user or generate one"""
        timestamp = int(time.time())

        if job_type == "ota" and package_name and version_name:
            clean_version = version_name.replace(".", "")
            suggested_id = f"upgrade{package_name.capitalize()}{clean_version}_{timestamp}"
        else:
            suggested_id = f"{job_type}Job_{timestamp}"

        print(f"\n{Fore.YELLOW}📝 Job ID Configuration:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Suggested: {suggested_id}{Style.RESET_ALL}")

        custom_id = input(f"{Fore.YELLOW}Enter custom job ID (or press Enter for suggested): {Style.RESET_ALL}").strip()
        return custom_id if custom_id else suggested_id

    def get_rollout_config(self):
        """Configure job rollout settings"""
        self.educational_pause(
            "Rollout Configuration - Controlled Deployment Strategy",
            "Rollout configuration controls how quickly jobs are deployed across your fleet:\n"
            "• Simple Rate Limiting: Set maximum executions per minute (e.g., 50 devices/min)\n"
            "• Exponential Rollout: Start slow, increase rate based on success criteria\n\n"
            "Exponential rollout is safer for large fleets - it starts with a small number of devices,\n"
            "monitors success rates, and gradually increases deployment speed. This prevents\n"
            "widespread failures from bad firmware or configuration changes.",
        )

        print(f"\n{Fore.BLUE}🚀 Rollout Configuration:{Style.RESET_ALL}")

        use_rollout = input(f"{Fore.YELLOW}Configure rollout settings? [y/N]: {Style.RESET_ALL}").strip().lower()
        if use_rollout not in ["y", "yes"]:
            return None

        print(f"\n{Fore.CYAN}📊 Rollout Options:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}1. Simple rate limit (maximumPerMinute){Style.RESET_ALL}")
        print(f"{Fore.CYAN}2. Exponential rollout{Style.RESET_ALL}")

        choice = input(f"{Fore.YELLOW}Select rollout type [1-2]: {Style.RESET_ALL}").strip()

        if choice == "1":
            try:
                max_per_min = int(input(f"{Fore.YELLOW}Maximum executions per minute [50]: {Style.RESET_ALL}") or "50")
            except ValueError:
                max_per_min = 50
            return {"maximumPerMinute": max_per_min}

        elif choice == "2":
            try:
                base_rate = int(input(f"{Fore.YELLOW}Base rate per minute [10]: {Style.RESET_ALL}") or "10")
            except ValueError:
                base_rate = 10
            try:
                increment_input = input(f"{Fore.YELLOW}Increment factor [2.0]: {Style.RESET_ALL}") or "2.0"
                if increment_input.lower() in ["nan", "inf", "-inf"]:
                    increment_factor = 2.0
                else:
                    increment_factor = float(increment_input)
            except ValueError:
                increment_factor = 2.0
            try:
                notify_threshold = int(input(f"{Fore.YELLOW}Notify threshold [10]: {Style.RESET_ALL}") or "10")
            except ValueError:
                notify_threshold = 10
            try:
                success_threshold = int(input(f"{Fore.YELLOW}Success threshold [5]: {Style.RESET_ALL}") or "5")
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
            "Job Execution Rate - Performance Optimization",
            "Execution rate settings control how fast individual devices process jobs:\n"
            "• Max Executions Per Minute: Prevents overwhelming your IoT infrastructure\n"
            "• Exponential Rate: Gradually increases processing speed based on success\n\n"
            "These settings are different from rollout config - rollout controls how many devices\n"
            "get the job, while execution rate controls how fast each device processes it.\n"
            "Proper rate limiting prevents API throttling and ensures stable job execution.",
        )

        print(f"\n{Fore.BLUE}🔄 Job Execution Rate Configuration:{Style.RESET_ALL}")

        use_config = input(f"{Fore.YELLOW}Configure execution rate settings? [y/N]: {Style.RESET_ALL}").strip().lower()
        if use_config not in ["y", "yes"]:
            return None

        try:
            max_per_min = int(input(f"{Fore.YELLOW}Max executions per minute [100]: {Style.RESET_ALL}") or "100")
        except ValueError:
            max_per_min = 100

        use_exponential = input(f"{Fore.YELLOW}Use exponential execution rate? [y/N]: {Style.RESET_ALL}").strip().lower()

        config = {"maxExecutionsPerMin": max_per_min}

        if use_exponential in ["y", "yes"]:
            try:
                base_rate = int(input(f"{Fore.YELLOW}Base execution rate per minute [10]: {Style.RESET_ALL}") or "10")
            except ValueError:
                base_rate = 10
            try:
                increment_input = input(f"{Fore.YELLOW}Increment factor [1.5]: {Style.RESET_ALL}") or "1.5"
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
            "Abort Configuration - Automatic Failure Protection",
            "Abort criteria automatically cancel jobs when failure rates exceed thresholds:\n"
            "• Failure Threshold: Percentage of devices that must fail before abort (e.g., 10%)\n"
            "• Minimum Executions: Number of devices to test before applying threshold\n"
            "• Failure Types: FAILED, REJECTED, TIMED_OUT, or ALL\n\n"
            "This prevents bad firmware or configurations from spreading across your entire fleet.\n"
            "For example: 'Cancel job if >10% of devices fail after testing on at least 5 devices'\n"
            "Essential for production deployments to minimize blast radius of failures.",
        )

        print(f"\n{Fore.BLUE}🛑 Abort Configuration:{Style.RESET_ALL}")

        use_abort = input(f"{Fore.YELLOW}Configure abort criteria? [y/N]: {Style.RESET_ALL}").strip().lower()
        if use_abort not in ["y", "yes"]:
            return None

        try:
            threshold_input = input(f"{Fore.YELLOW}Failure threshold percentage [10.0]: {Style.RESET_ALL}") or "10.0"
            if threshold_input.lower() in ["nan", "inf", "-inf"]:
                failure_threshold = 10.0
            else:
                failure_threshold = float(threshold_input)
        except ValueError:
            failure_threshold = 10.0
        try:
            min_executions = int(input(f"{Fore.YELLOW}Minimum executions before abort [5]: {Style.RESET_ALL}") or "5")
        except ValueError:
            min_executions = 5

        print(f"\n{Fore.CYAN}Failure Types:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}1. FAILED - Job execution failed{Style.RESET_ALL}")
        print(f"{Fore.CYAN}2. REJECTED - Job execution rejected{Style.RESET_ALL}")
        print(f"{Fore.CYAN}3. TIMED_OUT - Job execution timed out{Style.RESET_ALL}")
        print(f"{Fore.CYAN}4. ALL - Any failure type{Style.RESET_ALL}")

        failure_choice = input(f"{Fore.YELLOW}Select failure type [1-4]: {Style.RESET_ALL}").strip()
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
            "Timeout Configuration - Preventing Stuck Jobs",
            "Timeout settings prevent job executions from running indefinitely:\n"
            "• In-Progress Timeout: Maximum time a device can spend processing a job\n"
            "• Prevents devices from getting stuck in IN_PROGRESS state\n"
            "• Automatically marks stuck executions as TIMED_OUT\n\n"
            "Typical values: 60 minutes for firmware updates, 10 minutes for configuration changes.\n"
            "Without timeouts, stuck devices can prevent job completion and waste resources.\n"
            "Essential for maintaining fleet health and job lifecycle management.",
        )

        print(f"\n{Fore.BLUE}⏱️ Timeout Configuration:{Style.RESET_ALL}")

        use_timeout = input(f"{Fore.YELLOW}Configure timeout settings? [y/N]: {Style.RESET_ALL}").strip().lower()
        if use_timeout not in ["y", "yes"]:
            return None

        try:
            timeout_minutes = int(input(f"{Fore.YELLOW}In-progress timeout (minutes) [60]: {Style.RESET_ALL}") or "60")
        except ValueError:
            timeout_minutes = 60
        return {"inProgressTimeoutInMinutes": timeout_minutes}

    def get_target_selection(self):
        """Configure target selection type"""
        self.educational_pause(
            "Target Selection - Device Inclusion Strategy",
            "Target selection determines how jobs handle devices added to thing groups after job creation:\n"
            "• CONTINUOUS: Automatically includes new devices added to target groups (recommended)\n"
            "• SNAPSHOT: Only targets devices that existed in groups at job creation time\n\n"
            "CONTINUOUS jobs are ideal for dynamic fleets where devices are frequently added,\n"
            "while SNAPSHOT jobs provide predictable, fixed target lists for controlled deployments.",
        )

        print(f"\n{Fore.BLUE}🎯 Target Selection:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}1. CONTINUOUS - Include new devices added to groups{Style.RESET_ALL}")
        print(f"{Fore.CYAN}2. SNAPSHOT - Only current devices in groups{Style.RESET_ALL}")

        choice = input(f"{Fore.YELLOW}Select target selection [1-2]: {Style.RESET_ALL}").strip()
        return "CONTINUOUS" if choice == "1" else "SNAPSHOT"

    def create_custom_job_document(self):
        """Create custom job document"""
        print(f"\n{Fore.BLUE}🛠️ Custom Job Document:{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Enter JSON job document (or press Enter for template):{Style.RESET_ALL}")

        custom_json = input().strip()

        if custom_json:
            try:
                return json.loads(custom_json)
            except json.JSONDecodeError:
                print(f"{Fore.RED}❌ Invalid JSON. Using template.{Style.RESET_ALL}")

        # Template
        operation = input(f"{Fore.YELLOW}Operation name [customOperation]: {Style.RESET_ALL}") or "customOperation"

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
        print(f"\n{Fore.BLUE}🚀 Creating IoT job...{Style.RESET_ALL}")

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
            print(f"{Fore.GREEN}✅ IoT job created successfully!{Style.RESET_ALL}")

            # Display job details
            print(f"\n{Fore.CYAN}📋 Job Details:{Style.RESET_ALL}")
            print(f"{Fore.GREEN}🆔 Job ID: {response.get('jobId', 'N/A')}{Style.RESET_ALL}")
            print(f"{Fore.GREEN}🔗 Job ARN: {response.get('jobArn', 'N/A')}{Style.RESET_ALL}")
            print(f"{Fore.GREEN}👥 Target Groups: {', '.join(thing_groups)}{Style.RESET_ALL}")
            print(f"{Fore.GREEN}📄 Job Type: {job_type.upper()}{Style.RESET_ALL}")
            if package_version_info:
                print(f"{Fore.GREEN}📦 Package ARN: {package_version_info['arn']}{Style.RESET_ALL}")

            return True
        else:
            print(f"{Fore.RED}❌ Failed to create IoT job{Style.RESET_ALL}")
            return False

    def educational_pause(self, title, description):
        """Pause execution with educational content"""
        print(f"\n{Fore.YELLOW}📚 LEARNING MOMENT: {title}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{description}{Style.RESET_ALL}")
        input(f"\n{Fore.GREEN}Press Enter to continue...{Style.RESET_ALL}")
        print()

    def run(self):
        """Main execution flow"""
        self.print_header()

        # Get debug mode preference
        self.get_debug_mode()

        # Step 1: Resource Discovery
        self.educational_pause(
            "Resource Discovery - Finding Available Targets",
            "Before creating an IoT Job, we need to discover available thing groups and packages.\n"
            "Thing groups define which devices will receive the job. For OTA jobs, we also need\n"
            "packages from the Software Package Catalog. Other job types can work with thing\n"
            "groups alone, making them more flexible for various device operations.\n\n"
            "🔄 NEXT: We will scan for available thing groups and IoT packages in your account",
        )

        # Get available resources
        thing_groups = self.get_thing_groups()
        packages = self.get_packages()

        if not thing_groups:
            print(f"{Fore.RED}❌ No thing groups available. Please run provision script first.{Style.RESET_ALL}")
            sys.exit(1)

        # Packages are only required for OTA jobs
        print(f"{Fore.CYAN}📊 Found {len(thing_groups)} thing groups and {len(packages)} packages{Style.RESET_ALL}")

        # Step 2: Job Type Selection
        self.educational_pause(
            "Job Type Selection - Choosing Operation Type",
            "AWS IoT Jobs support two main operation types:\n"
            "• OTA Updates: Firmware deployment with Software Package Catalog integration\n"
            "• Custom Operations: Any device-specific commands or workflows with custom job documents\n\n"
            "🔄 NEXT: We will select the job type and configure the operation",
        )

        # Get job type
        job_type = self.get_job_type()

        # Step 3: Target and Configuration
        self.educational_pause(
            "Target and Configuration Setup",
            "Now we'll configure job targets, execution parameters, and advanced settings.\n"
            "Advanced configurations include rollout rates, retry policies, abort criteria,\n"
            "and timeout settings. These ensure reliable job execution across large fleets\n"
            "with proper error handling and performance optimization.\n\n"
            f"🔄 NEXT: We will configure the {job_type.upper()} job parameters",
        )

        # Get target groups
        selected_groups = self.select_thing_groups(thing_groups)
        if not selected_groups:
            print(f"{Fore.RED}❌ No thing groups selected{Style.RESET_ALL}")
            sys.exit(1)

        # Ask about advanced features
        use_advanced = (
            input(f"{Fore.YELLOW}Configure advanced job features (rollout, retry, abort, timeout)? [y/N]: {Style.RESET_ALL}")
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
            print(f"{Fore.GREEN}✅ Using default settings: CONTINUOUS target selection{Style.RESET_ALL}")

        # Get job description
        default_desc = f"{job_type.upper()} job for {', '.join(selected_groups)}"
        custom_desc = input(f"{Fore.YELLOW}Job description [{default_desc}]: {Style.RESET_ALL}").strip()
        self.job_config["description"] = custom_desc if custom_desc else default_desc

        # Job-specific configuration
        package_version_info = None
        selected_package = None
        if job_type == "ota":
            if not packages:
                print(f"{Fore.RED}❌ No packages available for OTA job{Style.RESET_ALL}")
                sys.exit(1)

            selected_package = self.select_package(packages)
            package_version_info = self.get_package_version(selected_package)
            if not package_version_info:
                print(f"{Fore.RED}❌ Failed to get package version information{Style.RESET_ALL}")
                sys.exit(1)
            job_document = self.create_job_document(selected_package, package_version_info["version"])
            job_id = self.get_job_id(job_type, selected_package, package_version_info["version"])

        elif job_type == "custom":
            job_document = self.create_custom_job_document()
            job_id = self.get_job_id(job_type)

        # Step 4: Job Creation
        self.educational_pause(
            "Job Creation - Deploying to Fleet",
            f"We'll now create the {job_type.upper()} job with all configured settings.\n"
            "The job will be deployed to the selected thing groups with the specified\n"
            "rollout, retry, and abort configurations. Devices will receive the job\n"
            "document and execute the defined operations according to the job parameters.\n\n"
            f"🔄 NEXT: We will create and deploy the job to {len(selected_groups)} thing groups",
        )

        # Display final configuration
        print(f"\n{Fore.CYAN}🎯 Final Job Configuration:{Style.RESET_ALL}")
        print(f"{Fore.GREEN}🆔 Job ID: {job_id}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}📄 Job Type: {job_type.upper()}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}👥 Thing Groups: {', '.join(selected_groups)}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}🎯 Target Selection: {self.job_config['targetSelection']}{Style.RESET_ALL}")

        if package_version_info:
            print(f"{Fore.GREEN}📦 Package: {selected_package} v{package_version_info['version']}{Style.RESET_ALL}")

        print(f"\n{Fore.CYAN}📋 Job Document:{Style.RESET_ALL}")
        print(json.dumps(job_document, indent=2))

        # Show advanced configurations if set
        if any(self.job_config.get(key) for key in ["rolloutConfig", "executionsConfig", "abortConfig", "timeoutConfig"]):
            print(f"\n{Fore.CYAN}⚙️  Advanced Configurations:{Style.RESET_ALL}")
            for key, value in self.job_config.items():
                if value and key not in ["targetSelection", "description"]:
                    print(f"{Fore.YELLOW}{key}: {json.dumps(value, indent=2)}{Style.RESET_ALL}")

        # Create the job
        success = self.create_job(job_id, selected_groups, job_document, job_type, package_version_info)

        if success:
            print(f"\n{Fore.GREEN}🎉 Job creation completed successfully!{Style.RESET_ALL}")
            if job_type == "ota":
                print(f"{Fore.CYAN}💡 Use the simulate_job_execution script to test job execution{Style.RESET_ALL}")
            else:
                print(f"{Fore.CYAN}💡 Use the explore_jobs script to monitor job progress{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.RED}❌ Job creation failed{Style.RESET_ALL}")
            sys.exit(1)


if __name__ == "__main__":
    job_creator = IoTJobCreator()
    try:
        job_creator.run()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}👋 Job creation cancelled by user. Goodbye!{Style.RESET_ALL}")
        sys.exit(0)
