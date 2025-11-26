#!/usr/bin/env python3

import json
import os
import sys
import tempfile
import time
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
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


class PackageManager:
    def __init__(self):
        self.region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        self.account_id = None
        self.debug_mode = False
        self.iot_client = None
        self.iot_data_client = None
        self.s3_client = None
        self.iam_client = None
        self.sts_client = None

        # Rate limiting semaphores
        self.api_semaphore = Semaphore(10)
        self.shadow_semaphore = Semaphore(20)

    def get_message(self, key, *args):
        """Get localized message with optional formatting"""
        # Handle nested keys like 'warnings.debug_warning'
        if '.' in key:
            keys = key.split('.')
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
            self.iot_data_client = boto3.client("iot-data", region_name=self.region)
            self.s3_client = boto3.client("s3", region_name=self.region)
            self.iam_client = boto3.client("iam", region_name=self.region)
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
        print(f"{Fore.CYAN}{self.get_message('separator')}{Style.RESET_ALL}\n")

        print(f"{Fore.YELLOW}{self.get_message('learning_goal')}{Style.RESET_ALL}")
        print(
            f"{Fore.CYAN}{self.get_message('learning_description')}{Style.RESET_ALL}\n"
        )

        # Initialize clients and display info
        if not self.initialize_clients():
            print(
                f"{Fore.RED}{self.get_message('errors.client_init_failed')}{Style.RESET_ALL}"
            )
            return False

        print(f"{Fore.CYAN}{self.get_message('region_label')} {Fore.GREEN}{self.region}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('account_id_label')} {Fore.GREEN}{self.account_id}{Style.RESET_ALL}\n")
        return True

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

    def get_operation_choice(self):
        """Get operation choice from user"""
        print(f"{Fore.BLUE}{self.get_message('ui.operation_menu')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('ui.create_package')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('ui.create_version')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('ui.list_packages')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('ui.describe_package')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('ui.describe_version')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('ui.check_config')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('ui.enable_config')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('ui.disable_config')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('ui.check_device_version')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('ui.revert_versions')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('ui.exit')}{Style.RESET_ALL}")

        while True:
            try:
                choice = int(input(f"{Fore.YELLOW}{self.get_message('prompts.operation_choice')}{Style.RESET_ALL}"))
                if 1 <= choice <= 11:
                    return choice
                print(f"{Fore.RED}{self.get_message('errors.invalid_choice')}{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED}{self.get_message('errors.invalid_number')}{Style.RESET_ALL}")

    def create_package(self):
        """Create a new software package"""
        print(f"\n{Fore.BLUE}{self.get_message('ui.create_package')}{Style.RESET_ALL}\n")

        package_name = input(f"{Fore.YELLOW}{self.get_message('prompts.package_name')}{Style.RESET_ALL}").strip()

        if not package_name:
            print(f"{Fore.RED}{self.get_message('errors.package_name_empty')}{Style.RESET_ALL}")
            return

        # Check if package exists using efficient pagination
        package_names = []
        paginator = self.iot_client.get_paginator("list_packages")

        try:
            for page in paginator.paginate():
                packages = page.get("packageSummaries", [])
                page_names = [p["packageName"] for p in packages]
                package_names.extend(page_names)
                if package_name in page_names:
                    print(f"{Fore.YELLOW}{self.get_message('errors.package_exists', package_name)}{Style.RESET_ALL}")
                    return
        except Exception as e:
            print(f"{Fore.RED}{self.get_message('errors.failed_check_packages', str(e))}{Style.RESET_ALL}")
            return

        # Create package
        response = self.safe_api_call(
            self.iot_client.create_package, "IoT Package", package_name, debug=self.debug_mode, packageName=package_name
        )

        if response:
            print(f"{Fore.GREEN}{self.get_message('status.package_created')}{Style.RESET_ALL}")
            print(f"{Fore.GREEN}{self.get_message('ui.package_name_label', response.get('packageName', 'N/A'))}{Style.RESET_ALL}")
            print(f"{Fore.GREEN}{self.get_message('ui.package_arn', response.get('packageArn', 'N/A'))}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}{self.get_message('errors.failed_create_package')}{Style.RESET_ALL}")

    def get_s3_bucket(self):
        """Get or create Amazon S3 bucket for firmware storage"""
        # Check for existing bucket in current region
        try:
            response = self.s3_client.list_buckets()
            existing_buckets = [
                b["Name"] for b in response.get("Buckets", []) if b["Name"].startswith(f"iot-firmware-{self.region}")
            ]

            if existing_buckets:
                bucket_name = existing_buckets[0]
                print(f"{Fore.GREEN}{self.get_message('ui.using_bucket', bucket_name)}{Style.RESET_ALL}")
                return bucket_name
        except Exception as e:
            print(f"{Fore.RED}{self.get_message('errors.failed_list_buckets', str(e))}{Style.RESET_ALL}")
            return None

        # Create new bucket
        bucket_name = f"iot-firmware-{self.region}-{int(time.time())}"
        print(f"{Fore.BLUE}{self.get_message('ui.creating_bucket', bucket_name)}{Style.RESET_ALL}")

        if self.region == "us-east-1":
            bucket_response = self.safe_api_call(
                self.s3_client.create_bucket, "S3 Bucket", bucket_name, debug=self.debug_mode, Bucket=bucket_name
            )
        else:
            bucket_response = self.safe_api_call(
                self.s3_client.create_bucket,
                "S3 Bucket",
                bucket_name,
                debug=self.debug_mode,
                Bucket=bucket_name,
                CreateBucketConfiguration={"LocationConstraint": self.region},
            )

        if bucket_response:
            print(f"{Fore.GREEN}{self.get_message('status.bucket_created')}{Style.RESET_ALL}")

            # Enable versioning
            versioning_response = self.safe_api_call(
                self.s3_client.put_bucket_versioning,
                "S3 Bucket Versioning",
                bucket_name,
                debug=self.debug_mode,
                Bucket=bucket_name,
                VersioningConfiguration={"Status": "Enabled"},
            )

            if versioning_response:
                print(f"{Fore.GREEN}{self.get_message('status.bucket_versioning')}{Style.RESET_ALL}")

            return bucket_name
        else:
            print(f"{Fore.RED}{self.get_message('errors.failed_create_bucket')}{Style.RESET_ALL}")
            return None

    def upload_firmware_to_s3(self, bucket_name, package_name, version):
        """Upload firmware package to Amazon S3"""
        import re

        # Sanitize inputs for S3 key
        safe_package_name = re.sub(r"[^a-zA-Z0-9.\-_]", "", str(package_name))
        safe_version = re.sub(r"[^a-zA-Z0-9.\-_]", "", str(version))
        clean_version = safe_version.replace(".", "_")
        key = f"{safe_package_name}_v{clean_version}.zip"

        print(f"{Fore.BLUE}{self.get_message('ui.uploading_firmware', key)}{Style.RESET_ALL}")

        # Check if file already exists
        try:
            response = self.s3_client.head_object(Bucket=bucket_name, Key=key)
            version_id = response.get("VersionId", "")
            print(f"{Fore.GREEN}{self.get_message('status.firmware_exists', version_id)}{Style.RESET_ALL}")
            return version_id, key
        except ClientError as e:
            if e.response["Error"]["Code"] != "404":
                print(f"{Fore.RED}{self.get_message('errors.failed_check_file', e.response['Error']['Message'])}{Style.RESET_ALL}")
                return None, key

        # Create dummy firmware zip file
        temp_fd, temp_file_path = tempfile.mkstemp(suffix=".zip")
        os.close(temp_fd)

        with zipfile.ZipFile(temp_file_path, "w") as zipf:
            zipf.writestr(
                f"firmware_{safe_version}.bin", f"Firmware version {safe_version} for {safe_package_name} - {int(time.time())}"
            )

        try:
            # Upload to Amazon S3
            with open(temp_file_path, "rb") as f:
                response = self.safe_api_call(
                    self.s3_client.put_object,
                    "S3 Object Upload",
                    key,
                    debug=self.debug_mode,
                    Bucket=bucket_name,
                    Key=key,
                    Body=f,
                )

            if response:
                version_id = response.get("VersionId", "")
                print(f"{Fore.GREEN}{self.get_message('status.firmware_uploaded', version_id)}{Style.RESET_ALL}")
                return version_id, key
            else:
                return None, key
        finally:
            os.remove(temp_file_path)

    def create_package_version(self):
        """Create a new package version with Amazon S3 integration"""
        print(f"\n{Fore.BLUE}{self.get_message('ui.create_version')}{Style.RESET_ALL}\n")

        # List available packages for selection
        packages_response = self.safe_api_call(
            self.iot_client.list_packages, "Package List", "all packages", debug=self.debug_mode
        )

        if not packages_response:
            print(f"{Fore.RED}{self.get_message('errors.failed_list_packages')}{Style.RESET_ALL}")
            return

        packages = packages_response.get("packageSummaries", [])

        if not packages:
            print(f"{Fore.YELLOW}{self.get_message('results.no_packages')}{Style.RESET_ALL}")
            return

        print(f"{Fore.GREEN}{self.get_message('ui.available_packages')}{Style.RESET_ALL}")
        for i, pkg in enumerate(packages, 1):
            print(f"{i}. {pkg['packageName']} (Created: {pkg.get('creationDate', 'Unknown')})")

        # Get package selection
        try:
            choice = int(input(f"\n{Fore.YELLOW}{self.get_message('prompts.select_package')}{Style.RESET_ALL}")) - 1
            if choice < 0 or choice >= len(packages):
                print(f"{Fore.RED}{self.get_message('errors.invalid_selection')}{Style.RESET_ALL}")
                return

            package_name = packages[choice]["packageName"]
            print(f"{Fore.GREEN}{self.get_message('status.selected_package', package_name)}{Style.RESET_ALL}")
        except (ValueError, IndexError):
            print(f"{Fore.RED}{self.get_message('errors.invalid_input')}{Style.RESET_ALL}")
            return

        self.educational_pause(
            self.get_message("learning.version_creation_title"),
            self.get_message("learning.version_creation_description"),
        )

        version = input(f"\n{Fore.YELLOW}{self.get_message('prompts.version_input')}{Style.RESET_ALL}").strip()

        if not version:
            print(f"{Fore.RED}{self.get_message('errors.version_empty')}{Style.RESET_ALL}")
            return

        # Check if version exists
        version_response = self.safe_api_call(
            self.iot_client.get_package_version,
            "Package Version Check",
            f"{package_name} v{version}",
            debug=self.debug_mode,
            packageName=package_name,
            versionName=version,
        )

        if version_response:
            print(f"{Fore.YELLOW}{self.get_message('errors.version_exists', version, package_name)}{Style.RESET_ALL}")
            return

        print(f"{Fore.GREEN}{self.get_message('status.version_available', version)}{Style.RESET_ALL}")

        self.educational_pause(
            self.get_message("learning.s3_bucket_title"),
            self.get_message("learning.s3_bucket_description"),
        )

        # Get or create Amazon S3 bucket
        bucket_name = self.get_s3_bucket()

        if not bucket_name:
            return

        self.educational_pause(
            self.get_message("learning.firmware_artifact_title"),
            self.get_message("learning.firmware_artifact_description"),
        )

        # Upload firmware to S3
        version_id, key = self.upload_firmware_to_s3(bucket_name, package_name, version)

        if not version_id:
            return

        self.educational_pause(
            self.get_message("learning.version_registration_title"),
            self.get_message("learning.version_registration_description"),
        )

        # Create package version
        version_response = self.safe_api_call(
            self.iot_client.create_package_version,
            "Package Version",
            f"{package_name} v{version}",
            debug=self.debug_mode,
            packageName=package_name,
            versionName=version,
            attributes={"signingKey": "SAMPLE-KEY-12345", "override": "true"},
            artifact={"s3Location": {"bucket": bucket_name, "key": key, "version": version_id}},
        )

        if version_response:
            print(f"{Fore.GREEN}{self.get_message('status.package_version_created')}{Style.RESET_ALL}")

            self.educational_pause(
                self.get_message("learning.version_publishing_title"),
                self.get_message("learning.version_publishing_description"),
            )

            # Publish the package version
            publish_response = self.safe_api_call(
                self.iot_client.update_package_version,
                "Package Version Publish",
                f"{package_name} v{version}",
                debug=self.debug_mode,
                packageName=package_name,
                versionName=version,
                action="PUBLISH",
            )

            if publish_response:
                print(f"{Fore.GREEN}{self.get_message('status.package_version_published')}{Style.RESET_ALL}")
                print(f"{Fore.GREEN}{self.get_message('ui.package_name_label', package_name)}{Style.RESET_ALL}")
                print(f"{Fore.GREEN}{self.get_message('ui.version_number', version)}{Style.RESET_ALL}")
                print(f"{Fore.GREEN}{self.get_message('ui.package_arn', version_response.get('packageVersionArn', 'N/A'))}{Style.RESET_ALL}")
                print(f"{Fore.GREEN}🪣 Amazon S3 Location: s3://{bucket_name}/{key}{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}{self.get_message('errors.failed_publish_version')}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}{self.get_message('errors.failed_create_version')}{Style.RESET_ALL}")

    def list_packages(self):
        """List all software packages with interactive options"""
        print(f"\n{Fore.BLUE}{self.get_message('ui.list_packages')}{Style.RESET_ALL}\n")

        response = self.safe_api_call(self.iot_client.list_packages, "Package List", "all packages", debug=self.debug_mode)

        if not response:
            print(f"{Fore.RED}{self.get_message('errors.failed_list_packages')}{Style.RESET_ALL}")
            return

        packages = response.get("packageSummaries", [])

        if not packages:
            print(f"{Fore.YELLOW}{self.get_message('results.no_packages_found')}{Style.RESET_ALL}")
            return

        print(f"{Fore.GREEN}{self.get_message('results.found_packages', len(packages))}{Style.RESET_ALL}")
        for i, pkg in enumerate(packages, 1):
            print(f"{i}. {pkg['packageName']} (Created: {pkg.get('creationDate', 'Unknown')})")

        # Ask if user wants to describe a package
        choice = input(f"\n{Fore.YELLOW}{self.get_message('prompts.describe_package')}{Style.RESET_ALL}").strip().lower()
        if choice in ["y", "yes"]:
            try:
                pkg_choice = int(input(f"{Fore.YELLOW}{self.get_message('prompts.select_package')}{Style.RESET_ALL}")) - 1
                if 0 <= pkg_choice < len(packages):
                    self.describe_package_interactive(packages[pkg_choice]["packageName"])
                else:
                    print(f"{Fore.RED}{self.get_message('errors.invalid_selection')}{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED}{self.get_message('errors.invalid_input')}{Style.RESET_ALL}")

    def describe_package(self):
        """Describe a specific package and its versions"""
        print(f"\n{Fore.BLUE}{self.get_message('ui.describe_package')}{Style.RESET_ALL}\n")

        package_name = input(f"{Fore.YELLOW}{self.get_message('prompts.package_name')}{Style.RESET_ALL}").strip()

        if not package_name:
            print(f"{Fore.RED}{self.get_message('errors.package_name_empty')}{Style.RESET_ALL}")
            return

        self.describe_package_interactive(package_name)

    def describe_package_interactive(self, package_name):
        """Describe a package with interactive version exploration"""
        # Get package details
        package_response = self.safe_api_call(
            self.iot_client.get_package, "Package Detail", package_name, debug=self.debug_mode, packageName=package_name
        )

        if not package_response:
            print(f"{Fore.RED}❌ Package '{package_name}' not found{Style.RESET_ALL}")
            return

        print(f"\n{Fore.GREEN}🏷️  Package Name: {package_response.get('packageName', 'N/A')}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}🔗 Package ARN: {package_response.get('packageArn', 'N/A')}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}📅 Created: {package_response.get('creationDate', 'N/A')}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}📝 Description: {package_response.get('description', 'None')}{Style.RESET_ALL}")

        # Get package versions
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
                print(f"\n{Fore.CYAN}📦 Versions ({len(versions)}):{Style.RESET_ALL}")
                for i, version in enumerate(versions, 1):
                    status = version.get("status", "N/A")
                    status_color = Fore.GREEN if status == "PUBLISHED" else Fore.YELLOW
                    print(
                        f"{i}. {version.get('versionName', 'N/A')} - {status_color}{status}{Style.RESET_ALL} (Created: {version.get('creationDate', 'N/A')})"
                    )

                # Ask if user wants to describe a version
                choice = input(f"\n{Fore.YELLOW}Describe a version? [y/N]: {Style.RESET_ALL}").strip().lower()
                if choice in ["y", "yes"]:
                    try:
                        ver_choice = int(input(f"{Fore.YELLOW}Select version number: {Style.RESET_ALL}")) - 1
                        if 0 <= ver_choice < len(versions):
                            self.describe_package_version_interactive(package_name, versions[ver_choice]["versionName"])
                        else:
                            print(f"{Fore.RED}❌ Invalid selection{Style.RESET_ALL}")
                    except ValueError:
                        print(f"{Fore.RED}❌ Invalid input{Style.RESET_ALL}")
            else:
                print(f"\n{Fore.YELLOW}📭 No versions found{Style.RESET_ALL}")

    def describe_package_version(self):
        """Describe a specific package version"""
        print(f"\n{Fore.BLUE}🔍 Describe AWS IoT Software Package Version{Style.RESET_ALL}\n")

        package_name = input(f"{Fore.YELLOW}Enter package name: {Style.RESET_ALL}").strip()

        if not package_name:
            print(f"{Fore.RED}❌ Package name cannot be empty{Style.RESET_ALL}")
            return

        version = input(f"{Fore.YELLOW}Enter version: {Style.RESET_ALL}").strip()

        if not version:
            print(f"{Fore.RED}❌ Version cannot be empty{Style.RESET_ALL}")
            return

        self.describe_package_version_interactive(package_name, version)

    def describe_package_version_interactive(self, package_name, version):
        """Describe a package version with full details"""
        version_response = self.safe_api_call(
            self.iot_client.get_package_version,
            "Package Version Detail",
            f"{package_name} v{version}",
            debug=self.debug_mode,
            packageName=package_name,
            versionName=version,
        )

        if not version_response:
            print(f"{Fore.RED}❌ Package version '{package_name}' v{version} not found{Style.RESET_ALL}")
            return

        print(f"\n{Fore.GREEN}🏷️  Package: {version_response.get('packageName', 'N/A')}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}📦 Version: {version_response.get('versionName', 'N/A')}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}🔗 ARN: {version_response.get('packageVersionArn', 'N/A')}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}📅 Created: {version_response.get('creationDate', 'N/A')}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}📝 Description: {version_response.get('description', 'None')}{Style.RESET_ALL}")

        status = version_response.get("status", "N/A")
        status_color = Fore.GREEN if status == "PUBLISHED" else Fore.YELLOW
        print(f"{Fore.GREEN}📊 Status: {status_color}{status}{Style.RESET_ALL}")

        # Show artifact details
        artifact = version_response.get("artifact", {})
        if artifact:
            s3_location = artifact.get("s3Location", {})
            if s3_location:
                bucket = s3_location.get("bucket", "N/A")
                key = s3_location.get("key", "N/A")
                version_id = s3_location.get("version", "N/A")

                print(f"\n{Fore.CYAN}🪣 S3 Artifact:{Style.RESET_ALL}")
                print(f"{Fore.GREEN}  Bucket: {bucket}{Style.RESET_ALL}")
                print(f"{Fore.GREEN}  Key: {key}{Style.RESET_ALL}")
                print(f"{Fore.GREEN}  Version: {version_id}{Style.RESET_ALL}")

        # Show attributes
        attributes = version_response.get("attributes", {})
        if attributes:
            print(f"\n{Fore.CYAN}🏷️  Attributes:{Style.RESET_ALL}")
            for attr_key, attr_value in attributes.items():
                print(f"{Fore.GREEN}  {attr_key}: {attr_value}{Style.RESET_ALL}")

    def check_package_configuration(self):
        """Check current package configuration status"""
        print(f"\n{Fore.BLUE}🔍 AWS IoT Software Package Catalog Configuration Status{Style.RESET_ALL}\n")

        self.educational_pause(
            "Package Configuration - Jobs to Shadow Integration",
            "AWS IoT Software Package Catalog Configuration controls the integration between AWS IoT Jobs and AWS IoT Device Shadows.\n"
            "When enabled, successful AWS IoT Jobs completions automatically update the device's $package shadow\n"
            "with the new firmware version. This creates an audit trail and ensures AWS IoT device inventory\n"
            "accuracy without manual intervention. The configuration requires an AWS Identity and Access Management (IAM) role with permissions\n"
            "to read and update AWS IoT Device Shadows.\n\n"
            "🔄 NEXT: We'll check the current package configuration status",
        )

        response = self.safe_api_call(
            self.iot_client.get_package_configuration, "Package Configuration", "global config", debug=self.debug_mode
        )

        if response:
            version_config = response.get("versionUpdateByJobsConfig", {})

            enabled = version_config.get("enabled", False)
            role_arn = version_config.get("roleArn", "Not configured")

            status_color = Fore.GREEN if enabled else Fore.RED
            status_text = "ENABLED" if enabled else "DISABLED"

            print(f"{Fore.GREEN}📊 Configuration Status: {status_color}{status_text}{Style.RESET_ALL}")
            print(f"{Fore.GREEN}🔗 IAM Role ARN: {role_arn}{Style.RESET_ALL}")

            if enabled:
                print(f"\n{Fore.CYAN}✅ Package configuration is active:{Style.RESET_ALL}")
                print(f"{Fore.CYAN}   • Job completions will update device $package shadows{Style.RESET_ALL}")
                print(f"{Fore.CYAN}   • Firmware versions are automatically tracked{Style.RESET_ALL}")
                print(f"{Fore.CYAN}   • Device inventory stays synchronized{Style.RESET_ALL}")
            else:
                print(f"\n{Fore.YELLOW}⚠️  Package configuration is disabled:{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}   • Job completions will NOT update device shadows{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}   • Manual shadow updates required{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}   • Device inventory may become outdated{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}❌ Failed to get package configuration{Style.RESET_ALL}")

    def create_package_config_role(self):
        """Create IAM role for package configuration"""
        print(
            f"{Fore.BLUE}🔐 Creating AWS Identity and Access Management (IAM) role for AWS IoT Software Package Catalog configuration...{Style.RESET_ALL}"
        )

        role_name = f"IoTPackageConfigRole-{self.region}-{self.account_id[:8]}"
        trust_policy = {
            "Version": "2012-10-17",
            "Statement": [{"Effect": "Allow", "Principal": {"Service": "iot.amazonaws.com"}, "Action": "sts:AssumeRole"}],
        }

        # Check if role exists
        try:
            self.iam_client.get_role(RoleName=role_name)
            print(f"{Fore.GREEN}✅ Package config role already exists{Style.RESET_ALL}")
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] != "NoSuchEntity":
                print(f"{Fore.RED}❌ Error checking role: {e.response['Error']['Message']}{Style.RESET_ALL}")
                return False

        # Create role
        role_response = self.safe_api_call(
            self.iam_client.create_role,
            "IAM Role",
            role_name,
            debug=self.debug_mode,
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            MaxSessionDuration=14400,  # 4 hours
        )

        if not role_response:
            return False

        print(f"{Fore.GREEN}✅ Package config role created{Style.RESET_ALL}")

        package_config_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": "iot:DescribeEndpoint",
                    "Resource": "*",
                    "Condition": {"StringEquals": {"aws:RequestedRegion": self.region}},
                },
                {
                    "Effect": "Allow",
                    "Action": ["iot:GetThingShadow", "iot:UpdateThingShadow"],
                    "Resource": [f"arn:aws:iot:{self.region}:{self.account_id}:thing/*/$package"],
                    "Condition": {"StringEquals": {"aws:RequestedRegion": self.region}},
                },
            ],
        }

        # Wait for role to be ready and attach policy
        time.sleep(3)  # AWS IAM role propagation delay  # nosemgrep: arbitrary-sleep
        policy_response = self.safe_api_call(
            self.iam_client.put_role_policy,
            "IAM Role Policy",
            "PackageConfigPolicy",
            debug=self.debug_mode,
            RoleName=role_name,
            PolicyName="PackageConfigPolicy",
            PolicyDocument=json.dumps(package_config_policy),
        )

        if policy_response:
            print(f"{Fore.GREEN}✅ Package config policy attached{Style.RESET_ALL}")
            return True
        else:
            print(f"{Fore.RED}❌ Failed to attach package config policy{Style.RESET_ALL}")
            return False

    def enable_package_configuration(self):
        """Enable package configuration with IAM role creation"""
        print(f"\n{Fore.BLUE}🔧 Enable AWS IoT Software Package Catalog Configuration{Style.RESET_ALL}\n")

        self.educational_pause(
            "Enabling Package Configuration - Automated Shadow Updates",
            "Enabling AWS IoT Software Package Catalog configuration requires an AWS Identity and Access Management (IAM) role that allows AWS IoT to update AWS IoT Device\n"
            "Shadows. The IoTPackageConfigRole grants permissions to read and write $package shadows\n"
            "for all AWS IoT devices. Once enabled, successful AWS IoT Jobs completions will automatically update the\n"
            "AWS IoT device's firmware version in its AWS IoT Device Shadow, creating a reliable audit trail.\n\n"
            "🔄 NEXT: We'll create the IAM role and enable the configuration",
        )

        # Create IAM role first
        if not self.create_package_config_role():
            return

        role_arn = f"arn:aws:iam::{self.account_id}:role/IoTPackageConfigRole-{self.region}-{self.account_id[:8]}"

        # Wait for role to be ready
        time.sleep(2)  # AWS IAM role propagation delay  # nosemgrep: arbitrary-sleep

        response = self.safe_api_call(
            self.iot_client.update_package_configuration,
            "Package Configuration Update",
            "enable config",
            debug=self.debug_mode,
            versionUpdateByJobsConfig={"enabled": True, "roleArn": role_arn},
        )

        if response:
            print(f"{Fore.GREEN}✅ Package configuration enabled successfully{Style.RESET_ALL}")
            print(f"{Fore.GREEN}🔗 Using IAM Role: {role_arn}{Style.RESET_ALL}")
            print(f"\n{Fore.CYAN}📋 What this enables:{Style.RESET_ALL}")
            print(f"{Fore.CYAN}   • Automatic $package shadow updates on job completion{Style.RESET_ALL}")
            print(f"{Fore.CYAN}   • Real-time firmware version tracking{Style.RESET_ALL}")
            print(f"{Fore.CYAN}   • Synchronized device inventory{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}❌ Failed to enable package configuration{Style.RESET_ALL}")

    def disable_package_configuration(self):
        """Disable package configuration"""
        print(f"\n{Fore.BLUE}🔧 Disable AWS IoT Software Package Catalog Configuration{Style.RESET_ALL}\n")

        self.educational_pause(
            "Disabling Package Configuration - Manual Shadow Management",
            "Disabling AWS IoT Software Package Catalog configuration stops automatic AWS IoT Device Shadow updates when AWS IoT Jobs complete.\n"
            "You'll need to manually update AWS IoT Device Shadows to track firmware versions. This might be\n"
            "useful for testing scenarios or when you want full control over AWS IoT Device Shadow updates. The AWS Identity and Access Management (IAM)\n"
            "role remains available for future re-enabling.\n\n"
            "🔄 NEXT: We'll disable automatic shadow updates",
        )

        response = self.safe_api_call(
            self.iot_client.update_package_configuration,
            "Package Configuration Update",
            "disable config",
            debug=self.debug_mode,
            versionUpdateByJobsConfig={"enabled": False},
        )

        if response:
            print(f"{Fore.GREEN}✅ Package configuration disabled successfully{Style.RESET_ALL}")
            print(f"\n{Fore.YELLOW}⚠️  Important changes:{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}   • Job completions will NOT update device shadows{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}   • Manual shadow updates required for version tracking{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}   • Device inventory may become outdated{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}❌ Failed to disable package configuration{Style.RESET_ALL}")

    def check_device_package_version(self):
        """Check package version for a specific device"""
        print(f"\n{Fore.BLUE}🔍 Check AWS IoT Device Package Version{Style.RESET_ALL}\n")

        self.educational_pause(
            "Device Package Version Tracking - $package Shadow Inspection",
            "Each AWS IoT device maintains a $package shadow that tracks its current firmware version.\n"
            "This AWS IoT Device Shadow is automatically updated when AWS IoT Jobs complete (if AWS IoT Software Package Catalog configuration\n"
            "is enabled) or can be manually updated. The AWS IoT Device Shadow contains the package name and\n"
            "version for each AWS IoT Thing Type, providing accurate AWS IoT device inventory information.\n\n"
            "🔄 NEXT: We'll retrieve the $package shadow for a specific device",
        )

        while True:
            device_name = input(f"{Fore.YELLOW}Enter device name (e.g., Vehicle-VIN-001): {Style.RESET_ALL}").strip()

            if not device_name:
                print(f"{Fore.RED}❌ Device name cannot be empty{Style.RESET_ALL}")
                continue

            # Get device's $package shadow
            try:
                response = self.iot_data_client.get_thing_shadow(thingName=device_name, shadowName="$package")

                shadow_data = json.loads(response["payload"].read())
                state = shadow_data.get("state", {})
                reported = state.get("reported", {})

                if not reported:
                    print(f"{Fore.YELLOW}📭 Device '{device_name}' has no reported package versions{Style.RESET_ALL}")
                else:
                    print(f"{Fore.GREEN}📱 Device: {device_name}{Style.RESET_ALL}")
                    print(f"{Fore.GREEN}📦 Package Information:{Style.RESET_ALL}")

                    # Display package versions for each thing type
                    for package_name, package_info in reported.items():
                        if isinstance(package_info, dict) and "version" in package_info:
                            version = package_info["version"]
                            attributes = package_info.get("attributes", {})

                            print(f"\n{Fore.CYAN}  📋 Package: {package_name}{Style.RESET_ALL}")
                            print(f"{Fore.CYAN}  🔢 Version: {version}{Style.RESET_ALL}")

                            if attributes:
                                print(f"{Fore.CYAN}  🏷️  Attributes:{Style.RESET_ALL}")
                                for attr_key, attr_value in attributes.items():
                                    print(f"{Fore.CYAN}    • {attr_key}: {attr_value}{Style.RESET_ALL}")

                    # Show shadow metadata
                    metadata = shadow_data.get("metadata", {})
                    if metadata:
                        reported_meta = metadata.get("reported", {})
                        if reported_meta:
                            print(f"\n{Fore.YELLOW}📅 Last Updated:{Style.RESET_ALL}")
                            for package_name, meta_info in reported_meta.items():
                                if isinstance(meta_info, dict) and "timestamp" in meta_info:
                                    timestamp = meta_info["timestamp"]
                                    print(f"{Fore.YELLOW}  • {package_name}: {timestamp}{Style.RESET_ALL}")

            except ClientError:
                print(f"{Fore.RED}❌ Failed to get $package shadow for device '{device_name}'{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}💡 This could mean:{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}   • Device doesn't exist{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}   • Device has no $package shadow{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}   • No firmware has been deployed to this device{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}❌ Error processing shadow data: {str(e)}{Style.RESET_ALL}")

            # Ask if user wants to check another device
            choice = input(f"\n{Fore.YELLOW}Check another device? [y/N]: {Style.RESET_ALL}").strip().lower()
            if choice not in ["y", "yes"]:
                break

    def update_device_shadow_parallel(self, device_name, thing_type, target_version):
        """Update device shadow in parallel for revert operation"""
        with self.shadow_semaphore:
            shadow_payload = {"state": {"reported": {thing_type: {"version": target_version, "attributes": {}}}}}

            try:
                self.iot_data_client.update_thing_shadow(
                    thingName=device_name, shadowName="$package", payload=json.dumps(shadow_payload)
                )
                return f"{Fore.GREEN}✅ {device_name}: Reverted to version {target_version}{Style.RESET_ALL}"
            except Exception as e:
                return f"{Fore.RED}❌ {device_name}: Failed to revert - {str(e)}{Style.RESET_ALL}"

    def revert_device_versions(self):
        """Revert device versions using Fleet Indexing"""
        print(f"\n{Fore.BLUE}🔄 Revert AWS IoT Device Versions{Style.RESET_ALL}\n")

        self.educational_pause(
            "Version Rollback - Fleet-wide Firmware Management",
            "Version rollback uses AWS IoT Fleet Indexing to find AWS IoT devices with specific firmware versions\n"
            "and updates their $package AWS IoT Device Shadows to reflect the rollback. This maintains accurate\n"
            "AWS IoT device inventory without requiring actual firmware downloads. It's useful for quickly\n"
            "marking AWS IoT devices as reverted in your management system before deploying older firmware.\n\n"
            "🔄 NEXT: We'll search for devices and update their package shadows",
        )

        # Get thing type
        thing_type = input(f"{Fore.YELLOW}Enter thing type (e.g., SedanVehicle): {Style.RESET_ALL}").strip()
        if not thing_type:
            print(f"{Fore.RED}❌ Thing type is required{Style.RESET_ALL}")
            return

        # Get target version
        target_version = input(f"{Fore.YELLOW}Enter target version (e.g., 1.0.0): {Style.RESET_ALL}").strip()
        if not target_version:
            print(f"{Fore.RED}❌ Target version is required{Style.RESET_ALL}")
            return

        # Sanitize inputs to prevent XSS
        import html

        thing_type = html.escape(thing_type)
        target_version = html.escape(target_version)

        # Find devices to revert
        print(f"{Fore.BLUE}🔍 Searching for devices to revert...{Style.RESET_ALL}")

        query = f"thingTypeName:{thing_type} AND shadow.name.$package.reported.{thing_type}.version:* AND NOT shadow.name.$package.reported.{thing_type}.version:{target_version}"

        # Collect all devices with pagination
        device_names = []
        next_token = None

        while True:
            search_params = {"indexName": "AWS_Things", "queryString": query, "maxResults": 250}
            if next_token:
                search_params["nextToken"] = next_token

            search_response = self.safe_api_call(
                self.iot_client.search_index,
                "Fleet Indexing Search",
                "devices to revert",
                debug=self.debug_mode,
                **search_params,
            )

            if not search_response:
                print(f"{Fore.RED}❌ Failed to search for devices{Style.RESET_ALL}")
                return

            things = search_response.get("things", [])
            batch_names = [thing.get("thingName") for thing in things if thing.get("thingName")]
            device_names.extend(batch_names)

            next_token = search_response.get("nextToken")
            if not next_token:
                break

        if not device_names:
            print(
                f"{Fore.GREEN}✅ All devices of type '{thing_type}' are already on version '{target_version}'{Style.RESET_ALL}"
            )
            return

        print(f"{Fore.GREEN}📊 Found {len(device_names)} devices to revert to version {target_version}{Style.RESET_ALL}")

        # Show device names that will be reverted
        print(f"\n{Fore.CYAN}📋 Devices to revert:{Style.RESET_ALL}")
        for i, device_name in enumerate(device_names, 1):
            print(f"{Fore.CYAN}  {i}. {device_name}{Style.RESET_ALL}")
            if i >= 10 and len(device_names) > 10:
                remaining = len(device_names) - 10
                print(f"{Fore.CYAN}  ... and {remaining} more devices{Style.RESET_ALL}")
                break

        # Confirm revert
        print(
            f"\n{Fore.YELLOW}⚠️  WARNING: This will update {len(device_names)} device shadows to version '{target_version}'{Style.RESET_ALL}"
        )
        confirm = input(f"\n{Fore.YELLOW}Type 'REVERT' to confirm: {Style.RESET_ALL}")

        if confirm != "REVERT":
            print(f"{Fore.YELLOW}❌ Version revert cancelled{Style.RESET_ALL}")
            return

        print(f"\n{Fore.BLUE}🚀 Updating device shadows...{Style.RESET_ALL}")

        # Update shadows
        if self.debug_mode:
            print(f"{Fore.BLUE}🔧 Updating shadows sequentially (debug mode)...{Style.RESET_ALL}")
            success_count = 0
            for i, device_name in enumerate(device_names, 1):
                result = self.update_device_shadow_parallel(device_name, thing_type, target_version)
                print(result)
                if "✅" in result:
                    success_count += 1

                if i % 10 == 0 or i == len(device_names):
                    print(
                        f"{Fore.CYAN}📊 Progress: {i}/{len(device_names)} devices processed, {success_count} successful{Style.RESET_ALL}"
                    )
        else:
            print(f"{Fore.BLUE}🔧 Updating shadows in parallel...{Style.RESET_ALL}")
            with ThreadPoolExecutor(max_workers=20) as executor:
                futures = [
                    executor.submit(self.update_device_shadow_parallel, device_name, thing_type, target_version)
                    for device_name in device_names
                ]

                success_count = 0
                completed = 0
                for future in as_completed(futures):
                    completed += 1
                    result = future.result()
                    print(result)
                    if "✅" in result:
                        success_count += 1

                    if completed % 10 == 0 or completed == len(device_names):
                        print(
                            f"{Fore.CYAN}📊 Progress: {completed}/{len(device_names)} devices processed, {success_count} successful{Style.RESET_ALL}"
                        )

        print(f"\n{Fore.GREEN}✅ Version revert completed: {success_count}/{len(device_names)} successful{Style.RESET_ALL}")

    def educational_pause(self, title, description):
        """Pause execution with educational content"""
        print(f"\n{Fore.YELLOW}{self.get_message('learning_goal')} {title}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{description}{Style.RESET_ALL}")
        input(f"\n{Fore.GREEN}{self.get_message('prompts.press_enter')}{Style.RESET_ALL}")
        print()

    def run(self):
        """Main execution flow"""
        if not self.print_header():
            return

        # Get debug mode preference
        self.get_debug_mode()

        # Educational pause
        self.educational_pause(
            self.get_message("learning.package_management_title"),
            self.get_message("learning.package_management_description"),
        )

        while True:
            # Get operation choice
            operation = self.get_operation_choice()

            if operation == 1:
                self.create_package()
            elif operation == 2:
                self.create_package_version()
            elif operation == 3:
                self.list_packages()
            elif operation == 4:
                self.describe_package()
            elif operation == 5:
                self.describe_package_version()
            elif operation == 6:
                self.check_package_configuration()
            elif operation == 7:
                self.enable_package_configuration()
            elif operation == 8:
                self.disable_package_configuration()
            elif operation == 9:
                self.check_device_package_version()
            elif operation == 10:
                self.revert_device_versions()
            elif operation == 11:
                print(f"\n{Fore.GREEN}{self.get_message('ui.goodbye')}{Style.RESET_ALL}")
                break

            # Ask if user wants to continue (except for exit)
            if operation != 11:
                print(f"\n{Fore.CYAN}{self.get_message('ui.separator_line')}{Style.RESET_ALL}")
                continue_choice = (
                    input(f"{Fore.YELLOW}{self.get_message('prompts.continue_operation')}{Style.RESET_ALL}").strip().lower()
                )
                if continue_choice in ["n", "no"]:
                    print(f"\n{Fore.GREEN}{self.get_message('ui.goodbye')}{Style.RESET_ALL}")
                    break
                print()


if __name__ == "__main__":
    # Initialize language
    USER_LANG = get_language()
    messages = load_messages("manage_packages", USER_LANG)
    
    manager = PackageManager()
    try:
        manager.run()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}{manager.get_message('ui.cancelled')}{Style.RESET_ALL}")
        sys.exit(0)
