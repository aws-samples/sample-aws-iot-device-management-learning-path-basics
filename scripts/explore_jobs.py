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

# Add i18n to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "i18n"))

from language_selector import get_language
from loader import load_messages

# Initialize colorama
init()

# Global variables for i18n
USER_LANG = "en"
messages = {}


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

    def get_message(self, key, *args):
        """Get localized message with optional formatting"""
        global messages
        
        # Handle nested keys like 'warnings.debug_warning'
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

    def format_job_document(self, job_doc):
        """Format job document as properly indented JSON"""
        if not job_doc:
            print(f"{Fore.YELLOW}  {self.get_message('ui.no_job_document')}{Style.RESET_ALL}")
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
                    print(self.get_message('debug.resource_not_found', resource_name))
                return None
            else:
                print(self.get_message('errors.api_error', operation_name, resource_name, e.response['Error']['Message']))
                if debug or self.debug_mode:
                    print(self.get_message('debug.full_error'))
                    print(json.dumps(e.response, indent=2, default=str))
            time.sleep(0.1)  # nosemgrep: arbitrary-sleep
            return None
        except Exception as e:
            print(self.get_message('errors.general_error', str(e)))
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

            # Get IoT Jobs endpoint
            endpoint_response = self.iot_client.describe_endpoint(endpointType="iot:Jobs")
            self.jobs_endpoint = endpoint_response["endpointAddress"]

            # Initialize IoT Jobs Data client with endpoint
            self.iot_jobs_data_client = boto3.client(
                "iot-jobs-data", region_name=self.region, endpoint_url=f"https://{self.jobs_endpoint}"
            )

            if self.debug_mode:
                print(self.get_message('status.clients_initialized'))
                print(self.get_message('status.iot_service', self.iot_client.meta.service_model.service_name))
                print(self.get_message('status.jobs_endpoint', self.jobs_endpoint))

            return True
        except Exception as e:
            print(self.get_message('errors.client_init_error', str(e)))
            return False

    def print_header(self):
        print(f"{Fore.CYAN}{self.get_message('title')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('separator')}{Style.RESET_ALL}\n")

        print(f"{Fore.YELLOW}{self.get_message('learning_goal')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('learning_description')}{Style.RESET_ALL}\n")

        # Initialize clients and display info
        if not self.initialize_clients():
            sys.exit(1)

        print(f"{Fore.CYAN}{self.get_message('region_label')} {Fore.GREEN}{self.region}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('account_id_label')} {Fore.GREEN}{self.account_id}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('jobs_endpoint_label')} {Fore.GREEN}{self.jobs_endpoint}{Style.RESET_ALL}\n")

    def get_debug_mode(self):
        """Ask user for debug mode"""
        print(f"{Fore.RED}{self.get_message('warnings.debug_warning')}{Style.RESET_ALL}")
        choice = (
            input(f"{Fore.YELLOW}{self.get_message('prompts.debug_mode')}{Style.RESET_ALL}")
            .strip()
            .lower()
        )
        self.debug_mode = choice in ["y", "yes"]

        if self.debug_mode:
            print(f"{Fore.GREEN}{self.get_message('status.debug_enabled')}{Style.RESET_ALL}\n")

    def get_exploration_choice(self):
        """Get exploration option from user"""
        print(f"{Fore.YELLOW}{self.get_message('ui.exploration_menu')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('ui.list_all_jobs')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('ui.explore_specific_job')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('ui.explore_job_execution')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('ui.list_job_executions')}{Style.RESET_ALL}")

        while True:
            try:
                choice = int(input(f"{Fore.YELLOW}{self.get_message('prompts.exploration_choice')}{Style.RESET_ALL}"))
                if 1 <= choice <= 4:
                    return choice
                print(f"{Fore.RED}{self.get_message('errors.invalid_choice')}{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED}{self.get_message('errors.invalid_number')}{Style.RESET_ALL}")

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
        print(f"{Fore.BLUE}{self.get_message('status.scanning_jobs')}{Style.RESET_ALL}")

        statuses = ["IN_PROGRESS", "COMPLETED", "CANCELED", "DELETION_IN_PROGRESS", "SCHEDULED"]
        all_jobs = []

        if self.debug_mode:
            print(f"{Fore.BLUE}{self.get_message('status.checking_sequential')}{Style.RESET_ALL}")
            for status in statuses:
                print(f"{Fore.CYAN}{self.get_message('status.checking_status', status)}{Style.RESET_ALL}")
                jobs_with_status = self.get_jobs_by_status_parallel(status)
                if jobs_with_status:
                    all_jobs.extend(jobs_with_status)
                    print(f"{Fore.GREEN}{self.get_message('status.found_jobs', len(jobs_with_status), status)}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.YELLOW}{self.get_message('status.no_jobs_status', status)}{Style.RESET_ALL}")
        else:
            print(f"{Fore.BLUE}{self.get_message('status.checking_parallel')}{Style.RESET_ALL}")
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(self.get_jobs_by_status_parallel, status) for status in statuses]

                for future in as_completed(futures):
                    jobs_with_status = future.result()
                    if jobs_with_status:
                        status = jobs_with_status[0][1]
                        print(f"{Fore.GREEN}{self.get_message('status.found_jobs', len(jobs_with_status), status)}{Style.RESET_ALL}")
                        all_jobs.extend(jobs_with_status)

        if not all_jobs:
            print(f"{Fore.YELLOW}{self.get_message('results.no_jobs_found')}{Style.RESET_ALL}")
            return

        print(f"\n{Fore.GREEN}{self.get_message('results.found_total_jobs', len(all_jobs))}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('ui.table_headers.jobs')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('ui.table_headers.separator')}{Style.RESET_ALL}")

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

        print(f"\n{Fore.CYAN}{self.get_message('learning.job_status_tip')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('learning.in_progress_tip')}{Style.RESET_ALL}")

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
            print(f"\n{Fore.YELLOW}{self.get_message('ui.available_job_ids')}{Style.RESET_ALL}")
            for i, job_id in enumerate(available_jobs, 1):
                print(f"{Fore.CYAN}{i}. {job_id}{Style.RESET_ALL}")

            print(f"\n{Fore.CYAN}{self.get_message('ui.options_label')}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{self.get_message('ui.select_from_list')}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{self.get_message('ui.enter_custom')}{Style.RESET_ALL}")

            choice = input(f"{Fore.YELLOW}{self.get_message('prompts.choose_option')}{Style.RESET_ALL}").strip()

            if choice == "1":
                try:
                    job_index = (
                        int(input(f"{Fore.YELLOW}{self.get_message('prompts.select_job', len(available_jobs))}{Style.RESET_ALL}")) - 1
                    )
                    if 0 <= job_index < len(available_jobs):
                        job_id = available_jobs[job_index]
                    else:
                        print(f"{Fore.RED}{self.get_message('errors.invalid_selection')}{Style.RESET_ALL}")
                        return
                except ValueError:
                    print(f"{Fore.RED}{self.get_message('errors.invalid_number')}{Style.RESET_ALL}")
                    return
            else:
                job_id = input(f"{Fore.YELLOW}{self.get_message('prompts.enter_job_id')}{Style.RESET_ALL}").strip()
        else:
            job_id = input(f"{Fore.YELLOW}{self.get_message('prompts.enter_job_id_explore')}{Style.RESET_ALL}").strip()

        if not job_id:
            print(f"{Fore.RED}{self.get_message('errors.job_id_required')}{Style.RESET_ALL}")
            return

        print(f"\n{Fore.BLUE}{self.get_message('status.getting_job_details', job_id)}{Style.RESET_ALL}")

        # Get job details
        job_response = self.safe_api_call(
            self.iot_client.describe_job, "Job Detail", job_id, debug=self.debug_mode, jobId=job_id
        )

        if not job_response:
            print(f"{Fore.RED}{self.get_message('errors.failed_job_details')}{Style.RESET_ALL}")
            return

        job = job_response.get("job", {})

        print(f"\n{Fore.GREEN}{self.get_message('ui.job_details')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('ui.job_id_label', job.get('jobId', self.get_message('results.na')))}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('ui.status_label', job.get('status', self.get_message('results.na')))}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('ui.description_label', job.get('description', self.get_message('results.na')))}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('ui.target_selection_label', job.get('targetSelection', self.get_message('results.na')))}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('ui.created_label', job.get('createdAt', self.get_message('results.na')))}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('ui.completed_label', job.get('completedAt', self.get_message('results.na')))}{Style.RESET_ALL}")

        # Show targets
        targets = job.get("targets", [])
        if targets:
            print(f"\n{Fore.GREEN}{self.get_message('ui.job_targets', len(targets))}{Style.RESET_ALL}")
            for target in targets:
                # Extract thing group name from ARN
                target_name = target.split("/")[-1] if "/" in target else target
                print(f"{Fore.CYAN}{self.get_message('ui.target_item', target_name)}{Style.RESET_ALL}")

        # Show job document
        job_document = job.get("jobDocument")
        if job_document:
            print(f"\n{Fore.GREEN}{self.get_message('ui.job_document')}{Style.RESET_ALL}")
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
            print(f"\n{Fore.GREEN}{self.get_message('ui.job_execution_config')}{Style.RESET_ALL}")
            print(json.dumps(job_executions_config, indent=2))

        # Show presigned URL config
        presigned_config = job.get("presignedUrlConfig", {})
        if presigned_config:
            print(f"\n{Fore.GREEN}{self.get_message('ui.presigned_url_config')}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{self.get_message('ui.role_arn', presigned_config.get('roleArn', self.get_message('results.na')))}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{self.get_message('ui.expires_in', presigned_config.get('expiresInSec', self.get_message('results.na')))}{Style.RESET_ALL}")

        print(f"\n{Fore.CYAN}{self.get_message('learning.job_document_tip')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('learning.presigned_url_tip')}{Style.RESET_ALL}")

    def explore_job_execution(self):
        """Explore a specific job execution by device and job ID"""
        # Get available jobs first for selection
        available_jobs = self.get_available_job_ids()

        if available_jobs:
            print(f"\n{Fore.YELLOW}{self.get_message('ui.available_job_ids')}{Style.RESET_ALL}")
            for i, job_id in enumerate(available_jobs, 1):
                print(f"{Fore.CYAN}{i}. {job_id}{Style.RESET_ALL}")

            print(f"\n{Fore.CYAN}{self.get_message('ui.options_label')}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{self.get_message('ui.select_from_list')}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{self.get_message('ui.enter_custom')}{Style.RESET_ALL}")

            choice = input(f"{Fore.YELLOW}{self.get_message('prompts.choose_option')}{Style.RESET_ALL}").strip()

            if choice == "1":
                try:
                    job_index = (
                        int(input(f"{Fore.YELLOW}{self.get_message('prompts.select_job', len(available_jobs))}{Style.RESET_ALL}")) - 1
                    )
                    if 0 <= job_index < len(available_jobs):
                        job_id = available_jobs[job_index]
                    else:
                        print(f"{Fore.RED}{self.get_message('errors.invalid_selection')}{Style.RESET_ALL}")
                        return
                except ValueError:
                    print(f"{Fore.RED}{self.get_message('errors.invalid_number')}{Style.RESET_ALL}")
                    return
            else:
                job_id = input(f"{Fore.YELLOW}{self.get_message('prompts.enter_job_id')}{Style.RESET_ALL}").strip()
        else:
            job_id = input(f"{Fore.YELLOW}{self.get_message('prompts.enter_job_id')}{Style.RESET_ALL}").strip()

        if not job_id:
            print(f"{Fore.RED}{self.get_message('errors.job_id_required')}{Style.RESET_ALL}")
            return

        thing_name = input(f"{Fore.YELLOW}{self.get_message('prompts.enter_thing_name')}{Style.RESET_ALL}").strip()

        if not job_id or not thing_name:
            print(f"{Fore.RED}{self.get_message('errors.both_required')}{Style.RESET_ALL}")
            return

        print(f"\n{Fore.BLUE}{self.get_message('status.getting_execution_details', thing_name)}{Style.RESET_ALL}")
        print(f"{Fore.BLUE}{self.get_message('status.job_label', job_id)}{Style.RESET_ALL}")

        # Get job execution details using IoT API (works for all job statuses)
        execution_response = self.safe_api_call(
            self.iot_client.describe_job_execution,
            "Job Execution Detail",
            f"{job_id} on {thing_name}",
            debug=self.debug_mode,
            jobId=job_id,
            thingName=thing_name,
        )

        if not execution_response:
            print(f"{Fore.RED}{self.get_message('errors.failed_execution_details')}{Style.RESET_ALL}")
            return

        execution = execution_response.get("execution", {})

        print(f"\n{Fore.GREEN}{self.get_message('ui.job_execution_details')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('ui.job_id_label', execution.get('jobId', self.get_message('results.na')))}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('ui.thing_name_label', execution.get('thingName', self.get_message('results.na')))}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('ui.status_label', execution.get('status', self.get_message('results.na')))}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('ui.execution_number', execution.get('executionNumber', self.get_message('results.na')))}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('ui.queued_at', execution.get('queuedAt', self.get_message('results.na')))}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('ui.started_at', execution.get('startedAt', self.get_message('results.na')))}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('ui.last_updated', execution.get('lastUpdatedAt', self.get_message('results.na')))}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('ui.version_number', execution.get('versionNumber', self.get_message('results.na')))}{Style.RESET_ALL}")

        # Show status details if available
        status_details = execution.get("statusDetails")
        if status_details:
            print(f"\n{Fore.GREEN}{self.get_message('ui.status_details')}{Style.RESET_ALL}")
            if isinstance(status_details, dict):
                for key, value in status_details.items():
                    print(f"{Fore.CYAN}  {key}: {Fore.WHITE}{value}{Style.RESET_ALL}")
            else:
                print(f"{Fore.WHITE}{status_details}{Style.RESET_ALL}")

        # Show job document (try to get from execution first, then from job details)
        job_document = execution.get("jobDocument")
        if not job_document:
            # If job document not in execution, try to get it from job details
            job_response = self.safe_api_call(
                self.iot_client.describe_job, "Job Detail", job_id, debug=False, jobId=job_id
            )
            if job_response:
                job = job_response.get("job", {})
                job_document = job.get("jobDocument")
        
        if job_document:
            print(f"\n{Fore.GREEN}{self.get_message('ui.job_document_execution')}{Style.RESET_ALL}")
            self.format_job_document(job_document)
        else:
            print(f"\n{Fore.YELLOW}{self.get_message('ui.no_job_document')}{Style.RESET_ALL}")

        print(f"\n{Fore.CYAN}{self.get_message('learning.execution_status_tip')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('learning.status_details_tip')}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{self.get_message('learning.api_access_note')}{Style.RESET_ALL}")

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
            print(f"\n{Fore.YELLOW}{self.get_message('ui.available_job_ids')}{Style.RESET_ALL}")
            for i, job_id in enumerate(available_jobs, 1):
                print(f"{Fore.CYAN}{i}. {job_id}{Style.RESET_ALL}")

            print(f"\n{Fore.CYAN}{self.get_message('ui.options_label')}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{self.get_message('ui.select_from_list')}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{self.get_message('ui.enter_custom')}{Style.RESET_ALL}")

            choice = input(f"{Fore.YELLOW}{self.get_message('prompts.choose_option')}{Style.RESET_ALL}").strip()

            if choice == "1":
                try:
                    job_index = (
                        int(input(f"{Fore.YELLOW}{self.get_message('prompts.select_job', len(available_jobs))}{Style.RESET_ALL}")) - 1
                    )
                    if 0 <= job_index < len(available_jobs):
                        job_id = available_jobs[job_index]
                    else:
                        print(f"{Fore.RED}{self.get_message('errors.invalid_selection')}{Style.RESET_ALL}")
                        return
                except ValueError:
                    print(f"{Fore.RED}{self.get_message('errors.invalid_number')}{Style.RESET_ALL}")
                    return
            else:
                job_id = input(f"{Fore.YELLOW}{self.get_message('prompts.enter_job_id')}{Style.RESET_ALL}").strip()
        else:
            job_id = input(f"{Fore.YELLOW}{self.get_message('prompts.enter_job_id_executions')}{Style.RESET_ALL}").strip()

        if not job_id:
            print(f"{Fore.RED}{self.get_message('errors.job_id_required')}{Style.RESET_ALL}")
            return

        print(f"\n{Fore.BLUE}{self.get_message('status.getting_executions', job_id)}{Style.RESET_ALL}")

        # Get executions for different statuses
        statuses = ["QUEUED", "IN_PROGRESS", "SUCCEEDED", "FAILED", "TIMED_OUT", "REJECTED", "REMOVED", "CANCELED"]
        all_executions = []

        if self.debug_mode:
            print(f"{Fore.BLUE}{self.get_message('status.checking_execution_sequential')}{Style.RESET_ALL}")
            for status in statuses:
                print(f"{Fore.CYAN}{self.get_message('status.checking_execution_status', status)}{Style.RESET_ALL}")
                executions_with_status = self.get_job_executions_by_status_parallel(job_id, status)
                if executions_with_status:
                    all_executions.extend(executions_with_status)
                    print(f"{Fore.GREEN}{self.get_message('status.found_executions', len(executions_with_status), status)}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.YELLOW}{self.get_message('status.no_executions_status', status)}{Style.RESET_ALL}")
        else:
            print(f"{Fore.BLUE}{self.get_message('status.checking_execution_statuses')}{Style.RESET_ALL}")
            with ThreadPoolExecutor(max_workers=8) as executor:
                futures = [executor.submit(self.get_job_executions_by_status_parallel, job_id, status) for status in statuses]

                for future in as_completed(futures):
                    executions_with_status = future.result()
                    if executions_with_status:
                        status = executions_with_status[0][1]
                        print(f"{Fore.GREEN}{self.get_message('status.found_executions', len(executions_with_status), status)}{Style.RESET_ALL}")
                        all_executions.extend(executions_with_status)

        if not all_executions:
            print(f"{Fore.YELLOW}{self.get_message('results.no_executions_found', job_id)}{Style.RESET_ALL}")
            return

        print(f"\n{Fore.GREEN}{self.get_message('results.found_total_executions', len(all_executions))}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('ui.table_headers.executions')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('ui.table_headers.executions_separator')}{Style.RESET_ALL}")

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

        print(f"\n{Fore.GREEN}{self.get_message('ui.execution_summary')}{Style.RESET_ALL}")
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

        print(f"\n{Fore.CYAN}{self.get_message('learning.execution_progress_tip')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('learning.succeeded_tip')}{Style.RESET_ALL}")

    def run(self):
        """Main execution flow with menu loop"""
        self.print_header()

        # Get debug mode preference
        self.get_debug_mode()

        while True:
            # Get exploration choice
            choice = self.get_exploration_choice()

            print(f"\n{Fore.BLUE}{self.get_message('status.starting_exploration')}{Style.RESET_ALL}\n")

            if choice == 1:
                self.list_all_jobs()
            elif choice == 2:
                self.explore_specific_job()
            elif choice == 3:
                self.explore_job_execution()
            elif choice == 4:
                self.list_job_executions()

            print(f"\n{Fore.GREEN}{self.get_message('status.exploration_completed')}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{self.get_message('status.exploration_info')}{Style.RESET_ALL}")

            # Ask if user wants to continue
            continue_choice = input(f"\n{Fore.YELLOW}{self.get_message('prompts.continue_exploration')}{Style.RESET_ALL}").strip().lower()
            if continue_choice in ["n", "no"]:
                print(f"\n{Fore.GREEN}{self.get_message('ui.goodbye')}{Style.RESET_ALL}")
                break

            print()  # Add spacing for next iteration


if __name__ == "__main__":
    # Initialize language
    USER_LANG = get_language()
    messages = load_messages("explore_jobs", USER_LANG)
    
    explorer = IoTJobsExplorer()
    try:
        explorer.run()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}{explorer.get_message('ui.cancelled')}{Style.RESET_ALL}")
        sys.exit(0)
