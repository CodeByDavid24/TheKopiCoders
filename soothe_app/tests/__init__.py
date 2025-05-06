# soothe_app/__init__.py
# This file can be empty or contain package-level imports and variables

# Optionally, you can expose key functions/classes to make imports cleaner
from soothe_app.blacklist import (
    load_blacklist_from_file,
    contains_blacklisted_content,
    filter_content,
    get_safety_disclaimer,
    get_safe_response_alternative
)
