#!/usr/bin/env python3

# Suppress urllib3 SSL warnings on macOS
import warnings
warnings.filterwarnings('ignore', message='urllib3 v2 only supports OpenSSL 1.1.1+')

import subprocess
import json
import os
import sys
import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Semaphore
from colorama import Fore, Style, init

# Initialize colorama
init()

class IoTJobSimulator:
    def __init__(self):
        self.temp_dir = "/tmp/iot_job_artifacts"
        self.verbose_mode = False
        self.debug_mode = False
        self.jobs_endpoint = None
        self.region = None
        self.account_id = None
        
        # Create temp directory
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # Rate limiting semaphore for job execution updates (200 TPS limit)
        self.job_execution_semaphore = Semaphore(150)  # Use 150 for safety
    
    def get_jobs_endpoint(self):
        """Get IoT Jobs endpoint"""
        result = self.run_aws_command_basic(f"aws iot describe-endpoint --endpoint-type iot:Jobs --region {self.region} --query 'endpointAddress' --output text")
        if result and result.returncode == 0:
            self.jobs_endpoint = result.stdout.strip()
        else:
            print(f"{Fore.RED}❌ Failed to get IoT Jobs endpoint{Style.RESET_ALL}")
    
    def run_aws_command_basic(self, command, capture_output=True):
        """Basic AWS CLI command execution without debug output"""
        try:
            return subprocess.run(command, shell=True, capture_output=capture_output, text=True)
        except Exception as e:
            print(f"{Fore.RED}❌ Error executing command: {e}{Style.RESET_ALL}")
            return None
    
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
        print(f"{Fore.CYAN}🤖 AWS IoT Job Execution Simulator{Style.RESET_ALL}")
        print(f"{Fore.CYAN}===================================={Style.RESET_ALL}\n")
        
        print(f"{Fore.YELLOW}📚 LEARNING GOAL:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}This script simulates realistic device behavior during IoT Job execution. It demonstrates{Style.RESET_ALL}")
        print(f"{Fore.CYAN}how devices download firmware from S3 using presigned URLs, process the updates, and{Style.RESET_ALL}")
        print(f"{Fore.CYAN}report success/failure status back to AWS IoT. This completes the OTA update lifecycle{Style.RESET_ALL}")
        print(f"{Fore.CYAN}and shows how Jobs, Package Catalog, and device shadows work together.{Style.RESET_ALL}\n")
        
        # Get and display region and account ID
        region_result = self.run_aws_command_basic("aws configure get region")
        account_result = self.run_aws_command_basic("aws sts get-caller-identity --query Account --output text")
        
        self.region = region_result.stdout.strip() if region_result and region_result.returncode == 0 else "us-east-1"
        self.account_id = account_result.stdout.strip() if account_result and account_result.returncode == 0 else "unknown"
        
        print(f"{Fore.CYAN}📍 Region: {Fore.GREEN}{self.region}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}🆔 Account ID: {Fore.GREEN}{self.account_id}{Style.RESET_ALL}\n")
    
    def get_verbose_mode(self):
        """Ask user for verbose mode"""
        choice = input(f"{Fore.YELLOW}🔧 Enable verbose mode (show input/output of job queries)? [y/N]: {Style.RESET_ALL}").strip().lower()
        self.verbose_mode = choice in ['y', 'yes']
        
        if self.verbose_mode:
            print(f"{Fore.GREEN}✅ Verbose mode enabled{Style.RESET_ALL}\n")
    
    def get_debug_mode(self):
        """Ask user for debug mode"""
        choice = input(f"{Fore.YELLOW}🔧 Enable debug mode (show all AWS commands and outputs)? [y/N]: {Style.RESET_ALL}").strip().lower()
        self.debug_mode = choice in ['y', 'yes']
        
        if self.debug_mode:
            print(f"{Fore.GREEN}✅ Debug mode enabled{Style.RESET_ALL}\n")
    
    def scan_active_jobs(self):
        """Scan for active IoT jobs"""
        print(f"{Fore.BLUE}🔍 Scanning for active IoT jobs...{Style.RESET_ALL}")
        
        # Get IN_PROGRESS jobs only (QUEUED is not a valid status for list-jobs)
        in_progress_result = self.run_aws_command("aws iot list-jobs --status IN_PROGRESS --query 'jobs[].{JobId:jobId,Status:status,CreatedAt:createdAt}' --output table")
        
        print(f"{Fore.GREEN}📋 Active Jobs:{Style.RESET_ALL}")
        if in_progress_result and in_progress_result.returncode == 0:
            print(in_progress_result.stdout)
        
        # Get job IDs for selection
        job_ids = []
        
        in_progress_ids_result = self.run_aws_command("aws iot list-jobs --status IN_PROGRESS --query 'jobs[].jobId' --output text")
        if in_progress_ids_result and in_progress_ids_result.returncode == 0:
            job_ids.extend([job_id for job_id in in_progress_ids_result.stdout.strip().split() if job_id])
        
        return job_ids
    
    def get_job_executions(self, job_id):
        """Get job executions for a specific job"""
        print(f"{Fore.BLUE}📊 Getting job executions for job: {Fore.YELLOW}{job_id}{Style.RESET_ALL}")
        
        thing_names = []
        
        # Get QUEUED executions
        queued_result = self.run_aws_command(f"aws iot list-job-executions-for-job --job-id {job_id} --status QUEUED")
        if queued_result and queued_result.returncode == 0:
            try:
                queued_data = json.loads(queued_result.stdout)
                queued_executions = queued_data.get('executionSummaries', [])
                if queued_executions:
                    print(f"{Fore.GREEN}📋 QUEUED Job Executions: {len(queued_executions)}{Style.RESET_ALL}")
                    for exec_summary in queued_executions:
                        if 'thingArn' in exec_summary:
                            # Extract thing name from ARN: arn:aws:iot:region:account:thing/THING_NAME
                            thing_name = exec_summary['thingArn'].split('/')[-1]
                            thing_names.append(thing_name)
            except json.JSONDecodeError:
                pass
        
        # Get IN_PROGRESS executions
        in_progress_result = self.run_aws_command(f"aws iot list-job-executions-for-job --job-id {job_id} --status IN_PROGRESS")
        if in_progress_result and in_progress_result.returncode == 0:
            try:
                in_progress_data = json.loads(in_progress_result.stdout)
                in_progress_executions = in_progress_data.get('executionSummaries', [])
                if in_progress_executions:
                    print(f"{Fore.GREEN}📋 IN_PROGRESS Job Executions: {len(in_progress_executions)}{Style.RESET_ALL}")
                    for exec_summary in in_progress_executions:
                        if 'thingArn' in exec_summary:
                            # Extract thing name from ARN: arn:aws:iot:region:account:thing/THING_NAME
                            thing_name = exec_summary['thingArn'].split('/')[-1]
                            thing_names.append(thing_name)
            except json.JSONDecodeError:
                pass
        
        print(f"{Fore.CYAN}📊 Total executions found: {len(thing_names)}{Style.RESET_ALL}")
        return thing_names
    
    def download_artifact_from_job(self, job_document, job_id, thing_name, execution_number):
        """Download real artifact from S3 presigned URL"""
        if self.verbose_mode or self.debug_mode:
            print(f"{Fore.YELLOW}⬇️  Extracting S3 presigned URL from job document...{Style.RESET_ALL}")
        
        try:
            # Handle both string and dict job documents
            if isinstance(job_document, str):
                job_doc = json.loads(job_document)
            else:
                job_doc = job_document
            
            if self.debug_mode:
                print(f"{Fore.CYAN}📋 DEBUG - Job document: {json.dumps(job_doc, indent=2)}{Style.RESET_ALL}")
            
            # Extract s3PresignedUrl from job document
            packages = job_doc.get('ota', {}).get('packages', {})
            presigned_url = None
            
            for package_name, package_info in packages.items():
                artifact = package_info.get('artifact', {})
                presigned_url = artifact.get('s3PresignedUrl')
                if presigned_url:
                    if self.debug_mode:
                        print(f"{Fore.CYAN}🔧 DEBUG - Found presigned URL in package: {package_name}{Style.RESET_ALL}")
                    break
            
            if not presigned_url:
                if self.verbose_mode or self.debug_mode:
                    print(f"{Fore.RED}❌ No S3 presigned URL found in job document{Style.RESET_ALL}")
                return False
            
            if self.verbose_mode or self.debug_mode:
                print(f"{Fore.GREEN}🔗 Found S3 presigned URL{Style.RESET_ALL}")
                if self.debug_mode:
                    print(f"{Fore.CYAN}🔗 DEBUG - Presigned URL: {presigned_url}{Style.RESET_ALL}")
            
            # Create unique filename
            artifact_file = os.path.join(self.temp_dir, f"{thing_name}_{job_id}_v{execution_number}.bin")
            
            # Download artifact from S3
            if self.verbose_mode or self.debug_mode:
                print(f"{Fore.BLUE}📥 Downloading artifact from S3...{Style.RESET_ALL}")
            
            if self.debug_mode:
                print(f"{Fore.CYAN}🔧 DEBUG - Downloading to: {artifact_file}{Style.RESET_ALL}")
            
            response = requests.get(presigned_url, stream=True, timeout=30)
            response.raise_for_status()
            
            if self.debug_mode:
                print(f"{Fore.CYAN}🔧 DEBUG - HTTP response status: {response.status_code}{Style.RESET_ALL}")
            
            with open(artifact_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            if os.path.exists(artifact_file) and os.path.getsize(artifact_file) > 0:
                file_size = self.get_human_readable_size(os.path.getsize(artifact_file))
                if self.verbose_mode or self.debug_mode:
                    print(f"{Fore.GREEN}📦 Artifact downloaded: {Fore.CYAN}{os.path.basename(artifact_file)}{Style.RESET_ALL} ({file_size})")
                
                # Simulate processing time (reduced for parallel execution)
                time.sleep(0.1)
                
                # Clean up artifact
                os.remove(artifact_file)
                if self.verbose_mode or self.debug_mode:
                    print(f"{Fore.YELLOW}🗑️  Artifact cleaned up{Style.RESET_ALL}")
                return True
            else:
                if self.verbose_mode or self.debug_mode:
                    print(f"{Fore.RED}❌ Downloaded file is empty or invalid{Style.RESET_ALL}")
                if os.path.exists(artifact_file):
                    os.remove(artifact_file)
                return False
                
        except Exception as e:
            if self.verbose_mode or self.debug_mode:
                print(f"{Fore.RED}❌ Failed to download artifact: {e}{Style.RESET_ALL}")
            return False
    
    def get_human_readable_size(self, size_bytes):
        """Convert bytes to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f}{unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f}TB"
    
    def update_job_execution_status(self, job_id, thing_name, should_succeed):
        """Update job execution status"""
        if should_succeed:
            if self.verbose_mode:
                print(f"{Fore.GREEN}✅ Updating job execution to SUCCEEDED{Style.RESET_ALL}")
            result = self.run_aws_command(f"aws iot-jobs-data update-job-execution --job-id {job_id} --thing-name {thing_name} --status SUCCEEDED --endpoint-url https://{self.jobs_endpoint}")
        else:
            if self.verbose_mode:
                print(f"{Fore.RED}❌ Updating job execution to FAILED{Style.RESET_ALL}")
            status_details = json.dumps({"failureType": "DOWNLOAD_FAILURE", "failureReason": "Simulated failure"})
            result = self.run_aws_command(f"aws iot-jobs-data update-job-execution --job-id {job_id} --thing-name {thing_name} --status FAILED --status-details '{status_details}' --endpoint-url https://{self.jobs_endpoint}")
        
        return result and result.returncode == 0
    
    def process_job_execution(self, job_id, thing_name, execution_number, should_succeed, index, total):
        """Process a single job execution with rate limiting"""
        with self.job_execution_semaphore:
            if index % 20 == 1 or self.verbose_mode:  # Progress update every 20 executions or in verbose mode
                print(f"{Fore.MAGENTA}🔧 Processing execution {index}/{total} for thing: {Fore.YELLOW}{thing_name}{Style.RESET_ALL}")
            
            # Get job execution details
            if self.verbose_mode:
                print(f"{Fore.CYAN}📥 Input - Getting job execution details:{Style.RESET_ALL}")
                print(f"aws iot-jobs-data describe-job-execution --job-id {job_id} --thing-name {thing_name} --include-job-document --endpoint-url https://{self.jobs_endpoint}")
            
            result = self.run_aws_command(f"aws iot-jobs-data describe-job-execution --job-id {job_id} --thing-name {thing_name} --include-job-document --endpoint-url https://{self.jobs_endpoint}")
            
            if not result or result.returncode != 0:
                print(f"{Fore.RED}❌ Failed to get job execution details for {thing_name}{Style.RESET_ALL}")
                return False
            
            if self.verbose_mode:
                print(f"{Fore.CYAN}📤 Output - Job execution details:{Style.RESET_ALL}")
                print(result.stdout)
            
            try:
                job_execution = json.loads(result.stdout)
                job_document = job_execution.get('execution', {}).get('jobDocument')
                
                if job_document:
                    if self.verbose_mode:
                        print(f"{Fore.GREEN}📄 Job document retrieved{Style.RESET_ALL}")
                        print(f"{Fore.CYAN}📋 Job Document:{Style.RESET_ALL}")
                        print(json.dumps(job_document, indent=2))
                    
                    # Download real artifact from S3
                    download_success = self.download_artifact_from_job(job_document, job_id, thing_name, execution_number)
                    
                    # Update job execution status based on should_succeed flag
                    if should_succeed and download_success:
                        success = self.update_job_execution_status(job_id, thing_name, True)
                        return success
                    elif not should_succeed:
                        # Intentionally fail this execution
                        success = self.update_job_execution_status(job_id, thing_name, False)
                        return False  # Return False to indicate planned failure
                    else:
                        # Download failed unexpectedly
                        if self.verbose_mode:
                            print(f"{Fore.RED}❌ Download failed - marking job execution as FAILED{Style.RESET_ALL}")
                        return self.update_job_execution_status(job_id, thing_name, False)
                else:
                    print(f"{Fore.RED}❌ No job document found for {thing_name}{Style.RESET_ALL}")
                    return False
                    
            except json.JSONDecodeError as e:
                print(f"{Fore.RED}❌ Failed to parse job execution response for {thing_name}: {e}{Style.RESET_ALL}")
                return False
            
            time.sleep(0.007)  # Rate limiting: 150 TPS
    
    def get_user_inputs(self, available_jobs, thing_names, total_executions):
        """Get user inputs for job simulation"""
        # Job selection
        print(f"\n{Fore.YELLOW}📝 Enter the Job ID to simulate:{Style.RESET_ALL}")
        selected_job_id = input().strip()
        
        if not selected_job_id or selected_job_id not in available_jobs:
            print(f"{Fore.RED}❌ Invalid job ID{Style.RESET_ALL}")
            return None, None, None
        
        return selected_job_id, None, None
    
    def run(self):
        """Main execution flow"""
        self.print_header()
        
        # Get IoT data ATS endpoint after region is set
        self.get_jobs_endpoint()
        
        # Get verbose and debug mode preferences
        self.get_verbose_mode()
        self.get_debug_mode()
        
        # Scan for active jobs
        available_jobs = self.scan_active_jobs()
        
        if not available_jobs:
            print(f"{Fore.RED}❌ No active jobs found{Style.RESET_ALL}")
            sys.exit(1)
        
        # Let user select a job
        selected_job_id, executions_to_process, success_percentage = self.get_user_inputs(available_jobs, [], 0)
        
        if not selected_job_id:
            sys.exit(1)
        
        # Get job executions
        thing_names = self.get_job_executions(selected_job_id)
        
        if not thing_names:
            print(f"{Fore.RED}❌ No pending job executions found for job: {selected_job_id}{Style.RESET_ALL}")
            sys.exit(1)
        
        total_executions = len(thing_names)
        
        # Get execution scope and success percentage only
        print(f"\n{Fore.GREEN}📊 Found {total_executions} pending job executions{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}🎯 Process ALL executions or specify a number? [ALL/number]:{Style.RESET_ALL}")
        execution_scope = input().strip()
        
        executions_to_process = total_executions
        if execution_scope.upper() != "ALL" and execution_scope.isdigit():
            executions_to_process = min(int(execution_scope), total_executions)
        
        # Success percentage
        while True:
            try:
                success_percentage = int(input(f"{Fore.YELLOW}📈 Enter success percentage (0-100):{Style.RESET_ALL}"))
                if 0 <= success_percentage <= 100:
                    break
                print(f"{Fore.RED}❌ Please enter a number between 0 and 100{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED}❌ Please enter a valid number{Style.RESET_ALL}")
        
        # Calculate success and failure counts
        success_count = (executions_to_process * success_percentage) // 100
        failure_count = executions_to_process - success_count
        
        print(f"\n{Fore.CYAN}🎯 Execution Plan:{Style.RESET_ALL}")
        print(f"{Fore.GREEN}✅ Success: {success_count} executions{Style.RESET_ALL}")
        print(f"{Fore.RED}❌ Failure: {failure_count} executions{Style.RESET_ALL}")
        print(f"{Fore.BLUE}📊 Total: {executions_to_process} executions{Style.RESET_ALL}\n")
        
        # Prepare execution data
        execution_data = []
        for i, thing_name in enumerate(thing_names[:executions_to_process], 1):
            should_succeed = i <= success_count
            
            # Get execution number
            exec_result = self.run_aws_command(f"aws iot describe-job-execution --job-id {selected_job_id} --thing-name {thing_name} --query 'execution.executionNumber' --output text")
            execution_number = exec_result.stdout.strip() if exec_result and exec_result.returncode == 0 else "1"
            
            execution_data.append((selected_job_id, thing_name, execution_number, should_succeed, i, executions_to_process))
            
            if self.verbose_mode:
                status = "SUCCESS" if should_succeed else "FAILURE"
                print(f"{Fore.CYAN}📋 Planned execution {i}: {thing_name} -> {status}{Style.RESET_ALL}")
        
        # Process job executions in parallel
        print(f"{Fore.BLUE}🚀 Processing {executions_to_process} job executions in parallel (150 TPS)...{Style.RESET_ALL}")
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=150) as executor:
            futures = [executor.submit(self.process_job_execution, *data) for data in execution_data]
            
            success_count_actual = 0
            failed_count_actual = 0
            completed = 0
            for future in as_completed(futures):
                completed += 1
                if future.result():
                    success_count_actual += 1
                else:
                    failed_count_actual += 1
                
                # Show individual results
                thing_name = execution_data[completed-1][1]  # Get thing name from execution data
                result_status = "✅ SUCCESS" if future.result() else "❌ FAILED"
                print(f"{Fore.CYAN}📋 [{completed}/{executions_to_process}] {thing_name}: {result_status}{Style.RESET_ALL}")
                
                # Progress update every 20 completions
                if completed % 20 == 0 or completed == executions_to_process:
                    print(f"{Fore.CYAN}📊 Progress: {completed}/{executions_to_process} executions processed, {success_count_actual} successful, {failed_count_actual} failed{Style.RESET_ALL}")
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"{Fore.GREEN}🎉 Job execution simulation completed!{Style.RESET_ALL}")
        print(f"{Fore.CYAN}📊 Processed {executions_to_process} executions: {success_count_actual} successful, {failed_count_actual} failed{Style.RESET_ALL}")
        print(f"{Fore.CYAN}⏱️  Total execution time: {duration:.2f} seconds{Style.RESET_ALL}")
    
    def cleanup(self):
        """Cleanup temporary files"""
        print(f"\n{Fore.YELLOW}🧹 Cleaning up temporary files...{Style.RESET_ALL}")
        try:
            import shutil
            shutil.rmtree(self.temp_dir, ignore_errors=True)
            print(f"{Fore.GREEN}✅ Cleanup completed{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.YELLOW}⚠️  Cleanup warning: {e}{Style.RESET_ALL}")

if __name__ == "__main__":
    simulator = IoTJobSimulator()
    try:
        simulator.run()
    finally:
        simulator.cleanup()