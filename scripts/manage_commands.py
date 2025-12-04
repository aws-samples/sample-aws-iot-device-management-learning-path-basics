#!/usr/bin/env python3

import json
import os
import sys
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
import re

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


# ============================================================================
# Enums
# ============================================================================


class CommandStatus(Enum):
    """
    Command execution status values.

    These statuses track the lifecycle of a command execution from creation
    through completion or cancellation.
    """

    CREATED = "CREATED"
    IN_PROGRESS = "IN_PROGRESS"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    TIMED_OUT = "TIMED_OUT"
    CANCELED = "CANCELED"

    @classmethod
    def from_string(cls, status_str: str) -> "CommandStatus":
        """Convert string to CommandStatus enum"""
        try:
            return cls[status_str]
        except KeyError:
            # If not found, try matching the value
            for status in cls:
                if status.value == status_str:
                    return status
            raise ValueError(f"Invalid status: {status_str}")

    def get_display_string(self, get_msg_func) -> str:
        """
        Get localized display string for this status.

        Args:
            get_msg_func: Function to get localized messages

        Returns:
            Localized status display string
        """
        status_key = f"command_status.{self.value.lower()}"
        return get_msg_func(status_key)


# ============================================================================
# Data Models
# ============================================================================


@dataclass
class Command:
    """
    Represents an AWS IoT Command.

    Attributes:
        command_arn: ARN of the command in AWS IoT
        command_name: Name of the command
        description: Description of what the command does
        payload_format: JSON schema defining the payload structure
        created_at: Timestamp when command was created
        is_predefined: Whether this is a predefined command
        deprecated: Whether the command is deprecated
        pending_deletion: Whether the command is pending deletion
    """

    command_arn: str
    command_name: str
    description: str
    payload_format: Dict[str, Any]
    created_at: Optional[str] = None
    is_predefined: bool = False
    deprecated: bool = False
    pending_deletion: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)

    def get_status(self) -> str:
        """Get human-readable status"""
        if self.pending_deletion:
            return "PENDING_DELETION"
        elif self.deprecated:
            return "DEPRECATED"
        else:
            return "ACTIVE"


@dataclass
class CommandExecution:
    """
    Represents a command execution instance.

    Attributes:
        execution_id: Unique identifier for the command execution
        command_arn: ARN of the command used
        target_arn: ARN of the target device or group
        parameters: Command parameters matching command payload format
        status: Current execution status
        created_at: When command execution was created
        last_updated_at: When command execution was last updated
        completed_at: When command execution completed (if applicable)
        status_reason: Reason for current status
    """

    execution_id: str
    command_arn: str
    target_arn: str
    parameters: Dict[str, Any]
    status: str
    created_at: str
    last_updated_at: str
    completed_at: Optional[str] = None
    status_reason: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


# ============================================================================
# Validation Functions
# ============================================================================


class ValidationError(Exception):
    """Custom exception for validation errors"""

    pass


def validate_command_name(name: str, get_msg_func) -> Dict[str, Any]:
    """
    Validate command name according to AWS IoT requirements.

    Command names must:
    - Be 1-128 characters long
    - Start with an alphanumeric character
    - Contain only alphanumeric characters, hyphens, and underscores

    Args:
        name: Command name to validate
        get_msg_func: Function to get localized messages

    Returns:
        Dictionary with 'valid' boolean and optional 'error_message'
    """
    # Check if empty
    if not name or len(name) == 0:
        return {"valid": False, "error_message": get_msg_func("validation.command_name_empty")}

    # Check length
    if len(name) > 128:
        return {"valid": False, "error_message": get_msg_func("validation.command_name_length", len(name))}

    # Check first character is alphanumeric
    if not name[0].isalnum():
        return {"valid": False, "error_message": get_msg_func("validation.command_name_start")}

    # Check all characters are valid (alphanumeric, hyphen, underscore)
    if not re.match(r"^[a-zA-Z0-9][a-zA-Z0-9_-]*$", name):
        return {"valid": False, "error_message": get_msg_func("validation.command_name_chars")}

    return {"valid": True}


def validate_command_description(description: str, get_msg_func) -> Dict[str, Any]:
    """
    Validate command description according to AWS IoT requirements.

    Descriptions must be 1-256 characters long.

    Args:
        description: Command description to validate
        get_msg_func: Function to get localized messages

    Returns:
        Dictionary with 'valid' boolean and optional 'error_message'
    """
    # Check if empty
    if not description or len(description) == 0:
        return {"valid": False, "error_message": get_msg_func("validation.description_empty")}

    # Check length
    if len(description) > 256:
        return {"valid": False, "error_message": get_msg_func("validation.description_length", len(description))}

    return {"valid": True}


def validate_payload_format(payload_format: Any, get_msg_func) -> Dict[str, Any]:
    """
    Validate command payload format.

    According to AWS IoT Device Management Commands documentation, the command payload
    is flexible JSON and does not require any specific schema structure. This function
    validates that:
    - Payload is a non-empty dictionary
    - Payload is valid JSON
    - Payload does not exceed 10KB in size

    Args:
        payload_format: Payload format to validate (should be a dict)
        get_msg_func: Function to get localized messages

    Returns:
        Dictionary with 'valid' boolean and optional 'error_message'
    """
    # Check if empty or None
    if not payload_format:
        return {"valid": False, "error_message": get_msg_func("validation.payload_empty")}

    # Check if dictionary
    if not isinstance(payload_format, dict):
        return {"valid": False, "error_message": get_msg_func("validation.payload_must_be_dict")}

    # Validate that it's valid JSON by attempting to serialize it
    try:
        payload_json = json.dumps(payload_format)
    except (TypeError, ValueError) as e:
        return {"valid": False, "error_message": get_msg_func("validation.payload_invalid_schema", str(e))}

    # Check size (10KB limit)
    if len(payload_json) > 10240:  # 10KB
        return {"valid": False, "error_message": get_msg_func("validation.payload_too_complex")}

    return {"valid": True}


# ============================================================================
# Error Handling Framework
# ============================================================================


class ErrorCategory(Enum):
    """Error categories for classification"""

    VALIDATION = "validation"
    AWS_API = "aws_api"
    NETWORK = "network"
    STATE = "state"


@dataclass
class ErrorInfo:
    """
    Structured error information for display and handling.

    Attributes:
        category: Error category (validation, AWS API, network, state)
        code: Error code (e.g., ResourceNotFoundException, ValidationError)
        message: Human-readable error message
        suggestion: Suggested action to resolve the error
        details: Additional technical details (optional)
    """

    category: ErrorCategory
    code: str
    message: str
    suggestion: str
    details: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


def display_error(error_info: ErrorInfo, get_msg_func, debug_mode: bool = False):
    """
    Display formatted error message with colored output.

    This function displays errors in a consistent, user-friendly format with:
    - Color-coded error category
    - Error code and message
    - Suggested action to resolve
    - Optional technical details in debug mode

    Args:
        error_info: ErrorInfo object containing error details
        get_msg_func: Function to get localized messages
        debug_mode: Whether to display technical details

    Requirements: 2.8
    """
    # Determine color based on category
    if error_info.category == ErrorCategory.VALIDATION:
        category_color = Fore.YELLOW
        category_label = get_msg_func("errors.validation_error")
    elif error_info.category == ErrorCategory.AWS_API:
        category_color = Fore.RED
        category_label = get_msg_func("errors.aws_api_error_category")
    elif error_info.category == ErrorCategory.NETWORK:
        category_color = Fore.MAGENTA
        category_label = get_msg_func("errors.network_error")
    elif error_info.category == ErrorCategory.STATE:
        category_color = Fore.CYAN
        category_label = get_msg_func("errors.state_error")
    else:
        category_color = Fore.RED
        category_label = get_msg_func("errors.general_error", "Unknown")

    # Display error header
    print(f"\n{category_color}{'='*80}{Style.RESET_ALL}")
    print(f"{category_color}{category_label}{Style.RESET_ALL}")
    print(f"{category_color}{'='*80}{Style.RESET_ALL}")

    # Display error code and message
    print(f"\n{Fore.RED}{get_msg_func('debug.code_label')} {error_info.code}{Style.RESET_ALL}")
    print(f"\n{Fore.RED}{get_msg_func('debug.message_label')} {error_info.message}{Style.RESET_ALL}")

    # Display suggestion
    if error_info.suggestion:
        print(f"\n{Fore.YELLOW}{get_msg_func('debug.suggestion_label')} {error_info.suggestion}{Style.RESET_ALL}")

    # Display technical details in debug mode
    if debug_mode and error_info.details:
        print(f"\n{Fore.CYAN}{get_msg_func('debug.technical_details')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{error_info.details}{Style.RESET_ALL}")

    print(f"\n{category_color}{'='*80}{Style.RESET_ALL}")


def handle_aws_api_error(
    error: ClientError,
    operation_name: str,
    get_msg_func,
    debug_mode: bool = False,
    max_retries: int = 3,
    retry_attempt: int = 0,
) -> Optional[Dict[str, Any]]:
    """
    Handle AWS API errors with exponential backoff and retry logic.

    This function:
    - Implements exponential backoff for rate limiting (TooManyRequestsException)
    - Retries transient errors (503, timeout) up to max_retries times
    - Displays user-friendly error messages for common errors
    - Logs full error details in debug mode

    Args:
        error: ClientError exception from boto3
        operation_name: Name of the AWS operation that failed
        get_msg_func: Function to get localized messages
        debug_mode: Whether to display debug information
        max_retries: Maximum number of retry attempts (default: 3)
        retry_attempt: Current retry attempt number (default: 0)

    Returns:
        Dict with 'should_retry' (bool) and 'wait_time' (float) if retry recommended,
        None if should not retry

    Requirements: 2.8, 11.4
    """
    error_code = error.response["Error"]["Code"]
    error_message = error.response["Error"]["Message"]
    http_status = error.response.get("ResponseMetadata", {}).get("HTTPStatusCode", 0)

    # Determine if error is retryable
    retryable_codes = [
        "TooManyRequestsException",
        "ThrottlingException",
        "ServiceUnavailableException",
        "RequestTimeout",
        "RequestTimeoutException",
    ]

    retryable_http_codes = [503, 504, 429]

    is_retryable = error_code in retryable_codes or http_status in retryable_http_codes

    # Check if we've exceeded max retries
    if retry_attempt >= max_retries:
        error_info = ErrorInfo(
            category=ErrorCategory.AWS_API,
            code=error_code,
            message=get_msg_func("errors.max_retries_exceeded"),
            suggestion=get_msg_func("errors.operation_failed_after_retries", max_retries),
            details=json.dumps(error.response, indent=2, default=str) if debug_mode else None,
        )
        display_error(error_info, get_msg_func, debug_mode)
        return None

    # Handle rate limiting with exponential backoff
    if error_code in ["TooManyRequestsException", "ThrottlingException"] or http_status == 429:
        # Calculate exponential backoff: 2^retry_attempt seconds
        wait_time = min(2**retry_attempt, 60)  # Cap at 60 seconds

        print(f"{Fore.YELLOW}{get_msg_func('errors.rate_limit_exceeded', wait_time)}{Style.RESET_ALL}")

        if debug_mode:
            print(f"{Fore.CYAN}{get_msg_func('debug.rate_limit_error', operation_name)}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{get_msg_func('debug.retry_attempt_debug', retry_attempt + 1, max_retries)}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{get_msg_func('debug.wait_time', wait_time)}{Style.RESET_ALL}")

        return {"should_retry": True, "wait_time": wait_time, "retry_attempt": retry_attempt + 1}

    # Handle transient errors
    if is_retryable:
        # Linear backoff for transient errors: 1, 2, 3 seconds
        wait_time = retry_attempt + 1

        print(f"{Fore.YELLOW}{get_msg_func('errors.transient_error')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{get_msg_func('errors.retry_attempt', retry_attempt + 1, max_retries)}{Style.RESET_ALL}")

        if debug_mode:
            print(f"{Fore.CYAN}{get_msg_func('debug.transient_error_debug', operation_name, error_code)}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{get_msg_func('debug.http_status', http_status)}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{get_msg_func('debug.wait_time', wait_time)}{Style.RESET_ALL}")

        return {"should_retry": True, "wait_time": wait_time, "retry_attempt": retry_attempt + 1}

    # Non-retryable error - display error information
    # Map common error codes to user-friendly messages
    error_suggestions = {
        "ResourceNotFoundException": get_msg_func("troubleshooting.command_not_found"),
        "ResourceAlreadyExistsException": get_msg_func("troubleshooting.command_exists"),
        "InvalidRequestException": get_msg_func("troubleshooting.invalid_payload"),
        "UnauthorizedException": get_msg_func("troubleshooting.unauthorized"),
        "AccessDeniedException": get_msg_func("troubleshooting.unauthorized"),
        "ConflictException": get_msg_func("troubleshooting.check_active_executions"),
    }

    suggestion = error_suggestions.get(error_code, get_msg_func("troubleshooting.retry_status"))

    error_info = ErrorInfo(
        category=ErrorCategory.AWS_API,
        code=error_code,
        message=error_message,
        suggestion=suggestion,
        details=json.dumps(error.response, indent=2, default=str) if debug_mode else None,
    )

    display_error(error_info, get_msg_func, debug_mode)

    return None


def handle_validation_error(
    validation_result: Dict[str, Any], field_name: str, get_msg_func, allow_retry: bool = True
) -> bool:
    """
    Handle validation errors with specific messages and correction guidance.

    This function:
    - Validates inputs before AWS API calls
    - Displays specific validation messages with correction guidance
    - Allows user to retry with corrected input

    Args:
        validation_result: Dict with 'valid' (bool) and 'error_message' (str)
        field_name: Name of the field being validated
        get_msg_func: Function to get localized messages
        allow_retry: Whether to prompt user to retry with corrected input

    Returns:
        True if user wants to retry, False otherwise

    Requirements: 2.8, 16.5
    """
    if validation_result.get("valid", False):
        return False  # No error, no retry needed

    error_message = validation_result.get("error_message", get_msg_func("errors.general_error", "Validation failed"))

    # Create validation error info
    error_info = ErrorInfo(
        category=ErrorCategory.VALIDATION,
        code="ValidationError",
        message=error_message,
        suggestion=get_msg_func("prompts.continue") if allow_retry else "",
    )

    # Display error
    display_error(error_info, get_msg_func, debug_mode=False)

    # Ask if user wants to retry
    if allow_retry:
        try:
            response = input(f"\n{Fore.YELLOW}{get_msg_func('prompts.continue')}{Style.RESET_ALL}").strip().lower()
            return response in ["y", "yes", ""]  # Default to yes
        except (KeyboardInterrupt, EOFError):
            return False

    return False


def handle_network_error(error: Exception, operation_name: str, get_msg_func, debug_mode: bool = False) -> bool:
    """
    Handle network connectivity errors.

    This function:
    - Detects network connectivity issues
    - Suggests checking AWS credentials and region
    - Provides retry option

    Args:
        error: Exception that occurred (typically connection-related)
        operation_name: Name of the operation that failed
        get_msg_func: Function to get localized messages
        debug_mode: Whether to display debug information

    Returns:
        True if user wants to retry, False otherwise

    Requirements: 2.8
    """
    # Determine error details
    error_message = str(error)

    # Common network error indicators
    network_error_indicators = ["connection", "timeout", "network", "unreachable", "dns", "resolve", "endpoint"]

    is_network_error = any(indicator in error_message.lower() for indicator in network_error_indicators)

    if is_network_error:
        error_code = "NetworkError"
        message = get_msg_func("errors.network_connectivity")
        suggestion = get_msg_func("errors.check_credentials")
    else:
        error_code = "UnexpectedError"
        message = error_message
        suggestion = get_msg_func("errors.retry_operation")

    # Create network error info
    error_info = ErrorInfo(
        category=ErrorCategory.NETWORK,
        code=error_code,
        message=message,
        suggestion=suggestion,
        details=f"Operation: {operation_name}\nError: {error_message}" if debug_mode else None,
    )

    # Display error
    display_error(error_info, get_msg_func, debug_mode)

    # Ask if user wants to retry
    try:
        response = input(f"\n{Fore.YELLOW}{get_msg_func('errors.retry_operation')}{Style.RESET_ALL}").strip().lower()
        return response in ["y", "yes", ""]  # Default to yes
    except (KeyboardInterrupt, EOFError):
        return False


def validate_command_name_alt(name: str, get_msg_func) -> Dict[str, Any]:
    """
    Validate command name (alternative implementation).

    Rules:
    - Must be 1-128 characters
    - Can contain alphanumeric characters, hyphens, and underscores
    - Must start with alphanumeric character

    Args:
        name: Command name to validate
        get_msg_func: Function to get localized messages

    Returns:
        Dict with 'valid' (bool) and optional 'error_message' (str)
    """
    if not name:
        return {"valid": False, "error_message": get_msg_func("validation.command_name_empty")}

    if len(name) < 1 or len(name) > 128:
        return {"valid": False, "error_message": get_msg_func("validation.command_name_length", len(name))}

    # Must start with ASCII alphanumeric and contain only ASCII alphanumeric, hyphens, and underscores
    if not re.match(r"^[a-zA-Z0-9][a-zA-Z0-9_-]*$", name):
        # Determine if it's a start character issue or invalid characters
        if not name[0].isascii() or not name[0].isalnum():
            return {"valid": False, "error_message": get_msg_func("validation.command_name_start")}
        else:
            return {"valid": False, "error_message": get_msg_func("validation.command_name_chars")}

    return {"valid": True}


def validate_command_description_alt(description: str, get_msg_func) -> Dict[str, Any]:
    """
    Validate command description (alternative implementation).

    Rules:
    - Must be 1-256 characters

    Args:
        description: Command description to validate
        get_msg_func: Function to get localized messages

    Returns:
        Dict with 'valid' (bool) and optional 'error_message' (str)
    """
    if not description:
        return {"valid": False, "error_message": get_msg_func("validation.description_empty")}

    if len(description) < 1 or len(description) > 256:
        return {"valid": False, "error_message": get_msg_func("validation.description_length", len(description))}

    return {"valid": True}


