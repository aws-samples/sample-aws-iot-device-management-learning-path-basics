#!/usr/bin/env python3

import json
import os
import random
import re
import sys
import tempfile
import time
import uuid
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from threading import Semaphore

import boto3
from botocore.exceptions import ClientError
from colorama import Fore, Style, init

# Initialize colorama
init()

# Configuration
CONTINENTS = {
    1: {
        "name": "North America",
        "countries": [
            "US",
            "CA",
            "MX",
            "GT",
            "BZ",
            "SV",
            "HN",
            "NI",
            "CR",
            "PA",
            "CU",
            "JM",
            "HT",
            "DO",
            "BS",
            "BB",
            "TT",
            "GD",
            "VC",
            "LC",
            "AG",
            "KN",
            "DM",
        ],
    },
    2: {"name": "South America", "countries": ["BR", "AR", "CL", "CO", "PE", "VE", "EC", "BO", "PY", "UY", "GY", "SR", "GF"]},
    3: {
        "name": "Europe",
        "countries": [
            "DE",
            "FR",
            "GB",
            "IT",
            "ES",
            "NL",
            "BE",
            "AT",
            "CH",
            "PT",
            "GR",
            "SE",
            "NO",
            "DK",
            "FI",
            "IE",
            "PL",
            "CZ",
            "HU",
            "SK",
            "SI",
            "HR",
            "BA",
            "RS",
            "ME",
            "MK",
            "AL",
            "BG",
            "RO",
            "MD",
            "UA",
            "BY",
            "LT",
            "LV",
            "EE",
            "RU",
            "IS",
            "MT",
            "CY",
            "LU",
            "LI",
            "AD",
            "MC",
            "SM",
            "VA",
        ],
    },
    4: {
        "name": "Asia",
        "countries": [
            "CN",
            "JP",
            "IN",
            "KR",
            "SG",
            "TH",
            "VN",
            "MY",
            "ID",
            "PH",
            "MM",
            "KH",
            "LA",
            "BN",
            "TL",
            "MN",
            "KZ",
            "UZ",
            "TM",
            "TJ",
            "KG",
            "AF",
            "PK",
            "BD",
            "LK",
            "MV",
            "BT",
            "NP",
            "IR",
            "IQ",
            "SY",
            "LB",
            "JO",
            "IL",
            "PS",
            "SA",
            "YE",
            "OM",
            "AE",
            "QA",
            "BH",
            "KW",
            "TR",
            "GE",
            "AM",
            "AZ",
        ],
    },
    5: {
        "name": "Africa",
        "countries": [
            "ZA",
            "NG",
            "EG",
            "KE",
            "MA",
            "DZ",
            "TN",
            "LY",
            "SD",
            "SS",
            "ET",
            "ER",
            "DJ",
            "SO",
            "UG",
            "TZ",
            "RW",
            "BI",
            "CD",
            "CG",
            "CF",
            "CM",
            "TD",
            "NE",
            "ML",
            "BF",
            "CI",
            "GH",
            "TG",
            "BJ",
            "SN",
            "GM",
            "GW",
            "GN",
            "SL",
            "LR",
            "MR",
            "CV",
            "ST",
            "GQ",
            "GA",
            "AO",
            "NA",
            "BW",
            "ZW",
            "ZM",
            "MW",
            "MZ",
            "SZ",
            "LS",
            "MG",
            "MU",
            "SC",
            "KM",
        ],
    },
    6: {
        "name": "Oceania",
        "countries": [
            "AU",
            "NZ",
            "FJ",
            "PG",
            "SB",
            "VU",
            "NC",
            "PF",
            "WS",
            "TO",
            "KI",
            "TV",
            "NR",
            "PW",
            "FM",
            "MH",
            "GU",
            "AS",
            "MP",
            "CK",
            "NU",
            "TK",
        ],
    },
    7: {"name": "Antarctica", "countries": ["AQ"]},
}


