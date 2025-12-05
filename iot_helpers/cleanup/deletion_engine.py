"""
Deletion Engine Module

This module provides the DeletionEngine class for safely deleting AWS IoT resources
with rate limiting, error handling, and dry-run support.
"""

import sys
import os
import time
from typing import Dict, List, Any, Optional
from botocore.exceptions import ClientError

# Add repository root to path for i18n imports
# Navigate 3 levels up from iot_helpers/cleanup/deletion_engine.py to repository root
repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from i18n.loader import load_messages


# Rate limits for AWS IoT operations (Transactions Per Second)
# These limits are set conservatively below AWS service limits for safety
RATE_LIMITS = {
    # IoT Core operations
    "things": 80,              # AWS limit: 100 TPS, use 80 for safety margin
    "static_groups": 80,       # AWS limit: 100 TPS for static groups
    "dynamic_groups": 4,       # AWS limit: 5 TPS for dynamic groups, use 4 for safety
    "thing_types": 8,          # AWS limit: 10 TPS, use 8 for safety
    "certificates": 80,        # AWS limit: 100 TPS
    "shadows": 80,             # AWS limit: 100 TPS
    
    # IoT Device Management operations
    "packages": 8,             # AWS limit: 10 TPS, use 8 for safety
    "package_versions": 8,     # AWS limit: 10 TPS
    "jobs": 10,                # Conservative limit for job operations
    "commands": 10,            # AWS limit: 10 TPS for IoT commands
    
    # Other AWS services
    "s3_operations": 100,      # S3 has high limits (3500+ TPS)
    "iam_operations": 10,      # Conservative limit for IAM operations
}


