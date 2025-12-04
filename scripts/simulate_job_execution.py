#!/usr/bin/env python3

import json
import os
import re
import sys
import tempfile
import time
import warnings
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Semaphore

import boto3
import requests
from botocore.exceptions import ClientError
from colorama import Fore, Style, init

# Add i18n to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "i18n"))

from language_selector import get_language
from loader import load_messages

# Suppress urllib3 SSL warnings on macOS
warnings.filterwarnings("ignore", message="urllib3 v2 only supports OpenSSL 1.1.1+")

# Initialize colorama
init()

# Global variables for i18n
USER_LANG = "en"
messages = {}


class IoTJobSimulator:
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp(prefix="iot_job_artifacts_")
        self.region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        self.account_id = None
        self.verbose_mode = False
        self.debug_mode = False
        self.iot_client = None
        self.iot_jobs_data_client = None
        self.sts_client = None
        self.jobs_endpoint = None

        # Rate limiting semaphore for job execution updates (200 TPS limit)
        self.job_execution_semaphore = Semaphore(150)  # Use 150 for safety
        self.api_semaphore = Semaphore(10)

    def get_message(self, key, *args):
        """Get localized message with optional formatting"""
        # Handle nested keys like 'warnings.debug_warning'
        if "." in key:
            keys = key.split(".")
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
                print(self.get_message("debug.input_params"))
                print(json.dumps(kwargs, indent=2, default=str))

            response = func(**kwargs)

            if debug or self.debug_mode:
                print(self.get_message("debug.api_response"))
                print(json.dumps(response, indent=2, default=str))

            time.sleep(0.1)  # Rate limiting  # nosemgrep: arbitrary-sleep
            return response
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code in ["ResourceNotFoundException", "ResourceNotFound"]:
                if debug or self.debug_mode:
                    print(self.get_message("debug.resource_not_found", resource_name))
                return None
            else:
                print(self.get_message("errors.api_error", operation_name, resource_name, e.response["Error"]["Message"]))
                if debug or self.debug_mode:
                    print(self.get_message("debug.full_error"))
                    print(json.dumps(e.response, indent=2, default=str))
            time.sleep(0.1)  # nosemgrep: arbitrary-sleep
            return None
        except Exception as e:
            print(self.get_message("errors.general_error", str(e)))
            if debug or self.debug_mode:
                import traceback

                print(self.get_message("debug.full_traceback"))
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
                print(self.get_message("status.clients_initialized"))
                print(self.get_message("status.iot_service", self.iot_client.meta.service_model.service_name))
                print(self.get_message("status.jobs_endpoint", self.jobs_endpoint))

            return True
        except Exception as e:
            print(self.get_message("errors.client_init_error", str(e)))
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

    def get_verbose_mode(self):
        """Ask user for verbose mode"""
        choice = input(f"{Fore.YELLOW}{self.get_message('prompts.verbose_mode')}{Style.RESET_ALL}").strip().lower()
        self.verbose_mode = choice in ["y", "yes"]

        if self.verbose_mode:
            print(f"{Fore.GREEN}{self.get_message('status.verbose_enabled')}{Style.RESET_ALL}\n")

    def get_debug_mode(self):
        """Ask user for debug mode"""
        print(f"{Fore.RED}{self.get_message('warnings.debug_warning')}{Style.RESET_ALL}")
        choice = input(f"{Fore.YELLOW}{self.get_message('prompts.debug_mode')}{Style.RESET_ALL}").strip().lower()
        self.debug_mode = choice in ["y", "yes"]

        if self.debug_mode:
            print(f"{Fore.GREEN}{self.get_message('status.debug_enabled')}{Style.RESET_ALL}\n")

    def scan_active_jobs(self):
        """Scan for active IoT jobs"""
        print(f"{Fore.BLUE}{self.get_message('status.scanning_jobs')}{Style.RESET_ALL}")

        # Get IN_PROGRESS jobs only
        response = self.safe_api_call(
            self.iot_client.list_jobs,
            "Active Jobs List",
            "IN_PROGRESS jobs",
            debug=self.debug_mode,
            status="IN_PROGRESS",
            maxResults=250,
        )

        if response:
            jobs = response.get("jobs", [])
            job_ids = [job.get("jobId") for job in jobs if job.get("jobId")]

            print(f"{Fore.GREEN}{self.get_message('ui.active_jobs')}{Style.RESET_ALL}")
            if jobs:
                for job in jobs:
                    job_id = job.get("jobId", "N/A")
                    status = job.get("status", "N/A")
                    created_at = str(job.get("createdAt", "N/A"))[:19] if job.get("createdAt") else "N/A"
                    print(
                        f"{Fore.CYAN}• {job_id} - {status} {self.get_message('ui.created_date', created_at)}{Style.RESET_ALL}"
                    )
            else:
                print(f"{Fore.YELLOW}{self.get_message('ui.no_active_jobs')}{Style.RESET_ALL}")

            return job_ids
        else:
            print(f"{Fore.RED}{self.get_message('errors.failed_list_jobs')}{Style.RESET_ALL}")
            return []

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
                thing_names = []
                for execution in executions:
                    thing_arn = execution.get("thingArn", "")
                    thing_name = thing_arn.split("/")[-1] if "/" in thing_arn else None
                    if thing_name:
                        thing_names.append(thing_name)
                return thing_names
            return []

    def get_job_executions(self, job_id):
        """Get job executions for a specific job"""
        print(f"{Fore.BLUE}{self.get_message('status.getting_executions', job_id)}{Style.RESET_ALL}")

        statuses = ["QUEUED", "IN_PROGRESS"]
        all_thing_names = []

        if self.debug_mode:
            print(f"{Fore.BLUE}{self.get_message('status.checking_sequential')}{Style.RESET_ALL}")
            for status in statuses:
                print(f"{Fore.CYAN}{self.get_message('status.checking_status', status)}{Style.RESET_ALL}")
                thing_names = self.get_job_executions_by_status_parallel(job_id, status)
                if thing_names:
                    all_thing_names.extend(thing_names)
                    print(f"{Fore.GREEN}{self.get_message('ui.executions_found', status, len(thing_names))}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.YELLOW}{self.get_message('ui.no_executions', status)}{Style.RESET_ALL}")
        else:
            print(f"{Fore.BLUE}{self.get_message('status.checking_statuses')}{Style.RESET_ALL}")
            with ThreadPoolExecutor(max_workers=2) as executor:
                futures = [executor.submit(self.get_job_executions_by_status_parallel, job_id, status) for status in statuses]

                for future in as_completed(futures):
                    thing_names = future.result()
                    if thing_names:
                        all_thing_names.extend(thing_names)

        print(f"{Fore.CYAN}{self.get_message('status.total_executions', len(all_thing_names))}{Style.RESET_ALL}")
        return all_thing_names

    def has_presigned_url(self, job_document):
        """Check if job document contains S3 presigned URL"""
        try:
            # Handle both string and dict job documents
            if isinstance(job_document, str):
                job_doc = json.loads(job_document)
            else:
                job_doc = job_document

            # Check for OTA structure with presigned URLs
            packages = job_doc.get("ota", {}).get("packages", {})
            for package_name, package_info in packages.items():
                artifact = package_info.get("artifact", {})
                presigned_url = artifact.get("s3PresignedUrl")
                if presigned_url and presigned_url.strip():
                    return True

            return False
        except (json.JSONDecodeError, AttributeError):
            return False

    def download_artifact_from_job(self, job_document, job_id, thing_name, execution_number):
        """Download real artifact from S3 presigned URL"""
        print(f"{Fore.YELLOW}{self.get_message('status.downloading_firmware', thing_name)}{Style.RESET_ALL}")
        if self.verbose_mode or self.debug_mode:
            print(f"{Fore.YELLOW}{self.get_message('status.extracting_url')}{Style.RESET_ALL}")

        try:
            # Handle both string and dict job documents
            if isinstance(job_document, str):
                job_doc = json.loads(job_document)
            else:
                job_doc = job_document

            if self.debug_mode:
                print(f"{Fore.CYAN}{self.get_message('debug.job_document', json.dumps(job_doc, indent=2))}{Style.RESET_ALL}")

            # Extract s3PresignedUrl from job document
            packages = job_doc.get("ota", {}).get("packages", {})
            presigned_url = None

            for package_name, package_info in packages.items():
                artifact = package_info.get("artifact", {})
                presigned_url = artifact.get("s3PresignedUrl")
                if presigned_url:
                    if self.debug_mode:
                        print(f"{Fore.CYAN}{self.get_message('debug.found_package', package_name)}{Style.RESET_ALL}")
                    break

            if not presigned_url:
                if self.verbose_mode or self.debug_mode:
                    print(f"{Fore.RED}{self.get_message('errors.no_presigned_url')}{Style.RESET_ALL}")
                return False

            if self.verbose_mode or self.debug_mode:
                print(f"{Fore.GREEN}{self.get_message('status.found_url')}{Style.RESET_ALL}")
                if self.debug_mode:
                    print(f"{Fore.CYAN}{self.get_message('debug.presigned_url', presigned_url)}{Style.RESET_ALL}")

            # Create unique filename with sanitized components to prevent path traversal
            safe_thing_name = re.sub(r"[^a-zA-Z0-9_-]", "_", str(thing_name))
            safe_job_id = re.sub(r"[^a-zA-Z0-9_-]", "_", str(job_id))
            safe_execution_number = re.sub(r"[^a-zA-Z0-9_-]", "_", str(execution_number))
            filename = f"{safe_thing_name}_{safe_job_id}_v{safe_execution_number}.bin"
            artifact_file = os.path.join(self.temp_dir, os.path.basename(filename))

            # Download artifact from Amazon S3
            if self.verbose_mode or self.debug_mode:
                print(f"{Fore.BLUE}{self.get_message('status.downloading_artifact')}{Style.RESET_ALL}")

            if self.debug_mode:
                print(f"{Fore.CYAN}{self.get_message('debug.download_path', artifact_file)}{Style.RESET_ALL}")

            response = requests.get(presigned_url, stream=True, timeout=30)
            response.raise_for_status()

            if self.debug_mode:
                print(f"{Fore.CYAN}{self.get_message('debug.http_status', response.status_code)}{Style.RESET_ALL}")

            with open(artifact_file, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            if os.path.exists(artifact_file) and os.path.getsize(artifact_file) > 0:
                file_size = self.get_human_readable_size(os.path.getsize(artifact_file))
                print(f"{Fore.GREEN}{self.get_message('status.downloaded_firmware', thing_name, file_size)}{Style.RESET_ALL}")
                if self.verbose_mode or self.debug_mode:
                    # Sanitize basename to prevent path traversal
                    safe_basename = re.sub(r"[^a-zA-Z0-9._-]", "_", os.path.basename(os.path.normpath(artifact_file)))
                    print(
                        f"{Fore.GREEN}{self.get_message('status.artifact_downloaded', safe_basename, file_size)}{Style.RESET_ALL}"
                    )

                # Simulate processing time (reduced for parallel execution)
                time.sleep(0.1)  # Firmware processing simulation  # nosemgrep: arbitrary-sleep

                # Clean up artifact
                os.remove(artifact_file)
                if self.verbose_mode or self.debug_mode:
                    print(f"{Fore.YELLOW}{self.get_message('status.artifact_cleanup')}{Style.RESET_ALL}")
                return True
            else:
                if self.verbose_mode or self.debug_mode:
                    print(f"{Fore.RED}{self.get_message('errors.empty_file')}{Style.RESET_ALL}")
                if os.path.exists(artifact_file):
                    os.remove(artifact_file)
                return False

        except Exception as e:
            if self.verbose_mode or self.debug_mode:
                print(f"{Fore.RED}{self.get_message('errors.failed_download', e)}{Style.RESET_ALL}")
            return False

    def display_job_document(self, job_document):
        """Display job document in a pretty, educational format"""
        print(f"\n{Fore.YELLOW}{self.get_message('ui.job_document_title')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('ui.separator_line')}{Style.RESET_ALL}")

        try:
            # Handle both string and dict job documents
            if isinstance(job_document, str):
                job_doc = json.loads(job_document)
            else:
                job_doc = job_document

            # Display OTA section
            ota_section = job_doc.get("ota", {})
            if ota_section:
                print(f"{Fore.GREEN}{self.get_message('ui.ota_config')}{Style.RESET_ALL}")

                # Display packages
                packages = ota_section.get("packages", {})
                if packages:
                    print(f"{Fore.CYAN}{self.get_message('ui.firmware_packages')}{Style.RESET_ALL}")

                    for package_name, package_info in packages.items():
                        print(f"{Fore.YELLOW}{self.get_message('ui.package_label', package_name)}{Style.RESET_ALL}")

                        # Display version
                        version = package_info.get("version")
                        if version:
                            print(f"{Fore.CYAN}{self.get_message('ui.version_label', version)}{Style.RESET_ALL}")

                        # Display artifact info
                        artifact = package_info.get("artifact", {})
                        if artifact:
                            print(f"{Fore.CYAN}{self.get_message('ui.artifact_details')}{Style.RESET_ALL}")

                            # S3 location
                            s3_location = artifact.get("s3Location", {})
                            if s3_location:
                                bucket = s3_location.get("bucket", "N/A")
                                key = s3_location.get("key", "N/A")
                                version_id = s3_location.get("version", "N/A")
                                print(f"{Fore.WHITE}{self.get_message('ui.s3_bucket', bucket)}{Style.RESET_ALL}")
                                print(f"{Fore.WHITE}{self.get_message('ui.s3_key', key)}{Style.RESET_ALL}")
                                print(f"{Fore.WHITE}{self.get_message('ui.version_id', version_id)}{Style.RESET_ALL}")

                            # Presigned URL (show presence, not full URL for security)
                            presigned_url = artifact.get("s3PresignedUrl")
                            if presigned_url:
                                print(f"{Fore.WHITE}{self.get_message('ui.presigned_url_available')}{Style.RESET_ALL}")

                            # File info
                            file_id = artifact.get("fileId")
                            if file_id:
                                print(f"{Fore.WHITE}{self.get_message('ui.file_id', file_id)}{Style.RESET_ALL}")

                # Display streamName if present
                stream_name = ota_section.get("streamName")
                if stream_name:
                    print(f"{Fore.CYAN}{self.get_message('ui.stream_name', stream_name)}{Style.RESET_ALL}")

                # Display roleArn if present
                role_arn = ota_section.get("roleArn")
                if role_arn:
                    print(f"{Fore.CYAN}{self.get_message('ui.iam_role', role_arn.split('/')[-1])}{Style.RESET_ALL}")

            # Display any other top-level keys
            other_keys = [k for k in job_doc.keys() if k != "ota"]
            if other_keys:
                print(f"\n{Fore.YELLOW}{self.get_message('ui.additional_params')}{Style.RESET_ALL}")
                for key in other_keys:
                    value = job_doc[key]
                    if isinstance(value, (dict, list)):
                        print(f"{Fore.CYAN}  {key}: {Fore.WHITE}{json.dumps(value, indent=4)}{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.CYAN}  {key}: {Fore.WHITE}{value}{Style.RESET_ALL}")

            print(f"{Fore.CYAN}{self.get_message('ui.separator_line')}{Style.RESET_ALL}\n")

        except Exception as e:
            print(f"{Fore.RED}{self.get_message('errors.parse_error', e)}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}{self.get_message('ui.raw_job_document')}{Style.RESET_ALL}")
            print(json.dumps(job_document, indent=2))

    def get_human_readable_size(self, size_bytes):
        """Convert bytes to human readable format"""
        for unit in ["B", "KB", "MB", "GB"]:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f}{unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f}TB"

    def update_job_execution_status(self, job_id, thing_name, should_succeed):
        """Update job execution status"""
        if should_succeed:
            print(f"{Fore.GREEN}{self.get_message('status.job_succeeded', thing_name)}{Style.RESET_ALL}")
            if self.verbose_mode:
                print(f"{Fore.GREEN}{self.get_message('status.updating_succeeded')}{Style.RESET_ALL}")

            response = self.safe_api_call(
                self.iot_jobs_data_client.update_job_execution,
                "Job Execution Update",
                f"{job_id} on {thing_name}",
                debug=self.debug_mode,
                jobId=job_id,
                thingName=thing_name,
                status="SUCCEEDED",
            )
        else:
            print(f"{Fore.RED}{self.get_message('status.job_failed', thing_name)}{Style.RESET_ALL}")
            if self.verbose_mode:
                print(f"{Fore.RED}{self.get_message('status.updating_failed')}{Style.RESET_ALL}")

            status_details = {"failureType": "DOWNLOAD_FAILURE", "failureReason": "Simulated failure"}
            response = self.safe_api_call(
                self.iot_jobs_data_client.update_job_execution,
                "Job Execution Update",
                f"{job_id} on {thing_name}",
                debug=self.debug_mode,
                jobId=job_id,
                thingName=thing_name,
                status="FAILED",
                statusDetails=status_details,
            )

        return response is not None

    def process_job_execution(self, job_id, thing_name, execution_number, should_succeed, index, total):
        """Process a single job execution with rate limiting"""
        with self.job_execution_semaphore:
            if self.verbose_mode:  # Only show individual processing in verbose mode
                print(
                    f"{Fore.MAGENTA}{self.get_message('status.processing_execution', index, total, thing_name)}{Style.RESET_ALL}"
                )

            # Get job execution details
            if self.verbose_mode:
                print(f"{Fore.CYAN}{self.get_message('status.getting_job_details', thing_name)}{Style.RESET_ALL}")

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
                print(f"{Fore.RED}{self.get_message('errors.failed_job_details', thing_name)}{Style.RESET_ALL}")
                return False

            if self.verbose_mode:
                print(f"{Fore.CYAN}{self.get_message('status.job_details_retrieved')}{Style.RESET_ALL}")

            execution = execution_response.get("execution", {})
            job_document = execution.get("jobDocument")

            if job_document:
                if self.verbose_mode:
                    print(f"{Fore.GREEN}{self.get_message('status.job_document_retrieved')}{Style.RESET_ALL}")
                    self.display_job_document(job_document)

                # Check if this is an OTA job with S3 download
                has_presigned_url = self.has_presigned_url(job_document)

                if has_presigned_url:
                    # OTA job - download real artifact from S3
                    download_success = self.download_artifact_from_job(job_document, job_id, thing_name, execution_number)

                    # Update job execution status based on should_succeed flag and download result
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
                            print(f"{Fore.RED}{self.get_message('errors.download_failed')}{Style.RESET_ALL}")
                        return self.update_job_execution_status(job_id, thing_name, False)
                else:
                    # Custom job - simulate processing without download
                    print(f"{Fore.BLUE}{self.get_message('status.processing_custom', thing_name)}{Style.RESET_ALL}")

                    # Simulate processing time
                    time.sleep(0.1)  # Custom job processing simulation  # nosemgrep: arbitrary-sleep

                    print(f"{Fore.GREEN}{self.get_message('status.custom_completed', thing_name)}{Style.RESET_ALL}")

                    # Update job execution status based on should_succeed flag only
                    success = self.update_job_execution_status(job_id, thing_name, should_succeed)
                    return success if should_succeed else False
            else:
                print(f"{Fore.RED}{self.get_message('errors.no_job_document', thing_name)}{Style.RESET_ALL}")
                return False

            time.sleep(0.007)  # AWS API rate limiting: 150 TPS for job executions  # nosemgrep: arbitrary-sleep

    def get_user_inputs(self, available_jobs, thing_names, total_executions):
        """Get user inputs for job simulation"""
        # Job selection
        print(f"\n{Fore.YELLOW}{self.get_message('prompts.enter_job_id')}{Style.RESET_ALL}")
        selected_job_id = input().strip()

        # Sanitize input to prevent XSS
        import html

        selected_job_id = html.escape(selected_job_id)

        if not selected_job_id or selected_job_id not in available_jobs:
            print(f"{Fore.RED}{self.get_message('errors.invalid_job_id')}{Style.RESET_ALL}")
            return None, None, None

        return selected_job_id, None, None

    def educational_pause(self, title, description):
        """Pause execution with educational content"""
        print(f"\n{Fore.YELLOW}📚 LEARNING MOMENT: {title}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{description}{Style.RESET_ALL}")
        input(f"\n{Fore.GREEN}{self.get_message('prompts.press_enter')}{Style.RESET_ALL}")
        print()

    def run(self):
        """Main execution flow"""
        self.print_header()

        # Get verbose and debug mode preferences
        self.get_verbose_mode()
        self.get_debug_mode()

        # Step 1: Job Discovery
        self.educational_pause(
            self.get_message("learning.job_discovery_title"),
            self.get_message("learning.job_discovery_description"),
        )

        # Scan for active jobs
        available_jobs = self.scan_active_jobs()

        if not available_jobs:
            print(f"{Fore.RED}{self.get_message('errors.no_active_jobs')}{Style.RESET_ALL}")
            sys.exit(1)

        # Let user select a job
        selected_job_id, executions_to_process, success_percentage = self.get_user_inputs(available_jobs, [], 0)

        if not selected_job_id:
            sys.exit(1)

        # Step 2: Execution Discovery
        self.educational_pause(
            self.get_message("learning.execution_discovery_title"),
            self.get_message("learning.execution_discovery_description", selected_job_id),
        )

        # Get job executions
        thing_names = self.get_job_executions(selected_job_id)

        if not thing_names:
            print(f"{Fore.RED}{self.get_message('errors.no_pending_executions', selected_job_id)}{Style.RESET_ALL}")
            sys.exit(1)

        total_executions = len(thing_names)

        # Get execution scope and success percentage only
        print(f"\n{Fore.GREEN}{self.get_message('status.found_executions', total_executions)}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{self.get_message('prompts.execution_scope')}{Style.RESET_ALL}")
        execution_scope = input().strip()

        executions_to_process = total_executions
        if execution_scope.upper() != "ALL" and execution_scope.isdigit():
            executions_to_process = min(int(execution_scope), total_executions)

        # Success percentage
        while True:
            try:
                success_percentage = int(
                    input(f"{Fore.YELLOW}{self.get_message('prompts.success_percentage')}{Style.RESET_ALL}")
                )
                if 0 <= success_percentage <= 100:
                    break
                print(f"{Fore.RED}{self.get_message('errors.invalid_percentage')}{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED}{self.get_message('errors.invalid_number')}{Style.RESET_ALL}")

        # Calculate success and failure counts
        success_count = (executions_to_process * success_percentage) // 100
        failure_count = executions_to_process - success_count

        print(f"\n{Fore.CYAN}{self.get_message('ui.execution_plan')}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{self.get_message('ui.success_label', success_count)}{Style.RESET_ALL}")
        print(f"{Fore.RED}{self.get_message('ui.failure_label', failure_count)}{Style.RESET_ALL}")
        print(f"{Fore.BLUE}{self.get_message('ui.total_label', executions_to_process)}{Style.RESET_ALL}")

        # Prepare execution data with visible progress
        print(f"{Fore.BLUE}{self.get_message('status.preparing_plan')}{Style.RESET_ALL}")
        execution_data = []
        for i, thing_name in enumerate(thing_names[:executions_to_process], 1):
            should_succeed = i <= success_count
            status = self.get_message("ui.success_status") if should_succeed else self.get_message("ui.failure_status")

            # Show progress for every device
            print(
                f"{Fore.CYAN}{self.get_message('status.plan_assignment', i, executions_to_process, thing_name, status)}{Style.RESET_ALL}"
            )

            # Get execution number
            exec_response = self.safe_api_call(
                self.iot_client.describe_job_execution,
                "Job Execution Detail",
                f"{selected_job_id} on {thing_name}",
                debug=False,
                jobId=selected_job_id,
                thingName=thing_name,
            )

            execution_number = "1"
            if exec_response:
                execution_number = str(exec_response.get("execution", {}).get("executionNumber", "1"))

            execution_data.append((selected_job_id, thing_name, execution_number, should_succeed, i, executions_to_process))

        print(f"\n{Fore.GREEN}{self.get_message('status.plan_prepared')}{Style.RESET_ALL}")

        # Ask user to proceed
        proceed = input(f"\n{Fore.YELLOW}{self.get_message('prompts.proceed_simulation')}{Style.RESET_ALL}").strip().lower()
        if proceed in ["n", "no"]:
            print(f"{Fore.YELLOW}{self.get_message('ui.cancelled_user')}{Style.RESET_ALL}")
            sys.exit(0)

        # Step 3: Execution Simulation
        self.educational_pause(
            self.get_message("learning.execution_simulation_title"),
            self.get_message("learning.execution_simulation_description", executions_to_process, success_percentage),
        )

        # Process job executions in parallel
        print(f"\n{Fore.BLUE}{self.get_message('status.processing_executions', executions_to_process)}{Style.RESET_ALL}")

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

                # Progress update every 20 completions or show all in verbose mode
                if completed % 20 == 0 or completed == executions_to_process or self.verbose_mode:
                    print(
                        f"{Fore.CYAN}{self.get_message('status.progress_update', completed, executions_to_process, success_count_actual, failed_count_actual)}{Style.RESET_ALL}"
                    )

        end_time = time.time()
        duration = end_time - start_time

        print(f"{Fore.GREEN}{self.get_message('status.simulation_completed')}{Style.RESET_ALL}")
        print(
            f"{Fore.CYAN}{self.get_message('status.processed_summary', executions_to_process, success_count_actual, failed_count_actual)}{Style.RESET_ALL}"
        )
        print(f"{Fore.CYAN}{self.get_message('status.execution_time', duration)}{Style.RESET_ALL}")

    def cleanup(self):
        """Cleanup temporary files"""
        print(f"\n{Fore.YELLOW}{self.get_message('status.cleaning_temp')}{Style.RESET_ALL}")
        try:
            import shutil

            shutil.rmtree(self.temp_dir, ignore_errors=True)
            print(f"{Fore.GREEN}{self.get_message('status.cleanup_completed')}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.YELLOW}{self.get_message('errors.cleanup_warning', e)}{Style.RESET_ALL}")


if __name__ == "__main__":
    # Initialize language and load messages
    USER_LANG = get_language()
    messages = load_messages("simulate_job_execution", USER_LANG)

    simulator = IoTJobSimulator()
    try:
        simulator.run()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}{simulator.get_message('ui.cancelled')}{Style.RESET_ALL}")
        sys.exit(0)
    finally:
        simulator.cleanup()
