#!/usr/bin/env python3

import json
import os
import sys
import time
import subprocess
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Semaphore
from datetime import datetime

import boto3
from botocore.exceptions import ClientError, EndpointConnectionError, ConnectionError
from colorama import Fore, Style, init

# Add repository root and i18n to path
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)
sys.path.append(os.path.join(repo_root, "i18n"))

from language_selector import get_language
from loader import load_messages

# Import resource tagging module from iot_helpers package
from iot_helpers.utils.resource_tagger import apply_workshop_tags

# Initialize colorama
init()

# Global variables for i18n
USER_LANG = "en"
messages = {}


class BulkProvisioningManager:
    def __init__(self):
        self.region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        self.account_id = None
        self.debug_mode = False
        self.iot_client = None
        self.s3_client = None
        self.sts_client = None
        self.iam_client = None

        # Rate limiting semaphore
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

    def safe_api_call(self, func, operation_name, resource_name, debug=False, max_retries=3, **kwargs):
        """Safely execute AWS API call with error handling, retry logic, and optional debug info"""
        for attempt in range(max_retries + 1):
            try:
                if debug or self.debug_mode:
                    if attempt > 0:
                        print(f"\n{self.get_message('debug.retry_attempt', attempt, max_retries)}")
                    print(f"\n{self.get_message('debug.debug_operation', operation_name, resource_name)}")
                    print(self.get_message("debug.api_call", func.__name__))
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
                
                # Handle retryable errors with exponential backoff
                if error_code in ["Throttling", "ThrottlingException", "RequestLimitExceeded", "ServiceUnavailable"] and attempt < max_retries:
                    backoff_time = (2 ** attempt) + random.uniform(0, 1)  # Exponential backoff with jitter
                    if debug or self.debug_mode:
                        print(self.get_message("debug.throttling_retry", error_code, backoff_time, attempt + 1, max_retries))
                    time.sleep(backoff_time)  # nosemgrep: arbitrary-sleep
                    continue
                
                # Handle non-retryable errors
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
                
            except (EndpointConnectionError, ConnectionError) as e:
                # Handle network connectivity errors with retry
                if attempt < max_retries:
                    backoff_time = (2 ** attempt) + random.uniform(0, 1)  # Exponential backoff with jitter
                    if debug or self.debug_mode:
                        print(self.get_message("debug.network_retry", str(e), backoff_time, attempt + 1, max_retries))
                    time.sleep(backoff_time)  # nosemgrep: arbitrary-sleep
                    continue
                else:
                    print(self.get_message("errors.network_error", operation_name, str(e)))
                    if debug or self.debug_mode:
                        print(self.get_message("debug.network_troubleshooting"))
                    return None
                    
            except Exception as e:
                print(self.get_message("errors.general_error", str(e)))
                if debug or self.debug_mode:
                    import traceback
                    print(self.get_message("debug.full_traceback"))
                    traceback.print_exc()
                time.sleep(0.1)  # nosemgrep: arbitrary-sleep
                return None
        
        # If we get here, all retries were exhausted
        print(self.get_message("errors.max_retries_exceeded", operation_name, max_retries))
        return None

    def initialize_clients(self):
        """Initialize AWS clients"""
        try:
            self.iot_client = boto3.client("iot", region_name=self.region)
            self.s3_client = boto3.client("s3", region_name=self.region)
            self.sts_client = boto3.client("sts", region_name=self.region)
            self.iam_client = boto3.client("iam", region_name=self.region)

            # Get account ID
            identity = self.sts_client.get_caller_identity()
            self.account_id = identity["Account"]

            if self.debug_mode:
                print(self.get_message("status.clients_initialized"))
                print(self.get_message("status.iot_service", self.iot_client.meta.service_model.service_name))
                print(self.get_message("status.api_version", self.iot_client.meta.service_model.api_version))

            return True
        except Exception as e:
            print(self.get_message("errors.client_init_error", str(e)))
            return False

    def educational_pause(self, title, description):
        """Pause execution with educational content"""
        print(f"\n{Fore.YELLOW}📚 LEARNING MOMENT: {title}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{description}{Style.RESET_ALL}")
        input(f"\n{Fore.GREEN}{self.get_message('prompts.press_enter')}{Style.RESET_ALL}")
        print()

    def print_header(self):
        """Print educational header about bulk provisioning"""
        print(f"{Fore.CYAN}{self.get_message('title')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('separator')}{Style.RESET_ALL}\n")

        print(f"{Fore.YELLOW}{self.get_message('learning_goal')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('learning_description')}{Style.RESET_ALL}\n")

        # Initialize clients and display info
        if not self.initialize_clients():
            return False

        print(f"{Fore.CYAN}{self.get_message('region_label')} {Fore.GREEN}{self.region}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('account_id_label')} {Fore.GREEN}{self.account_id}{Style.RESET_ALL}\n")

    def get_debug_mode(self):
        """Ask user for debug mode"""
        print(f"{Fore.RED}{self.get_message('warnings.debug_warning')}{Style.RESET_ALL}")
        choice = input(f"{Fore.YELLOW}{self.get_message('prompts.debug_mode')}{Style.RESET_ALL}").strip().lower()
        self.debug_mode = choice in ["y", "yes"]

        if self.debug_mode:
            print(f"{Fore.GREEN}{self.get_message('status.debug_enabled')}{Style.RESET_ALL}\n")

    def get_operation_choice(self):
        """Get operation choice from user"""
        print(f"{Fore.BLUE}{self.get_message('ui.operation_menu')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('ui.list_tasks_option')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('ui.describe_task_option')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('ui.register_bulk_option')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('ui.check_results_option')}{Style.RESET_ALL}")

        while True:
            try:
                choice = int(input(f"{Fore.YELLOW}{self.get_message('prompts.operation_choice')}{Style.RESET_ALL}"))
                if 1 <= choice <= 4:
                    return choice
                print(f"{Fore.RED}{self.get_message('errors.invalid_choice')}{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED}{self.get_message('errors.invalid_number')}{Style.RESET_ALL}")

    def list_registration_tasks(self):
        """List all bulk thing registration tasks"""
        print(f"\n{Fore.BLUE}📋 {self.get_message('ui.listing_tasks')}{Style.RESET_ALL}\n")

        response = self.safe_api_call(
            self.iot_client.list_thing_registration_tasks,
            "List Thing Registration Tasks",
            "all tasks",
            debug=self.debug_mode,
            maxResults=50
        )

        if not response:
            print(f"{Fore.RED}{self.get_message('errors.failed_list_tasks')}{Style.RESET_ALL}")
            return

        tasks = response.get("taskIds", [])

        if not tasks:
            print(f"{Fore.YELLOW}{self.get_message('results.no_tasks_found')}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{self.get_message('results.create_first_task')}{Style.RESET_ALL}")
            return

        print(f"{Fore.GREEN}{self.get_message('results.found_tasks', len(tasks))}{Style.RESET_ALL}\n")

        # Get details for each task
        for i, task_id in enumerate(tasks, 1):
            task_details = self.safe_api_call(
                self.iot_client.describe_thing_registration_task,
                "Describe Thing Registration Task",
                task_id,
                debug=False,
                taskId=task_id
            )

            if task_details:
                status = task_details.get("status", "Unknown")
                creation_date = task_details.get("creationDate", "Unknown")
                success_count = task_details.get("successCount", 0)
                failure_count = task_details.get("failureCount", 0)
                
                print(f"{Fore.CYAN}{i}. {Fore.YELLOW}{task_id}{Style.RESET_ALL}")
                print(f"   {Fore.GREEN}{self.get_message('status.task_status', status)}{Style.RESET_ALL}")
                print(f"   {Fore.GREEN}{self.get_message('status.task_created', creation_date)}{Style.RESET_ALL}")
                print(f"   {Fore.GREEN}{self.get_message('status.task_success_count', success_count)} | {self.get_message('status.task_failure_count', failure_count)}{Style.RESET_ALL}")
                print()

    def describe_registration_task(self):
        """Describe a specific bulk registration task"""
        print(f"\n{Fore.BLUE}🔍 {self.get_message('ui.describe_task')}{Style.RESET_ALL}\n")

        task_id = input(f"{Fore.YELLOW}{self.get_message('prompts.task_id_input')}{Style.RESET_ALL}").strip()

        if not task_id:
            print(f"{Fore.RED}{self.get_message('errors.task_id_empty')}{Style.RESET_ALL}")
            return

        response = self.safe_api_call(
            self.iot_client.describe_thing_registration_task,
            "Describe Thing Registration Task",
            task_id,
            debug=self.debug_mode,
            taskId=task_id
        )

        if not response:
            print(f"{Fore.RED}{self.get_message('errors.task_not_found', task_id)}{Style.RESET_ALL}")
            return

        # Display comprehensive task details
        print(f"{Fore.GREEN}{self.get_message('ui.task_details')}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{self.get_message('status.task_id', response.get('taskId', 'N/A'))}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{self.get_message('status.task_status', response.get('status', 'N/A'))}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{self.get_message('status.task_created', response.get('creationDate', 'N/A'))}{Style.RESET_ALL}")
        
        # Extract and display template information
        template_info = self._extract_template_info(response.get('templateBody', ''))
        print(f"{Fore.GREEN}{self.get_message('status.task_template', template_info)}{Style.RESET_ALL}")
        
        print(f"{Fore.GREEN}{self.get_message('status.task_input_file', response.get('inputFileBucket', 'N/A'), response.get('inputFileKey', 'N/A'))}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{self.get_message('status.task_role_arn', response.get('roleArn', 'N/A'))}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{self.get_message('status.task_success_count', response.get('successCount', 0))}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{self.get_message('status.task_failure_count', response.get('failureCount', 0))}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{self.get_message('status.task_progress', response.get('percentageProgress', 0))}{Style.RESET_ALL}")

        # Educational pause about task lifecycle
        self.educational_pause(
            self.get_message("learning.task_lifecycle_title"),
            self.get_message("learning.task_lifecycle_description")
        )

    def _extract_template_info(self, template_body):
        """Extract meaningful information from template body without showing full JSON"""
        if not template_body:
            return "N/A"
        
        try:
            import json
            template = json.loads(template_body) if isinstance(template_body, str) else template_body
            
            # Extract key information
            info_parts = []
            
            # Check for template name/description
            if 'templateName' in template:
                info_parts.append(f"Name: {template['templateName']}")
            elif 'Description' in template:
                info_parts.append(f"Desc: {template['Description'][:50]}...")
            
            # Count parameters and resources
            parameters = template.get('Parameters', {})
            resources = template.get('Resources', {})
            
            if parameters:
                param_names = list(parameters.keys())[:3]  # Show first 3 parameters
                param_str = ", ".join(param_names)
                if len(parameters) > 3:
                    param_str += f" (+{len(parameters)-3} more)"
                info_parts.append(f"Params: {param_str}")
            
            if resources:
                resource_types = [res.get('Type', 'Unknown') for res in resources.values()]
                unique_types = list(set(resource_types))[:3]  # Show first 3 unique types
                type_str = ", ".join(unique_types)
                if len(unique_types) > 3:
                    type_str += f" (+{len(unique_types)-3} more)"
                info_parts.append(f"Resources: {type_str}")
            
            if info_parts:
                return " | ".join(info_parts)
            else:
                return f"Template with {len(template)} sections"
                
        except (json.JSONDecodeError, TypeError, AttributeError) as e:
            if self.debug_mode:
                print(f"{Fore.YELLOW}{self.get_message('errors.template_parsing_error', e)}{Style.RESET_ALL}")
            return "Template (parsing error)"

    def get_available_thing_types(self):
        """Get list of available thing types from AWS IoT"""
        try:
            response = self.safe_api_call(
                self.iot_client.list_thing_types,
                "List Thing Types",
                "all thing types",
                debug=self.debug_mode,
                maxResults=50
            )
            
            if not response:
                return []
            
            thing_types = []
            for thing_type in response.get("thingTypes", []):
                thing_types.append(thing_type["thingTypeName"])
            
            if self.debug_mode:
                print(f"{Fore.GREEN}{self.get_message('status.found_thing_types', len(thing_types))}{Style.RESET_ALL}")
                
            return thing_types
            
        except Exception as e:
            print(f"{Fore.RED}{self.get_message('errors.error_retrieving_thing_types', e)}{Style.RESET_ALL}")
            return []

    def analyze_device_naming_pattern(self):
        """Analyze existing device names to detect naming pattern and next number"""
        try:
            # Get existing things from IoT registry
            response = self.safe_api_call(
                self.iot_client.list_things,
                "List Things",
                "existing devices",
                debug=self.debug_mode,
                maxResults=100
            )
            
            if not response or not response.get("things"):
                # No existing devices, use default pattern
                if self.debug_mode:
                    print(f"{Fore.YELLOW}{self.get_message('status.no_existing_devices')}{Style.RESET_ALL}")
                return "Vehicle-VIN-", 1
            
            things = response.get("things", [])
            thing_names = [thing["thingName"] for thing in things]
            
            if self.debug_mode:
                print(f"{Fore.GREEN}{self.get_message('status.found_existing_devices', len(thing_names))}{Style.RESET_ALL}")
                print(self.get_message("debug.sample_names", thing_names[:5]))
            
            # Analyze naming patterns
            import re
            patterns = [
                r"^(.+-)(\d+)$",           # Vehicle-VIN-025 -> ("Vehicle-VIN-", 25)
                r"^(.+_)(\d+)$",           # device_001 -> ("device_", 1)
                r"^(.+)(\d+)$",            # fleet024 -> ("fleet", 24)
            ]
            
            pattern_matches = {}
            
            for name in thing_names:
                for pattern in patterns:
                    match = re.match(pattern, name)
                    if match:
                        prefix = match.group(1)
                        number = int(match.group(2))
                        
                        if prefix not in pattern_matches:
                            pattern_matches[prefix] = []
                        pattern_matches[prefix].append(number)
                        break
            
            if not pattern_matches:
                # No recognizable pattern, use default
                if self.debug_mode:
                    print(f"{Fore.YELLOW}{self.get_message('status.no_recognizable_pattern')}{Style.RESET_ALL}")
                return "Vehicle-VIN-", 1
            
            # Find the most common pattern (prefix with most matches)
            most_common_prefix = max(pattern_matches.keys(), key=lambda k: len(pattern_matches[k]))
            highest_number = max(pattern_matches[most_common_prefix])
            
            if self.debug_mode:
                print(f"{Fore.GREEN}{self.get_message('status.detected_pattern', most_common_prefix, highest_number)}{Style.RESET_ALL}")
                print(self.get_message("debug.numbers_found", sorted(pattern_matches[most_common_prefix])))
            
            return most_common_prefix, highest_number + 1
            
        except Exception as e:
            print(f"{Fore.RED}{self.get_message('errors.error_analyzing_naming', e)}{Style.RESET_ALL}")
            # Return default pattern on error
            return "Vehicle-VIN-", 1

    def generate_device_names(self, prefix, start_number, count=5):
        """Generate device names based on pattern and starting number"""
        device_names = []
        for i in range(count):
            device_name = f"{prefix}{start_number + i:03d}"  # Zero-padded 3 digits
            device_names.append(device_name)
        
        if self.debug_mode:
            print(f"{Fore.CYAN}{self.get_message('status.generated_device_names_header')}{Style.RESET_ALL}")
            for name in device_names:
                print(self.get_message("debug.generated_device_names", name))
        
        return device_names

    def register_things_bulk(self):
        """Execute complete bulk registration workflow with enhanced educational flow"""
        print(f"\n{Fore.BLUE}🚀 {self.get_message('ui.bulk_registration')}{Style.RESET_ALL}\n")
        
        # Enhanced educational introduction - explain the complete process first
        self.educational_pause(
            self.get_message("learning.understanding_bulk_registration_title"),
            self.get_message("learning.understanding_bulk_registration_description")
        )
        
        # Explain what learners will experience in this workflow
        self.educational_pause(
            self.get_message("learning.what_you_will_learn_title"),
            self.get_message("learning.what_you_will_learn_description")
        )
        
        # Check OpenSSL availability first
        if not self.test_openssl_availability():
            return
        
        # Execute the enhanced 5-step workflow
        try:
            # Step 0: Explain provisioning template (enhanced)
            if not self.step0_explain_provisioning_template_enhanced():
                return
            
            # Pre-Step 1: Explain input file requirements
            self.explain_input_file_requirements()
            
            # Step 1: Create input file (with enhanced context)
            input_file_path = self.step1_create_input_file_enhanced()
            if not input_file_path:
                return
            
            # Pre-Step 2: Explain S3 storage purpose
            self.explain_s3_storage_purpose()
            
            # Step 2: Upload to S3
            s3_key = self.step2_upload_to_s3(input_file_path)
            if not s3_key:
                return
            
            # Pre-Step 3: Explain IAM policy requirements
            self.explain_iam_policy_requirements()
            
            # Step 3: Ensure policy exists
            if not self.step3_ensure_policy_exists():
                return
            
            # Pre-Step 4: Explain task creation and monitoring
            self.explain_task_creation_process()
            
            # Step 4: Start registration task
            task_id = self.step4_start_registration_task(s3_key)
            if task_id:
                print(f"\n{Fore.GREEN}🎉 {self.get_message('ui.workflow_completed')}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}💡 {self.get_message('ui.check_results_guidance')}{Style.RESET_ALL}")
            
        except Exception as e:
            print(f"{Fore.RED}❌ {self.get_message('errors.workflow_failed', str(e))}{Style.RESET_ALL}")
        finally:
            # Clean up temporary files
            if 'input_file_path' in locals() and input_file_path and os.path.exists(input_file_path):
                try:
                    os.remove(input_file_path)
                    if self.debug_mode:
                        print(f"{Fore.CYAN}{self.get_message('status.cleaned_up_temp_file', input_file_path)}{Style.RESET_ALL}")
                except Exception as e:
                    if self.debug_mode:
                        print(f"{Fore.YELLOW}{self.get_message('status.cleanup_failed', input_file_path, e)}{Style.RESET_ALL}")

    def step0_explain_provisioning_template_enhanced(self):
        """Step 0: Enhanced learning moment explaining provisioning template"""
        try:
            # Load and display provisioning template
            template = self.load_provisioning_template()
            if not template:
                return False
            
            # Enhanced educational explanation
            self.educational_pause(
                self.get_message("learning.step0_understanding_templates_title"),
                self.get_message("learning.step0_understanding_templates_description")
            )
            
            # Show template structure in educational way
            if template and 'Parameters' in template:
                params = list(template['Parameters'].keys())
                resources = list(template.get('Resources', {}).keys())
                
                self.educational_pause(
                    self.get_message("learning.template_components_title"),
                    self.get_message("learning.template_components_description", ', '.join(params), ', '.join(resources))
                )
            
            return True
            
        except Exception as e:
            print(f"{Fore.RED}❌ {self.get_message('errors.step0_failed', str(e))}{Style.RESET_ALL}")
            return False

    def explain_input_file_requirements(self):
        """Explain what the input file contains and why it's needed"""
        self.educational_pause(
            self.get_message("learning.understanding_input_file_title"),
            self.get_message("learning.understanding_input_file_description")
        )

    def explain_s3_storage_purpose(self):
        """Explain why S3 storage is needed for bulk operations"""
        self.educational_pause(
            self.get_message("learning.why_s3_storage_title"),
            self.get_message("learning.why_s3_storage_description")
        )

    def explain_iam_policy_requirements(self):
        """Explain the IAM policy requirements for bulk provisioning"""
        self.educational_pause(
            self.get_message("learning.understanding_iam_policy_title"),
            self.get_message("learning.understanding_iam_policy_description")
        )

    def explain_task_creation_process(self):
        """Explain how the registration task works"""
        self.educational_pause(
            self.get_message("learning.how_registration_task_works_title"),
            self.get_message("learning.how_registration_task_works_description")
        )

    def step1_create_input_file_enhanced(self):
        """Step 1: Create bulk_registration_input_YYYYMMDD_hhmmss.json with enhanced context"""
        print(f"\n{Fore.BLUE}📝 {self.get_message('ui.step1_title')}{Style.RESET_ALL}")
        
        try:
            # Explain thing types before showing the list
            self.educational_pause(
                self.get_message("learning.understanding_thing_types_title"),
                self.get_message("learning.understanding_thing_types_description")
            )
            
            # Get available thing types
            thing_types = self.get_available_thing_types()
            if not thing_types:
                print(f"{Fore.YELLOW}⚠️  {self.get_message('warnings.no_thing_types')}{Style.RESET_ALL}")
                thing_type = "DefaultThingType"
                
                self.educational_pause(
                    self.get_message("learning.no_thing_types_found_title"),
                    self.get_message("learning.no_thing_types_found_description")
                )
            else:
                # Explain the available options
                print(f"\n{Fore.CYAN}{self.get_message('status.available_thing_types_header')}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}{self.get_message('status.thing_types_description')}\n{Style.RESET_ALL}")
                
                for i, tt in enumerate(thing_types, 1):
                    print(f"{Fore.GREEN}  {i}. {tt}{Style.RESET_ALL}")
                
                print(f"\n{Fore.CYAN}{self.get_message('status.thing_type_properties_note')}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}   {self.get_message('status.thing_type_inheritance_note')}{Style.RESET_ALL}")
                
                while True:
                    try:
                        choice = int(input(f"\n{Fore.YELLOW}{self.get_message('prompts.select_thing_type', len(thing_types))}{Style.RESET_ALL}"))
                        if 1 <= choice <= len(thing_types):
                            thing_type = thing_types[choice - 1]
                            break
                        print(f"{Fore.RED}{self.get_message('errors.invalid_number_range', len(thing_types))}{Style.RESET_ALL}")
                    except ValueError:
                        print(f"{Fore.RED}{self.get_message('errors.invalid_number')}{Style.RESET_ALL}")
            
            print(f"\n{Fore.GREEN}{self.get_message('status.selected_thing_type', thing_type)}{Style.RESET_ALL}")
            
            # Explain device naming analysis
            self.educational_pause(
                self.get_message("learning.analyzing_device_naming_title"),
                self.get_message("learning.analyzing_device_naming_description")
            )
            
            # Analyze device naming pattern
            prefix, highest_number = self.analyze_device_naming_pattern()
            device_names = self.generate_device_names(prefix, highest_number, 5)
            
            # Explain the naming pattern results
            print(f"\n{Fore.GREEN}{self.get_message('status.device_naming_results')}{Style.RESET_ALL}")
            print(f"   {Fore.CYAN}{self.get_message('status.pattern_detected', f'{prefix}XXX')}{Style.RESET_ALL}")
            print(f"   {Fore.CYAN}{self.get_message('status.highest_existing_number', highest_number - 1)}{Style.RESET_ALL}")
            print(f"   {Fore.CYAN}{self.get_message('status.new_devices_range', device_names[0], device_names[-1])}{Style.RESET_ALL}")
            
            # Explain certificate generation process
            self.educational_pause(
                self.get_message("learning.generating_security_certificates_title"),
                self.get_message("learning.generating_security_certificates_description")
            )
            
            # Generate timestamp for filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"bulk_registration_input_{timestamp}.json"
            
            # Create line-delimited JSON entries
            json_entries = []
            manufacturing_date = datetime.now().strftime("%Y-%m-%d")
            
            print(f"\n{Fore.CYAN}{self.get_message('status.generating_certificates_progress')}{Style.RESET_ALL}")
            
            for i, device_name in enumerate(device_names, 1):
                print(f"  {Fore.YELLOW}{self.get_message('status.processing_device', i, 5, device_name)}{Style.RESET_ALL}")
                
                # Generate CSR for this device
                csr_content = self.generate_device_credentials(device_name)
                if not csr_content:
                    print(f"{Fore.RED}{self.get_message('errors.certificate_generation_failed', device_name)}{Style.RESET_ALL}")
                    return None
                
                # Create device entry (flat structure matching template parameters)
                entry = {
                    "ThingName": device_name,
                    "ManufacturingDate": manufacturing_date,
                    "ThingType": thing_type,
                    "CSR": csr_content
                }
                json_entries.append(json.dumps(entry))
                print(f"    {Fore.GREEN}{self.get_message('status.certificate_generated')}{Style.RESET_ALL}")
            
            # Explain the file format before writing
            self.educational_pause(
                self.get_message("learning.input_file_format_title"),
                self.get_message("learning.input_file_format_description", filename, len(device_names))
            )
            
            # Write to file (line-delimited JSON format)
            file_path = os.path.join(os.getcwd(), filename)
            try:
                with open(file_path, 'w') as f:
                    for entry in json_entries:
                        f.write(entry + '\n')
            except PermissionError:
                print(f"{Fore.RED}{self.get_message('errors.file_permission_denied', file_path)}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}{self.get_message('help.file_permissions')}{Style.RESET_ALL}")
                return None
            except OSError as e:
                print(f"{Fore.RED}{self.get_message('errors.file_write_failed', str(e))}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}{self.get_message('help.file_write_troubleshooting')}{Style.RESET_ALL}")
                return None
            
            print(f"\n{Fore.GREEN}{self.get_message('status.input_file_created', filename)}{Style.RESET_ALL}")
            print(f"   {Fore.CYAN}{self.get_message('status.device_count', len(device_names))}{Style.RESET_ALL}")
            print(f"   {Fore.CYAN}{self.get_message('status.file_format')}{Style.RESET_ALL}")
            
            if self.debug_mode:
                print(self.get_message("debug.full_path", file_path))
                print(self.get_message("debug.file_size", os.path.getsize(file_path)))
            
            return file_path
            
        except Exception as e:
            print(f"{Fore.RED}❌ Step 1 failed: {str(e)}{Style.RESET_ALL}")
            return None

    def step2_upload_to_s3(self, file_path):
        """Step 2: Upload input file to S3 bucket"""
        print(f"\n{Fore.BLUE}📤 {self.get_message('ui.step2_title')}{Style.RESET_ALL}")
        
        try:
            # Get S3 bucket from provisioning script
            bucket_name = self.get_s3_bucket_from_provisioning()
            if not bucket_name:
                return None
            
            # Verify bucket region matches our current region
            try:
                bucket_location = self.safe_api_call(
                    self.s3_client.get_bucket_location,
                    "Get Bucket Location",
                    bucket_name,
                    debug=self.debug_mode,
                    Bucket=bucket_name
                )
                
                if bucket_location:
                    bucket_region = bucket_location.get('LocationConstraint')
                    # Note: us-east-1 returns None for LocationConstraint
                    if bucket_region is None:
                        bucket_region = 'us-east-1'
                    
                    if bucket_region != self.region:
                        print(f"{Fore.YELLOW}{self.get_message('status.bucket_region_mismatch', bucket_region, self.region)}{Style.RESET_ALL}")
                        print(f"{Fore.CYAN}{self.get_message('status.creating_s3_client_for_region', bucket_region)}{Style.RESET_ALL}")
                        
                        # Create S3 client for the bucket's region
                        bucket_s3_client = boto3.client("s3", region_name=bucket_region)
                    else:
                        bucket_s3_client = self.s3_client
                        if self.debug_mode:
                            print(f"{Fore.GREEN}{self.get_message('status.bucket_region_matches', self.region)}{Style.RESET_ALL}")
                else:
                    # If we can't get bucket location, use the default client
                    bucket_s3_client = self.s3_client
                    
            except Exception as e:
                if self.debug_mode:
                    print(f"{Fore.YELLOW}{self.get_message('status.checking_bucket_region', e)}{Style.RESET_ALL}")
                bucket_s3_client = self.s3_client
            
            # Generate S3 key
            filename = os.path.basename(file_path)
            s3_key = f"bulk-provisioning/{filename}"
            
            print(f"{Fore.CYAN}📤 {self.get_message('ui.uploading_to_s3')}{Style.RESET_ALL}")
            print(f"   {Fore.GREEN}{self.get_message('status.bucket_info', bucket_name)}{Style.RESET_ALL}")
            print(f"   {Fore.GREEN}{self.get_message('status.key_info', s3_key)}{Style.RESET_ALL}")
            
            # Upload file to S3 using the appropriate client
            # Note: upload_file returns None on success, which creates ambiguity with safe_api_call
            # We'll handle this by calling upload_file directly and catching exceptions
            try:
                if self.debug_mode:
                    print(f"\n{self.get_message('debug.debug_operation', 'S3 Upload', s3_key)}")
                    print(self.get_message("debug.api_call", 'upload_file'))
                    print(self.get_message("debug.input_params"))
                    print(json.dumps({
                        "Filename": file_path,
                        "Bucket": bucket_name,
                        "Key": s3_key
                    }, indent=2, default=str))
                
                # Call upload_file directly since it returns None on success
                bucket_s3_client.upload_file(
                    Filename=file_path,
                    Bucket=bucket_name,
                    Key=s3_key
                )
                
                if self.debug_mode:
                    print(self.get_message("debug.api_response"))
                    print(self.get_message("debug.upload_null_response"))  # upload_file returns None on success
                
                # If we get here, upload succeeded
                print(f"{Fore.GREEN}✅ {self.get_message('status.s3_upload_success')}{Style.RESET_ALL}")
                
            except ClientError as e:
                error_code = e.response["Error"]["Code"]
                error_message = e.response["Error"]["Message"]
                print(f"{Fore.RED}❌ S3 Upload failed: {error_code} - {error_message}{Style.RESET_ALL}")
                
                if self.debug_mode:
                    print(self.get_message("debug.full_error"))
                    print(json.dumps(e.response, indent=2, default=str))
                
                return None
                
            except Exception as e:
                print(f"{Fore.RED}❌ S3 Upload failed: {str(e)}{Style.RESET_ALL}")
                
                if self.debug_mode:
                    import traceback
                    print(self.get_message("debug.full_traceback"))
                    traceback.print_exc()
                
                return None
            
            # Apply workshop tags to the S3 object (separate from upload success)
            try:
                tag_success = apply_workshop_tags(
                    client=bucket_s3_client,
                    resource_arn=f"arn:aws:s3:::{bucket_name}/{s3_key}",
                    resource_type='s3-object',
                    script_name='manage-bulk-provisioning'
                )
                
                if self.debug_mode:
                    if tag_success:
                        print(f"{Fore.GREEN}{self.get_message('status.s3_tags_applied')}{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.YELLOW}{self.get_message('status.s3_tags_warning')}{Style.RESET_ALL}")
            except Exception as e:
                if self.debug_mode:
                    print(f"{Fore.YELLOW}{self.get_message('status.s3_tags_failed', e)}{Style.RESET_ALL}")
            
            # Educational pause about S3 integration
            self.educational_pause(
                self.get_message("learning.s3_upload_title"),
                self.get_message("learning.s3_upload_description")
            )
            
            return s3_key
                
        except Exception as e:
            print(f"{Fore.RED}❌ {self.get_message('errors.step2_failed', str(e))}{Style.RESET_ALL}")
            return None

    def step3_ensure_policy_exists(self):
        """Step 3: Check/create BulkProvisioningPolicy and ensure IAM role has proper permissions"""
        print(f"\n{Fore.BLUE}🔐 {self.get_message('ui.step3_title')}{Style.RESET_ALL}")
        
        try:
            # First, ensure the IAM role exists and has proper permissions for bulk provisioning
            role_arn = self.get_iam_role_from_provisioning()
            if not role_arn:
                print(f"{Fore.RED}{self.get_message('status.no_iam_role_found')}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}{self.get_message('status.run_provisioning_first')}{Style.RESET_ALL}")
                return False
            
            # Ensure the IAM role has bulk provisioning permissions
            if not self.ensure_iam_role_has_bulk_provisioning_permissions(role_arn):
                print(f"{Fore.YELLOW}{self.get_message('status.could_not_verify_iam_permissions')}{Style.RESET_ALL}")
                # Continue anyway as the role exists
            
            # Create IoT policy for devices (this is separate from IAM role permissions)
            policy_name = "BulkProvisioningPolicy"
            
            # Check if IoT policy exists
            print(f"{Fore.CYAN}{self.get_message('status.checking_policy_exists', policy_name)}{Style.RESET_ALL}")
            
            existing_policy = self.safe_api_call(
                self.iot_client.get_policy,
                "Get Policy",
                policy_name,
                debug=self.debug_mode,
                policyName=policy_name
            )
            
            if existing_policy:
                print(f"{Fore.GREEN}✅ {self.get_message('status.policy_exists', policy_name)}{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}📝 {self.get_message('status.creating_policy', policy_name)}{Style.RESET_ALL}")
                
                # Create IoT policy document for devices
                policy_document = {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Action": "iot:*",
                            "Resource": f"arn:aws:iot:{self.region}:{self.account_id}:*"
                        }
                    ]
                }
                
                # Create the IoT policy
                response = self.safe_api_call(
                    self.iot_client.create_policy,
                    "Create Policy",
                    policy_name,
                    debug=self.debug_mode,
                    policyName=policy_name,
                    policyDocument=json.dumps(policy_document)
                )
                
                if response:
                    print(f"{Fore.GREEN}✅ {self.get_message('status.policy_created', policy_name)}{Style.RESET_ALL}")
                    
                    # Apply workshop tags to the policy
                    policy_arn = response.get('policyArn')
                    if policy_arn:
                        tag_success = apply_workshop_tags(
                            client=self.iot_client,
                            resource_arn=policy_arn,
                            resource_type='policy',
                            script_name='manage-bulk-provisioning'
                        )
                        
                        if self.debug_mode:
                            if tag_success:
                                print(f"{Fore.GREEN}{self.get_message('status.workshop_tags_applied')}{Style.RESET_ALL}")
                            else:
                                print(f"{Fore.YELLOW}{self.get_message('status.could_not_apply_tags')}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}{self.get_message('status.failed_to_create_policy', policy_name)}{Style.RESET_ALL}")
                    return False
            
            # Educational pause about IoT policies vs IAM policies
            self.educational_pause(
                self.get_message("learning.iot_policies_vs_iam_title"),
                self.get_message("learning.iot_policies_vs_iam_description")
            )
            
            return True
            
        except Exception as e:
            print(f"{Fore.RED}❌ {self.get_message('errors.step3_failed', str(e))}{Style.RESET_ALL}")
            return False

    def step4_start_registration_task(self, s3_key):
        """Step 4: Start the bulk registration task"""
        print(f"\n{Fore.BLUE}🚀 {self.get_message('ui.step4_title')}{Style.RESET_ALL}")
        
        try:
            # Get required parameters
            bucket_name = self.get_s3_bucket_from_provisioning()
            role_arn = self.get_iam_role_from_provisioning()
            
            if not bucket_name or not role_arn:
                return None
            
            # Load the provisioning template content
            template = self.load_provisioning_template()
            if not template:
                print(f"{Fore.RED}{self.get_message('status.failed_load_provisioning_template')}{Style.RESET_ALL}")
                return None
            
            # Convert template to JSON string for the API
            template_body = json.dumps(template)
            template_name = "BulkProvisioningTemplate"
            
            print(f"{Fore.CYAN}{self.get_message('status.task_parameters_header')}{Style.RESET_ALL}")
            print(f"   {Fore.GREEN}{self.get_message('status.template_info', template_name)}{Style.RESET_ALL}")
            print(f"   {Fore.GREEN}{self.get_message('status.bucket_info', bucket_name)}{Style.RESET_ALL}")
            print(f"   {Fore.GREEN}{self.get_message('status.key_info', s3_key)}{Style.RESET_ALL}")
            print(f"   {Fore.GREEN}{self.get_message('status.role_info', role_arn)}{Style.RESET_ALL}")
            
            # Start the registration task with template body (not template name)
            response = self.safe_api_call(
                self.iot_client.start_thing_registration_task,
                "Start Thing Registration Task",
                template_name,
                debug=self.debug_mode,
                templateBody=template_body,
                inputFileBucket=bucket_name,
                inputFileKey=s3_key,
                roleArn=role_arn
            )
            
            if response:
                task_id = response.get('taskId')
                print(f"\n{Fore.GREEN}{self.get_message('status.task_started')}{Style.RESET_ALL}")
                print(f"   {Fore.YELLOW}{self.get_message('status.task_id', task_id)}{Style.RESET_ALL}")
                print(f"   {Fore.CYAN}{self.get_message('status.task_initializing')}{Style.RESET_ALL}")
                
                # Educational pause about task monitoring
                self.educational_pause(
                    self.get_message("learning.task_monitoring_title"),
                    self.get_message("learning.task_monitoring_description")
                )
                
                return task_id
            else:
                print(f"{Fore.RED}❌ {self.get_message('errors.task_start_failed')}{Style.RESET_ALL}")
                return None
                
        except Exception as e:
            print(f"{Fore.RED}❌ {self.get_message('errors.step4_failed', str(e))}{Style.RESET_ALL}")
            return None

    def get_s3_bucket_from_provisioning(self):
        """Retrieve S3 bucket configured during provisioning script"""
        try:
            # Check for provisioning script configuration
            # This would typically read from a config file or environment variable
            # For now, we'll simulate this by checking common patterns
            
            # Try to get bucket from environment or config
            bucket_name = os.getenv('IOT_WORKSHOP_S3_BUCKET')
            
            if not bucket_name:
                # Use the same logic as provision_script.py to find existing buckets
                response = self.safe_api_call(
                    self.s3_client.list_buckets,
                    "List S3 Buckets",
                    "firmware buckets",
                    debug=self.debug_mode
                )
                
                if response:
                    # Look for buckets created by provision_script.py with pattern: iot-firmware-{region}-{timestamp}
                    existing_buckets = [
                        b["Name"] for b in response.get("Buckets", []) 
                        if b["Name"].startswith(f"iot-firmware-{self.region}")
                    ]
                    
                    if existing_buckets:
                        # Use the first (most recent) bucket found
                        bucket_name = existing_buckets[0]
                        if self.debug_mode:
                            print(f"{Fore.CYAN}🪣 Found provision script bucket: {bucket_name}{Style.RESET_ALL}")
                    else:
                        # Fallback: look for any bucket with firmware or workshop patterns
                        fallback_buckets = [
                            b["Name"] for b in response.get("Buckets", [])
                            if any(pattern in b["Name"].lower() for pattern in ['firmware', 'workshop', 'iot-device-management'])
                        ]
                        
                        if fallback_buckets:
                            bucket_name = fallback_buckets[0]
                            if self.debug_mode:
                                print(f"{Fore.YELLOW}🪣 Found fallback bucket: {bucket_name}{Style.RESET_ALL}")
                        else:
                            bucket_name = None
            
            if bucket_name:
                print(f"{Fore.GREEN}✅ {self.get_message('status.s3_bucket_found', bucket_name)}{Style.RESET_ALL}")
                return bucket_name
            else:
                print(f"{Fore.RED}❌ {self.get_message('errors.s3_bucket_not_found')}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}💡 {self.get_message('help.run_provisioning_script')}{Style.RESET_ALL}")
                return None
                
        except Exception as e:
            print(f"{Fore.RED}❌ {self.get_message('errors.s3_bucket_lookup_failed', str(e))}{Style.RESET_ALL}")
            return None

    def get_iam_role_from_provisioning(self):
        """Retrieve or create IAM role for bulk provisioning operations"""
        try:
            # Check for provisioning script configuration
            role_arn = os.getenv('IOT_WORKSHOP_ROLE_ARN')
            
            if role_arn:
                print(f"{Fore.GREEN}✅ Using role from environment: {role_arn.split('/')[-1]}{Style.RESET_ALL}")
                return role_arn
            
            # Try to find or create the standard IoT Jobs role
            role_name = f"IoTJobsRole-{self.region}-{self.account_id[:8]}"
            
            try:
                # First, try to get the existing role
                response = self.safe_api_call(
                    self.iam_client.get_role,
                    "Get IAM Role",
                    role_name,
                    debug=self.debug_mode,
                    RoleName=role_name
                )
                
                if response:
                    role_arn = response['Role']['Arn']
                    print(f"{Fore.GREEN}✅ Found existing IoT Jobs role: {role_name}{Style.RESET_ALL}")
                    return role_arn
                    
            except Exception:
                # Role doesn't exist, create it
                print(f"{Fore.YELLOW}📝 Creating IoT Jobs role: {role_name}{Style.RESET_ALL}")
                
                trust_policy = {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Principal": {"Service": "iot.amazonaws.com"},
                            "Action": "sts:AssumeRole"
                        }
                    ]
                }
                
                response = self.safe_api_call(
                    self.iam_client.create_role,
                    "Create IAM Role",
                    role_name,
                    debug=self.debug_mode,
                    RoleName=role_name,
                    AssumeRolePolicyDocument=json.dumps(trust_policy),
                    MaxSessionDuration=14400  # 4 hours
                )
                
                if response:
                    role_arn = response['Role']['Arn']
                    print(f"{Fore.GREEN}✅ {self.get_message('status.created_iot_jobs_role', role_name)}{Style.RESET_ALL}")
                    
                    # Apply workshop tags to the role
                    tag_success = apply_workshop_tags(
                        client=self.iam_client,
                        resource_arn=role_arn,
                        resource_type='iam-role',
                        script_name='manage-bulk-provisioning'
                    )
                    
                    if self.debug_mode:
                        if tag_success:
                            print(f"{Fore.GREEN}{self.get_message('status.workshop_tags_applied_to_role')}{Style.RESET_ALL}")
                        else:
                            print(f"{Fore.YELLOW}{self.get_message('status.could_not_apply_tags_to_role')}{Style.RESET_ALL}")
                    
                    # Create and attach the S3 policy for IoT Jobs (same as provision_script.py)
                    self._create_and_attach_s3_policy(role_name)
                    
                    return role_arn
                else:
                    print(f"{Fore.RED}{self.get_message('status.failed_to_create_iot_jobs_role')}{Style.RESET_ALL}")
                    return None
                
        except Exception as e:
            print(f"{Fore.RED}❌ Error in get_iam_role_from_provisioning: {str(e)}{Style.RESET_ALL}")
            return None

    def ensure_iam_role_has_bulk_provisioning_permissions(self, role_arn):
        """Ensure the IAM role has the necessary permissions for bulk provisioning operations"""
        try:
            # Extract role name from ARN
            role_name = role_arn.split('/')[-1]
            
            print(f"{Fore.CYAN}{self.get_message('status.checking_iam_permissions', role_name)}{Style.RESET_ALL}")
            
            # Check if the role already has a bulk provisioning policy
            bulk_policy_name = "BulkProvisioningIAMPolicy"
            
            existing_policy = self.safe_api_call(
                self.iam_client.get_role_policy,
                "Get Role Policy",
                f"{role_name}/{bulk_policy_name}",
                debug=self.debug_mode,
                RoleName=role_name,
                PolicyName=bulk_policy_name
            )
            
            if existing_policy is not None:
                print(f"{Fore.GREEN}{self.get_message('status.iam_has_permissions')}{Style.RESET_ALL}")
                return True
            else:
                # Policy doesn't exist, create it
                print(f"{Fore.YELLOW}{self.get_message('status.adding_bulk_provisioning_permissions')}{Style.RESET_ALL}")
                
                # Create IAM policy document for bulk provisioning operations
                bulk_provisioning_policy = {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Action": [
                                "iot:RegisterThing",
                                "iot:CreateCertificateFromCsr"
                            ],
                            "Resource": "*"
                        },
                        {
                            "Effect": "Allow",
                            "Action": [
                                "iot:CreateThing",
                                "iot:CreateThingType",
                                "iot:DescribeThing",
                                "iot:DescribeThingType",
                                "iot:ListThings",
                                "iot:ListThingTypes",
                                "iot:UpdateThing",
                                "iot:CreateKeysAndCertificate",
                                "iot:DescribeCertificate",
                                "iot:AttachThingPrincipal",
                                "iot:AttachPrincipalPolicy",
                                "iot:DetachThingPrincipal",
                                "iot:DetachPrincipalPolicy",
                                "iot:ListPrincipalPolicies",
                                "iot:ListPolicyPrincipals"
                            ],
                            "Resource": f"arn:aws:iot:{self.region}:{self.account_id}:*"
                        },
                        {
                            "Effect": "Allow",
                            "Action": [
                                "s3:GetObject",
                                "s3:PutObject",
                                "s3:GetObjectVersion"
                            ],
                            "Resource": f"arn:aws:s3:::iot-firmware-{self.region}-*/*"
                        }
                    ]
                }
                
                # Attach the policy to the role
                response = self.safe_api_call(
                    self.iam_client.put_role_policy,
                    "Put Role Policy",
                    f"{role_name}/{bulk_policy_name}",
                    debug=self.debug_mode,
                    RoleName=role_name,
                    PolicyName=bulk_policy_name,
                    PolicyDocument=json.dumps(bulk_provisioning_policy)
                )
                
                if response is not None:
                    print(f"{Fore.GREEN}{self.get_message('status.iam_permissions_added')}{Style.RESET_ALL}")
                    return True
                else:
                    print(f"{Fore.RED}{self.get_message('status.failed_add_bulk_provisioning_permissions')}{Style.RESET_ALL}")
                    return False
                    
        except Exception as e:
            print(f"{Fore.RED}{self.get_message('errors.error_ensuring_iam_permissions', str(e))}{Style.RESET_ALL}")
            return False

    def _create_and_attach_s3_policy(self, role_name):
        """Create and attach S3 policy to the IoT Jobs role (same as provision_script.py)"""
        try:
            policy_name = "IoTJobsS3Policy"
            
            # Check if policy is already attached
            try:
                self.iam_client.get_role_policy(RoleName=role_name, PolicyName=policy_name)
                if self.debug_mode:
                    print(f"{Fore.GREEN}{self.get_message('status.s3_policy_already_attached_to_role')}{Style.RESET_ALL}")
                return True
            except ClientError as e:
                if e.response["Error"]["Code"] != "NoSuchEntity":
                    print(f"{Fore.RED}{self.get_message('errors.error_checking_role_policy', e.response['Error']['Message'])}{Style.RESET_ALL}")
                    return False
            
            # Create and attach the S3 policy
            iot_jobs_policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": ["s3:*"],
                        "Resource": f"arn:aws:s3:::iot-firmware-{self.region}-*/*",
                        "Condition": {
                            "StringEquals": {"aws:RequestedRegion": self.region},
                            "Bool": {"aws:SecureTransport": "true"},
                        },
                    },
                    {
                        "Effect": "Allow",
                        "Action": ["iot:*"],
                        "Resource": f"arn:aws:iot:{self.region}:{self.account_id}:*/*",
                    }
                ],
            }
            
            response = self.safe_api_call(
                self.iam_client.put_role_policy,
                "Attach S3 Policy to Role",
                f"{role_name}/{policy_name}",
                debug=self.debug_mode,
                RoleName=role_name,
                PolicyName=policy_name,
                PolicyDocument=json.dumps(iot_jobs_policy)
            )
            
            if response is not None:
                print(f"{Fore.GREEN}{self.get_message('status.s3_policy_attached')}{Style.RESET_ALL}")
                return True
            else:
                print(f"{Fore.RED}{self.get_message('errors.failed_attach_s3_policy')}{Style.RESET_ALL}")
                return False
                
        except Exception as e:
            print(f"{Fore.RED}{self.get_message('errors.error_creating_s3_policy', str(e))}{Style.RESET_ALL}")
            return False

    def load_provisioning_template(self):
        """Load and parse provisioning template from iot_helpers"""
        try:
            template_path = os.path.join(repo_root, "iot_helpers", "utils", "bulk_provisioning_template.json")
            with open(template_path, 'r') as f:
                template = json.load(f)
            
            if self.debug_mode:
                print(f"{Fore.GREEN}{self.get_message('status.provisioning_template_loaded')}{Style.RESET_ALL}")
                print(self.get_message("debug.template_parameters", list(template.get('Parameters', {}).keys())))
                print(self.get_message("debug.template_resources", list(template.get('Resources', {}).keys())))
            
            return template
        except FileNotFoundError:
            print(f"{Fore.RED}❌ {self.get_message('errors.template_file_not_found')}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}💡 {self.get_message('help.template_file_location')}{Style.RESET_ALL}")
            return None
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}❌ {self.get_message('errors.template_json_invalid', str(e))}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}💡 {self.get_message('help.template_json_validation')}{Style.RESET_ALL}")
            return None
        except PermissionError:
            print(f"{Fore.RED}❌ {self.get_message('errors.template_permission_denied')}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}💡 {self.get_message('help.template_permissions')}{Style.RESET_ALL}")
            return None
        except Exception as e:
            print(f"{Fore.RED}❌ {self.get_message('errors.template_load_failed', str(e))}{Style.RESET_ALL}")
            return None

    def load_input_template(self):
        """Load input file template"""
        try:
            template_path = os.path.join(repo_root, "iot_helpers", "utils", "bulk_registration_input.json")
            with open(template_path, 'r') as f:
                template = json.loads(f.read())
            
            if self.debug_mode:
                print(f"{Fore.GREEN}{self.get_message('status.input_template_loaded')}{Style.RESET_ALL}")
                print(self.get_message("debug.input_template_keys", list(template.keys())))
            
            return template
        except Exception as e:
            print(f"{Fore.RED}{self.get_message('errors.error_loading_input_template', e)}{Style.RESET_ALL}")
            return None



    def generate_device_credentials(self, device_name):
        """Generate private key and CSR using OpenSSL"""
        import tempfile
        import os
        import shutil
        
        temp_dir = tempfile.mkdtemp()
        key_file = os.path.join(temp_dir, f"{device_name}.key")
        csr_file = os.path.join(temp_dir, f"{device_name}.csr")
        
        try:
            if self.debug_mode:
                print(f"{Fore.CYAN}{self.get_message('status.generating_credentials_for', device_name)}{Style.RESET_ALL}")
            
            # Generate private key (2048-bit RSA)
            key_result = subprocess.run([
                "openssl", "genrsa", "-out", key_file, "2048"
            ], capture_output=True, text=True, check=True)
            
            if self.debug_mode:
                print(self.get_message("debug.private_key_generated", key_file))
            
            # Set secure permissions on private key (600 - owner read/write only)
            os.chmod(key_file, 0o600)
            
            # Generate CSR with proper device identification
            csr_result = subprocess.run([
                "openssl", "req", "-new", "-key", key_file,
                "-out", csr_file, "-subj", f"/CN={device_name}/O=AWS IoT Workshop/C=US"
            ], capture_output=True, text=True, check=True)
            
            if self.debug_mode:
                print(self.get_message("debug.csr_generated", csr_file))
            
            # Read CSR content
            with open(csr_file, "r") as f:
                csr_content = f.read().strip()
            
            if self.debug_mode:
                print(self.get_message("debug.csr_length", len(csr_content)))
            
            return csr_content
            
        except subprocess.CalledProcessError as e:
            error_msg = f"OpenSSL command failed: {e.stderr if e.stderr else str(e)}"
            print(f"{Fore.RED}❌ {self.get_message('errors.openssl_failed', device_name, error_msg)}{Style.RESET_ALL}")
            
            # Provide specific troubleshooting guidance
            if "permission denied" in str(e).lower():
                print(f"{Fore.CYAN}💡 {self.get_message('help.openssl_permissions')}{Style.RESET_ALL}")
            elif "no such file" in str(e).lower():
                print(f"{Fore.CYAN}💡 {self.get_message('help.openssl_path')}{Style.RESET_ALL}")
            else:
                print(f"{Fore.CYAN}💡 {self.get_message('help.openssl_general')}{Style.RESET_ALL}")
            
            return None
            
        except FileNotFoundError:
            print(f"{Fore.RED}❌ {self.get_message('errors.openssl_not_found')}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}💡 {self.get_message('help.install_openssl')}{Style.RESET_ALL}")
            return None
            
        except Exception as e:
            print(f"{Fore.RED}❌ {self.get_message('errors.credential_generation_failed', device_name, str(e))}{Style.RESET_ALL}")
            return None
            
        finally:
            # Secure cleanup of temporary files
            self.cleanup_temp_files([key_file, csr_file, temp_dir])

    def cleanup_temp_files(self, file_paths):
        """Securely delete temporary credential files"""
        import shutil
        
        for file_path in file_paths:
            try:
                if os.path.isfile(file_path):
                    # Overwrite file with zeros before deletion for security
                    with open(file_path, "r+b") as f:
                        length = f.seek(0, 2)  # Get file length
                        f.seek(0)
                        f.write(b'\x00' * length)  # Overwrite with zeros
                    os.remove(file_path)
                    
                    if self.debug_mode:
                        print(self.get_message("debug.securely_deleted", file_path))
                        
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                    
                    if self.debug_mode:
                        print(self.get_message("debug.removed_directory", file_path))
                        
            except Exception as e:
                if self.debug_mode:
                    print(self.get_message("debug.cleanup_warning", file_path, e))

    def test_openssl_availability(self):
        """Test if OpenSSL is available and working"""
        try:
            result = subprocess.run(
                ["openssl", "version"], 
                capture_output=True, 
                text=True, 
                check=True
            )
            
            if self.debug_mode:
                print(f"{Fore.GREEN}{self.get_message('status.openssl_available', result.stdout.strip())}{Style.RESET_ALL}")
            
            return True
            
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"{Fore.RED}{self.get_message('errors.openssl_not_available')}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{self.get_message('help.install_openssl')}{Style.RESET_ALL}")
            return False

    def check_task_results(self):
        """Check results and failures of a bulk registration task"""
        print(f"\n{Fore.BLUE}📊 {self.get_message('ui.check_results')}{Style.RESET_ALL}\n")

        task_id = input(f"{Fore.YELLOW}{self.get_message('prompts.task_id_input')}{Style.RESET_ALL}").strip()

        if not task_id:
            print(f"{Fore.RED}{self.get_message('errors.task_id_empty')}{Style.RESET_ALL}")
            return

        # Get both success and error reports
        success_reports = []
        failure_reports = []
        
        # Get RESULTS report (successful registrations)
        results_response = self.safe_api_call(
            self.iot_client.list_thing_registration_task_reports,
            "List Thing Registration Task Reports (Results)",
            task_id,
            debug=self.debug_mode,
            taskId=task_id,
            reportType="RESULTS",
            maxResults=50
        )
        
        if results_response:
            success_reports = results_response.get("resourceLinks", [])
        
        # Get ERRORS report (failed registrations)
        errors_response = self.safe_api_call(
            self.iot_client.list_thing_registration_task_reports,
            "List Thing Registration Task Reports (Errors)",
            task_id,
            debug=self.debug_mode,
            taskId=task_id,
            reportType="ERRORS",
            maxResults=50
        )
        
        if errors_response:
            failure_reports = errors_response.get("resourceLinks", [])

        if not success_reports and not failure_reports:
            print(f"{Fore.YELLOW}{self.get_message('results.no_results_yet')}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{self.get_message('results.check_later')}{Style.RESET_ALL}")
            return

        # Display success results with content preview
        if success_reports:
            print(f"{Fore.GREEN}✅ {self.get_message('ui.successful_registrations', len(success_reports))}{Style.RESET_ALL}")
            for i, report_url in enumerate(success_reports[:3], 1):  # Show first 3 with content
                print(f"{Fore.GREEN}  {i}. {report_url}{Style.RESET_ALL}")
                
                # Download and display report content
                success_content = self._download_report_content(report_url)
                if success_content:
                    self._display_success_report_content(success_content, max_entries=5)
                else:
                    print(f"    {Fore.YELLOW}{self.get_message('ui.report_download_failed')}{Style.RESET_ALL}")
                print()  # Add spacing between reports
            
            if len(success_reports) > 3:
                print(f"{Fore.CYAN}  {self.get_message('reports.more_success_reports', len(success_reports) - 3)}{Style.RESET_ALL}")

        # Display failure results with content preview
        if failure_reports:
            print(f"\n{Fore.RED}❌ {self.get_message('ui.failed_registrations', len(failure_reports))}{Style.RESET_ALL}")
            for i, report_url in enumerate(failure_reports[:3], 1):  # Show first 3 with content
                print(f"{Fore.RED}  {i}. {report_url}{Style.RESET_ALL}")
                
                # Download and display report content
                error_content = self._download_report_content(report_url)
                if error_content:
                    self._display_error_report_content(error_content, max_entries=5)
                else:
                    print(f"    {Fore.YELLOW}{self.get_message('ui.report_download_failed')}{Style.RESET_ALL}")
                print()  # Add spacing between reports
            
            if len(failure_reports) > 3:
                print(f"{Fore.CYAN}  {self.get_message('reports.more_error_reports', len(failure_reports) - 3)}{Style.RESET_ALL}")
            
            print(f"\n{Fore.CYAN}{self.get_message('ui.troubleshooting_guidance')}{Style.RESET_ALL}")

        # Educational pause about task results
        self.educational_pause(
            self.get_message("learning.task_results_title"),
            self.get_message("learning.task_results_description")
        )

    def _download_report_content(self, s3_url):
        """Download and parse report content from S3 URL"""
        try:
            # Parse S3 URL to extract bucket and key
            # Handle various S3 URL formats including signed URLs with query parameters
            import re
            from urllib.parse import urlparse, parse_qs
            
            # Remove query parameters first (for signed URLs)
            base_url = s3_url.split('?')[0]
            
            # Try different S3 URL formats
            patterns = [
                r'https://s3\.amazonaws\.com/([^/]+)/(.+)',  # https://s3.amazonaws.com/bucket/key
                r'https://([^.]+)\.s3\.amazonaws\.com/(.+)',  # https://bucket.s3.amazonaws.com/key
                r'https://s3\.([^.]+)\.amazonaws\.com/([^/]+)/(.+)',  # https://s3.region.amazonaws.com/bucket/key
                r'https://([^.]+)\.s3\.([^.]+)\.amazonaws\.com/(.+)',  # https://bucket.s3.region.amazonaws.com/key
            ]
            
            bucket_name = None
            key_name = None
            
            for pattern in patterns:
                match = re.match(pattern, base_url)
                if match:
                    groups = match.groups()
                    if len(groups) == 2:
                        bucket_name, key_name = groups
                    elif len(groups) == 3:
                        if 's3.' in pattern and 'amazonaws.com' in pattern:
                            # Pattern: https://s3.region.amazonaws.com/bucket/key
                            bucket_name, key_name = groups[1], groups[2]
                        else:
                            # Pattern: https://bucket.s3.region.amazonaws.com/key
                            bucket_name, key_name = groups[0], groups[2]
                    break
            
            if not bucket_name or not key_name:
                if self.debug_mode:
                    print(f"{Fore.YELLOW}{self.get_message('reports.parse_url_error', s3_url)}{Style.RESET_ALL}")
                    print(f"{Fore.YELLOW}     {self.get_message('reports.base_url_info', base_url)}{Style.RESET_ALL}")
                return None
            
            if self.debug_mode:
                print(f"{Fore.CYAN}{self.get_message('reports.downloading_report', bucket_name, key_name)}{Style.RESET_ALL}")
            
            # For signed URLs, use direct HTTP request instead of S3 API
            if '?' in s3_url and 'X-Amz-Signature' in s3_url:
                # This is a signed URL, use it directly
                import urllib.request
                import urllib.error
                
                if self.debug_mode:
                    print(f"{Fore.CYAN}{self.get_message('reports.using_signed_url')}{Style.RESET_ALL}")
                
                try:
                    with urllib.request.urlopen(s3_url) as response:
                        content = response.read().decode('utf-8')
                        return content
                except urllib.error.HTTPError as e:
                    if self.debug_mode:
                        print(f"{Fore.YELLOW}{self.get_message('reports.http_error', e.code, e.reason)}{Style.RESET_ALL}")
                    return None
                except urllib.error.URLError as e:
                    if self.debug_mode:
                        print(f"{Fore.YELLOW}{self.get_message('reports.url_error', e.reason)}{Style.RESET_ALL}")
                    return None
            else:
                # Regular S3 URL, use S3 client
                response = self.safe_api_call(
                    self.s3_client.get_object,
                    "S3 Get Object",
                    key_name,
                    debug=False,  # Don't show full debug for report downloads
                    Bucket=bucket_name,
                    Key=key_name
                )
                
                if response:
                    content = response['Body'].read().decode('utf-8')
                    return content
                else:
                    return None
                
        except Exception as e:
            if self.debug_mode:
                print(f"{Fore.YELLOW}{self.get_message('reports.download_failed', str(e))}{Style.RESET_ALL}")
            return None

    def _display_success_report_content(self, content, max_entries=5):
        """Display success report content with masked certificate data"""
        try:
            lines = content.strip().split('\n')
            
            print(f"    {Fore.GREEN}{self.get_message('reports.success_preview', min(len(lines), max_entries), len(lines))}{Style.RESET_ALL}")
            
            for i, line in enumerate(lines[:max_entries]):
                if not line.strip():
                    continue
                    
                try:
                    entry = json.loads(line)
                    
                    # Handle actual AWS IoT success report format
                    if 'response' in entry and 'ResourceArns' in entry['response']:
                        # AWS IoT bulk registration success format
                        line_number = entry.get('lineNumber', i + 1)
                        response = entry.get('response', {})
                        resource_arns = response.get('ResourceArns', {})
                        
                        # Extract device information
                        thing_arn = resource_arns.get('thing', 'Unknown')
                        cert_arn = resource_arns.get('certificate', 'Unknown')
                        policy_arn = resource_arns.get('policy', 'Unknown')
                        
                        # Extract thing name from thing ARN
                        thing_name = thing_arn.split('/')[-1] if thing_arn != 'Unknown' else f"Device #{line_number}"
                        
                        # Mask certificate ARN for security (show first/last parts)
                        if cert_arn != 'Unknown' and len(cert_arn) > 20:
                            masked_cert = f"{cert_arn[:25]}****{cert_arn[-10:]}"
                        else:
                            masked_cert = cert_arn
                        
                        # Mask certificate PEM data completely for security
                        cert_pem = response.get('CertificatePem', '')
                        if cert_pem:
                            cert_preview = "-----BEGIN CERTIFICATE-----\n[CERTIFICATE DATA MASKED FOR SECURITY]\n-----END CERTIFICATE-----"
                        else:
                            cert_preview = "No certificate data"
                        
                        print(f"    {Fore.GREEN}  {i+1}. {self.get_message('reports.device_label', thing_name)}{Style.RESET_ALL}")
                        print(f"    {Fore.GREEN}     {self.get_message('reports.certificate_arn_label', masked_cert)}{Style.RESET_ALL}")
                        print(f"    {Fore.GREEN}     {self.get_message('reports.thing_arn_label', thing_arn)}{Style.RESET_ALL}")
                        print(f"    {Fore.GREEN}     {self.get_message('reports.certificate_label', cert_preview)}{Style.RESET_ALL}")
                        
                    else:
                        # Legacy format (thingName, certificateArn, thingArn)
                        thing_name = entry.get('thingName', 'Unknown')
                        cert_arn = entry.get('certificateArn', 'Unknown')
                        thing_arn = entry.get('thingArn', 'Unknown')
                        
                        # Mask certificate ARN for security (show first/last parts)
                        if cert_arn != 'Unknown' and len(cert_arn) > 20:
                            masked_cert = f"{cert_arn[:25]}****{cert_arn[-10:]}"
                        else:
                            masked_cert = cert_arn
                        
                        print(f"    {Fore.GREEN}  {i+1}. {self.get_message('reports.device_label', thing_name)}{Style.RESET_ALL}")
                        print(f"    {Fore.GREEN}     {self.get_message('reports.certificate_arn_label', masked_cert)}{Style.RESET_ALL}")
                        print(f"    {Fore.GREEN}     {self.get_message('reports.thing_arn_label', thing_arn)}{Style.RESET_ALL}")
                    
                except json.JSONDecodeError:
                    # Handle non-JSON lines
                    print(f"    {Fore.GREEN}  {i+1}. {line[:100]}{'...' if len(line) > 100 else ''}{Style.RESET_ALL}")
            
            if len(lines) > max_entries:
                print(f"    {Fore.CYAN}     {self.get_message('reports.more_success', len(lines) - max_entries)}{Style.RESET_ALL}")
                
        except Exception as e:
            print(f"    {Fore.YELLOW}{self.get_message('reports.parse_error', 'success', str(e))}{Style.RESET_ALL}")

    def _display_error_report_content(self, content, max_entries=5):
        """Display error report content with failure details"""
        try:
            lines = content.strip().split('\n')
            
            print(f"    {Fore.RED}{self.get_message('reports.error_preview', min(len(lines), max_entries), len(lines))}{Style.RESET_ALL}")
            
            for i, line in enumerate(lines[:max_entries]):
                if not line.strip():
                    continue
                    
                try:
                    entry = json.loads(line)
                    
                    # Handle actual AWS IoT error report format
                    if 'errorMessage' in entry and 'lineNumber' in entry:
                        # AWS IoT bulk registration error format
                        line_number = entry.get('lineNumber', i + 1)
                        error_message = entry.get('errorMessage', 'No details available')
                        
                        # Extract device name from line number (line numbers are 1-based)
                        device_name = f"Device #{line_number}"
                        
                        # Parse error code and details from error message
                        error_code = "ResourceRegistrationFailureException"
                        error_details = error_message
                        
                        # Try to extract more specific error information
                        if "Thing Type" in error_message and "not found" in error_message:
                            error_code = "ThingTypeNotFound"
                            # Extract thing type from error message
                            import re
                            thing_type_match = re.search(r'Thing Type ([^:]+):([^\s]+)', error_message)
                            if thing_type_match:
                                account_id = thing_type_match.group(1)
                                thing_type = thing_type_match.group(2)
                                error_details = f"Thing Type '{thing_type}' not found in account {account_id}"
                        elif "ResourceAlreadyExistsException" in error_message:
                            error_code = "ResourceAlreadyExists"
                            error_details = "Device name already exists"
                        elif "InvalidRequestException" in error_message:
                            error_code = "InvalidRequest"
                            error_details = "Invalid CSR or request format"
                        
                        print(f"    {Fore.RED}  {i+1}. {device_name}{Style.RESET_ALL}")
                        print(f"    {Fore.RED}     {self.get_message('reports.error_label', error_code)}{Style.RESET_ALL}")
                        print(f"    {Fore.RED}     {self.get_message('reports.details_label', error_details[:100] + ('...' if len(error_details) > 100 else ''))}{Style.RESET_ALL}")
                        
                    else:
                        # Legacy format (thingName, errorCode, errorMessage)
                        thing_name = entry.get('thingName', 'Unknown')
                        error_code = entry.get('errorCode', 'Unknown')
                        error_message = entry.get('errorMessage', 'No details available')
                        
                        print(f"    {Fore.RED}  {i+1}. {self.get_message('reports.device_label', thing_name)}{Style.RESET_ALL}")
                        print(f"    {Fore.RED}     {self.get_message('reports.error_label', error_code)}{Style.RESET_ALL}")
                        print(f"    {Fore.RED}     {self.get_message('reports.details_label', error_message[:100] + ('...' if len(error_message) > 100 else ''))}{Style.RESET_ALL}")
                    
                except json.JSONDecodeError:
                    # Handle non-JSON lines
                    print(f"    {Fore.RED}  {i+1}. {line[:100]}{'...' if len(line) > 100 else ''}{Style.RESET_ALL}")
            
            if len(lines) > max_entries:
                print(f"    {Fore.CYAN}     {self.get_message('reports.more_errors', len(lines) - max_entries)}{Style.RESET_ALL}")
                
        except Exception as e:
            print(f"    {Fore.YELLOW}{self.get_message('reports.parse_error', 'error', str(e))}{Style.RESET_ALL}")

    def run(self):
        """Main execution flow"""
        self.print_header()

        # Get debug mode preference
        self.get_debug_mode()

        while True:
            # Get operation choice
            operation = self.get_operation_choice()

            if operation == 1:
                self.list_registration_tasks()
            elif operation == 2:
                self.describe_registration_task()
            elif operation == 3:
                self.register_things_bulk()
            elif operation == 4:
                self.check_task_results()

            # Ask if user wants to continue
            print(f"\n{Fore.CYAN}{self.get_message('ui.separator_line')}{Style.RESET_ALL}")
            continue_choice = (
                input(f"{Fore.YELLOW}{self.get_message('prompts.continue_operation')}{Style.RESET_ALL}").strip().lower()
            )
            if continue_choice in ["n", "no"]:
                print(f"\n{Fore.GREEN}{self.get_message('ui.goodbye')}{Style.RESET_ALL}")
                break
            print()  # Add spacing before next operation


if __name__ == "__main__":
    # Get user's preferred language
    USER_LANG = get_language()

    # Load messages for this script and language
    messages = load_messages("manage_bulk_provisioning", USER_LANG)

    manager = BulkProvisioningManager()
    try:
        manager.run()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}{manager.get_message('ui.cancelled')}{Style.RESET_ALL}")
        sys.exit(0)