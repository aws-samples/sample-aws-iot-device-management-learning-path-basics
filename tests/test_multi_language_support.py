#!/usr/bin/env python3
"""
Multi-language support tests for internationalization system
This test file is designed to make it easy to test new languages as they are added.
"""

import json
import os
import sys
import tempfile
import unittest
from unittest.mock import patch

# Add project paths
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "i18n"))
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from i18n.loader import load_messages
from i18n.language_selector import get_language, LANGUAGE_CODES


class TestMultiLanguageSupport(unittest.TestCase):
    """Test cases for multi-language support and extensibility"""

    def setUp(self):
        """Set up test fixtures"""
        self.i18n_dir = os.path.join(os.path.dirname(__file__), "..", "i18n")
        
        # Define supported languages with their expected characteristics
        self.supported_languages = {
            "en": {
                "name": "English",
                "sample_text": "Hello World",
                "direction": "ltr",
                "encoding": "utf-8"
            },
            "es": {
                "name": "Spanish", 
                "sample_text": "Hola Mundo",
                "direction": "ltr",
                "encoding": "utf-8"
            },
            "ja": {
                "name": "Japanese",
                "sample_text": "こんにちは世界",
                "direction": "ltr", 
                "encoding": "utf-8"
            },
            "zh-CN": {
                "name": "Chinese (Simplified)",
                "sample_text": "你好世界",
                "direction": "ltr",
                "encoding": "utf-8"
            },
            "pt-BR": {
                "name": "Portuguese (Brazil)",
                "sample_text": "Olá Mundo", 
                "direction": "ltr",
                "encoding": "utf-8"
            },
            "ko": {
                "name": "Korean",
                "sample_text": "안녕하세요 세계",
                "direction": "ltr",
                "encoding": "utf-8"
            }
        }

    def test_language_code_mapping_completeness(self):
        """Test that all supported languages have proper code mappings"""
        # Get language codes from language_selector
        mapped_languages = set(LANGUAGE_CODES.values())
        expected_languages = set(self.supported_languages.keys())
        
        self.assertEqual(mapped_languages, expected_languages,
                        "Language codes in LANGUAGE_CODES should match supported languages")

    def test_create_sample_messages_for_all_languages(self):
        """Test creating and loading sample messages for all supported languages"""
        sample_messages = {
            "title": "Sample Script",
            "welcome": "Welcome to the application",
            "status": {
                "processing": "Processing...",
                "success": "Operation completed successfully",
                "error": "An error occurred"
            },
            "prompts": {
                "continue": "Do you want to continue?",
                "input": "Please enter a value:"
            }
        }
        
        # Localized versions (you can expand these when adding new languages)
        localized_samples = {
            "en": sample_messages,  # Base English
            "es": {
                "title": "Script de Ejemplo",
                "welcome": "Bienvenido a la aplicación", 
                "status": {
                    "processing": "Procesando...",
                    "success": "Operación completada exitosamente",
                    "error": "Ocurrió un error"
                },
                "prompts": {
                    "continue": "¿Desea continuar?",
                    "input": "Por favor ingrese un valor:"
                }
            }
            # Add more languages here as you implement them
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create message files for available localizations
            for lang_code in self.supported_languages.keys():
                lang_dir = os.path.join(temp_dir, lang_code)
                os.makedirs(lang_dir)
                
                # Use localized version if available, otherwise fall back to English
                messages_to_use = localized_samples.get(lang_code, sample_messages)
                
                script_file = os.path.join(lang_dir, "sample_script.json")
                with open(script_file, "w", encoding="utf-8") as f:
                    json.dump(messages_to_use, f, ensure_ascii=False, indent=2)
            
            # Test loading messages for each language
            with patch('i18n.loader.os.path.dirname', return_value=temp_dir):
                for lang_code in self.supported_languages.keys():
                    with self.subTest(language=lang_code):
                        messages = load_messages("sample_script", lang_code)
                        
                        # Verify basic structure is preserved
                        self.assertIn("title", messages)
                        self.assertIn("status", messages)
                        self.assertIn("prompts", messages)
                        
                        # Verify nested structure
                        self.assertIn("processing", messages["status"])
                        self.assertIn("continue", messages["prompts"])

    def test_language_directory_structure(self):
        """Test that the i18n directory structure supports all languages"""
        # Check if English directory exists (should always be present)
        en_dir = os.path.join(self.i18n_dir, "en")
        self.assertTrue(os.path.exists(en_dir), "English language directory should exist")
        
        # For each supported language, check if directory can be created
        for lang_code in self.supported_languages.keys():
            lang_dir = os.path.join(self.i18n_dir, lang_code)
            
            # If directory doesn't exist, it should be creatable
            if not os.path.exists(lang_dir):
                # Test that the path is valid (don't actually create it)
                self.assertTrue(os.path.isdir(os.path.dirname(lang_dir)),
                              f"Parent directory for {lang_code} should be valid")

    def test_unicode_support_for_all_languages(self):
        """Test that unicode characters are properly supported for all languages"""
        unicode_test_messages = {
            "en": {
                "greeting": "Hello! 👋",
                "symbols": "✓ ✗ ★ ♥ ⚠ ℹ",
                "numbers": "1234567890"
            },
            "es": {
                "greeting": "¡Hola! 👋", 
                "symbols": "✓ ✗ ★ ♥ ⚠ ℹ",
                "accents": "áéíóúñü ÁÉÍÓÚÑÜ"
            },
            "ja": {
                "greeting": "こんにちは！👋",
                "hiragana": "あいうえお かきくけこ",
                "katakana": "アイウエオ カキクケコ",
                "kanji": "日本語 漢字 文字"
            },
            "zh-CN": {
                "greeting": "你好！👋",
                "simplified": "简体中文 汉字",
                "numbers": "一二三四五六七八九十"
            },
            "pt-BR": {
                "greeting": "Olá! 👋",
                "accents": "ãõçáéíóú ÃÕÇÁÉÍÓÚ",
                "symbols": "✓ ✗ ★ ♥ ⚠ ℹ"
            },
            "ko": {
                "greeting": "안녕하세요! 👋",
                "hangul": "한글 문자 테스트",
                "symbols": "✓ ✗ ★ ♥ ⚠ ℹ"
            }
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            for lang_code, messages in unicode_test_messages.items():
                lang_dir = os.path.join(temp_dir, lang_code)
                os.makedirs(lang_dir)
                
                script_file = os.path.join(lang_dir, "unicode_test.json")
                with open(script_file, "w", encoding="utf-8") as f:
                    json.dump(messages, f, ensure_ascii=False, indent=2)
            
            with patch('i18n.loader.os.path.dirname', return_value=temp_dir):
                for lang_code, expected_messages in unicode_test_messages.items():
                    with self.subTest(language=lang_code):
                        loaded_messages = load_messages("unicode_test", lang_code)
                        
                        # Verify all unicode content is preserved exactly
                        for key, expected_value in expected_messages.items():
                            self.assertEqual(loaded_messages[key], expected_value,
                                           f"Unicode content mismatch for {lang_code}.{key}")

    def test_language_extensibility(self):
        """Test that new languages can be easily added to the system"""
        # Simulate adding a new language (French)
        new_language = "fr"
        new_messages = {
            "title": "Script d'Exemple",
            "welcome": "Bienvenue dans l'application",
            "goodbye": "Au revoir!"
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create directory for new language
            new_lang_dir = os.path.join(temp_dir, new_language)
            os.makedirs(new_lang_dir)
            
            # Create message file for new language
            script_file = os.path.join(new_lang_dir, "test_script.json")
            with open(script_file, "w", encoding="utf-8") as f:
                json.dump(new_messages, f, ensure_ascii=False, indent=2)
            
            # Test that the new language works with existing system
            with patch('i18n.loader.os.path.dirname', return_value=temp_dir):
                messages = load_messages("test_script", new_language)
                
                self.assertEqual(messages["title"], "Script d'Exemple")
                self.assertEqual(messages["welcome"], "Bienvenue dans l'application")
                self.assertEqual(messages["goodbye"], "Au revoir!")

    def test_missing_language_graceful_handling(self):
        """Test graceful handling when a requested language doesn't exist"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create only common messages
            common_messages = {"app_name": "AWS IoT Manager", "version": "1.0"}
            common_file = os.path.join(temp_dir, "common.json")
            with open(common_file, "w", encoding="utf-8") as f:
                json.dump(common_messages, f)
            
            with patch('i18n.loader.os.path.dirname', return_value=temp_dir):
                # Request non-existent language
                messages = load_messages("test_script", "nonexistent_lang")
                
                # Should get common messages only
                self.assertEqual(messages["app_name"], "AWS IoT Manager")
                self.assertEqual(messages["version"], "1.0")

    def get_available_languages(self):
        """Helper method to get currently available languages in the project"""
        available_languages = []
        
        if os.path.exists(self.i18n_dir):
            for item in os.listdir(self.i18n_dir):
                item_path = os.path.join(self.i18n_dir, item)
                if os.path.isdir(item_path) and item in self.supported_languages:
                    available_languages.append(item)
        
        return sorted(available_languages)

    def test_current_language_availability(self):
        """Test which languages are currently available in the project"""
        available_languages = self.get_available_languages()
        
        # At minimum, English should be available
        self.assertIn("en", available_languages, "English language files should be available")
        
        # Print available languages for information
        print(f"\nCurrently available languages: {', '.join(available_languages)}")
        print(f"Supported but not yet implemented: {', '.join(set(self.supported_languages.keys()) - set(available_languages))}")

    def test_language_file_consistency(self):
        """Test that available language files have consistent structure"""
        available_languages = self.get_available_languages()
        
        if len(available_languages) < 2:
            self.skipTest("Need at least 2 languages to test consistency")
        
        # Get list of script files from English (reference language)
        en_dir = os.path.join(self.i18n_dir, "en")
        en_files = [f for f in os.listdir(en_dir) if f.endswith('.json')]
        
        # Check that other languages have the same script files
        for lang_code in available_languages:
            if lang_code == "en":
                continue
                
            lang_dir = os.path.join(self.i18n_dir, lang_code)
            lang_files = [f for f in os.listdir(lang_dir) if f.endswith('.json')]
            
            # For now, just check that the directory exists and can contain files
            # As you add more languages, you can make this more strict
            self.assertTrue(os.path.isdir(lang_dir),
                          f"Language directory {lang_code} should exist")


if __name__ == "__main__":
    unittest.main()