class IoTProvisioner:
    def __init__(self):
        self.region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        self.debug_mode = False
        self.iot_client = None
        self.s3_client = None
        self.iam_client = None
        self.sts_client = None
        self.account_id = None

        # Rate limiting semaphores for AWS API limits
        self.thing_type_semaphore = Semaphore(8)
        self.thing_creation_semaphore = Semaphore(80)
        self.package_semaphore = Semaphore(8)

    def safe_api_call(self, func, operation_name, resource_name, debug=False, **kwargs):
        """Safely execute AWS API call with error handling and optional debug info"""
        try:
            if debug or self.debug_mode:
                print(f"\n🔍 DEBUG: {operation_name}: {resource_name}")
                print(f"📤 API Call: {func.__name__}")
                print("📥 Input Parameters:")
                print(json.dumps(kwargs, indent=2, default=str))
            else:
                print(f"Creating {operation_name}: {resource_name}")

            response = func(**kwargs)

            if debug or self.debug_mode:
                print("📤 API Response:")
                print(json.dumps(response, indent=2, default=str))

            print(f"✅ Created {operation_name}: {resource_name}")
            time.sleep(0.125)  # Rate limiting  # nosemgrep: arbitrary-sleep
            return response
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code in ["ResourceAlreadyExistsException", "ConflictException"]:
                print(f"⚠️  {operation_name} {resource_name} already exists, skipping")
            else:
                print(f"❌ Error creating {operation_name} {resource_name}: {e.response['Error']['Message']}")
                if debug or self.debug_mode:
                    print("🔍 DEBUG: Full error response:")
                    print(json.dumps(e.response, indent=2, default=str))
            time.sleep(0.125)  # nosemgrep: arbitrary-sleep
            return None
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            if debug or self.debug_mode:
                import traceback

                print("🔍 DEBUG: Full traceback:")
                traceback.print_exc()
            time.sleep(0.125)  # nosemgrep: arbitrary-sleep
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

            print("✅ AWS clients initialized")
            if self.debug_mode:
                print("🔍 DEBUG: Client configuration:")
                print(f"   IoT Service: {self.iot_client.meta.service_model.service_name}")
                print(f"   API Version: {self.iot_client.meta.service_model.api_version}")

            return True
        except Exception as e:
            print(f"❌ Error initializing AWS clients: {str(e)}")
            return False

    def print_header(self):
        print(f"{Fore.CYAN}🚀 AWS IoT Provisioning Script (Boto3){Style.RESET_ALL}")
        print(f"{Fore.CYAN}======================================{Style.RESET_ALL}")

        print(f"{Fore.BLUE}📍 AWS Configuration:{Style.RESET_ALL}")
        print(f"{Fore.GREEN}   Account ID: {self.account_id}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}   Region: {self.region}{Style.RESET_ALL}")
        print()

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

    def get_thing_types(self):
        """Get thing types from user input"""
        default_types = "SedanVehicle,SUVVehicle,TruckVehicle"
        print(
            f"{Fore.YELLOW}📝 Enter thing types (comma-separated, e.g., SedanVehicle,SUVVehicle,TruckVehicle):{Style.RESET_ALL}"
        )
        print(f"{Fore.CYAN}   Default: {default_types}{Style.RESET_ALL}")
        thing_types_input = input(f"{Fore.YELLOW}   Your choice [{default_types}]: {Style.RESET_ALL}").strip()

        if not thing_types_input:
            thing_types_input = default_types
            print(f"{Fore.GREEN}✅ Using default: {default_types}{Style.RESET_ALL}")

        return [t.strip() for t in thing_types_input.split(",")]

    def get_continent_choice(self):
        """Get continent selection from user"""
        default_choice = 1
        print(f"{Fore.BLUE}🌍 Select continent:{Style.RESET_ALL}")
        for num, info in CONTINENTS.items():
            marker = " (default)" if num == default_choice else ""
            print(f"{Fore.CYAN}{num}. {info['name']}{marker}{Style.RESET_ALL}")

        while True:
            try:
                user_input = input(
                    f"{Fore.YELLOW}Enter choice [1-{len(CONTINENTS)}] [{default_choice}]: {Style.RESET_ALL}"
                ).strip()
                if not user_input:
                    print(f"{Fore.GREEN}✅ Using default: {CONTINENTS[default_choice]['name']}{Style.RESET_ALL}")
                    return default_choice

                choice = int(user_input)
                if 1 <= choice <= len(CONTINENTS):
                    return choice
                print(f"{Fore.RED}❌ Invalid choice. Please enter 1-{len(CONTINENTS)}{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED}❌ Please enter a valid number{Style.RESET_ALL}")

    def get_country_selection(self, continent_choice):
        """Get country selection from user"""
        continent_info = CONTINENTS[continent_choice]
        available_countries = continent_info["countries"]
        max_countries = len(available_countries)
        default_selection = "3" if continent_choice == 1 else "2"

        print(
            f"\n{Fore.BLUE}🇦 Available countries in {continent_info['name']}: {', '.join(available_countries)}{Style.RESET_ALL}"
        )
        print(f"{Fore.CYAN}Options:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}1. Enter a number (1-{max_countries}) to use first N countries{Style.RESET_ALL}")
        print(f"{Fore.CYAN}2. Enter comma-separated country codes (e.g., US,CA,MX){Style.RESET_ALL}")
        print(f"{Fore.CYAN}   Default: {default_selection} (first {default_selection} countries){Style.RESET_ALL}")

        while True:
            user_input = input(
                f"{Fore.YELLOW}📊 Enter number or country codes [{default_selection}]: {Style.RESET_ALL}"
            ).strip()

            if not user_input:
                count = int(default_selection)
                selected = available_countries[:count]
                print(f"{Fore.GREEN}✅ Using default: {', '.join(selected)}{Style.RESET_ALL}")
                return selected

            try:
                count = int(user_input)
                if 1 <= count <= max_countries:
                    return available_countries[:count]
                print(f"{Fore.RED}❌ Please enter a number between 1 and {max_countries}{Style.RESET_ALL}")
                continue
            except ValueError:
                pass

            if "," in user_input or len(user_input) == 2:
                country_codes = [code.strip().upper() for code in user_input.split(",")]
                invalid_codes = [code for code in country_codes if code not in available_countries]

                if invalid_codes:
                    print(f"{Fore.RED}❌ Invalid country codes: {', '.join(invalid_codes)}{Style.RESET_ALL}")
                    print(f"{Fore.YELLOW}Available codes: {', '.join(available_countries)}{Style.RESET_ALL}")
                    continue

                if not country_codes:
                    print(f"{Fore.RED}❌ Please provide at least one country code{Style.RESET_ALL}")
                    continue

                return country_codes

            print(f"{Fore.RED}❌ Invalid input. Enter a number or comma-separated country codes{Style.RESET_ALL}")

    def get_package_versions(self):
        """Get package versions from user input"""
        default_versions = "1.0.0,1.1.0"
        print(f"{Fore.YELLOW}📝 Enter package versions (comma-separated, e.g., 1.0.0,1.1.0,2.0.0):{Style.RESET_ALL}")
        print(f"{Fore.CYAN}   Default: {default_versions}{Style.RESET_ALL}")
        versions_input = input(f"{Fore.YELLOW}   Your choice [{default_versions}]: {Style.RESET_ALL}").strip()

        if not versions_input:
            print(f"{Fore.GREEN}✅ Using default: {default_versions}{Style.RESET_ALL}")
            return ["1.0.0", "1.1.0"]

        versions = [v.strip() for v in versions_input.split(",")]

        # Basic validation
        for version in versions:
            if not version or not all(c.isdigit() or c == "." for c in version):
                print(f"{Fore.RED}❌ Invalid version format: {version}{Style.RESET_ALL}")
                return self.get_package_versions()

        return versions

    def get_device_count(self):
        """Get number of devices to create"""
        default_count = "100"
        while True:
            try:
                user_input = input(
                    f"{Fore.YELLOW}📊 Enter number of devices to create [{default_count}]: {Style.RESET_ALL}"
                ).strip()

                if not user_input:
                    print(f"{Fore.GREEN}✅ Using default: {default_count}{Style.RESET_ALL}")
                    return int(default_count)

                count = int(user_input)
                if count > 0:
                    return count
                print(f"{Fore.RED}❌ Please enter a positive number{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED}❌ Please enter a valid number{Style.RESET_ALL}")

    def create_single_thing_type(self, thing_type, index, total):
        """Create or undeprecate a single thing type"""
        with self.thing_type_semaphore:
            print(f"{Fore.BLUE}📋 Processing thing type {index}/{total}: {Fore.YELLOW}{thing_type}{Style.RESET_ALL}")

            # Try to create thing type first (more efficient than checking existence)
            description = f"Template for {thing_type.replace('Vehicle', ' Vehicle')} category"

            try:
                try:
                    if self.debug_mode:
                        print(f"\n🔍 DEBUG: Thing Type Create: {thing_type}")
                        print("📤 API Call: create_thing_type")
                        print("📥 Input Parameters:")
                        params = {
                            "thingTypeName": thing_type,
                            "thingTypeProperties": {
                                "thingTypeDescription": description,
                                "searchableAttributes": ["customerId", "country", "manufacturingDate"],
                            },
                        }
                        print(json.dumps(params, indent=2))

                    response = self.iot_client.create_thing_type(
                        thingTypeName=thing_type,
                        thingTypeProperties={
                            "thingTypeDescription": description,
                            "searchableAttributes": ["customerId", "country", "manufacturingDate"],
                        },
                    )

                    if self.debug_mode:
                        print("📤 API Response:")
                        print(json.dumps(response, indent=2, default=str))

                    print(f"{Fore.GREEN}✅ Created thing type: {thing_type}{Style.RESET_ALL}")
                    return True
                except ClientError as e:
                    if e.response["Error"]["Code"] == "ResourceAlreadyExistsException":
                        print(f"{Fore.CYAN}🔍 Thing type exists, checking deprecation status...{Style.RESET_ALL}")
                        # Check if deprecated
                        describe_response = self.iot_client.describe_thing_type(thingTypeName=thing_type)
                        deprecated = describe_response.get("thingTypeMetadata", {}).get("deprecated", False)
                        print(f"{Fore.CYAN}📊 Thing type '{thing_type}' deprecated: {deprecated}{Style.RESET_ALL}")

                        if deprecated:
                            print(f"{Fore.YELLOW}🔄 Undeprecating thing type...{Style.RESET_ALL}")
                            self.iot_client.deprecate_thing_type(thingTypeName=thing_type, undoDeprecate=True)
                            print(f"{Fore.GREEN}✅ Thing type undeprecated: {thing_type}{Style.RESET_ALL}")
                        else:
                            print(f"{Fore.GREEN}✅ Thing type already active: {thing_type}{Style.RESET_ALL}")
                        return True
                    else:
                        print(f"{Fore.RED}❌ Failed to create thing type: {e.response['Error']['Message']}{Style.RESET_ALL}")
                        return False

            except Exception as e:
                print(f"{Fore.RED}❌ Error processing thing type '{thing_type}': {str(e)}{Style.RESET_ALL}")
                return False

    def create_thing_types(self, thing_types):
        """Create or undeprecate thing types in parallel (or sequential in debug mode)"""
        if self.debug_mode:
            print(f"{Fore.BLUE}🔧 Creating/updating AWS IoT thing types sequentially (debug mode)...{Style.RESET_ALL}")
            success_count = 0
            for i, thing_type in enumerate(thing_types, 1):
                if self.create_single_thing_type(thing_type, i, len(thing_types)):
                    success_count += 1
        else:
            print(f"{Fore.BLUE}🔧 Creating/updating AWS IoT thing types in parallel...{Style.RESET_ALL}")
            with ThreadPoolExecutor(max_workers=8) as executor:
                futures = [
                    executor.submit(self.create_single_thing_type, thing_type, i, len(thing_types))
                    for i, thing_type in enumerate(thing_types, 1)
                ]

                success_count = 0
                for future in as_completed(futures):
                    try:
                        if future.result():
                            success_count += 1
                    except Exception as e:
                        print(f"{Fore.RED}❌ Thread execution failed: {e}{Style.RESET_ALL}")

        print(f"{Fore.CYAN}📊 Thing types completed: {success_count}/{len(thing_types)} successful{Style.RESET_ALL}")

    def enable_fleet_indexing(self):
        """Enable AWS IoT Fleet Indexing with $package shadow support"""
        print(f"{Fore.BLUE}🔍 Enabling AWS IoT Fleet Indexing with $package shadow...{Style.RESET_ALL}")

        try:
            if self.debug_mode:
                print("📤 API Call: update_indexing_configuration")
                print("📥 Input Parameters:")
                config = {
                    "thingIndexingConfiguration": {
                        "thingIndexingMode": "REGISTRY_AND_SHADOW",
                        "thingConnectivityIndexingMode": "STATUS",
                        "deviceDefenderIndexingMode": "VIOLATIONS",
                        "namedShadowIndexingMode": "ON",
                        "filter": {"namedShadowNames": ["$package"]},
                    },
                    "thingGroupIndexingConfiguration": {"thingGroupIndexingMode": "ON"},
                }
                print(json.dumps(config, indent=2))

            response = self.iot_client.update_indexing_configuration(
                thingIndexingConfiguration={
                    "thingIndexingMode": "REGISTRY_AND_SHADOW",
                    "thingConnectivityIndexingMode": "STATUS",
                    "deviceDefenderIndexingMode": "VIOLATIONS",
                    "namedShadowIndexingMode": "ON",
                    "filter": {"namedShadowNames": ["$package"]},
                },
                thingGroupIndexingConfiguration={"thingGroupIndexingMode": "ON"},
            )

            if self.debug_mode:
                print("📤 API Response:")
                print(json.dumps(response, indent=2, default=str))

            print(f"{Fore.GREEN}✅ AWS IoT Fleet Indexing enabled with $package shadow support{Style.RESET_ALL}")
            return True
        except Exception as e:
            print(f"{Fore.RED}❌ Failed to enable AWS IoT Fleet Indexing: {str(e)}{Style.RESET_ALL}")
            return False

    def create_s3_bucket(self):
        """Create Amazon S3 bucket for firmware storage with versioning enabled"""
        try:
            # Check for existing bucket with debug output
            print(f"{Fore.BLUE}🔍 Checking for existing Amazon S3 buckets...{Style.RESET_ALL}")

            if self.debug_mode:
                print("\n🔍 DEBUG: Check Existing Buckets")
                print("📤 API Call: list_buckets")
                print("📥 Input Parameters: {}")

            response = self.s3_client.list_buckets()

            if self.debug_mode:
                print("📤 API Response:")
                print(json.dumps(response, indent=2, default=str))

            existing_buckets = [
                b["Name"] for b in response.get("Buckets", []) if b["Name"].startswith(f"iot-firmware-{self.region}")
            ]

            if existing_buckets:
                bucket_name = existing_buckets[0]
                print(f"{Fore.GREEN}✅ Using existing Amazon S3 bucket: {Fore.YELLOW}{bucket_name}{Style.RESET_ALL}")
                return bucket_name

            # Create new bucket
            bucket_name = f"iot-firmware-{self.region}-{int(time.time())}"

            if self.region == "us-east-1":
                response = self.safe_api_call(
                    self.s3_client.create_bucket, "S3 Bucket", bucket_name, debug=self.debug_mode, Bucket=bucket_name
                )
            else:
                response = self.safe_api_call(
                    self.s3_client.create_bucket,
                    "S3 Bucket",
                    bucket_name,
                    debug=self.debug_mode,
                    Bucket=bucket_name,
                    CreateBucketConfiguration={"LocationConstraint": self.region},
                )

            if not response:
                return None

            # Enable versioning with debug output
            versioning_response = self.safe_api_call(
                self.s3_client.put_bucket_versioning,
                "S3 Bucket Versioning",
                bucket_name,
                debug=self.debug_mode,
                Bucket=bucket_name,
                VersioningConfiguration={"Status": "Enabled"},
            )

            if versioning_response:
                print(f"{Fore.GREEN}✅ Amazon S3 bucket versioning enabled{Style.RESET_ALL}")

            return bucket_name

        except Exception as e:
            print(f"{Fore.RED}❌ Failed to create Amazon S3 bucket: {str(e)}{Style.RESET_ALL}")
            return None

    def upload_firmware_to_s3(self, bucket_name, package_name, version):
        """Upload firmware package to Amazon S3"""
        safe_package_name = re.sub(r"[^a-zA-Z0-9.\-_]", "", str(package_name))
        safe_version = re.sub(r"[^a-zA-Z0-9.\-_]", "", str(version))
        clean_version = safe_version.replace(".", "_")
        key = f"{safe_package_name}_v{clean_version}.zip"

        try:
            # Check if file exists
            if self.debug_mode:
                print(f"\n🔍 DEBUG: S3 Head Object Check: {key}")
                print("📤 API Call: head_object")
                print("📥 Input Parameters:")
                print(json.dumps({"Bucket": bucket_name, "Key": key}, indent=2))

            response = self.s3_client.head_object(Bucket=bucket_name, Key=key)

            if self.debug_mode:
                print("📤 API Response:")
                print(json.dumps(response, indent=2, default=str))
            version_id = response.get("VersionId", "")
            print(f"{Fore.GREEN}✅ Package already exists (Version: {version_id}){Style.RESET_ALL}")
            return version_id, key

        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                # File doesn't exist - this is expected, continue to upload
                if self.debug_mode:
                    print("📝 Package not found, will create new one")
            else:
                if self.debug_mode:
                    print("🔍 DEBUG: S3 head_object error (non-404):")
                    print(json.dumps(e.response, indent=2, default=str))
                print(f"{Fore.RED}❌ Error checking file: {e.response['Error']['Message']}{Style.RESET_ALL}")
                return None, key
        except Exception as e:
            if self.debug_mode:
                print(f"🔍 DEBUG: Unexpected error in head_object: {str(e)}")
            # File doesn't exist, continue to upload

        # Create dummy firmware zip file
        temp_fd, temp_file_path = tempfile.mkstemp(suffix=".zip")
        os.close(temp_fd)

        with zipfile.ZipFile(temp_file_path, "w") as zipf:
            zipf.writestr(
                f"firmware_{safe_version}.bin", f"Firmware version {safe_version} for {safe_package_name} - {int(time.time())}"
            )

        try:
            # Upload with debug output
            print(f"{Fore.BLUE}⬆️  Uploading new package: {Fore.YELLOW}{key}{Style.RESET_ALL}")
            with open(temp_file_path, "rb") as f:
                if self.debug_mode:
                    print(f"\n🔍 DEBUG: S3 Put Object: {key}")
                    print("📤 API Call: put_object")
                    print("📥 Input Parameters:")
                    print(json.dumps({"Bucket": bucket_name, "Key": key, "Body": "<file_content>"}, indent=2))

                response = self.s3_client.put_object(Bucket=bucket_name, Key=key, Body=f)

                if self.debug_mode:
                    print("📤 API Response:")
                    print(json.dumps(response, indent=2, default=str))

            if response:
                version_id = response.get("VersionId", "")
                print(f"{Fore.GREEN}✅ Package uploaded successfully (Version: {version_id}){Style.RESET_ALL}")
                return version_id, key
            else:
                return None, key

        except Exception as e:
            print(f"{Fore.RED}❌ Failed to upload package: {str(e)}{Style.RESET_ALL}")
            return None, key
        finally:
            os.remove(temp_file_path)

    def create_single_iot_package(self, bucket_name, thing_type, version_ids, package_versions, index, total):
        """Create a single IoT software package for a thing type"""
        with self.package_semaphore:
            print(f"{Fore.BLUE}📦 Creating package {index}/{total}: {Fore.YELLOW}{thing_type}{Style.RESET_ALL}")

            try:
                # Try to create package first (more efficient than checking existence)
                response = self.safe_api_call(
                    self.iot_client.create_package, "IoT Package", thing_type, debug=self.debug_mode, packageName=thing_type
                )
                if not response:
                    # Check if it failed due to already existing
                    try:
                        self.iot_client.get_package(packageName=thing_type)
                        print(f"{Fore.GREEN}✅ Package already exists{Style.RESET_ALL}")
                    except ClientError:
                        return False

                # Create all user-defined versions for this thing type
                success_count = 0

                for version in package_versions:
                    clean_version = version.replace(".", "_")
                    key = f"{thing_type}_v{clean_version}.zip"

                    # Check if version exists with debug output
                    try:
                        version_id = version_ids.get(key, "")

                        # Create package version with artifact
                        response = self.safe_api_call(
                            self.iot_client.create_package_version,
                            "Package Version",
                            f"{thing_type} v{version}",
                            debug=self.debug_mode,
                            packageName=thing_type,
                            versionName=version,
                            attributes={"signingKey": "SAMPLE-KEY-12345", "override": "true"},
                            artifact={"s3Location": {"bucket": bucket_name, "key": key, "version": version_id}},
                        )

                        if response:
                            # Publish the package version
                            publish_response = self.safe_api_call(
                                self.iot_client.update_package_version,
                                "Package Version Publish",
                                f"{thing_type} v{version}",
                                debug=self.debug_mode,
                                packageName=thing_type,
                                versionName=version,
                                action="PUBLISH",
                            )

                            if publish_response:
                                success_count += 1
                        else:
                            # Check if it failed due to already existing
                            try:
                                self.iot_client.get_package_version(packageName=thing_type, versionName=version)
                                print(
                                    f"{Fore.GREEN}✅ Package '{thing_type}' version {version} already exists{Style.RESET_ALL}"
                                )
                                success_count += 1
                            except ClientError:
                                pass

                    except Exception as e:
                        print(f"{Fore.RED}❌ Error processing version {version}: {str(e)}{Style.RESET_ALL}")

                time.sleep(0.125)  # Rate limiting  # nosemgrep: arbitrary-sleep
                return success_count == len(package_versions)

            except Exception as e:
                print(f"{Fore.RED}❌ Error creating package {thing_type}: {str(e)}{Style.RESET_ALL}")
                return False

    def create_iot_packages(self, bucket_name, version_ids, thing_types, package_versions):
        """Create IoT software packages for each thing type with user-defined versions"""
        if self.debug_mode:
            print(
                f"{Fore.BLUE}📋 Creating AWS IoT Software Package Catalog packages sequentially (debug mode)...{Style.RESET_ALL}"
            )
            success_count = 0
            for i, thing_type in enumerate(thing_types, 1):
                if self.create_single_iot_package(bucket_name, thing_type, version_ids, package_versions, i, len(thing_types)):
                    success_count += 1
        else:
            print(f"{Fore.BLUE}📋 Creating AWS IoT Software Package Catalog packages in parallel...{Style.RESET_ALL}")
            with ThreadPoolExecutor(max_workers=min(8, len(thing_types))) as executor:
                futures = [
                    executor.submit(
                        self.create_single_iot_package,
                        bucket_name,
                        thing_type,
                        version_ids,
                        package_versions,
                        i,
                        len(thing_types),
                    )
                    for i, thing_type in enumerate(thing_types, 1)
                ]

                success_count = sum(1 for future in as_completed(futures) if future.result())

        print(f"{Fore.CYAN}📊 Packages completed: {success_count}/{len(thing_types)} successful{Style.RESET_ALL}")

    def create_iot_jobs_role(self):
        """Create IAM role for AWS IoT Jobs presigned URLs"""
        print(f"{Fore.BLUE}🔐 Creating AWS Identity and Access Management (IAM) role for AWS IoT Jobs...{Style.RESET_ALL}")

        role_name = f"IoTJobsRole-{self.region}-{self.account_id[:8]}"
        trust_policy = {
            "Version": "2012-10-17",
            "Statement": [{"Effect": "Allow", "Principal": {"Service": "iot.amazonaws.com"}, "Action": "sts:AssumeRole"}],
        }

        try:
            # Check if role exists
            if self.debug_mode:
                print("📤 API Call: get_role")
                print(f"📥 Input Parameters: {{'RoleName': '{role_name}'}}")

            response = self.iam_client.get_role(RoleName=role_name)
            print(f"{Fore.GREEN}✅ AWS IoT Jobs role already exists{Style.RESET_ALL}")

        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchEntity":
                # Create role
                response = self.safe_api_call(
                    self.iam_client.create_role,
                    "IAM Role",
                    role_name,
                    debug=self.debug_mode,
                    RoleName=role_name,
                    AssumeRolePolicyDocument=json.dumps(trust_policy),
                    MaxSessionDuration=14400,  # 4 hours
                )
                if not response:
                    return False
            else:
                print(f"{Fore.RED}❌ Error checking role: {e.response['Error']['Message']}{Style.RESET_ALL}")
                return False

        # Check and attach policy
        policy_name = "IoTJobsS3Policy"
        try:
            if self.debug_mode:
                print("📤 API Call: get_role_policy")
                print(f"📥 Input Parameters: {{'RoleName': '{role_name}', 'PolicyName': '{policy_name}'}}")

            self.iam_client.get_role_policy(RoleName=role_name, PolicyName=policy_name)
            print(f"{Fore.GREEN}✅ Amazon S3 policy already attached to AWS IoT Jobs role{Style.RESET_ALL}")

        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchEntity":
                # Create and attach policy
                iot_jobs_policy = {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Action": ["s3:GetObject", "s3:GetObjectVersion"],
                            "Resource": f"arn:aws:s3:::iot-firmware-{self.region}-*/*",
                            "Condition": {
                                "StringEquals": {"aws:RequestedRegion": self.region},
                                "Bool": {"aws:SecureTransport": "true"},
                            },
                        }
                    ],
                }

                time.sleep(2)  # IAM propagation delay  # nosemgrep: arbitrary-sleep

                if self.debug_mode:
                    print("📤 API Call: put_role_policy")
                    print("📥 Input Parameters:")
                    print(
                        json.dumps(
                            {"RoleName": role_name, "PolicyName": policy_name, "PolicyDocument": iot_jobs_policy}, indent=2
                        )
                    )

                response = self.iam_client.put_role_policy(
                    RoleName=role_name, PolicyName=policy_name, PolicyDocument=json.dumps(iot_jobs_policy)
                )

                if self.debug_mode:
                    print("📤 API Response:")
                    print(json.dumps(response, indent=2, default=str))

                print(f"{Fore.GREEN}✅ Amazon S3 policy attached to AWS IoT Jobs role{Style.RESET_ALL}")

        return True

    def create_package_config_role(self):
        """Create IAM role for package configuration shadow updates"""
        print(
            f"{Fore.BLUE}🔐 Creating AWS Identity and Access Management (IAM) role for package configuration...{Style.RESET_ALL}"
        )

        role_name = f"IoTPackageConfigRole-{self.region}-{self.account_id[:8]}"
        trust_policy = {
            "Version": "2012-10-17",
            "Statement": [{"Effect": "Allow", "Principal": {"Service": "iot.amazonaws.com"}, "Action": "sts:AssumeRole"}],
        }

        try:
            response = self.iam_client.get_role(RoleName=role_name)
            print(f"{Fore.GREEN}✅ Package config role already exists{Style.RESET_ALL}")
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchEntity":
                response = self.safe_api_call(
                    self.iam_client.create_role,
                    "IAM Role",
                    role_name,
                    debug=self.debug_mode,
                    RoleName=role_name,
                    AssumeRolePolicyDocument=json.dumps(trust_policy),
                    MaxSessionDuration=14400,  # 4 hours
                )
                if not response:
                    return False

        # Check and attach policy
        policy_name = "PackageConfigPolicy"
        try:
            self.iam_client.get_role_policy(RoleName=role_name, PolicyName=policy_name)
            print(f"{Fore.GREEN}✅ Package config policy already attached{Style.RESET_ALL}")
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchEntity":
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

                time.sleep(2)  # IAM propagation delay  # nosemgrep: arbitrary-sleep

                response = self.iam_client.put_role_policy(
                    RoleName=role_name, PolicyName=policy_name, PolicyDocument=json.dumps(package_config_policy)
                )

                print(f"{Fore.GREEN}✅ Package config policy attached{Style.RESET_ALL}")

        return True

    def update_package_configurations(self):
        """Update global package configuration for automated shadow updates"""
        print(
            f"{Fore.BLUE}📦 Updating AWS IoT Software Package Catalog configuration for automated shadow updates...{Style.RESET_ALL}"
        )

        role_arn = f"arn:aws:iam::{self.account_id}:role/IoTPackageConfigRole-{self.region}-{self.account_id[:8]}"

        time.sleep(2)  # IAM propagation delay  # nosemgrep: arbitrary-sleep

        try:
            if self.debug_mode:
                print("📤 API Call: update_package_configuration")
                print(f"📥 Input Parameters: {{'versionUpdateByJobsConfig': {{'enabled': True, 'roleArn': '{role_arn}'}}}}")

            response = self.iot_client.update_package_configuration(
                versionUpdateByJobsConfig={"enabled": True, "roleArn": role_arn}
            )

            if self.debug_mode:
                print("📤 API Response:")
                print(json.dumps(response, indent=2, default=str))

            print(f"{Fore.GREEN}✅ Global package configuration updated{Style.RESET_ALL}")
            return True
        except Exception as e:
            print(f"{Fore.RED}❌ Failed to update global package configuration: {str(e)}{Style.RESET_ALL}")
            return False

    def create_single_thing(self, thing_name, thing_type, group_name, country, version, index, total):
        """Create a single IoT thing with proper attributes, shadows, and add to group"""
        with self.thing_creation_semaphore:
            try:
                # Generate random attributes
                customer_id = str(uuid.uuid4())
                end_date = datetime.now()
                start_date = end_date - timedelta(days=365)
                random_date = start_date + timedelta(seconds=random.randint(0, int((end_date - start_date).total_seconds())))
                manufacturing_date = random_date.strftime("%Y-%m-%d")
                battery_level = random.randint(30, 100)

                # Create thing
                if self.debug_mode:
                    print("📤 API Call: create_thing")
                    print("📥 Input Parameters:")
                    params = {
                        "thingName": thing_name,
                        "thingTypeName": thing_type,
                        "attributePayload": {
                            "attributes": {
                                "customerId": customer_id,
                                "country": country,
                                "manufacturingDate": manufacturing_date,
                            }
                        },
                    }
                    print(json.dumps(params, indent=2))

                response = self.iot_client.create_thing(
                    thingName=thing_name,
                    thingTypeName=thing_type,
                    attributePayload={
                        "attributes": {"customerId": customer_id, "country": country, "manufacturingDate": manufacturing_date}
                    },
                )

                if self.debug_mode:
                    print("📤 API Response:")
                    print(json.dumps(response, indent=2, default=str))

                # Add to thing group
                self.iot_client.add_thing_to_thing_group(thingGroupName=group_name, thingName=thing_name)

                # Create classic shadow
                iot_data = boto3.client("iot-data", region_name=self.region)
                classic_shadow = json.dumps({"state": {"reported": {"batteryStatus": battery_level}}})

                if self.debug_mode:
                    print("📤 API Call: update_thing_shadow (classic)")
                    print(f"📥 Input Parameters: thingName={thing_name}, payload={classic_shadow}")

                iot_data.update_thing_shadow(thingName=thing_name, payload=classic_shadow)

                if self.debug_mode:
                    print(f"✅ Classic shadow created for {thing_name}")

                # Create $package shadow with first user-defined version
                package_shadow = json.dumps({"state": {"reported": {thing_type: {"version": version, "attributes": {}}}}})

                if self.debug_mode:
                    print("📤 API Call: update_thing_shadow ($package)")
                    print(f"📥 Input Parameters: thingName={thing_name}, shadowName=$package, payload={package_shadow}")

                iot_data.update_thing_shadow(thingName=thing_name, shadowName="$package", payload=package_shadow)

                if self.debug_mode:
                    print(f"✅ $package shadow created for {thing_name} with {thing_type} v{version}")
                elif not self.debug_mode and index % 20 == 0:
                    print(f"📊 Created shadows for {index} devices...")

                if not self.debug_mode:
                    print(f"✅ Device {thing_name} created with classic and $package shadows")

                return True

            except Exception as e:
                print(f"{Fore.RED}❌ Failed to create device {thing_name}: {str(e)}{Style.RESET_ALL}")
                if self.debug_mode:
                    import traceback

                    traceback.print_exc()
                return False

            time.sleep(0.0125)  # Rate limiting  # nosemgrep: arbitrary-sleep

    def create_things_and_groups(self, thing_types, package_versions, continent_choice, selected_countries, device_count):
        """Create IoT things and thing groups in parallel"""
        continent_info = CONTINENTS[continent_choice]

        print(
            f"{Fore.BLUE}🏭 Creating {device_count} AWS IoT things in {continent_info['name']} (parallel processing)...{Style.RESET_ALL}"
        )

        # Create static thing groups
        group_names = [f"{country}_Fleet" for country in selected_countries]

        print(f"{Fore.BLUE}👥 Creating {len(group_names)} AWS IoT static thing groups...{Style.RESET_ALL}")
        group_success = 0

        for i, (country, group_name) in enumerate(zip(selected_countries, group_names), 1):
            print(f"{Fore.BLUE}[{i}/{len(group_names)}] Creating thing group: {Fore.YELLOW}{group_name}{Style.RESET_ALL}")

            try:
                response = self.iot_client.describe_thing_group(thingGroupName=group_name)
                print(f"{Fore.GREEN}✅ Thing group already exists{Style.RESET_ALL}")
                group_success += 1
            except ClientError as e:
                if e.response["Error"]["Code"] == "ResourceNotFoundException":
                    # Create group
                    response = self.safe_api_call(
                        self.iot_client.create_thing_group,
                        "Thing Group",
                        group_name,
                        debug=self.debug_mode,
                        thingGroupName=group_name,
                        thingGroupProperties={
                            "thingGroupDescription": f"Vehicle fleet in {country}",
                            "attributePayload": {"attributes": {"country": country}},
                        },
                        tags=[{"Key": "country", "Value": country}],
                    )
                    if response:
                        group_success += 1

        print(f"{Fore.CYAN}📊 Static thing groups completed: {group_success}/{len(group_names)} successful{Style.RESET_ALL}")

        # Prepare thing creation data
        thing_data = []
        for i in range(1, device_count + 1):
            country = selected_countries[(i - 1) % len(selected_countries)]
            thing_type = thing_types[(i - 1) % len(thing_types)]
            thing_name = f"Vehicle-VIN-{i:03d}"
            group_name = f"{country}_Fleet"
            default_version = package_versions[0]  # Use first user-defined version as default
            thing_data.append((thing_name, thing_type, group_name, country, default_version, i, device_count))

        # Create things with progress tracking
        if self.debug_mode:
            print(f"{Fore.BLUE}🚀 Creating {device_count} AWS IoT devices sequentially (debug mode)...{Style.RESET_ALL}")
            success_count = 0
            for data in thing_data:
                if self.create_single_thing(*data):
                    success_count += 1
        else:
            print(f"{Fore.BLUE}🚀 Creating {device_count} AWS IoT devices with progress tracking...{Style.RESET_ALL}")
            with ThreadPoolExecutor(max_workers=80) as executor:
                thing_futures = [executor.submit(self.create_single_thing, *data) for data in thing_data]

                success_count = 0
                completed = 0
                for future in as_completed(thing_futures):
                    completed += 1
                    if future.result():
                        success_count += 1

                    if completed % 20 == 0 or completed == device_count:
                        progress_percent = (completed * 100) // device_count
                        print(
                            f"{Fore.CYAN}📊 Progress: {completed}/{device_count} ({progress_percent}%) devices processed, {success_count} successful{Style.RESET_ALL}"
                        )

        print(f"{Fore.CYAN}📊 Things creation completed: {success_count}/{device_count} successful{Style.RESET_ALL}")

    def educational_pause(self, title, description):
        """Pause execution with educational content"""
        print(f"\n{Fore.YELLOW}📚 LEARNING MOMENT: {title}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{description}{Style.RESET_ALL}")
        input(f"\n{Fore.GREEN}Press Enter to continue...{Style.RESET_ALL}")
        print()

    def run(self):
        """Main execution flow"""
        # Initialize AWS clients first
        if not self.initialize_clients():
            sys.exit(1)

        # Print header with account info
        self.print_header()

        # Get debug mode preference
        self.get_debug_mode()

        # Get user inputs
        thing_types = self.get_thing_types()
        package_versions = self.get_package_versions()
        continent_choice = self.get_continent_choice()
        selected_countries = self.get_country_selection(continent_choice)
        device_count = self.get_device_count()

        print(f"\n{Fore.CYAN}🎯 Provisioning Plan:{Style.RESET_ALL}")
        print(f"{Fore.GREEN}📋 Thing types: {', '.join(thing_types)}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}🌍 Continent: {CONTINENTS[continent_choice]['name']}{Style.RESET_ALL}")
        print(
            f"{Fore.GREEN}🇦 Countries: {', '.join(selected_countries)} ({len(selected_countries)} of {len(CONTINENTS[continent_choice]['countries'])}){Style.RESET_ALL}"
        )
        print(f"{Fore.GREEN}📊 Device count: {device_count}{Style.RESET_ALL}\n")

        # Execute provisioning steps with timing
        start_time = time.time()

        # Step 1: Thing Types
        self.educational_pause(
            "Thing Types - Device Categories",
            "AWS IoT Thing Types are templates that define categories of IoT devices using the CreateThingType API.\n"
            "They act as blueprints specifying common attributes and behaviors for similar devices. The API\n"
            "creates searchable attributes that enable Fleet Indexing queries and bulk operations on device categories.\n"
            "Thing types help organize your device fleet and enable scalable IoT device management.\n\n"
            f"🔄 NEXT: We will create {len(thing_types)} thing types using the IoT CreateThingType API: {', '.join(thing_types)}",
        )
        self.create_thing_types(thing_types)

        # Step 2: Fleet Indexing
        self.educational_pause(
            "Fleet Indexing - Device Search & Query",
            "AWS IoT Fleet Indexing uses the UpdateIndexingConfiguration API to enable powerful search capabilities.\n"
            "It indexes device registry data, connectivity status, and device shadows (including the special\n"
            "$package shadow for firmware versions). The API configures indexing modes and shadow filters\n"
            "to enable dynamic thing groups and fleet-wide queries for large-scale deployments.\n\n"
            "🔄 NEXT: We will enable Fleet Indexing with $package shadow support using UpdateIndexingConfiguration API",
        )
        self.enable_fleet_indexing()

        # Step 3: S3 Storage
        self.educational_pause(
            "S3 Storage - Firmware Distribution",
            "Amazon S3 APIs (CreateBucket, PutBucketVersioning) provide secure, scalable firmware storage.\n"
            "The CreateBucket API establishes the storage location while PutBucketVersioning enables\n"
            "immutable firmware tracking. S3 integrates with AWS IoT Jobs through presigned URLs\n"
            "generated via GetObject API for secure, credential-free firmware downloads.\n\n"
            f"🔄 NEXT: We will create an S3 bucket in {self.region} with versioning using S3 APIs",
        )
        bucket_name = self.create_s3_bucket()

        if bucket_name:
            # Step 4: Firmware Upload
            self.educational_pause(
                "Firmware Packages - Version Management",
                "S3 PutObject API uploads firmware packages as ZIP files with unique version IDs.\n"
                "Each upload generates immutable artifacts through S3 versioning. The HeadObject API\n"
                "checks for existing files while PutObject creates new versions for precise\n"
                "firmware lifecycle control and over-the-air update management.\n\n"
                f"🔄 NEXT: We will upload {len(thing_types) * len(package_versions)} firmware packages ({len(thing_types)} types × {len(package_versions)} versions)",
            )
            # Upload firmware packages for each thing type and version
            version_ids = {}
            total_packages = len(thing_types) * len(package_versions)
            package_count = 0

            print(f"{Fore.BLUE}📦 Uploading {total_packages} firmware packages...{Style.RESET_ALL}")
            for thing_type in thing_types:
                for version in package_versions:
                    package_count += 1
                    print(
                        f"{Fore.BLUE}[{package_count}/{total_packages}] Processing: {thing_type} v{version}{Style.RESET_ALL}"
                    )
                    clean_version = version.replace(".", "_")
                    key = f"{thing_type}_v{clean_version}.zip"
                    version_id, _ = self.upload_firmware_to_s3(bucket_name, thing_type, version)
                    if version_id:
                        version_ids[key] = version_id

            # Step 5: Software Package Catalog
            self.educational_pause(
                "Software Package Catalog - Centralized Management",
                "AWS IoT Software Package Catalog APIs (CreatePackage, CreatePackageVersion) provide centralized firmware management.\n"
                "CreatePackage establishes the package while CreatePackageVersion links S3 artifacts to IoT packages.\n"
                "The UpdatePackageVersion API publishes versions, enabling automated device shadow updates\n"
                "when jobs complete successfully. This integration creates complete firmware lifecycle management.\n\n"
                f"🔄 NEXT: We will create {len(thing_types)} IoT packages and publish all versions to the catalog",
            )
            self.create_iot_packages(bucket_name, version_ids, thing_types, package_versions)

        # Step 6: IAM Roles for Jobs
        self.educational_pause(
            "IAM Roles - Secure Access Control",
            "AWS Identity and Access Management APIs (CreateRole, PutRolePolicy) provide secure service credentials.\n"
            "The CreateRole API establishes trust relationships while PutRolePolicy grants specific\n"
            "permissions. IAM roles enable AWS IoT to generate presigned URLs for S3 firmware downloads\n"
            "without exposing AWS credentials to devices, ensuring secure and scalable access control.\n\n"
            "🔄 NEXT: We will create IoTJobsRole and IoTPackageConfigRole using IAM APIs",
        )
        self.create_iot_jobs_role()
        self.create_package_config_role()

        # Step 7: Package Configuration
        self.educational_pause(
            "Package Configuration - Automated Shadow Updates",
            "AWS IoT Software Package Catalog UpdatePackageConfiguration API enables automatic device shadow updates.\n"
            "When devices report successful firmware installation via AWS IoT Jobs, AWS IoT Core automatically\n"
            "updates the device's $package shadow with the new firmware version. This creates a reliable\n"
            "audit trail and ensures device inventory reflects actual firmware state across your fleet.\n\n"
            "🔄 NEXT: We will enable global package configuration using UpdatePackageConfiguration API",
        )
        self.update_package_configurations()

        # Step 8: Device Creation
        self.educational_pause(
            "IoT Things & Thing Groups - Device Fleet Creation",
            "AWS IoT CreateThing and CreateThingGroup APIs establish your device fleet in the cloud.\n"
            "CreateThing registers individual devices with attributes while CreateThingGroup provides\n"
            "organizational structure. AddThingToThingGroup API creates relationships enabling\n"
            "bulk operations and policy inheritance across your IoT device fleet.\n\n"
            f"🔄 NEXT: We will create {len(selected_countries)} thing groups and {device_count} IoT devices using IoT APIs",
        )
        self.create_things_and_groups(thing_types, package_versions, continent_choice, selected_countries, device_count)

        end_time = time.time()
        duration = end_time - start_time

        print(f"\n{Fore.GREEN}🎉 Provisioning completed successfully!{Style.RESET_ALL}")
        print(f"{Fore.CYAN}📊 Created {device_count} devices across {len(selected_countries)} countries{Style.RESET_ALL}")
        print(f"{Fore.CYAN}⏱️  Total execution time: {duration:.2f} seconds{Style.RESET_ALL}")

        print(f"\n{Fore.YELLOW}🎓 What You've Learned:{Style.RESET_ALL}")
        print(f"{Fore.GREEN}✅ AWS IoT Thing Types organize devices using CreateThingType API{Style.RESET_ALL}")
        print(f"{Fore.GREEN}✅ Fleet Indexing enables device search via UpdateIndexingConfiguration API{Style.RESET_ALL}")
        print(
            f"{Fore.GREEN}✅ Amazon S3 provides secure firmware storage using CreateBucket and PutObject APIs{Style.RESET_ALL}"
        )
        print(
            f"{Fore.GREEN}✅ AWS IoT Software Package Catalog centralizes firmware using CreatePackage APIs{Style.RESET_ALL}"
        )
        print(f"{Fore.GREEN}✅ IAM roles enable secure access through CreateRole and PutRolePolicy APIs{Style.RESET_ALL}")
        print(
            f"{Fore.GREEN}✅ Package Configuration automates shadow updates via UpdatePackageConfiguration API{Style.RESET_ALL}"
        )
        print(f"{Fore.GREEN}✅ Device fleet creation uses CreateThing and CreateThingGroup APIs{Style.RESET_ALL}")
        print(
            f"{Fore.GREEN}✅ Boto3 provides direct AWS API access with detailed request/response visibility{Style.RESET_ALL}"
        )
        print(
            f"\n{Fore.CYAN}🚀 Next Steps: Use scripts/manage_dynamic_groups.py to create dynamic thing groups and scripts/create_job.py to deploy firmware updates!{Style.RESET_ALL}"
        )


if __name__ == "__main__":
    provisioner = IoTProvisioner()
    try:
        provisioner.run()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}👋 Provisioning cancelled by user. Goodbye!{Style.RESET_ALL}")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n{Fore.RED}❌ Provisioning failed with error: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)
