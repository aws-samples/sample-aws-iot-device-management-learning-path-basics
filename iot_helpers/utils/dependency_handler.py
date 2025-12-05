"""
Dependency Handler Module

This module provides functionality to handle resource dependencies during cleanup operations.
It ensures that dependent resources are deleted in the correct order to avoid errors and
maintain data integrity.

The DependencyHandler class manages:
- Deletion order for different resource types
- Shadow deletion for things
- Certificate detachment and deletion
- Package version deletion
- S3 object deletion
- IAM policy deletion
- Job cancellation
"""

import sys
import os
import time

# Add repository root to path for i18n imports
# Navigate 3 levels up from iot_helpers/utils/dependency_handler.py to repository root
repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from i18n.loader import load_messages


# Deletion order constants
# These define the correct order for deleting resources to handle dependencies
DELETION_ORDER = {
    "all_resources": [
        "thing_shadows",      # Delete shadows first (attached to things)
        "certificates",       # Delete certs (detach from things first)
        "things",            # Delete things
        "thing_groups",      # Delete groups
        "commands",          # Delete IoT commands
        "jobs",              # Delete jobs
        "packages",          # Delete packages (and versions)
        "s3_buckets",        # Delete buckets (and objects)
        "package_config",    # Disable package configuration
        "iam_roles",         # Delete IAM roles (and policies)
        "fleet_indexing",    # Disable fleet indexing
        "thing_types"        # Delete thing types (deprecate first, wait 5 min)
    ],
    "things_only": [
        "thing_shadows",     # Delete shadows first
        "certificates",      # Delete certificates
        "things"            # Delete things
    ],
    "groups_only": [
        "thing_groups"      # Delete groups only
    ]
}


