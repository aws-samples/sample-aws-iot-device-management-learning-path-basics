#!/usr/bin/env python3

import subprocess
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Semaphore
from colorama import Fore, Style, init

# Initialize colorama for cross-platform color support
init()

# Configuration
CONTINENTS = {
    1: {"name": "North America", "countries": ["US", "CA", "MX", "GT", "BZ", "SV", "HN", "NI", "CR", "PA", "CU", "JM", "HT", "DO", "BS", "BB", "TT", "GD", "VC", "LC", "AG", "KN", "DM"]},
    2: {"name": "South America", "countries": ["BR", "AR", "CL", "CO", "PE", "VE", "EC", "BO", "PY", "UY", "GY", "SR", "GF"]},
    3: {"name": "Europe", "countries": ["DE", "FR", "GB", "IT", "ES", "NL", "BE", "AT", "CH", "PT", "GR", "SE", "NO", "DK", "FI", "IE", "PL", "CZ", "HU", "SK", "SI", "HR", "BA", "RS", "ME", "MK", "AL", "BG", "RO", "MD", "UA", "BY", "LT", "LV", "EE", "RU", "IS", "MT", "CY", "LU", "LI", "AD", "MC", "SM", "VA"]},
    4: {"name": "Asia", "countries": ["CN", "JP", "IN", "KR", "SG", "TH", "VN", "MY", "ID", "PH", "MM", "KH", "LA", "BN", "TL", "MN", "KZ", "UZ", "TM", "TJ", "KG", "AF", "PK", "BD", "LK", "MV", "BT", "NP", "IR", "IQ", "SY", "LB", "JO", "IL", "PS", "SA", "YE", "OM", "AE", "QA", "BH", "KW", "TR", "GE", "AM", "AZ"]},
    5: {"name": "Africa", "countries": ["ZA", "NG", "EG", "KE", "MA", "DZ", "TN", "LY", "SD", "SS", "ET", "ER", "DJ", "SO", "UG", "TZ", "RW", "BI", "CD", "CG", "CF", "CM", "TD", "NE", "ML", "BF", "CI", "GH", "TG", "BJ", "SN", "GM", "GW", "GN", "SL", "LR", "MR", "CV", "ST", "GQ", "GA", "AO", "NA", "BW", "ZW", "ZM", "MW", "MZ", "SZ", "LS", "MG", "MU", "SC", "KM"]},
    6: {"name": "Oceania", "countries": ["AU", "NZ", "FJ", "PG", "SB", "VU", "NC", "PF", "WS", "TO", "KI", "TV", "NR", "PW", "FM", "MH", "GU", "AS", "MP", "CK", "NU", "TK"]},
    7: {"name": "Antarctica", "countries": ["AQ"]}
}

