#!/usr/bin/env python3
"""
Test runner for the internationalization test suite
"""

import os
import sys
import unittest

# Add project paths
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "i18n"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "scripts"))

# Import test modules
from .test_i18n_loader import TestI18nLoader
from .test_language_selector import TestLanguageSelector
from .test_script_integration import TestScriptIntegration
from .test_backward_compatibility import TestBackwardCompatibility
from .test_multi_language_support import TestMultiLanguageSupport


def create_test_suite():
    """Create a comprehensive test suite for internationalization"""
    suite = unittest.TestSuite()

    # Add unit tests
    suite.addTest(unittest.makeSuite(TestI18nLoader))
    suite.addTest(unittest.makeSuite(TestLanguageSelector))

    # Add integration tests
    suite.addTest(unittest.makeSuite(TestScriptIntegration))

    # Add multi-language support tests
    suite.addTest(unittest.makeSuite(TestMultiLanguageSupport))

    # Add backward compatibility tests
    suite.addTest(unittest.makeSuite(TestBackwardCompatibility))

    return suite


def run_tests(verbosity=2):
    """Run the complete test suite"""
    print("=" * 70)
    print("AWS IoT Device Management - Internationalization Test Suite")
    print("=" * 70)

    # Create test suite
    suite = create_test_suite()

    # Run tests
    runner = unittest.TextTestRunner(verbosity=verbosity, buffer=True)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped) if hasattr(result, 'skipped') else 0}")

    if result.failures:
        print(f"\nFAILURES ({len(result.failures)}):")
        for test, traceback in result.failures:
            print(f"- {test}")

    if result.errors:
        print(f"\nERRORS ({len(result.errors)}):")
        for test, traceback in result.errors:
            print(f"- {test}")

    success = len(result.failures) == 0 and len(result.errors) == 0
    print(f"\nOverall result: {'PASSED' if success else 'FAILED'}")
    print("=" * 70)

    return success


def run_specific_test_category(category, verbosity=2):
    """Run a specific category of tests"""
    suite = unittest.TestSuite()

    if category == "unit":
        suite.addTest(unittest.makeSuite(TestI18nLoader))
        suite.addTest(unittest.makeSuite(TestLanguageSelector))
        print("Running Unit Tests...")
    elif category == "integration":
        suite.addTest(unittest.makeSuite(TestScriptIntegration))
        print("Running Integration Tests...")
    elif category == "multilang":
        suite.addTest(unittest.makeSuite(TestMultiLanguageSupport))
        print("Running Multi-Language Support Tests...")
    elif category == "compatibility":
        suite.addTest(unittest.makeSuite(TestBackwardCompatibility))
        print("Running Backward Compatibility Tests...")
    else:
        print(f"Unknown test category: {category}")
        return False

    runner = unittest.TextTestRunner(verbosity=verbosity, buffer=True)
    result = runner.run(suite)

    success = len(result.failures) == 0 and len(result.errors) == 0
    print(f"Category '{category}' result: {'PASSED' if success else 'FAILED'}")

    return success


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run internationalization tests")
    parser.add_argument(
        "--category", choices=["unit", "integration", "multilang", "compatibility"], help="Run specific test category"
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    verbosity = 2 if args.verbose else 1

    if args.category:
        success = run_specific_test_category(args.category, verbosity)
    else:
        success = run_tests(verbosity)

    sys.exit(0 if success else 1)
