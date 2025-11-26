#!/usr/bin/env python3
"""
README Structure Validation Script

This script validates that all README translation files maintain consistent
structure with the main README.md file.

Usage:
    python docs/templates/validation_scripts/validate_readme_structure.py

Requirements:
    - All README files must be in the project root directory
    - Main README.md must exist as the reference
"""

import os
import re
import sys
from typing import List, Dict, Tuple

def extract_headers(content: str) -> List[Tuple[int, str]]:
    """
    Extract all markdown headers from content.
    
    Returns:
        List of tuples (level, text) where level is header depth (1-6)
    """
    headers = []
    lines = content.split('\n')
    
    for line in lines:
        # Match markdown headers (# ## ### etc.)
        match = re.match(r'^(#{1,6})\s+(.+)$', line.strip())
        if match:
            level = len(match.group(1))
            text = match.group(2).strip()
            headers.append((level, text))
    
    return headers

def extract_navigation_table(content: str) -> str:
    """
    Extract the language navigation table from README content.
    
    Returns:
        The navigation table as a string, or empty string if not found
    """
    lines = content.split('\n')
    in_table = False
    table_lines = []
    
    for line in lines:
        # Look for the start of the navigation table
        if '🌍 Available Languages' in line:
            in_table = True
            table_lines.append(line)
            continue
        
        if in_table:
            # Continue collecting table lines
            if line.strip().startswith('|') or line.strip().startswith('---'):
                table_lines.append(line)
            elif line.strip() == '':
                # Empty line might be part of table formatting
                table_lines.append(line)
            elif line.strip().startswith('---') and len(line.strip()) > 10:
                # End of table section
                table_lines.append(line)
                break
            elif not line.strip().startswith('|') and line.strip() != '':
                # Non-table content, end of table
                break
    
    return '\n'.join(table_lines)

def validate_structure() -> bool:
    """
    Validate README structure consistency across all language files.
    
    Returns:
        True if all files are consistent, False otherwise
    """
    # Define expected README files
    main_readme = "README.md"
    translation_files = [
        "README.es.md",
        "README.ja.md", 
        "README.ko.md",
        "README.pt.md",
        "README.zh.md"
    ]
    
    print("🔍 README Structure Validation")
    print("=" * 50)
    
    # Check if main README exists
    if not os.path.exists(main_readme):
        print(f"❌ Main README file '{main_readme}' not found!")
        return False
    
    # Read main README
    try:
        with open(main_readme, 'r', encoding='utf-8') as f:
            main_content = f.read()
    except Exception as e:
        print(f"❌ Error reading {main_readme}: {e}")
        return False
    
    # Extract structure from main README
    main_headers = extract_headers(main_content)
    main_navigation = extract_navigation_table(main_content)
    
    print(f"📄 Main README ({main_readme}):")
    print(f"   Headers: {len(main_headers)}")
    print(f"   Navigation table: {'✅ Found' if main_navigation else '❌ Not found'}")
    
    all_valid = True
    
    # Validate each translation file
    for translation_file in translation_files:
        print(f"\n📄 Checking {translation_file}:")
        
        if not os.path.exists(translation_file):
            print(f"   ⚠️  File not found (skipping)")
            continue
        
        try:
            with open(translation_file, 'r', encoding='utf-8') as f:
                translation_content = f.read()
        except Exception as e:
            print(f"   ❌ Error reading file: {e}")
            all_valid = False
            continue
        
        # Extract structure from translation
        translation_headers = extract_headers(translation_content)
        translation_navigation = extract_navigation_table(translation_content)
        
        # Validate header count
        if len(main_headers) != len(translation_headers):
            print(f"   ❌ Header count mismatch:")
            print(f"      Main: {len(main_headers)}, Translation: {len(translation_headers)}")
            all_valid = False
        else:
            print(f"   ✅ Header count consistent ({len(translation_headers)})")
        
        # Validate header levels (structure)
        main_levels = [level for level, _ in main_headers]
        translation_levels = [level for level, _ in translation_headers]
        
        if main_levels != translation_levels:
            print(f"   ❌ Header structure mismatch:")
            print(f"      Main levels: {main_levels}")
            print(f"      Translation levels: {translation_levels}")
            all_valid = False
        else:
            print(f"   ✅ Header structure consistent")
        
        # Validate navigation table presence
        if not translation_navigation:
            print(f"   ❌ Navigation table not found")
            all_valid = False
        else:
            print(f"   ✅ Navigation table found")
            
            # Check if navigation tables have same number of language entries
            main_nav_lines = [line for line in main_navigation.split('\n') if line.strip().startswith('|') and 'Language' not in line and '---' not in line]
            trans_nav_lines = [line for line in translation_navigation.split('\n') if line.strip().startswith('|') and 'Language' not in line and '---' not in line]
            
            if len(main_nav_lines) != len(trans_nav_lines):
                print(f"   ❌ Navigation table entry count mismatch:")
                print(f"      Main: {len(main_nav_lines)}, Translation: {len(trans_nav_lines)}")
                all_valid = False
            else:
                print(f"   ✅ Navigation table entries consistent ({len(trans_nav_lines)})")
    
    print("\n" + "=" * 50)
    if all_valid:
        print("✅ All README files have consistent structure!")
        return True
    else:
        print("❌ Structure inconsistencies found. Please review and fix.")
        return False

def main():
    """Main function to run validation."""
    print("README Structure Validation Tool")
    print("Checking consistency across all language versions...\n")
    
    # Change to project root directory if script is run from templates directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.join(script_dir, '..', '..', '..')
    
    if os.path.exists(os.path.join(project_root, 'README.md')):
        os.chdir(project_root)
        print(f"📁 Working directory: {os.getcwd()}")
    else:
        print("❌ Could not find project root directory with README.md")
        sys.exit(1)
    
    # Run validation
    success = validate_structure()
    
    if success:
        print("\n🎉 Validation completed successfully!")
        sys.exit(0)
    else:
        print("\n💥 Validation failed. Please fix issues and run again.")
        sys.exit(1)

if __name__ == "__main__":
    main()