class IoTProvisioner:
    def __init__(self):
        self.region = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
        self.bucket_key_v1_1_0 = os.getenv('BUCKET_KEY_VERSION_1_1_0', 'firmware-v1.1.0.zip')
        self.bucket_key_v1_1_1 = os.getenv('BUCKET_KEY_VERSION_1_1_1', 'firmware-v1.1.1.zip')
        
        # Rate limiting semaphores for AWS API limits
        self.thing_type_semaphore = Semaphore(8)  # 10 TPS limit, use 8 for safety
        self.thing_creation_semaphore = Semaphore(80)  # 100 TPS limit, use 80 for safety
        self.package_semaphore = Semaphore(8)  # 10 TPS limit for packages
        self.debug_mode = False
        
    def run_aws_command(self, command, capture_output=True):
        """Execute AWS CLI command and return result"""
        try:
            if self.debug_mode:
                print(f"{Fore.CYAN}📥 DEBUG - Command: {command}{Style.RESET_ALL}")
            
            result = subprocess.run(command, shell=True, capture_output=capture_output, text=True)
            
            if self.debug_mode:
                print(f"{Fore.CYAN}📤 DEBUG - Return code: {result.returncode}{Style.RESET_ALL}")
                if result.stdout:
                    print(f"{Fore.CYAN}📤 DEBUG - Stdout: {result.stdout.strip()}{Style.RESET_ALL}")
                if result.stderr:
                    print(f"{Fore.CYAN}📤 DEBUG - Stderr: {result.stderr.strip()}{Style.RESET_ALL}")
            
            return result
        except Exception as e:
            print(f"{Fore.RED}❌ Error executing command: {e}{Style.RESET_ALL}")
            return None
    
    def print_header(self):
        print(f"{Fore.CYAN}🚀 AWS IoT Provisioning Script{Style.RESET_ALL}")
        print(f"{Fore.CYAN}================================{Style.RESET_ALL}\n")
    
    def get_debug_mode(self):
        """Ask user for debug mode"""
        choice = input(f"{Fore.YELLOW}🔧 Enable debug mode (show all commands and outputs)? [y/N]: {Style.RESET_ALL}").strip().lower()
        self.debug_mode = choice in ['y', 'yes']
        
        if self.debug_mode:
            print(f"{Fore.GREEN}✅ Debug mode enabled{Style.RESET_ALL}\n")
    
    def get_thing_types(self):
        """Get thing types from user input"""
        print(f"{Fore.YELLOW}📝 Enter thing types (comma-separated, e.g., sensor,gateway,device):{Style.RESET_ALL}")
        thing_types_input = input().strip()
        
        if not thing_types_input:
            print(f"{Fore.RED}❌ No thing types provided{Style.RESET_ALL}")
            sys.exit(1)
        
        return [t.strip() for t in thing_types_input.split(',')]
    
    def get_continent_choice(self):
        """Get continent selection from user"""
        print(f"{Fore.BLUE}🌍 Select continent:{Style.RESET_ALL}")
        for num, info in CONTINENTS.items():
            print(f"{Fore.CYAN}{num}. {info['name']}{Style.RESET_ALL}")
        
        while True:
            try:
                choice = int(input(f"{Fore.YELLOW}Enter choice [1-7]: {Style.RESET_ALL}"))
                if 1 <= choice <= 7:
                    return choice
                print(f"{Fore.RED}❌ Invalid choice. Please enter 1-7{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED}❌ Please enter a valid number{Style.RESET_ALL}")
    
    def get_country_selection(self, continent_choice):
        """Get country selection from user - either count or specific list"""
        continent_info = CONTINENTS[continent_choice]
        available_countries = continent_info['countries']
        max_countries = len(available_countries)
        
        print(f"\n{Fore.BLUE}🇦 Available countries in {continent_info['name']}: {', '.join(available_countries)}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Options:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}1. Enter a number (1-{max_countries}) to use first N countries{Style.RESET_ALL}")
        print(f"{Fore.CYAN}2. Enter comma-separated country codes (e.g., US,CA,MX){Style.RESET_ALL}")
        
        while True:
            user_input = input(f"{Fore.YELLOW}📊 Enter number or country codes: {Style.RESET_ALL}").strip()
            
            # Try to parse as number first
            try:
                count = int(user_input)
                if 1 <= count <= max_countries:
                    return available_countries[:count]
                print(f"{Fore.RED}❌ Please enter a number between 1 and {max_countries}{Style.RESET_ALL}")
                continue
            except ValueError:
                pass
            
            # Parse as comma-separated country codes
            if ',' in user_input or len(user_input) == 2:
                country_codes = [code.strip().upper() for code in user_input.split(',')]
                
                # Validate all country codes
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
        print(f"{Fore.YELLOW}📝 Enter package versions (comma-separated, e.g., 1.0.0,1.1.0,2.0.0):{Style.RESET_ALL}")
        versions_input = input().strip()
        
        if not versions_input:
            print(f"{Fore.YELLOW}⚠️  No versions provided, using defaults: 1.0.0,1.1.0{Style.RESET_ALL}")
            return ["1.0.0", "1.1.0"]
        
        versions = [v.strip() for v in versions_input.split(',')]
        
        # Basic validation
        for version in versions:
            if not version or not all(c.isdigit() or c == '.' for c in version):
                print(f"{Fore.RED}❌ Invalid version format: {version}{Style.RESET_ALL}")
                return self.get_package_versions()
        
        return versions
    
    def get_device_count(self):
        """Get number of devices to create"""
        while True:
            try:
                count = int(input(f"{Fore.YELLOW}📊 Enter number of devices to create: {Style.RESET_ALL}"))
                if count > 0:
                    return count
                print(f"{Fore.RED}❌ Please enter a positive number{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED}❌ Please enter a valid number{Style.RESET_ALL}")
    
    def create_single_thing_type(self, thing_type, index, total):
        """Create or undeprecate a single thing type"""
        with self.thing_type_semaphore:
            print(f"{Fore.BLUE}📋 Processing thing type {index}/{total}: {Fore.YELLOW}{thing_type}{Style.RESET_ALL}")
            
            # Check if thing type already exists
            check_result = self.run_aws_command(f"aws iot describe-thing-type --thing-type-name {thing_type}")
            
            if check_result and check_result.returncode == 0:
                # Thing type exists, check if deprecated
                try:
                    thing_type_info = json.loads(check_result.stdout)
                    if thing_type_info.get('thingTypeMetadata', {}).get('deprecated', False):
                        print(f"{Fore.YELLOW}🔄 Thing type exists but is deprecated, undeprecating...{Style.RESET_ALL}")
                        undeprecate_result = self.run_aws_command(f"aws iot deprecate-thing-type --thing-type-name {thing_type} --undo-deprecate")
                        
                        if undeprecate_result and undeprecate_result.returncode == 0:
                            print(f"{Fore.GREEN}✅ Thing type '{thing_type}' undeprecated successfully{Style.RESET_ALL}")
                            return True
                        else:
                            print(f"{Fore.RED}❌ Failed to undeprecate thing type '{thing_type}'{Style.RESET_ALL}")
                            return False
                    else:
                        print(f"{Fore.GREEN}✅ Thing type '{thing_type}' already exists and is active{Style.RESET_ALL}")
                        return True
                except json.JSONDecodeError:
                    print(f"{Fore.RED}❌ Failed to parse thing type info{Style.RESET_ALL}")
                    return False
            else:
                # Thing type doesn't exist, create it
                result = self.run_aws_command(f"aws iot create-thing-type --thing-type-name {thing_type}")
                
                if result and result.returncode == 0:
                    print(f"{Fore.GREEN}✅ Thing type '{thing_type}' created successfully{Style.RESET_ALL}")
                    return True
                else:
                    print(f"{Fore.RED}❌ Failed to create thing type '{thing_type}'{Style.RESET_ALL}")
                    return False
            
            time.sleep(0.125)  # Rate limiting: 8 TPS
    
    def create_thing_types(self, thing_types):
        """Create or undeprecate thing types in parallel"""
        print(f"{Fore.BLUE}🔧 Creating/updating thing types in parallel...{Style.RESET_ALL}")
        
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(self.create_single_thing_type, thing_type, i, len(thing_types)) 
                      for i, thing_type in enumerate(thing_types, 1)]
            
            success_count = 0
            for future in as_completed(futures):
                if future.result():
                    success_count += 1
        
        print(f"{Fore.CYAN}📊 Thing types completed: {success_count}/{len(thing_types)} successful{Style.RESET_ALL}")
    
    def create_s3_bucket(self):
        """Create S3 bucket for firmware storage with versioning enabled"""
        # Check for existing bucket first
        existing_result = self.run_aws_command("aws s3api list-buckets --query 'Buckets[?starts_with(Name, `iot-firmware`)].Name' --output text")
        
        if existing_result and existing_result.returncode == 0:
            existing_buckets = existing_result.stdout.strip().split()
            if existing_buckets and existing_buckets != ['']:
                bucket_name = existing_buckets[0]
                print(f"{Fore.GREEN}✅ Using existing S3 bucket: {Fore.YELLOW}{bucket_name}{Style.RESET_ALL}")
                return bucket_name
        
        bucket_name = f"iot-firmware-{self.region}-{int(time.time())}"
        print(f"{Fore.BLUE}🪣 Creating S3 bucket: {Fore.YELLOW}{bucket_name}{Style.RESET_ALL}")
        
        if self.region == 'us-east-1':
            result = self.run_aws_command(f"aws s3 mb s3://{bucket_name}")
        else:
            result = self.run_aws_command(f"aws s3 mb s3://{bucket_name} --region {self.region}")
        
        if result and result.returncode == 0:
            print(f"{Fore.GREEN}✅ S3 bucket created successfully{Style.RESET_ALL}")
            
            # Enable versioning
            print(f"{Fore.BLUE}🔄 Enabling S3 bucket versioning...{Style.RESET_ALL}")
            versioning_result = self.run_aws_command(f"aws s3api put-bucket-versioning --bucket {bucket_name} --versioning-configuration Status=Enabled")
            
            if versioning_result and versioning_result.returncode == 0:
                print(f"{Fore.GREEN}✅ S3 bucket versioning enabled{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}❌ Failed to enable S3 bucket versioning{Style.RESET_ALL}")
            
            return bucket_name
        else:
            print(f"{Fore.RED}❌ Failed to create S3 bucket{Style.RESET_ALL}")
            return None
    
    def upload_single_package(self, bucket_name, package, index, total):
        """Upload a single firmware package to S3 as zip file"""
        print(f"{Fore.BLUE}⬆️  Uploading package {index}/{total}: {Fore.YELLOW}{package['key']}{Style.RESET_ALL}")
        
        # Check if file already exists
        check_result = self.run_aws_command(f"aws s3api head-object --bucket {bucket_name} --key {package['key']}")
        
        if check_result and check_result.returncode == 0:
            # File exists, get version ID
            try:
                response = json.loads(check_result.stdout)
                version_id = response.get('VersionId', '')
                print(f"{Fore.GREEN}✅ Package already exists (Version: {version_id}){Style.RESET_ALL}")
                return package['version'], version_id, package['key']
            except json.JSONDecodeError:
                pass
        
        # Create dummy firmware zip file
        import zipfile
        temp_file = f"/tmp/{package['key']}_{int(time.time())}.zip"
        
        with zipfile.ZipFile(temp_file, 'w') as zipf:
            zipf.writestr(f"firmware_{package['version']}.bin", f"Firmware version {package['version']} - {int(time.time())}")
        
        # Upload to S3 and capture version ID
        result = self.run_aws_command(f"aws s3api put-object --bucket {bucket_name} --key {package['key']} --body {temp_file}")
        
        # Cleanup temp file
        os.remove(temp_file)
        
        if result and result.returncode == 0:
            response = json.loads(result.stdout)
            version_id = response.get('VersionId', '')
            print(f"{Fore.GREEN}✅ Package uploaded successfully (Version: {version_id}){Style.RESET_ALL}")
            return package['version'], version_id, package['key']
        else:
            print(f"{Fore.RED}❌ Failed to upload package{Style.RESET_ALL}")
            return package['version'], None, package['key']
    
    def upload_firmware_packages(self, bucket_name, thing_types, package_versions):
        """Upload firmware packages to S3 for each thing type and version"""
        print(f"{Fore.BLUE}📦 Uploading firmware packages for each thing type and version...{Style.RESET_ALL}")
        
        packages = []
        for thing_type in thing_types:
            for version in package_versions:
                clean_version = version.replace('.', '_')
                packages.append({
                    "key": f"{thing_type}_v{clean_version}.zip", 
                    "version": version, 
                    "thing_type": thing_type
                })
        
        version_ids = {}
        
        with ThreadPoolExecutor(max_workers=min(8, len(packages))) as executor:
            futures = [executor.submit(self.upload_single_package, bucket_name, package, i, len(packages)) 
                      for i, package in enumerate(packages, 1)]
            
            for future in as_completed(futures):
                version, version_id, key = future.result()
                if version_id:
                    version_ids[key] = version_id
        
        return version_ids
    
    def create_single_iot_package(self, bucket_name, thing_type, version_ids, package_versions, index, total):
        """Create a single IoT software package for a thing type"""
        with self.package_semaphore:
            print(f"{Fore.BLUE}📦 Creating package {index}/{total}: {Fore.YELLOW}{thing_type}{Style.RESET_ALL}")
            
            # Check if package exists
            check_result = self.run_aws_command(f"aws iot list-packages --query 'packageSummaries[?packageName==`{thing_type}`].packageName' --output text")
            
            if check_result and check_result.returncode == 0 and check_result.stdout.strip() == thing_type:
                print(f"{Fore.GREEN}✅ Package already exists{Style.RESET_ALL}")
            else:
                # Create package
                result = self.run_aws_command(f"aws iot create-package --package-name {thing_type}")
                if result and result.returncode == 0:
                    print(f"{Fore.GREEN}✅ Package '{thing_type}' created{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}❌ Failed to create package '{thing_type}'{Style.RESET_ALL}")
            
            # Create all user-defined versions for this thing type
            success_count = 0
            
            for version in package_versions:
                clean_version = version.replace('.', '_')
                key = f"{thing_type}_v{clean_version}.zip"
                # Check if version exists
                version_check = self.run_aws_command(f"aws iot list-package-versions --package-name {thing_type} --query 'packageVersionSummaries[?versionName==`{version}`].versionName' --output text")
                
                if version_check and version_check.returncode == 0 and version_check.stdout.strip() == version:
                    print(f"{Fore.GREEN}✅ Package '{thing_type}' version {version} already exists{Style.RESET_ALL}")
                    success_count += 1
                else:
                    version_id = version_ids.get(key, '')
                    
                    version_cmd = f"aws iot create-package-version --package-name {thing_type} --version-name {version} --attributes 'signingKey=2422345,override=true' --artifact 's3Location={{bucket={bucket_name},key={key},version={version_id}}}'"
                    
                    version_result = self.run_aws_command(version_cmd)
                    if version_result and version_result.returncode == 0:
                        print(f"{Fore.GREEN}✅ Package '{thing_type}' version {version} created{Style.RESET_ALL}")
                        
                        # Publish the package version
                        publish_result = self.run_aws_command(f"aws iot update-package-version --package-name {thing_type} --version-name {version} --action PUBLISH")
                        if publish_result and publish_result.returncode == 0:
                            print(f"{Fore.GREEN}✅ Package '{thing_type}' version {version} published{Style.RESET_ALL}")
                        
                        success_count += 1
                    else:
                        print(f"{Fore.RED}❌ Failed to create package '{thing_type}' version {version}{Style.RESET_ALL}")
            
            time.sleep(0.125)  # Rate limiting: 8 TPS
            return success_count == len(package_versions)
    
    def create_iot_packages(self, bucket_name, version_ids, thing_types, package_versions):
        """Create IoT software packages for each thing type with user-defined versions"""
        print(f"{Fore.BLUE}📋 Creating IoT software packages for each thing type...{Style.RESET_ALL}")
        
        with ThreadPoolExecutor(max_workers=min(8, len(thing_types))) as executor:
            futures = [executor.submit(self.create_single_iot_package, bucket_name, thing_type, version_ids, package_versions, i, len(thing_types)) 
                      for i, thing_type in enumerate(thing_types, 1)]
            
            success_count = sum(1 for future in as_completed(futures) if future.result())
        
        print(f"{Fore.CYAN}📊 Packages completed: {success_count}/{len(thing_types)} successful{Style.RESET_ALL}")
    

    
    def create_iot_jobs_role(self):
        """Create IAM role for IoT Jobs presigned URLs"""
        print(f"{Fore.BLUE}🔐 Creating IAM role for IoT Jobs...{Style.RESET_ALL}")
        
        trust_policy = {
            "Version": "2012-10-17",
            "Statement": [{
                "Effect": "Allow",
                "Principal": {"Service": "iot.amazonaws.com"},
                "Action": "sts:AssumeRole"
            }]
        }
        
        # Check if role exists
        check_result = self.run_aws_command("aws iam get-role --role-name IoTJobsRole")
        
        if check_result and check_result.returncode == 0:
            print(f"{Fore.GREEN}✅ IoT Jobs role already exists{Style.RESET_ALL}")
        else:
            # Create role
            result = self.run_aws_command(f"aws iam create-role --role-name IoTJobsRole --assume-role-policy-document '{json.dumps(trust_policy)}'")
            
            if result and result.returncode == 0:
                print(f"{Fore.GREEN}✅ IoT Jobs role created{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}❌ Failed to create IoT Jobs role{Style.RESET_ALL}")
                return
        
        # Check if policy is already attached
        policy_check = self.run_aws_command("aws iam get-role-policy --role-name IoTJobsRole --policy-name IoTJobsS3Policy")
        
        if policy_check and policy_check.returncode == 0:
            print(f"{Fore.GREEN}✅ S3 policy already attached to IoT Jobs role{Style.RESET_ALL}")
        else:
            # Get account ID for policy
            account_id = self.run_aws_command("aws sts get-caller-identity --query Account --output text")
            if account_id and account_id.returncode == 0:
                account_id = account_id.stdout.strip()
                
                iot_jobs_policy = {
                    "Version": "2012-10-17",
                    "Statement": [{
                        "Effect": "Allow",
                        "Action": [
                            "s3:GetObject",
                            "s3:GetObjectVersion"
                        ],
                        "Resource": f"arn:aws:s3:::iot-firmware-{self.region}-*/*"
                    }]
                }
                
                # Wait for role to be ready and attach custom policy
                time.sleep(2)
                policy_result = self.run_aws_command(f"aws iam put-role-policy --role-name IoTJobsRole --policy-name IoTJobsS3Policy --policy-document '{json.dumps(iot_jobs_policy)}'")
                
                if policy_result and policy_result.returncode == 0:
                    print(f"{Fore.GREEN}✅ S3 policy attached to IoT Jobs role{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}❌ Failed to attach S3 policy{Style.RESET_ALL}")
    
    def create_package_config_role(self):
        """Create IAM role for package configuration shadow updates"""
        print(f"{Fore.BLUE}🔐 Creating IAM role for package configuration...{Style.RESET_ALL}")
        
        trust_policy = {
            "Version": "2012-10-17",
            "Statement": [{
                "Effect": "Allow",
                "Principal": {"Service": "iot.amazonaws.com"},
                "Action": "sts:AssumeRole"
            }]
        }
        
        # Check if role exists
        check_result = self.run_aws_command("aws iam get-role --role-name IoTPackageConfigRole")
        
        if check_result and check_result.returncode == 0:
            print(f"{Fore.GREEN}✅ Package config role already exists{Style.RESET_ALL}")
        else:
            # Create role
            result = self.run_aws_command(f"aws iam create-role --role-name IoTPackageConfigRole --assume-role-policy-document '{json.dumps(trust_policy)}'")
            
            if result and result.returncode == 0:
                print(f"{Fore.GREEN}✅ Package config role created{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}❌ Failed to create package config role{Style.RESET_ALL}")
                return
        
        # Check if policy is already attached
        policy_check = self.run_aws_command("aws iam get-role-policy --role-name IoTPackageConfigRole --policy-name PackageConfigPolicy")
        
        if policy_check and policy_check.returncode == 0:
            print(f"{Fore.GREEN}✅ Package config policy already attached{Style.RESET_ALL}")
        else:
            # Get account ID for policy
            account_id = self.run_aws_command("aws sts get-caller-identity --query Account --output text")
            if account_id and account_id.returncode == 0:
                account_id = account_id.stdout.strip()
                
                package_config_policy = {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Action": "iot:DescribeEndpoint",
                            "Resource": "*"
                        },
                        {
                            "Effect": "Allow",
                            "Action": [
                                "iot:GetThingShadow",
                                "iot:UpdateThingShadow"
                            ],
                            "Resource": [
                                f"arn:aws:iot:{self.region}:{account_id}:thing/*/$package"
                            ]
                        }
                    ]
                }
                
                # Wait for role to be ready and attach policy
                time.sleep(3)
                policy_result = self.run_aws_command(f"aws iam put-role-policy --role-name IoTPackageConfigRole --policy-name PackageConfigPolicy --policy-document '{json.dumps(package_config_policy)}'")
                
                if policy_result and policy_result.returncode == 0:
                    print(f"{Fore.GREEN}✅ Package config policy attached{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}❌ Failed to attach package config policy{Style.RESET_ALL}")
    
    def update_package_configurations(self, thing_types):
        """Update global package configuration for automated shadow updates"""
        print(f"{Fore.BLUE}📦 Updating global package configuration for automated shadow updates...{Style.RESET_ALL}")
        
        # Get account ID for role ARN
        account_id = self.run_aws_command("aws sts get-caller-identity --query Account --output text")
        if not account_id or account_id.returncode != 0:
            print(f"{Fore.RED}❌ Failed to get account ID{Style.RESET_ALL}")
            return
        
        account_id = account_id.stdout.strip()
        role_arn = f"arn:aws:iam::{account_id}:role/IoTPackageConfigRole"
        
        # Wait for role to be ready
        time.sleep(2)
        
        result = self.run_aws_command(f"aws iot update-package-configuration --version-update-by-jobs-config 'enabled=true,roleArn={role_arn}'")
        
        if result and result.returncode == 0:
            print(f"{Fore.GREEN}✅ Global package configuration updated{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}❌ Failed to update global package configuration{Style.RESET_ALL}")
    
    def enable_fleet_indexing(self):
        """Enable IoT Fleet Indexing with $package shadow support"""
        print(f"{Fore.BLUE}🔍 Enabling Fleet Indexing with $package shadow...{Style.RESET_ALL}")
        
        result = self.run_aws_command('aws iot update-indexing-configuration --thing-indexing-configuration "thingIndexingMode=REGISTRY_AND_SHADOW,thingConnectivityIndexingMode=STATUS,deviceDefenderIndexingMode=VIOLATIONS,namedShadowIndexingMode=ON,filter={namedShadowNames=[\$package]}" --thing-group-indexing-configuration "thingGroupIndexingMode=ON"')
        
        if result and result.returncode == 0:
            print(f"{Fore.GREEN}✅ Fleet Indexing enabled with $package shadow support{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}❌ Failed to enable Fleet Indexing{Style.RESET_ALL}")
    
    def create_single_thing_group(self, group_name, is_dynamic=False):
        """Create a single thing group (static or dynamic)"""
        if is_dynamic:
            # Dynamic thing groups have 5 TPS limit
            print(f"{Fore.BLUE}👥 Creating dynamic thing group: {Fore.YELLOW}{group_name}{Style.RESET_ALL}")
            time.sleep(0.25)  # Rate limiting: 4 TPS for safety
        else:
            # Static thing groups have 100 TPS limit
            print(f"{Fore.BLUE}👥 Creating static thing group: {Fore.YELLOW}{group_name}{Style.RESET_ALL}")
            time.sleep(0.0125)  # Rate limiting: 80 TPS for safety
        
        result = self.run_aws_command(f"aws iot create-thing-group --thing-group-name {group_name}")
        if result and result.returncode == 0:
            print(f"{Fore.GREEN}✅ Thing group created{Style.RESET_ALL}")
            return True
        else:
            print(f"{Fore.YELLOW}⚠️  Thing group might already exist{Style.RESET_ALL}")
            return False
    
    def create_single_thing(self, thing_name, thing_type, group_name, country, version, index, total):
        """Create a single IoT thing with proper attributes, shadows, and add to group"""
        with self.thing_creation_semaphore:
            import random
            
            # Generate random attributes like bash script
            year = 2020 + random.randint(0, 4)
            month = random.randint(1, 12)
            day = random.randint(1, 28)
            hour = random.randint(0, 23)
            minute = random.randint(0, 59)
            second = random.randint(0, 59)
            onboarded_date = f"{year:04d}-{month:02d}-{day:02d}.{hour:02d}:{minute:02d}:{second:02d}"
            
            battery_level = random.randint(30, 100)
            sern_mfgs = ["MFG-00001", "MFG-00002", "MFG-00003", "MFG-00004", "MFG-00005"]
            sern_mfg = random.choice(sern_mfgs)
            
            # Create thing with proper attributes matching bash script
            attributes = json.dumps({"attributes": {"onboardedOn": onboarded_date, "country": country, "sernMfg": sern_mfg}})
            result = self.run_aws_command(f"aws iot create-thing --thing-name {thing_name} --thing-type-name {thing_type} --attribute-payload '{attributes}'")
            
            if result and result.returncode == 0:
                # Add to static thing group
                group_result = self.run_aws_command(f"aws iot add-thing-to-thing-group --thing-name {thing_name} --thing-group-name {group_name}")
                
                # Create classic shadow
                classic_shadow = json.dumps({"state": {"reported": {"batteryStatus": battery_level}}})
                self.run_aws_command(f"aws iot-data update-thing-shadow --thing-name {thing_name} --cli-binary-format raw-in-base64-out --payload '{classic_shadow}' /dev/null")
                
                # Create $package shadow with first user-defined version
                package_shadow = json.dumps({"state": {"reported": {thing_type: {"version": version, "attributes": {}}}}})
                self.run_aws_command(f"aws iot-data update-thing-shadow --thing-name {thing_name} --shadow-name '$package' --cli-binary-format raw-in-base64-out --payload '{package_shadow}' /dev/null")
                
                if group_result and group_result.returncode == 0:
                    return True
                else:
                    print(f"{Fore.YELLOW}⚠️  Device {thing_name} created but failed to add to group{Style.RESET_ALL}")
                    return False
            else:
                print(f"{Fore.RED}❌ Failed to create device {thing_name}{Style.RESET_ALL}")
                return False
            
            time.sleep(0.0125)  # Rate limiting: 80 TPS
    
    def create_things_and_groups(self, thing_types, package_versions, continent_choice, selected_countries, device_count):
        """Create IoT things and thing groups in parallel"""
        continent_info = CONTINENTS[continent_choice]
        countries = selected_countries
        
        print(f"{Fore.BLUE}🏭 Creating {device_count} IoT things in {continent_info['name']} (parallel processing)...{Style.RESET_ALL}")
        
        # Create static thing groups for countries like bash script
        group_names = [f"{country}_devices" for country in countries]
        
        print(f"{Fore.BLUE}👥 Creating {len(group_names)} static thing groups...{Style.RESET_ALL}")
        group_success = 0
        for i, (country, group_name) in enumerate(zip(countries, group_names), 1):
            print(f"{Fore.BLUE}[{i}/{len(group_names)}] Creating thing group: {Fore.YELLOW}{group_name}{Style.RESET_ALL}")
            
            # Check if static thing group exists
            check_result = self.run_aws_command(f"aws iot describe-thing-group --thing-group-name {group_name}")
            
            if check_result and check_result.returncode == 0:
                print(f"{Fore.GREEN}✅ Thing group already exists{Style.RESET_ALL}")
                group_success += 1
            else:
                # Create with description and tags like bash script
                result = self.run_aws_command(f"aws iot create-thing-group --thing-group-name {group_name} --thing-group-properties 'thingGroupDescription=Devices in {country}' --tags 'Key=country,Value={country}'")
                if result and result.returncode == 0:
                    group_success += 1
                    print(f"{Fore.GREEN}✅ Thing group created{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}❌ Failed to create thing group{Style.RESET_ALL}")
        
        print(f"{Fore.CYAN}📊 Static thing groups completed: {group_success}/{len(group_names)} successful{Style.RESET_ALL}")
        

        
        # Prepare thing creation data with proper naming like bash script
        thing_data = []
        import random
        
        for i in range(1, device_count + 1):
            country = countries[i % len(countries)]
            thing_type = thing_types[i % len(thing_types)]
            
            # Generate random thing name like bash script
            random_num1 = random.randint(1000000, 9999999)
            random_num2 = random.randint(10000000, 99999999)
            thing_name = f"SENSOR-{random_num1}-{random_num2}"
            
            group_name = f"{country}_devices"
            default_version = package_versions[0]  # Use first user-defined version as default
            thing_data.append((thing_name, thing_type, group_name, country, default_version, i, device_count))
        
        # Create things with better progress visualization
        print(f"{Fore.BLUE}🚀 Creating {device_count} devices with progress tracking...{Style.RESET_ALL}")
        
        with ThreadPoolExecutor(max_workers=80) as executor:
            thing_futures = [executor.submit(self.create_single_thing, *data) for data in thing_data]
            
            success_count = 0
            completed = 0
            for future in as_completed(thing_futures):
                completed += 1
                if future.result():
                    success_count += 1
                
                # Progress update every 20 completions for better visibility
                if completed % 20 == 0 or completed == device_count:
                    progress_percent = (completed * 100) // device_count
                    print(f"{Fore.CYAN}📊 Progress: {completed}/{device_count} ({progress_percent}%) devices processed, {success_count} successful{Style.RESET_ALL}")
        
        print(f"{Fore.CYAN}📊 Things creation completed: {success_count}/{device_count} successful{Style.RESET_ALL}")
    
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
        
        # Get user inputs
        thing_types = self.get_thing_types()
        package_versions = self.get_package_versions()
        continent_choice = self.get_continent_choice()
        selected_countries = self.get_country_selection(continent_choice)
        device_count = self.get_device_count()
        
        print(f"\n{Fore.CYAN}🎯 Provisioning Plan:{Style.RESET_ALL}")
        print(f"{Fore.GREEN}📋 Thing types: {', '.join(thing_types)}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}📦 Package versions: {', '.join(package_versions)}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}🌍 Continent: {CONTINENTS[continent_choice]['name']}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}🇦 Countries: {', '.join(selected_countries)} ({len(selected_countries)} of {len(CONTINENTS[continent_choice]['countries'])}){Style.RESET_ALL}")
        print(f"{Fore.GREEN}📊 Device count: {device_count}{Style.RESET_ALL}\n")
        
        # Execute provisioning steps with timing
        start_time = time.time()
        
        # Step 1: Thing Types
        self.educational_pause(
            "Thing Types - Device Categories",
            "Thing Types are templates that define categories of IoT devices. They act as blueprints that specify\n"
            "common attributes and behaviors for similar devices. For example, a 'motionSensor' thing type might\n"
            "define attributes like sensitivity and detection range. Thing types help organize your device fleet\n"
            "and enable bulk operations on similar devices. They're essential for scalable IoT device management."
        )
        self.create_thing_types(thing_types)
        
        # Step 2: Fleet Indexing
        self.educational_pause(
            "Fleet Indexing - Device Search & Query",
            "Fleet Indexing enables powerful search and query capabilities across your entire IoT device fleet.\n"
            "It indexes device registry data, connectivity status, and device shadows (including the special\n"
            "$package shadow for firmware versions). This allows you to find devices by attributes like country,\n"
            "firmware version, or battery level. Fleet Indexing is crucial for creating dynamic thing groups\n"
            "and managing large-scale deployments efficiently."
        )
        self.enable_fleet_indexing()
        
        # Step 3: S3 Storage
        self.educational_pause(
            "S3 Storage - Firmware Distribution",
            "Amazon S3 provides secure, scalable storage for firmware packages. We enable versioning to track\n"
            "different firmware releases and ensure devices can access the correct version. S3 integrates with\n"
            "AWS IoT Jobs to provide presigned URLs for secure firmware downloads. This eliminates the need\n"
            "for devices to have direct S3 credentials while ensuring secure, authenticated access to firmware."
        )
        bucket_name = self.create_s3_bucket()
        
        if bucket_name:
            # Step 4: Firmware Upload
            self.educational_pause(
                "Firmware Packages - Version Management",
                "We upload firmware packages as ZIP files to S3, creating one package per thing type and version.\n"
                "Each upload generates a unique version ID that ensures immutable firmware artifacts. This\n"
                "approach supports multiple device types with different firmware requirements and enables\n"
                "precise version control for over-the-air updates."
            )
            version_ids = self.upload_firmware_packages(bucket_name, thing_types, package_versions)
            
            # Step 5: Software Package Catalog
            self.educational_pause(
                "Software Package Catalog - Centralized Management",
                "The AWS IoT Software Package Catalog provides centralized management of firmware versions.\n"
                "It links S3 artifacts to IoT packages and versions, enabling automated device shadow updates\n"
                "when jobs complete successfully. This integration between packages, jobs, and shadows creates\n"
                "a complete firmware lifecycle management system with automatic state synchronization."
            )
            self.create_iot_packages(bucket_name, version_ids, thing_types, package_versions)
        
        # Step 6: IAM Roles for Jobs
        self.educational_pause(
            "IAM Roles - Secure Access Control",
            "IAM roles provide secure, temporary credentials for AWS IoT services. The IoT Jobs role enables\n"
            "AWS IoT to generate presigned URLs for S3 firmware downloads, eliminating the need for devices\n"
            "to store AWS credentials. The Package Configuration role allows automatic device shadow updates\n"
            "when firmware installations complete, maintaining accurate device state information."
        )
        self.create_iot_jobs_role()
        self.create_package_config_role()
        
        # Step 7: Package Configuration
        self.educational_pause(
            "Package Configuration - Automated Shadow Updates",
            "Package Configuration enables automatic device shadow updates when IoT Jobs complete successfully.\n"
            "When a device reports successful firmware installation, AWS IoT automatically updates the device's\n"
            "$package shadow with the new firmware version. This creates a reliable audit trail and ensures\n"
            "your device inventory always reflects the actual firmware state across your fleet."
        )
        self.update_package_configurations(thing_types)
        
        # Step 8: Device Creation
        self.educational_pause(
            "IoT Things & Thing Groups - Device Fleet Creation",
            "IoT Things represent your physical devices in the AWS cloud. Each thing has attributes (metadata),\n"
            "device shadows (state), and belongs to thing groups for organization. We create static thing groups\n"
            "by country for geographical organization and assign each device to the appropriate group. Device\n"
            "shadows store both operational data (battery level) and firmware information ($package shadow)."
        )
        self.create_things_and_groups(thing_types, package_versions, continent_choice, selected_countries, device_count)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n{Fore.GREEN}🎉 Provisioning completed successfully!{Style.RESET_ALL}")
        print(f"{Fore.CYAN}📊 Created {device_count} devices across {len(selected_countries)} countries{Style.RESET_ALL}")
        print(f"{Fore.CYAN}⏱️  Total execution time: {duration:.2f} seconds{Style.RESET_ALL}")
        
        print(f"\n{Fore.YELLOW}🎓 What You've Learned:{Style.RESET_ALL}")
        print(f"{Fore.GREEN}✅ Thing Types organize devices into manageable categories{Style.RESET_ALL}")
        print(f"{Fore.GREEN}✅ Fleet Indexing enables powerful device search and dynamic grouping{Style.RESET_ALL}")
        print(f"{Fore.GREEN}✅ S3 provides secure, scalable firmware storage with versioning{Style.RESET_ALL}")
        print(f"{Fore.GREEN}✅ Software Package Catalog centralizes firmware version management{Style.RESET_ALL}")
        print(f"{Fore.GREEN}✅ IAM roles provide secure, credential-free access to AWS services{Style.RESET_ALL}")
        print(f"{Fore.GREEN}✅ Package Configuration automates device state synchronization{Style.RESET_ALL}")
        print(f"{Fore.GREEN}✅ Thing Groups and Device Shadows enable organized fleet management{Style.RESET_ALL}")
        print(f"\n{Fore.CYAN}🚀 Next Steps: Use create_job.py to deploy firmware updates to your devices!{Style.RESET_ALL}")

if __name__ == "__main__":
    provisioner = IoTProvisioner()
    provisioner.run()