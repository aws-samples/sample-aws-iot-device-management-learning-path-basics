# Internationalization Test Suite

This directory contains comprehensive tests for the internationalization (i18n) system implemented across all AWS IoT Device Management scripts.

## Test Structure

### Unit Tests
- **`test_i18n_loader.py`**: Tests for message loading, fallback behavior, and JSON file handling
- **`test_language_selector.py`**: Tests for environment variable detection and interactive language selection

### Integration Tests
- **`test_script_integration.py`**: Tests for proper i18n integration across all scripts

### Multi-Language Support Tests
- **`test_multi_language_support.py`**: Tests for multi-language functionality and extensibility
- **`language_test_helper.py`**: Utility for testing new language implementations

### Multilingual README Tests
- **`test_multilingual_readme.py`**: Comprehensive validation suite for multilingual README implementation
- **`test_readme_navigation.py`**: Tests for navigation table consistency across all README files
- **`test_readme_essentials.py`**: Tests for essential requirements and content preservation

### Backward Compatibility Tests
- **`test_backward_compatibility.py`**: Tests to ensure existing functionality is preserved

### Test Runner
- **`test_runner.py`**: Centralized test runner with category-specific execution

## Running Tests

### Run All Tests
```bash
python3 tests/test_runner.py
```

### Run Specific Categories
```bash
# Unit tests only
python3 tests/test_runner.py --category unit

# Integration tests only
python3 tests/test_runner.py --category integration

# Multi-language support tests only
python3 tests/test_runner.py --category multilang

# Backward compatibility tests only
python3 tests/test_runner.py --category compatibility
```

### Verbose Output
```bash
python3 tests/test_runner.py --verbose
```

### Multilingual README Validation
```bash
# Run comprehensive multilingual README validation
python3 tests/test_multilingual_readme.py

# Run individual validation components
python3 tests/test_readme_navigation.py
python3 tests/test_readme_essentials.py
```

## Test Coverage

### Message Loading (`test_i18n_loader.py`)
- ✅ Loading messages with existing files
- ✅ Script-specific messages overriding common messages
- ✅ Handling missing common.json files
- ✅ Handling missing script-specific files
- ✅ Handling missing both files (empty dict fallback)
- ✅ Malformed JSON error handling
- ✅ Different language support
- ✅ Nested message structure support

### Language Selection (`test_language_selector.py`)
- ✅ Environment variable detection for all supported languages
- ✅ Case-insensitive environment variable handling
- ✅ Interactive selection with valid choices
- ✅ Invalid input handling with retry logic
- ✅ Keyboard interrupt handling
- ✅ Language code completeness validation
- ✅ Fallback to interactive mode when no environment variable

### Script Integration (`test_script_integration.py`)
- ✅ Proper i18n imports in all scripts
- ✅ Required global variables (USER_LANG, messages)
- ✅ get_message() method implementation
- ✅ Language initialization in main functions
- ✅ Message file existence and validity
- ✅ Script import functionality
- ✅ Consistent message key patterns

### Backward Compatibility (`test_backward_compatibility.py`)
- ✅ Main execution structure preservation
- ✅ AWS client initialization patterns
- ✅ Error handling preservation
- ✅ Colorama usage preservation
- ✅ Threading patterns preservation
- ✅ get_message fallback behavior
- ✅ Environment variable compatibility
- ✅ Command-line interface preservation
- ✅ Debug mode functionality
- ✅ Special character and emoji preservation

## Requirements Validation

This test suite validates the following requirements:

- **Requirement 2.4**: Graceful handling of missing message keys and files
- **Requirement 5.3**: Backward compatibility with existing functionality
- **Requirement 5.4**: Preservation of command-line interfaces and parameters
- **Requirement 5.5**: Maintenance of exit codes and error handling patterns

## Test Philosophy

- **Minimal Mocking**: Tests use real functionality where possible
- **Focused Testing**: Each test focuses on core functional logic
- **Fallback Validation**: Extensive testing of error conditions and fallbacks
- **Integration Verification**: Tests verify actual script integration rather than just imports
- **Compatibility Assurance**: Tests ensure existing automation continues to work

## Multi-Language Testing Tools

### Language Test Helper
```bash
# Check available languages
python3 tests/language_test_helper.py

# Generate report for specific language
python3 tests/language_test_helper.py --language es

# Generate comprehensive report for all languages
python3 tests/language_test_helper.py --report

# Compare two language implementations
python3 tests/language_test_helper.py --compare en es
```

### Testing New Languages

When adding a new language (e.g., French):

1. **Create language directory**: `i18n/fr/`
2. **Add message files**: Copy from `i18n/en/` and translate
3. **Test the implementation**:
   ```bash
   python3 tests/test_runner.py --category multilang
   python3 tests/language_test_helper.py --language fr
   ```
4. **Validate completeness**:
   ```bash
   python3 tests/language_test_helper.py --compare en fr
   ```

### Language Testing Features

- ✅ **Unicode Support**: Tests all character sets (emojis, accents, CJK characters)
- ✅ **Structure Validation**: Ensures consistent message structure across languages
- ✅ **Completeness Checking**: Identifies missing translations
- ✅ **Fallback Testing**: Validates graceful handling of missing languages
- ✅ **Extensibility Testing**: Verifies new languages integrate seamlessly

## Adding New Tests

When adding new tests:

1. Follow the existing naming convention (`test_*.py`)
2. Add new test classes to the appropriate category
3. Update `test_runner.py` to include new test modules
4. Ensure tests are self-contained and don't require external resources
5. Test both success and failure scenarios
6. Validate fallback behavior for error conditions
7. For language-specific tests, use `test_multi_language_support.py` as a template