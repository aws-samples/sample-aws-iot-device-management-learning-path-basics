#!/usr/bin/env python3
"""
Example: How to test a new language implementation

This file demonstrates how to test a new language when you add it to the system.
Copy and modify this template for testing your new language implementations.
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
from i18n.language_selector import get_language
from tests.language_test_helper import LanguageTestHelper


class TestNewLanguageExample(unittest.TestCase):
    """
    Example test class for a new language (French in this example)
    
    To test your new language:
    1. Replace 'fr' with your language code
    2. Update the sample messages with your translations
    3. Run the test to validate your implementation
    """

    def setUp(self):
        """Set up test fixtures for French language example"""
        self.language_code = "fr"  # Change this to your language code
        
        # Sample French translations (replace with your language)
        self.sample_translations = {
            "manage_dynamic_groups": {
                "title": "Gestionnaire de Groupes Dynamiques AWS IoT",
                "separator": "=" * 50,
                "prompts": {
                    "enable_debug": "🔧 Activer le mode debug (afficher tous les appels API et réponses)? [y/N]: ",
                    "continue": "Appuyez sur Entrée pour continuer..."
                },
                "status": {
                    "processing": "Traitement en cours...",
                    "success": "✅ Opération réussie",
                    "failed": "❌ Échec de l'opération"
                }
            },
            "cleanup_script": {
                "title": "Script de Nettoyage AWS IoT",
                "warnings": {
                    "destructive": "⚠️ ATTENTION: Cette opération est destructive!",
                    "cost_impact": "💰 Cela peut affecter vos coûts AWS"
                },
                "prompts": {
                    "confirm_cleanup": "Êtes-vous sûr de vouloir continuer? [y/N]: "
                }
            }
        }

    def test_language_message_loading(self):
        """Test that the new language messages can be loaded correctly"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create language directory
            lang_dir = os.path.join(temp_dir, self.language_code)
            os.makedirs(lang_dir)
            
            # Create message files
            for script_name, messages in self.sample_translations.items():
                script_file = os.path.join(lang_dir, f"{script_name}.json")
                with open(script_file, "w", encoding="utf-8") as f:
                    json.dump(messages, f, ensure_ascii=False, indent=2)
            
            # Test loading messages
            with patch('i18n.loader.os.path.dirname', return_value=temp_dir):
                for script_name in self.sample_translations.keys():
                    with self.subTest(script=script_name):
                        messages = load_messages(script_name, self.language_code)
                        
                        # Verify basic structure
                        self.assertIn("title", messages)
                        self.assertIsInstance(messages["title"], str)
                        
                        # Verify nested structure if present
                        if "prompts" in messages:
                            self.assertIsInstance(messages["prompts"], dict)

    def test_language_unicode_support(self):
        """Test that the new language properly handles unicode characters"""
        unicode_test_messages = {
            "accents": "Français avec accents: àáâãäåæçèéêë",
            "symbols": "Symboles: ✓ ✗ ★ ♥ ⚠ ℹ €",
            "quotes": "Guillemets français: « Bonjour le monde »"
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            lang_dir = os.path.join(temp_dir, self.language_code)
            os.makedirs(lang_dir)
            
            script_file = os.path.join(lang_dir, "unicode_test.json")
            with open(script_file, "w", encoding="utf-8") as f:
                json.dump(unicode_test_messages, f, ensure_ascii=False, indent=2)
            
            with patch('i18n.loader.os.path.dirname', return_value=temp_dir):
                messages = load_messages("unicode_test", self.language_code)
                
                # Verify all unicode content is preserved
                for key, expected_value in unicode_test_messages.items():
                    self.assertEqual(messages[key], expected_value)

    def test_language_environment_variable_detection(self):
        """Test that environment variable detection works for the new language"""
        # This test assumes you've added your language to language_selector.py
        # You'll need to update the get_language() function to support your language
        
        original_env = os.environ.get("AWS_IOT_LANG")
        
        try:
            # Test various forms of your language code
            test_cases = [
                "fr",           # ISO code
                "french",       # English name
                "français",     # Native name
                "FR",           # Uppercase
                "FRENCH"        # Uppercase English
            ]
            
            for env_value in test_cases:
                with self.subTest(env_value=env_value):
                    os.environ["AWS_IOT_LANG"] = env_value
                    
                    # Note: This will only work if you've updated language_selector.py
                    # to recognize your language codes
                    try:
                        result = get_language()
                        # Update this assertion based on your language code
                        # self.assertEqual(result, self.language_code)
                        print(f"Environment '{env_value}' -> Language '{result}'")
                    except:
                        # Expected if language not yet added to language_selector.py
                        print(f"Language detection not yet implemented for '{env_value}'")
        
        finally:
            # Restore original environment
            if original_env is not None:
                os.environ["AWS_IOT_LANG"] = original_env
            elif "AWS_IOT_LANG" in os.environ:
                del os.environ["AWS_IOT_LANG"]

    def test_language_completeness_with_helper(self):
        """Test language completeness using the language test helper"""
        helper = LanguageTestHelper()
        
        # This will show what's missing for your language
        validation = helper.validate_language_completeness(self.language_code)
        
        print(f"\nLanguage validation for '{self.language_code}':")
        print(f"  Exists: {validation['exists']}")
        print(f"  Script files: {len(validation['script_files'])}")
        print(f"  Missing scripts: {validation['missing_scripts']}")
        print(f"  Errors: {validation['errors']}")
        
        # You can add assertions here based on your implementation status
        # For example, if you've implemented all scripts:
        # self.assertTrue(validation['exists'])
        # self.assertEqual(len(validation['missing_scripts']), 0)

    def test_compare_with_english(self):
        """Compare your new language implementation with English"""
        helper = LanguageTestHelper()
        
        # This will only work if your language directory exists
        if self.language_code in helper.get_available_languages():
            comparison = helper.compare_languages("en", self.language_code)
            
            print(f"\nComparison: English vs {self.language_code}")
            print(f"  Common scripts: {len(comparison['common_scripts'])}")
            print(f"  Structure matches: {sum(comparison['structure_matches'].values())}")
            print(f"  Message count differences: {len(comparison['message_count_differences'])}")
            
            # Add assertions based on your expectations
            # self.assertGreater(len(comparison['common_scripts']), 0)
        else:
            print(f"Language '{self.language_code}' not yet implemented")


def run_new_language_test():
    """Helper function to run just this language test"""
    suite = unittest.TestLoader().loadTestsFromTestCase(TestNewLanguageExample)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == "__main__":
    print("=" * 60)
    print("New Language Implementation Test Example")
    print("=" * 60)
    print()
    print("This is an example of how to test a new language implementation.")
    print("To use this for your language:")
    print("1. Update the language_code and sample_translations")
    print("2. Add your language to i18n/language_selector.py")
    print("3. Create your language directory and message files")
    print("4. Run this test to validate your implementation")
    print()
    
    success = run_new_language_test()
    
    if success:
        print("\n✅ All tests passed! Your language implementation looks good.")
    else:
        print("\n❌ Some tests failed. Check the output above for details.")
    
    print("\nNext steps:")
    print("- Use language_test_helper.py to validate completeness")
    print("- Run the full test suite: python3 tests/test_runner.py")
    print("- Test with actual scripts using AWS_IOT_LANG environment variable")