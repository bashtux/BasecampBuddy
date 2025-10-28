"""
validation.py
----------------------------------
Centralized input validation utilities for the application.

Contains generic validation helpers (URL, email, numeric, etc.)
and reusable input prompt functions that integrate with language
translations and configuration.
"""

from urllib.parse import urlparse
from app.lang import lang
from datetime import datetime

# ---------------------------
# URL Validation
# ---------------------------
def is_valid_url(url: str) -> bool:
    """
    Validate that the given string is a valid HTTP/HTTPS URL.
    Returns True if valid, False otherwise.
    """
    try:
        result = urlparse(url)
        return all([result.scheme in ("http", "https"), result.netloc])
    except ValueError:
        return False


# ---------------------------
# Generic Input Prompt with Validation
# ---------------------------
def prompt_validated_input(
    prompt_key: str,
    validator,
    allow_empty: bool = True,
    error_key: str = 'msg.invalid_input'
    ) -> str | None:

    """
    Prompt the user for input and validate it using the given validator function.

    Args:
        prompt_key (str): Language key for the input prompt, e.g. 'brand.prompt.url'
        validator (callable): Function that takes a string and returns True/False
        allow_empty (bool): Whether to allow skipping (return None)
        error_key (str): Language key for the error message

    Returns:
        str | None: The valid input string, or None if left empty
    """

    while True:
        value = input(lang.t(prompt_key)).strip()
        if not value and allow_empty:
            return None
        try:
            return validator(value)
        except ValueError:
            print(lang.t(error_key))


# ---------------------------
# General Validators
# ---------------------------
def is_nonempty_string(value: str) -> bool:
    """Checks that the string is not empty or just whitespace."""
    return bool(value and value.strip())


def is_positive_number(value: str) -> bool:
    """Checks if the value is a positive integer or float."""
    try:
        return float(value) > 0
    except ValueError:
        return False


def is_yes_no(value: str) -> bool:
    """Checks if the value is a yes/no response (localized variants can be added)."""
    return value.lower() in ("y", "yes", "n", "no")


def is_valid_date(value: str) -> datetime.date:
    """
    Validate and convert a date string to a date object.
    Supports multiple common formats.
    """
    if not value:
        raise ValueError("Empty date not allowed")

    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    raise ValueError("Invalid date format")

