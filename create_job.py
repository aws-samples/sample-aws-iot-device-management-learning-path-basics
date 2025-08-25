#!/usr/bin/env python3

import subprocess
import json
import sys
from colorama import Fore, Style, init

# Initialize colorama
init()

class IoTJobCreator:
    def __init__(self):
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
        print(f"{Fore.CYAN}🚀 AWS IoT Job Creator{Style.RESET_ALL}")
        print(f"{Fore.CYAN}====================={Style.RESET_ALL}\n")
        
        print(f"{Fore.YELLOW}📚 LEARNING GOAL:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}This script demonstrates how to create AWS IoT Jobs for over-the-air (OTA) firmware updates.{Style.RESET_ALL}")
        print(f"{Fore.CYAN}IoT Jobs orchestrate remote operations on devices, using presigned URLs for secure firmware{Style.RESET_ALL}")
        print(f"{Fore.CYAN}downloads and integrating with the Software Package Catalog for version management.{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Jobs can target multiple thing groups and automatically include new devices (continuous jobs).{Style.RESET_ALL}\n")
    
    def get_debug_mode(self):
        """Ask user for debug mode"""
        choice = input(f"{Fore.YELLOW}🔧 Enable debug mode (show all commands and outputs)? [y/N]: {Style.RESET_ALL}").strip().lower()
        self.debug_mode = choice in ['y', 'yes']
        
        if self.debug_mode:
            print(f"{Fore.GREEN}✅ Debug mode enabled{Style.RESET_ALL}\n")
    
    def get_thing_groups(self):
        """Get available thing groups"""
        print(f"{Fore.BLUE}🔍 Scanning for thing groups...{Style.RESET_ALL}")
        
        result = self.run_aws_command("aws iot list-thing-groups --query 'thingGroups[].groupName' --output table")
        
        if not result or result.returncode != 0:
            print(f"{Fore.RED}❌ Failed to list thing groups{Style.RESET_ALL}")
            return []
        
        print(f"{Fore.GREEN}📋 Available Thing Groups:{Style.RESET_ALL}")
        print(result.stdout)
        
        # Get group names for selection
        groups_result = self.run_aws_command("aws iot list-thing-groups --query 'thingGroups[].groupName' --output text")
        
        if groups_result and groups_result.returncode == 0:
            group_names = groups_result.stdout.strip().split()
            return [name for name in group_names if name]
        
        return []
    
    def get_packages(self):
        """Get available IoT packages"""
        print(f"{Fore.BLUE}🔍 Scanning for IoT packages...{Style.RESET_ALL}")
        
        result = self.run_aws_command("aws iot list-packages --query 'packageSummaries[].{PackageName:packageName,CreatedDate:creationDate}' --output table")
        
        if not result or result.returncode != 0:
            print(f"{Fore.RED}❌ Failed to list packages{Style.RESET_ALL}")
            return []
        
        print(f"{Fore.GREEN}📦 Available Packages:{Style.RESET_ALL}")
        print(result.stdout)
        
        # Get package names for selection
        packages_result = self.run_aws_command("aws iot list-packages --query 'packageSummaries[].packageName' --output text")
        
        if packages_result and packages_result.returncode == 0:
            package_names = packages_result.stdout.strip().split()
            return [name for name in package_names if name]
        
        return []
    
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
                if ',' in user_input:
                    choices = [int(x.strip()) for x in user_input.split(',')]
                else:
                    choices = [int(user_input)]
                
                # Validate all choices
                invalid_choices = [c for c in choices if c < 1 or c > len(available_groups)]
                
                if invalid_choices:
                    print(f"{Fore.RED}❌ Invalid choices: {', '.join(map(str, invalid_choices))}. Please enter numbers between 1-{len(available_groups)}{Style.RESET_ALL}")
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
        
        result = self.run_aws_command(f"aws iot list-package-versions --package-name {package_name} --query 'packageVersionSummaries[].{{VersionName:versionName,Status:status,CreatedDate:creationDate}}' --output table")
        
        if result and result.returncode == 0:
            print(f"{Fore.GREEN}📋 Available Versions:{Style.RESET_ALL}")
            print(result.stdout)
        
        version = input(f"{Fore.YELLOW}📝 Enter package version: {Style.RESET_ALL}").strip()
        
        if not version:
            print(f"{Fore.RED}❌ No version provided{Style.RESET_ALL}")
            return None
        
        # Get AWS region and account ID to format the ARN
        region_result = self.run_aws_command("aws configure get region")
        account_result = self.run_aws_command("aws sts get-caller-identity --query Account --output text")
        
        region = region_result.stdout.strip() if region_result and region_result.returncode == 0 else "us-east-1"
        account_id = account_result.stdout.strip() if account_result and account_result.returncode == 0 else "*"
        
        # Format the package version ARN: arn:aws:iot:region:account:package/packageName/version/versionName
        package_arn = f"arn:aws:iot:{region}:{account_id}:package/{package_name}/version/{version}"
        
        return {
            'version': version,
            'arn': package_arn
        }
    
    def generate_job_id(self, package_name, version_name):
        """Generate job ID from package name, version and timestamp"""
        import time
        timestamp = int(time.time())
        # Clean version for job ID (remove dots)
        clean_version = version_name.replace('.', '')
        job_id = f"upgrade{package_name.capitalize()}{clean_version}_{timestamp}"
        return job_id
    
    def create_job_document(self, package_name, version_name):
        """Create job document with AWS IoT presigned URL placeholders"""
        job_document = {
            "ota": {
                "packages": {
                    package_name: {
                        "attributes": f"${{aws:iot:package:{package_name}:version:{version_name}:attributes}}",
                        "artifact": {
                            "s3PresignedUrl": f"${{aws:iot:package:{package_name}:version:{version_name}:artifact:s3-presigned-url}}"
                        }
                    }
                }
            }
        }
        
        return job_document
    
    def create_job(self, job_id, thing_groups, job_document, package_name, package_version_info):
        """Create the IoT job with proper configuration for multiple groups"""
        print(f"\n{Fore.BLUE}🚀 Creating IoT job...{Style.RESET_ALL}")
        
        # Get AWS region and account ID for proper ARN
        region_result = self.run_aws_command("aws configure get region")
        account_result = self.run_aws_command("aws sts get-caller-identity --query Account --output text")
        
        region = region_result.stdout.strip() if region_result and region_result.returncode == 0 else "us-east-1"
        account_id = account_result.stdout.strip() if account_result and account_result.returncode == 0 else "*"
        
        # Create ARNs for all selected groups
        target_arns = [f"arn:aws:iot:{region}:{account_id}:thinggroup/{group}" for group in thing_groups]
        
        job_config = {
            "targets": target_arns,
            "document": json.dumps(job_document),
            "description": f"OTA update job for {', '.join(thing_groups)}",
            "targetSelection": "CONTINUOUS",
            "destinationPackageVersions": [package_version_info['arn']],
            "presignedUrlConfig": {
                "roleArn": f"arn:aws:iam::{account_id}:role/IoTJobsRole",
                "expiresInSec": 3600
            }
        }
        
        if self.debug_mode:
            print(f"{Fore.CYAN}📋 DEBUG - Job config: {json.dumps(job_config, indent=2)}{Style.RESET_ALL}")
        
        # Create the job
        command = f"aws iot create-job --job-id {job_id} --cli-input-json '{json.dumps(job_config)}'"
        result = self.run_aws_command(command)
        
        if result and result.returncode == 0:
            print(f"{Fore.GREEN}✅ IoT job created successfully!{Style.RESET_ALL}")
            
            # Parse and display job details
            try:
                job_response = json.loads(result.stdout)
                print(f"\n{Fore.CYAN}📋 Job Details:{Style.RESET_ALL}")
                print(f"{Fore.GREEN}🆔 Job ID: {job_response.get('jobId', 'N/A')}{Style.RESET_ALL}")
                print(f"{Fore.GREEN}🔗 Job ARN: {job_response.get('jobArn', 'N/A')}{Style.RESET_ALL}")
                print(f"{Fore.GREEN}👥 Target Groups: {', '.join(thing_groups)}{Style.RESET_ALL}")
                print(f"{Fore.GREEN}📦 Package ARN: {package_version_info['arn']}{Style.RESET_ALL}")
            except json.JSONDecodeError:
                print(f"{Fore.YELLOW}⚠️  Job created but couldn't parse response details{Style.RESET_ALL}")
            
            return True
        else:
            print(f"{Fore.RED}❌ Failed to create IoT job{Style.RESET_ALL}")
            if result and result.stderr:
                print(f"{Fore.RED}Error: {result.stderr}{Style.RESET_ALL}")
            return False
    
    def run(self):
        """Main execution flow"""
        self.print_header()
        
        # Get debug mode preference
        self.get_debug_mode()
        
        # Get available resources
        thing_groups = self.get_thing_groups()
        packages = self.get_packages()
        
        if not thing_groups:
            print(f"{Fore.RED}❌ No thing groups available. Please run provision script first.{Style.RESET_ALL}")
            sys.exit(1)
        
        if not packages:
            print(f"{Fore.RED}❌ No packages available. Please run provision script first.{Style.RESET_ALL}")
            sys.exit(1)
        
        # Get user selections
        selected_groups = self.select_thing_groups(thing_groups)
        selected_package = self.select_package(packages)
        package_version_info = self.get_package_version(selected_package)
        
        if not all([selected_groups, selected_package, package_version_info]):
            print(f"{Fore.RED}❌ Missing required information{Style.RESET_ALL}")
            sys.exit(1)
        
        # Generate base job ID
        base_job_id = self.generate_job_id(selected_package, package_version_info['version'])
        
        # Create job document
        job_document = self.create_job_document(selected_package, package_version_info['version'])
        
        print(f"\n{Fore.CYAN}🎯 Job Configuration:{Style.RESET_ALL}")
        print(f"{Fore.GREEN}🆔 Base Job ID: {base_job_id}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}👥 Thing Groups: {', '.join(selected_groups)}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}📦 Package: {selected_package} v{package_version_info['version']}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}🔗 Package ARN: {package_version_info['arn']}{Style.RESET_ALL}")
        
        print(f"\n{Fore.CYAN}📋 Job Document:{Style.RESET_ALL}")
        print(json.dumps(job_document, indent=2))
        
        # Create single job for all selected groups
        success = self.create_job(base_job_id, selected_groups, job_document, selected_package, package_version_info)
        
        if success:
            print(f"\n{Fore.GREEN}🎉 Job creation completed successfully!{Style.RESET_ALL}")
            print(f"{Fore.CYAN}💡 Use the simulate_job_execution script to test job execution{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.RED}❌ Job creation failed{Style.RESET_ALL}")
            sys.exit(1)

if __name__ == "__main__":
    job_creator = IoTJobCreator()
    job_creator.run()