class DependencyHandler:
    """
    Handles resource dependencies during cleanup operations.
    
    This class ensures that dependent resources are deleted in the correct order
    to avoid errors. For example, thing shadows and certificates must be deleted
    before the thing itself can be deleted.
    """
    
    def __init__(self, iot_client, s3_client, iam_client, language='en', debug_mode=False):
        """
        Initialize the DependencyHandler.
        
        Args:
            iot_client: Boto3 IoT client
            s3_client: Boto3 S3 client
            iam_client: Boto3 IAM client
            language: Language code for i18n messages (default: 'en')
            debug_mode: Whether to enable debug output
        """
        self.iot_client = iot_client
        self.s3_client = s3_client
        self.iam_client = iam_client
        self.debug_mode = debug_mode
        
        # Load i18n messages
        self.messages = load_messages('dependency_handler', language)
    
    def get_deletion_order(self, choice):
        """
        Get the correct deletion order for resources based on cleanup choice.
        
        Args:
            choice: Cleanup choice (1=all resources, 2=things only, 3=groups only)
            
        Returns:
            list: List of resource types in deletion order
            
        Raises:
            ValueError: If choice is not valid
        """
        if choice == 1:
            return DELETION_ORDER["all_resources"]
        elif choice == 2:
            return DELETION_ORDER["things_only"]
        elif choice == 3:
            return DELETION_ORDER["groups_only"]
        else:
            raise ValueError(f"Invalid cleanup choice: {choice}. Must be 1, 2, or 3.")
    
    def delete_thing_shadows(self, thing_name):
        """
        Delete all shadows for a thing (classic and named shadows).
        
        Args:
            thing_name: Name of the thing
            
        Returns:
            list: List of deleted shadow names
        """
        deleted_shadows = []
        
        try:
            if self.debug_mode:
                msg = self.messages.get('debug.listing_shadows', '')
                if msg:
                    print(msg.format(thing_name))
            
            # List all named shadows for the thing
            try:
                response = self.iot_client.list_named_shadows_for_thing(thingName=thing_name)
                named_shadows = response.get('results', [])
                
                if self.debug_mode and named_shadows:
                    msg = self.messages.get('debug.found_named_shadows', '')
                    if msg:
                        print(msg.format(len(named_shadows), thing_name))
                
                # Delete each named shadow
                for shadow_name in named_shadows:
                    try:
                        self.iot_client.delete_thing_shadow(
                            thingName=thing_name,
                            shadowName=shadow_name
                        )
                        deleted_shadows.append(f"{shadow_name} (named)")
                        
                        if self.debug_mode:
                            msg = self.messages.get('debug.deleted_named_shadow', '')
                            if msg:
                                print(msg.format(shadow_name, thing_name))
                            
                    except Exception as e:
                        if self.debug_mode:
                            msg = self.messages.get('debug.shadow_delete_error', '')
                            if msg:
                                print(msg.format(shadow_name, thing_name, str(e)))
                        
            except self.iot_client.exceptions.ResourceNotFoundException:
                # No named shadows exist
                if self.debug_mode:
                    msg = self.messages.get('debug.no_named_shadows', '')
                    if msg:
                        print(msg.format(thing_name))
            
            # Try to delete classic shadow
            try:
                self.iot_client.delete_thing_shadow(thingName=thing_name)
                deleted_shadows.append("classic")
                
                if self.debug_mode:
                    msg = self.messages.get('debug.deleted_classic_shadow', '')
                    if msg:
                        print(msg.format(thing_name))
                    
            except self.iot_client.exceptions.ResourceNotFoundException:
                # Classic shadow doesn't exist
                if self.debug_mode:
                    msg = self.messages.get('debug.no_classic_shadow', '')
                    if msg:
                        print(msg.format(thing_name))
                    
            except Exception as e:
                if self.debug_mode:
                    msg = self.messages.get('debug.shadow_delete_error', '')
                    if msg:
                        print(msg.format('classic', thing_name, str(e)))
            
            return deleted_shadows
            
        except Exception as e:
            if self.debug_mode:
                msg = self.messages.get('debug.shadow_list_error', '')
                if msg:
                    print(msg.format(thing_name, str(e)))
            return deleted_shadows
    
    def detach_and_delete_certificates(self, thing_name):
        """
        Detach and delete all certificates attached to a thing.
        
        This method lists all principals (certificates) attached to a thing,
        detaches each one, updates it to INACTIVE status, and then deletes it.
        
        Args:
            thing_name: Name of the thing
            
        Returns:
            list: List of deleted certificate IDs
        """
        deleted_certificates = []
        
        try:
            if self.debug_mode:
                msg = self.messages.get('debug.listing_principals', '')
                if msg:
                    print(msg.format(thing_name))
            
            # List all principals attached to the thing
            response = self.iot_client.list_thing_principals(thingName=thing_name)
            principals = response.get('principals', [])
            
            if self.debug_mode and principals:
                msg = self.messages.get('debug.found_principals', '')
                if msg:
                    print(msg.format(len(principals), thing_name))
            
            # Process each principal (certificate)
            for principal_arn in principals:
                try:
                    # Extract certificate ID from ARN
                    # ARN format: arn:aws:iot:region:account:cert/certificateId
                    certificate_id = principal_arn.split('/')[-1]
                    
                    if self.debug_mode:
                        msg = self.messages.get('debug.processing_certificate', '')
                        if msg:
                            print(msg.format(certificate_id, thing_name))
                    
                    # Step 1: Detach certificate from thing
                    self.iot_client.detach_thing_principal(
                        thingName=thing_name,
                        principal=principal_arn
                    )
                    
                    if self.debug_mode:
                        msg = self.messages.get('debug.detached_certificate', '')
                        if msg:
                            print(msg.format(certificate_id, thing_name))
                    
                    # Step 2: Update certificate to INACTIVE
                    self.iot_client.update_certificate(
                        certificateId=certificate_id,
                        newStatus='INACTIVE'
                    )
                    
                    if self.debug_mode:
                        msg = self.messages.get('debug.inactivated_certificate', '')
                        if msg:
                            print(msg.format(certificate_id))
                    
                    # Step 3: Delete certificate
                    self.iot_client.delete_certificate(certificateId=certificate_id)
                    deleted_certificates.append(certificate_id)
                    
                    if self.debug_mode:
                        msg = self.messages.get('debug.deleted_certificate', '')
                        if msg:
                            print(msg.format(certificate_id))
                        
                except Exception as e:
                    if self.debug_mode:
                        cert_id = principal_arn.split('/')[-1] if '/' in principal_arn else principal_arn
                        msg = self.messages.get('debug.certificate_delete_error', '')
                        if msg:
                            print(msg.format(cert_id, str(e)))
            
            return deleted_certificates
            
        except Exception as e:
            if self.debug_mode:
                msg = self.messages.get('debug.principal_list_error', '')
                if msg:
                    print(msg.format(thing_name, str(e)))
            return deleted_certificates
    
    def delete_package_versions(self, package_name):
        """
        Delete all versions of a package.
        
        Args:
            package_name: Name of the package
            
        Returns:
            list: List of deleted version names
        """
        deleted_versions = []
        
        try:
            if self.debug_mode:
                msg = self.messages.get('debug.listing_package_versions', '')
                if msg:
                    print(msg.format(package_name))
            
            # List all versions for the package
            response = self.iot_client.list_package_versions(packageName=package_name)
            versions = response.get('packageVersionSummaries', [])
            
            if self.debug_mode and versions:
                msg = self.messages.get('debug.found_package_versions', '')
                if msg:
                    print(msg.format(len(versions), package_name))
            
            # Delete each version
            for version in versions:
                version_name = version.get('versionName')
                
                try:
                    self.iot_client.delete_package_version(
                        packageName=package_name,
                        versionName=version_name
                    )
                    deleted_versions.append(version_name)
                    
                    if self.debug_mode:
                        msg = self.messages.get('debug.deleted_package_version', '')
                        if msg:
                            print(msg.format(version_name, package_name))
                        
                except Exception as e:
                    if self.debug_mode:
                        msg = self.messages.get('debug.package_version_delete_error', '')
                        if msg:
                            print(msg.format(version_name, package_name, str(e)))
            
            return deleted_versions
            
        except Exception as e:
            if self.debug_mode:
                msg = self.messages.get('debug.package_version_list_error', '')
                if msg:
                    print(msg.format(package_name, str(e)))
            return deleted_versions
    
    def delete_s3_objects(self, bucket_name):
        """
        Delete all objects and versions from an S3 bucket.
        
        This method deletes all object versions and delete markers to prepare
        the bucket for deletion.
        
        Args:
            bucket_name: Name of the S3 bucket
            
        Returns:
            int: Count of deleted objects
        """
        deleted_count = 0
        
        try:
            if self.debug_mode:
                msg = self.messages.get('debug.listing_s3_objects', '')
                if msg:
                    print(msg.format(bucket_name))
            
            # List all object versions (including delete markers)
            paginator = self.s3_client.get_paginator('list_object_versions')
            pages = paginator.paginate(Bucket=bucket_name)
            
            for page in pages:
                # Collect objects to delete
                objects_to_delete = []
                
                # Add regular versions
                for version in page.get('Versions', []):
                    objects_to_delete.append({
                        'Key': version['Key'],
                        'VersionId': version['VersionId']
                    })
                
                # Add delete markers
                for marker in page.get('DeleteMarkers', []):
                    objects_to_delete.append({
                        'Key': marker['Key'],
                        'VersionId': marker['VersionId']
                    })
                
                # Delete objects in batches (max 1000 per request)
                if objects_to_delete:
                    if self.debug_mode:
                        msg = self.messages.get('debug.deleting_s3_batch', '')
                        if msg:
                            print(msg.format(len(objects_to_delete), bucket_name))
                    
                    response = self.s3_client.delete_objects(
                        Bucket=bucket_name,
                        Delete={'Objects': objects_to_delete}
                    )
                    
                    deleted = response.get('Deleted', [])
                    deleted_count += len(deleted)
                    
                    if self.debug_mode:
                        msg = self.messages.get('debug.deleted_s3_batch', '')
                        if msg:
                            print(msg.format(len(deleted), bucket_name))
                    
                    # Check for errors
                    errors = response.get('Errors', [])
                    if errors and self.debug_mode:
                        for error in errors:
                            msg = self.messages.get('debug.s3_delete_error', '')
                            if msg:
                                print(msg.format(error.get('Key'), error.get('Message')))
            
            if self.debug_mode:
                msg = self.messages.get('debug.s3_objects_deleted', '')
                if msg:
                    print(msg.format(deleted_count, bucket_name))
            
            return deleted_count
            
        except Exception as e:
            if self.debug_mode:
                msg = self.messages.get('debug.s3_object_list_error', '')
                if msg:
                    print(msg.format(bucket_name, str(e)))
            return deleted_count
    
    def delete_iam_policies(self, role_name):
        """
        Delete all inline policies attached to an IAM role.
        
        Args:
            role_name: Name of the IAM role
            
        Returns:
            list: List of deleted policy names
        """
        deleted_policies = []
        
        try:
            if self.debug_mode:
                msg = self.messages.get('debug.listing_iam_policies', '')
                if msg:
                    print(msg.format(role_name))
            
            # List all inline policies for the role
            response = self.iam_client.list_role_policies(RoleName=role_name)
            policy_names = response.get('PolicyNames', [])
            
            if self.debug_mode and policy_names:
                msg = self.messages.get('debug.found_iam_policies', '')
                if msg:
                    print(msg.format(len(policy_names), role_name))
            
            # Delete each inline policy
            for policy_name in policy_names:
                try:
                    self.iam_client.delete_role_policy(
                        RoleName=role_name,
                        PolicyName=policy_name
                    )
                    deleted_policies.append(policy_name)
                    
                    if self.debug_mode:
                        msg = self.messages.get('debug.deleted_iam_policy', '')
                        if msg:
                            print(msg.format(policy_name, role_name))
                        
                except Exception as e:
                    if self.debug_mode:
                        msg = self.messages.get('debug.iam_policy_delete_error', '')
                        if msg:
                            print(msg.format(policy_name, role_name, str(e)))
            
            return deleted_policies
            
        except Exception as e:
            if self.debug_mode:
                msg = self.messages.get('debug.iam_policy_list_error', '')
                if msg:
                    print(msg.format(role_name, str(e)))
            return deleted_policies
    
    def cancel_job(self, job_id):
        """
        Cancel a job if it is in progress.
        
        Args:
            job_id: ID of the job to cancel
            
        Returns:
            bool: True if job was cancelled or already completed, False otherwise
        """
        try:
            if self.debug_mode:
                msg = self.messages.get('debug.checking_job_status', '')
                if msg:
                    print(msg.format(job_id))
            
            # Get job status
            response = self.iot_client.describe_job(jobId=job_id)
            job_status = response.get('job', {}).get('status')
            
            if self.debug_mode:
                msg = self.messages.get('debug.job_status', '')
                if msg:
                    print(msg.format(job_id, job_status))
            
            # If job is in progress, cancel it
            if job_status == 'IN_PROGRESS':
                if self.debug_mode:
                    msg = self.messages.get('debug.cancelling_job', '')
                    if msg:
                        print(msg.format(job_id))
                
                self.iot_client.cancel_job(jobId=job_id)
                
                # Wait for cancellation to complete (with timeout)
                max_wait_time = 30  # seconds
                wait_interval = 2   # seconds
                elapsed_time = 0
                
                while elapsed_time < max_wait_time:
                    time.sleep(wait_interval)
                    elapsed_time += wait_interval
                    
                    response = self.iot_client.describe_job(jobId=job_id)
                    current_status = response.get('job', {}).get('status')
                    
                    if current_status == 'CANCELED':
                        if self.debug_mode:
                            msg = self.messages.get('debug.job_cancelled', '')
                            if msg:
                                print(msg.format(job_id))
                        return True
                    
                    if self.debug_mode:
                        msg = self.messages.get('debug.waiting_for_cancellation', '')
                        if msg:
                            print(msg.format(job_id, current_status))
                
                # Timeout reached
                if self.debug_mode:
                    msg = self.messages.get('debug.job_cancel_timeout', '')
                    if msg:
                        print(msg.format(job_id))
                return False
                
            else:
                # Job is not in progress, no need to cancel
                if self.debug_mode:
                    msg = self.messages.get('debug.job_not_in_progress', '')
                    if msg:
                        print(msg.format(job_id, job_status))
                return True
            
        except Exception as e:
            if self.debug_mode:
                msg = self.messages.get('debug.job_cancel_error', '')
                if msg:
                    print(msg.format(job_id, str(e)))
            return False
    
    def is_dynamic_thing_group(self, group_name):
        """
        Check if a thing group is dynamic (has a query string).
        
        Dynamic thing groups manage their membership automatically based on a query,
        so we cannot manually remove things from them.
        
        Args:
            group_name: Name of the thing group
            
        Returns:
            bool: True if the group is dynamic, False if static
        """
        try:
            response = self.iot_client.describe_thing_group(thingGroupName=group_name)
            # Dynamic groups have a queryString attribute
            query_string = response.get('queryString')
            is_dynamic = query_string is not None and query_string != ''
            
            if self.debug_mode:
                group_type = "dynamic" if is_dynamic else "static"
                msg = self.messages.get('debug.thing_group_type', '')
                if msg:
                    print(msg.format(group_name, group_type))
                if is_dynamic:
                    msg = self.messages.get('debug.query_string', '')
                    if msg:
                        print(msg.format(query_string))
            
            return is_dynamic
            
        except Exception as e:
            if self.debug_mode:
                msg = self.messages.get('debug.error_checking_dynamic', '')
                if msg:
                    print(msg.format(str(e)))
            # If we can't determine, assume static to be safe
            return False
    
    def remove_things_from_group(self, group_name):
        """
        Remove all things from a thing group before deletion.
        
        Note: This only works for static thing groups. Dynamic thing groups
        manage their membership automatically and cannot have things manually removed.
        
        Args:
            group_name: Name of the thing group
            
        Returns:
            list: List of thing names removed from the group
        """
        removed_things = []
        
        try:
            # Check if this is a dynamic group
            if self.is_dynamic_thing_group(group_name):
                if self.debug_mode:
                    msg = self.messages.get('debug.skipping_dynamic_group', '')
                    if msg:
                        print(msg.format(group_name))
                return removed_things
            
            if self.debug_mode:
                msg = self.messages.get('debug.listing_things_in_group', '')
                if msg:
                    print(msg.format(group_name))
            
            # List all things in the group
            paginator = self.iot_client.get_paginator('list_things_in_thing_group')
            for page in paginator.paginate(thingGroupName=group_name):
                things = page.get('things', [])
                
                if self.debug_mode and things:
                    msg = self.messages.get('debug.found_things_in_group', '')
                    if msg:
                        print(msg.format(len(things), group_name))
                
                # Remove each thing from the group
                for thing_name in things:
                    try:
                        self.iot_client.remove_thing_from_thing_group(
                            thingGroupName=group_name,
                            thingName=thing_name
                        )
                        removed_things.append(thing_name)
                        
                        if self.debug_mode:
                            msg = self.messages.get('debug.removed_thing_from_group', '')
                            if msg:
                                print(msg.format(thing_name, group_name))
                            
                    except Exception as e:
                        if self.debug_mode:
                            msg = self.messages.get('debug.error_removing_thing', '')
                            if msg:
                                print(msg.format(thing_name, group_name, str(e)))
            
            return removed_things
            
        except Exception as e:
            if self.debug_mode:
                msg = self.messages.get('debug.error_listing_things', '')
                if msg:
                    print(msg.format(group_name, str(e)))
            return removed_things
    
    def delete_with_dependencies(self, resource, resource_type, dry_run=False):
        """
        Delete a resource and its dependencies in the correct order.
        
        This method handles dependency deletion for various resource types:
        - Things: Delete shadows and certificates first
        - Packages: Delete versions first
        - S3 Buckets: Delete objects first
        - IAM Roles: Delete policies first
        - Jobs: Cancel if in progress first
        - Thing Groups: Remove things from group first
        - Commands: Direct deletion
        - Thing Types: Direct deletion (should already be deprecated)
        
        Args:
            resource: Resource metadata dictionary
            resource_type: Type of resource (thing, package, s3-bucket, iam-role, job, thing-group, command, thing-type)
            dry_run: If True, only simulate deletion without actually deleting
            
        Returns:
            tuple: (success, list of deleted resource names)
        """
        deleted_resources = []
        success = True
        
        try:
            # Extract resource identifier based on type
            # Note: Use the exact field names returned by AWS APIs
            resource_name = resource.get('thingName') or resource.get('packageName') or \
                           resource.get('Name') or resource.get('RoleName') or \
                           resource.get('commandId') or resource.get('groupName') or \
                           resource.get('jobId') or 'unknown'
            
            if dry_run:
                if self.debug_mode:
                    msg = self.messages.get('debug.dry_run_delete', '')
                    if msg:
                        print(msg.format(resource_name, resource_type))
                return (True, [f"{resource_name} (dry-run)"])
            
            if self.debug_mode:
                msg = self.messages.get('debug.deleting_with_dependencies', '')
                if msg:
                    print(msg.format(resource_name, resource_type))
            
            # Handle dependencies based on resource type
            if resource_type == 'thing':
                thing_name = resource.get('thingName')
                
                # Delete shadows first
                shadows = self.delete_thing_shadows(thing_name)
                if shadows:
                    deleted_resources.extend([f"shadow:{s}" for s in shadows])
                
                # Detach and delete certificates
                certificates = self.detach_and_delete_certificates(thing_name)
                if certificates:
                    deleted_resources.extend([f"cert:{c}" for c in certificates])
                
                # Delete the thing itself
                self.iot_client.delete_thing(thingName=thing_name)
                deleted_resources.append(f"thing:{thing_name}")
                
                if self.debug_mode:
                    msg = self.messages.get('debug.deleted_thing', '')
                    if msg:
                        print(msg.format(thing_name))
                
            elif resource_type == 'package':
                package_name = resource.get('packageName')
                
                # Delete all versions first
                versions = self.delete_package_versions(package_name)
                if versions:
                    deleted_resources.extend([f"version:{v}" for v in versions])
                
                # Delete the package itself
                self.iot_client.delete_package(packageName=package_name)
                deleted_resources.append(f"package:{package_name}")
                
                if self.debug_mode:
                    msg = self.messages.get('debug.deleted_package', '')
                    if msg:
                        print(msg.format(package_name))
                
            elif resource_type == 's3-bucket':
                # S3 API returns 'Name' field, not 'bucketName'
                bucket_name = resource.get('Name')
                
                # Delete all objects first
                object_count = self.delete_s3_objects(bucket_name)
                if object_count > 0:
                    deleted_resources.append(f"s3-objects:{object_count}")
                
                # Delete the bucket itself
                self.s3_client.delete_bucket(Bucket=bucket_name)
                deleted_resources.append(f"bucket:{bucket_name}")
                
                if self.debug_mode:
                    msg = self.messages.get('debug.deleted_bucket', '')
                    if msg:
                        print(msg.format(bucket_name))
                
            elif resource_type == 'iam-role':
                # IAM API returns 'RoleName' field (capital R)
                role_name = resource.get('RoleName')
                
                # Delete all inline policies first
                policies = self.delete_iam_policies(role_name)
                if policies:
                    deleted_resources.extend([f"policy:{p}" for p in policies])
                
                # Delete the role itself
                self.iam_client.delete_role(RoleName=role_name)
                deleted_resources.append(f"role:{role_name}")
                
                if self.debug_mode:
                    msg = self.messages.get('debug.deleted_role', '')
                    if msg:
                        print(msg.format(role_name))
                
            elif resource_type == 'job':
                job_id = resource.get('jobId')
                
                # Cancel job if in progress
                cancelled = self.cancel_job(job_id)
                if cancelled:
                    deleted_resources.append(f"job-cancelled:{job_id}")
                
                # Delete the job itself
                self.iot_client.delete_job(jobId=job_id)
                deleted_resources.append(f"job:{job_id}")
                
                if self.debug_mode:
                    msg = self.messages.get('debug.deleted_job', '')
                    if msg:
                        print(msg.format(job_id))
            
            elif resource_type in ['thing-group', 'thing_group']:
                group_name = resource.get('groupName')
                
                # Check if this is a dynamic or static thing group
                is_dynamic = self.is_dynamic_thing_group(group_name)
                
                if is_dynamic:
                    # Dynamic groups: use delete_dynamic_thing_group API
                    # No need to remove things - membership is managed automatically
                    if self.debug_mode:
                        msg = self.messages.get('debug.deleting_dynamic_group', '')
                        if msg:
                            print(msg.format(group_name))
                    
                    self.iot_client.delete_dynamic_thing_group(thingGroupName=group_name)
                    deleted_resources.append(f"dynamic-thing-group:{group_name}")
                    
                    if self.debug_mode:
                        msg = self.messages.get('debug.deleted_thing_group', '')
                        if msg:
                            print(msg.format(group_name))
                else:
                    # Static groups: remove things first, then use delete_thing_group API
                    if self.debug_mode:
                        msg = self.messages.get('debug.deleting_static_group', '')
                        if msg:
                            print(msg.format(group_name))
                    
                    removed_things = self.remove_things_from_group(group_name)
                    if removed_things:
                        deleted_resources.append(f"removed-things:{len(removed_things)}")
                    
                    self.iot_client.delete_thing_group(thingGroupName=group_name)
                    deleted_resources.append(f"thing-group:{group_name}")
                    
                    if self.debug_mode:
                        msg = self.messages.get('debug.deleted_thing_group', '')
                        if msg:
                            print(msg.format(group_name))
            
            elif resource_type == 'command':
                # AWS API uses commandId in list response but commandName for deletion
                command_id = resource.get('commandId') or resource.get('commandName')
                
                if self.debug_mode:
                    msg = self.messages.get('debug.deleting_command', '')
                    if msg:
                        print(msg.format(command_id))
                
                # Delete the command itself
                self.iot_client.delete_command(commandId=command_id)
                deleted_resources.append(f"command:{command_id}")
                
                if self.debug_mode:
                    msg = self.messages.get('debug.deleted_command', '')
                    if msg:
                        print(msg.format(command_id))
            
            elif resource_type in ['thing-type', 'thing_type']:
                type_name = resource.get('thingTypeName')
                
                # Delete the thing type itself (should already be deprecated)
                self.iot_client.delete_thing_type(thingTypeName=type_name)
                deleted_resources.append(f"thing-type:{type_name}")
                
                if self.debug_mode:
                    msg = self.messages.get('debug.deleted_thing_type', '')
                    if msg:
                        print(msg.format(type_name))
            
            else:
                # For other resource types without special dependencies, just note them
                # This should rarely be reached now
                if self.debug_mode:
                    msg = self.messages.get('debug.unhandled_resource_type', '')
                    if msg:
                        print(msg.format(resource_type))
                deleted_resources.append(f"{resource_type}:{resource_name}")
            
            return (success, deleted_resources)
            
        except Exception as e:
            if self.debug_mode:
                msg = self.messages.get('debug.exception_in_delete', '')
                if msg:
                    print(msg.format(str(e)))
                import traceback
                traceback.print_exc()
                msg = self.messages.get('debug.delete_with_dependencies_error', '')
                if msg:
                    print(msg.format(resource_name, resource_type, str(e)))
            return (False, deleted_resources)
