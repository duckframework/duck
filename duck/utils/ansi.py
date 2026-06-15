"""
Utilities for removing ANSI escape codes from strings and collections
of strings.

These helpers are useful when processing terminal output, log messages,
or any text containing ANSI color and formatting sequences.
"""
import re

from typing import Iterable, Union


ANSI_REMOVAL_PATTERN = re.compile(r"\x1B[@-_][0-?]*[ -/]*[@-~]")


def remove_ansi_escape_codes(lines: Union[list[str], tuple[str, ...], set[str]]) -> list[str]:
    """
    Remove ANSI escape codes from multiple strings.

    Args:
        lines: A list, tuple, or set containing strings with optional ANSI
            escape codes.

    Returns:
        A list of strings with ANSI escape codes removed.

    Raises:
        TypeError: If ``lines`` is not a list, tuple, or set.
        TypeError: If any item in ``lines`` is not a string.
    """
    if not isinstance(lines, (list, tuple, set)):
        raise TypeError(
            f"lines must be a list, tuple, or set, not {type(lines).__name__!r}."
        )

    cleaned_lines: list[str] = []

    for line in lines:
        if not isinstance(line, str):
            raise TypeError(
                f"all items in lines must be strings, got {type(line).__name__!r}."
            )

        cleaned_lines.append(remove_ansi_escape_codes_str(line))

    return cleaned_lines


def remove_ansi_escape_codes_str(string: str) -> str:
    """
    Remove ANSI escape codes from a string.

    Args:
        string: A string with optional ANSI escape codes.

    Returns:
        The string with ANSI escape codes removed.

    Raises:
        TypeError: If ``string`` is not a string.
    """
    if not isinstance(string, str):
        raise TypeError(f"string must be a string, not {type(string).__name__!r}.")
    return ANSI_REMOVAL_PATTERN.sub("", string)
