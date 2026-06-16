"""
Localized yes/no confirmation handling.

This module provides functions to validate user input for yes/no prompts
across all supported languages, so that a German user typing 'j' (for 'ja')
or a French user typing 'o' (for 'oui') gets the expected behavior.
"""

# Affirmative responses per language (lowercase)
AFFIRMATIVE_RESPONSES = {
    "en": ["y", "yes"],
    "de": ["j", "ja", "y", "yes"],
    "fr": ["o", "oui", "y", "yes"],
    "it": ["s", "sì", "si", "y", "yes"],
    "es": ["s", "sí", "si", "y", "yes"],
    "pt": ["s", "sim", "y", "yes"],
    "ja": ["y", "yes", "はい"],
    "ko": ["y", "yes", "예", "네"],
    "zh": ["y", "yes", "是"],
}

# Negative responses per language (lowercase)
NEGATIVE_RESPONSES = {
    "en": ["n", "no"],
    "de": ["n", "nein", "no"],
    "fr": ["n", "non", "no"],
    "it": ["n", "no"],
    "es": ["n", "no"],
    "pt": ["n", "não", "nao", "no"],
    "ja": ["n", "no", "いいえ"],
    "ko": ["n", "no", "아니요", "아니"],
    "zh": ["n", "no", "否"],
}


def is_affirmative(response, language="en"):
    """
    Check if a user response is affirmative (yes) in the given language.

    Always accepts English 'y'/'yes' as a fallback regardless of language.

    Args:
        response: The user's input string (will be stripped and lowercased)
        language: The current language code (e.g., 'de', 'fr', 'it')

    Returns:
        True if the response is affirmative, False otherwise
    """
    cleaned = response.strip().lower()
    affirmatives = AFFIRMATIVE_RESPONSES.get(language, AFFIRMATIVE_RESPONSES["en"])
    return cleaned in affirmatives


def is_negative(response, language="en"):
    """
    Check if a user response is negative (no) in the given language.

    Always accepts English 'n'/'no' as a fallback regardless of language.

    Args:
        response: The user's input string (will be stripped and lowercased)
        language: The current language code (e.g., 'de', 'fr', 'it')

    Returns:
        True if the response is negative, False otherwise
    """
    cleaned = response.strip().lower()
    negatives = NEGATIVE_RESPONSES.get(language, NEGATIVE_RESPONSES["en"])
    return cleaned in negatives
