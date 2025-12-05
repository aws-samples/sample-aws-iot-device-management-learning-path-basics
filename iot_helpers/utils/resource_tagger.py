#!/usr/bin/env python3
"""
Resource Tagging Module for AWS IoT Workshop

This module provides functionality to apply workshop identification tags to AWS resources.
It supports tagging of IoT resources, S3 buckets, and IAM roles with consistent workshop
metadata for safe cleanup operations.
"""

import sys
import os
from datetime import datetime
from typing import Dict, Optional

# Add i18n to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "i18n"))

import boto3
from botocore.exceptions import ClientError

# Workshop tag constants
WORKSHOP_TAGS = {
    "workshop": "learning-aws-iot-dm-basics",
    "created-by": "provision-script",
    "creation-date": ""  # Will be set dynamically
}


def validate_tag_schema(tags: Dict[str, str]) -> bool:
    """
    Validate that tags conform to AWS tagging requirements.
    
    Args:
        tags: Dictionary of tag key-value pairs
        
    Returns:
        True if tags are valid, False otherwise
    """
    if not tags:
        return False
    
    for key, value in tags.items():
        # AWS tag key requirements: 1-128 characters
        if not key or len(key) > 128:
            return False
        # AWS tag value requirements: 0-256 characters
        if value is not None and len(value) > 256:
            return False
    
    return True


def apply_workshop_tags(
    client: boto3.client,
    resource_arn: str,
    resource_type: str,
    additional_tags: Optional[Dict[str, str]] = None,
    script_name: str = "provision-script"
) -> bool:
    """
    Apply workshop tags to a resource.
    
    This function applies standard workshop identification tags to AWS resources
    for safe cleanup operations. It handles service-specific tagging APIs and
    gracefully handles errors to prevent resource creation failures.
    
    Args:
        client: Boto3 client for the service (iot, s3, or iam)
        resource_arn: ARN of the resource to tag
        resource_type: Type of resource (thing-type, thing-group, package, 
                      package-version, job, command, s3-bucket, iam-role)
        additional_tags: Optional additional tags to apply
        script_name: Name of the script creating the resource (default: provision-script)
        
    Returns:
        True if tagging succeeded, False otherwise
        
    Supported Resource Types:
        - thing-type: IoT Thing Types
        - thing-group: IoT Thing Groups (static and dynamic)
        - package: IoT Software Packages
        - package-version: IoT Software Package Versions
        - job: IoT Jobs
        - command: IoT Commands
        - s3-bucket: S3 Buckets
        - iam-role: IAM Roles
    """
    try:
        # Create base tags with timestamp
        tags = WORKSHOP_TAGS.copy()
        tags["creation-date"] = datetime.utcnow().isoformat() + "Z"
        tags["created-by"] = script_name
        
        # Merge additional tags if provided
        if additional_tags:
            tags.update(additional_tags)
        
        # Validate tag schema
        if not validate_tag_schema(tags):
            return False
        
        # Apply tags based on resource type
        if resource_type in ["thing-type", "thing-group", "package", "package-version", "job", "command"]:
            # IoT resources use tag_resource API
            tag_list = [{"Key": k, "Value": v} for k, v in tags.items()]
            client.tag_resource(
                resourceArn=resource_arn,
                tags=tag_list
            )
            return True
            
        elif resource_type == "s3-bucket":
            # S3 buckets use put_bucket_tagging API
            # Extract bucket name from ARN (arn:aws:s3:::bucket-name)
            bucket_name = resource_arn.split(":")[-1]
            tag_set = [{"Key": k, "Value": v} for k, v in tags.items()]
            client.put_bucket_tagging(
                Bucket=bucket_name,
                Tagging={"TagSet": tag_set}
            )
            return True
            
        elif resource_type == "iam-role":
            # IAM roles use tag_role API
            # Extract role name from ARN
            role_name = resource_arn.split("/")[-1]
            tag_list = [{"Key": k, "Value": v} for k, v in tags.items()]
            client.tag_role(
                RoleName=role_name,
                Tags=tag_list
            )
            return True
            
        else:
            # Unknown resource type
            return False
            
    except ClientError as e:
        # Handle AWS API errors gracefully
        error_code = e.response.get("Error", {}).get("Code", "Unknown")
        
        # Common errors that should not prevent resource creation
        if error_code in ["ResourceNotFoundException", "InvalidParameterException", "AccessDeniedException"]:
            return False
        
        # Re-raise unexpected errors
        raise
        
    except Exception:
        # Catch all other exceptions to prevent resource creation failure
        return False


if __name__ == "__main__":
    # Module can be imported but not run directly
    print("This module provides resource tagging functionality.")
    print("Import it in your scripts to use apply_workshop_tags().")