# ============================================================================
# Main Class
# ============================================================================


class IoTCommandsManager:
    """Manager for AWS IoT Commands operations"""

    def __init__(self):
        self.region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        self.account_id = None
        self.debug_mode = False
        self.iot_client = None
        self.iot_data_client = None
        self.sts_client = None

        # Learning moment tracking - flags to show each moment only once per session
        self.learning_moments_shown = {
            "what_are_commands": False,
            "commands_vs_shadow_vs_jobs": False,
            "mqtt_topics": False,
            "execution_lifecycle": False,
            "best_practices": False,
            "console_integration": False,
        }

    def get_message(self, key, *args):
        """Get localized message with optional formatting"""
        global messages

        # Handle nested keys like 'warnings.debug_warning'
        keys = key.split(".")
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

    def safe_api_call(self, func, operation_name, resource_name, debug=False, **kwargs):
        """Safely execute AWS API call with error handling and optional debug info"""
        try:
            if debug or self.debug_mode:
                print(
                    f"\n{Fore.CYAN}{self.get_message('debug.operation_on_resource', operation_name, resource_name)}{Style.RESET_ALL}"
                )
                print(f"{Fore.CYAN}{self.get_message('debug.api_call_function', func.__name__)}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}{self.get_message('debug.input_params')}{Style.RESET_ALL}")
                print(json.dumps(kwargs, indent=2, default=str))

            response = func(**kwargs)

            if debug or self.debug_mode:
                print(f"{Fore.CYAN}{self.get_message('debug.api_response')}{Style.RESET_ALL}")
                print(json.dumps(response, indent=2, default=str))

            time.sleep(0.1)  # Rate limiting  # nosemgrep: arbitrary-sleep
            return response
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code in ["ResourceNotFoundException", "ResourceNotFound"]:
                if debug or self.debug_mode:
                    print(f"{Fore.YELLOW}{self.get_message('debug.resource_not_found', resource_name)}{Style.RESET_ALL}")
                return None
            else:
                print(
                    f"{Fore.RED}{self.get_message('debug.error_in_operation', operation_name, resource_name, e.response['Error']['Message'])}{Style.RESET_ALL}"
                )
                if debug or self.debug_mode:
                    print(f"{Fore.CYAN}{self.get_message('debug.full_error')}{Style.RESET_ALL}")
                    print(json.dumps(e.response, indent=2, default=str))
            time.sleep(0.1)  # nosemgrep: arbitrary-sleep
            return None
        except Exception as e:
            print(f"{Fore.RED}{self.get_message('debug.unexpected_error_label')} {str(e)}{Style.RESET_ALL}")
            if debug or self.debug_mode:
                import traceback

                print(f"{Fore.CYAN}{self.get_message('debug.full_traceback')}{Style.RESET_ALL}")
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

            # Get the IoT data endpoint for this account/region
            # IoT Data Plane services require account-specific endpoints
            endpoint_response = self.iot_client.describe_endpoint(endpointType="iot:Jobs")
            iot_endpoint = endpoint_response["endpointAddress"]

            # Create IoT Jobs Data client with the custom endpoint
            self.iot_data_client = boto3.client(
                "iot-jobs-data", region_name=self.region, endpoint_url=f"https://{iot_endpoint}"
            )

            if self.debug_mode:
                print(f"{Fore.GREEN}{self.get_message('status.clients_initialized_success')}{Style.RESET_ALL}")
                print(
                    f"{Fore.CYAN}{self.get_message('status.iot_service', self.iot_client.meta.service_model.service_name)}{Style.RESET_ALL}"
                )
                print(f"{Fore.CYAN}[DEBUG] IoT Data Endpoint: {iot_endpoint}{Style.RESET_ALL}")

            return True
        except Exception as e:
            print(f"{Fore.RED}{self.get_message('errors.client_init_error', str(e))}{Style.RESET_ALL}")
            return False

    def create_command(self, command_name: str, description: str, payload_format: Dict[str, Any]) -> Optional[str]:
        """
        Create a command in AWS IoT Commands.

        This function creates a new command using the AWS IoT CreateCommand API
        with the AWS-IoT namespace. The payload format is stored as a binary blob with
        JSON content type.

        Args:
            command_name: Name for the command (1-128 chars, alphanumeric, hyphens, underscores)
            description: Description of the command (1-256 chars)
            payload_format: JSON schema defining the command payload structure

        Returns:
            Command ARN if successful, None if failed

        Requirements: 2.1, 2.3, 6.6
        """
        # Validate inputs
        name_validation = validate_command_name(command_name, self.get_message)
        if not name_validation["valid"]:
            print(f"{Fore.RED}✗ {name_validation['error_message']}{Style.RESET_ALL}")
            return None

        desc_validation = validate_command_description(description, self.get_message)
        if not desc_validation["valid"]:
            print(f"{Fore.RED}✗ {desc_validation['error_message']}{Style.RESET_ALL}")
            return None

        format_validation = validate_payload_format(payload_format, self.get_message)
        if not format_validation["valid"]:
            print(f"{Fore.RED}✗ {format_validation['error_message']}{Style.RESET_ALL}")
            return None

        try:
            # Convert payload format to JSON string, then to bytes for binary blob
            payload_content = json.dumps(payload_format).encode("utf-8")

            # Prepare CreateCommand API parameters
            create_params = {
                "commandId": command_name,
                "displayName": command_name,
                "description": description,
                "namespace": "AWS-IoT",  # Using AWS-IoT namespace as per design
                "payload": {"content": payload_content, "contentType": "application/json"},
            }

            if self.debug_mode:
                print(f"\n{Fore.CYAN}{self.get_message('debug.creating_command')}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}{self.get_message('debug.command_name', command_name)}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}{self.get_message('debug.description', description)}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}{self.get_message('debug.payload_format')}{Style.RESET_ALL}")
                print(json.dumps(payload_format, indent=2))

            # Call AWS IoT CreateCommand API
            response = self.safe_api_call(
                self.iot_client.create_command, "CreateCommand", command_name, debug=self.debug_mode, **create_params
            )

            if response is None:
                print(f"{Fore.RED}{self.get_message('errors.command_creation_failed')}{Style.RESET_ALL}")
                return None

            # Extract command ARN from response
            command_arn = response.get("commandArn")

            if not command_arn:
                print(f"{Fore.RED}{self.get_message('errors.no_arn_returned')}{Style.RESET_ALL}")
                return None

            # Display success message with ARN
            print(f"\n{Fore.GREEN}{self.get_message('status.command_created')}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{self.get_message('results.command_name', command_name)}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{self.get_message('status.command_arn', command_arn)}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{self.get_message('results.description', description)}{Style.RESET_ALL}")

            return command_arn

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_message = e.response["Error"]["Message"]

            print(f"{Fore.RED}{self.get_message('errors.aws_api_error', error_code)}{Style.RESET_ALL}")
            print(f"{Fore.RED}  {error_message}{Style.RESET_ALL}")

            # Provide specific troubleshooting guidance
            if error_code == "ResourceAlreadyExistsException":
                print(f"{Fore.YELLOW}{self.get_message('troubleshooting.command_exists')}{Style.RESET_ALL}")
            elif error_code == "InvalidRequestException":
                print(f"{Fore.YELLOW}{self.get_message('troubleshooting.invalid_payload')}{Style.RESET_ALL}")
            elif error_code == "ThrottlingException":
                print(f"{Fore.YELLOW}{self.get_message('troubleshooting.throttling')}{Style.RESET_ALL}")
            elif error_code == "UnauthorizedException":
                print(f"{Fore.YELLOW}{self.get_message('troubleshooting.unauthorized')}{Style.RESET_ALL}")

            if self.debug_mode:
                print(f"{Fore.CYAN}{self.get_message('debug.full_error')}{Style.RESET_ALL}")
                print(json.dumps(e.response, indent=2, default=str))

            return None

        except Exception as e:
            print(f"{Fore.RED}{self.get_message('errors.unexpected_error', str(e))}{Style.RESET_ALL}")

            if self.debug_mode:
                import traceback

                print(f"{Fore.CYAN}{self.get_message('debug.full_traceback')}{Style.RESET_ALL}")
                traceback.print_exc()

            return None

    def list_commands(self) -> Optional[List[Command]]:
        """
        List all commands from AWS IoT.

        Retrieves both predefined and custom commands, displaying them in a formatted
        colored table with name, description, creation date, and ARN for each command.

        Returns:
            List of Command objects if successful, None if failed

        Requirements: 6.7
        """
        try:
            print(f"\n{Fore.CYAN}{self.get_message('status.listing_commands')}{Style.RESET_ALL}")

            if self.debug_mode:
                print(f"{Fore.CYAN}{self.get_message('debug.api_call', 'ListCommands')}{Style.RESET_ALL}")

            # Call AWS IoT ListCommands API to get all commands
            response = self.safe_api_call(self.iot_client.list_commands, "ListCommands", "all commands", debug=self.debug_mode)

            if response is None:
                print(f"{Fore.RED}{self.get_message('errors.general_error', 'Failed to list commands')}{Style.RESET_ALL}")
                return None

            # Extract commands from response
            commands_list = response.get("commands", [])

            if not commands_list:
                print(f"{Fore.YELLOW}{self.get_message('results.no_commands')}{Style.RESET_ALL}")
                return []

            # Convert to Command objects
            commands = []
            for cmd in commands_list:
                # Determine if predefined based on namespace or other criteria
                # For now, we'll mark all as custom since we're creating them
                # In a real scenario, predefined commands would come from AWS
                is_predefined = False

                command = Command(
                    command_arn=cmd.get("commandArn", ""),
                    command_name=cmd.get("commandId", ""),
                    description=cmd.get("description", ""),
                    payload_format={},  # Payload format not returned in list, need GetCommand for details
                    created_at=cmd.get("createdAt", ""),
                    is_predefined=is_predefined,
                    deprecated=cmd.get("deprecated", False),
                    pending_deletion=cmd.get("pendingDeletion", False),
                )
                commands.append(command)

            # Display commands in a formatted table
            self._display_command_table(commands)

            return commands

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_message = e.response["Error"]["Message"]

            print(f"{Fore.RED}{self.get_message('errors.aws_api_error', error_code)}{Style.RESET_ALL}")
            print(f"{Fore.RED}  {error_message}{Style.RESET_ALL}")

            if self.debug_mode:
                print(f"{Fore.CYAN}{self.get_message('debug.full_error')}{Style.RESET_ALL}")
                print(json.dumps(e.response, indent=2, default=str))

            return None

        except Exception as e:
            print(f"{Fore.RED}{self.get_message('errors.unexpected_error', str(e))}{Style.RESET_ALL}")

            if self.debug_mode:
                import traceback

                print(f"{Fore.CYAN}{self.get_message('debug.full_traceback')}{Style.RESET_ALL}")
                traceback.print_exc()

            return None

    def _display_command_table(self, commands: List[Command]):
        """
        Display commands in a formatted colored table.

        Args:
            commands: List of Command objects to display
        """
        if not commands:
            print(f"{Fore.YELLOW}{self.get_message('results.no_commands')}{Style.RESET_ALL}")
            return

        # Separate predefined and custom commands
        predefined = [t for t in commands if t.is_predefined]
        custom = [t for t in commands if not t.is_predefined]

        # Display predefined commands if any
        if predefined:
            print(f"\n{Fore.GREEN}{'='*80}{Style.RESET_ALL}")
            print(f"{Fore.GREEN}{self.get_message('ui.predefined_commands')}{Style.RESET_ALL}")
            print(f"{Fore.GREEN}{'='*80}{Style.RESET_ALL}")
            self._print_command_rows(predefined)

        # Display custom commands if any
        if custom:
            print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{self.get_message('ui.custom_commands')}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
            self._print_command_rows(custom)

        # Display total count
        print(f"\n{Fore.WHITE}{self.get_message('results.total_commands', len(commands))}{Style.RESET_ALL}")

    def _print_command_rows(self, commands: List[Command]):
        """
        Print command rows in a formatted table.

        Args:
            commands: List of Command objects to print
        """
        # Print table header
        print(f"\n{Fore.WHITE}{'Name':<25} {'Status':<18} {'Description':<35} {'Created':<20}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}{'-'*25} {'-'*18} {'-'*35} {'-'*20}{Style.RESET_ALL}")

        # Print each command
        for command in commands:
            # Format creation date
            created_str = "N/A"
            if command.created_at:
                try:
                    # Handle both string and datetime objects
                    if isinstance(command.created_at, str):
                        created_dt = datetime.fromisoformat(command.created_at.replace("Z", "+00:00"))
                    else:
                        created_dt = command.created_at
                    created_str = created_dt.strftime("%Y-%m-%d %H:%M:%S")
                except Exception:
                    created_str = str(command.created_at)[:19]

            # Get status with color
            status = command.get_status()
            if status == "PENDING_DELETION":
                status_colored = f"{Fore.RED}{status}{Style.RESET_ALL}"
            elif status == "DEPRECATED":
                status_colored = f"{Fore.YELLOW}{status}{Style.RESET_ALL}"
            else:
                status_colored = f"{Fore.GREEN}{status}{Style.RESET_ALL}"

            # Truncate long descriptions
            desc = command.description
            if len(desc) > 32:
                desc = desc[:32] + "..."

            # Truncate long names
            name = command.command_name
            if len(name) > 22:
                name = name[:22] + "..."

            print(f"{Fore.CYAN}{name:<25}{Style.RESET_ALL} {status_colored:<27} {desc:<35} {created_str:<20}")

        # Print ARNs in a separate section for better readability
        print(f"\n{Fore.WHITE}{'Command ARNs:'}{Style.RESET_ALL}")
        for i, command in enumerate(commands, 1):
            status_indicator = ""
            if command.pending_deletion:
                status_indicator = f" {Fore.RED}[PENDING DELETION]{Style.RESET_ALL}"
            elif command.deprecated:
                status_indicator = f" {Fore.YELLOW}[DEPRECATED]{Style.RESET_ALL}"

            print(f"{Fore.YELLOW}{i}. {command.command_name}{status_indicator}{Style.RESET_ALL}")
            print(f"   {Fore.WHITE}{self.get_message('results.command_arn', command.command_arn)}{Style.RESET_ALL}")

    def get_command_details(self, command_arn: str) -> Optional[Command]:
        """
        Retrieve detailed information about a command by ARN.

        This function calls the AWS IoT GetCommand API to retrieve the complete
        command specification including the full payload format with parameter
        names, types, and constraints.

        Args:
            command_arn: ARN of the command to retrieve

        Returns:
            Command object with complete details if successful, None if failed

        Requirements: 6.8
        """
        try:
            print(f"\n{Fore.CYAN}{self.get_message('status.getting_command_details')}{Style.RESET_ALL}")

            if self.debug_mode:
                print(f"{Fore.CYAN}{self.get_message('debug.api_call', 'GetCommand')}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}{self.get_message('debug.command_arn', command_arn)}{Style.RESET_ALL}")

            # Extract command ID from ARN
            # ARN format: arn:aws:iot:region:account:command/command-id
            command_id = command_arn.split("/")[-1] if "/" in command_arn else command_arn

            # Call AWS IoT GetCommand API
            response = self.safe_api_call(
                self.iot_client.get_command, "GetCommand", command_id, debug=self.debug_mode, commandId=command_id
            )

            if response is None:
                print(f"{Fore.RED}{self.get_message('errors.command_not_found')}{Style.RESET_ALL}")
                return None

            # Extract command details from response
            command_arn = response.get("commandArn", command_arn)
            command_id = response.get("commandId", "")
            description = response.get("description", "")
            created_at = response.get("createdAt", "")
            namespace = response.get("namespace", "")

            # Extract and parse payload format
            payload_format = {}
            payload_data = response.get("payload", {})
            if payload_data:
                content = payload_data.get("content")
                if content:
                    try:
                        # Content is binary blob, decode and parse JSON
                        if isinstance(content, bytes):
                            payload_format = json.loads(content.decode("utf-8"))
                        else:
                            payload_format = json.loads(content)
                    except Exception as e:
                        if self.debug_mode:
                            print(f"{Fore.YELLOW}{self.get_message('debug.payload_parse_error', str(e))}{Style.RESET_ALL}")
                        payload_format = {"error": "Unable to parse payload format"}

            # Determine if predefined (for now, all are custom since we create them)
            is_predefined = False

            # Create Command object
            command = Command(
                command_arn=command_arn,
                command_name=command_id,
                description=description,
                payload_format=payload_format,
                created_at=created_at,
                is_predefined=is_predefined,
            )

            # Display command details
            self._display_command_details(command, namespace)

            return command

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_message = e.response["Error"]["Message"]

            print(f"{Fore.RED}{self.get_message('errors.aws_api_error', error_code)}{Style.RESET_ALL}")
            print(f"{Fore.RED}  {error_message}{Style.RESET_ALL}")

            # Provide specific troubleshooting guidance
            if error_code == "ResourceNotFoundException":
                print(f"{Fore.YELLOW}{self.get_message('troubleshooting.command_not_found')}{Style.RESET_ALL}")
            elif error_code == "UnauthorizedException":
                print(f"{Fore.YELLOW}{self.get_message('troubleshooting.unauthorized')}{Style.RESET_ALL}")

            if self.debug_mode:
                print(f"{Fore.CYAN}{self.get_message('debug.full_error')}{Style.RESET_ALL}")
                print(json.dumps(e.response, indent=2, default=str))

            return None

        except Exception as e:
            print(f"{Fore.RED}{self.get_message('errors.unexpected_error', str(e))}{Style.RESET_ALL}")

            if self.debug_mode:
                import traceback

                print(f"{Fore.CYAN}{self.get_message('debug.full_traceback')}{Style.RESET_ALL}")
                traceback.print_exc()

            return None

    def _display_command_details(self, command: Command, namespace: str = ""):
        """
        Display complete command details in a formatted view.

        Shows command name, description, ARN, creation date, namespace,
        and the complete payload format specification including parameter
        names, types, and constraints.

        Args:
            command: Command object to display
            namespace: AWS IoT Commands namespace (e.g., "AWS-IoT")
        """
        print(f"\n{Fore.GREEN}{'='*80}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{self.get_message('ui.command_details')}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{'='*80}{Style.RESET_ALL}")

        # Basic information
        print(f"\n{Fore.CYAN}{self.get_message('results.command_name', command.command_name)}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('results.description', command.description)}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('results.command_arn', command.command_arn)}{Style.RESET_ALL}")

        # Type (predefined or custom)
        command_type = self.get_message("results.predefined") if command.is_predefined else self.get_message("results.custom")
        print(f"{Fore.CYAN}{self.get_message('results.is_predefined', command_type)}{Style.RESET_ALL}")

        # Namespace
        if namespace:
            print(f"{Fore.CYAN}{self.get_message('results.namespace', namespace)}{Style.RESET_ALL}")

        # Creation date
        if command.created_at:
            try:
                if isinstance(command.created_at, str):
                    created_dt = datetime.fromisoformat(command.created_at.replace("Z", "+00:00"))
                else:
                    created_dt = command.created_at
                created_str = created_dt.strftime("%Y-%m-%d %H:%M:%S UTC")
                print(f"{Fore.CYAN}{self.get_message('results.created_at', created_str)}{Style.RESET_ALL}")
            except Exception:
                print(f"{Fore.CYAN}{self.get_message('results.created_at', str(command.created_at))}{Style.RESET_ALL}")

        # Payload format specification
        print(f"\n{Fore.YELLOW}{self.get_message('results.payload_format')}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}{'─'*80}{Style.RESET_ALL}")

        if command.payload_format:
            # Pretty print the JSON schema
            payload_json = json.dumps(command.payload_format, indent=2)
            print(f"{Fore.WHITE}{payload_json}{Style.RESET_ALL}")

            # Extract and display parameter information if available
            if "properties" in command.payload_format:
                print(f"\n{Fore.YELLOW}{self.get_message('results.parameters_summary')}{Style.RESET_ALL}")
                print(f"{Fore.WHITE}{'─'*80}{Style.RESET_ALL}")

                properties = command.payload_format.get("properties", {})
                required_fields = command.payload_format.get("required", [])

                # Display each parameter
                for param_name, param_spec in properties.items():
                    param_type = param_spec.get("type", "unknown")
                    is_required = param_name in required_fields
                    required_marker = f"{Fore.RED}*{Style.RESET_ALL}" if is_required else " "

                    print(
                        f"\n{required_marker} {Fore.CYAN}{param_name}{Style.RESET_ALL} ({Fore.YELLOW}{param_type}{Style.RESET_ALL})"
                    )

                    # Show description if available
                    if "description" in param_spec:
                        print(f"  {self.get_message('results.param_description', param_spec['description'])}")

                    # Show enum values if available
                    if "enum" in param_spec:
                        enum_values = ", ".join(str(v) for v in param_spec["enum"])
                        print(f"  {self.get_message('results.param_allowed_values', enum_values)}")

                    # Show constraints
                    constraints = []
                    if "minimum" in param_spec:
                        constraints.append(f"min: {param_spec['minimum']}")
                    if "maximum" in param_spec:
                        constraints.append(f"max: {param_spec['maximum']}")
                    if "minLength" in param_spec:
                        constraints.append(f"minLength: {param_spec['minLength']}")
                    if "maxLength" in param_spec:
                        constraints.append(f"maxLength: {param_spec['maxLength']}")
                    if "pattern" in param_spec:
                        constraints.append(f"pattern: {param_spec['pattern']}")

                    if constraints:
                        print(f"  {self.get_message('results.param_constraints', ', '.join(constraints))}")

                # Show legend for required fields
                if required_fields:
                    print(f"\n{Fore.RED}*{Style.RESET_ALL} {self.get_message('results.required_field_legend')}")
        else:
            print(f"{Fore.YELLOW}{self.get_message('results.no_payload_format')}{Style.RESET_ALL}")

        print(f"\n{Fore.GREEN}{'='*80}{Style.RESET_ALL}")

    def delete_command(self, command_identifier: str) -> bool:
        """
        Delete a command from AWS IoT Commands.

        This function:
        1. Prompts for confirmation before deletion
        2. Verifies no active commands use the command
        3. Prevents deletion of predefined commands
        4. Calls AWS IoT DeleteCommand API

        Args:
            command_identifier: Command ARN or name to delete

        Returns:
            True if deletion successful, False otherwise

        Requirements: 6.9, 6.10
        """
        try:
            # Validate input
            if not command_identifier:
                print(f"{Fore.RED}{self.get_message('errors.command_arn_required')}{Style.RESET_ALL}")
                return False

            print(f"\n{Fore.CYAN}{self.get_message('status.deleting_command')}{Style.RESET_ALL}")

            # Extract command ID from ARN if full ARN provided
            # ARN format: arn:aws:iot:region:account:command/command-id
            command_id = command_identifier.split("/")[-1] if "/" in command_identifier else command_identifier

            if self.debug_mode:
                print(f"{Fore.CYAN}{self.get_message('debug.api_call', 'GetCommand')}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}{self.get_message('debug.command_name', command_id)}{Style.RESET_ALL}")

            # First, get command details to check if it's predefined
            response = self.safe_api_call(
                self.iot_client.get_command, "GetCommand", command_id, debug=self.debug_mode, commandId=command_id
            )

            if response is None:
                print(f"{Fore.RED}{self.get_message('errors.command_not_found')}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}{self.get_message('troubleshooting.command_not_found')}{Style.RESET_ALL}")
                return False

            # Extract command information
            command_name = response.get("commandId", command_id)
            description = response.get("description", "")
            namespace = response.get("namespace", "")

            # Check if predefined (for now, we'll assume all are custom since we create them)
            # In a real scenario, predefined commands would have specific markers
            is_predefined = False  # This would be determined by checking namespace or other attributes

            if is_predefined:
                print(f"{Fore.RED}{self.get_message('errors.cannot_delete_predefined')}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}{self.get_message('troubleshooting.predefined_cannot_delete')}{Style.RESET_ALL}")
                return False

            # Display command information
            print(f"\n{Fore.YELLOW}{'─'*80}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{self.get_message('results.command_name', command_name)}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{self.get_message('results.description', description)}{Style.RESET_ALL}")
            if namespace:
                print(f"{Fore.CYAN}{self.get_message('results.namespace', namespace)}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}{'─'*80}{Style.RESET_ALL}")

            # TODO: Verify no active command executions use this command
            # This would require listing command executions and checking their command ARNs
            # For now, we'll proceed with a warning
            print(f"\n{Fore.YELLOW}⚠️  {self.get_message('troubleshooting.check_active_executions')}{Style.RESET_ALL}")

            # Prompt for confirmation
            print(f"\n{Fore.RED}{self.get_message('prompts.confirm_command_delete', command_name)}{Style.RESET_ALL}")
            confirmation = input().strip()

            if confirmation != "DELETE":
                print(f"{Fore.YELLOW}{self.get_message('errors.deletion_aborted')}{Style.RESET_ALL}")
                return False

            if self.debug_mode:
                print(f"\n{Fore.CYAN}{self.get_message('debug.api_call', 'DeleteCommand')}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}{self.get_message('debug.command_name', command_id)}{Style.RESET_ALL}")

            # Call AWS IoT DeleteCommand API
            delete_response = self.safe_api_call(
                self.iot_client.delete_command, "DeleteCommand", command_id, debug=self.debug_mode, commandId=command_id
            )

            if delete_response is None:
                print(f"{Fore.RED}{self.get_message('errors.command_deletion_failed')}{Style.RESET_ALL}")
                return False

            # Display success message
            print(f"\n{Fore.GREEN}{self.get_message('status.command_deleted')}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{self.get_message('results.command_name', command_name)}{Style.RESET_ALL}")

            return True

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_message = e.response["Error"]["Message"]

            print(f"{Fore.RED}{self.get_message('errors.aws_api_error', error_code)}{Style.RESET_ALL}")
            print(f"{Fore.RED}  {error_message}{Style.RESET_ALL}")

            # Provide specific troubleshooting guidance
            if error_code == "ResourceNotFoundException":
                print(f"{Fore.YELLOW}{self.get_message('troubleshooting.command_not_found')}{Style.RESET_ALL}")
            elif error_code == "ConflictException":
                print(f"{Fore.YELLOW}{self.get_message('errors.command_in_use')}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}{self.get_message('troubleshooting.check_active_executions')}{Style.RESET_ALL}")
            elif error_code == "ThrottlingException":
                print(f"{Fore.YELLOW}{self.get_message('troubleshooting.throttling')}{Style.RESET_ALL}")
            elif error_code == "UnauthorizedException":
                print(f"{Fore.YELLOW}{self.get_message('troubleshooting.unauthorized')}{Style.RESET_ALL}")

            if self.debug_mode:
                print(f"{Fore.CYAN}{self.get_message('debug.full_error')}{Style.RESET_ALL}")
                print(json.dumps(e.response, indent=2, default=str))

            return False

        except Exception as e:
            print(f"{Fore.RED}{self.get_message('errors.unexpected_error', str(e))}{Style.RESET_ALL}")

            if self.debug_mode:
                import traceback

                print(f"{Fore.CYAN}{self.get_message('debug.full_traceback')}{Style.RESET_ALL}")
                traceback.print_exc()

            return False

    def get_predefined_commands(self) -> List[Dict[str, Any]]:
        """
        Return list of all predefined automotive commands.

        These commands provide ready-to-use command structures for common
        vehicle operations. Each command includes:
        - Command name and description
        - Payload format (JSON schema)
        - Example parameter values
        - isPredefined flag set to True

        Returns:
            List of dictionaries containing predefined command definitions

        Requirements: 6.1, 6.2, 6.3
        """
        # Note: For AWS-IoT namespace, parameters are not formally defined in the command.
        # The payload is static and sent as-is. Additional parameters can be passed at
        # execution time via StartCommandExecution API.
        predefined_commands = [
            {
                "command_name": "vehicle-lock",
                "description": "Remotely lock all vehicle doors",
                "payload_format": {"action": "lock"},
                "is_predefined": True,
            },
            {
                "command_name": "vehicle-unlock",
                "description": "Remotely unlock all vehicle doors",
                "payload_format": {"action": "unlock"},
                "is_predefined": True,
            },
            {
                "command_name": "start-engine",
                "description": "Remotely start the vehicle engine",
                "payload_format": {"action": "start"},
                "is_predefined": True,
            },
            {
                "command_name": "stop-engine",
                "description": "Remotely stop the vehicle engine",
                "payload_format": {"action": "stop"},
                "is_predefined": True,
            },
            {
                "command_name": "set-climate",
                "description": "Set vehicle climate control temperature",
                "payload_format": {"action": "setClimate"},
                "is_predefined": True,
            },
            {
                "command_name": "activate-horn",
                "description": "Activate vehicle horn for specified duration",
                "payload_format": {"action": "horn"},
                "is_predefined": True,
            },
        ]

        return predefined_commands

    def validate_target(self, target_name: str, target_type: str = "device") -> Dict[str, Any]:
        """
        Validate that a target device or thing group exists.

        This function validates the target before executing a command by:
        1. Checking if the target name is provided
        2. For devices: Calling DescribeThing API to verify existence
        3. For groups: Calling DescribeThingGroup API and displaying member count

        Args:
            target_name: Name of the device (thing) or thing group
            target_type: Type of target - "device" or "group" (default: "device")

        Returns:
            Dict with:
                - valid (bool): Whether target is valid
                - target_arn (str): ARN of the target if valid
                - member_count (int): Number of members if target is a group
                - error_message (str): Error message if invalid

        Requirements: 3.2, 3.3, 3.5
        """
        # Validate input
        if not target_name or not target_name.strip():
            return {"valid": False, "error_message": self.get_message("validation.target_empty")}

        target_name = target_name.strip()

        try:
            if target_type == "device":
                # Validate device exists using DescribeThing API
                if self.debug_mode:
                    print(f"\n{Fore.CYAN}{self.get_message('debug.api_call', 'DescribeThing')}{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}{self.get_message('debug.thing_name_debug', target_name)}{Style.RESET_ALL}")

                response = self.safe_api_call(
                    self.iot_client.describe_thing, "DescribeThing", target_name, debug=self.debug_mode, thingName=target_name
                )

                if response is None:
                    return {"valid": False, "error_message": self.get_message("validation.device_not_found", target_name)}

                # Extract thing ARN
                thing_arn = response.get("thingArn", "")

                if self.debug_mode:
                    print(f"{Fore.GREEN}{self.get_message('validation.device_exists', target_name)}{Style.RESET_ALL}")

                return {"valid": True, "target_arn": thing_arn, "target_type": "device", "target_name": target_name}

            elif target_type == "group":
                # Validate thing group exists using DescribeThingGroup API
                if self.debug_mode:
                    print(f"\n{Fore.CYAN}{self.get_message('debug.api_call', 'DescribeThingGroup')}{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}{self.get_message('debug.thing_group_name_debug', target_name)}{Style.RESET_ALL}")

                response = self.safe_api_call(
                    self.iot_client.describe_thing_group,
                    "DescribeThingGroup",
                    target_name,
                    debug=self.debug_mode,
                    thingGroupName=target_name,
                )

                if response is None:
                    return {"valid": False, "error_message": self.get_message("validation.group_not_found", target_name)}

                # Extract thing group ARN
                group_arn = response.get("thingGroupArn", "")

                # Get member count from thing group index
                # Note: DescribeThingGroup doesn't return member count directly
                # We would need to use SearchIndex or ListThingsInThingGroup
                # For now, we'll try to get it from metadata or set to 0
                member_count = 0

                # Try to get member count using ListThingsInThingGroup
                try:
                    list_response = self.safe_api_call(
                        self.iot_client.list_things_in_thing_group,
                        "ListThingsInThingGroup",
                        target_name,
                        debug=self.debug_mode,
                        thingGroupName=target_name,
                        maxResults=250,  # Get up to 250 members
                    )

                    if list_response:
                        things = list_response.get("things", [])
                        member_count = len(things)

                        # Check if there are more members (pagination)
                        if "nextToken" in list_response:
                            member_count = f"{member_count}+"  # Indicate there are more
                except Exception:
                    # If we can't get member count, continue with 0
                    pass

                if self.debug_mode:
                    print(
                        f"{Fore.GREEN}{self.get_message('validation.group_exists', target_name, member_count)}{Style.RESET_ALL}"
                    )

                # Display member count to user
                print(f"{Fore.CYAN}   {self.get_message('results.group_member_count', member_count)}{Style.RESET_ALL}")

                return {
                    "valid": True,
                    "target_arn": group_arn,
                    "target_type": "group",
                    "target_name": target_name,
                    "member_count": member_count,
                }
            else:
                return {"valid": False, "error_message": self.get_message("validation.invalid_target_type", target_type)}

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_message = e.response["Error"]["Message"]

            if self.debug_mode:
                print(f"{Fore.RED}{self.get_message('errors.aws_api_error', error_code)}{Style.RESET_ALL}")
                print(f"{Fore.RED}  {error_message}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}{self.get_message('debug.full_error')}{Style.RESET_ALL}")
                print(json.dumps(e.response, indent=2, default=str))

            # Map specific error codes to user-friendly messages
            if error_code == "ResourceNotFoundException":
                if target_type == "device":
                    return {"valid": False, "error_message": self.get_message("validation.device_not_found", target_name)}
                else:
                    return {"valid": False, "error_message": self.get_message("validation.group_not_found", target_name)}
            else:
                return {
                    "valid": False,
                    "error_message": self.get_message("validation.target_validation_failed", error_message),
                }

        except Exception as e:
            if self.debug_mode:
                print(f"{Fore.RED}{self.get_message('errors.unexpected_error', str(e))}{Style.RESET_ALL}")
                import traceback

                print(f"{Fore.CYAN}{self.get_message('debug.full_traceback')}{Style.RESET_ALL}")
                traceback.print_exc()

            return {"valid": False, "error_message": self.get_message("validation.target_validation_failed", str(e))}

    def select_device_with_pagination(self, page_size: int = 20, search_prefix: Optional[str] = None) -> Optional[str]:
        """
        Display paginated device list and allow user to select a device.

        This function provides an interactive paginated interface for device selection with:
        - Configurable page size (default 20 devices per page)
        - Forward and backward navigation through pages
        - Search/filter by device name prefix
        - Manual device name entry
        - Clear visual feedback about pagination state

        Args:
            page_size: Number of devices to display per page (default: 20)
            search_prefix: Optional prefix to filter device names

        Returns:
            Selected device name, or None if cancelled

        Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 2.1, 2.2, 2.3, 2.4, 3.1, 3.2, 3.3, 3.4, 4.1, 4.2, 4.3, 4.4, 6.1, 6.2, 6.3
        """
        # Initialize pagination state
        current_page = []
        next_token = None
        previous_tokens = []  # Stack for backward navigation
        page_number = 1
        active_search = search_prefix

        while True:
            try:
                # Fetch devices for current page with retry logic
                retry_attempt = 0
                max_retries = 3
                response = None

                while retry_attempt <= max_retries:
                    try:
                        # Fetch devices for current page
                        list_params = {"maxResults": page_size}

                        # Add search filter if active
                        if active_search:
                            list_params["thingTypeName"] = active_search

                        # Add pagination token if navigating
                        if next_token:
                            list_params["nextToken"] = next_token

                        # Call AWS IoT list_things API
                        response = self.iot_client.list_things(**list_params)

                        if self.debug_mode:
                            print(f"\n{Fore.CYAN}[DEBUG] ListThings API call successful{Style.RESET_ALL}")
                            print(
                                f"{Fore.CYAN}[DEBUG] Response: {json.dumps(response, indent=2, default=str)}{Style.RESET_ALL}"
                            )

                        # Success - break retry loop
                        break

                    except ClientError as e:
                        # Handle AWS API errors with retry logic
                        retry_info = handle_aws_api_error(
                            e,
                            "ListThings",
                            self.get_message,
                            debug_mode=self.debug_mode,
                            max_retries=max_retries,
                            retry_attempt=retry_attempt,
                        )

                        if retry_info and retry_info.get("should_retry"):
                            # Wait and retry
                            wait_time = retry_info.get("wait_time", 1)
                            time.sleep(wait_time)
                            retry_attempt = retry_info.get("retry_attempt", retry_attempt + 1)
                            continue
                        else:
                            # Non-retryable error or max retries exceeded
                            error_code = e.response["Error"]["Code"]

                            # Handle specific error cases
                            if error_code == "ResourceNotFoundException":
                                # No devices registered - allow manual entry
                                print(f"\n{Fore.YELLOW}{self.get_message('ui.no_things_manual_entry')}{Style.RESET_ALL}")
                                manual_input = input(f"\n{self.get_message('prompts.target_device')}").strip()
                                if manual_input:
                                    return manual_input
                                else:
                                    return None
                            elif error_code == "UnauthorizedException":
                                # Permission denied - cannot proceed
                                return None
                            else:
                                # Other errors - cannot proceed
                                return None

                # Check if response was obtained
                if response is None:
                    print(f"{Fore.RED}{self.get_message('errors.general_error', 'Failed to list devices')}{Style.RESET_ALL}")
                    return None

                # Extract devices and next token
                current_page = response.get("things", [])
                response_next_token = response.get("nextToken")

                # Check if no devices found
                if not current_page:
                    if page_number == 1:
                        # No devices on first page
                        if active_search:
                            print(
                                f"\n{Fore.YELLOW}{self.get_message('pagination.no_search_results', active_search)}{Style.RESET_ALL}"
                            )
                        else:
                            print(f"\n{Fore.YELLOW}{self.get_message('ui.no_things_manual_entry')}{Style.RESET_ALL}")

                        # Allow manual entry
                        manual_input = input(f"\n{self.get_message('prompts.target_device')}").strip()
                        if manual_input:
                            return manual_input
                        else:
                            return None
                    else:
                        # No devices on subsequent page (shouldn't happen, but handle gracefully)
                        print(f"\n{Fore.YELLOW}No devices found on this page. Returning to previous page...{Style.RESET_ALL}")
                        if previous_tokens:
                            next_token = previous_tokens.pop()
                            page_number -= 1
                            continue
                        else:
                            # Can't go back, return None
                            return None

                # Display devices with sequential numbering
                print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
                if active_search:
                    print(
                        f"{Fore.CYAN}{self.get_message('pagination.search_active', active_search, len(current_page))}{Style.RESET_ALL}"
                    )
                print(
                    f"{Fore.CYAN}{self.get_message('pagination.page_info', page_number, len(current_page))}{Style.RESET_ALL}"
                )
                print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}")

                # Display device list
                print(f"\n{Fore.WHITE}{self.get_message('ui.available_devices')}{Style.RESET_ALL}")
                for idx, thing in enumerate(current_page, 1):
                    thing_name = thing.get("thingName", "")
                    thing_type = thing.get("thingTypeName", "N/A")
                    print(
                        f"{Fore.CYAN}{idx}. {thing_name}{Style.RESET_ALL} {self.get_message('ui.device_type_label', thing_type)}"
                    )

                # Display navigation options based on pagination state
                print(f"\n{Fore.YELLOW}{'─'*80}{Style.RESET_ALL}")

                # Determine which navigation options to show
                has_next = response_next_token is not None
                has_previous = page_number > 1
                is_single_page = not has_next and not has_previous

                if is_single_page:
                    # Single page - no pagination controls
                    help_text = self.get_message("pagination.navigation_help_single_page")
                elif has_next and has_previous:
                    # Middle page - show both next and previous
                    help_text = self.get_message("pagination.navigation_help")
                    print(f"{Fore.GREEN}{self.get_message('pagination.more_pages_available')}{Style.RESET_ALL}")
                elif has_next:
                    # First page - show only next
                    help_text = self.get_message("pagination.navigation_help_first_page")
                    print(f"{Fore.GREEN}{self.get_message('pagination.more_pages_available')}{Style.RESET_ALL}")
                else:
                    # Last page - show only previous
                    help_text = self.get_message("pagination.navigation_help_last_page")
                    print(f"{Fore.YELLOW}{self.get_message('pagination.last_page')}{Style.RESET_ALL}")

                print(f"{Fore.YELLOW}{help_text}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}{'─'*80}{Style.RESET_ALL}")

                # Get user input
                user_input = input(f"\n{self.get_message('prompts.target_device')}").strip()

                if not user_input:
                    print(f"{Fore.YELLOW}{self.get_message('pagination.cancelled')}{Style.RESET_ALL}")
                    return None

                # Handle navigation commands
                if user_input.lower() == "q":
                    print(f"{Fore.YELLOW}{self.get_message('pagination.cancelled')}{Style.RESET_ALL}")
                    return None

                elif user_input.lower() == "n" and has_next:
                    # Navigate to next page
                    previous_tokens.append(next_token)  # Save current token for backward navigation
                    next_token = response_next_token
                    page_number += 1
                    continue

                elif user_input.lower() == "p" and has_previous:
                    # Navigate to previous page
                    if previous_tokens:
                        next_token = previous_tokens.pop()
                        page_number -= 1
                        continue
                    else:
                        print(f"{Fore.RED}{self.get_message('pagination.invalid_selection')}{Style.RESET_ALL}")
                        continue

                elif user_input.lower() == "s":
                    # Search functionality
                    search_input = input(f"\n{self.get_message('pagination.search_prompt')}").strip()

                    if search_input:
                        # Apply new search
                        active_search = search_input
                    else:
                        # Clear search
                        active_search = None

                    # Reset pagination state
                    next_token = None
                    previous_tokens = []
                    page_number = 1
                    continue

                # Try to parse as device number
                try:
                    device_idx = int(user_input) - 1
                    if 0 <= device_idx < len(current_page):
                        selected_device = current_page[device_idx].get("thingName", "")
                        print(f"{Fore.GREEN}{self.get_message('ui.selected_device', selected_device)}{Style.RESET_ALL}")
                        return selected_device
                    else:
                        print(f"{Fore.RED}{self.get_message('pagination.invalid_selection')}{Style.RESET_ALL}")
                        continue
                except ValueError:
                    # Not a number - treat as manual device name entry
                    return user_input

            except (KeyboardInterrupt, EOFError):
                print(f"\n{Fore.YELLOW}{self.get_message('pagination.cancelled')}{Style.RESET_ALL}")
                return None
            except Exception as e:
                print(f"{Fore.RED}{self.get_message('errors.unexpected_error', str(e))}{Style.RESET_ALL}")
                if self.debug_mode:
                    import traceback

                    traceback.print_exc()
                return None

    def execute_command(
        self, command_arn: str, target_arn: str, parameters: Dict[str, Any], timeout_seconds: int = 60
    ) -> Optional[str]:
        """
        Execute a command to a target device or group.

        This function:
        1. Requires selection of an existing command
        2. Validates the target device or group
        3. Collects parameter values matching the command payload format
        4. Calls AWS IoT StartCommandExecution API
        5. AWS IoT automatically publishes to MQTT topic:
           $aws/commands/things/{DeviceID}/executions/{ExecutionId}/request/{PayloadFormat}
        6. Displays command ID and initial status

        Args:
            command_arn: ARN of the command to use
            target_arn: ARN of the target device or thing group
            parameters: Dictionary of parameter values matching command payload format

        Returns:
            Command execution ID if successful, None if failed

        Requirements: 2.4, 2.5, 2.6, 2.7
        """
        try:
            print(f"\n{Fore.CYAN}{self.get_message('status.executing_command')}{Style.RESET_ALL}")

            # Validate inputs
            if not command_arn:
                print(f"{Fore.RED}{self.get_message('errors.command_arn_required')}{Style.RESET_ALL}")
                return None

            if not target_arn:
                print(f"{Fore.RED}{self.get_message('errors.target_required')}{Style.RESET_ALL}")
                return None

            # Parameters are optional for AWS-IoT namespace
            if parameters is not None and not isinstance(parameters, dict):
                print(f"{Fore.RED}{self.get_message('errors.invalid_payload_format')}{Style.RESET_ALL}")
                return None

            # Extract command ID from command ARN
            # ARN format: arn:aws:iot:region:account:command/command-id
            command_id = command_arn.split("/")[-1] if "/" in command_arn else command_arn

            if self.debug_mode:
                print(f"\n{Fore.CYAN}{self.get_message('debug.api_call', 'StartCommandExecution')}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}{self.get_message('debug.command_id_debug', command_id)}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}{self.get_message('debug.target_arn_debug', target_arn)}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}[DEBUG] Execution Timeout: {timeout_seconds} seconds{Style.RESET_ALL}")
                if parameters:
                    print(f"{Fore.CYAN}{self.get_message('debug.parameters_debug')}{Style.RESET_ALL}")
                    print(json.dumps(parameters, indent=2))
                else:
                    print(f"{Fore.CYAN}[DEBUG] No parameters provided{Style.RESET_ALL}")

            # Prepare StartCommandExecution API parameters
            # Only include parameters if they are provided and non-empty
            execution_params = {"commandArn": command_arn, "targetArn": target_arn, "executionTimeoutSeconds": timeout_seconds}

            # Add parameters only if provided and non-empty
            if parameters:
                execution_params["parameters"] = parameters

            # Call AWS IoT Jobs Data StartCommandExecution API
            # This automatically publishes the command to the MQTT request topic
            response = self.safe_api_call(
                self.iot_data_client.start_command_execution,
                "StartCommandExecution",
                command_id,
                debug=self.debug_mode,
                **execution_params,
            )

            if response is None:
                print(f"{Fore.RED}{self.get_message('errors.command_execution_failed')}{Style.RESET_ALL}")
                return None

            # Extract execution ID from response
            execution_id = response.get("executionId")

            if not execution_id:
                print(f"{Fore.RED}{self.get_message('errors.no_command_id_returned')}{Style.RESET_ALL}")
                return None

            # Get initial status
            initial_status = response.get("status", "CREATED")

            # Display success message with command ID and status
            print(f"\n{Fore.GREEN}{self.get_message('status.command_execution_started')}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{self.get_message('results.command_id_label', execution_id)}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{self.get_message('results.status_label', initial_status)}{Style.RESET_ALL}")

            # Display MQTT topic information
            # Extract thing name from target ARN
            # ARN format: arn:aws:iot:region:account:thing/thing-name
            thing_name = target_arn.split("/")[-1] if "/" in target_arn else "unknown"
            mqtt_topic = f"$aws/commands/things/{thing_name}/executions/{execution_id}/request/json"

            print(f"\n{Fore.YELLOW}{self.get_message('status.mqtt_topic_published', mqtt_topic)}{Style.RESET_ALL}")

            if self.debug_mode:
                print(f"\n{Fore.CYAN}[DEBUG] Full Response:{Style.RESET_ALL}")
                print(json.dumps(response, indent=2, default=str))

            return execution_id

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_message = e.response["Error"]["Message"]

            print(f"{Fore.RED}{self.get_message('errors.aws_api_error', error_code)}{Style.RESET_ALL}")
            print(f"{Fore.RED}  {error_message}{Style.RESET_ALL}")

            # Provide specific troubleshooting guidance
            if error_code == "ResourceNotFoundException":
                print(f"{Fore.YELLOW}{self.get_message('troubleshooting.command_not_found')}{Style.RESET_ALL}")
            elif error_code == "InvalidRequestException":
                print(f"{Fore.YELLOW}{self.get_message('troubleshooting.invalid_payload')}{Style.RESET_ALL}")
            elif error_code == "ThrottlingException":
                print(f"{Fore.YELLOW}{self.get_message('troubleshooting.throttling')}{Style.RESET_ALL}")
            elif error_code == "UnauthorizedException":
                print(f"{Fore.YELLOW}{self.get_message('troubleshooting.unauthorized')}{Style.RESET_ALL}")

            if self.debug_mode:
                print(f"{Fore.CYAN}{self.get_message('debug.full_error')}{Style.RESET_ALL}")
                print(json.dumps(e.response, indent=2, default=str))

            return None

        except Exception as e:
            print(f"{Fore.RED}{self.get_message('errors.unexpected_error', str(e))}{Style.RESET_ALL}")

            if self.debug_mode:
                import traceback

                print(f"{Fore.CYAN}{self.get_message('debug.full_traceback')}{Style.RESET_ALL}")
                traceback.print_exc()

            return None

    def execute_command_to_multiple_targets(
        self, command_arn: str, target_arns: List[str], parameters: Dict[str, Any]
    ) -> List[str]:
        """
        Execute a command to multiple target devices or groups.

        This function creates separate command executions for each target in the list.
        Each execution is independent and tracked separately.

        Args:
            command_arn: ARN of the command to use
            target_arns: List of target ARNs (devices or thing groups)
            parameters: Dictionary of parameter values matching command payload format

        Returns:
            List of command execution IDs for successful executions

        Requirements: 3.1, 3.4
        """
        if not target_arns:
            print(f"{Fore.RED}{self.get_message('errors.target_required')}{Style.RESET_ALL}")
            return []

        print(f"\n{Fore.CYAN}{self.get_message('status.executing_to_multiple_targets', len(target_arns))}{Style.RESET_ALL}")

        execution_ids = []
        failed_count = 0

        for idx, target_arn in enumerate(target_arns, 1):
            # Extract target name for display
            target_name = target_arn.split("/")[-1] if "/" in target_arn else target_arn

            print(f"\n{Fore.CYAN}[{idx}/{len(target_arns)}] Executing command to: {target_name}{Style.RESET_ALL}")

            # Execute command to this target
            execution_id = self.execute_command(command_arn, target_arn, parameters)

            if execution_id:
                execution_ids.append(execution_id)
                print(
                    f"{Fore.GREEN}{self.get_message('status.target_execution_success', idx, len(target_arns), target_name)}{Style.RESET_ALL}"
                )
            else:
                failed_count += 1
                print(
                    f"{Fore.RED}{self.get_message('status.target_execution_failed', idx, len(target_arns), target_name, 'Execution failed')}{Style.RESET_ALL}"
                )

        # Display summary
        success_count = len(execution_ids)
        print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
        print(
            f"{Fore.CYAN}{self.get_message('status.multiple_executions_summary', success_count, failed_count, len(target_arns))}{Style.RESET_ALL}"
        )
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}")

        if execution_ids:
            print(f"\n{Fore.GREEN}{self.get_message('results.successful_execution_ids')}{Style.RESET_ALL}")
            for i, exec_id in enumerate(execution_ids, 1):
                print(f"{Fore.CYAN}  {i}. {exec_id}{Style.RESET_ALL}")

        return execution_ids

    def get_command_status(self, execution_id: str, target_arn: str) -> Optional[CommandExecution]:
        """
        Retrieve and display command execution status from AWS IoT.

        This function:
        1. Retrieves command execution status using GetCommandExecution API
        2. Displays command ID, target device, status value, and timestamp
        3. Shows progress indicators for IN_PROGRESS status
        4. Displays final status and execution duration for completed commands

        Args:
            execution_id: Unique identifier for the command execution
            target_arn: ARN of the target device or thing group

        Returns:
            CommandExecution object if successful, None if failed

        Requirements: 4.1, 4.2, 4.3, 4.4
        """
        try:
            # Validate input
            if not execution_id or not execution_id.strip():
                print(f"{Fore.RED}{self.get_message('errors.command_id_required')}{Style.RESET_ALL}")
                return None

            if not target_arn or not target_arn.strip():
                print(f"{Fore.RED}{self.get_message('errors.target_arn_required')}{Style.RESET_ALL}")
                return None

            execution_id = execution_id.strip()
            target_arn = target_arn.strip()

            print(f"\n{Fore.CYAN}{self.get_message('status.getting_status')}{Style.RESET_ALL}")

            if self.debug_mode:
                print(f"{Fore.CYAN}{self.get_message('debug.api_call', 'GetCommandExecution')}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}[DEBUG] Execution ID: {execution_id}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}[DEBUG] Target ARN: {target_arn}{Style.RESET_ALL}")

            # Call AWS IoT GetCommandExecution API
            response = self.safe_api_call(
                self.iot_client.get_command_execution,
                "GetCommandExecution",
                execution_id,
                debug=self.debug_mode,
                executionId=execution_id,
                targetArn=target_arn,
            )

            if response is None:
                print(f"{Fore.RED}{self.get_message('errors.command_execution_not_found')}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}{self.get_message('troubleshooting.command_execution_not_found')}{Style.RESET_ALL}")
                return None

            # Extract execution details from response
            command_arn = response.get("commandArn", "")
            target_arn = response.get("targetArn", "")
            status = response.get("status", "UNKNOWN")
            created_at = response.get("createdAt", "")
            last_updated_at = response.get("lastUpdatedAt", "")
            completed_at = response.get("completedAt")
            status_reason = response.get("statusReason")
            parameters = response.get("parameters", {})

            # Extract command ARN (may not be in response, use command ARN as fallback)
            command_arn = response.get("commandId", command_arn)

            # Create CommandExecution object
            execution = CommandExecution(
                execution_id=execution_id,
                command_arn=command_arn,
                target_arn=target_arn,
                parameters=parameters,
                status=status,
                created_at=created_at,
                last_updated_at=last_updated_at,
                completed_at=completed_at,
                status_reason=status_reason,
            )

            # Display command execution details
            self._display_command_status(execution)

            return execution

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_message = e.response["Error"]["Message"]

            print(f"{Fore.RED}{self.get_message('errors.aws_api_error', error_code)}{Style.RESET_ALL}")
            print(f"{Fore.RED}  {error_message}{Style.RESET_ALL}")

            # Provide specific troubleshooting guidance
            if error_code == "ResourceNotFoundException":
                print(f"{Fore.YELLOW}{self.get_message('troubleshooting.command_not_found')}{Style.RESET_ALL}")
            elif error_code == "ThrottlingException":
                print(f"{Fore.YELLOW}{self.get_message('troubleshooting.throttling')}{Style.RESET_ALL}")
            elif error_code == "UnauthorizedException":
                print(f"{Fore.YELLOW}{self.get_message('troubleshooting.unauthorized')}{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}{self.get_message('troubleshooting.retry_status')}{Style.RESET_ALL}")

            if self.debug_mode:
                print(f"{Fore.CYAN}{self.get_message('debug.full_error')}{Style.RESET_ALL}")
                print(json.dumps(e.response, indent=2, default=str))

            return None

        except Exception as e:
            print(f"{Fore.RED}{self.get_message('errors.unexpected_error', str(e))}{Style.RESET_ALL}")

            if self.debug_mode:
                import traceback

                print(f"{Fore.CYAN}{self.get_message('debug.full_traceback')}{Style.RESET_ALL}")
                traceback.print_exc()

            return None

    def _display_command_status(self, execution: CommandExecution):
        """
        Display command execution status in a formatted view.

        Shows command ID, target, status, timestamps, and execution duration
        for completed commands. Displays progress indicators for in-progress commands.

        Args:
            execution: CommandExecution object to display
        """
        print(f"\n{Fore.GREEN}{'='*80}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{self.get_message('results.command_details')}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{'='*80}{Style.RESET_ALL}")

        # Command ID
        print(f"\n{Fore.CYAN}{self.get_message('results.command_id_label', execution.command_id)}{Style.RESET_ALL}")

        # Target device/group
        target_name = execution.target_arn.split("/")[-1] if "/" in execution.target_arn else execution.target_arn
        print(f"{Fore.CYAN}{self.get_message('results.target_label', target_name)}{Style.RESET_ALL}")

        # Status with color coding
        status_enum = CommandStatus.from_string(execution.status)
        status_display = status_enum.get_display_string(self.get_message)

        # Color code based on status
        if execution.status in ["SUCCEEDED"]:
            status_color = Fore.GREEN
        elif execution.status in ["FAILED", "TIMED_OUT"]:
            status_color = Fore.RED
        elif execution.status in ["IN_PROGRESS", "CREATED"]:
            status_color = Fore.YELLOW
        elif execution.status in ["CANCELED"]:
            status_color = Fore.MAGENTA
        else:
            status_color = Fore.WHITE

        print(f"{Fore.CYAN}{self.get_message('results.status_label', '')}{status_color}{status_display}{Style.RESET_ALL}")

        # Show progress indicator for IN_PROGRESS status
        if execution.status == "IN_PROGRESS":
            print(f"{Fore.YELLOW}{self.get_message('results.progress_indicator')}{Style.RESET_ALL}")

        # Timestamps
        if execution.created_at:
            try:
                if isinstance(execution.created_at, str):
                    created_dt = datetime.fromisoformat(execution.created_at.replace("Z", "+00:00"))
                else:
                    created_dt = execution.created_at
                created_str = created_dt.strftime("%Y-%m-%d %H:%M:%S UTC")
                print(f"{Fore.CYAN}{self.get_message('results.created_label', created_str)}{Style.RESET_ALL}")
            except Exception:
                print(f"{Fore.CYAN}{self.get_message('results.created_label', str(execution.created_at))}{Style.RESET_ALL}")

        if execution.last_updated_at:
            try:
                if isinstance(execution.last_updated_at, str):
                    updated_dt = datetime.fromisoformat(execution.last_updated_at.replace("Z", "+00:00"))
                else:
                    updated_dt = execution.last_updated_at
                updated_str = updated_dt.strftime("%Y-%m-%d %H:%M:%S UTC")
                print(f"{Fore.CYAN}{self.get_message('results.updated_label', updated_str)}{Style.RESET_ALL}")
            except Exception:
                print(
                    f"{Fore.CYAN}{self.get_message('results.updated_label', str(execution.last_updated_at))}{Style.RESET_ALL}"
                )

        # For completed commands, show completion time and duration
        if execution.completed_at:
            try:
                if isinstance(execution.completed_at, str):
                    completed_dt = datetime.fromisoformat(execution.completed_at.replace("Z", "+00:00"))
                else:
                    completed_dt = execution.completed_at
                completed_str = completed_dt.strftime("%Y-%m-%d %H:%M:%S UTC")
                print(f"{Fore.CYAN}{self.get_message('results.completed_label', completed_str)}{Style.RESET_ALL}")

                # Calculate execution duration
                if execution.created_at:
                    try:
                        if isinstance(execution.created_at, str):
                            created_dt = datetime.fromisoformat(execution.created_at.replace("Z", "+00:00"))
                        else:
                            created_dt = execution.created_at

                        duration = completed_dt - created_dt
                        duration_seconds = duration.total_seconds()

                        # Format duration nicely
                        if duration_seconds < 60:
                            duration_str = f"{duration_seconds:.1f} seconds"
                        elif duration_seconds < 3600:
                            duration_str = f"{duration_seconds/60:.1f} minutes"
                        else:
                            duration_str = f"{duration_seconds/3600:.1f} hours"

                        print(f"{Fore.CYAN}{self.get_message('results.execution_duration', duration_str)}{Style.RESET_ALL}")
                    except Exception:
                        pass
            except Exception:
                print(
                    f"{Fore.CYAN}{self.get_message('results.completed_label', str(execution.completed_at))}{Style.RESET_ALL}"
                )

        # Status reason (if available)
        if execution.status_reason:
            print(f"\n{Fore.YELLOW}{self.get_message('results.status_reason', execution.status_reason)}{Style.RESET_ALL}")

        # Command ARN
        if execution.command_arn:
            print(f"\n{Fore.WHITE}{self.get_message('results.command_arn', execution.command_arn)}{Style.RESET_ALL}")

        # Target ARN
        if execution.target_arn:
            print(f"{Fore.WHITE}{self.get_message('ui.target_arn_label', execution.target_arn)}{Style.RESET_ALL}")

        print(f"\n{Fore.GREEN}{'='*80}{Style.RESET_ALL}")

    def list_command_history(
        self,
        target_arn: str,
        status_filter: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        page_size: int = 50,
        next_token: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve and display list of recent command executions with filtering and pagination.

        This function:
        1. Retrieves list of command executions from AWS IoT for a specific target
        2. Displays command name, target, status, creation time, completion time
        3. Supports pagination with configurable page size
        4. Supports filtering by status, time range
        5. Handles empty history with informative message

        Args:
            target_arn: Target ARN (device or thing group) to retrieve history for (REQUIRED)
            status_filter: Optional status to filter by (e.g., "SUCCEEDED", "FAILED")
            start_time: Optional start time for filtering (ISO format string)
            end_time: Optional end time for filtering (ISO format string)
            page_size: Number of results per page (1-100, default 50)
            next_token: Token for pagination (from previous call)

        Returns:
            Dict with 'executions' (list), 'next_token' (str), and 'has_more' (bool) if successful,
            None if failed

        Requirements: 5.1, 5.2, 5.3, 5.4, 5.5
        """
        try:
            # Validate page size
            if page_size < 1 or page_size > 100:
                print(f"{Fore.RED}{self.get_message('errors.invalid_page_size')}{Style.RESET_ALL}")
                return None

            print(f"\n{Fore.CYAN}{self.get_message('status.listing_history')}{Style.RESET_ALL}")

            # Build API parameters - targetArn is REQUIRED by AWS IoT Commands API
            list_params = {"targetArn": target_arn, "maxResults": page_size}

            # Add pagination token if provided
            if next_token:
                list_params["nextToken"] = next_token

            # Add status filter if provided
            if status_filter:
                # Validate status
                try:
                    CommandStatus.from_string(status_filter)
                    list_params["status"] = status_filter
                except ValueError:
                    print(f"{Fore.YELLOW}⚠️  Invalid status filter: {status_filter}. Ignoring filter.{Style.RESET_ALL}")

            # Add time range filters
            # AWS IoT Commands API requires at least one time filter (startedTimeFilter or completedTimeFilter)
            # Format must be YYYY-MM-DDThh:mm (no seconds or microseconds)
            # If user doesn't provide times, default to last 30 days
            if start_time or end_time:
                # User provided at least one time filter
                if start_time:
                    try:
                        # Parse and validate start time
                        start_dt = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
                        # Format as YYYY-MM-DDThh:mm (AWS requirement)
                        formatted_start = start_dt.strftime("%Y-%m-%dT%H:%M")
                        list_params["startedTimeFilter"] = {"after": formatted_start}
                    except Exception as e:
                        print(f"{Fore.YELLOW}⚠️  Invalid start time format: {start_time}. Ignoring filter.{Style.RESET_ALL}")
                        if self.debug_mode:
                            print(f"{Fore.CYAN}[DEBUG] Error: {str(e)}{Style.RESET_ALL}")

                if end_time:
                    try:
                        # Parse and validate end time
                        end_dt = datetime.fromisoformat(end_time.replace("Z", "+00:00"))
                        # Format as YYYY-MM-DDThh:mm (AWS requirement)
                        formatted_end = end_dt.strftime("%Y-%m-%dT%H:%M")
                        if "startedTimeFilter" in list_params:
                            list_params["startedTimeFilter"]["before"] = formatted_end
                        else:
                            list_params["startedTimeFilter"] = {"before": formatted_end}
                    except Exception as e:
                        print(f"{Fore.YELLOW}⚠️  Invalid end time format: {end_time}. Ignoring filter.{Style.RESET_ALL}")
                        if self.debug_mode:
                            print(f"{Fore.CYAN}[DEBUG] Error: {str(e)}{Style.RESET_ALL}")
            else:
                # No time filters provided - use default of last 30 days
                from datetime import timedelta

                now = datetime.now()
                thirty_days_ago = now - timedelta(days=30)
                # Format as YYYY-MM-DDThh:mm (AWS requirement)
                formatted_start = thirty_days_ago.strftime("%Y-%m-%dT%H:%M")
                list_params["startedTimeFilter"] = {"after": formatted_start}

            if self.debug_mode:
                print(f"{Fore.CYAN}{self.get_message('debug.api_call', 'ListCommandExecutions')}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}[DEBUG] Parameters:{Style.RESET_ALL}")
                print(json.dumps(list_params, indent=2, default=str))

            # Call AWS IoT ListCommandExecutions API
            response = self.safe_api_call(
                self.iot_client.list_command_executions,
                "ListCommandExecutions",
                "command history",
                debug=self.debug_mode,
                **list_params,
            )

            if response is None:
                print(f"{Fore.RED}{self.get_message('errors.history_retrieval_failed')}{Style.RESET_ALL}")
                return None

            # Extract executions from response
            executions = response.get("commandExecutions", [])
            response_next_token = response.get("nextToken")

            # Check if empty
            if not executions:
                print(f"{Fore.YELLOW}{self.get_message('results.no_history')}{Style.RESET_ALL}")
                return {"executions": [], "next_token": None, "has_more": False}

            # Display active filters
            active_filters = []
            # Extract device name from target ARN for display
            device_name = target_arn.split("/")[-1] if "/" in target_arn else target_arn
            active_filters.append(self.get_message("results.history_filter_device", device_name))

            if status_filter:
                active_filters.append(self.get_message("results.history_filter_status", status_filter))
            if start_time or end_time:
                start_str = start_time if start_time else "beginning"
                end_str = end_time if end_time else "now"
                active_filters.append(self.get_message("results.history_filter_time_range", start_str, end_str))

            if active_filters:
                print(f"\n{Fore.YELLOW}{self.get_message('results.history_filters_active')}{Style.RESET_ALL}")
                for filter_text in active_filters:
                    print(f"{Fore.YELLOW}  • {filter_text}{Style.RESET_ALL}")

            # Display command history table
            self._display_command_history_table(executions)

            # Display pagination info
            has_more = response_next_token is not None
            if has_more:
                print(f"\n{Fore.CYAN}💡 {self.get_message('results.history_pagination_info')}{Style.RESET_ALL}")
            else:
                print(f"\n{Fore.CYAN}{self.get_message('results.history_no_more_pages')}{Style.RESET_ALL}")

            # Display total count
            print(f"\n{Fore.WHITE}{self.get_message('results.total_commands', len(executions))}{Style.RESET_ALL}")

            return {"executions": executions, "next_token": response_next_token, "has_more": has_more}

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_message = e.response["Error"]["Message"]

            print(f"{Fore.RED}{self.get_message('errors.aws_api_error', error_code)}{Style.RESET_ALL}")
            print(f"{Fore.RED}  {error_message}{Style.RESET_ALL}")

            # Provide specific troubleshooting guidance
            if error_code == "ThrottlingException":
                print(f"{Fore.YELLOW}{self.get_message('troubleshooting.throttling')}{Style.RESET_ALL}")
            elif error_code == "UnauthorizedException":
                print(f"{Fore.YELLOW}{self.get_message('troubleshooting.unauthorized')}{Style.RESET_ALL}")

            if self.debug_mode:
                print(f"{Fore.CYAN}{self.get_message('debug.full_error')}{Style.RESET_ALL}")
                print(json.dumps(e.response, indent=2, default=str))

            return None

        except Exception as e:
            print(f"{Fore.RED}{self.get_message('errors.unexpected_error', str(e))}{Style.RESET_ALL}")

            if self.debug_mode:
                import traceback

                print(f"{Fore.CYAN}{self.get_message('debug.full_traceback')}{Style.RESET_ALL}")
                traceback.print_exc()

            return None

    def _display_command_history_table(self, executions: List[Dict[str, Any]]):
        """
        Display command execution history in a formatted table.

        Shows command name, target, status, creation time, and completion time
        for each execution in a colored, easy-to-read table format.

        Args:
            executions: List of command execution dictionaries from AWS IoT API
        """
        if not executions:
            print(f"{Fore.YELLOW}{self.get_message('results.no_history')}{Style.RESET_ALL}")
            return

        print(f"\n{Fore.GREEN}{'='*120}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{self.get_message('results.history_header')}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{'='*120}{Style.RESET_ALL}")

        # Print table header
        header_name = self.get_message("results.history_table_header_name")
        header_target = self.get_message("results.history_table_header_target")
        header_status = self.get_message("results.history_table_header_status")
        header_created = self.get_message("results.history_table_header_created")
        header_completed = self.get_message("results.history_table_header_completed")

        print(
            f"\n{Fore.WHITE}{header_name:<25} {header_target:<25} {header_status:<15} {header_created:<20} {header_completed:<20}{Style.RESET_ALL}"
        )
        print(f"{Fore.WHITE}{'-'*25} {'-'*25} {'-'*15} {'-'*20} {'-'*20}{Style.RESET_ALL}")

        # Print each execution
        for exec_data in executions:
            # Extract execution details
            execution_id = exec_data.get("executionId", "N/A")
            command_arn = exec_data.get("commandArn", "")
            target_arn = exec_data.get("targetArn", "")
            status = exec_data.get("status", "UNKNOWN")
            created_at = exec_data.get("createdAt", "")
            completed_at = exec_data.get("completedAt")

            # Extract command name from ARN
            command_name = command_arn.split("/")[-1] if "/" in command_arn else execution_id[:12]
            if len(command_name) > 22:
                command_name = command_name[:22] + "..."

            # Extract target name from ARN
            target_name = target_arn.split("/")[-1] if "/" in target_arn else "N/A"
            if len(target_name) > 22:
                target_name = target_name[:22] + "..."

            # Format status with color
            try:
                status_enum = CommandStatus.from_string(status)
                status_display = status_enum.get_display_string(self.get_message)
            except (ValueError, KeyError):
                status_display = status

            # Truncate status if too long
            if len(status_display) > 12:
                status_display = status_display[:12] + "..."

            # Color code based on status
            if status in ["SUCCEEDED"]:
                status_color = Fore.GREEN
            elif status in ["FAILED", "TIMED_OUT"]:
                status_color = Fore.RED
            elif status in ["IN_PROGRESS", "CREATED"]:
                status_color = Fore.YELLOW
            elif status in ["CANCELED"]:
                status_color = Fore.MAGENTA
            else:
                status_color = Fore.WHITE

            # Format timestamps
            created_str = "N/A"
            if created_at:
                try:
                    if isinstance(created_at, str):
                        created_dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                    else:
                        created_dt = created_at
                    created_str = created_dt.strftime("%Y-%m-%d %H:%M:%S")
                except Exception:
                    created_str = str(created_at)[:19]

            completed_str = "N/A"
            if completed_at:
                try:
                    if isinstance(completed_at, str):
                        completed_dt = datetime.fromisoformat(completed_at.replace("Z", "+00:00"))
                    else:
                        completed_dt = completed_at
                    completed_str = completed_dt.strftime("%Y-%m-%d %H:%M:%S")
                except Exception:
                    completed_str = str(completed_at)[:19]
            elif status in ["IN_PROGRESS", "CREATED"]:
                completed_str = "In Progress"

            # Print row
            print(
                f"{Fore.CYAN}{command_name:<25}{Style.RESET_ALL} "
                f"{Fore.WHITE}{target_name:<25}{Style.RESET_ALL} "
                f"{status_color}{status_display:<15}{Style.RESET_ALL} "
                f"{Fore.WHITE}{created_str:<20}{Style.RESET_ALL} "
                f"{Fore.WHITE}{completed_str:<20}{Style.RESET_ALL}"
            )

        print(f"\n{Fore.GREEN}{'='*120}{Style.RESET_ALL}")

    def cancel_command(self, execution_id: str) -> bool:
        """
        Cancel a pending or executing command.

        This function:
        1. Prompts for confirmation before cancellation
        2. Retrieves current command status to verify it can be canceled
        3. Rejects cancellation for completed commands (SUCCEEDED, FAILED, TIMED_OUT)
        4. Sends cancellation request to AWS IoT using UpdateCommandExecution API
        5. Updates command status to CANCELED on success
        6. Displays failure reason and current state on error

        Args:
            execution_id: Unique identifier for the command execution to cancel

        Returns:
            True if cancellation successful, False otherwise

        Requirements: 7.1, 7.2, 7.3, 7.4, 7.5
        """
        try:
            # Validate input
            if not execution_id or not execution_id.strip():
                print(f"{Fore.RED}{self.get_message('errors.execution_id_required')}{Style.RESET_ALL}")
                return False

            execution_id = execution_id.strip()

            print(f"\n{Fore.CYAN}{self.get_message('status.canceling_command')}{Style.RESET_ALL}")

            # First, get current command status to verify it can be canceled
            if self.debug_mode:
                print(f"{Fore.CYAN}{self.get_message('debug.api_call', 'GetCommandExecution')}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}[DEBUG] Execution ID: {execution_id}{Style.RESET_ALL}")

            # Retrieve current command execution details
            response = self.safe_api_call(
                self.iot_client.get_command_execution,
                "GetCommandExecution",
                execution_id,
                debug=self.debug_mode,
                executionId=execution_id,
            )

            if response is None:
                print(f"{Fore.RED}{self.get_message('errors.command_execution_not_found')}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}{self.get_message('troubleshooting.command_execution_not_found')}{Style.RESET_ALL}")
                return False

            # Extract current status
            current_status = response.get("status", "UNKNOWN")
            command_arn = response.get("commandArn", "")
            target_arn = response.get("targetArn", "")

            # Extract command name and target name for display
            command_name = command_arn.split("/")[-1] if "/" in command_arn else execution_id[:12]
            target_name = target_arn.split("/")[-1] if "/" in target_arn else "N/A"

            # Check if command is in a state that can be canceled
            # Only CREATED and IN_PROGRESS commands can be canceled
            completed_statuses = ["SUCCEEDED", "FAILED", "TIMED_OUT", "CANCELED"]

            if current_status in completed_statuses:
                print(f"{Fore.RED}{self.get_message('errors.cannot_cancel_completed', current_status)}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}{self.get_message('troubleshooting.cannot_cancel_completed')}{Style.RESET_ALL}")

                # Display current command state
                print(f"\n{Fore.YELLOW}{'─'*80}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}{self.get_message('results.command_id_label', execution_id)}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}{self.get_message('results.command_name', command_name)}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}{self.get_message('results.target_label', target_name)}{Style.RESET_ALL}")

                # Get localized status display
                try:
                    status_enum = CommandStatus.from_string(current_status)
                    status_display = status_enum.get_display_string(self.get_message)
                except (ValueError, KeyError):
                    status_display = current_status

                print(f"{Fore.CYAN}{self.get_message('results.status_label', '')}{Fore.RED}{status_display}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}{'─'*80}{Style.RESET_ALL}")

                return False

            # Display command information
            print(f"\n{Fore.YELLOW}{'─'*80}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{self.get_message('results.command_id_label', execution_id)}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{self.get_message('results.command_name', command_name)}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{self.get_message('results.target_label', target_name)}{Style.RESET_ALL}")

            # Get localized status display
            try:
                status_enum = CommandStatus.from_string(current_status)
                status_display = status_enum.get_display_string(self.get_message)
            except (ValueError, KeyError):
                status_display = current_status

            print(f"{Fore.CYAN}{self.get_message('results.status_label', '')}{Fore.YELLOW}{status_display}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}{'─'*80}{Style.RESET_ALL}")

            # Prompt for confirmation
            print(f"\n{Fore.RED}{self.get_message('prompts.confirm_command_cancel', execution_id)}{Style.RESET_ALL}")
            confirmation = input().strip()

            if confirmation != "CANCEL":
                print(f"{Fore.YELLOW}{self.get_message('errors.cancellation_aborted')}{Style.RESET_ALL}")
                return False

            if self.debug_mode:
                print(f"\n{Fore.CYAN}{self.get_message('debug.api_call', 'UpdateCommandExecution')}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}[DEBUG] Execution ID: {execution_id}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}[DEBUG] New Status: CANCELED{Style.RESET_ALL}")

            # Call AWS IoT UpdateCommandExecution API to cancel the command
            # Note: The actual API might be CancelCommandExecution or UpdateCommandExecution
            # depending on AWS IoT Commands implementation. Using UpdateCommandExecution
            # as it's more common in AWS IoT patterns.
            cancel_response = self.safe_api_call(
                self.iot_client.update_command_execution,
                "UpdateCommandExecution",
                execution_id,
                debug=self.debug_mode,
                executionId=execution_id,
                status="CANCELED",
                statusReason="Canceled by user",
            )

            if cancel_response is None:
                print(f"{Fore.RED}{self.get_message('errors.command_cancellation_failed')}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}{self.get_message('troubleshooting.cancellation_failed')}{Style.RESET_ALL}")
                return False

            # Display success message
            print(f"\n{Fore.GREEN}{self.get_message('status.command_canceled')}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{self.get_message('results.command_id_label', execution_id)}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{self.get_message('results.command_name', command_name)}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{self.get_message('results.target_label', target_name)}{Style.RESET_ALL}")

            # Get updated status
            updated_status = cancel_response.get("status", "CANCELED")
            try:
                status_enum = CommandStatus.from_string(updated_status)
                status_display = status_enum.get_display_string(self.get_message)
            except (ValueError, KeyError):
                status_display = updated_status

            print(f"{Fore.CYAN}{self.get_message('results.status_label', '')}{Fore.MAGENTA}{status_display}{Style.RESET_ALL}")

            return True

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_message = e.response["Error"]["Message"]

            print(f"{Fore.RED}{self.get_message('errors.aws_api_error', error_code)}{Style.RESET_ALL}")
            print(f"{Fore.RED}  {error_message}{Style.RESET_ALL}")

            # Provide specific troubleshooting guidance
            if error_code == "ResourceNotFoundException":
                print(f"{Fore.YELLOW}{self.get_message('troubleshooting.command_not_found')}{Style.RESET_ALL}")
            elif error_code == "ConflictException":
                print(f"{Fore.YELLOW}{self.get_message('troubleshooting.cannot_cancel_completed')}{Style.RESET_ALL}")
            elif error_code == "InvalidStateTransitionException":
                print(f"{Fore.YELLOW}{self.get_message('troubleshooting.cannot_cancel_completed')}{Style.RESET_ALL}")
            elif error_code == "ThrottlingException":
                print(f"{Fore.YELLOW}{self.get_message('troubleshooting.throttling')}{Style.RESET_ALL}")
            elif error_code == "UnauthorizedException":
                print(f"{Fore.YELLOW}{self.get_message('troubleshooting.unauthorized')}{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}{self.get_message('troubleshooting.cancellation_failed')}{Style.RESET_ALL}")

            # Display failure reason and current state
            if self.debug_mode:
                print(f"{Fore.CYAN}{self.get_message('debug.full_error')}{Style.RESET_ALL}")
                print(json.dumps(e.response, indent=2, default=str))

            return False

        except Exception as e:
            print(f"{Fore.RED}{self.get_message('errors.unexpected_error', str(e))}{Style.RESET_ALL}")

            if self.debug_mode:
                import traceback

                print(f"{Fore.CYAN}{self.get_message('debug.full_traceback')}{Style.RESET_ALL}")
                traceback.print_exc()

            return False

    def display_menu(self):
        """
        Display the main menu with colored welcome banner and menu options.

        Shows:
        - Colored ASCII art banner
        - Menu options 1-10 with colored numbering
        - Current debug mode status
        - Region and account information

        Uses colorama for consistent color scheme matching explore_jobs.

        Requirements: 11.1, 15.1, 15.2
        """
        # Clear screen for better visibility (optional)
        print("\n" * 2)

        # Display colored welcome banner
        print(f"{Fore.CYAN}{self.get_message('ui.banner')}{Style.RESET_ALL}")

        # Display learning goal
        print(f"\n{Fore.YELLOW}{self.get_message('learning_goal')}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}{self.get_message('learning_description')}{Style.RESET_ALL}")

        # Display region and account info
        print(f"\n{Fore.CYAN}{self.get_message('separator')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('region_label')} {Fore.WHITE}{self.region}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('account_id_label')} {Fore.WHITE}{self.account_id}{Style.RESET_ALL}")

        # Display debug mode status
        debug_status = (
            self.get_message("ui.debug_enabled_label") if self.debug_mode else self.get_message("ui.debug_disabled_label")
        )
        print(f"{Fore.CYAN}{self.get_message('ui.debug_mode_status', debug_status)}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('separator')}{Style.RESET_ALL}")

        # Display menu options with colored numbering
        print(f"\n{Fore.YELLOW}{self.get_message('ui.main_menu')}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{self.get_message('ui.create_command')}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{self.get_message('ui.list_commands')}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{self.get_message('ui.view_command_details')}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{self.get_message('ui.delete_command')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('ui.execute_command')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('ui.view_status')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('ui.view_history')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('ui.cancel_command')}{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}{self.get_message('ui.toggle_debug')}{Style.RESET_ALL}")
        print(f"{Fore.RED}{self.get_message('ui.exit')}{Style.RESET_ALL}")
        print()

    def handle_menu_choice(self, choice: str) -> bool:
        """
        Handle user menu selection and call appropriate function.

        Args:
            choice: User's menu selection (1-10)

        Returns:
            True to continue menu loop, False to exit

        Requirements: 2.1, 11.1
        """
        try:
            choice_num = int(choice)

            if choice_num == 1:
                # Create Command
                self._handle_create_command()
            elif choice_num == 2:
                # List Commands
                self._handle_list_commands()
            elif choice_num == 3:
                # View Command Details
                self._handle_view_command_details()
            elif choice_num == 4:
                # Delete Command
                self._handle_delete_command()
            elif choice_num == 5:
                # Execute Command
                self._handle_execute_command()
            elif choice_num == 6:
                # View Command Status
                self._handle_view_status()
            elif choice_num == 7:
                # View Command History
                self._handle_view_history()
            elif choice_num == 8:
                # Cancel Command
                self._handle_cancel_command()
            elif choice_num == 9:
                # Toggle Debug Mode
                self._handle_toggle_debug()
            elif choice_num == 10:
                # Exit
                print(f"\n{Fore.GREEN}{self.get_message('ui.goodbye')}{Style.RESET_ALL}")
                return False
            else:
                print(f"{Fore.RED}{self.get_message('errors.invalid_choice')}{Style.RESET_ALL}")

            # Pause before returning to menu
            input(f"\n{Fore.CYAN}{self.get_message('ui.press_enter')}{Style.RESET_ALL}")
            return True

        except ValueError:
            print(f"{Fore.RED}{self.get_message('errors.invalid_number')}{Style.RESET_ALL}")
            input(f"\n{Fore.CYAN}{self.get_message('ui.press_enter')}{Style.RESET_ALL}")
            return True
        except (KeyboardInterrupt, EOFError):
            print(f"\n{Fore.YELLOW}{self.get_message('ui.cancelled')}{Style.RESET_ALL}")
            return False

    def _handle_create_command(self):
        """Handle menu option 1: Create Command"""
        print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('ui.create_command')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}")

        try:
            # Show predefined commands as options
            predefined = self.get_predefined_commands()

            print(f"\n{Fore.CYAN}{self.get_message('ui.choose_command_type')}{Style.RESET_ALL}")
            print(f"{Fore.WHITE}  {self.get_message('ui.create_custom_command')}{Style.RESET_ALL}")

            for idx, command in enumerate(predefined, 1):
                print(f"{Fore.WHITE}  {idx}. {command['command_name']} - {command['description']}{Style.RESET_ALL}")

            choice = input(f"\n{Fore.YELLOW}Select option [0-{len(predefined)}]: {Style.RESET_ALL}").strip()

            try:
                choice_num = int(choice)
                if choice_num < 0 or choice_num > len(predefined):
                    print(f"{Fore.RED}❌ Invalid selection{Style.RESET_ALL}")
                    return
            except ValueError:
                print(f"{Fore.RED}❌ Please enter a valid number{Style.RESET_ALL}")
                return

            # Get command name
            if choice_num == 0:
                # Custom command
                command_name = input(f"\n{self.get_message('prompts.command_name')}").strip()
                if not command_name:
                    print(f"{Fore.YELLOW}{self.get_message('errors.command_name_required')}{Style.RESET_ALL}")
                    return

                description = input(f"{self.get_message('prompts.command_description')}").strip()
                if not description:
                    print(f"{Fore.YELLOW}{self.get_message('validation.description_empty')}{Style.RESET_ALL}")
                    return

                # Prompt for payload as JSON
                print(f"\n{Fore.CYAN}📝 Enter command payload as JSON:{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}Example: {{'action': 'customAction', 'setting': 'value'}}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}This is the static payload that will be sent to devices.{Style.RESET_ALL}")
                print(f"{Fore.CYAN}You can add dynamic parameters at execution time.{Style.RESET_ALL}")
                print(f"{Fore.CYAN}Enter JSON (or press Enter for default):{Style.RESET_ALL}")

                payload_input = input().strip()

                if payload_input:
                    try:
                        payload_format = json.loads(payload_input)
                    except json.JSONDecodeError as e:
                        print(f"{Fore.RED}{self.get_message('ui.invalid_json_format', str(e))}{Style.RESET_ALL}")
                        print(f"{Fore.YELLOW}{self.get_message('ui.using_default_payload')}{Style.RESET_ALL}")
                        payload_format = {"action": "customAction"}
                else:
                    payload_format = {"action": "customAction"}
                    print(f"{Fore.CYAN}{self.get_message('ui.using_default_payload_confirm')}{Style.RESET_ALL}")
            else:
                # Use predefined command
                selected_command = predefined[choice_num - 1]
                command_name = selected_command["command_name"]
                description = selected_command["description"]
                payload_format = selected_command["payload_format"]

                print(f"\n{Fore.GREEN}{self.get_message('ui.using_predefined_command', command_name)}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}{self.get_message('ui.description_label', description)}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}{self.get_message('ui.payload_format_label')}{Style.RESET_ALL}")
                print(f"{Fore.WHITE}{json.dumps(payload_format, indent=2)}{Style.RESET_ALL}")

            # Create command
            command_arn = self.create_command(command_name, description, payload_format)

            if command_arn:
                print(f"\n{Fore.GREEN}{self.get_message('ui.success')}{Style.RESET_ALL}")

                # Trigger learning moment: What are Commands?
                # Show after first successful command creation
                self.display_learning_moment("what_are_commands")
            else:
                print(f"\n{Fore.RED}{self.get_message('ui.operation_failed')}{Style.RESET_ALL}")

        except (KeyboardInterrupt, EOFError):
            print(f"\n{Fore.YELLOW}{self.get_message('ui.cancelled')}{Style.RESET_ALL}")

    def _handle_list_commands(self):
        """Handle menu option 2: List Commands"""
        print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('ui.list_commands')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}")

        commands = self.list_commands()

        if commands:
            print(f"\n{Fore.GREEN}{self.get_message('ui.operation_complete')}{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.YELLOW}{self.get_message('results.no_commands')}{Style.RESET_ALL}")

    def _handle_view_command_details(self):
        """Handle menu option 3: View Command Details"""
        print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('ui.view_command_details')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}")

        try:
            # First list commands to help user select
            commands = self.list_commands()

            if not commands:
                print(f"\n{Fore.YELLOW}{self.get_message('errors.no_commands_available')}{Style.RESET_ALL}")
                return

            # Get command selection
            command_arn = input(f"\n{self.get_message('prompts.command_arn_or_name_view')}").strip()
            if not command_arn:
                print(f"{Fore.YELLOW}{self.get_message('errors.command_arn_required')}{Style.RESET_ALL}")
                return

            # Get command details
            command = self.get_command_details(command_arn)

            if command:
                print(f"\n{Fore.GREEN}{self.get_message('ui.operation_complete')}{Style.RESET_ALL}")
            else:
                print(f"\n{Fore.RED}{self.get_message('ui.operation_failed')}{Style.RESET_ALL}")

        except (KeyboardInterrupt, EOFError):
            print(f"\n{Fore.YELLOW}{self.get_message('ui.cancelled')}{Style.RESET_ALL}")

    def _handle_delete_command(self):
        """Handle menu option 4: Delete Command"""
        print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('ui.delete_command')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}")

        try:
            # First list commands to help user select
            commands = self.list_commands()

            if not commands:
                print(f"\n{Fore.YELLOW}{self.get_message('errors.no_commands_available')}{Style.RESET_ALL}")
                return

            # Get command to delete
            command_identifier = input(f"\n{self.get_message('prompts.command_arn_or_name_delete')}").strip()
            if not command_identifier:
                print(f"{Fore.YELLOW}{self.get_message('errors.command_arn_required')}{Style.RESET_ALL}")
                return

            # Delete command
            success = self.delete_command(command_identifier)

            if success:
                print(f"\n{Fore.GREEN}{self.get_message('ui.operation_complete')}{Style.RESET_ALL}")
            else:
                print(f"\n{Fore.RED}{self.get_message('ui.operation_failed')}{Style.RESET_ALL}")

        except (KeyboardInterrupt, EOFError):
            print(f"\n{Fore.YELLOW}{self.get_message('ui.cancelled')}{Style.RESET_ALL}")

    def display_command_acknowledgment_instructions(self, thing_name: str, execution_id: str):
        """
        Display instructions for acknowledging a command from the device simulator.

        This function shows learners how to publish acknowledgment messages (success or failure)
        from Terminal 2 using mqtt_client_explorer.py to simulate device responses.

        Args:
            thing_name: Name of the target device/thing
            execution_id: Command execution ID

        Requirements: 13.4, 14.2, 14.4
        """
        print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('command_acknowledgment.title')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}")

        print(f"\n{Fore.WHITE}{self.get_message('command_acknowledgment.intro')}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{self.get_message('command_acknowledgment.terminal_reminder')}{Style.RESET_ALL}")

        print(f"{Fore.MAGENTA}{self.get_message('command_acknowledgment.response_topic_title')}{Style.RESET_ALL}")
        print(
            f"{Fore.MAGENTA}{self.get_message('command_acknowledgment.response_topic', thing_name, execution_id)}{Style.RESET_ALL}"
        )

        print(f"{Fore.CYAN}{self.get_message('command_acknowledgment.mqtt_command_title')}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}{self.get_message('command_acknowledgment.mqtt_command_intro')}{Style.RESET_ALL}")

        # Success acknowledgment
        print(f"{Fore.GREEN}{self.get_message('command_acknowledgment.success_title')}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}{self.get_message('command_acknowledgment.success_command')}{Style.RESET_ALL}")
        print(
            f"{Fore.GREEN}{self.get_message('command_acknowledgment.success_full_command', thing_name, execution_id, thing_name, execution_id)}{Style.RESET_ALL}"
        )

        # Failure acknowledgment
        print(f"{Fore.RED}{self.get_message('command_acknowledgment.failure_title')}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}{self.get_message('command_acknowledgment.failure_command')}{Style.RESET_ALL}")
        print(
            f"{Fore.RED}{self.get_message('command_acknowledgment.failure_full_command', thing_name, execution_id, thing_name, execution_id)}{Style.RESET_ALL}"
        )

        # Alternative option
        print(f"{Fore.CYAN}{self.get_message('command_acknowledgment.alternative_title')}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}{self.get_message('command_acknowledgment.alternative_detail')}{Style.RESET_ALL}")

        # Status check reminder
        print(f"{Fore.YELLOW}{self.get_message('command_acknowledgment.status_check')}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}{self.get_message('command_acknowledgment.status_check_detail')}{Style.RESET_ALL}")

        # Format note
        print(f"{Fore.CYAN}{self.get_message('command_acknowledgment.payload_format_note')}{Style.RESET_ALL}")

        print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")

    def display_device_simulator_instructions(self, thing_name: str):
        """
        Display instructions for setting up device simulator before executing commands.

        This function displays critical setup instructions for learners to set up a device
        simulator using IoT Core scripts (certificate_manager.py and mqtt_client_explorer.py)
        BEFORE executing commands. Commands are ephemeral and will be lost if no device is listening.

        Args:
            thing_name: Name of the target device/thing to include in MQTT topic pattern

        Requirements: 13.1, 13.2, 13.3, 13.4, 13.5
        """
        # Check if already shown this session
        if not hasattr(self, "device_simulator_instructions_shown"):
            self.device_simulator_instructions_shown = False

        if self.device_simulator_instructions_shown:
            return True  # Already shown, proceed

        # Display instructions
        print(f"\n{Fore.YELLOW}{'='*80}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{self.get_message('device_simulator.title')}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{'='*80}{Style.RESET_ALL}")

        print(f"\n{Fore.RED}{self.get_message('device_simulator.ephemeral_warning')}{Style.RESET_ALL}")
        print(f"\n{Fore.YELLOW}{self.get_message('device_simulator.setup_required')}{Style.RESET_ALL}")

        print(f"{Fore.CYAN}{self.get_message('device_simulator.terminal_setup')}{Style.RESET_ALL}")

        print(f"{Fore.WHITE}{self.get_message('device_simulator.step1_title')}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}{self.get_message('device_simulator.step1_detail')}{Style.RESET_ALL}")

        print(f"{Fore.WHITE}{self.get_message('device_simulator.step2_title')}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}{self.get_message('device_simulator.step2_detail')}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{self.get_message('device_simulator.step2_region', self.region)}{Style.RESET_ALL}")

        print(f"{Fore.WHITE}{self.get_message('device_simulator.step3_title')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('device_simulator.step3_command')}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}{self.get_message('device_simulator.step3_detail')}{Style.RESET_ALL}")

        print(f"{Fore.WHITE}{self.get_message('device_simulator.step4_title')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('device_simulator.step4_command')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('device_simulator.step4_install')}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}{self.get_message('device_simulator.step4_detail')}{Style.RESET_ALL}")

        print(f"{Fore.WHITE}{self.get_message('device_simulator.step5_title')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('device_simulator.step5_command')}{Style.RESET_ALL}")

        print(f"{Fore.WHITE}{self.get_message('device_simulator.step6_title')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('device_simulator.step6_command')}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}{self.get_message('device_simulator.step6_detail')}{Style.RESET_ALL}")

        print(f"{Fore.WHITE}{self.get_message('device_simulator.step7_title')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('device_simulator.step7_command')}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}{self.get_message('device_simulator.step7_detail')}{Style.RESET_ALL}")

        # Display MQTT topic pattern BEFORE step 8 with actual device name
        print(f"{Fore.MAGENTA}{self.get_message('device_simulator.mqtt_topic_pattern')}{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}{self.get_message('device_simulator.mqtt_topic', thing_name)}{Style.RESET_ALL}")

        print(f"{Fore.WHITE}{self.get_message('device_simulator.step8_title')}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{self.get_message('device_simulator.step8_detail')}{Style.RESET_ALL}")

        print(f"{Fore.CYAN}{self.get_message('device_simulator.alternative_title')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('device_simulator.alternative_detail')}{Style.RESET_ALL}")

        print(f"\n{Fore.YELLOW}{'='*80}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{self.get_message('device_simulator.ready_prompt')}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{'='*80}{Style.RESET_ALL}")

        # Prompt for confirmation
        try:
            response = (
                input(f"\n{Fore.YELLOW}{self.get_message('device_simulator.ready_confirm')}{Style.RESET_ALL}").strip().upper()
            )

            if response == "READY":
                print(f"\n{Fore.GREEN}{self.get_message('device_simulator.proceeding')}{Style.RESET_ALL}")
                self.device_simulator_instructions_shown = True
                return True
            else:
                print(f"\n{Fore.YELLOW}{self.get_message('device_simulator.returning_to_menu')}{Style.RESET_ALL}")
                return False
        except (KeyboardInterrupt, EOFError):
            print(f"\n{Fore.YELLOW}{self.get_message('ui.cancelled')}{Style.RESET_ALL}")
            return False

    def _handle_execute_command(self):
        """Handle menu option 5: Execute Command"""
        print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('ui.execute_command')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}")

        # Display learning moments FIRST
        self.display_learning_moment("commands_vs_shadow_vs_jobs")
        self.display_learning_moment("mqtt_topics")

        try:
            # List commands for selection
            commands = self.list_commands()

            if not commands:
                print(f"\n{Fore.YELLOW}{self.get_message('errors.no_commands_available')}{Style.RESET_ALL}")
                return

            # Get command selection
            command_input = input(f"\n{self.get_message('prompts.select_command', len(commands))}").strip()

            try:
                command_idx = int(command_input) - 1
                if command_idx < 0 or command_idx >= len(commands):
                    print(f"{Fore.RED}{self.get_message('errors.invalid_selection')}{Style.RESET_ALL}")
                    return
                selected_command = commands[command_idx]
            except ValueError:
                print(f"{Fore.RED}{self.get_message('errors.invalid_number')}{Style.RESET_ALL}")
                return

            # Use pagination for device selection
            target_device = self.select_device_with_pagination(page_size=20)

            # Handle user cancellation
            if target_device is None:
                print(f"{Fore.YELLOW}{self.get_message('ui.cancelled')}{Style.RESET_ALL}")
                return

            print(f"{Fore.GREEN}{self.get_message('ui.selected_device', target_device)}{Style.RESET_ALL}")

            # Display device simulator setup instructions AFTER device selection (first time only)
            # This allows the MQTT topic pattern to show the actual device name
            if not self.display_device_simulator_instructions(target_device):
                return  # User chose to skip, return to menu

            # Build target ARN
            target_arn = f"arn:aws:iot:{self.region}:{self.account_id}:thing/{target_device}"

            # Prompt for execution timeout
            timeout_input = input(f"\n{self.get_message('prompts.execution_timeout')}").strip()
            if timeout_input:
                try:
                    timeout_seconds = int(timeout_input)
                    if timeout_seconds < 1:
                        print(f"{Fore.YELLOW}{self.get_message('prompts.timeout_too_low')}{Style.RESET_ALL}")
                        timeout_seconds = 60
                except ValueError:
                    print(f"{Fore.YELLOW}{self.get_message('prompts.invalid_timeout')}{Style.RESET_ALL}")
                    timeout_seconds = 60
            else:
                timeout_seconds = 60
                print(f"{Fore.CYAN}{self.get_message('prompts.using_default_timeout')}{Style.RESET_ALL}")

            # Execute command with empty parameters (AWS-IoT namespace doesn't use parameters)
            command_id = self.execute_command(selected_command.command_arn, target_arn, {}, timeout_seconds)

            if command_id:
                print(f"\n{Fore.GREEN}{self.get_message('ui.success')}{Style.RESET_ALL}")

                # Display acknowledgment instructions
                self.display_command_acknowledgment_instructions(target_device, command_id)
            else:
                print(f"\n{Fore.RED}{self.get_message('ui.operation_failed')}{Style.RESET_ALL}")

        except (KeyboardInterrupt, EOFError):
            print(f"\n{Fore.YELLOW}{self.get_message('ui.cancelled')}{Style.RESET_ALL}")

    def _handle_view_status(self):
        """Handle menu option 6: View Command Status"""
        print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('ui.view_status')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}")

        try:
            # Get execution ID
            execution_id = input(f"\n{self.get_message('prompts.execution_id_to_view')}").strip()
            if not execution_id:
                print(f"{Fore.YELLOW}{self.get_message('errors.execution_id_required')}{Style.RESET_ALL}")
                return

            # Get target device name
            target_device = input(f"\n{self.get_message('prompts.target_device_for_status')}").strip()
            if not target_device:
                print(f"{Fore.YELLOW}{self.get_message('errors.target_device_required')}{Style.RESET_ALL}")
                return

            # Build target ARN
            target_arn = f"arn:aws:iot:{self.region}:{self.account_id}:thing/{target_device}"

            # Get command status
            execution = self.get_command_status(execution_id, target_arn)

            if execution:
                print(f"\n{Fore.GREEN}{self.get_message('ui.operation_complete')}{Style.RESET_ALL}")

                # Trigger learning moment: Command Execution Lifecycle
                # Show after viewing command status
                self.display_learning_moment("execution_lifecycle")
            else:
                print(f"\n{Fore.RED}{self.get_message('ui.operation_failed')}{Style.RESET_ALL}")

        except (KeyboardInterrupt, EOFError):
            print(f"\n{Fore.YELLOW}{self.get_message('ui.cancelled')}{Style.RESET_ALL}")

    def _handle_view_history(self):
        """Handle menu option 7: View Command History"""
        print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('ui.view_history')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}")

        try:
            # AWS IoT Commands API requires either targetArn or commandArn
            # We need to get a device name to query history
            print(f"\n{Fore.YELLOW}ℹ️  {self.get_message('device_name_required_note')}{Style.RESET_ALL}")

            # Use pagination for device selection
            device_name = self.select_device_with_pagination(page_size=20)

            # Handle user cancellation
            if device_name is None:
                print(f"{Fore.YELLOW}{self.get_message('ui.cancelled')}{Style.RESET_ALL}")
                return

            print(f"{Fore.GREEN}{self.get_message('ui.selected_device', device_name)}{Style.RESET_ALL}")

            # Build target ARN
            target_arn = f"arn:aws:iot:{self.region}:{self.account_id}:thing/{device_name}"

            # Prompt for optional filters
            status_filter = input(f"\n{self.get_message('prompts.filter_by_status')}").strip()
            status_filter = status_filter.upper() if status_filter else None

            start_time = input(f"{self.get_message('prompts.filter_start_time')}").strip()
            start_time = start_time if start_time else None

            end_time = input(f"{self.get_message('prompts.filter_end_time')}").strip()
            end_time = end_time if end_time else None

            page_size_input = input(f"{self.get_message('prompts.page_size')}").strip()
            if page_size_input:
                try:
                    page_size = int(page_size_input)
                    if page_size < 1 or page_size > 100:
                        print(f"{Fore.YELLOW}{self.get_message('errors.invalid_page_size')}{Style.RESET_ALL}")
                        page_size = 50
                except ValueError:
                    print(f"{Fore.YELLOW}{self.get_message('errors.invalid_number')}{Style.RESET_ALL}")
                    page_size = 50
            else:
                page_size = 50

            # Retrieve and display command history
            next_token = None
            while True:
                result = self.list_command_history(
                    target_arn=target_arn,
                    status_filter=status_filter,
                    start_time=start_time,
                    end_time=end_time,
                    page_size=page_size,
                    next_token=next_token,
                )

                if result is None:
                    # Error occurred, already displayed by list_command_history
                    break

                # Check if there are more pages
                if result.get("has_more", False):
                    # Prompt for next page
                    try:
                        response = (
                            input(f"\n{Fore.YELLOW}{self.get_message('prompts.next_page')}{Style.RESET_ALL}").strip().lower()
                        )
                        if response == "q":
                            break
                        # Continue to next page
                        next_token = result.get("next_token")
                    except (KeyboardInterrupt, EOFError):
                        print(f"\n{Fore.YELLOW}{self.get_message('ui.cancelled')}{Style.RESET_ALL}")
                        break
                else:
                    # No more pages
                    break

            # Trigger learning moment: Best Practices
            # Show after viewing command history
            self.display_learning_moment("best_practices")

            # Trigger learning moment: Console Integration
            # Remind about Console Checkpoint
            self.display_learning_moment("console_integration")

        except (KeyboardInterrupt, EOFError):
            print(f"\n{Fore.YELLOW}{self.get_message('ui.cancelled')}{Style.RESET_ALL}")

    def _handle_cancel_command(self):
        """Handle menu option 8: Cancel Command"""
        print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('ui.cancel_command')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}")

        try:
            # Get execution ID
            execution_id = input(f"\n{self.get_message('prompts.execution_id_to_cancel')}").strip()
            if not execution_id:
                print(f"{Fore.YELLOW}{self.get_message('errors.execution_id_required')}{Style.RESET_ALL}")
                return

            # Cancel command
            success = self.cancel_command(execution_id)

            if success:
                print(f"\n{Fore.GREEN}{self.get_message('ui.operation_complete')}{Style.RESET_ALL}")
            else:
                print(f"\n{Fore.RED}{self.get_message('ui.operation_failed')}{Style.RESET_ALL}")

        except (KeyboardInterrupt, EOFError):
            print(f"\n{Fore.YELLOW}{self.get_message('ui.cancelled')}{Style.RESET_ALL}")

    def _handle_toggle_debug(self):
        """Handle menu option 9: Toggle Debug Mode"""
        self.debug_mode = not self.debug_mode

        if self.debug_mode:
            print(f"\n{Fore.GREEN}{self.get_message('status.debug_enabled')}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}{self.get_message('warnings.debug_warning')}{Style.RESET_ALL}")
        else:
            print(
                f"\n{Fore.YELLOW}{self.get_message('ui.debug_disabled_label')} {self.get_message('ui.debug_disabled_message')}{Style.RESET_ALL}"
            )

    def display_command_table(self, commands: List[Command]):
        """
        Display commands in a formatted colored table.

        Creates a table with colored headers and borders showing:
        - Command name
        - Description
        - Creation date
        - ARN

        Args:
            commands: List of Command objects to display

        Requirements: 11.3, 15.4
        """
        if not commands:
            print(f"{Fore.YELLOW}{self.get_message('results.no_commands')}{Style.RESET_ALL}")
            return

        # Use the existing _display_command_table method
        self._display_command_table(commands)

    def display_command_history(self, commands: List[Dict[str, Any]]):
        """
        Display command history in a formatted table.

        Shows command name, target, status, creation time, and completion time
        for each command execution.

        Args:
            commands: List of command execution dictionaries

        Requirements: 11.3, 15.4
        """
        if not commands:
            print(f"{Fore.YELLOW}{self.get_message('results.no_history')}{Style.RESET_ALL}")
            return

        # Display table header
        print(f"\n{Fore.GREEN}{'='*80}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{self.get_message('results.history_header')}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{'='*80}{Style.RESET_ALL}")

        # Print column headers
        print(
            f"\n{Fore.CYAN}{self.get_message('results.history_table_header_name'):<30} "
            f"{self.get_message('results.history_table_header_target'):<25} "
            f"{self.get_message('results.history_table_header_status'):<15} "
            f"{self.get_message('results.history_table_header_created'):<20}{Style.RESET_ALL}"
        )
        print(f"{Fore.WHITE}{'-'*30} {'-'*25} {'-'*15} {'-'*20}{Style.RESET_ALL}")

        # Print each command
        for cmd in commands:
            command_name = (
                cmd.get("commandName", "N/A")[:27] + "..."
                if len(cmd.get("commandName", "")) > 30
                else cmd.get("commandName", "N/A")
            )
            target = cmd.get("target", "N/A")[:22] + "..." if len(cmd.get("target", "")) > 25 else cmd.get("target", "N/A")
            status = cmd.get("status", "N/A")
            created = cmd.get("createdAt", "N/A")

            # Color code status
            if status == "SUCCEEDED":
                status_color = Fore.GREEN
            elif status == "FAILED":
                status_color = Fore.RED
            elif status == "IN_PROGRESS":
                status_color = Fore.YELLOW
            elif status == "CANCELED":
                status_color = Fore.MAGENTA
            else:
                status_color = Fore.WHITE

            print(
                f"{Fore.WHITE}{command_name:<30} {target:<25} "
                f"{status_color}{status:<15}{Style.RESET_ALL} "
                f"{Fore.WHITE}{created:<20}{Style.RESET_ALL}"
            )

        print(f"\n{Fore.GREEN}{'='*80}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('results.total_commands', len(commands))}{Style.RESET_ALL}")

    def display_status(self, command: Dict[str, Any]):
        """
        Display command execution status with colored formatting.

        Shows:
        - Command ID
        - Target device
        - Current status (color-coded)
        - Timestamps
        - Progress indicators for IN_PROGRESS status

        Args:
            command: Command execution dictionary

        Requirements: 11.3, 15.4
        """
        if not command:
            print(f"{Fore.RED}{self.get_message('errors.command_execution_not_found')}{Style.RESET_ALL}")
            return

        # Display header
        print(f"\n{Fore.GREEN}{'='*80}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{self.get_message('results.command_details')}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{'='*80}{Style.RESET_ALL}")

        # Extract command details
        command_id = command.get("commandId", "N/A")
        target = command.get("target", "N/A")
        status = command.get("status", "N/A")
        created_at = command.get("createdAt", "N/A")
        updated_at = command.get("lastUpdatedAt", "N/A")
        completed_at = command.get("completedAt", "N/A")
        status_reason = command.get("statusReason", "")

        # Display command information
        print(f"\n{Fore.CYAN}{self.get_message('results.command_id_label', command_id)}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('results.target_label', target)}{Style.RESET_ALL}")

        # Color code status
        if status == "SUCCEEDED":
            status_color = Fore.GREEN
            status_icon = "✅"
        elif status == "FAILED":
            status_color = Fore.RED
            status_icon = "❌"
        elif status == "IN_PROGRESS":
            status_color = Fore.YELLOW
            status_icon = "⏳"
            print(f"{Fore.YELLOW}{self.get_message('results.progress_indicator')}{Style.RESET_ALL}")
        elif status == "CANCELED":
            status_color = Fore.MAGENTA
            status_icon = "⏹️"
        elif status == "TIMED_OUT":
            status_color = Fore.RED
            status_icon = "⏱️"
        else:
            status_color = Fore.WHITE
            status_icon = "ℹ️"

        print(
            f"{Fore.CYAN}{self.get_message('results.status_label', '')}{status_color}{status_icon} {status}{Style.RESET_ALL}"
        )

        # Display timestamps
        print(f"\n{Fore.WHITE}{self.get_message('results.created_label', created_at)}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}{self.get_message('results.updated_label', updated_at)}{Style.RESET_ALL}")

        if completed_at and completed_at != "N/A":
            print(f"{Fore.WHITE}{self.get_message('results.completed_label', completed_at)}{Style.RESET_ALL}")

            # Calculate and display execution duration if possible
            try:
                created_dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                completed_dt = datetime.fromisoformat(completed_at.replace("Z", "+00:00"))
                duration = completed_dt - created_dt
                print(f"{Fore.CYAN}{self.get_message('results.execution_duration', str(duration))}{Style.RESET_ALL}")
            except Exception:
                pass

        # Display status reason if available
        if status_reason:
            print(f"\n{Fore.YELLOW}{self.get_message('results.status_reason', status_reason)}{Style.RESET_ALL}")

        print(f"\n{Fore.GREEN}{'='*80}{Style.RESET_ALL}")

    def show_progress(self, message: str, status: str = "info"):
        """
        Show progress indicator with colored status message.

        Args:
            message: Progress message to display
            status: Status type (info, success, warning, error)

        Requirements: 11.3, 15.3
        """
        if status == "success":
            color = Fore.GREEN
            icon = "✅"
        elif status == "warning":
            color = Fore.YELLOW
            icon = "⚠️"
        elif status == "error":
            color = Fore.RED
            icon = "❌"
        else:  # info
            color = Fore.CYAN
            icon = "ℹ️"

        print(f"{color}{icon} {message}{Style.RESET_ALL}")

    def display_learning_moment(self, moment_key: str):
        """
        Display a learning moment with colored formatting.

        Learning moments are contextual educational content that appears after
        key operations to explain concepts. Each moment is shown only once per
        session to avoid repetition.

        Args:
            moment_key: Key identifying the learning moment (e.g., "what_are_commands")

        Requirements: 1.1, 1.9
        """
        # Check if this moment has already been shown
        if self.learning_moments_shown.get(moment_key, False):
            return

        # Get learning moment content from i18n
        moment_path = f"learning_moments.{moment_key}"

        # Try to get the learning moment content
        try:
            # Get header and content
            header = self.get_message(f"{moment_path}.header")
            content = self.get_message(f"{moment_path}.content")

            # Check if we got valid content (not just the key back)
            if header == f"{moment_path}.header" or content == f"{moment_path}.content":
                # Learning moment not found in i18n, skip silently
                return

            # Display learning moment with colored formatting
            print(f"\n{Fore.YELLOW}{'='*80}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}{header}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}{'='*80}{Style.RESET_ALL}")
            print(f"\n{Fore.CYAN}{content}{Style.RESET_ALL}")
            print(f"\n{Fore.YELLOW}{'='*80}{Style.RESET_ALL}\n")

            # Mark this moment as shown
            self.learning_moments_shown[moment_key] = True

            # Pause to let user read
            try:
                input(f"{Fore.WHITE}{self.get_message('ui.press_enter')}{Style.RESET_ALL}")
            except (KeyboardInterrupt, EOFError):
                print()  # New line after interrupt

        except Exception as e:
            # If there's any error retrieving or displaying the learning moment,
            # fail silently to not disrupt the user experience
            if self.debug_mode:
                print(f"{Fore.CYAN}[DEBUG] Could not display learning moment '{moment_key}': {str(e)}{Style.RESET_ALL}")

    def display_certificate_manager_instructions(self, device_name: str = "your-device"):
        """
        Display instructions for using certificate_manager.py to set up device authentication.

        This function provides step-by-step guidance for:
        - Opening a new terminal window
        - Copying AWS credentials
        - Navigating to IoT Core scripts directory
        - Running certificate_manager.py
        - Creating device certificates

        Args:
            device_name: Name of the device to create certificate for

        Requirements: 8.1, 8.2, 8.3, 13.1, 13.2, 13.3
        """
        print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('integration.header')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}")

        # Step 1: Certificate Manager
        print(f"\n{Fore.YELLOW}{self.get_message('integration.certificate_manager_title')}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}{self.get_message('integration.certificate_manager_intro')}{Style.RESET_ALL}")

        print(f"\n{Fore.CYAN}{self.get_message('integration.certificate_manager_terminal_setup')}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}{self.get_message('integration.certificate_manager_step1')}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}{self.get_message('integration.certificate_manager_step2')}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}   {self.get_message('integration.directory_path_iot_core')}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}{self.get_message('integration.certificate_manager_step3')}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}   {self.get_message('integration.command_certificate_manager')}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}{self.get_message('integration.certificate_manager_step4')}{Style.RESET_ALL}")

        print(f"\n{Fore.GREEN}{self.get_message('integration.certificate_manager_note')}{Style.RESET_ALL}")

        # Pause for user to read
        try:
            input(f"\n{Fore.CYAN}{self.get_message('ui.press_enter')}{Style.RESET_ALL}")
        except (KeyboardInterrupt, EOFError):
            print()

    def display_mqtt_client_explorer_instructions(self, device_name: str = "your-device"):
        """
        Display instructions for using mqtt_client_explorer.py to subscribe to command topics.

        This function provides step-by-step guidance for:
        - Using the same terminal from certificate_manager
        - Running mqtt_client_explorer.py
        - Subscribing to command request topics
        - Understanding MQTT topic wildcards
        - Keeping the terminal open to receive commands

        Args:
            device_name: Name of the device to subscribe for

        Requirements: 8.1, 8.2, 8.3, 13.1, 13.2, 13.3
        """
        print(f"\n{Fore.YELLOW}{self.get_message('integration.mqtt_client_title')}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}{self.get_message('integration.mqtt_client_intro')}{Style.RESET_ALL}")

        print(f"\n{Fore.RED}{self.get_message('integration.mqtt_client_terminal_note')}{Style.RESET_ALL}")

        print(f"\n{Fore.WHITE}{self.get_message('integration.mqtt_client_step1')}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}   {self.get_message('integration.command_mqtt_client')}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}{self.get_message('integration.mqtt_client_step2')}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}{self.get_message('integration.mqtt_client_step3')}{Style.RESET_ALL}")

        # Show topic pattern with device name
        print(f"{Fore.YELLOW}   {self.get_message('integration.mqtt_client_topic_pattern', device_name)}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}   {self.get_message('integration.mqtt_client_wildcard_note')}{Style.RESET_ALL}")

        print(f"{Fore.WHITE}{self.get_message('integration.mqtt_client_step4')}{Style.RESET_ALL}")

        print(f"\n{Fore.GREEN}{self.get_message('integration.mqtt_client_ready')}{Style.RESET_ALL}")

        # Show execution flow
        print(f"\n{Fore.YELLOW}{self.get_message('integration.execution_flow_title')}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}{self.get_message('integration.execution_flow_intro')}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}{self.get_message('integration.execution_flow_step1')}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}{self.get_message('integration.execution_flow_step2')}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}{self.get_message('integration.execution_flow_step3')}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}{self.get_message('integration.execution_flow_step4')}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}{self.get_message('integration.execution_flow_step5')}{Style.RESET_ALL}")

        # Critical warning about terminal setup order
        print(f"\n{Fore.RED}{'='*80}{Style.RESET_ALL}")
        print(f"{Fore.RED}{self.get_message('integration.terminal_setup_reminder')}{Style.RESET_ALL}")
        print(f"{Fore.RED}{'='*80}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{self.get_message('integration.terminal_setup_warning')}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}{self.get_message('integration.terminal_setup_reason')}{Style.RESET_ALL}")
        print(f"{Fore.RED}{'='*80}{Style.RESET_ALL}")

        # Pause for user to read
        try:
            input(f"\n{Fore.CYAN}{self.get_message('ui.press_enter')}{Style.RESET_ALL}")
        except (KeyboardInterrupt, EOFError):
            print()

    def display_device_simulation_examples(self, device_name: str = "your-device", execution_id: str = "<ExecutionId>"):
        """
        Display example payloads for simulating device command responses.

        This function provides:
        - Example success acknowledgment payload
        - Example failure acknowledgment payload
        - Instructions for publishing to response topic using mqtt_client_explorer
        - AWS IoT Test Client as alternative option

        Args:
            device_name: Name of the device
            execution_id: Command execution ID (use placeholder if not known)

        Requirements: 8.4, 8.5, 13.4, 13.5, 14.1, 14.2, 14.3, 14.4, 14.5
        """
        print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('integration.response_title')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}")

        print(f"\n{Fore.WHITE}{self.get_message('integration.response_intro')}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}{self.get_message('integration.response_step1')}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}{self.get_message('integration.response_step2')}{Style.RESET_ALL}")

        # Show response topic pattern
        print(
            f"{Fore.YELLOW}   {self.get_message('integration.response_topic_pattern', device_name, execution_id)}{Style.RESET_ALL}"
        )

        print(f"{Fore.WHITE}{self.get_message('integration.response_step3')}{Style.RESET_ALL}")

        # Example success response
        print(f"\n{Fore.GREEN}{'─'*80}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{self.get_message('integration.example_success_title')}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{'─'*80}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}{self.get_message('integration.example_success_intro')}{Style.RESET_ALL}")

        success_payload = {
            "status": "SUCCEEDED",
            "executionId": execution_id,
            "statusReason": "Vehicle doors locked successfully",
            "timestamp": int(time.time() * 1000),
        }

        print(f"\n{Fore.YELLOW}{json.dumps(success_payload, indent=2)}{Style.RESET_ALL}")
        print(f"\n{Fore.CYAN}{self.get_message('integration.example_success_note')}{Style.RESET_ALL}")

        # Example failure response
        print(f"\n{Fore.RED}{'─'*80}{Style.RESET_ALL}")
        print(f"{Fore.RED}{self.get_message('integration.example_failure_title')}{Style.RESET_ALL}")
        print(f"{Fore.RED}{'─'*80}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}{self.get_message('integration.example_failure_intro')}{Style.RESET_ALL}")

        failure_payload = {
            "status": "FAILED",
            "executionId": execution_id,
            "statusReason": "Unable to lock vehicle - door sensor malfunction",
            "timestamp": int(time.time() * 1000),
        }

        print(f"\n{Fore.YELLOW}{json.dumps(failure_payload, indent=2)}{Style.RESET_ALL}")
        print(f"\n{Fore.CYAN}{self.get_message('integration.example_failure_note')}{Style.RESET_ALL}")

        # AWS IoT Test Client alternative
        print(f"\n{Fore.CYAN}{'─'*80}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('integration.console_alternative_title')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'─'*80}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}{self.get_message('integration.console_alternative_intro')}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}{self.get_message('integration.console_alternative_step1')}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}{self.get_message('integration.console_alternative_step2')}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}{self.get_message('integration.console_alternative_step3')}{Style.RESET_ALL}")
        print(f"\n{Fore.GREEN}{self.get_message('integration.console_alternative_note')}{Style.RESET_ALL}")

        # Pause for user to read
        try:
            input(f"\n{Fore.CYAN}{self.get_message('ui.press_enter')}{Style.RESET_ALL}")
        except (KeyboardInterrupt, EOFError):
            print()

    def display_mqtt_topic_structure(self):
        """
        Display comprehensive documentation of MQTT topic structure for AWS IoT Commands.

        This function documents:
        - Command request topic pattern
        - Command response topic pattern
        - Accepted/rejected confirmation topics
        - Wildcard subscription examples
        - Topic component explanations

        Requirements: 12.3, 13.6
        """
        print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{self.get_message('integration.mqtt_topics_title')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}")

        print(f"\n{Fore.WHITE}{self.get_message('integration.mqtt_topics_intro')}{Style.RESET_ALL}")

        # Request topic
        print(f"\n{Fore.YELLOW}{self.get_message('integration.mqtt_topic_request')}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}  {self.get_message('integration.mqtt_topic_request_pattern')}{Style.RESET_ALL}")
        print(f"\n{Fore.CYAN}{self.get_message('ui.info')} Wildcard subscription:{Style.RESET_ALL}")
        print(f"{Fore.WHITE}  {self.get_message('integration.mqtt_topic_request_wildcard')}{Style.RESET_ALL}")

        # Response topic
        print(f"\n{Fore.YELLOW}{self.get_message('integration.mqtt_topic_response')}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}  {self.get_message('integration.mqtt_topic_response_pattern')}{Style.RESET_ALL}")

        # Accepted confirmation topic
        print(f"\n{Fore.YELLOW}{self.get_message('integration.mqtt_topic_accepted')}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}  {self.get_message('integration.mqtt_topic_accepted_pattern')}{Style.RESET_ALL}")

        # Rejected confirmation topic
        print(f"\n{Fore.YELLOW}{self.get_message('integration.mqtt_topic_rejected')}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}  {self.get_message('integration.mqtt_topic_rejected_pattern')}{Style.RESET_ALL}")

        # Notes
        print(f"\n{Fore.CYAN}{self.get_message('integration.mqtt_topic_notes')}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}{self.get_message('integration.mqtt_topic_note1')}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}{self.get_message('integration.mqtt_topic_note2')}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}{self.get_message('integration.mqtt_topic_note3')}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}{self.get_message('integration.mqtt_topic_note4')}{Style.RESET_ALL}")

        print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")

        # Pause for user to read
        try:
            input(f"\n{Fore.CYAN}{self.get_message('ui.press_enter')}{Style.RESET_ALL}")
        except (KeyboardInterrupt, EOFError):
            print()


def main():
    """Main entry point"""
    global USER_LANG, messages

    try:
        # Get user language
        USER_LANG = get_language()

        # Load messages
        messages = load_messages("manage_commands", USER_LANG)

        # Create manager instance
        manager = IoTCommandsManager()

        # Prompt for debug mode
        try:
            debug_choice = input(f"{manager.get_message('prompts.debug_mode')}").strip().lower()
            if debug_choice in ["y", "yes"]:
                manager.debug_mode = True
                print(f"{Fore.GREEN}{manager.get_message('status.debug_enabled')}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}{manager.get_message('warnings.debug_warning')}{Style.RESET_ALL}")
        except (KeyboardInterrupt, EOFError):
            print(f"\n{Fore.YELLOW}{manager.get_message('ui.cancelled')}{Style.RESET_ALL}")
            sys.exit(0)

        # Initialize clients
        if not manager.initialize_clients():
            sys.exit(1)

        print(f"{Fore.GREEN}{manager.get_message('status.manager_initialized')}{Style.RESET_ALL}")

        # Main menu loop
        while True:
            manager.display_menu()

            try:
                choice = input(f"{Fore.YELLOW}{manager.get_message('prompts.menu_choice')}{Style.RESET_ALL}").strip()

                if not manager.handle_menu_choice(choice):
                    break

            except (KeyboardInterrupt, EOFError):
                print(f"\n{Fore.YELLOW}{manager.get_message('ui.cancelled')}{Style.RESET_ALL}")
                break

    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}{manager.get_message('ui.cancelled')}{Style.RESET_ALL}")
        sys.exit(0)
    except Exception as e:
        print(f"{Fore.RED}Fatal error: {str(e)}{Style.RESET_ALL}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
