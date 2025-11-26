#!/usr/bin/env python3
"""
README Link Validation Script

This script validates that all links in README translation files are functional
and consistent across all language versions.

Usage:
    python docs/templates/validation_scripts/validate_readme_links.py

Requirements:
    - requests library (pip install requests)
    - All README files must be in the project root directory
"""

import os
import re
import sys
import time
from typing import List, Dict, Tuple
from urllib.parse import urlparse

try:
    import requests
except ImportError:
    print("❌ Error: requests library not found.")
    print("Please install it with: pip install requests")
    sys.exit(1)

def extract_links(content: str) -> List[Tuple[str, str]]:
    """
    Extract all markdown links from content.
    
    Returns:
        List of tuples (link_text, link_url)
    """
    # Match markdown links: [text](url)
    pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    matches = re.findall(pattern, content)
    return matches

def is_external_link(url: str) -> bool:
    """Check if a URL is external (starts with http/https)."""
    return url.startswith('http://') or url.startswith('https://')

def validate_internal_link(url: str) -> bool:
    """
    Validate internal link (file path or anchor).
    
    Returns:
        True if link is valid, False otherwise
    """
    # Remove anchor part for file existence check
    file_path = url.split('#')[0] if '#' in url else url
    
    # Skip empty paths (pure anchors)
    if not file_path:
        return True
    
    # Check if file exists
    return os.path.exists(file_path)

def validate_external_link(url: str, timeout: int = 10) -> Tuple[bool, str]:
    """
    Validate external link by making HTTP request.
    
    Returns:
        Tuple of (is_valid, status_message)
    """
    try:
        # Use HEAD request to avoid downloading content
        response = requests.head(url, timeout=timeout, allow_redirects=True)
        
        if response.status_code < 400:
            return True, f"OK ({response.status_code})"
        else:
            return False, f"HTTP {response.status_code}"
            
    except requests.exceptions.Timeout:
        return False, "Timeout"
    except requests.exceptions.ConnectionError:
        return False, "Connection Error"
    except requests.exceptions.RequestException as e:
        return False, f"Request Error: {str(e)[:50]}"
    except Exception as e:
        return False, f"Unknown Error: {str(e)[:50]}"

def validate_readme_links() -> bool:
    """
    Validate links in all README files.
    
    Returns:
        True if all links are valid, False otherwise
    """
    readme_files = [
        "README.md",
        "README.es.md",
        "README.ja.md", 
        "README.ko.md",
        "README.pt.md",
        "README.zh.md"
    ]
    
    print("🔗 README Link Validation")
    print("=" * 50)
    
    all_valid = True
    external_links_cache = {}  # Cache external link results
    
    for readme_file in readme_files:
        print(f"\n📄 Checking {readme_file}:")
        
        if not os.path.exists(readme_file):
            print(f"   ⚠️  File not found (skipping)")
            continue
        
        try:
            with open(readme_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"   ❌ Error reading file: {e}")
            all_valid = False
            continue
        
        # Extract all links
        links = extract_links(content)
        
        if not links:
            print(f"   ⚠️  No links found")
            continue
        
        print(f"   Found {len(links)} links")
        
        internal_count = 0
        external_count = 0
        broken_count = 0
        
        for link_text, link_url in links:
            if is_external_link(link_url):
                external_count += 1
                
                # Check cache first
                if link_url in external_links_cache:
                    is_valid, status = external_links_cache[link_url]
                else:
                    is_valid, status = validate_external_link(link_url)
                    external_links_cache[link_url] = (is_valid, status)
                    # Add small delay to avoid overwhelming servers
                    time.sleep(0.1)
                
                if is_valid:
                    print(f"   ✅ {link_text}: {link_url} ({status})")
                else:
                    print(f"   ❌ {link_text}: {link_url} ({status})")
                    broken_count += 1
                    all_valid = False
            else:
                internal_count += 1
                
                if validate_internal_link(link_url):
                    print(f"   ✅ {link_text}: {link_url}")
                else:
                    print(f"   ❌ {link_text}: {link_url} (File not found)")
                    broken_count += 1
                    all_valid = False
        
        print(f"   📊 Summary: {len(links)} total, {internal_count} internal, {external_count} external, {broken_count} broken")
    
    print("\n" + "=" * 50)
    if all_valid:
        print("✅ All links are functional!")
        return True
    else:
        print("❌ Some links are broken. Please review and fix.")
        return False

def validate_navigation_consistency() -> bool:
    """
    Validate that navigation tables are consistent across all README files.
    
    Returns:
        True if navigation is consistent, False otherwise
    """
    readme_files = [
        "README.md",
        "README.es.md",
        "README.ja.md", 
        "README.ko.md",
        "README.pt.md",
        "README.zh.md"
    ]
    
    print("\n🧭 Navigation Consistency Check")
    print("=" * 50)
    
    navigation_links = {}
    all_consistent = True
    
    for readme_file in readme_files:
        if not os.path.exists(readme_file):
            continue
        
        try:
            with open(readme_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"❌ Error reading {readme_file}: {e}")
            all_consistent = False
            continue
        
        # Extract navigation table links
        nav_links = []
        lines = content.split('\n')
        in_nav_table = False
        
        for line in lines:
            if '🌍 Available Languages' in line:
                in_nav_table = True
                continue
            
            if in_nav_table and line.strip().startswith('|') and 'README' in line:
                # Extract README links from table row
                matches = re.findall(r'\[([^\]]+\.md)\]\(([^)]+)\)', line)
                for match in matches:
                    nav_links.append(match[1])  # Store the URL part
            elif in_nav_table and line.strip() and not line.strip().startswith('|'):
                # End of table
                break
        
        navigation_links[readme_file] = sorted(nav_links)
        print(f"📄 {readme_file}: {len(nav_links)} navigation links")
    
    # Compare navigation links across files
    if navigation_links:
        reference_links = list(navigation_links.values())[0]
        
        for readme_file, links in navigation_links.items():
            if links != reference_links:
                print(f"❌ {readme_file}: Navigation links inconsistent")
                print(f"   Expected: {reference_links}")
                print(f"   Found: {links}")
                all_consistent = False
            else:
                print(f"✅ {readme_file}: Navigation consistent")
    
    return all_consistent

def main():
    """Main function to run link validation."""
    print("README Link Validation Tool")
    print("Checking all links across language versions...\n")
    
    # Change to project root directory if script is run from templates directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.join(script_dir, '..', '..', '..')
    
    if os.path.exists(os.path.join(project_root, 'README.md')):
        os.chdir(project_root)
        print(f"📁 Working directory: {os.getcwd()}")
    else:
        print("❌ Could not find project root directory with README.md")
        sys.exit(1)
    
    # Run validations
    links_valid = validate_readme_links()
    nav_consistent = validate_navigation_consistency()
    
    if links_valid and nav_consistent:
        print("\n🎉 All validations passed!")
        sys.exit(0)
    else:
        print("\n💥 Validation failed. Please fix issues and run again.")
        sys.exit(1)

if __name__ == "__main__":
    main()