#!/usr/bin/env python3
"""
Quick formatting fix script for the project
"""

import subprocess
import sys


def run_command(cmd_list, description):
    """Run a command and print results"""
    print(f"Running {description}...")
    try:
        result = subprocess.run(cmd_list, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
        else:
            print(f"❌ {description} failed:")
            print(result.stdout)
            print(result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running {description}: {e}")
        return False


def main():
    """Fix common formatting issues"""
    print("🔧 Fixing code formatting issues...\n")

    # Install required tools
    print("Installing formatting tools...")
    subprocess.run([sys.executable, "-m", "pip", "install", "black", "isort"], capture_output=True)  # nosec B603

    # Fix formatting with black
    run_command(["black", "--line-length=127", "."], "Black formatting")

    # Fix import sorting
    run_command(["isort", "--profile=black", "--line-length=127", "."], "Import sorting")

    print("\n✅ Formatting fixes completed!")
    print("💡 Commit these changes and push to fix the CI checks")


if __name__ == "__main__":
    main()
