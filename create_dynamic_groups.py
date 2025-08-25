#!/usr/bin/env python3

import subprocess
import json
import sys
import time
from colorama import Fore, Style, init

# Initialize colorama
init()

class DynamicGroupCreator:
    def __init__(self):
        self.region = None
        self.account_id = None
        self.debug_mode = False
    
    def run_aws_command_basic(self, command, capture_output=True):
        """Basic AWS CLI command execution without debug output"""
        try:
            return subprocess.run(command, shell=True, capture_output=capture_output, text=True)
        except Exception as e:
            print(f"{Fore.RED}❌ Error executing command: {e}{Style.RESET_ALL}")
            return None
    
    def run_aws_command(self, command, capture_output=True):
        """Execute AWS CLI command and return result"""
        try:
            if self.debug_mode:
                print(f"{Fore.CYAN}📥 DEBUG - Command: {command}{Style.RESET_ALL}")
            
            result = subprocess.run(command, shell=True, capture_output=capture_output, text=True)
            
            if self.debug_mode:
                print(f"{Fore.CYAN}📤 DEBUG - Return code: {result.returncode}{Style.RESET_ALL}")
                if result.stdout:
                    print(f"{Fore.CYAN}📤 DEBUG - Stdout: {result.stdout.strip()}{Style.RESET_ALL}")
                if result.stderr:
                    print(f"{Fore.CYAN}📤 DEBUG - Stderr: {result.stderr.strip()}{Style.RESET_ALL}")
            
            return result
        except Exception as e:
            print(f"{Fore.RED}❌ Error executing command: {e}{Style.RESET_ALL}")
            return None
    
    def print_header(self):
        print(f"{Fore.CYAN}🔍 AWS IoT Dynamic Group Creator{Style.RESET_ALL}")
        print(f"{Fore.CYAN}=================================={Style.RESET_ALL}\n")
        
        print(f"{Fore.YELLOW}📚 LEARNING GOAL:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}This script demonstrates how to create Dynamic Thing Groups using Fleet Indexing queries.{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Dynamic groups automatically include/exclude devices based on real-time criteria like{Style.RESET_ALL}")
        print(f"{Fore.CYAN}country, firmware version, battery level, or thing type. Unlike static groups,{Style.RESET_ALL}")
        print(f"{Fore.CYAN}dynamic groups update membership automatically as device attributes change.{Style.RESET_ALL}\n")
        
        # Get and display region and account ID
        region_result = self.run_aws_command_basic("aws configure get region")
        account_result = self.run_aws_command_basic("aws sts get-caller-identity --query Account --output text")
        
        self.region = region_result.stdout.strip() if region_result and region_result.returncode == 0 else "us-east-1"
        self.account_id = account_result.stdout.strip() if account_result and account_result.returncode == 0 else "unknown"
        
        print(f"{Fore.CYAN}📍 Region: {Fore.GREEN}{self.region}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}🆔 Account ID: {Fore.GREEN}{self.account_id}{Style.RESET_ALL}\n")
    
    def get_debug_mode(self):
        """Ask user for debug mode"""
        choice = input(f"{Fore.YELLOW}🔧 Enable debug mode (show all commands and outputs)? [y/N]: {Style.RESET_ALL}").strip().lower()
        self.debug_mode = choice in ['y', 'yes']
        
        if self.debug_mode:
            print(f"{Fore.GREEN}✅ Debug mode enabled{Style.RESET_ALL}\n")
    
    def get_user_inputs(self):
        """Get dynamic group criteria from user"""
        print(f"{Fore.BLUE}📝 Define Dynamic Group Criteria (all fields optional):{Style.RESET_ALL}\n")
        
        # Countries
        print(f"{Fore.YELLOW}🌍 Countries (comma-separated, e.g., US,CA,MX or leave empty):{Style.RESET_ALL}")
        countries_input = input().strip()
        countries = [c.strip().upper() for c in countries_input.split(',') if c.strip()] if countries_input else []
        
        # Thing type
        print(f"{Fore.YELLOW}📱 Thing type (e.g., motionSensor or leave empty):{Style.RESET_ALL}")
        thing_type = input().strip() or None
        
        # Versions
        print(f"{Fore.YELLOW}📦 Package versions (comma-separated, e.g., 1.0.0,1.1.0 or leave empty):{Style.RESET_ALL}")
        versions_input = input().strip()
        versions = [v.strip() for v in versions_input.split(',') if v.strip()] if versions_input else []
        
        # Battery level
        print(f"{Fore.YELLOW}🔋 Battery level (e.g., >50, <30, =75 or leave empty):{Style.RESET_ALL}")
        battery_level = input().strip() or None
        
        return countries, thing_type, versions, battery_level
    
    def generate_group_name(self, countries, thing_type, versions, battery_level):
        """Generate group name based on criteria"""
        name_parts = []
        
        # Add country (if single)
        if len(countries) == 1:
            name_parts.append(countries[0])
        
        # Add thing type
        if thing_type:
            name_parts.append(thing_type)
        
        # Add version (if single)
        if len(versions) == 1:
            version_clean = versions[0].replace('.', '_')
            name_parts.append(version_clean)
        
        # Add battery level
        if battery_level:
            battery_clean = battery_level.replace('>', 'gt').replace('<', 'lt').replace('=', 'eq')
            name_parts.append(f"battery{battery_clean}")
        
        # Add suffix
        name_parts.append("Devices")
        
        return "_".join(name_parts)
    
    def get_group_name(self, countries, thing_type, versions, battery_level):
        """Get group name from user or generate automatically"""
        # Check if multiple countries or versions (requires custom name)
        needs_custom_name = len(countries) > 1 or len(versions) > 1
        
        if needs_custom_name:
            print(f"\n{Fore.YELLOW}📝 Multiple countries or versions selected. Please provide a custom group name:{Style.RESET_ALL}")
            custom_name = input().strip()
            if not custom_name:
                print(f"{Fore.RED}❌ Group name is required when multiple countries or versions are selected{Style.RESET_ALL}")
                return None
            return custom_name
        else:
            # Generate automatic name
            auto_name = self.generate_group_name(countries, thing_type, versions, battery_level)
            print(f"\n{Fore.CYAN}🏷️  Generated group name: {Fore.YELLOW}{auto_name}{Style.RESET_ALL}")
            
            confirm = input(f"{Fore.YELLOW}Use this name? [Y/n]: {Style.RESET_ALL}").strip().lower()
            if confirm in ['n', 'no']:
                custom_name = input(f"{Fore.YELLOW}Enter custom name: {Style.RESET_ALL}").strip()
                return custom_name if custom_name else auto_name
            
            return auto_name
    
    def build_query_string(self, countries, thing_type, versions, battery_level):
        """Build Fleet Indexing query string"""
        conditions = []
        
        # Thing type condition
        if thing_type:
            conditions.append(f"thingTypeName:{thing_type}")
        
        # Country conditions
        if countries:
            if len(countries) == 1:
                conditions.append(f"attributes.country:{countries[0]}")
            else:
                country_conditions = " OR ".join(countries)
                conditions.append(f"attributes.country:({country_conditions})")
        
        # Version conditions
        if versions and thing_type:
            if len(versions) == 1:
                conditions.append(f"shadow.name.\\$package.reported.{thing_type}.version:{versions[0]}")
            else:
                version_conditions = " OR ".join(versions)
                conditions.append(f"shadow.name.\\$package.reported.{thing_type}.version:({version_conditions})")
        
        # Battery level condition
        if battery_level:
            if battery_level.startswith('>'):
                level = battery_level[1:]
                conditions.append(f"shadow.reported.batteryStatus:[{level} TO *]")
            elif battery_level.startswith('<'):
                level = battery_level[1:]
                conditions.append(f"shadow.reported.batteryStatus:[* TO {level}}}")
            elif battery_level.startswith('='):
                level = battery_level[1:]
                conditions.append(f"shadow.reported.batteryStatus:{level}")
            else:
                conditions.append(f"shadow.reported.batteryStatus:{battery_level}")
        
        return " AND ".join(conditions)
    
    def create_dynamic_group(self, group_name, query_string, countries):
        """Create the dynamic thing group"""
        print(f"\n{Fore.BLUE}🔍 Creating dynamic thing group: {Fore.YELLOW}{group_name}{Style.RESET_ALL}")
        
        if self.debug_mode:
            print(f"{Fore.CYAN}🔧 DEBUG - Query string: {query_string}{Style.RESET_ALL}")
        
        # Check if group already exists
        check_result = self.run_aws_command(f"aws iot describe-thing-group --thing-group-name {group_name}")
        
        if check_result and check_result.returncode == 0:
            print(f"{Fore.YELLOW}⚠️  Dynamic thing group already exists: {group_name}{Style.RESET_ALL}")
            return False
        
        # Create tags (use first country if multiple)
        tag_country = countries[0] if countries else "global"
        
        # Create dynamic thing group
        result = self.run_aws_command(f"aws iot create-dynamic-thing-group --thing-group-name {group_name} --query-string '{query_string}' --tags 'Key=country,Value={tag_country}'")
        
        if result and result.returncode == 0:
            print(f"{Fore.GREEN}✅ Dynamic thing group created successfully{Style.RESET_ALL}")
            
            # Show group details
            try:
                group_response = json.loads(result.stdout)
                print(f"\n{Fore.CYAN}📋 Group Details:{Style.RESET_ALL}")
                print(f"{Fore.GREEN}🏷️  Name: {group_response.get('thingGroupName', 'N/A')}{Style.RESET_ALL}")
                print(f"{Fore.GREEN}🔗 ARN: {group_response.get('thingGroupArn', 'N/A')}{Style.RESET_ALL}")
                print(f"{Fore.GREEN}🔍 Query: {query_string}{Style.RESET_ALL}")
            except json.JSONDecodeError:
                print(f"{Fore.YELLOW}⚠️  Group created but couldn't parse response details{Style.RESET_ALL}")
            
            return True
        else:
            print(f"{Fore.RED}❌ Failed to create dynamic thing group{Style.RESET_ALL}")
            if result and result.stderr:
                print(f"{Fore.RED}Error: {result.stderr}{Style.RESET_ALL}")
            return False
    
    def validate_inputs(self, countries, thing_type, versions, battery_level):
        """Validate user inputs"""
        if not any([countries, thing_type, versions, battery_level]):
            print(f"{Fore.RED}❌ At least one criteria must be specified{Style.RESET_ALL}")
            return False
        
        if versions and not thing_type:
            print(f"{Fore.RED}❌ Thing type is required when specifying package versions{Style.RESET_ALL}")
            return False
        
        return True
    
    def run(self):
        """Main execution flow"""
        self.print_header()
        
        # Get debug mode preference
        self.get_debug_mode()
        
        # Get user inputs
        countries, thing_type, versions, battery_level = self.get_user_inputs()
        
        # Validate inputs
        if not self.validate_inputs(countries, thing_type, versions, battery_level):
            sys.exit(1)
        
        # Get group name
        group_name = self.get_group_name(countries, thing_type, versions, battery_level)
        
        if not group_name:
            sys.exit(1)
        
        # Build query string
        query_string = self.build_query_string(countries, thing_type, versions, battery_level)
        
        if not query_string:
            print(f"{Fore.RED}❌ Failed to build query string{Style.RESET_ALL}")
            sys.exit(1)
        
        print(f"\n{Fore.CYAN}🎯 Dynamic Group Configuration:{Style.RESET_ALL}")
        print(f"{Fore.GREEN}🏷️  Group Name: {group_name}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}🌍 Countries: {', '.join(countries) if countries else 'Any'}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}📱 Thing Type: {thing_type or 'Any'}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}📦 Versions: {', '.join(versions) if versions else 'Any'}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}🔋 Battery Level: {battery_level or 'Any'}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}🔍 Query: {query_string}{Style.RESET_ALL}")
        
        # Confirm creation
        confirm = input(f"\n{Fore.YELLOW}Create this dynamic group? [Y/n]: {Style.RESET_ALL}").strip().lower()
        if confirm in ['n', 'no']:
            print(f"{Fore.YELLOW}❌ Dynamic group creation cancelled{Style.RESET_ALL}")
            sys.exit(0)
        
        # Create dynamic group
        success = self.create_dynamic_group(group_name, query_string, countries)
        
        if success:
            print(f"\n{Fore.GREEN}🎉 Dynamic group creation completed successfully!{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.RED}❌ Dynamic group creation failed{Style.RESET_ALL}")
            sys.exit(1)

if __name__ == "__main__":
    creator = DynamicGroupCreator()
    creator.run()