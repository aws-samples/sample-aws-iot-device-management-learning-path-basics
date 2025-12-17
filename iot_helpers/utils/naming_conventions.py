"""
Naming Convention Module for AWS IoT Workshop Resources

This module provides utilities for generating and validating resource names
according to workshop naming conventions. It supports:
- Thing name generation with configurable prefixes
- Prefix validation against AWS IoT requirements
- Pattern matching for workshop resource identification

The naming conventions ensure consistent resource naming across workshop scripts
and enable reliable identification during cleanup operations.
"""

import re
from typing import Optional, List


# Naming patterns for each resource type
# These patterns are used to identify workshop resources during cleanup
NAMING_PATTERNS = {
    "thing": [
        r"^Vehicle-VIN-\d{3}$",  # Default pattern: Vehicle-VIN-001, Vehicle-VIN-002, etc.
        r"^{custom_prefix}\d{3}$",  # Custom prefix pattern (substituted at runtime)
        r"^vehicle-[A-Z]{2}-(sedan|suv|truck)-\d+$"  # Legacy pattern for backward compatibility
    ],
    "thing_group": [
        r"^fleet-[a-zA-Z\s]+$",  # Static groups: fleet-USA, fleet-Germany, etc.
        r"^.*-workshop-.*$"  # Dynamic groups with workshop identifier
    ],
    "thing_type": [
        r"^(sedan|suv|truck)$"  # Thing type names match vehicle types
    ],
    "package": [
        r"^(sedan|suv|truck)$",  # Package names match thing types
        r"^.*-workshop-.*$"  # Packages with workshop identifier
    ],
    "job": [
        r"^.*-v\d+\.\d+\.\d+$",  # OTA jobs with version: sedan-v1.0.0, suv-v2.1.3
        r"^command-.*$"  # Command jobs: command-reboot, command-update
    ],
    "command": [
        r"^.*-command$",  # IoT Commands ending with -command
        r"^command-.*$"  # IoT Commands starting with command-
    ],
    "s3_bucket": [
        r"^iot-firmware-[a-z0-9-]+-[a-z0-9]+$"  # S3 buckets: iot-firmware-us-east-1-abc123
    ],
    "iam_role": [
        r"^IoTJobsRole(-[a-z0-9-]+-[a-z0-9]+)?$",  # IoTJobsRole or IoTJobsRole-us-east-1-123456789
        r"^IoTPackageConfigRole(-[a-z0-9-]+-[a-z0-9]+)?$"  # IoTPackageConfigRole or with region-account
    ],
    "iot_rule": [
        r"^.*Rule$",  # Rules ending with "Rule"
        r"^rule_.*$",  # Rules starting with "rule_"
        r"^.*_workshop_.*$"  # Rules containing "_workshop_"
    ]
}


def generate_thing_name(prefix: str, sequential_number: int) -> str:
    """
    Generate a thing name using the configured prefix and sequential number.
    
    This function creates standardized thing names for the workshop by combining
    a prefix with a zero-padded 3-digit sequential number. This ensures consistent
    naming across all workshop things and enables reliable identification during cleanup.
    
    Args:
        prefix: Thing name prefix (e.g., "Vehicle-VIN-")
        sequential_number: Sequential number from 1 to 999
        
    Returns:
        Formatted thing name (e.g., "Vehicle-VIN-001", "Vehicle-VIN-042")
        
    Raises:
        ValueError: If sequential_number is not in range 1-999
        
    Examples:
        >>> generate_thing_name("Vehicle-VIN-", 1)
        'Vehicle-VIN-001'
        >>> generate_thing_name("Vehicle-VIN-", 42)
        'Vehicle-VIN-042'
        >>> generate_thing_name("Custom-", 999)
        'Custom-999'
    """
    # Validate sequential number range
    if not isinstance(sequential_number, int) or sequential_number < 1 or sequential_number > 999:
        raise ValueError(
            f"sequential_number must be an integer between 1 and 999, got: {sequential_number}"
        )
    
    # Format with zero-padding to 3 digits
    padded_number = str(sequential_number).zfill(3)
    
    # Combine prefix and padded number
    return f"{prefix}{padded_number}"


def validate_thing_prefix(prefix: str) -> bool:
    """
    Validate thing name prefix against AWS IoT requirements.
    
    AWS IoT thing names must follow specific character and length requirements.
    This function validates that a prefix meets these requirements to ensure
    generated thing names will be valid.
    
    Validation Rules:
        - Must not be empty
        - Must contain only alphanumeric characters, hyphens, underscores, and colons
        - Must be 20 characters or less (to leave room for 3-digit sequential number)
        
    Args:
        prefix: Prefix to validate
        
    Returns:
        True if prefix is valid, False otherwise
        
    Examples:
        >>> validate_thing_prefix("Vehicle-VIN-")
        True
        >>> validate_thing_prefix("Custom_Prefix:")
        True
        >>> validate_thing_prefix("")
        False
        >>> validate_thing_prefix("Invalid Prefix!")
        False
        >>> validate_thing_prefix("ThisPrefixIsTooLongForValidation")
        False
    """
    # Check for empty string
    if not prefix or len(prefix) == 0:
        return False
    
    # Check length (maximum 20 characters)
    if len(prefix) > 20:
        return False
    
    # Check character set: alphanumeric, hyphens, underscores, colons only
    # AWS IoT thing names allow: a-z, A-Z, 0-9, -, _, :
    valid_pattern = r'^[a-zA-Z0-9\-_:]+$'
    if not re.match(valid_pattern, prefix):
        return False
    
    return True


def matches_workshop_pattern(
    resource_name: str,
    resource_type: str,
    prefix: Optional[str] = None
) -> bool:
    """
    Check if a resource name matches workshop naming patterns.
    
    This function determines whether a resource name follows the expected
    workshop naming conventions for its type. It supports custom prefixes
    for thing names and recognizes legacy patterns for backward compatibility.
    
    Args:
        resource_name: Name of the resource to check
        resource_type: Type of resource (thing, thing_group, package, job, etc.)
        prefix: Optional custom prefix for thing pattern matching
        
    Returns:
        True if resource name matches any workshop pattern for its type,
        False otherwise
        
    Examples:
        >>> matches_workshop_pattern("Vehicle-VIN-001", "thing")
        True
        >>> matches_workshop_pattern("fleet-USA", "thing_group")
        True
        >>> matches_workshop_pattern("sedan", "thing_type")
        True
        >>> matches_workshop_pattern("random-resource", "thing")
        False
        >>> matches_workshop_pattern("Custom-001", "thing", prefix="Custom-")
        True
    """
    # Get patterns for the resource type
    if resource_type not in NAMING_PATTERNS:
        return False
    
    patterns = NAMING_PATTERNS[resource_type]
    
    # For thing patterns, handle custom prefix substitution
    if resource_type == "thing" and prefix:
        # Create a custom pattern by substituting the prefix
        # Escape special regex characters in the prefix
        escaped_prefix = re.escape(prefix)
        custom_pattern = f"^{escaped_prefix}\\d{{3}}$"
        
        # Test against custom pattern first
        if re.match(custom_pattern, resource_name):
            return True
    
    # Test resource name against each pattern
    for pattern in patterns:
        # Skip the custom prefix placeholder pattern
        if pattern == r"^{custom_prefix}\d{3}$":
            continue
            
        if re.match(pattern, resource_name):
            return True
    
    return False
