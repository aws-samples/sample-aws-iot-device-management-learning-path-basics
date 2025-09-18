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

# Initialize colorama
init()


class DynamicGroupManager:
    def __init__(self):
        self.region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        self.account_id = None
        self.debug_mode = False
        self.iot_client = None
        self.sts_client = None

        # Rate limiting semaphore
        self.api_semaphore = Semaphore(10)

    def safe_api_call(self, func, operation_name, resource_name, debug=False, **kwargs):
        """Safely execute AWS API call with error handling and optional debug info"""
        try:
            if debug or self.debug_mode:
                print(f"\n🔍 DEBUG: {operation_name}: {resource_name}")
                print(f"📤 API Call: {func.__name__}")
                print("📥 Input Parameters:")
                print(json.dumps(kwargs, indent=2, default=str))

            response = func(**kwargs)

            if debug or self.debug_mode:
                print("📤 API Response:")
                print(json.dumps(response, indent=2, default=str))

            time.sleep(0.1)  # Rate limiting  # nosemgrep: arbitrary-sleep
            return response
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code in ["ResourceNotFoundException", "ResourceNotFound"]:
                if debug or self.debug_mode:
                    print(f"📝 Resource not found: {resource_name}")
                return None
            else:
                print(f"❌ Error in {operation_name} {resource_name}: {e.response['Error']['Message']}")
                if debug or self.debug_mode:
                    print("🔍 DEBUG: Full error response:")
                    print(json.dumps(e.response, indent=2, default=str))
            time.sleep(0.1)  # nosemgrep: arbitrary-sleep
            return None
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            if debug or self.debug_mode:
                import traceback

                print("🔍 DEBUG: Full traceback:")
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

            if self.debug_mode:
                print("🔍 DEBUG: Client configuration:")
                print(f"   IoT Service: {self.iot_client.meta.service_model.service_name}")
                print(f"   API Version: {self.iot_client.meta.service_model.api_version}")

            return True
        except Exception as e:
            print(f"❌ Error initializing AWS clients: {str(e)}")
            return False

    def print_header(self):
        print(f"{Fore.CYAN}🔍 AWS IoT Dynamic Thing Groups Manager (Boto3){Style.RESET_ALL}")
        print(f"{Fore.CYAN}==============================================={Style.RESET_ALL}\n")

        print(f"{Fore.YELLOW}📚 LEARNING GOAL:{Style.RESET_ALL}")
        print(
            f"{Fore.CYAN}This script provides comprehensive management of AWS IoT Dynamic Thing Groups with AWS IoT Fleet Indexing.{Style.RESET_ALL}"
        )
        print(
            f"{Fore.CYAN}You can create groups with query validation, list existing groups with membership counts,{Style.RESET_ALL}"
        )
        print(
            f"{Fore.CYAN}and safely delete groups. Dynamic groups automatically update membership based on real-time{Style.RESET_ALL}"
        )
        print(
            f"{Fore.CYAN}device attributes, firmware versions, and shadow data using AWS IoT Fleet Indexing queries.{Style.RESET_ALL}\n"
        )

        # Initialize clients and display info
        if not self.initialize_clients():
            return False

        print(f"{Fore.CYAN}📍 Region: {Fore.GREEN}{self.region}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}🆔 Account ID: {Fore.GREEN}{self.account_id}{Style.RESET_ALL}\n")

    def get_debug_mode(self):
        """Ask user for debug mode"""
        print(
            f"{Fore.RED}⚠️  WARNING: Debug mode exposes sensitive information (ARNs, account IDs, API responses){Style.RESET_ALL}"
        )
        choice = (
            input(f"{Fore.YELLOW}🔧 Enable debug mode (show all API calls and responses)? [y/N]: {Style.RESET_ALL}")
            .strip()
            .lower()
        )
        self.debug_mode = choice in ["y", "yes"]

        if self.debug_mode:
            print(f"{Fore.GREEN}✅ Debug mode enabled{Style.RESET_ALL}\n")

    def get_operation_choice(self):
        """Get operation choice from user"""
        print(f"{Fore.BLUE}🎯 Select Operation:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}1. Create Dynamic Thing Group{Style.RESET_ALL}")
        print(f"{Fore.CYAN}2. List Dynamic Thing Groups{Style.RESET_ALL}")
        print(f"{Fore.CYAN}3. Describe Dynamic Thing Group{Style.RESET_ALL}")
        print(f"{Fore.CYAN}4. Delete Dynamic Thing Group{Style.RESET_ALL}")
        print(f"{Fore.CYAN}5. Test AWS IoT Fleet Indexing Query{Style.RESET_ALL}")

        while True:
            try:
                choice = int(input(f"{Fore.YELLOW}Enter choice [1-5]: {Style.RESET_ALL}"))
                if 1 <= choice <= 5:
                    return choice
                print(f"{Fore.RED}❌ Invalid choice. Please enter 1-5{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED}❌ Please enter a valid number{Style.RESET_ALL}")

    def get_create_inputs(self):
        """Get dynamic group criteria from user"""
        print(f"\n{Fore.BLUE}📝 Choose Creation Method:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}1. Guided wizard (recommended){Style.RESET_ALL}")
        print(f"{Fore.CYAN}2. Custom Fleet Indexing query{Style.RESET_ALL}")

        while True:
            try:
                choice = int(input(f"{Fore.YELLOW}Enter choice [1-2]: {Style.RESET_ALL}"))
                if choice in [1, 2]:
                    break
                print(f"{Fore.RED}❌ Invalid choice. Please enter 1 or 2{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED}❌ Please enter a valid number{Style.RESET_ALL}")

        if choice == 2:
            return self.get_custom_query_inputs()

        print(f"\n{Fore.BLUE}📝 Define Dynamic Group Criteria (all fields optional):{Style.RESET_ALL}\n")

        # Countries
        print(f"{Fore.YELLOW}🌍 Countries (comma-separated, e.g., US,CA,MX or leave empty):{Style.RESET_ALL}")
        countries_input = input().strip()
        if countries_input:
            countries = [c.strip().upper() for c in countries_input.split(",") if c.strip()]
        else:
            countries = []

        # Thing type
        print(f"{Fore.YELLOW}📱 Thing type (e.g., SedanVehicle or leave empty):{Style.RESET_ALL}")
        thing_type_input = input().strip()
        thing_type = thing_type_input if thing_type_input else None

        # Versions
        print(f"{Fore.YELLOW}📦 Package versions (comma-separated, e.g., 1.0.0,1.1.0 or leave empty):{Style.RESET_ALL}")
        versions_input = input().strip()
        if versions_input:
            versions = [v.strip() for v in versions_input.split(",") if v.strip()]
        else:
            versions = []

        # Battery level
        print(f"{Fore.YELLOW}🔋 Battery level (e.g., >50, <30, =75 or leave empty):{Style.RESET_ALL}")
        battery_level_input = input().strip()
        battery_level = battery_level_input if battery_level_input else None

        return countries, thing_type, versions, battery_level

    def get_custom_query_inputs(self):
        """Get custom query and group name from user"""
        print(f"\n{Fore.BLUE}🧪 Custom AWS IoT Fleet Indexing Query:{Style.RESET_ALL}\n")

        print(f"{Fore.CYAN}Example queries:{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}• thingTypeName:SedanVehicle{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}• attributes.country:US AND shadow.reported.batteryStatus:[50 TO *]{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}• shadow.name.$package.reported.SedanVehicle.version:1.0.0{Style.RESET_ALL}")

        query = input(f"\n{Fore.YELLOW}Enter AWS IoT Fleet Indexing query: {Style.RESET_ALL}").strip()

        if not query:
            print(f"{Fore.RED}❌ Query cannot be empty{Style.RESET_ALL}")
            return None

        group_name = input(f"{Fore.YELLOW}Enter group name: {Style.RESET_ALL}").strip()

        if not group_name:
            print(f"{Fore.RED}❌ Group name cannot be empty{Style.RESET_ALL}")
            return None

        return "CUSTOM", query, group_name

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
            version_clean = versions[0].replace(".", "_")
            name_parts.append(version_clean)

        # Add battery level
        if battery_level:
            battery_clean = battery_level.replace(">", "gt").replace("<", "lt").replace("=", "eq")
            name_parts.append(f"battery{battery_clean}")

        # Add suffix
        name_parts.append("Devices")

        return "_".join(name_parts)

    def get_group_name(self, countries, thing_type, versions, battery_level):
        """Get group name from user or generate automatically"""
        # Check if multiple countries or versions (requires custom name)
        needs_custom_name = len(countries) > 1 or len(versions) > 1

        if needs_custom_name:
            print(
                f"\n{Fore.YELLOW}📝 Multiple countries or versions selected. Please provide a custom group name:{Style.RESET_ALL}"
            )
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
            if confirm in ["n", "no"]:
                custom_name = input(f"{Fore.YELLOW}Enter custom name: {Style.RESET_ALL}").strip()
                if custom_name:
                    return custom_name
                else:
                    return auto_name

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
                conditions.append(f"shadow.name.$package.reported.{thing_type}.version:{versions[0]}")
            else:
                version_conditions = " OR ".join(versions)
                conditions.append(f"shadow.name.$package.reported.{thing_type}.version:({version_conditions})")

        # Battery level condition
        if battery_level:
            if battery_level.startswith(">"):
                level = battery_level[1:]
                conditions.append(f"shadow.reported.batteryStatus:[{level} TO *]")
            elif battery_level.startswith("<"):
                level = battery_level[1:]
                conditions.append(f"shadow.reported.batteryStatus:[* TO {level}]")
            elif battery_level.startswith("="):
                level = battery_level[1:]
                conditions.append(f"shadow.reported.batteryStatus:{level}")
            else:
                conditions.append(f"shadow.reported.batteryStatus:{battery_level}")

        return " AND ".join(conditions)

    def test_query(self, query_string):
        """Test Fleet Indexing query and show matching devices"""
        print(f"\n{Fore.BLUE}🔍 Testing AWS IoT Fleet Indexing query...{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Query: {query_string}{Style.RESET_ALL}\n")

        # Search for matching things using AWS IoT Fleet Indexing
        response = self.safe_api_call(
            self.iot_client.search_index,
            "Fleet Indexing Search",
            query_string,
            debug=self.debug_mode,
            indexName="AWS_Things",
            queryString=query_string,
            maxResults=250,
        )

        if response:
            things = response.get("things", [])
            next_token = response.get("nextToken")
            count = len(things)

            if count == 0:
                print(f"{Fore.YELLOW}⚠️  No devices currently match this query{Style.RESET_ALL}")
                return 0
            elif count < 250 and not next_token:
                print(f"{Fore.GREEN}✅ Found {count} devices that match this query{Style.RESET_ALL}")
            else:
                print(f"{Fore.GREEN}✅ Found {count}+ devices that match this query (showing first 250){Style.RESET_ALL}")

            # Show device details
            if things and count <= 10:
                print(f"\n{Fore.CYAN}📋 Matching devices:{Style.RESET_ALL}")
                for thing in things:
                    name = thing.get("thingName", "Unknown")
                    thing_type = thing.get("thingTypeName", "N/A")
                    print(f"{Fore.GREEN}  • {name} ({thing_type}){Style.RESET_ALL}")
            elif things:
                print(f"\n{Fore.CYAN}📋 Sample devices:{Style.RESET_ALL}")
                for thing in things[:5]:
                    name = thing.get("thingName", "Unknown")
                    thing_type = thing.get("thingTypeName", "N/A")
                    print(f"{Fore.GREEN}  • {name} ({thing_type}){Style.RESET_ALL}")
                print(f"{Fore.CYAN}  ... and {count - 5} more{Style.RESET_ALL}")

            return count
        else:
            print(f"{Fore.RED}❌ Failed to search for matching devices{Style.RESET_ALL}")
            return -1

    def create_dynamic_group(self, group_name, query_string, countries):
        """Create the dynamic thing group"""
        print(f"\n{Fore.BLUE}🔍 Creating dynamic thing group: {Fore.YELLOW}{group_name}{Style.RESET_ALL}")

        # Check if group already exists
        existing_group = self.safe_api_call(
            self.iot_client.describe_thing_group,
            "Thing Group Check",
            group_name,
            debug=self.debug_mode,
            thingGroupName=group_name,
        )

        if existing_group:
            print(f"{Fore.YELLOW}⚠️  Dynamic thing group already exists: {group_name}{Style.RESET_ALL}")
            return False

        # Create tags (use first country if multiple)
        tag_country = countries[0] if countries else "global"
        tags = [{"Key": "country", "Value": tag_country}]

        # Create dynamic thing group
        response = self.safe_api_call(
            self.iot_client.create_dynamic_thing_group,
            "Dynamic Thing Group",
            group_name,
            debug=self.debug_mode,
            thingGroupName=group_name,
            queryString=query_string,
            tags=tags,
        )

        if response:
            print(f"{Fore.GREEN}✅ Dynamic thing group created successfully{Style.RESET_ALL}")

            # Show group details
            print(f"\n{Fore.CYAN}📋 Group Details:{Style.RESET_ALL}")
            print(f"{Fore.GREEN}🏷️  Name: {response.get('thingGroupName', 'N/A')}{Style.RESET_ALL}")
            print(f"{Fore.GREEN}🔗 ARN: {response.get('thingGroupArn', 'N/A')}{Style.RESET_ALL}")
            print(f"{Fore.GREEN}🔍 Query: {query_string}{Style.RESET_ALL}")

            return True
        else:
            print(f"{Fore.RED}❌ Failed to create dynamic thing group{Style.RESET_ALL}")
            return False

    def get_group_details_parallel(self, group_name):
        """Get group details in parallel for list operation"""
        with self.api_semaphore:
            # Get group details to check if it's dynamic
            detail_response = self.safe_api_call(
                self.iot_client.describe_thing_group,
                "Thing Group Detail",
                group_name,
                debug=False,  # Don't debug in parallel operations
                thingGroupName=group_name,
            )

            if not detail_response:
                return None

            query_string = detail_response.get("queryString")
            if not query_string:  # Not a dynamic group
                return None

            # Get group info
            group_info = detail_response.get("thingGroupInfo", {})
            creation_date = group_info.get("creationDate", "Unknown")

            # Get member count
            member_response = self.safe_api_call(
                self.iot_client.list_things_in_thing_group,
                "Thing Group Members",
                group_name,
                debug=False,
                thingGroupName=group_name,
                maxResults=250,
            )

            member_count = 0
            if member_response:
                things = member_response.get("things", [])
                member_count = len(things)

                # Check if there are more members
                if member_response.get("nextToken") and member_count == 250:
                    member_count = f"{member_count}+"
            else:
                member_count = "Unknown"

            return {"name": group_name, "query": query_string, "created": creation_date, "members": member_count}

    def list_dynamic_groups(self):
        """List all dynamic thing groups with details"""
        print(f"\n{Fore.BLUE}📋 Listing Dynamic Thing Groups...{Style.RESET_ALL}\n")

        # Get all thing groups
        response = self.safe_api_call(
            self.iot_client.list_thing_groups, "Thing Groups List", "all groups", debug=self.debug_mode, maxResults=250
        )

        if not response:
            print(f"{Fore.RED}❌ Failed to list thing groups{Style.RESET_ALL}")
            return

        all_groups = response.get("thingGroups", [])
        group_names = [group.get("groupName") for group in all_groups if group.get("groupName")]

        if not group_names:
            print(f"{Fore.YELLOW}📭 No thing groups found{Style.RESET_ALL}")
            return

        # Filter for dynamic groups and get details
        if self.debug_mode:
            print(f"{Fore.BLUE}🔧 Processing {len(group_names)} groups sequentially (debug mode)...{Style.RESET_ALL}")
            dynamic_groups = []
            for group_name in group_names:
                group_details = self.get_group_details_parallel(group_name)
                if group_details:
                    dynamic_groups.append(group_details)
        else:
            print(f"{Fore.BLUE}🔧 Processing {len(group_names)} groups in parallel...{Style.RESET_ALL}")
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(self.get_group_details_parallel, group_name) for group_name in group_names]
                dynamic_groups = [future.result() for future in as_completed(futures) if future.result()]

        if not dynamic_groups:
            print(f"{Fore.YELLOW}📭 No dynamic thing groups found{Style.RESET_ALL}")
            print(f"{Fore.CYAN}💡 Use option 1 to create your first dynamic group{Style.RESET_ALL}")
            return

        print(f"{Fore.GREEN}✅ Found {len(dynamic_groups)} dynamic thing group(s):{Style.RESET_ALL}\n")

        for i, group in enumerate(dynamic_groups, 1):
            print(f"{Fore.CYAN}{i}. {Fore.YELLOW}{group['name']}{Style.RESET_ALL}")
            print(f"   {Fore.GREEN}👥 Members: {group['members']}{Style.RESET_ALL}")
            print(f"   {Fore.GREEN}🔍 Query: {group['query']}{Style.RESET_ALL}")
            print(f"   {Fore.GREEN}📅 Created: {group['created']}{Style.RESET_ALL}")
            print()

    def get_thing_details_parallel(self, thing_name):
        """Get thing details in parallel for describe operation"""
        with self.api_semaphore:
            response = self.safe_api_call(
                self.iot_client.describe_thing, "Thing Detail", thing_name, debug=False, thingName=thing_name
            )

            if response:
                thing_type = response.get("thingTypeName", "N/A")
                attributes = response.get("attributes", {})
                country = attributes.get("country", "N/A")
                return f"{thing_name} ({thing_type}) - {country}"
            else:
                return thing_name

    def describe_dynamic_group(self):
        """Describe a specific dynamic thing group and show its devices"""
        print(f"\n{Fore.BLUE}🔍 Describe Dynamic Thing Group{Style.RESET_ALL}\n")

        group_name = input(f"{Fore.YELLOW}Enter dynamic thing group name: {Style.RESET_ALL}").strip()

        if not group_name:
            print(f"{Fore.RED}❌ Group name cannot be empty{Style.RESET_ALL}")
            return

        # Get group details
        detail_response = self.safe_api_call(
            self.iot_client.describe_thing_group,
            "Thing Group Detail",
            group_name,
            debug=self.debug_mode,
            thingGroupName=group_name,
        )

        if not detail_response:
            print(f"{Fore.RED}❌ Thing group '{group_name}' not found{Style.RESET_ALL}")
            return

        query_string = detail_response.get("queryString")
        if not query_string:
            print(f"{Fore.RED}❌ '{group_name}' is not a dynamic thing group{Style.RESET_ALL}")
            return

        # Display group information
        group_info = detail_response.get("thingGroupInfo", {})
        print(f"{Fore.GREEN}🏷️  Group Name: {group_name}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}🔍 Query: {query_string}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}📅 Created: {group_info.get('creationDate', 'Unknown')}{Style.RESET_ALL}")

        # Get group members
        member_response = self.safe_api_call(
            self.iot_client.list_things_in_thing_group,
            "Thing Group Members",
            group_name,
            debug=self.debug_mode,
            thingGroupName=group_name,
            maxResults=250,
        )

        if not member_response:
            print(f"{Fore.RED}❌ Failed to get group members{Style.RESET_ALL}")
            return

        things = member_response.get("things", [])

        if not things:
            print(f"{Fore.YELLOW}💭 No devices currently in this group{Style.RESET_ALL}")
        else:
            has_more = member_response.get("nextToken") is not None
            count_text = f"{len(things)}+" if has_more else str(len(things))

            print(f"{Fore.GREEN}👥 Members: {count_text} devices{Style.RESET_ALL}")

            # Show device details
            print(f"\n{Fore.CYAN}📝 Device List:{Style.RESET_ALL}")

            if self.debug_mode:
                print(f"{Fore.BLUE}🔧 Getting device details sequentially (debug mode)...{Style.RESET_ALL}")
                for i, thing_name in enumerate(things, 1):
                    thing_detail = self.get_thing_details_parallel(thing_name)
                    print(f"{Fore.GREEN}{i:3d}. {thing_detail}{Style.RESET_ALL}")
            else:
                print(f"{Fore.BLUE}🔧 Getting device details in parallel...{Style.RESET_ALL}")
                with ThreadPoolExecutor(max_workers=10) as executor:
                    futures = [executor.submit(self.get_thing_details_parallel, thing_name) for thing_name in things]

                    for i, future in enumerate(as_completed(futures), 1):
                        thing_detail = future.result()
                        print(f"{Fore.GREEN}{i:3d}. {thing_detail}{Style.RESET_ALL}")

            if has_more:
                print(f"{Fore.CYAN}   ... and more (showing first 250){Style.RESET_ALL}")

    def delete_dynamic_group(self):
        """Delete a dynamic thing group"""
        print(f"\n{Fore.BLUE}🗑️  Delete Dynamic Thing Group{Style.RESET_ALL}\n")

        # Get list of dynamic groups first
        response = self.safe_api_call(
            self.iot_client.list_thing_groups, "Thing Groups List", "all groups", debug=self.debug_mode, maxResults=250
        )

        if not response:
            print(f"{Fore.RED}❌ Failed to list thing groups{Style.RESET_ALL}")
            return

        all_groups = response.get("thingGroups", [])
        group_names = [group.get("groupName") for group in all_groups if group.get("groupName")]

        # Filter for dynamic groups
        dynamic_groups = []

        print(f"{Fore.BLUE}🔍 Checking {len(group_names)} groups for dynamic groups...{Style.RESET_ALL}")

        for group_name in group_names:
            detail_response = self.safe_api_call(
                self.iot_client.describe_thing_group, "Thing Group Check", group_name, debug=False, thingGroupName=group_name
            )

            if detail_response and detail_response.get("queryString"):  # Has query string = dynamic
                dynamic_groups.append(group_name)

        if not dynamic_groups:
            print(f"{Fore.YELLOW}📭 No dynamic thing groups found to delete{Style.RESET_ALL}")
            return

        # Show available groups
        print(f"{Fore.CYAN}Available dynamic thing groups:{Style.RESET_ALL}")
        for i, group_name in enumerate(dynamic_groups, 1):
            print(f"{Fore.CYAN}{i}. {group_name}{Style.RESET_ALL}")

        # Get user selection
        while True:
            try:
                choice = int(input(f"\n{Fore.YELLOW}Select group to delete [1-{len(dynamic_groups)}]: {Style.RESET_ALL}"))
                if 1 <= choice <= len(dynamic_groups):
                    selected_group = dynamic_groups[choice - 1]
                    break
                print(f"{Fore.RED}❌ Invalid choice. Please enter 1-{len(dynamic_groups)}{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED}❌ Please enter a valid number{Style.RESET_ALL}")

        # Confirm deletion
        print(f"\n{Fore.YELLOW}⚠️  You are about to delete dynamic thing group: {Fore.RED}{selected_group}{Style.RESET_ALL}")
        confirm = input(f"{Fore.YELLOW}Type 'DELETE' to confirm: {Style.RESET_ALL}").strip()

        if confirm != "DELETE":
            print(f"{Fore.YELLOW}❌ Deletion cancelled{Style.RESET_ALL}")
            return

        # Delete the group
        response = self.safe_api_call(
            self.iot_client.delete_dynamic_thing_group,
            "Dynamic Thing Group Delete",
            selected_group,
            debug=self.debug_mode,
            thingGroupName=selected_group,
        )

        if response:
            print(f"{Fore.GREEN}✅ Dynamic thing group '{selected_group}' deleted successfully{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}❌ Failed to delete dynamic thing group{Style.RESET_ALL}")

    def test_custom_query(self):
        """Test a custom Fleet Indexing query"""
        print(f"\n{Fore.BLUE}🧪 Test AWS IoT Fleet Indexing Query{Style.RESET_ALL}\n")

        print(f"{Fore.CYAN}Example queries:{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}• thingTypeName:SedanVehicle{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}• attributes.country:US{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}• shadow.reported.batteryStatus:[50 TO *]{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}• thingTypeName:SedanVehicle AND attributes.country:US{Style.RESET_ALL}")

        while True:
            query = input(
                f"\n{Fore.YELLOW}Enter AWS IoT Fleet Indexing query (or 'exit' to return): {Style.RESET_ALL}"
            ).strip()

            if query.lower() in ["exit", "quit", "back"]:
                break

            if not query:
                print(f"{Fore.RED}❌ No query provided{Style.RESET_ALL}")
                continue

            self.test_query(query)

            print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")

    def validate_create_inputs(self, countries, thing_type, versions, battery_level):
        """Validate user inputs for creation"""
        if not any([countries, thing_type, versions, battery_level]):
            print(f"{Fore.RED}❌ At least one criteria must be specified{Style.RESET_ALL}")
            return False

        if versions and not thing_type:
            print(f"{Fore.RED}❌ Thing type is required when specifying package versions{Style.RESET_ALL}")
            return False

        return True

    def educational_pause(self, title, description):
        """Pause execution with educational content"""
        print(f"\n{Fore.YELLOW}📚 LEARNING MOMENT: {title}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{description}{Style.RESET_ALL}")
        input(f"\n{Fore.GREEN}Press Enter to continue...{Style.RESET_ALL}")
        print()

    def run_create_operation(self):
        """Run create dynamic group operation"""
        self.educational_pause(
            "Dynamic Groups - Automated Device Organization",
            "AWS IoT Dynamic Thing Groups use AWS IoT Fleet Indexing queries to automatically organize devices based\n"
            "on real-time attributes. Unlike AWS IoT static thing groups, membership updates automatically when\n"
            "device properties change. You can query AWS IoT device registry attributes (country, thing type),\n"
            "AWS IoT Device Shadows (battery level), and AWS IoT Software Package Catalog shadows (firmware versions). This enables\n"
            "sophisticated device segmentation for targeted operations and monitoring.\n\n"
            "🔄 NEXT: We will define criteria and validate the query before creating the group",
        )

        # Get user inputs
        inputs = self.get_create_inputs()

        if not inputs:
            return

        # Handle custom query
        if inputs[0] == "CUSTOM":
            _, query_string, group_name = inputs
            countries = []  # No specific countries for custom query
        else:
            countries, thing_type, versions, battery_level = inputs

            # Validate inputs
            if not self.validate_create_inputs(countries, thing_type, versions, battery_level):
                return

            # Get group name
            group_name = self.get_group_name(countries, thing_type, versions, battery_level)

            if not group_name:
                return

            # Build query string
            query_string = self.build_query_string(countries, thing_type, versions, battery_level)

            if not query_string:
                print(f"{Fore.RED}❌ Failed to build query string{Style.RESET_ALL}")
                return

            print(f"\n{Fore.CYAN}🎯 Dynamic Group Configuration:{Style.RESET_ALL}")
            print(f"{Fore.GREEN}🏷️  Group Name: {group_name}{Style.RESET_ALL}")
            print(f"{Fore.GREEN}🌍 Countries: {', '.join(countries) if countries else 'Any'}{Style.RESET_ALL}")
            print(f"{Fore.GREEN}📱 Thing Type: {thing_type or 'Any'}{Style.RESET_ALL}")
            print(f"{Fore.GREEN}📦 Versions: {', '.join(versions) if versions else 'Any'}{Style.RESET_ALL}")
            print(f"{Fore.GREEN}🔋 Battery Level: {battery_level or 'Any'}{Style.RESET_ALL}")

        print(f"{Fore.GREEN}🔍 Query: {query_string}{Style.RESET_ALL}")

        # Test query first
        device_count = self.test_query(query_string)

        if device_count == -1:
            print(f"{Fore.RED}❌ Query validation failed. Please check AWS IoT Fleet Indexing is enabled.{Style.RESET_ALL}")
            return

        # Confirm creation
        confirm = input(f"\n{Fore.YELLOW}Create this dynamic group? [Y/n]: {Style.RESET_ALL}").strip().lower()
        if confirm in ["n", "no"]:
            print(f"{Fore.YELLOW}❌ Dynamic group creation cancelled{Style.RESET_ALL}")
            return

        # Create dynamic group
        success = self.create_dynamic_group(group_name, query_string, countries)

        if success:
            print(f"\n{Fore.GREEN}🎉 Dynamic group creation completed successfully!{Style.RESET_ALL}")
            print(f"{Fore.CYAN}💡 The group will automatically update as device attributes change{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.RED}❌ Dynamic group creation failed{Style.RESET_ALL}")

    def run(self):
        """Main execution flow"""
        self.print_header()

        # Get debug mode preference
        self.get_debug_mode()

        while True:
            # Get operation choice
            operation = self.get_operation_choice()

            if operation == 1:
                self.run_create_operation()
            elif operation == 2:
                self.list_dynamic_groups()
            elif operation == 3:
                self.describe_dynamic_group()
            elif operation == 4:
                self.delete_dynamic_group()
            elif operation == 5:
                self.test_custom_query()

            # Ask if user wants to continue
            print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
            continue_choice = input(f"{Fore.YELLOW}Continue with another operation? [Y/n]: {Style.RESET_ALL}").strip().lower()
            if continue_choice in ["n", "no"]:
                print(f"\n{Fore.GREEN}👋 Thank you for using Dynamic Groups Manager!{Style.RESET_ALL}")
                break
            print()  # Add spacing before next operation


if __name__ == "__main__":
    manager = DynamicGroupManager()
    try:
        manager.run()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}👋 Dynamic group management cancelled by user. Goodbye!{Style.RESET_ALL}")
        sys.exit(0)
