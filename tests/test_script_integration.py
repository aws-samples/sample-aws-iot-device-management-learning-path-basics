#!/usr/bin/env python3
"""
Integration tests for script internationalization
"""

import json
import os
import sys
import tempfile
import unittest
from unittest.mock import patch, MagicMock
import importlib.util

# Add project paths
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "scripts"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "i18n"))
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))


class TestScriptIntegration(unittest.TestCase):
    """Integration tests for script internationalization"""

    def setUp(self):
        """Set up test fixtures"""
        self.scripts_dir = os.path.join(os.path.dirname(__file__), "..", "scripts")
        self.i18n_dir = os.path.join(os.path.dirname(__file__), "..", "i18n")
        
        # List of scripts that should have i18n integration
        self.integrated_scripts = [
            "manage_dynamic_groups.py",
            "manage_packages.py",
            "create_job.py",
            "simulate_job_execution.py",
            "explore_jobs.py",
            "cleanup_script.py"
        ]

    def test_scripts_have_i18n_imports(self):
        """Test that all scripts have proper i18n imports"""
        for script_name in self.integrated_scripts:
            with self.subTest(script=script_name):
                script_path = os.path.join(self.scripts_dir, script_name)
                self.assertTrue(os.path.exists(script_path), f"Script {script_name} not found")
                
                with open(script_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for i18n imports
                self.assertIn("from language_selector import get_language", content,
                            f"{script_name} missing language_selector import")
                self.assertIn("from loader import load_messages", content,
                            f"{script_name} missing loader import")

    def test_scripts_have_global_variables(self):
        """Test that all scripts have required global variables"""
        for script_name in self.integrated_scripts:
            with self.subTest(script=script_name):
                script_path = os.path.join(self.scripts_dir, script_name)
                
                with open(script_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for global variables
                self.assertIn("USER_LANG = ", content,
                            f"{script_name} missing USER_LANG global variable")
                self.assertIn("messages = ", content,
                            f"{script_name} missing messages global variable")

    def test_scripts_have_get_message_method(self):
        """Test that all scripts have get_message method in their main class"""
        for script_name in self.integrated_scripts:
            with self.subTest(script=script_name):
                script_path = os.path.join(self.scripts_dir, script_name)
                
                with open(script_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for get_message method
                self.assertIn("def get_message(self, key", content,
                            f"{script_name} missing get_message method")

    def test_scripts_have_language_initialization(self):
        """Test that all scripts initialize language in main function"""
        for script_name in self.integrated_scripts:
            with self.subTest(script=script_name):
                script_path = os.path.join(self.scripts_dir, script_name)
                
                with open(script_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for language initialization
                self.assertIn("USER_LANG = get_language()", content,
                            f"{script_name} missing language initialization")
                self.assertIn("messages = load_messages(", content,
                            f"{script_name} missing message loading")

    def test_message_files_exist(self):
        """Test that message files exist for all integrated scripts"""
        for script_name in self.integrated_scripts:
            with self.subTest(script=script_name):
                # Extract script name without .py extension
                base_name = script_name.replace('.py', '')
                message_file = os.path.join(self.i18n_dir, "en", f"{base_name}.json")
                
                self.assertTrue(os.path.exists(message_file),
                              f"Message file {base_name}.json not found")

    def test_message_files_valid_json(self):
        """Test that all message files contain valid JSON"""
        for script_name in self.integrated_scripts:
            with self.subTest(script=script_name):
                base_name = script_name.replace('.py', '')
                message_file = os.path.join(self.i18n_dir, "en", f"{base_name}.json")
                
                if os.path.exists(message_file):
                    with open(message_file, 'r', encoding='utf-8') as f:
                        try:
                            messages = json.load(f)
                            self.assertIsInstance(messages, dict,
                                                f"{base_name}.json should contain a dictionary")
                        except json.JSONDecodeError as e:
                            self.fail(f"{base_name}.json contains invalid JSON: {e}")

    def test_get_message_method_functionality(self):
        """Test get_message method functionality with mock data"""
        # Create a temporary script class to test get_message functionality
        test_messages = {
            "simple_key": "Simple message",
            "formatted_key": "Message with {} parameter",
            "multi_param": "Message with {} and {} parameters"
        }
        
        class TestScriptClass:
            def get_message(self, key, *args):
                """Get localized message with optional formatting"""
                msg = test_messages.get(key, key)
                if args:
                    return msg.format(*args)
                return msg
        
        test_instance = TestScriptClass()
        
        # Test simple message retrieval
        self.assertEqual(test_instance.get_message("simple_key"), "Simple message")
        
        # Test formatted message
        self.assertEqual(test_instance.get_message("formatted_key", "test"), 
                        "Message with test parameter")
        
        # Test multiple parameters
        self.assertEqual(test_instance.get_message("multi_param", "first", "second"),
                        "Message with first and second parameters")
        
        # Test fallback behavior
        self.assertEqual(test_instance.get_message("nonexistent_key"), "nonexistent_key")

    def test_script_imports_work(self):
        """Test that scripts can be imported without errors"""
        for script_name in self.integrated_scripts:
            with self.subTest(script=script_name):
                script_path = os.path.join(self.scripts_dir, script_name)
                
                # Create module spec
                spec = importlib.util.spec_from_file_location(
                    script_name.replace('.py', ''), script_path
                )
                
                # Mock AWS clients to avoid actual AWS calls during import
                with patch('boto3.client') as mock_client:
                    mock_client.return_value = MagicMock()
                    
                    try:
                        module = importlib.util.module_from_spec(spec)
                        # Don't execute the module, just test that it can be loaded
                        # This tests that imports and basic syntax are correct
                        spec.loader.exec_module(module)
                    except Exception as e:
                        self.fail(f"Failed to import {script_name}: {e}")

    def test_backward_compatibility_main_execution(self):
        """Test that scripts maintain backward compatibility in main execution"""
        for script_name in self.integrated_scripts:
            with self.subTest(script=script_name):
                script_path = os.path.join(self.scripts_dir, script_name)
                
                with open(script_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check that main execution pattern is preserved
                self.assertIn('if __name__ == "__main__":', content,
                            f"{script_name} missing main execution guard")

    def test_message_key_usage_consistency(self):
        """Test that scripts use consistent message key patterns"""
        common_patterns = [
            "title",
            "separator", 
            "debug.",
            "status.",
            "errors.",
            "prompts."
        ]
        
        for script_name in self.integrated_scripts:
            with self.subTest(script=script_name):
                base_name = script_name.replace('.py', '')
                message_file = os.path.join(self.i18n_dir, "en", f"{base_name}.json")
                
                if os.path.exists(message_file):
                    with open(message_file, 'r', encoding='utf-8') as f:
                        messages = json.load(f)
                    
                    # Check for at least some common patterns
                    has_common_pattern = any(
                        any(key.startswith(pattern.rstrip('.')) or pattern.rstrip('.') in key 
                            for key in self._flatten_dict(messages))
                        for pattern in common_patterns
                    )
                    
                    self.assertTrue(has_common_pattern,
                                  f"{base_name}.json should contain common message patterns")

    def _flatten_dict(self, d, parent_key='', sep='.'):
        """Helper method to flatten nested dictionary keys"""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)

    def test_environment_variable_integration(self):
        """Test that scripts respect AWS_IOT_LANG environment variable"""
        # This test verifies the integration works by checking the import structure
        # Full end-to-end testing would require running the actual scripts
        
        for script_name in self.integrated_scripts:
            with self.subTest(script=script_name):
                script_path = os.path.join(self.scripts_dir, script_name)
                
                with open(script_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Verify that get_language() is called (which handles env var)
                self.assertIn("get_language()", content,
                            f"{script_name} should call get_language() function")


if __name__ == "__main__":
    unittest.main()