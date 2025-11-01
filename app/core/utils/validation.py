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

        # Allow empty values if permitted
        if not value and allow_empty:
            return None

        # Validator can return cleaned value or None
        cleaned = validator(value)
        if cleaned is not None:
            return cleaned

        print(lang.t(validation.error.key))

# ---------------------------
# General Validators
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

# Non empty string
# ---------------------------
def is_nonempty_string(value: str) -> str | None:
    """Checks that the string is not empty or just whitespace."""
    return value.strip() if value and value.strip() else None

# Is positive number
# ---------------------------
def is_positive_number(value: str) -> bool:
    """Returns a positive float if valid, otherwise None."""
    try:
        number = float(value)
        if number > 0:
            return number
    except ValueError:
        pass
    return None

# Is Yes or No
# ---------------------------
def is_yes_no(value: str) -> bool | None:
    """
    Validates yes/no or true/false input.
    Returns True or False (not strings).
    Returns None if invalid or empty (so prompt_validated_input can retry).
    """
    if not value:
        return None

    normalized = value.strip().lower()

    truthy = {"y", "yes", "true", "1"}
    falsy = {"n", "no", "false", "0"}

    if normalized in truthy:
        return True
    elif normalized in falsy:
        return False
    else:
        return None

# Is Valid date of defined format
# ---------------------------
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

