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

        print(lang.t(error_key))

# ---------------------------
# General Validators
# ---------------------------

# URL Validation
# ---------------------------
def is_valid_url(url: str) -> str | None:
    """
    Validate that the given string is a valid HTTP/HTTPS URL.
    Returns the url string if valid, None otherwise.
    """
    try:
        result = urlparse(url)
        if all([result.scheme in ("http", "https"), result.netloc]):
            return url
        return None
    except ValueError:
        return None

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
def is_valid_date(value: str):
    """Validate date string and return date object."""
    if not value or value.strip() == "":
        return None
    try:
        return datetime.strptime(value, "%d.%m.%Y").date()
    except ValueError:
        return None

# Is positive integer
# ---------------------------
def is_positive_integer(value: str) -> int | None:
    """Returns a positive integer if valid, otherwise None."""
    try:
        number = int(value)
        if number > 0:
            return number
    except ValueError:
        pass
    return None

# Is valid month (1-12)
# ---------------------------
def is_valid_month(value: str) -> int | None:
    """Returns month as int (1-12) if valid, otherwise None."""
    try:
        month = int(value)
        if 1 <= month <= 12:
            return month
    except ValueError:
        pass
    return None

# Is valid tag, coma seperated
# ---------------------------
def is_valid_tags(value: str) -> list[str] | None:
    """
    Validate a comma-separated list of tags.
    Returns a list of stripped, non-empty strings, or None if nothing valid.
    """
    tags = [t.strip().lower() for t in value.split(",") if t.strip()]
    return tags if tags else None


# Is positive integer or empty
# ---------------------------
def is_positive_integer_or_empty(value: str) -> int | None:
    """
    Returns a positive integer if valid.
    Returns 0 for empty (meaning infinite lifespan).
    Returns None if invalid (triggers retry).
    """
    if not value.strip():
        return 0
    try:
        number = int(value)
        if number > 0:
            return number
    except ValueError:
        pass
    return None
