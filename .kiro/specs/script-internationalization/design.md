# Design Document

## Overview

This design extends the existing internationalization system to all AWS IoT Device Management scripts, ensuring consistent multi-language support across the entire project. The design leverages the proven architecture already implemented in the provision script, applying the same patterns to the remaining scripts while preserving all existing functionality.

## Architecture

### Current I18n System Architecture

The existing internationalization system consists of:

1. **Language Selection Module** (`i18n/language_selector.py`): Handles language detection and user selection
2. **Message Loader** (`i18n/loader.py`): Loads and merges common and script-specific messages
3. **Message Storage**: JSON files organized by language and script
4. **Integration Pattern**: Scripts import the system and use a `get_message()` method

### Extended Architecture

The design extends this system to cover all scripts:

```
i18n/
├── common.json                    # Shared messages across all scripts
├── loader.py                      # Message loading utility (unchanged)
├── language_selector.py           # Language selection (unchanged)
└── en/                           # English language files
    ├── provision_script.json     # Existing
    ├── manage_dynamic_groups.json # New
    ├── manage_packages.json       # New
    ├── create_job.json           # New
    ├── simulate_job_execution.json # New
    ├── explore_jobs.json         # New
    └── cleanup_script.json       # New
```

## Components and Interfaces

### 1. Script Integration Pattern

Each script will follow this integration pattern:

```python
# Add i18n to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "i18n"))

from language_selector import get_language
from loader import load_messages

# Global variables for i18n
USER_LANG = "en"
messages = {}

class ScriptClass:
    def get_message(self, key, *args):
        """Get localized message with optional formatting"""
        msg = messages.get(key, key)
        if args:
            return msg.format(*args)
        return msg

# In main function
if __name__ == "__main__":
    USER_LANG = get_language()
    messages = load_messages("script_name", USER_LANG)
    # Rest of script execution
```

### 2. Message Key Extraction Strategy

For each script, messages will be categorized as:

- **UI Headers and Titles**: Script titles, section headers, separators
- **User Prompts**: Input requests, confirmations, selections
- **Status Messages**: Progress updates, success/failure notifications
- **Error Messages**: Error descriptions, warnings, validation messages
- **Debug Messages**: Debug output, API call information
- **Learning Content**: Educational moments, explanations, next steps

### 3. Message File Structure

Each script's JSON file will follow this structure:

```json
{
    "title": "Script Title",
    "separator": "================",
    "prompts": {
        "user_input": "Enter value: ",
        "confirmation": "Continue? [y/N]: "
    },
    "status": {
        "processing": "Processing...",
        "success": "✅ Success",
        "failed": "❌ Failed"
    },
    "errors": {
        "invalid_input": "❌ Invalid input",
        "api_error": "❌ API Error: {}"
    },
    "debug": {
        "api_call": "📤 API Call: {}",
        "response": "📤 API Response:"
    }
}
```

## Data Models

### Message Loading Flow

1. **Language Detection**: Check environment variable or prompt user
2. **Common Messages**: Load shared messages from `common.json`
3. **Script Messages**: Load script-specific messages from `{language}/{script}.json`
4. **Message Merging**: Script-specific messages override common ones
5. **Fallback Handling**: Missing keys return the key itself as fallback

### Script Modification Pattern

Each script requires these modifications:

1. **Import Addition**: Add i18n imports at the top
2. **Global Variables**: Add USER_LANG and messages globals
3. **Class Method**: Add get_message() method to main class
4. **String Replacement**: Replace hardcoded strings with get_message() calls
5. **Main Function**: Add language initialization in main block

## Error Handling

### Missing Message Keys

When a message key is not found:
- Return the key itself as fallback text
- Log a warning in debug mode
- Continue script execution without interruption

### Missing Language Files

When a language file doesn't exist:
- Fall back to English messages
- Display a warning about missing translations
- Continue with available messages

### Malformed JSON Files

When JSON files are corrupted:
- Log the parsing error
- Fall back to English or use key as fallback
- Prevent script crashes due to i18n issues

## Testing Strategy

### Unit Testing Approach

1. **Message Loading Tests**: Verify correct loading of messages for each script
2. **Fallback Tests**: Test behavior with missing keys and files
3. **Language Selection Tests**: Verify environment variable and interactive selection
4. **Formatting Tests**: Test message formatting with parameters

### Integration Testing

1. **Script Execution Tests**: Run each script with different languages
2. **Environment Variable Tests**: Test AWS_IOT_LANG behavior
3. **Interactive Mode Tests**: Test language selection prompts
4. **Backward Compatibility Tests**: Ensure existing functionality is preserved

### Manual Testing Checklist

For each script:
- [ ] Language selection works correctly
- [ ] All user-visible text is localized
- [ ] Error messages appear in selected language
- [ ] Debug output is localized when enabled
- [ ] Script functionality remains unchanged
- [ ] Environment variable override works
- [ ] Fallback to English works for missing translations

## Implementation Phases

### Phase 1: Message Extraction and JSON Creation

1. Analyze each script to identify all user-facing strings
2. Create comprehensive message keys for each string
3. Generate English JSON files for each script
4. Validate message completeness and accuracy

### Phase 2: Script Integration

1. Add i18n imports to each script
2. Implement get_message() method in each script class
3. Replace hardcoded strings with get_message() calls
4. Add language initialization to main functions

### Phase 3: Testing and Validation

1. Test each script with English language
2. Verify all functionality remains intact
3. Test language selection and environment variable behavior
4. Validate error handling and fallback mechanisms

### Phase 4: Documentation and Cleanup

1. Update script documentation to mention i18n support
2. Add examples of language usage to README
3. Clean up any temporary or debug code
4. Prepare for future language additions

## Design Decisions and Rationales

### Reuse Existing Architecture

**Decision**: Use the same i18n pattern as the provision script
**Rationale**: Proven architecture, consistent developer experience, minimal learning curve

### Script-Specific JSON Files

**Decision**: Create separate JSON files for each script
**Rationale**: Better organization, easier maintenance, allows script-specific customization

### Fallback to Key Names

**Decision**: Return the key itself when messages are missing
**Rationale**: Provides debugging information, prevents crashes, maintains functionality

### Preserve All Functionality

**Decision**: Maintain 100% backward compatibility
**Rationale**: Ensures existing automation continues to work, reduces adoption friction

### Global Message Variables

**Decision**: Use global variables for messages in each script
**Rationale**: Matches existing pattern, simple implementation, easy to understand and maintain