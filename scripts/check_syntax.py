#!/usr/bin/env python3

"""
Pre-publication syntax checker for AWS IoT Device Management project.
Validates all Python scripts for syntax errors and import issues.
"""

import os
import py_compile
import sys
from pathlib import Path


def check_syntax():
    """Check syntax of all Python files"""
    print("🔍 Checking Python syntax...")

    # Check if we're in scripts/ directory, if so look in current dir, otherwise look in scripts/
    if Path.cwd().name == "scripts":
        python_files = list(Path(".").glob("*.py"))
    else:
        python_files = list(Path("scripts").glob("*.py"))

    errors = []

    for file_path in python_files:
        if file_path.name == "check_syntax.py":  # Skip self
            continue

        try:
            py_compile.compile(str(file_path), doraise=True)
            print(f"✅ {file_path.name}")
        except py_compile.PyCompileError as e:
            print(f"❌ {file_path.name}: {e}")
            errors.append(str(file_path))

    return errors


def check_imports():
    """Check if main imports work"""
    print("\n🔍 Checking imports...")

    imports_to_test = [
        ("subprocess", "Subprocess (stdlib)"),
        ("json", "JSON (stdlib)"),
        ("os", "OS (stdlib)"),
        ("sys", "Sys (stdlib)"),
        ("time", "Time (stdlib)"),
        ("concurrent.futures", "Concurrent futures (stdlib)"),
        ("threading", "Threading (stdlib)"),
        ("colorama", "Colorama (terminal colors)"),
        ("zipfile", "Zipfile (stdlib)"),
        ("tempfile", "Tempfile (stdlib)"),
        ("uuid", "UUID (stdlib)"),
        ("datetime", "Datetime (stdlib)"),
    ]

    errors = []
    for module, description in imports_to_test:
        try:
            __import__(module)
            print(f"✅ {module} ({description})")
        except ImportError as e:
            print(f"❌ {module} ({description}): {e}")
            errors.append(module)

    return errors


def check_requirements():
    """Check requirements.txt exists and is readable"""
    print("\n🔍 Checking requirements.txt...")

    # Look for requirements.txt in parent directory if we're in scripts/
    req_file = "../requirements.txt" if Path.cwd().name == "scripts" else "requirements.txt"

    if not os.path.exists(req_file):
        print("❌ requirements.txt not found")
        return False

    try:
        with open(req_file, "r", encoding="utf-8") as f:
            requirements = f.read().strip().split("\n")
            print(f"✅ requirements.txt ({len(requirements)} dependencies)")
            for req in requirements:
                if req.strip():
                    print(f"   • {req.strip()}")
        return True
    except Exception as e:
        print(f"❌ Error reading requirements.txt: {e}")
        return False


def main():
    """Run all pre-publication checks"""
    print("🚀 AWS IoT Device Management - Pre-publication Check")
    print("=" * 50)

    # Check syntax
    syntax_errors = check_syntax()

    # Check imports
    import_errors = check_imports()

    # Check requirements
    requirements_ok = check_requirements()

    # Summary
    print("\n" + "=" * 50)
    print("📊 SUMMARY")

    total_errors = len(syntax_errors) + len(import_errors) + (0 if requirements_ok else 1)

    if total_errors == 0:
        print("✅ ALL CHECKS PASSED - Ready for publication!")
        sys.exit(0)
    else:
        print(f"❌ {total_errors} issue(s) found:")

        if syntax_errors:
            print(f"   • Syntax errors in: {', '.join(syntax_errors)}")

        if import_errors:
            print(f"   • Import errors: {', '.join(import_errors)}")

        if not requirements_ok:
            print("   • Requirements file issue")

        print("\n💡 Fix these issues before publication")
        sys.exit(1)


if __name__ == "__main__":
    main()
