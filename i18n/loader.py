import json
import os


def load_messages(script_name, language="en"):
    """Load messages for a specific script and language"""
    base_path = os.path.dirname(__file__)

    # Load common messages
    common_file = os.path.join(base_path, "common.json")
    messages = {}
    if os.path.exists(common_file):
        with open(common_file, "r", encoding="utf-8") as f:
            messages.update(json.load(f))

    # Load script-specific messages
    script_file = os.path.join(base_path, language, f"{script_name}.json")
    if os.path.exists(script_file):
        with open(script_file, "r", encoding="utf-8") as f:
            messages.update(json.load(f))

    return messages
