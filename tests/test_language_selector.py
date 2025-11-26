#!/usr/bin/env python3
"""
Unit tests for language selection and environment variable behavior
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock
from io import StringIO

# Add project paths
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "i18n"))
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from i18n.language_selector import get_language, LANGUAGE_CODES


class TestLanguageSelector(unittest.TestCase):
    """Test cases for language selection functionality"""

    def setUp(self):
        """Set up test fixtures"""
        # Store original environment
        self.original_env = os.environ.get("AWS_IOT_LANG")

    def tearDown(self):
        """Clean up after tests"""
        # Restore original environment
        if self.original_env is not None:
            os.environ["AWS_IOT_LANG"] = self.original_env
        elif "AWS_IOT_LANG" in os.environ:
            del os.environ["AWS_IOT_LANG"]

    def test_environment_variable_english(self):
        """Test language detection from environment variable - English variants"""
        test_cases = ["en", "english", "EN", "ENGLISH", "English"]
        
        for env_value in test_cases:
            with self.subTest(env_value=env_value):
                os.environ["AWS_IOT_LANG"] = env_value
                result = get_language()
                self.assertEqual(result, "en")

    def test_environment_variable_spanish(self):
        """Test language detection from environment variable - Spanish variants"""
        test_cases = ["es", "spanish", "español", "ES", "SPANISH", "ESPAÑOL"]
        
        for env_value in test_cases:
            with self.subTest(env_value=env_value):
                os.environ["AWS_IOT_LANG"] = env_value
                result = get_language()
                self.assertEqual(result, "es")

    def test_environment_variable_japanese(self):
        """Test language detection from environment variable - Japanese variants"""
        test_cases = ["ja", "japanese", "日本語", "jp", "JA", "JAPANESE"]
        
        for env_value in test_cases:
            with self.subTest(env_value=env_value):
                os.environ["AWS_IOT_LANG"] = env_value
                result = get_language()
                self.assertEqual(result, "ja")

    def test_environment_variable_chinese(self):
        """Test language detection from environment variable - Chinese variants"""
        test_cases = ["zh-cn", "chinese", "中文", "zh", "ZH-CN", "CHINESE"]
        
        for env_value in test_cases:
            with self.subTest(env_value=env_value):
                os.environ["AWS_IOT_LANG"] = env_value
                result = get_language()
                self.assertEqual(result, "zh-CN")

    def test_environment_variable_portuguese(self):
        """Test language detection from environment variable - Portuguese variants"""
        test_cases = ["pt", "pt-br", "portuguese", "português", "PT", "PT-BR", "PORTUGUESE"]
        
        for env_value in test_cases:
            with self.subTest(env_value=env_value):
                os.environ["AWS_IOT_LANG"] = env_value
                result = get_language()
                self.assertEqual(result, "pt-BR")

    def test_environment_variable_korean(self):
        """Test language detection from environment variable - Korean variants"""
        test_cases = ["ko", "korean", "한국어", "kr", "KO", "KOREAN"]
        
        for env_value in test_cases:
            with self.subTest(env_value=env_value):
                os.environ["AWS_IOT_LANG"] = env_value
                result = get_language()
                self.assertEqual(result, "ko")

    def test_environment_variable_invalid(self):
        """Test behavior with invalid environment variable values"""
        # Clear environment variable
        if "AWS_IOT_LANG" in os.environ:
            del os.environ["AWS_IOT_LANG"]
        
        # Mock user input for interactive selection
        with patch('builtins.input', return_value='1'):
            with patch('builtins.print'):
                result = get_language()
                self.assertEqual(result, "en")

    @patch('builtins.print')
    @patch('builtins.input')
    def test_interactive_selection_valid_choices(self, mock_input, mock_print):
        """Test interactive language selection with valid choices"""
        # Clear environment variable
        if "AWS_IOT_LANG" in os.environ:
            del os.environ["AWS_IOT_LANG"]
        
        test_cases = [
            ("1", "en"),
            ("2", "es"),
            ("3", "ja"),
            ("4", "zh-CN"),
            ("5", "pt-BR"),
            ("6", "ko")
        ]
        
        for user_input, expected_lang in test_cases:
            with self.subTest(user_input=user_input, expected_lang=expected_lang):
                mock_input.return_value = user_input
                result = get_language()
                self.assertEqual(result, expected_lang)

    @patch('builtins.print')
    @patch('builtins.input')
    def test_interactive_selection_invalid_then_valid(self, mock_input, mock_print):
        """Test interactive selection with invalid input followed by valid input"""
        # Clear environment variable
        if "AWS_IOT_LANG" in os.environ:
            del os.environ["AWS_IOT_LANG"]
        
        # Simulate invalid input followed by valid input
        mock_input.side_effect = ["invalid", "7", "0", "1"]
        result = get_language()
        self.assertEqual(result, "en")
        
        # Verify error message was printed
        error_calls = [call for call in mock_print.call_args_list 
                      if "Invalid selection" in str(call)]
        self.assertGreater(len(error_calls), 0)

    @patch('builtins.print')
    @patch('builtins.input')
    def test_interactive_selection_keyboard_interrupt(self, mock_input, mock_print):
        """Test handling of KeyboardInterrupt during interactive selection"""
        # Clear environment variable
        if "AWS_IOT_LANG" in os.environ:
            del os.environ["AWS_IOT_LANG"]
        
        mock_input.side_effect = KeyboardInterrupt()
        
        with self.assertRaises(SystemExit):
            get_language()

    def test_language_codes_completeness(self):
        """Test that all language codes are properly defined"""
        expected_codes = {"1", "2", "3", "4", "5", "6"}
        self.assertEqual(set(LANGUAGE_CODES.keys()), expected_codes)
        
        expected_languages = {"en", "es", "ja", "zh-CN", "pt-BR", "ko"}
        self.assertEqual(set(LANGUAGE_CODES.values()), expected_languages)

    @patch.dict(os.environ, {}, clear=True)
    @patch('builtins.print')
    @patch('builtins.input')
    def test_no_environment_variable_interactive_fallback(self, mock_input, mock_print):
        """Test that interactive selection is used when no environment variable is set"""
        mock_input.return_value = "2"
        result = get_language()
        self.assertEqual(result, "es")
        
        # Verify that the language selection header was printed
        header_calls = [call for call in mock_print.call_args_list 
                       if "Language Selection" in str(call)]
        self.assertGreater(len(header_calls), 0)

    def test_environment_variable_empty_string(self):
        """Test behavior when environment variable is set to empty string"""
        os.environ["AWS_IOT_LANG"] = ""
        
        with patch('builtins.input', return_value='1'):
            with patch('builtins.print'):
                result = get_language()
                self.assertEqual(result, "en")

    def test_environment_variable_whitespace(self):
        """Test behavior when environment variable contains only whitespace"""
        os.environ["AWS_IOT_LANG"] = "   "
        
        with patch('builtins.input', return_value='1'):
            with patch('builtins.print'):
                result = get_language()
                self.assertEqual(result, "en")


if __name__ == "__main__":
    unittest.main()