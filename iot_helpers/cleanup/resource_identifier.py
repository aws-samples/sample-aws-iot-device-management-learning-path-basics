"""
Resource Identifier Module

This module provides functionality to identify workshop resources using multiple
identification methods: tags, naming patterns, and resource associations.

The ResourceIdentifier class implements a priority-based identification strategy:
1. Tag-based identification (highest priority)
2. Naming pattern identification
3. Association-based identification (for non-taggable resources)
"""

import sys
import os

# Add repository root to path for i18n imports
# Navigate 3 levels up from iot_helpers/cleanup/resource_identifier.py to repository root
repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from i18n.loader import load_messages
from iot_helpers.utils.naming_conventions import matches_workshop_pattern


class ResourceIdentifier:
    """
    Identifies workshop resources using tags, naming patterns, and associations.
    
    This class implements a multi-layered identification strategy to determine
    if a resource belongs to the workshop. It checks in priority order:
    1. Workshop tags (highest priority)
    2. Naming patterns
    3. Resource associations
    """
    
    def __init__(self, iot_client, s3_client, iam_client, language='en', debug_mode=False):
        """
        Initialize the ResourceIdentifier.
        
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
        self.messages = load_messages('resource_identifier', language)

    
    def check_tags(self, resource_arn, resource_type):
        """
        Check if a resource has workshop tags.
        
        Args:
            resource_arn: ARN of the resource to check
            resource_type: Type of resource (thing-type, thing-group, package, job, etc.)
            
        Returns:
            bool: True if resource has workshop tag, False otherwise
        """
        try:
            # Workshop tag to look for
            workshop_tag_key = "workshop"
            workshop_tag_value = "learning-aws-iot-dm-basics"
            
            if self.debug_mode:
                msg = self.messages.get('debug.checking_tags_for_resource', '')
                if msg:
                    print(msg.format(resource_type, resource_arn))
                msg = self.messages.get('debug.looking_for_tag', '')
                if msg:
                    print(msg.format(workshop_tag_key, workshop_tag_value))
            
            # Check tags based on resource type
            if resource_type in ['thing-type', 'thing-group', 'package', 'job', 'command']:
                # IoT resources use list_tags_for_resource
                response = self.iot_client.list_tags_for_resource(resourceArn=resource_arn)
                tags = response.get('tags', [])
                
                if self.debug_mode:
                    msg = self.messages.get('debug.found_tags_on_resource', '')
                    if msg:
                        print(msg.format(len(tags)))
                    for tag in tags:
                        msg = self.messages.get('debug.tag_detail', '')
                        if msg:
                            print(msg.format(tag.get('Key'), tag.get('Value')))
                
                # Check if workshop tag exists with correct value
                for tag in tags:
                    if tag.get('Key') == workshop_tag_key and tag.get('Value') == workshop_tag_value:
                        if self.debug_mode:
                            msg = self.messages.get('debug.workshop_tag_match_found', '')
                            if msg:
                                print(msg)
                        return True
                        
            elif resource_type == 's3-bucket':
                # S3 buckets use get_bucket_tagging
                # Extract bucket name from ARN (arn:aws:s3:::bucket-name)
                bucket_name = resource_arn.split(':')[-1]
                
                try:
                    response = self.s3_client.get_bucket_tagging(Bucket=bucket_name)
                    tag_set = response.get('TagSet', [])
                    
                    if self.debug_mode:
                        msg = self.messages.get('debug.found_tags_on_resource', '')
                        if msg:
                            print(msg.format(len(tag_set)))
                        for tag in tag_set:
                            msg = self.messages.get('debug.tag_detail', '')
                            if msg:
                                print(msg.format(tag.get('Key'), tag.get('Value')))
                    
                    # Check if workshop tag exists with correct value
                    for tag in tag_set:
                        if tag.get('Key') == workshop_tag_key and tag.get('Value') == workshop_tag_value:
                            if self.debug_mode:
                                msg = self.messages.get('debug.workshop_tag_match_found', '')
                                if msg:
                                    print(msg)
                            return True
                except self.s3_client.exceptions.NoSuchTagSet:
                    # Bucket has no tags
                    if self.debug_mode:
                        msg = self.messages.get('debug.s3_bucket_no_tags', '')
                        if msg:
                            print(msg)
                    return False
                    
            elif resource_type == 'iam-role':
                # IAM roles use list_role_tags
                # Extract role name from ARN
                role_name = resource_arn.split('/')[-1]
                
                response = self.iam_client.list_role_tags(RoleName=role_name)
                tags = response.get('Tags', [])
                
                if self.debug_mode:
                    msg = self.messages.get('debug.found_tags_on_resource', '')
                    if msg:
                        print(msg.format(len(tags)))
                    for tag in tags:
                        msg = self.messages.get('debug.tag_detail', '')
                        if msg:
                            print(msg.format(tag.get('Key'), tag.get('Value')))
                
                # Check if workshop tag exists with correct value
                for tag in tags:
                    if tag.get('Key') == workshop_tag_key and tag.get('Value') == workshop_tag_value:
                        if self.debug_mode:
                            msg = self.messages.get('debug.workshop_tag_match_found', '')
                            if msg:
                                print(msg)
                        return True
            
            # No matching tag found
            if self.debug_mode:
                msg = self.messages.get('debug.no_workshop_tag_found', '')
                if msg:
                    print(msg)
            return False
            
        except self.iot_client.exceptions.ResourceNotFoundException:
            # Resource doesn't exist or was already deleted
            if self.debug_mode:
                print(self.messages.get('debug.resource_not_found', resource_arn))
            return False
            
        except Exception as e:
            # Log error but don't fail - fall back to other identification methods
            if self.debug_mode:
                print(self.messages.get('debug.tag_check_error', resource_arn, str(e)))
            return False

    
    def check_naming(self, resource_name, resource_type, prefix=None):
        """
        Check if a resource name matches workshop naming patterns.
        
        Args:
            resource_name: Name of the resource
            resource_type: Type of resource (thing, thing-group, package, etc.)
            prefix: Optional custom prefix for things
            
        Returns:
            bool: True if name matches workshop pattern, False otherwise
        """
        if self.debug_mode:
            msg = self.messages.get('debug.checking_naming_pattern', '')
            if msg:
                print(msg.format(resource_type, resource_name))
            if prefix:
                msg = self.messages.get('debug.using_custom_prefix', '')
                if msg:
                    print(msg.format(prefix))
        
        # Use the naming_conventions module to check pattern match
        matches = matches_workshop_pattern(resource_name, resource_type, prefix)
        
        if self.debug_mode:
            if matches:
                msg = self.messages.get('debug.naming_pattern_matches', '')
                if msg:
                    print(msg)
            else:
                msg = self.messages.get('debug.naming_pattern_no_match', '')
                if msg:
                    print(msg)
        
        return matches

    
    def check_association(self, resource, resource_type):
        """
        Check if a resource is associated with workshop resources.
        
        This method is used for non-taggable resources like certificates and shadows
        that can be identified by their association with workshop things.
        
        Args:
            resource: Resource metadata dictionary
            resource_type: Type of resource (certificate, shadow)
            
        Returns:
            bool: True if resource is associated with workshop resource, False otherwise
        """
        try:
            if self.debug_mode:
                resource_id = resource.get('certificateId') or resource.get('shadowName') or 'unknown'
                print(self.messages.get('debug.checking_association', resource_id, resource_type))
            
            if resource_type == 'certificate':
                # Check if certificate is attached to a workshop thing
                certificate_arn = resource.get('certificateArn')
                if not certificate_arn:
                    return False
                
                # List things this certificate is attached to
                response = self.iot_client.list_principal_things(principal=certificate_arn)
                things = response.get('things', [])
                
                # Check if any of the attached things are workshop things
                for thing_name in things:
                    # Check if thing name matches workshop patterns
                    if self.check_naming(thing_name, 'thing'):
                        if self.debug_mode:
                            print(self.messages.get('debug.association_match_found', 
                                                   resource.get('certificateId'), thing_name))
                        return True
                        
            elif resource_type == 'shadow':
                # Check if shadow belongs to a workshop thing
                thing_name = resource.get('thingName')
                if not thing_name:
                    return False
                
                # Check if the thing name matches workshop patterns
                if self.check_naming(thing_name, 'thing'):
                    if self.debug_mode:
                        shadow_name = resource.get('shadowName', 'classic')
                        print(self.messages.get('debug.association_match_found', 
                                               shadow_name, thing_name))
                    return True
            
            # No association found
            if self.debug_mode:
                resource_id = resource.get('certificateId') or resource.get('shadowName') or 'unknown'
                print(self.messages.get('debug.no_association', resource_id))
            return False
            
        except Exception as e:
            # Log error but don't fail
            if self.debug_mode:
                resource_id = resource.get('certificateId') or resource.get('shadowName') or 'unknown'
                print(self.messages.get('debug.association_check_error', resource_id, str(e)))
            return False

    
    def identify_resource(self, resource, resource_type, custom_prefix=None):
        """
        Identify if a resource belongs to the workshop using multiple methods.
        
        This method implements a priority-based identification strategy:
        1. Check tags (highest priority) - for taggable resources
        2. Check naming patterns - for all resources
        3. Check associations - for non-taggable resources (certificates, shadows)
        
        Args:
            resource: Resource metadata dictionary
            resource_type: Type of resource
            custom_prefix: Optional custom thing prefix for identification
            
        Returns:
            tuple: (is_workshop_resource, identification_method)
                   identification_method: "tag", "naming", "association", or "none"
        """
        resource_name = resource.get('thingName') or resource.get('groupName') or \
                       resource.get('packageName') or resource.get('jobId') or \
                       resource.get('commandId') or resource.get('commandName') or \
                       resource.get('thingTypeName') or \
                       resource.get('Name') or resource.get('RoleName') or \
                       resource.get('certificateId') or resource.get('shadowName') or 'unknown'
        
        if self.debug_mode:
            msg = self.messages.get('debug.identifying_resource_header', '')
            if msg:
                print(f"\n{msg}")
            msg = self.messages.get('debug.resource_name_debug', '')
            if msg:
                print(msg.format(resource_name))
            msg = self.messages.get('debug.resource_type_debug', '')
            if msg:
                print(msg.format(resource_type))
        
        # Priority 1: Check tags (for taggable resources)
        if resource_type in ['thing-type', 'thing-group', 'package', 'job', 'command', 's3-bucket', 'iam-role']:
            # Extract ARN based on resource type
            resource_arn = None
            if resource_type == 'thing-type':
                resource_arn = resource.get('thingTypeArn')
            elif resource_type == 'thing-group':
                resource_arn = resource.get('groupArn')
            elif resource_type == 'package':
                # Package ARN might not be in list response, try to get it or construct it
                resource_arn = resource.get('packageArn')
                if not resource_arn and resource_name != 'unknown':
                    # Try to get full package details to get the ARN
                    try:
                        if self.debug_mode:
                            msg = self.messages.get('debug.package_arn_not_in_list', '')
                            if msg:
                                print(msg.format(resource_name))
                        package_response = self.iot_client.get_package(packageName=resource_name)
                        resource_arn = package_response.get('packageArn')
                        if self.debug_mode:
                            msg = self.messages.get('debug.retrieved_package_arn', '')
                            if msg:
                                print(msg.format(resource_arn))
                    except Exception as e:
                        if self.debug_mode:
                            msg = self.messages.get('debug.could_not_get_package_arn', '')
                            if msg:
                                print(msg.format(resource_name, str(e)))
                            msg = self.messages.get('debug.skip_tag_check_proceed_naming', '')
                            if msg:
                                print(msg)
            elif resource_type == 'job':
                resource_arn = resource.get('jobArn')
            elif resource_type == 'command':
                resource_arn = resource.get('commandArn')
            elif resource_type == 's3-bucket':
                # S3 bucket ARN format: arn:aws:s3:::bucket-name
                resource_arn = f"arn:aws:s3:::{resource_name}"
            elif resource_type == 'iam-role':
                resource_arn = resource.get('Arn')
                if not resource_arn and resource_name != 'unknown':
                    # Try to get role details to get the ARN
                    try:
                        if self.debug_mode:
                            msg = self.messages.get('debug.role_arn_not_in_resource', '')
                            if msg:
                                print(msg.format(resource_name))
                        role_response = self.iam_client.get_role(RoleName=resource_name)
                        resource_arn = role_response.get('Role', {}).get('Arn')
                        if self.debug_mode:
                            msg = self.messages.get('debug.retrieved_role_arn', '')
                            if msg:
                                print(msg.format(resource_arn))
                    except Exception as e:
                        if self.debug_mode:
                            msg = self.messages.get('debug.could_not_get_role_arn', '')
                            if msg:
                                print(msg.format(resource_name, str(e)))
                            msg = self.messages.get('debug.skip_tag_check_proceed_naming', '')
                            if msg:
                                print(msg)
            
            if self.debug_mode:
                msg = self.messages.get('debug.resource_arn_debug', '')
                if msg:
                    print(msg.format(resource_arn))
            
            if resource_arn and self.check_tags(resource_arn, resource_type):
                if self.debug_mode:
                    msg = self.messages.get('debug.identified_by_tag_debug', '')
                    if msg:
                        print(msg)
                return (True, "tag")
        
        # Priority 2: Check naming patterns (for all resources)
        if self.debug_mode:
            msg = self.messages.get('debug.checking_naming_pattern_debug', '')
            if msg:
                print(msg)
        if self.check_naming(resource_name, resource_type, custom_prefix):
            if self.debug_mode:
                msg = self.messages.get('debug.identified_by_naming_debug', '')
                if msg:
                    print(msg)
            return (True, "naming")
        
        # Priority 3: Check associations (for non-taggable resources)
        if resource_type in ['certificate', 'shadow']:
            if self.debug_mode:
                msg = self.messages.get('debug.checking_associations_debug', '')
                if msg:
                    print(msg)
            if self.check_association(resource, resource_type):
                if self.debug_mode:
                    msg = self.messages.get('debug.identified_by_association_debug', '')
                    if msg:
                        print(msg)
                return (True, "association")
        
        # No identification method matched
        if self.debug_mode:
            msg = self.messages.get('debug.not_identified_debug', '')
            if msg:
                print(msg)
        return (False, "none")
