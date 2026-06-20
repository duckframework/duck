"""
Password strength validation utilities.

This module provides reusable validators for checking password length,
numeric-only passwords, common passwords, and user-attribute similarity.
"""

from __future__ import annotations

import gzip
import difflib

from pathlib import Path
from typing import Iterable, Sequence

from duck.storage import duck_storage


_COMMON_PASSWORDS_CACHE: set[str] | None = None
_COMMON_PASSWORDS_PATH = Path(duck_storage) / "etc/others/common-passwords.txt.gz"


class PasswordValidationError(ValueError):
    """
    Raised when a password fails one or more strength checks.
    """
    def __init__(self, messages: Sequence[str]) -> None:
        super().__init__(f"Password validation failed: {messages[0]}")
        self.messages = list(messages)


def load_common_passwords(path: str | Path) -> set[str]:
    """
    Load common passwords from a plain text or gzip-compressed file.

    Args:
        path: Path to a `.txt` or `.txt.gz` password list.

    Returns:
        A normalized set of lowercase passwords.
    """
    password_path = Path(path)

    if password_path.suffix == ".gz":
        opener = gzip.open
    else:
        opener = open

    with opener(password_path, "rt", encoding="utf-8") as file:
        return {
            line.strip().lower()
            for line in file
            if line.strip()
        }


def get_common_passwords(path: str | Path) -> set[str]:
    """
    Load and cache common passwords.

    Args:
        path: Path to a common-password list.

    Returns:
        Cached set of common passwords.
    """
    global _COMMON_PASSWORDS_CACHE

    if _COMMON_PASSWORDS_CACHE is None:
        _COMMON_PASSWORDS_CACHE = load_common_passwords(path)

    return _COMMON_PASSWORDS_CACHE


def is_too_similar(
    password: str,
    user_attributes: Iterable[str],
    *,
    max_similarity: float = 0.7,
) -> bool:
    """
    Check whether a password is too similar to user attributes.

    Args:
        password: Raw password.
        user_attributes: User-related values like username, email, or name.
        max_similarity: Maximum allowed similarity ratio.

    Returns:
        True if the password is too similar, otherwise False.
    """
    normalized_password = password.lower()

    for value in user_attributes:
        value = str(value).strip().lower()

        if not value:
            continue
       
        # Compute similarity ratio
        similarity = difflib.SequenceMatcher(
            a=normalized_password,
            b=value,
        ).quick_ratio()
        
        # Check if similarity is greater than max_similarity
        if similarity >= max_similarity:
            return True

    return False


def validate_password_strength(
    password: str,
    *,
    user_attributes: Iterable[str] = (),
    common_passwords_path: str | Path | None = _COMMON_PASSWORDS_PATH,
    min_length: int = 8,
    max_similarity: float = 0.7,
) -> None:
    """
    Validate password strength.

    Args:
        password: Raw password to validate.
        user_attributes: Optional user-related values to compare against.
        common_passwords_path: Optional path to common-passwords `.txt` or `.txt.gz`.
        min_length: Minimum allowed password length.
        max_similarity: Maximum allowed similarity to user attributes.

    Raises:
        TypeError: If password is not a string.
        PasswordValidationError: If password fails validation.
    """
    errors: list[str] = []
    
    if not isinstance(password, str):
        raise TypeError("Password must be a string.")
        
    if len(password) < min_length:
        errors.append(f"Password must contain at least {min_length} characters.")

    if password.isdigit():
        errors.append("Password cannot be entirely numeric.")

    if common_passwords_path is not None:
        common_passwords = get_common_passwords(common_passwords_path)
        
        if password.lower() in common_passwords:
            errors.append("Password is too common.")

    if is_too_similar(password, user_attributes, max_similarity=max_similarity):
        errors.append("Password is too similar to your personal information.")

    if errors:
        raise PasswordValidationError(errors)
