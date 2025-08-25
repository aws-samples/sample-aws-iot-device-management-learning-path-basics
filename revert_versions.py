#!/usr/bin/env python3

import subprocess
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Semaphore, Lock
from colorama import Fore, Style, init

# Initialize colorama
init()

class IoTVersionReverter:
    def __init__(self):
        self.region = None
        self.account_id = None
        self.data_endpoint = None
        self.debug_mode = False
        
        # Rate limiting semaphore for shadow updates (100 TPS limit)
        self.shadow_update_semaphore = Semaphore(80)  # Use 80 for safety
        
        # Progress tracking
        self.progress_lock = Lock()
        self.updated_count = 0
    
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
        print(f"{Fore.CYAN}🔄 AWS IoT Version Reverter{Style.RESET_ALL}")
        print(f"{Fore.CYAN}============================{Style.RESET_ALL}\n")
        
        print(f"{Fore.YELLOW}📚 LEARNING GOAL:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}This script demonstrates firmware version rollback using Fleet Indexing and device shadows.{Style.RESET_ALL}")
        print(f"{Fore.CYAN}It shows how to query devices by firmware version, update device shadows to reflect{Style.RESET_ALL}")
        print(f"{Fore.CYAN}rollback operations, and maintain accurate device state across your IoT fleet.{Style.RESET_ALL}")
        print(f"{Fore.CYAN}This is essential for managing firmware deployments and handling rollback scenarios.{Style.RESET_ALL}\n")
        
        # Get and display region and account ID
        region_result = self.run_aws_command_basic("aws configure get region")
        account_result = self.run_aws_command_basic("aws sts get-caller-identity --query Account --output text")
        
        self.region = region_result.stdout.strip() if region_result and region_result.returncode == 0 else "us-east-1"
        self.account_id = account_result.stdout.strip() if account_result and account_result.returncode == 0 else "unknown"
        
        print(f"{Fore.CYAN}📍 Region: {Fore.GREEN}{self.region}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}🆔 Account ID: {Fore.GREEN}{self.account_id}{Style.RESET_ALL}\n")
    
    def get_data_endpoint(self):
        """Get IoT data ATS endpoint"""
        result = self.run_aws_command_basic(f"aws iot describe-endpoint --endpoint-type iot:Data-ATS --region {self.region} --query 'endpointAddress' --output text")
        if result and result.returncode == 0:
            self.data_endpoint = result.stdout.strip()
        else:
            print(f"{Fore.RED}❌ Failed to get IoT data endpoint{Style.RESET_ALL}")
    
    def get_debug_mode(self):
        """Ask user for debug mode"""
        choice = input(f"{Fore.YELLOW}🔧 Enable debug mode (show all commands and outputs)? [y/N]: {Style.RESET_ALL}").strip().lower()
        self.debug_mode = choice in ['y', 'yes']
        
        if self.debug_mode:
            print(f"{Fore.GREEN}✅ Debug mode enabled{Style.RESET_ALL}\n")
    
    def get_user_inputs(self):
        """Get thing type and target version from user"""
        print(f"{Fore.YELLOW}📝 Enter thing type (e.g., motionSensor):{Style.RESET_ALL}")
        thing_type = input().strip()
        
        if not thing_type:
            print(f"{Fore.RED}❌ Thing type is required{Style.RESET_ALL}")
            return None, None
        
        print(f"{Fore.YELLOW}📝 Enter target version (e.g., 1.0.0):{Style.RESET_ALL}")
        target_version = input().strip()
        
        if not target_version:
            print(f"{Fore.RED}❌ Target version is required{Style.RESET_ALL}")
            return None, None
        
        return thing_type, target_version
    
    def find_devices_to_revert(self, thing_type, target_version):
        """Find devices that need version revert using Fleet Indexing"""
        print(f"{Fore.BLUE}🔍 Searching for devices to revert...{Style.RESET_ALL}")
        
        # Query: devices with thing type that have $package shadow but NOT the target version
        query = f"thingTypeName:{thing_type} AND shadow.name.\\$package.reported.{thing_type}.version:* AND NOT shadow.name.\\$package.reported.{thing_type}.version:{target_version}"
        
        if self.debug_mode:
            print(f"{Fore.CYAN}🔧 DEBUG - Search query: {query}{Style.RESET_ALL}")
        
        result = self.run_aws_command(f"aws iot search-index --index-name AWS_Things --query-string '{query}' --query 'things[].thingName' --output text")
        
        if not result or result.returncode != 0:
            print(f"{Fore.RED}❌ Failed to search for devices{Style.RESET_ALL}")
            return []
        
        device_names = result.stdout.strip().split()
        device_names = [name for name in device_names if name and name != 'None']
        
        print(f"{Fore.GREEN}📊 Found {len(device_names)} devices to revert to version {target_version}{Style.RESET_ALL}")
        
        return device_names
    
    def update_device_shadow(self, device_name, thing_type, target_version, index, total):
        """Update a single device's $package shadow version"""
        with self.shadow_update_semaphore:
            if self.debug_mode or index % 20 == 1:
                print(f"{Fore.MAGENTA}🔄 Processing device {index}/{total}: {Fore.YELLOW}{device_name}{Style.RESET_ALL}")
            
            # Create shadow payload
            shadow_payload = {
                "state": {
                    "reported": {
                        thing_type: {
                            "version": target_version,
                            "attributes": {}
                        }
                    }
                }
            }
            
            payload_json = json.dumps(shadow_payload)
            
            # Update $package shadow
            result = self.run_aws_command(f"aws iot-data update-thing-shadow --thing-name {device_name} --shadow-name '$package' --cli-binary-format raw-in-base64-out --payload '{payload_json}' --endpoint-url https://{self.data_endpoint} /dev/null")
            
            if result and result.returncode == 0:
                with self.progress_lock:
                    self.updated_count += 1
                    if self.debug_mode:
                        print(f"{Fore.GREEN}✅ [{self.updated_count}/{total}] Updated: {device_name}{Style.RESET_ALL}")
                return True
            else:
                print(f"{Fore.RED}❌ Failed to update device: {device_name}{Style.RESET_ALL}")
                return False
            
            time.sleep(0.0125)  # Rate limiting: 80 TPS
    
    def revert_device_versions(self, device_names, thing_type, target_version):
        """Revert device versions in parallel"""
        if not device_names:
            print(f"{Fore.YELLOW}ℹ️  No devices found to revert{Style.RESET_ALL}")
            return
        
        print(f"{Fore.BLUE}🚀 Reverting {len(device_names)} devices to version {target_version} (80 TPS)...{Style.RESET_ALL}")
        
        self.updated_count = 0  # Reset counter
        
        with ThreadPoolExecutor(max_workers=80) as executor:
            futures = [executor.submit(self.update_device_shadow, device_name, thing_type, target_version, i, len(device_names)) 
                      for i, device_name in enumerate(device_names, 1)]
            
            success_count = 0
            completed = 0
            for future in as_completed(futures):
                completed += 1
                if future.result():
                    success_count += 1
                
                # Progress update every 20 completions
                if completed % 20 == 0 or completed == len(device_names):
                    print(f"{Fore.CYAN}📊 Progress: {completed}/{len(device_names)} devices processed, {success_count} successful{Style.RESET_ALL}")
        
        print(f"{Fore.CYAN}📊 Version revert completed: {success_count}/{len(device_names)} successful{Style.RESET_ALL}")
    
    def confirm_revert(self, device_count, thing_type, target_version):
        """Confirm version revert with user"""
        print(f"\n{Fore.YELLOW}⚠️  WARNING: This will revert {device_count} devices of type '{thing_type}' to version '{target_version}'{Style.RESET_ALL}")
        
        confirm = input(f"\n{Fore.YELLOW}Type 'REVERT' to confirm: {Style.RESET_ALL}")
        return confirm == "REVERT"
    
    def run(self):
        """Main execution flow"""
        self.print_header()
        
        # Get IoT data ATS endpoint
        self.get_data_endpoint()
        
        # Get debug mode preference
        self.get_debug_mode()
        
        # Get user inputs
        thing_type, target_version = self.get_user_inputs()
        
        if not thing_type or not target_version:
            sys.exit(1)
        
        # Find devices to revert
        device_names = self.find_devices_to_revert(thing_type, target_version)
        
        if not device_names:
            print(f"{Fore.GREEN}✅ All devices of type '{thing_type}' are already on version '{target_version}'{Style.RESET_ALL}")
            sys.exit(0)
        
        # Confirm revert
        if not self.confirm_revert(len(device_names), thing_type, target_version):
            print(f"{Fore.YELLOW}❌ Version revert cancelled by user{Style.RESET_ALL}")
            sys.exit(0)
        
        print(f"\n{Fore.BLUE}🔄 Starting version revert process...{Style.RESET_ALL}\n")
        
        start_time = time.time()
        
        # Revert device versions
        self.revert_device_versions(device_names, thing_type, target_version)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n{Fore.GREEN}🎉 Version revert completed successfully!{Style.RESET_ALL}")
        print(f"{Fore.CYAN}📊 Reverted {len(device_names)} devices to version {target_version}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}⏱️  Total execution time: {duration:.2f} seconds{Style.RESET_ALL}")

if __name__ == "__main__":
    reverter = IoTVersionReverter()
    reverter.run()