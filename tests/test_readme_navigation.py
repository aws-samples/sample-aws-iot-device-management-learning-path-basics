#!/usr/bin/env python3
"""
Cross-validation script for README navigation consistency.
Validates that all language navigation tables are identical in structure
and that all language links point to correct files.
"""

import os
import re
import sys
from pathlib import Path


def extract_navigation_table(content):
    """Extract the navigation table from README content."""
    # Look for the multilingual header and table
    pattern = r"## 🌍 Available Languages.*?\n\n(.*?)\n\n---"
    match = re.search(pattern, content, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None


def parse_navigation_table(table_content):
    """Parse navigation table and extract language entries."""
    if not table_content:
        return []

    lines = table_content.split("\n")
    entries = []

    for line in lines:
        if line.startswith("|") and not line.startswith("| Language"):
            # Parse table row: | 🇺🇸 English | [README.md](README.md) |
            parts = [part.strip() for part in line.split("|")[1:-1]]  # Remove empty first/last
            if len(parts) == 2:
                language_cell = parts[0]
                link_cell = parts[1]

                # Extract flag, language name, and link
                flag_match = re.search(r"(🇺🇸|🇪🇸|🇯🇵|🇰🇷|🇧🇷|🇨🇳)", language_cell)
                flag = flag_match.group(1) if flag_match else ""

                language_name = language_cell.replace(flag, "").strip()

                # Extract link from markdown format [text](url)
                link_match = re.search(r"\[([^\]]+)\]\(([^)]+)\)", link_cell)
                if link_match:
                    link_text = link_match.group(1)
                    link_url = link_match.group(2)

                    entries.append({"flag": flag, "language": language_name, "link_text": link_text, "link_url": link_url})

    return entries


def validate_navigation_consistency():
    """Validate navigation consistency across all README files."""
    readme_files = ["README.md", "README.es.md", "README.ja.md", "README.ko.md", "README.pt.md", "README.zh.md"]

    print("🔍 Validating README navigation consistency...")
    print("=" * 60)

    navigation_tables = {}
    errors = []

    # Extract navigation tables from all files
    for readme_file in readme_files:
        if not os.path.exists(readme_file):
            errors.append(f"❌ Missing file: {readme_file}")
            continue

        with open(readme_file, "r", encoding="utf-8") as f:
            content = f.read()

        table_content = extract_navigation_table(content)
        if not table_content:
            errors.append(f"❌ No navigation table found in {readme_file}")
            continue

        navigation_tables[readme_file] = {"content": table_content, "entries": parse_navigation_table(table_content)}

    # Validate structure consistency
    if navigation_tables:
        reference_file = list(navigation_tables.keys())[0]
        reference_entries = navigation_tables[reference_file]["entries"]

        print(f"📋 Using {reference_file} as reference structure")
        print(f"   Found {len(reference_entries)} navigation entries")

        for filename, data in navigation_tables.items():
            if filename == reference_file:
                continue

            entries = data["entries"]

            # Check number of entries
            if len(entries) != len(reference_entries):
                errors.append(f"❌ {filename}: Entry count mismatch ({len(entries)} vs {len(reference_entries)})")
                continue

            # Check each entry
            for i, (ref_entry, entry) in enumerate(zip(reference_entries, entries)):
                # Check flag consistency
                if entry["flag"] != ref_entry["flag"]:
                    errors.append(f"❌ {filename}: Flag mismatch at position {i+1} ({entry['flag']} vs {ref_entry['flag']})")

                # Check link URL consistency
                if entry["link_url"] != ref_entry["link_url"]:
                    errors.append(
                        f"❌ {filename}: Link URL mismatch at position {i+1} ({entry['link_url']} vs {ref_entry['link_url']})"
                    )

                # Check link text consistency
                if entry["link_text"] != ref_entry["link_text"]:
                    errors.append(
                        f"❌ {filename}: Link text mismatch at position {i+1} ({entry['link_text']} vs {ref_entry['link_text']})"
                    )

    # Validate file naming conventions
    expected_files = {
        "README.md": "🇺🇸 English",
        "README.es.md": "🇪🇸 Español",
        "README.ja.md": "🇯🇵 日本語",
        "README.ko.md": "🇰🇷 한국어",
        "README.pt.md": "🇧🇷 Português",
        "README.zh.md": "🇨🇳 中文",
    }

    print("\n📁 Validating file naming conventions...")
    for expected_file, language_desc in expected_files.items():
        if not os.path.exists(expected_file):
            errors.append(f"❌ Missing expected file: {expected_file} for {language_desc}")
        else:
            print(f"✅ {expected_file} exists")

    # Validate that all linked files exist
    print("\n🔗 Validating navigation links...")
    if navigation_tables:
        for filename, data in navigation_tables.items():
            for entry in data["entries"]:
                link_file = entry["link_url"]
                if not os.path.exists(link_file):
                    errors.append(f"❌ {filename}: Broken link to {link_file}")
                else:
                    print(f"✅ {filename}: Link to {link_file} is valid")

    # Report results
    print("\n" + "=" * 60)
    if errors:
        print(f"❌ Validation failed with {len(errors)} errors:")
        for error in errors:
            print(f"   {error}")
        return False
    else:
        print("✅ All navigation tables are consistent!")
        print("✅ All file naming conventions are correct!")
        print("✅ All navigation links are valid!")
        return True


if __name__ == "__main__":
    success = validate_navigation_consistency()
    sys.exit(0 if success else 1)
