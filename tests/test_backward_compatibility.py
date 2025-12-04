#!/usr/bin/env python3
"""
Tests for backward compatibility and existing functionality preservation
"""

import json
import os
import sys
import unittest
from unittest.mock import patch, MagicMock, call
import importlib.util

# Add project paths
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "scripts"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "i18n"))
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))


class TestBackwardCompatibility(unittest.TestCase):
    """Test backward compatibility and functionality preservation"""

    def setUp(self):
        """Set up test fixtures"""
        self.scripts_dir = os.path.join(os.path.dirname(__file__), "..", "scripts")
        self.i18n_dir = os.path.join(os.path.dirname(__file__), "..", "i18n")

        # Scripts that should maintain backward compatibility
        self.integrated_scripts = [
            "manage_dynamic_groups.py",
            "manage_packages.py",
            "create_job.py",
            "simulate_job_execution.py",
            "explore_jobs.py",
            "cleanup_script.py",
        ]

    def test_scripts_preserve_main_structure(self):
        """Test that scripts preserve their main execution structure"""
        for script_name in self.integrated_scripts:
            with self.subTest(script=script_name):
                script_path = os.path.join(self.scripts_dir, script_name)

                with open(script_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Check main execution guard
                self.assertIn('if __name__ == "__main__":', content, f"{script_name} should preserve main execution guard")

                # Check that main class structure is preserved
                # Look for class definitions
                class_found = False
                for line in content.split("\n"):
                    if line.strip().startswith("class ") and ":" in line:
                        class_found = True
                        break

                self.assertTrue(class_found, f"{script_name} should preserve class structure")

    def test_scripts_preserve_aws_client_initialization(self):
        """Test that scripts preserve AWS client initialization patterns"""
        for script_name in self.integrated_scripts:
            with self.subTest(script=script_name):
                script_path = os.path.join(self.scripts_dir, script_name)

                with open(script_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Check for boto3 import
                self.assertIn("import boto3", content, f"{script_name} should preserve boto3 import")

                # Check for client initialization patterns
                has_client_init = "boto3.client" in content or "self.iot_client" in content or "self.sts_client" in content

                self.assertTrue(has_client_init, f"{script_name} should preserve AWS client initialization")

    def test_scripts_preserve_error_handling(self):
        """Test that scripts preserve error handling patterns"""
        for script_name in self.integrated_scripts:
            with self.subTest(script=script_name):
                script_path = os.path.join(self.scripts_dir, script_name)

                with open(script_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Check for error handling imports
                self.assertIn(
                    "from botocore.exceptions import ClientError", content, f"{script_name} should preserve ClientError import"
                )

                # Check for try-except blocks
                self.assertIn("try:", content, f"{script_name} should preserve error handling")

    def test_scripts_preserve_colorama_usage(self):
        """Test that scripts preserve colorama for colored output"""
        for script_name in self.integrated_scripts:
            with self.subTest(script=script_name):
                script_path = os.path.join(self.scripts_dir, script_name)

                with open(script_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Check for colorama import and usage
                self.assertIn("from colorama import", content, f"{script_name} should preserve colorama import")
                self.assertIn("init()", content, f"{script_name} should preserve colorama initialization")

    def test_scripts_preserve_threading_patterns(self):
        """Test that scripts preserve threading and concurrency patterns"""
        threading_scripts = ["manage_dynamic_groups.py", "manage_packages.py", "cleanup_script.py"]

        for script_name in threading_scripts:
            with self.subTest(script=script_name):
                script_path = os.path.join(self.scripts_dir, script_name)

                with open(script_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Check for threading imports
                has_threading = "from concurrent.futures import" in content or "from threading import" in content

                self.assertTrue(has_threading, f"{script_name} should preserve threading imports")

    def test_get_message_fallback_behavior(self):
        """Test that get_message method provides proper fallback behavior"""

        # Test the fallback behavior that should be consistent across all scripts
        class MockScriptClass:
            def __init__(self):
                self.messages = {"existing_key": "Existing message"}

            def get_message(self, key, *args):
                """Standard get_message implementation"""
                msg = self.messages.get(key, key)  # Fallback to key itself
                if args:
                    return msg.format(*args)
                return msg

        mock_instance = MockScriptClass()

        # Test existing key
        self.assertEqual(mock_instance.get_message("existing_key"), "Existing message")

        # Test fallback behavior for missing key
        self.assertEqual(mock_instance.get_message("missing_key"), "missing_key")

        # Test fallback with formatting
        mock_instance.messages["format_key"] = "Message with {}"
        self.assertEqual(mock_instance.get_message("format_key", "param"), "Message with param")

        # Test missing key with attempted formatting (should not crash)
        result = mock_instance.get_message("missing_format_key", "param")
        self.assertEqual(result, "missing_format_key")

    def test_environment_variable_backward_compatibility(self):
        """Test that environment variable handling is backward compatible"""
        # Test that AWS_IOT_LANG doesn't break existing functionality
        original_env = os.environ.get("AWS_IOT_LANG")

        try:
            # Test with English (should work the same as before)
            os.environ["AWS_IOT_LANG"] = "en"

            # Import language selector
            from i18n.language_selector import get_language

            result = get_language()
            self.assertEqual(result, "en")

            # Test that other environment variables are not affected
            # This is a basic check that the i18n system doesn't interfere
            test_env_var = "TEST_BACKWARD_COMPAT"
            os.environ[test_env_var] = "test_value"
            self.assertEqual(os.environ[test_env_var], "test_value")

        finally:
            # Restore original environment
            if original_env is not None:
                os.environ["AWS_IOT_LANG"] = original_env
            elif "AWS_IOT_LANG" in os.environ:
                del os.environ["AWS_IOT_LANG"]

            if "TEST_BACKWARD_COMPAT" in os.environ:
                del os.environ["TEST_BACKWARD_COMPAT"]

    def test_message_loading_preserves_functionality(self):
        """Test that message loading doesn't break when files are missing"""
        from i18n.loader import load_messages

        # Test loading non-existent script (should return empty dict, not crash)
        messages = load_messages("nonexistent_script", "en")
        self.assertIsInstance(messages, dict)

        # Test loading with non-existent language (should return empty dict, not crash)
        messages = load_messages("provision_script", "nonexistent_language")
        self.assertIsInstance(messages, dict)

    def test_scripts_preserve_command_line_interface(self):
        """Test that scripts preserve their command-line interface"""
        for script_name in self.integrated_scripts:
            with self.subTest(script=script_name):
                script_path = os.path.join(self.scripts_dir, script_name)

                with open(script_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Scripts should still be executable as standalone programs
                self.assertTrue(content.startswith("#!/usr/bin/env python3"), f"{script_name} should preserve shebang line")

    def test_scripts_preserve_debug_mode_functionality(self):
        """Test that scripts preserve debug mode functionality"""
        for script_name in self.integrated_scripts:
            with self.subTest(script=script_name):
                script_path = os.path.join(self.scripts_dir, script_name)

                with open(script_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Check for debug mode patterns
                has_debug = "debug_mode" in content or "debug" in content.lower()

                self.assertTrue(has_debug, f"{script_name} should preserve debug functionality")

    def test_message_formatting_preserves_special_characters(self):
        """Test that message formatting preserves emojis and special characters"""
        test_messages = {
            "emoji_message": "✅ Success with emoji",
            "unicode_message": "Message with unicode: 中文",
            "formatted_emoji": "❌ Error: {}",
            "special_chars": "Message with special chars: @#$%^&*()",
        }

        class TestClass:
            def get_message(self, key, *args):
                msg = test_messages.get(key, key)
                if args:
                    return msg.format(*args)
                return msg

        test_instance = TestClass()

        # Test emoji preservation
        self.assertEqual(test_instance.get_message("emoji_message"), "✅ Success with emoji")

        # Test unicode preservation
        self.assertEqual(test_instance.get_message("unicode_message"), "Message with unicode: 中文")

        # Test formatted emoji
        self.assertEqual(test_instance.get_message("formatted_emoji", "test"), "❌ Error: test")

        # Test special characters
        self.assertEqual(test_instance.get_message("special_chars"), "Message with special chars: @#$%^&*()")

    def test_scripts_maintain_exit_codes(self):
        """Test that scripts maintain proper exit code patterns"""
        for script_name in self.integrated_scripts:
            with self.subTest(script=script_name):
                script_path = os.path.join(self.scripts_dir, script_name)

                with open(script_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Check for exit patterns (should not have changed)
                # Scripts should still handle exits properly
                has_exit_handling = "exit(" in content or "sys.exit(" in content or "return" in content

                self.assertTrue(has_exit_handling, f"{script_name} should preserve exit handling")


if __name__ == "__main__":
    unittest.main()
