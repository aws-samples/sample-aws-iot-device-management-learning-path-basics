#!/usr/bin/env python3
"""
Comprehensive multilingual README validation script.
Combines navigation consistency and content validation checks.
"""

import os
import sys
import subprocess
from pathlib import Path


def run_validation_script(script_name, description):
    """Run a validation script and return success status."""
    print(f"\n🔍 {description}")
    print("=" * 60)

    try:
        result = subprocess.run([sys.executable, script_name], capture_output=True, text=True, cwd=".")

        # Print the output
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)

        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running {script_name}: {e}")
        return False


def main():
    """Run comprehensive multilingual README validation."""
    print("🌍 Multilingual README Validation Suite")
    print("=" * 60)
    print("Validating cross-language consistency and content preservation")

    # Check if we're in the right directory
    if not os.path.exists("README.md"):
        print("❌ Error: README.md not found. Please run from project root.")
        return False

    validation_scripts = [
        ("tests/test_readme_navigation.py", "Navigation Consistency Validation"),
        ("tests/test_readme_essentials.py", "Essential Requirements Validation"),
    ]

    all_passed = True

    for script_path, description in validation_scripts:
        if not os.path.exists(script_path):
            print(f"❌ Validation script not found: {script_path}")
            all_passed = False
            continue

        success = run_validation_script(script_path, description)
        if not success:
            all_passed = False

    # Final summary
    print("\n" + "=" * 60)
    print("🏁 VALIDATION SUMMARY")
    print("=" * 60)

    if all_passed:
        print("✅ ALL VALIDATIONS PASSED!")
        print("✅ Navigation tables are consistent across all language versions")
        print("✅ Content structure is maintained across all translations")
        print("✅ Code blocks are identical in all README files")
        print("✅ AWS service names and technical terms are preserved")
        print("✅ File naming conventions follow the established pattern")
        print("\n🎉 Multilingual README implementation is complete and validated!")
    else:
        print("❌ VALIDATION FAILED!")
        print("❌ Some consistency checks did not pass")
        print("❌ Please review the errors above and fix the issues")
        print("\n🔧 Run individual test scripts to debug specific issues:")
        print("   python tests/test_readme_navigation.py")
        print("   python tests/test_readme_essentials.py")

    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