class DeletionEngine:
    """
    Engine for deleting AWS IoT resources with safety mechanisms.
    
    Features:
    - Rate limiting to respect AWS service limits
    - Dry-run mode for safe preview
    - Error handling with graceful degradation
    - Detailed statistics tracking
    """
    
    def __init__(self, clients: Dict[str, Any], debug_mode: bool = False, dry_run: bool = False, language: str = 'en'):
        """
        Initialize the deletion engine.
        
        Args:
            clients: Dictionary of AWS clients (iot_client, s3_client, iam_client)
            debug_mode: Whether to show detailed debug information
            dry_run: Whether to simulate deletions without actually deleting
            language: Language code for i18n messages (default: 'en')
        """
        self.clients = clients
        self.debug_mode = debug_mode
        self.dry_run = dry_run
        
        # Extract individual clients for convenience
        self.iot_client = clients.get('iot_client')
        self.s3_client = clients.get('s3_client')
        self.iam_client = clients.get('iam_client')
        
        # Load i18n messages
        self.messages = load_messages('deletion_engine', language)
        
        # Track last operation time for rate limiting
        self._last_operation_time = {}
    
    def _apply_rate_limit(self, resource_type: str) -> None:
        """
        Apply rate limiting for the specified resource type.
        
        This method ensures we don't exceed AWS service limits by adding
        appropriate delays between operations.
        
        Args:
            resource_type: Type of resource being operated on
        """
        # Get the rate limit for this resource type
        rate_limit = RATE_LIMITS.get(resource_type, 10)  # Default to 10 TPS if not specified
        
        # Calculate minimum time between operations (in seconds)
        min_interval = 1.0 / rate_limit
        
        # Get the last operation time for this resource type
        last_time = self._last_operation_time.get(resource_type, 0)
        current_time = time.time()
        
        # Calculate how long we need to wait
        elapsed = current_time - last_time
        if elapsed < min_interval:
            wait_time = min_interval - elapsed
            if self.debug_mode:
                msg = self.messages.get('debug', {}).get('rate_limiting', '')
                if msg:
                    print(f"[DEBUG] {msg.format(wait_time, resource_type)}")
            time.sleep(wait_time)
        
        # Update the last operation time
        self._last_operation_time[resource_type] = time.time()

    
    def delete_resources(
        self,
        resources: List[Dict[str, Any]],
        resource_type: str,
        identifier: Any,
        dependency_handler: Any = None,
        custom_prefix: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Delete a list of resources with identification and rate limiting.
        
        This method:
        1. Identifies which resources belong to the workshop
        2. Deletes workshop resources (or simulates in dry-run mode)
        3. Applies rate limiting between deletions
        4. Handles errors gracefully
        5. Returns detailed statistics
        
        Args:
            resources: List of resource dictionaries from AWS API
            resource_type: Type of resources (thing, thing_group, package, etc.)
            identifier: ResourceIdentifier instance for identifying workshop resources
            dependency_handler: DependencyHandler instance for handling dependencies
            custom_prefix: Optional custom thing prefix for identification
            
        Returns:
            Dictionary with statistics:
            {
                "total": int,           # Total resources processed
                "deleted": int,         # Successfully deleted
                "skipped": int,         # Skipped (non-workshop)
                "failed": int,          # Failed to delete
                "skipped_resources": list[str]  # Names of skipped resources
            }
        """
        # Initialize statistics
        stats = {
            "total": len(resources),
            "deleted": 0,
            "skipped": 0,
            "failed": 0,
            "skipped_resources": []
        }
        
        if self.debug_mode:
            msg = self.messages.get('debug', {}).get('processing_resources', '')
            if msg:
                print(f"\n[DEBUG] {msg.format(len(resources), resource_type)}")
        
        # Process each resource
        for idx, resource in enumerate(resources, 1):
            # Extract resource name/ID based on resource type
            resource_name = self._get_resource_name(resource, resource_type)
            
            if self.debug_mode:
                msg = self.messages.get('debug', {}).get('processing_item', '')
                if msg:
                    print(f"\n[DEBUG] {msg.format(idx, len(resources), resource_name)}")
            
            try:
                # Identify if this is a workshop resource
                is_workshop, identification_method = identifier.identify_resource(
                    resource, resource_type, custom_prefix
                )
                
                if self.debug_mode:
                    msg = self.messages.get('debug', {}).get('resource_name', '')
                    if msg:
                        print(f"[DEBUG] {msg.format(resource_name)}")
                    msg = self.messages.get('debug', {}).get('is_workshop_resource', '')
                    if msg:
                        print(f"[DEBUG] {msg.format(is_workshop)}")
                    msg = self.messages.get('debug', {}).get('identification_method', '')
                    if msg:
                        print(f"[DEBUG] {msg.format(identification_method)}")
                
                if not is_workshop:
                    # Skip non-workshop resources
                    stats["skipped"] += 1
                    stats["skipped_resources"].append(resource_name)
                    if self.debug_mode:
                        msg = self.messages.get('debug', {}).get('skipping_non_workshop', '')
                        if msg:
                            print(f"[DEBUG] {msg.format(resource_name)}")
                    continue
                
                if self.debug_mode:
                    msg = self.messages.get('debug', {}).get('proceeding_to_delete', '')
                    if msg:
                        print(f"[DEBUG] {msg.format(resource_name)}")
                
                # Apply rate limiting before deletion
                self._apply_rate_limit(resource_type)
                
                # Delete the resource (with dependencies if handler provided)
                if dependency_handler:
                    if self.debug_mode:
                        msg = self.messages.get('debug', {}).get('deleting_with_dependencies', '')
                        if msg:
                            print(f"[DEBUG] {msg}")
                    success, deleted_items = dependency_handler.delete_with_dependencies(
                        resource, resource_type, self.dry_run
                    )
                    if self.debug_mode:
                        msg = self.messages.get('debug', {}).get('dependency_handler_result', '')
                        if msg:
                            print(f"[DEBUG] {msg.format(success, deleted_items)}")
                else:
                    if self.debug_mode:
                        msg = self.messages.get('debug', {}).get('deleting_single_resource', '')
                        if msg:
                            print(f"[DEBUG] {msg}")
                    success = self._delete_single_resource(resource, resource_type)
                    if self.debug_mode:
                        msg = self.messages.get('debug', {}).get('single_resource_result', '')
                        if msg:
                            print(f"[DEBUG] {msg.format(success)}")
                
                if success:
                    stats["deleted"] += 1
                    if self.debug_mode:
                        msg = self.messages.get('debug', {}).get('successfully_deleted', '')
                        if msg:
                            print(f"[DEBUG] {msg.format(resource_name)}")
                else:
                    stats["failed"] += 1
                    if self.debug_mode:
                        msg = self.messages.get('debug', {}).get('failed_to_delete', '')
                        if msg:
                            print(f"[DEBUG] {msg.format(resource_name)}")
                        
            except Exception as e:
                # Handle errors gracefully - log and continue
                stats["failed"] += 1
                if self.debug_mode:
                    msg = self.messages.get('error', {}).get('processing_error', '')
                    if msg:
                        print(f"[ERROR] {msg.format(resource_name, str(e))}")
                    import traceback
                    traceback.print_exc()
                continue
        
        if self.debug_mode:
            msg = self.messages.get('debug', {}).get('completed_processing', '')
            if msg:
                print(f"\n[DEBUG] {msg.format(resource_type)}")
            msg = self.messages.get('debug', {}).get('processing_stats', '')
            if msg:
                print(f"[DEBUG] {msg.format(stats['total'], stats['deleted'], stats['skipped'], stats['failed'])}")
        
        return stats
    
    def _get_resource_name(self, resource: Dict[str, Any], resource_type: str) -> str:
        """
        Extract the resource name/ID from a resource dictionary.
        
        Args:
            resource: Resource dictionary from AWS API
            resource_type: Type of resource
            
        Returns:
            Resource name or ID
        """
        # Map resource types to their name/ID fields
        # Note: Use the exact field names returned by AWS APIs
        name_fields = {
            "thing": "thingName",
            "thing-group": "groupName",  # Fixed: was "thing_group"
            "thing-type": "thingTypeName",  # Fixed: was "thing_type"
            "package": "packageName",
            "job": "jobId",
            "command": "commandId",
            "certificate": "certificateId",
            "shadow": "shadowName",
            "s3-bucket": "Name",  # Fixed: was "s3_bucket", S3 API returns "Name"
            "iam-role": "RoleName"  # Fixed: was "iam_role"
        }
        
        field = name_fields.get(resource_type, "name")
        return resource.get(field, resource.get("name", "unknown"))
    
    def _delete_single_resource(self, resource: Dict[str, Any], resource_type: str) -> bool:
        """
        Delete a single resource without dependencies.
        
        Args:
            resource: Resource to delete
            resource_type: Type of resource
            
        Returns:
            True if deletion succeeded, False otherwise
        """
        if self.dry_run:
            # In dry-run mode, just simulate the deletion
            return True
        
        try:
            resource_name = self._get_resource_name(resource, resource_type)
            
            # Delete based on resource type
            if resource_type == "thing":
                self.iot_client.delete_thing(thingName=resource_name)
            elif resource_type in ["thing-group", "thing_group"]:
                self.iot_client.delete_thing_group(thingGroupName=resource_name)
            elif resource_type in ["thing-type", "thing_type"]:
                self.iot_client.delete_thing_type(thingTypeName=resource_name)
            elif resource_type == "package":
                self.iot_client.delete_package(packageName=resource_name)
            elif resource_type == "command":
                self.iot_client.delete_command(commandId=resource_name)
            elif resource_type == "job":
                self.iot_client.delete_job(jobId=resource_name, force=True)
            elif resource_type == "certificate":
                self.iot_client.delete_certificate(certificateId=resource_name, forceDelete=True)
            elif resource_type in ["s3-bucket", "s3_bucket"]:
                self.s3_client.delete_bucket(Bucket=resource_name)
            elif resource_type in ["iam-role", "iam_role"]:
                self.iam_client.delete_role(RoleName=resource_name)
            else:
                if self.debug_mode:
                    msg = self.messages.get('warning', {}).get('unknown_resource_type', '')
                    if msg:
                        print(f"[WARNING] {msg.format(resource_type)}")
                return False
            
            return True
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            
            # ResourceNotFoundException is expected if resource was already deleted
            if error_code == 'ResourceNotFoundException':
                return True  # Consider it a success
            
            if self.debug_mode:
                msg = self.messages.get('error', {}).get('aws_api_error', '')
                if msg:
                    print(f"[ERROR] {msg.format(resource_name, error_code)}")
            return False
            
        except Exception as e:
            if self.debug_mode:
                msg = self.messages.get('error', {}).get('unexpected_error', '')
                if msg:
                    print(f"[ERROR] {msg.format(str(e))}")
            return False
