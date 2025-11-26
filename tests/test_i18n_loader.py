#!/usr/bin/env python3
"""
Unit tests for i18n message loading and fallback behavior
"""

import json
import os
import sys
import tempfile
import unittest
from unittest.mock import patch, mock_open

# Add project paths
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "i18n"))
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from i18n.loader import load_messages


class TestI18nLoader(unittest.TestCase):
    """Test cases for message loading functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_common_messages = {
            "account_id": "Account ID",
            "region": "Region",
            "press_enter": "Press Enter to continue...",
            "goodbye": "Goodbye!"
        }
        
        self.test_script_messages = {
            "title": "Test Script",
            "separator": "================",
            "prompts": {
                "user_input": "Enter value: ",
                "confirmation": "Continue? [y/N]: "
            },
            "status": {
                "processing": "Processing...",
                "success": "✅ Success",
                "failed": "❌ Failed"
            }
        }

    def test_load_messages_with_existing_files(self):
        """Test loading messages when both common and script files exist"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create common.json
            common_file = os.path.join(temp_dir, "common.json")
            with open(common_file, "w", encoding="utf-8") as f:
                json.dump(self.test_common_messages, f)
            
            # Create script-specific file
            lang_dir = os.path.join(temp_dir, "en")
            os.makedirs(lang_dir)
            script_file = os.path.join(lang_dir, "test_script.json")
            with open(script_file, "w", encoding="utf-8") as f:
                json.dump(self.test_script_messages, f)
            
            # Mock the base path
            with patch('i18n.loader.os.path.dirname', return_value=temp_dir):
                messages = load_messages("test_script", "en")
                
                # Should contain both common and script messages
                self.assertIn("account_id", messages)
                self.assertIn("title", messages)
                self.assertEqual(messages["account_id"], "Account ID")
                self.assertEqual(messages["title"], "Test Script")

    def test_load_messages_script_overrides_common(self):
        """Test that script-specific messages override common messages"""
        common_messages = {"shared_key": "Common Value", "unique_common": "Common Only"}
        script_messages = {"shared_key": "Script Value", "unique_script": "Script Only"}
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create common.json
            common_file = os.path.join(temp_dir, "common.json")
            with open(common_file, "w", encoding="utf-8") as f:
                json.dump(common_messages, f)
            
            # Create script-specific file
            lang_dir = os.path.join(temp_dir, "en")
            os.makedirs(lang_dir)
            script_file = os.path.join(lang_dir, "test_script.json")
            with open(script_file, "w", encoding="utf-8") as f:
                json.dump(script_messages, f)
            
            with patch('i18n.loader.os.path.dirname', return_value=temp_dir):
                messages = load_messages("test_script", "en")
                
                # Script message should override common
                self.assertEqual(messages["shared_key"], "Script Value")
                self.assertEqual(messages["unique_common"], "Common Only")
                self.assertEqual(messages["unique_script"], "Script Only")

    def test_load_messages_missing_common_file(self):
        """Test loading messages when common.json doesn't exist"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create only script-specific file
            lang_dir = os.path.join(temp_dir, "en")
            os.makedirs(lang_dir)
            script_file = os.path.join(lang_dir, "test_script.json")
            with open(script_file, "w", encoding="utf-8") as f:
                json.dump(self.test_script_messages, f)
            
            with patch('i18n.loader.os.path.dirname', return_value=temp_dir):
                messages = load_messages("test_script", "en")
                
                # Should only contain script messages
                self.assertNotIn("account_id", messages)
                self.assertIn("title", messages)
                self.assertEqual(messages["title"], "Test Script")

    def test_load_messages_missing_script_file(self):
        """Test loading messages when script-specific file doesn't exist"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create only common.json
            common_file = os.path.join(temp_dir, "common.json")
            with open(common_file, "w", encoding="utf-8") as f:
                json.dump(self.test_common_messages, f)
            
            with patch('i18n.loader.os.path.dirname', return_value=temp_dir):
                messages = load_messages("nonexistent_script", "en")
                
                # Should only contain common messages
                self.assertIn("account_id", messages)
                self.assertNotIn("title", messages)
                self.assertEqual(messages["account_id"], "Account ID")

    def test_load_messages_missing_both_files(self):
        """Test loading messages when both files are missing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('i18n.loader.os.path.dirname', return_value=temp_dir):
                messages = load_messages("nonexistent_script", "en")
                
                # Should return empty dictionary
                self.assertEqual(messages, {})

    def test_load_messages_malformed_json(self):
        """Test handling of malformed JSON files"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create malformed common.json
            common_file = os.path.join(temp_dir, "common.json")
            with open(common_file, "w", encoding="utf-8") as f:
                f.write("{ invalid json }")
            
            # Create valid script file
            lang_dir = os.path.join(temp_dir, "en")
            os.makedirs(lang_dir)
            script_file = os.path.join(lang_dir, "test_script.json")
            with open(script_file, "w", encoding="utf-8") as f:
                json.dump(self.test_script_messages, f)
            
            with patch('i18n.loader.os.path.dirname', return_value=temp_dir):
                # Should raise JSONDecodeError
                with self.assertRaises(json.JSONDecodeError):
                    load_messages("test_script", "en")

    def test_load_messages_different_languages(self):
        """Test loading messages for different languages"""
        # Define test messages for multiple languages
        language_messages = {
            "en": {"title": "Test Script", "goodbye": "Goodbye!"},
            "es": {"title": "Script de Prueba", "goodbye": "¡Adiós!"},
            "ja": {"title": "テストスクリプト", "goodbye": "さようなら！"},
            "zh-CN": {"title": "测试脚本", "goodbye": "再见！"},
            "pt-BR": {"title": "Script de Teste", "goodbye": "Tchau!"},
            "ko": {"title": "테스트 스크립트", "goodbye": "안녕히 가세요!"}
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create message files for all supported languages
            for lang_code, messages in language_messages.items():
                lang_dir = os.path.join(temp_dir, lang_code)
                os.makedirs(lang_dir)
                lang_file = os.path.join(lang_dir, "test_script.json")
                with open(lang_file, "w", encoding="utf-8") as f:
                    json.dump(messages, f)
            
            with patch('i18n.loader.os.path.dirname', return_value=temp_dir):
                # Test each language
                for lang_code, expected_messages in language_messages.items():
                    with self.subTest(language=lang_code):
                        loaded_messages = load_messages("test_script", lang_code)
                        self.assertEqual(loaded_messages["title"], expected_messages["title"])
                        self.assertEqual(loaded_messages["goodbye"], expected_messages["goodbye"])

    def test_load_messages_nested_structure(self):
        """Test loading messages with nested dictionary structure"""
        nested_messages = {
            "prompts": {
                "user_input": "Enter value: ",
                "nested": {
                    "deep": "Deep nested value"
                }
            }
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            lang_dir = os.path.join(temp_dir, "en")
            os.makedirs(lang_dir)
            script_file = os.path.join(lang_dir, "test_script.json")
            with open(script_file, "w", encoding="utf-8") as f:
                json.dump(nested_messages, f)
            
            with patch('i18n.loader.os.path.dirname', return_value=temp_dir):
                messages = load_messages("test_script", "en")
                
                self.assertIn("prompts", messages)
                self.assertIsInstance(messages["prompts"], dict)
                self.assertEqual(messages["prompts"]["user_input"], "Enter value: ")
                self.assertEqual(messages["prompts"]["nested"]["deep"], "Deep nested value")

    def test_language_fallback_behavior(self):
        """Test fallback behavior when requested language doesn't exist"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create only English messages
            en_dir = os.path.join(temp_dir, "en")
            os.makedirs(en_dir)
            en_file = os.path.join(en_dir, "test_script.json")
            with open(en_file, "w", encoding="utf-8") as f:
                json.dump(self.test_script_messages, f)
            
            # Create common messages
            common_file = os.path.join(temp_dir, "common.json")
            with open(common_file, "w", encoding="utf-8") as f:
                json.dump(self.test_common_messages, f)
            
            with patch('i18n.loader.os.path.dirname', return_value=temp_dir):
                # Request non-existent language - should only get common messages
                messages = load_messages("test_script", "fr")  # French doesn't exist
                
                # Should contain common messages but not script-specific ones
                self.assertIn("account_id", messages)  # From common
                self.assertNotIn("title", messages)    # Script-specific not available

    def test_unicode_and_special_characters(self):
        """Test handling of unicode characters and special symbols in all languages"""
        unicode_messages = {
            "en": {
                "emoji": "✅ Success! 🎉",
                "symbols": "Progress: ▓▓▓░░ 60%",
                "currency": "Cost: $12.34"
            },
            "es": {
                "emoji": "✅ ¡Éxito! 🎉", 
                "symbols": "Progreso: ▓▓▓░░ 60%",
                "currency": "Costo: €12,34"
            },
            "ja": {
                "emoji": "✅ 成功！🎉",
                "symbols": "進捗: ▓▓▓░░ 60%", 
                "currency": "費用: ¥1234"
            },
            "zh-CN": {
                "emoji": "✅ 成功！🎉",
                "symbols": "进度: ▓▓▓░░ 60%",
                "currency": "费用: ¥12.34"
            }
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            for lang_code, messages in unicode_messages.items():
                lang_dir = os.path.join(temp_dir, lang_code)
                os.makedirs(lang_dir)
                lang_file = os.path.join(lang_dir, "test_script.json")
                with open(lang_file, "w", encoding="utf-8") as f:
                    json.dump(messages, f)
            
            with patch('i18n.loader.os.path.dirname', return_value=temp_dir):
                for lang_code, expected_messages in unicode_messages.items():
                    with self.subTest(language=lang_code):
                        loaded_messages = load_messages("test_script", lang_code)
                        
                        # Verify all unicode characters are preserved
                        self.assertEqual(loaded_messages["emoji"], expected_messages["emoji"])
                        self.assertEqual(loaded_messages["symbols"], expected_messages["symbols"])
                        self.assertEqual(loaded_messages["currency"], expected_messages["currency"])


if __name__ == "__main__":
    unittest.main()