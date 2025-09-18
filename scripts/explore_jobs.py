#!/usr/bin/env python3

import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Semaphore

import boto3
from botocore.exceptions import ClientError
from colorama import Fore, Style, init

# Initialize colorama
init()


class IoTJobsExplorer:
    def __init__(self):
        self.region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        self.account_id = None
        self.debug_mode = False
        self.iot_client = None
        self.iot_jobs_data_client = None
        self.sts_client = None
        self.jobs_endpoint = None

        # Rate limiting semaphore
        self.api_semaphore = Semaphore(10)

    def format_job_document(self, job_doc):
        """Format job document as properly indented JSON"""
        if not job_doc:
            print(f"{Fore.YELLOW}  No job document available{Style.RESET_ALL}")
            return

        # Parse string to dict if needed
        if isinstance(job_doc, str):
            try:
                job_doc = json.loads(job_doc)
            except json.JSONDecodeError:
                print(job_doc)
                return

        # Format as clean JSON with proper indentation
        formatted_json = json.dumps(job_doc, indent=2, separators=(",", ": "))
        print(formatted_json)

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

            # Get IoT Jobs endpoint
            endpoint_response = self.iot_client.describe_endpoint(endpointType="iot:Jobs")
            self.jobs_endpoint = endpoint_response["endpointAddress"]

            # Initialize IoT Jobs Data client with endpoint
            self.iot_jobs_data_client = boto3.client(
                "iot-jobs-data", region_name=self.region, endpoint_url=f"https://{self.jobs_endpoint}"
            )

            if self.debug_mode:
                print("🔍 DEBUG: Client configuration:")
                print(f"   IoT Service: {self.iot_client.meta.service_model.service_name}")
                print(f"   Jobs Endpoint: {self.jobs_endpoint}")

            return True
        except Exception as e:
            print(f"❌ Error initializing AWS clients: {str(e)}")
            return False

    def print_header(self):
        print(f"{Fore.CYAN}🔍 AWS IoT Jobs Explorer (Boto3){Style.RESET_ALL}")
        print(f"{Fore.CYAN}=================================={Style.RESET_ALL}\n")

        print(f"{Fore.YELLOW}📚 LEARNING GOAL:{Style.RESET_ALL}")
        print(
            f"{Fore.CYAN}This script helps you explore and understand AWS IoT Jobs in detail. You'll learn how{Style.RESET_ALL}"
        )
        print(
            f"{Fore.CYAN}to inspect job configurations, monitor job executions across devices, and understand{Style.RESET_ALL}"
        )
        print(
            f"{Fore.CYAN}job status reporting. This is essential for managing OTA deployments and troubleshooting{Style.RESET_ALL}"
        )
        print(f"{Fore.CYAN}device update issues in production IoT environments.{Style.RESET_ALL}\n")

        # Initialize clients and display info
        if not self.initialize_clients():
            sys.exit(1)

        print(f"{Fore.CYAN}📍 Region: {Fore.GREEN}{self.region}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}🆔 Account ID: {Fore.GREEN}{self.account_id}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}🔗 Jobs Endpoint: {Fore.GREEN}{self.jobs_endpoint}{Style.RESET_ALL}\n")

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

    def get_exploration_choice(self):
        """Get exploration option from user"""
        options = {
            1: "List all jobs (overview)",
            2: "Explore specific job by ID",
            3: "Explore job execution by device and job ID",
            4: "List job executions for a specific job",
        }

        print(f"{Fore.YELLOW}🎯 Select exploration option:{Style.RESET_ALL}")  # nosec B608
        for num, description in options.items():
            print(f"{Fore.CYAN}{num}. {description}{Style.RESET_ALL}")

        while True:
            try:
                choice = int(input(f"{Fore.YELLOW}Enter choice [1-4]: {Style.RESET_ALL}"))
                if 1 <= choice <= 4:
                    return choice
                print(f"{Fore.RED}❌ Invalid choice. Please enter 1-4{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED}❌ Please enter a valid number{Style.RESET_ALL}")

    def get_jobs_by_status_parallel(self, status):
        """Get jobs by status in parallel"""
        with self.api_semaphore:
            response = self.safe_api_call(
                self.iot_client.list_jobs,
                "Jobs List",
                f"{status} jobs",
                debug=False,  # Don't debug in parallel operations
                status=status,
                maxResults=250,
            )

            if response:
                jobs = response.get("jobs", [])
                return [(job, status) for job in jobs]
            return []

    def list_all_jobs(self):
        """List all jobs with their status"""
        print(f"{Fore.BLUE}🔍 Scanning for IoT jobs across all statuses...{Style.RESET_ALL}")

        statuses = ["IN_PROGRESS", "COMPLETED", "CANCELED", "DELETION_IN_PROGRESS", "SCHEDULED"]
        all_jobs = []

        if self.debug_mode:
            print(f"{Fore.BLUE}🔧 Checking job statuses sequentially (debug mode)...{Style.RESET_ALL}")
            for status in statuses:
                print(f"{Fore.CYAN}📊 Checking {status} jobs...{Style.RESET_ALL}")
                jobs_with_status = self.get_jobs_by_status_parallel(status)
                if jobs_with_status:
                    all_jobs.extend(jobs_with_status)
                    print(f"{Fore.GREEN}  ✅ Found {len(jobs_with_status)} {status} jobs{Style.RESET_ALL}")
                else:
                    print(f"{Fore.YELLOW}  ℹ️  No {status} jobs found{Style.RESET_ALL}")
        else:
            print(f"{Fore.BLUE}🔧 Checking job statuses in parallel...{Style.RESET_ALL}")
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(self.get_jobs_by_status_parallel, status) for status in statuses]

                for future in as_completed(futures):
                    jobs_with_status = future.result()
                    if jobs_with_status:
                        status = jobs_with_status[0][1]
                        print(f"{Fore.GREEN}  ✅ Found {len(jobs_with_status)} {status} jobs{Style.RESET_ALL}")
                        all_jobs.extend(jobs_with_status)

        if not all_jobs:
            print(f"{Fore.YELLOW}ℹ️  No jobs found in your account{Style.RESET_ALL}")
            return

        print(f"\n{Fore.GREEN}📋 Found {len(all_jobs)} total jobs:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'Job ID':<30} {'Status':<15} {'Created':<20} {'Completed':<20}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'-' * 85}{Style.RESET_ALL}")

        for job, _ in all_jobs:
            job_id = job.get("jobId", "N/A")[:29]
            status = job.get("status", "N/A")
            created = str(job.get("createdAt", "N/A"))[:19] if job.get("createdAt") else "N/A"
            completed = str(job.get("completedAt", "N/A"))[:19] if job.get("completedAt") else "N/A"

            # Color code by status
            if status == "COMPLETED":
                status_color = Fore.GREEN
            elif status == "IN_PROGRESS":
                status_color = Fore.BLUE
            elif status == "CANCELED":
                status_color = Fore.YELLOW
            else:
                status_color = Fore.RED

            print(
                f"{Fore.WHITE}{job_id:<30} {status_color}{status:<15}{Style.RESET_ALL} {Fore.CYAN}{created:<20} {completed:<20}{Style.RESET_ALL}"
            )

        print(
            f"\n{Fore.CYAN}💡 Learning Tip: Job statuses indicate the overall progress of your OTA deployment.{Style.RESET_ALL}"
        )
        print(f"{Fore.CYAN}   IN_PROGRESS jobs are actively deploying to devices.{Style.RESET_ALL}")

    def get_available_job_ids(self):
        """Get list of available job IDs"""
        statuses = ["IN_PROGRESS", "COMPLETED", "CANCELED", "DELETION_IN_PROGRESS", "SCHEDULED"]
        all_job_ids = []

        for status in statuses:
            response = self.safe_api_call(
                self.iot_client.list_jobs, "Jobs List", f"{status} jobs", debug=False, status=status, maxResults=250
            )

            if response:
                jobs = response.get("jobs", [])
                job_ids = [job.get("jobId") for job in jobs if job.get("jobId")]
                all_job_ids.extend(job_ids)

        return list(set(all_job_ids))  # Remove duplicates

    def explore_specific_job(self):
        """Explore a specific job by ID"""
        # Get available jobs first for selection
        available_jobs = self.get_available_job_ids()

        if available_jobs:
            print(f"\n{Fore.YELLOW}📝 Available Job IDs:{Style.RESET_ALL}")
            for i, job_id in enumerate(available_jobs, 1):
                print(f"{Fore.CYAN}{i}. {job_id}{Style.RESET_ALL}")

            print(f"\n{Fore.CYAN}Options:{Style.RESET_ALL}")
            print(f"{Fore.CYAN}1. Select from list above (enter number){Style.RESET_ALL}")  # nosec B608
            print(f"{Fore.CYAN}2. Enter custom Job ID{Style.RESET_ALL}")

            choice = input(f"{Fore.YELLOW}Choose option [1-2]: {Style.RESET_ALL}").strip()

            if choice == "1":
                try:
                    job_index = (
                        int(input(f"{Fore.YELLOW}Select job [1-{len(available_jobs)}]: {Style.RESET_ALL}")) - 1
                    )  # nosec B608
                    if 0 <= job_index < len(available_jobs):
                        job_id = available_jobs[job_index]
                    else:
                        print(f"{Fore.RED}❌ Invalid selection{Style.RESET_ALL}")
                        return
                except ValueError:
                    print(f"{Fore.RED}❌ Please enter a valid number{Style.RESET_ALL}")
                    return
            else:
                job_id = input(f"{Fore.YELLOW}📝 Enter Job ID: {Style.RESET_ALL}").strip()
        else:
            job_id = input(f"{Fore.YELLOW}📝 Enter Job ID to explore: {Style.RESET_ALL}").strip()

        if not job_id:
            print(f"{Fore.RED}❌ Job ID is required{Style.RESET_ALL}")
            return

        print(f"\n{Fore.BLUE}🔍 Getting detailed information for job: {Fore.YELLOW}{job_id}{Style.RESET_ALL}")

        # Get job details
        job_response = self.safe_api_call(
            self.iot_client.describe_job, "Job Detail", job_id, debug=self.debug_mode, jobId=job_id
        )

        if not job_response:
            print(f"{Fore.RED}❌ Failed to get job details. Job might not exist.{Style.RESET_ALL}")
            return

        job = job_response.get("job", {})

        print(f"\n{Fore.GREEN}📋 Job Details:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}🆔 Job ID: {Fore.WHITE}{job.get('jobId', 'N/A')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}📊 Status: {Fore.WHITE}{job.get('status', 'N/A')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}📝 Description: {Fore.WHITE}{job.get('description', 'N/A')}{Style.RESET_ALL}")
        print(
            f"{Fore.CYAN}🎯 Target Selection: {Fore.WHITE}{job.get('targetSelection', 'N/A')}{Style.RESET_ALL}"
        )  # nosec B608
        print(f"{Fore.CYAN}📅 Created: {Fore.WHITE}{job.get('createdAt', 'N/A')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}✅ Completed: {Fore.WHITE}{job.get('completedAt', 'N/A')}{Style.RESET_ALL}")

        # Show targets
        targets = job.get("targets", [])
        if targets:
            print(f"\n{Fore.GREEN}🎯 Job Targets ({len(targets)}):{Style.RESET_ALL}")
            for target in targets:
                # Extract thing group name from ARN
                target_name = target.split("/")[-1] if "/" in target else target
                print(f"{Fore.CYAN}  • {target_name}{Style.RESET_ALL}")

        # Show job document
        job_document = job.get("jobDocument")
        if job_document:
            print(f"\n{Fore.GREEN}📄 Job Document:{Style.RESET_ALL}")
            if isinstance(job_document, str):
                try:
                    job_doc = json.loads(job_document)
                    self.format_job_document(job_doc)
                except json.JSONDecodeError:
                    print(job_document)
            else:
                self.format_job_document(job_document)

        # Show job execution configuration
        job_executions_config = job.get("jobExecutionsRolloutConfig", {})
        if job_executions_config:
            print(f"\n{Fore.GREEN}⚙️  Job Execution Configuration:{Style.RESET_ALL}")
            print(json.dumps(job_executions_config, indent=2))

        # Show presigned URL config
        presigned_config = job.get("presignedUrlConfig", {})
        if presigned_config:
            print(f"\n{Fore.GREEN}🔗 Presigned URL Configuration:{Style.RESET_ALL}")
            print(f"{Fore.CYAN}🔐 Role ARN: {Fore.WHITE}{presigned_config.get('roleArn', 'N/A')}{Style.RESET_ALL}")
            print(
                f"{Fore.CYAN}⏰ Expires In: {Fore.WHITE}{presigned_config.get('expiresInSec', 'N/A')} seconds{Style.RESET_ALL}"
            )

        print(f"\n{Fore.CYAN}💡 Learning Tip: The job document contains the instructions sent to devices.{Style.RESET_ALL}")
        print(f"{Fore.CYAN}   Presigned URLs allow secure S3 access without device credentials.{Style.RESET_ALL}")

    def explore_job_execution(self):
        """Explore a specific job execution by device and job ID"""
        # Get available jobs first for selection
        available_jobs = self.get_available_job_ids()

        if available_jobs:
            print(f"\n{Fore.YELLOW}📝 Available Job IDs:{Style.RESET_ALL}")
            for i, job_id in enumerate(available_jobs, 1):
                print(f"{Fore.CYAN}{i}. {job_id}{Style.RESET_ALL}")

            print(f"\n{Fore.CYAN}Options:{Style.RESET_ALL}")
            print(f"{Fore.CYAN}1. Select from list above (enter number){Style.RESET_ALL}")  # nosec B608
            print(f"{Fore.CYAN}2. Enter custom Job ID{Style.RESET_ALL}")

            choice = input(f"{Fore.YELLOW}Choose option [1-2]: {Style.RESET_ALL}").strip()

            if choice == "1":
                try:
                    job_index = (
                        int(input(f"{Fore.YELLOW}Select job [1-{len(available_jobs)}]: {Style.RESET_ALL}")) - 1
                    )  # nosec B608
                    if 0 <= job_index < len(available_jobs):
                        job_id = available_jobs[job_index]
                    else:
                        print(f"{Fore.RED}❌ Invalid selection{Style.RESET_ALL}")
                        return
                except ValueError:
                    print(f"{Fore.RED}❌ Please enter a valid number{Style.RESET_ALL}")
                    return
            else:
                job_id = input(f"{Fore.YELLOW}📝 Enter Job ID: {Style.RESET_ALL}").strip()
        else:
            job_id = input(f"{Fore.YELLOW}📝 Enter Job ID: {Style.RESET_ALL}").strip()

        if not job_id:
            print(f"{Fore.RED}❌ Job ID is required{Style.RESET_ALL}")
            return

        thing_name = input(f"{Fore.YELLOW}Enter Device/Thing Name: {Style.RESET_ALL}").strip()

        if not job_id or not thing_name:
            print(f"{Fore.RED}❌ Both Job ID and Thing Name are required{Style.RESET_ALL}")
            return

        print(f"\n{Fore.BLUE}🔍 Getting job execution details for device: {Fore.YELLOW}{thing_name}{Style.RESET_ALL}")
        print(f"{Fore.BLUE}   Job: {Fore.YELLOW}{job_id}{Style.RESET_ALL}")

        # Get job execution details using IoT Jobs Data endpoint
        execution_response = self.safe_api_call(
            self.iot_jobs_data_client.describe_job_execution,
            "Job Execution Detail",
            f"{job_id} on {thing_name}",
            debug=self.debug_mode,
            jobId=job_id,
            thingName=thing_name,
            includeJobDocument=True,
        )

        if not execution_response:
            print(f"{Fore.RED}❌ Failed to get job execution details. Check job ID and thing name.{Style.RESET_ALL}")
            return

        execution = execution_response.get("execution", {})

        print(f"\n{Fore.GREEN}📋 Job Execution Details:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}🆔 Job ID: {Fore.WHITE}{execution.get('jobId', 'N/A')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}📱 Thing Name: {Fore.WHITE}{execution.get('thingName', 'N/A')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}📊 Status: {Fore.WHITE}{execution.get('status', 'N/A')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}🔢 Execution Number: {Fore.WHITE}{execution.get('executionNumber', 'N/A')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}📅 Queued At: {Fore.WHITE}{execution.get('queuedAt', 'N/A')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}🚀 Started At: {Fore.WHITE}{execution.get('startedAt', 'N/A')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}✅ Last Updated: {Fore.WHITE}{execution.get('lastUpdatedAt', 'N/A')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}📈 Version Number: {Fore.WHITE}{execution.get('versionNumber', 'N/A')}{Style.RESET_ALL}")

        # Show status details if available
        status_details = execution.get("statusDetails")
        if status_details:
            print(f"\n{Fore.GREEN}📊 Status Details:{Style.RESET_ALL}")
            if isinstance(status_details, dict):
                for key, value in status_details.items():
                    print(f"{Fore.CYAN}  {key}: {Fore.WHITE}{value}{Style.RESET_ALL}")
            else:
                print(f"{Fore.WHITE}{status_details}{Style.RESET_ALL}")

        # Show job document
        job_document = execution.get("jobDocument")
        if job_document:
            print(f"\n{Fore.GREEN}📄 Job Document for this Execution:{Style.RESET_ALL}")
            self.format_job_document(job_document)

        print(f"\n{Fore.CYAN}💡 Learning Tip: Job executions track individual device progress.{Style.RESET_ALL}")
        print(f"{Fore.CYAN}   Status details contain device-reported information about success/failure.{Style.RESET_ALL}")

    def get_job_executions_by_status_parallel(self, job_id, status):
        """Get job executions by status in parallel"""
        with self.api_semaphore:
            response = self.safe_api_call(
                self.iot_client.list_job_executions_for_job,
                "Job Executions List",
                f"{job_id} {status}",
                debug=False,
                jobId=job_id,
                status=status,
                maxResults=250,
            )

            if response:
                executions = response.get("executionSummaries", [])
                return [(execution, status) for execution in executions]
            return []

    def list_job_executions(self):
        """List job executions for a specific job"""
        # Get available jobs first for selection
        available_jobs = self.get_available_job_ids()

        if available_jobs:
            print(f"\n{Fore.YELLOW}📝 Available Job IDs:{Style.RESET_ALL}")
            for i, job_id in enumerate(available_jobs, 1):
                print(f"{Fore.CYAN}{i}. {job_id}{Style.RESET_ALL}")

            print(f"\n{Fore.CYAN}Options:{Style.RESET_ALL}")
            print(f"{Fore.CYAN}1. Select from list above (enter number){Style.RESET_ALL}")  # nosec B608
            print(f"{Fore.CYAN}2. Enter custom Job ID{Style.RESET_ALL}")

            choice = input(f"{Fore.YELLOW}Choose option [1-2]: {Style.RESET_ALL}").strip()

            if choice == "1":
                try:
                    job_index = (
                        int(input(f"{Fore.YELLOW}Select job [1-{len(available_jobs)}]: {Style.RESET_ALL}")) - 1
                    )  # nosec B608
                    if 0 <= job_index < len(available_jobs):
                        job_id = available_jobs[job_index]
                    else:
                        print(f"{Fore.RED}❌ Invalid selection{Style.RESET_ALL}")
                        return
                except ValueError:
                    print(f"{Fore.RED}❌ Please enter a valid number{Style.RESET_ALL}")
                    return
            else:
                job_id = input(f"{Fore.YELLOW}📝 Enter Job ID: {Style.RESET_ALL}").strip()
        else:
            job_id = input(f"{Fore.YELLOW}📝 Enter Job ID to explore executions: {Style.RESET_ALL}").strip()

        if not job_id:
            print(f"{Fore.RED}❌ Job ID is required{Style.RESET_ALL}")
            return

        print(f"\n{Fore.BLUE}🔍 Getting job executions for job: {Fore.YELLOW}{job_id}{Style.RESET_ALL}")

        # Get executions for different statuses
        statuses = ["QUEUED", "IN_PROGRESS", "SUCCEEDED", "FAILED", "TIMED_OUT", "REJECTED", "REMOVED", "CANCELED"]
        all_executions = []

        if self.debug_mode:
            print(f"{Fore.BLUE}🔧 Checking execution statuses sequentially (debug mode)...{Style.RESET_ALL}")
            for status in statuses:
                print(f"{Fore.CYAN}📊 Checking {status} executions...{Style.RESET_ALL}")
                executions_with_status = self.get_job_executions_by_status_parallel(job_id, status)
                if executions_with_status:
                    all_executions.extend(executions_with_status)
                    print(f"{Fore.GREEN}  ✅ Found {len(executions_with_status)} {status} executions{Style.RESET_ALL}")
                else:
                    print(f"{Fore.YELLOW}  ℹ️  No {status} executions found{Style.RESET_ALL}")
        else:
            print(f"{Fore.BLUE}🔧 Checking execution statuses in parallel...{Style.RESET_ALL}")
            with ThreadPoolExecutor(max_workers=8) as executor:
                futures = [executor.submit(self.get_job_executions_by_status_parallel, job_id, status) for status in statuses]

                for future in as_completed(futures):
                    executions_with_status = future.result()
                    if executions_with_status:
                        status = executions_with_status[0][1]
                        print(f"{Fore.GREEN}  ✅ Found {len(executions_with_status)} {status} executions{Style.RESET_ALL}")
                        all_executions.extend(executions_with_status)

        if not all_executions:
            print(f"{Fore.YELLOW}ℹ️  No job executions found for job: {job_id}{Style.RESET_ALL}")
            return

        print(f"\n{Fore.GREEN}📋 Found {len(all_executions)} total job executions:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'Thing Name':<25} {'Status':<12} {'Execution #':<12} {'Queued At':<20}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'-' * 75}{Style.RESET_ALL}")

        for execution, status in all_executions:
            # Extract thing name from ARN
            thing_arn = execution.get("thingArn", "")
            thing_name = thing_arn.split("/")[-1] if "/" in thing_arn else "N/A"
            thing_name = thing_name[:24]  # Truncate for display

            # Get execution details from jobExecutionSummary
            job_exec_summary = execution.get("jobExecutionSummary", {})
            exec_num = str(job_exec_summary.get("executionNumber", "N/A"))
            queued_at = str(job_exec_summary.get("queuedAt", "N/A"))[:19] if job_exec_summary.get("queuedAt") else "N/A"

            # Color code by status
            if status == "SUCCEEDED":
                status_color = Fore.GREEN
            elif status in ["IN_PROGRESS", "QUEUED"]:
                status_color = Fore.BLUE
            elif status in ["FAILED", "TIMED_OUT", "REJECTED"]:
                status_color = Fore.RED
            else:
                status_color = Fore.YELLOW

            print(
                f"{Fore.WHITE}{thing_name:<25} {status_color}{status:<12}{Style.RESET_ALL} {Fore.CYAN}{exec_num:<12} {queued_at:<20}{Style.RESET_ALL}"
            )

        # Show summary statistics
        status_counts = {}
        for _, status in all_executions:
            status_counts[status] = status_counts.get(status, 0) + 1

        print(f"\n{Fore.GREEN}📊 Execution Summary:{Style.RESET_ALL}")
        for status, count in status_counts.items():
            if status == "SUCCEEDED":
                color = Fore.GREEN
            elif status in ["IN_PROGRESS", "QUEUED"]:
                color = Fore.BLUE
            elif status in ["FAILED", "TIMED_OUT", "REJECTED"]:
                color = Fore.RED
            else:
                color = Fore.YELLOW

            print(f"{color}  {status}: {count}{Style.RESET_ALL}")

        print(
            f"\n{Fore.CYAN}💡 Learning Tip: Job execution status shows how your OTA deployment is progressing.{Style.RESET_ALL}"
        )
        print(f"{Fore.CYAN}   SUCCEEDED means the device successfully completed the update.{Style.RESET_ALL}")

    def run(self):
        """Main execution flow with menu loop"""
        self.print_header()

        # Get debug mode preference
        self.get_debug_mode()

        while True:
            # Get exploration choice
            choice = self.get_exploration_choice()

            print(f"\n{Fore.BLUE}🚀 Starting exploration...{Style.RESET_ALL}\n")

            if choice == 1:
                self.list_all_jobs()
            elif choice == 2:
                self.explore_specific_job()
            elif choice == 3:
                self.explore_job_execution()
            elif choice == 4:
                self.list_job_executions()

            print(f"\n{Fore.GREEN}🎉 Exploration completed!{Style.RESET_ALL}")
            print(
                f"{Fore.CYAN}💡 Use this information to understand your IoT deployment status and troubleshoot issues.{Style.RESET_ALL}"
            )

            # Ask if user wants to continue
            continue_choice = input(f"\n{Fore.YELLOW}Would you like to explore more? [Y/n]: {Style.RESET_ALL}").strip().lower()
            if continue_choice in ["n", "no"]:
                print(f"\n{Fore.GREEN}👋 Thank you for exploring AWS IoT Jobs!{Style.RESET_ALL}")
                break

            print()  # Add spacing for next iteration


if __name__ == "__main__":
    explorer = IoTJobsExplorer()
    try:
        explorer.run()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}👋 Job exploration cancelled by user. Goodbye!{Style.RESET_ALL}")
        sys.exit(0)
