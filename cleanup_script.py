#!/usr/bin/env python3

import subprocess
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Semaphore
from colorama import Fore, Style, init
from threading import Lock

# Initialize colorama
init()

class IoTCleanup:
    def __init__(self):
        self.cleanup_options = {
            1: "ALL resources (Things, Thing Groups, Thing Types, Packages, S3 Buckets, IAM Roles)",
            2: "Things only",
            3: "Thing Groups only"
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
        print(f"{Fore.CYAN}🧹 AWS IoT Cleanup Script{Style.RESET_ALL}")
        print(f"{Fore.CYAN}========================{Style.RESET_ALL}\n")
        
        print(f"{Fore.YELLOW}📚 LEARNING GOAL:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}This script demonstrates proper AWS IoT resource cleanup and lifecycle management.{Style.RESET_ALL}")
        print(f"{Fore.CYAN}It shows how to safely delete IoT resources in the correct order, handle dependencies{Style.RESET_ALL}")
        print(f"{Fore.CYAN}between services, and avoid orphaned resources. Understanding cleanup is crucial for{Style.RESET_ALL}")
        print(f"{Fore.CYAN}cost management and maintaining a clean AWS environment.{Style.RESET_ALL}\n")
    
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
    
    def get_debug_mode(self):
        """Ask user for debug mode"""
        choice = input(f"{Fore.YELLOW}🔧 Enable debug mode (show all commands and outputs)? [y/N]: {Style.RESET_ALL}").strip().lower()
        self.debug_mode = choice in ['y', 'yes']
        
        if self.debug_mode:
            print(f"{Fore.GREEN}✅ Debug mode enabled{Style.RESET_ALL}\n")
    
    def confirm_deletion(self, choice):
        """Confirm deletion with user"""
        print(f"\n{Fore.RED}⚠️  WARNING: This will permanently delete:{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{self.cleanup_options[choice]}{Style.RESET_ALL}")
        
        confirm = input(f"\n{Fore.YELLOW}Type 'DELETE' to confirm: {Style.RESET_ALL}")
        return confirm == "DELETE"
    
    def delete_single_thing(self, thing_name, index, total):
        """Delete a single IoT thing (AWS automatically removes from groups)"""
        with self.thing_deletion_semaphore:
            # Delete the thing (AWS automatically removes from all groups)
            delete_result = self.run_aws_command(f"aws iot delete-thing --thing-name {thing_name}")
            
            if delete_result and delete_result.returncode == 0:
                with self.progress_lock:
                    self.deleted_count += 1
                    print(f"{Fore.GREEN}✅ [{self.deleted_count}/{total}] Deleted thing: {Fore.YELLOW}{thing_name}{Style.RESET_ALL}")
                return True
            else:
                print(f"{Fore.RED}❌ Failed to delete thing {thing_name}{Style.RESET_ALL}")
                return False
            
            time.sleep(0.0125)  # Rate limiting: 80 TPS
    
    def delete_things(self):
        """Delete all IoT things in parallel"""
        print(f"{Fore.BLUE}🔍 Scanning for IoT things...{Style.RESET_ALL}")
        
        result = self.run_aws_command("aws iot list-things --query 'things[].thingName' --output text")
        
        if not result or result.returncode != 0:
            print(f"{Fore.RED}❌ Failed to list things{Style.RESET_ALL}")
            return
        
        thing_names = result.stdout.strip().split()
        
        if not thing_names or thing_names == ['']:
            print(f"{Fore.YELLOW}ℹ️  No things found to delete{Style.RESET_ALL}")
            return
        
        print(f"{Fore.GREEN}📊 Found {len(thing_names)} things to delete{Style.RESET_ALL}")
        print(f"{Fore.BLUE}🚀 Deleting things in parallel (80 TPS)...{Style.RESET_ALL}")
        
        self.deleted_count = 0  # Reset counter
        
        with ThreadPoolExecutor(max_workers=80) as executor:
            futures = [executor.submit(self.delete_single_thing, thing_name, i, len(thing_names)) 
                      for i, thing_name in enumerate(thing_names, 1)]
            
            success_count = 0
            for future in as_completed(futures):
                if future.result():
                    success_count += 1
        
        print(f"{Fore.CYAN}📊 Things deletion completed: {success_count}/{len(thing_names)} successful{Style.RESET_ALL}")
    
    def delete_single_thing_group(self, group_name, index, total):
        """Delete a single thing group (handles both static and dynamic groups)"""
        # First, check if it's a dynamic thing group by getting its info
        if self.debug_mode:
            print(f"{Fore.CYAN}🔧 DEBUG - Checking group type: {group_name}{Style.RESET_ALL}")
        
        describe_result = self.run_aws_command(f"aws iot describe-thing-group --thing-group-name {group_name}")
        
        if describe_result and describe_result.returncode == 0:
            try:
                group_info = json.loads(describe_result.stdout)
                
                if self.debug_mode:
                    print(f"{Fore.CYAN}🔧 DEBUG - Group info: {json.dumps(group_info, indent=2)}{Style.RESET_ALL}")
                
                # Check if this is a dynamic thing group by looking for queryString at root level
                query_string = group_info.get('queryString')
                
                if query_string:
                    # This is a dynamic thing group - use 5 TPS limit
                    with self.dynamic_group_deletion_semaphore:
                        if self.debug_mode:
                            print(f"{Fore.CYAN}🔧 DEBUG - Dynamic group detected with query: {query_string}{Style.RESET_ALL}")
                        
                        delete_result = self.run_aws_command(f"aws iot delete-dynamic-thing-group --thing-group-name {group_name}")
                        
                        if delete_result and delete_result.returncode == 0:
                            with self.progress_lock:
                                self.deleted_count += 1
                                print(f"{Fore.GREEN}✅ [{self.deleted_count}/{total}] Deleted dynamic thing group: {Fore.YELLOW}{group_name}{Style.RESET_ALL}")
                            return True
                        else:
                            print(f"{Fore.RED}❌ Failed to delete dynamic thing group: {group_name}{Style.RESET_ALL}")
                            if delete_result and delete_result.stderr:
                                print(f"{Fore.RED}   Error: {delete_result.stderr.strip()}{Style.RESET_ALL}")
                            return False
                        
                        time.sleep(0.25)  # Rate limiting: 4 TPS
                
                else:
                    # This is a static thing group - use 100 TPS limit
                    with self.static_group_deletion_semaphore:
                        if self.debug_mode:
                            print(f"{Fore.CYAN}🔧 DEBUG - Static group detected (no queryString){Style.RESET_ALL}")
                        
                        delete_result = self.run_aws_command(f"aws iot delete-thing-group --thing-group-name {group_name}")
                        
                        if delete_result and delete_result.returncode == 0:
                            with self.progress_lock:
                                self.deleted_count += 1
                                print(f"{Fore.GREEN}✅ [{self.deleted_count}/{total}] Deleted static thing group: {Fore.YELLOW}{group_name}{Style.RESET_ALL}")
                            return True
                        else:
                            print(f"{Fore.RED}❌ Failed to delete static thing group: {group_name}{Style.RESET_ALL}")
                            if delete_result and delete_result.stderr:
                                print(f"{Fore.RED}   Error: {delete_result.stderr.strip()}{Style.RESET_ALL}")
                            return False
                        
                        time.sleep(0.0125)  # Rate limiting: 80 TPS
            
            except json.JSONDecodeError as e:
                if self.debug_mode:
                    print(f"{Fore.RED}🔧 DEBUG - Failed to parse group info: {e}{Style.RESET_ALL}")
                return False
        
        else:
            print(f"{Fore.RED}❌ Failed to describe thing group: {group_name}{Style.RESET_ALL}")
            return False
    
    def delete_thing_groups(self):
        """Delete all thing groups in parallel"""
        print(f"{Fore.BLUE}🔍 Scanning for thing groups...{Style.RESET_ALL}")
        
        result = self.run_aws_command("aws iot list-thing-groups --query 'thingGroups[].groupName' --output text")
        
        if not result or result.returncode != 0:
            print(f"{Fore.RED}❌ Failed to list thing groups{Style.RESET_ALL}")
            return
        
        group_names = result.stdout.strip().split()
        
        if not group_names or group_names == ['']:
            print(f"{Fore.YELLOW}ℹ️  No thing groups found to delete{Style.RESET_ALL}")
            return
        
        print(f"{Fore.GREEN}📊 Found {len(group_names)} thing groups to delete{Style.RESET_ALL}")
        print(f"{Fore.BLUE}🚀 Deleting thing groups in parallel (80 TPS)...{Style.RESET_ALL}")
        
        self.deleted_count = 0  # Reset counter
        
        with ThreadPoolExecutor(max_workers=min(80, len(group_names))) as executor:
            futures = [executor.submit(self.delete_single_thing_group, group_name, i, len(group_names)) 
                      for i, group_name in enumerate(group_names, 1)]
            
            success_count = sum(1 for future in as_completed(futures) if future.result())
        
        print(f"{Fore.CYAN}📊 Thing groups deletion completed: {success_count}/{len(group_names)} successful{Style.RESET_ALL}")
    
    def deprecate_single_thing_type(self, type_name, index, total):
        """Deprecate a single thing type"""
        deprecate_result = self.run_aws_command(f"aws iot deprecate-thing-type --thing-type-name {type_name}")
        
        if deprecate_result and deprecate_result.returncode == 0:
            with self.progress_lock:
                self.deleted_count += 1
                print(f"{Fore.YELLOW}⏸️  [{self.deleted_count}/{total}] Deprecated thing type: {Fore.YELLOW}{type_name}{Style.RESET_ALL}")
            return True
        else:
            print(f"{Fore.YELLOW}⚠️  Thing type might already be deprecated: {type_name}{Style.RESET_ALL}")
            return False
    
    def delete_single_thing_type(self, type_name, index, total):
        """Delete a single thing type"""
        delete_result = self.run_aws_command(f"aws iot delete-thing-type --thing-type-name {type_name}")
        
        if delete_result and delete_result.returncode == 0:
            with self.progress_lock:
                self.deleted_count += 1
                print(f"{Fore.GREEN}✅ [{self.deleted_count}/{total}] Deleted thing type: {Fore.YELLOW}{type_name}{Style.RESET_ALL}")
            return True
        else:
            print(f"{Fore.RED}❌ Failed to delete thing type: {type_name}{Style.RESET_ALL}")
            return False
    
    def delete_thing_types(self):
        """Delete all thing types in parallel"""
        print(f"{Fore.BLUE}🔍 Scanning for thing types...{Style.RESET_ALL}")
        
        result = self.run_aws_command("aws iot list-thing-types --query 'thingTypes[].thingTypeName' --output text")
        
        if not result or result.returncode != 0:
            print(f"{Fore.RED}❌ Failed to list thing types{Style.RESET_ALL}")
            return
        
        type_names = result.stdout.strip().split()
        
        if not type_names or type_names == ['']:
            print(f"{Fore.YELLOW}ℹ️  No thing types found to delete{Style.RESET_ALL}")
            return
        
        print(f"{Fore.GREEN}📊 Found {len(type_names)} thing types to delete{Style.RESET_ALL}")
        
        # Deprecate thing types first in parallel
        print(f"{Fore.BLUE}🚀 Deprecating thing types in parallel...{Style.RESET_ALL}")
        
        self.deleted_count = 0  # Reset counter
        
        with ThreadPoolExecutor(max_workers=8) as executor:
            deprecate_futures = [executor.submit(self.deprecate_single_thing_type, type_name, i, len(type_names)) 
                               for i, type_name in enumerate(type_names, 1)]
            
            deprecate_success = sum(1 for future in as_completed(deprecate_futures) if future.result())
        
        print(f"{Fore.CYAN}📊 Thing types deprecation completed: {deprecate_success}/{len(type_names)} successful{Style.RESET_ALL}")
        
        # Wait 5 minutes before deletion
        print(f"{Fore.YELLOW}⏰ Waiting 5 minutes before deleting thing types...{Style.RESET_ALL}")
        for remaining in range(300, 0, -30):
            mins, secs = divmod(remaining, 60)
            print(f"{Fore.CYAN}⏳ Time remaining: {mins:02d}:{secs:02d}{Style.RESET_ALL}")
            time.sleep(30)
        
        # Delete thing types in parallel
        print(f"{Fore.BLUE}🚀 Deleting thing types in parallel...{Style.RESET_ALL}")
        
        self.deleted_count = 0  # Reset counter
        
        with ThreadPoolExecutor(max_workers=8) as executor:
            delete_futures = [executor.submit(self.delete_single_thing_type, type_name, i, len(type_names)) 
                            for i, type_name in enumerate(type_names, 1)]
            
            delete_success = sum(1 for future in as_completed(delete_futures) if future.result())
        
        print(f"{Fore.CYAN}📊 Thing types deletion completed: {delete_success}/{len(type_names)} successful{Style.RESET_ALL}")
    
    def delete_single_package(self, package_name, index, total):
        """Delete a single IoT package and its versions"""
        with self.package_semaphore:
            # Delete package versions first
            versions_result = self.run_aws_command(f"aws iot list-package-versions --package-name {package_name} --query 'packageVersionSummaries[].versionName' --output text")
            
            if versions_result and versions_result.returncode == 0:
                version_names = versions_result.stdout.strip().split()
                for version_name in version_names:
                    if version_name:
                        self.run_aws_command(f"aws iot delete-package-version --package-name {package_name} --version-name {version_name}")
            
            # Delete the package
            delete_result = self.run_aws_command(f"aws iot delete-package --package-name {package_name}")
            
            if delete_result and delete_result.returncode == 0:
                with self.progress_lock:
                    self.deleted_count += 1
                    print(f"{Fore.GREEN}✅ [{self.deleted_count}/{total}] Deleted package: {Fore.YELLOW}{package_name}{Style.RESET_ALL}")
                return True
            else:
                print(f"{Fore.RED}❌ Failed to delete package: {package_name}{Style.RESET_ALL}")
                return False
            
            time.sleep(0.125)  # Rate limiting: 8 TPS
    
    def delete_packages(self):
        """Delete IoT software packages in parallel"""
        print(f"{Fore.BLUE}🔍 Scanning for IoT packages...{Style.RESET_ALL}")
        
        result = self.run_aws_command("aws iot list-packages --query 'packageSummaries[].packageName' --output text")
        
        if not result or result.returncode != 0:
            print(f"{Fore.RED}❌ Failed to list packages{Style.RESET_ALL}")
            return
        
        package_names = result.stdout.strip().split()
        
        if not package_names or package_names == ['']:
            print(f"{Fore.YELLOW}ℹ️  No packages found to delete{Style.RESET_ALL}")
            return
        
        print(f"{Fore.GREEN}📊 Found {len(package_names)} packages to delete{Style.RESET_ALL}")
        print(f"{Fore.BLUE}🚀 Deleting packages in parallel (8 TPS)...{Style.RESET_ALL}")
        
        self.deleted_count = 0  # Reset counter
        
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(self.delete_single_package, package_name, i, len(package_names)) 
                      for i, package_name in enumerate(package_names, 1)]
            
            success_count = sum(1 for future in as_completed(futures) if future.result())
        
        print(f"{Fore.CYAN}📊 Packages deletion completed: {success_count}/{len(package_names)} successful{Style.RESET_ALL}")
    
    def delete_single_s3_bucket(self, bucket_name, index, total):
        """Delete a single S3 bucket with all versions"""
        # Delete all object versions first
        versions_result = self.run_aws_command(f"aws s3api list-object-versions --bucket {bucket_name} --query 'Versions[].{{Key:Key,VersionId:VersionId}}' --output json")
        
        if versions_result and versions_result.returncode == 0:
            try:
                versions = json.loads(versions_result.stdout)
                if versions:
                    for version in versions:
                        if version:
                            self.run_aws_command(f"aws s3api delete-object --bucket {bucket_name} --key {version['Key']} --version-id {version['VersionId']}")
            except (json.JSONDecodeError, KeyError, TypeError):
                pass
        
        # Delete delete markers
        markers_result = self.run_aws_command(f"aws s3api list-object-versions --bucket {bucket_name} --query 'DeleteMarkers[].{{Key:Key,VersionId:VersionId}}' --output json")
        
        if markers_result and markers_result.returncode == 0:
            try:
                markers = json.loads(markers_result.stdout)
                if markers:
                    for marker in markers:
                        if marker:
                            self.run_aws_command(f"aws s3api delete-object --bucket {bucket_name} --key {marker['Key']} --version-id {marker['VersionId']}")
            except (json.JSONDecodeError, KeyError, TypeError):
                pass
        
        # Delete bucket
        delete_result = self.run_aws_command(f"aws s3 rb s3://{bucket_name}")
        
        if delete_result and delete_result.returncode == 0:
            with self.progress_lock:
                self.deleted_count += 1
                print(f"{Fore.GREEN}✅ [{self.deleted_count}/{total}] Deleted S3 bucket: {Fore.YELLOW}{bucket_name}{Style.RESET_ALL}")
            return True
        else:
            print(f"{Fore.RED}❌ Failed to delete S3 bucket: {bucket_name}{Style.RESET_ALL}")
            return False
    
    def delete_s3_buckets(self):
        """Delete S3 buckets with iot-firmware prefix in parallel"""
        print(f"{Fore.BLUE}🔍 Scanning for IoT firmware S3 buckets...{Style.RESET_ALL}")
        
        result = self.run_aws_command("aws s3api list-buckets --query 'Buckets[?starts_with(Name, `iot-firmware`)].Name' --output text")
        
        if not result or result.returncode != 0:
            print(f"{Fore.RED}❌ Failed to list S3 buckets{Style.RESET_ALL}")
            return
        
        bucket_names = result.stdout.strip().split()
        
        if not bucket_names or bucket_names == ['']:
            print(f"{Fore.YELLOW}ℹ️  No IoT firmware buckets found to delete{Style.RESET_ALL}")
            return
        
        print(f"{Fore.GREEN}📊 Found {len(bucket_names)} buckets to delete{Style.RESET_ALL}")
        print(f"{Fore.BLUE}🚀 Deleting S3 buckets in parallel...{Style.RESET_ALL}")
        
        self.deleted_count = 0  # Reset counter
        
        with ThreadPoolExecutor(max_workers=min(10, len(bucket_names))) as executor:
            futures = [executor.submit(self.delete_single_s3_bucket, bucket_name, i, len(bucket_names)) 
                      for i, bucket_name in enumerate(bucket_names, 1)]
            
            success_count = sum(1 for future in as_completed(futures) if future.result())
        
        print(f"{Fore.CYAN}📊 S3 buckets deletion completed: {success_count}/{len(bucket_names)} successful{Style.RESET_ALL}")
    

    
    def delete_iot_jobs_role(self):
        """Delete IoT Jobs IAM role"""
        print(f"{Fore.BLUE}🔍 Deleting IoT Jobs IAM role...{Style.RESET_ALL}")
        
        # Delete inline policy first
        policy_result = self.run_aws_command("aws iam delete-role-policy --role-name IoTJobsRole --policy-name IoTJobsS3Policy")
        
        # Delete role
        delete_result = self.run_aws_command("aws iam delete-role --role-name IoTJobsRole")
        
        if delete_result and delete_result.returncode == 0:
            print(f"{Fore.GREEN}✅ IoT Jobs role deleted successfully{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}⚠️  IoT Jobs role might not exist or failed to delete{Style.RESET_ALL}")
    
    def disable_package_configuration(self):
        """Disable global package configuration for automated shadow updates"""
        print(f"{Fore.BLUE}📦 Disabling global package configuration...{Style.RESET_ALL}")
        
        result = self.run_aws_command("aws iot update-package-configuration --version-update-by-jobs-config 'enabled=false'")
        
        if result and result.returncode == 0:
            print(f"{Fore.GREEN}✅ Global package configuration disabled{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}⚠️  Package configuration might already be disabled or failed to update{Style.RESET_ALL}")
    
    def delete_package_config_role(self):
        """Delete package configuration IAM role"""
        print(f"{Fore.BLUE}🔍 Deleting package configuration IAM role...{Style.RESET_ALL}")
        
        # Delete inline policy first
        policy_result = self.run_aws_command("aws iam delete-role-policy --role-name IoTPackageConfigRole --policy-name PackageConfigPolicy")
        
        # Delete role
        delete_result = self.run_aws_command("aws iam delete-role --role-name IoTPackageConfigRole")
        
        if delete_result and delete_result.returncode == 0:
            print(f"{Fore.GREEN}✅ Package config role deleted successfully{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}⚠️  Package config role might not exist or failed to delete{Style.RESET_ALL}")
    
    def delete_jobs(self):
        """Delete all IoT jobs"""
        print(f"{Fore.BLUE}🔍 Scanning for IoT jobs...{Style.RESET_ALL}")
        
        # Get all jobs (IN_PROGRESS, COMPLETED, CANCELED, etc.)
        statuses = ["IN_PROGRESS", "COMPLETED", "CANCELED", "DELETION_IN_PROGRESS", "SCHEDULED"]
        all_jobs = []
        
        for status in statuses:
            result = self.run_aws_command(f"aws iot list-jobs --status {status} --query 'jobs[].jobId' --output text")
            if result and result.returncode == 0:
                job_ids = [job_id for job_id in result.stdout.strip().split() if job_id and job_id != 'None']
                all_jobs.extend(job_ids)
        
        if not all_jobs:
            print(f"{Fore.YELLOW}ℹ️  No jobs found to delete{Style.RESET_ALL}")
            return
        
        print(f"{Fore.GREEN}📊 Found {len(all_jobs)} jobs to delete{Style.RESET_ALL}")
        
        success_count = 0
        for i, job_id in enumerate(all_jobs, 1):
            print(f"{Fore.BLUE}[{i}/{len(all_jobs)}] Processing job: {Fore.YELLOW}{job_id}{Style.RESET_ALL}")
            
            # Get job status
            status_result = self.run_aws_command(f"aws iot describe-job --job-id {job_id} --query 'job.status' --output text")
            
            if status_result and status_result.returncode == 0:
                job_status = status_result.stdout.strip()
                
                # Cancel job if not completed/canceled, then delete
                if job_status in ["IN_PROGRESS", "SCHEDULED"]:
                    print(f"  ⏹️  Cancelling job (status: {job_status})...")
                    cancel_result = self.run_aws_command(f"aws iot cancel-job --job-id {job_id}")
                    if cancel_result and cancel_result.returncode == 0:
                        # Wait for cancellation to complete (max 60 seconds)
                        wait_time = 0
                        while wait_time < 60:
                            time.sleep(2)
                            wait_time += 2
                            status_check = self.run_aws_command(f"aws iot describe-job --job-id {job_id} --query 'job.status' --output text")
                            if status_check and status_check.returncode == 0:
                                current_status = status_check.stdout.strip()
                                if current_status == "CANCELED":
                                    print(f"  ✅ Job cancelled successfully")
                                    break
                        else:
                            print(f"  ⚠️  Cancellation timeout after 60 seconds, proceeding with deletion")
                
                
                # Delete job
                print(f"  🗑️  Deleting job: {job_id}")
                delete_result = self.run_aws_command(f"aws iot delete-job --job-id {job_id} --force")
                
                if delete_result and delete_result.returncode == 0:
                    success_count += 1
                    print(f"{Fore.GREEN}✅ Job deleted successfully{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}❌ Failed to delete job{Style.RESET_ALL}")
        
        print(f"{Fore.CYAN}📊 Jobs deletion completed: {success_count}/{len(all_jobs)} successful{Style.RESET_ALL}")
    
    def disable_fleet_indexing(self):
        """Disable Fleet Indexing"""
        print(f"{Fore.BLUE}🔍 Disabling Fleet Indexing...{Style.RESET_ALL}")
        
        result = self.run_aws_command('aws iot update-indexing-configuration --thing-indexing-configuration "thingIndexingMode=OFF" --thing-group-indexing-configuration "thingGroupIndexingMode=OFF"')
        
        if result and result.returncode == 0:
            print(f"{Fore.GREEN}✅ Fleet Indexing disabled successfully{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}⚠️  Fleet Indexing might already be disabled or failed to update{Style.RESET_ALL}")
    
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
    cleanup = IoTCleanup()
    cleanup.run()