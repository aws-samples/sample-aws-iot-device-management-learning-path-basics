#!/usr/bin/env python3
"""
Language Testing Helper - Utilities for testing new language implementations
"""

import json
import os
import sys
from typing import Dict, List, Set, Tuple

# Add project paths
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "i18n"))
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from i18n.loader import load_messages


class LanguageTestHelper:
    """Helper class for testing language implementations"""
    
    def __init__(self):
        self.i18n_dir = os.path.join(os.path.dirname(__file__), "..", "i18n")
        self.scripts_dir = os.path.join(os.path.dirname(__file__), "..", "scripts")
        
        # Define expected script files (based on integrated scripts)
        self.expected_scripts = [
            "manage_dynamic_groups",
            "manage_packages", 
            "create_job",
            "simulate_job_execution",
            "explore_jobs",
            "cleanup_script"
        ]

    def get_available_languages(self) -> List[str]:
        """Get list of currently available languages"""
        languages = []
        
        if os.path.exists(self.i18n_dir):
            for item in os.listdir(self.i18n_dir):
                item_path = os.path.join(self.i18n_dir, item)
                if os.path.isdir(item_path) and not item.startswith('.'):
                    languages.append(item)
        
        return sorted(languages)

    def get_script_files_for_language(self, language: str) -> List[str]:
        """Get list of script message files for a specific language"""
        lang_dir = os.path.join(self.i18n_dir, language)
        
        if not os.path.exists(lang_dir):
            return []
        
        script_files = []
        for file in os.listdir(lang_dir):
            if file.endswith('.json'):
                script_files.append(file.replace('.json', ''))
        
        return sorted(script_files)

    def validate_language_completeness(self, language: str) -> Dict[str, any]:
        """Validate that a language implementation is complete"""
        results = {
            'language': language,
            'exists': False,
            'script_files': [],
            'missing_scripts': [],
            'valid_json': [],
            'invalid_json': [],
            'message_counts': {},
            'unicode_support': True,
            'errors': []
        }
        
        lang_dir = os.path.join(self.i18n_dir, language)
        
        # Check if language directory exists
        if not os.path.exists(lang_dir):
            results['errors'].append(f"Language directory '{language}' does not exist")
            return results
        
        results['exists'] = True
        results['script_files'] = self.get_script_files_for_language(language)
        
        # Check for missing expected scripts
        results['missing_scripts'] = [
            script for script in self.expected_scripts 
            if script not in results['script_files']
        ]
        
        # Validate each script file
        for script in results['script_files']:
            script_file = os.path.join(lang_dir, f"{script}.json")
            
            try:
                with open(script_file, 'r', encoding='utf-8') as f:
                    messages = json.load(f)
                    results['valid_json'].append(script)
                    results['message_counts'][script] = self._count_messages(messages)
                    
                    # Test unicode support
                    json_str = json.dumps(messages, ensure_ascii=False)
                    
            except json.JSONDecodeError as e:
                results['invalid_json'].append(script)
                results['errors'].append(f"Invalid JSON in {script}.json: {e}")
            except UnicodeDecodeError as e:
                results['unicode_support'] = False
                results['errors'].append(f"Unicode error in {script}.json: {e}")
            except Exception as e:
                results['errors'].append(f"Error processing {script}.json: {e}")
        
        return results

    def _count_messages(self, messages: dict, prefix: str = "") -> int:
        """Recursively count messages in a nested dictionary"""
        count = 0
        for key, value in messages.items():
            if isinstance(value, dict):
                count += self._count_messages(value, f"{prefix}{key}.")
            else:
                count += 1
        return count

    def compare_languages(self, lang1: str, lang2: str) -> Dict[str, any]:
        """Compare two language implementations for consistency"""
        results = {
            'lang1': lang1,
            'lang2': lang2,
            'common_scripts': [],
            'lang1_only': [],
            'lang2_only': [],
            'structure_matches': {},
            'message_count_differences': {},
            'errors': []
        }
        
        lang1_scripts = set(self.get_script_files_for_language(lang1))
        lang2_scripts = set(self.get_script_files_for_language(lang2))
        
        results['common_scripts'] = sorted(lang1_scripts & lang2_scripts)
        results['lang1_only'] = sorted(lang1_scripts - lang2_scripts)
        results['lang2_only'] = sorted(lang2_scripts - lang1_scripts)
        
        # Compare structure for common scripts
        for script in results['common_scripts']:
            try:
                messages1 = load_messages(script, lang1)
                messages2 = load_messages(script, lang2)
                
                keys1 = set(self._get_all_keys(messages1))
                keys2 = set(self._get_all_keys(messages2))
                
                results['structure_matches'][script] = keys1 == keys2
                
                count1 = self._count_messages(messages1)
                count2 = self._count_messages(messages2)
                
                if count1 != count2:
                    results['message_count_differences'][script] = {
                        lang1: count1,
                        lang2: count2,
                        'difference': abs(count1 - count2)
                    }
                    
            except Exception as e:
                results['errors'].append(f"Error comparing {script}: {e}")
        
        return results

    def _get_all_keys(self, messages: dict, prefix: str = "") -> List[str]:
        """Get all keys from a nested dictionary"""
        keys = []
        for key, value in messages.items():
            full_key = f"{prefix}{key}" if prefix else key
            keys.append(full_key)
            
            if isinstance(value, dict):
                keys.extend(self._get_all_keys(value, f"{full_key}."))
        
        return keys

    def generate_language_report(self, language: str = None) -> str:
        """Generate a comprehensive report for a language or all languages"""
        if language:
            return self._generate_single_language_report(language)
        else:
            return self._generate_all_languages_report()

    def _generate_single_language_report(self, language: str) -> str:
        """Generate report for a single language"""
        validation = self.validate_language_completeness(language)
        
        report = f"""
Language Implementation Report: {language.upper()}
{'=' * 50}

Status: {'✅ Available' if validation['exists'] else '❌ Not Available'}

Script Files ({len(validation['script_files'])}):
{chr(10).join(f"  ✅ {script}.json ({validation['message_counts'].get(script, 0)} messages)" for script in validation['valid_json'])}
{chr(10).join(f"  ❌ {script}.json (Invalid JSON)" for script in validation['invalid_json'])}

Missing Scripts ({len(validation['missing_scripts'])}):
{chr(10).join(f"  ⚠️  {script}.json" for script in validation['missing_scripts'])}

Unicode Support: {'✅ Supported' if validation['unicode_support'] else '❌ Issues Found'}

Errors ({len(validation['errors'])}):
{chr(10).join(f"  ❌ {error}" for error in validation['errors'])}
"""
        return report

    def _generate_all_languages_report(self) -> str:
        """Generate report for all available languages"""
        available_languages = self.get_available_languages()
        
        report = f"""
Multi-Language Implementation Report
{'=' * 50}

Available Languages ({len(available_languages)}): {', '.join(available_languages)}

Language Details:
"""
        
        for lang in available_languages:
            validation = self.validate_language_completeness(lang)
            completeness = len(validation['script_files']) / len(self.expected_scripts) * 100
            
            report += f"""
{lang.upper()}:
  Scripts: {len(validation['script_files'])}/{len(self.expected_scripts)} ({completeness:.1f}% complete)
  Status: {'✅ Valid' if not validation['errors'] else '⚠️ Issues'}
  Total Messages: {sum(validation['message_counts'].values())}
"""
        
        return report

    def test_message_loading(self, language: str, script: str) -> Dict[str, any]:
        """Test message loading for a specific script and language"""
        result = {
            'language': language,
            'script': script,
            'success': False,
            'messages_loaded': 0,
            'sample_messages': {},
            'errors': []
        }
        
        try:
            messages = load_messages(script, language)
            result['success'] = True
            result['messages_loaded'] = self._count_messages(messages)
            
            # Get sample messages (first few keys)
            sample_keys = list(self._get_all_keys(messages))[:5]
            for key in sample_keys:
                # Navigate to nested value
                value = messages
                for part in key.split('.'):
                    value = value[part]
                result['sample_messages'][key] = value
                
        except Exception as e:
            result['errors'].append(str(e))
        
        return result


def main():
    """Main function for command-line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Language Testing Helper")
    parser.add_argument("--language", "-l", help="Test specific language")
    parser.add_argument("--compare", "-c", nargs=2, metavar=("LANG1", "LANG2"),
                       help="Compare two languages")
    parser.add_argument("--report", "-r", action="store_true",
                       help="Generate comprehensive report")
    
    args = parser.parse_args()
    
    helper = LanguageTestHelper()
    
    if args.compare:
        comparison = helper.compare_languages(args.compare[0], args.compare[1])
        print(f"Comparison: {comparison['lang1']} vs {comparison['lang2']}")
        print(f"Common scripts: {len(comparison['common_scripts'])}")
        print(f"Structure mismatches: {sum(1 for match in comparison['structure_matches'].values() if not match)}")
        
    elif args.language:
        report = helper.generate_language_report(args.language)
        print(report)
        
    elif args.report:
        report = helper.generate_language_report()
        print(report)
        
    else:
        # Default: show available languages
        languages = helper.get_available_languages()
        print(f"Available languages: {', '.join(languages)}")
        print("Use --help for more options")


if __name__ == "__main__":
    main()