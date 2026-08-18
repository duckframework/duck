"""
Human readable formatting utilities.

Converts raw values -- byte counts, durations, timestamps, and large
numbers -- into concise, human readable strings suitable for display
in UIs, logs, and reports.

Functions:
    readable_size: Format a byte count as a storage size (e.g. "1.50 MB").
    readable_duration: Format a duration in seconds (e.g. "2 hours 5 minutes").
    readable_date: Format a datetime as relative or absolute (e.g. "3 days ago").
    readable_count: Format a large number compactly (e.g. "1.2K", "3.4M").
"""
from __future__ import annotations

import math
from datetime import datetime


# Datetime
RELATIVE_DATE_THRESHOLD_DAYS = 7  # beyond this, show absolute date
DURATION_UNITS = (
    ("year", 365 * 24 * 3600),
    ("day", 24 * 3600),
    ("hour", 3600),
    ("minute", 60),
    ("second", 1),
)

# Storage Size
BINARY_UNITS = ("B", "KB", "MB", "GB", "TB", "PB", "EB")
BINARY_BASE = 1024

# Compact Count
COMPACT_COUNT_UNITS = (("B", 1e9), ("M", 1e6), ("K", 1e3))


def readable_size(num_bytes: int, precision: int = 2) -> str:
    """
    Convert a byte count into a human readable storage size string.

    Args:
        num_bytes: Size in bytes. Must be non-negative.
        precision: Number of decimal places to show.

    Returns:
        Human readable size, e.g. "1.50 MB".

    Raises:
        ValueError: If num_bytes is negative.
    """
    if num_bytes < 0:
        raise ValueError("num_bytes must be non-negative")

    if num_bytes == 0:
        return "0 B"

    exponent = min(int(math.log(num_bytes, BINARY_BASE)), len(BINARY_UNITS) - 1)
    value = num_bytes / (BINARY_BASE**exponent)
    unit = BINARY_UNITS[exponent]

    # Skip decimals when the value is still in whole bytes
    if unit == "B":
        return f"{int(value)} {unit}"

    return f"{value:.{precision}f} {unit}"


def readable_duration(total_seconds: float, max_units: int = 2) -> str:
    """
    Convert a duration in seconds into a human readable string.

    Args:
        total_seconds: Duration in seconds. Must be non-negative.
        max_units: Maximum number of time units to include, e.g. 2
            gives "1 day 3 hours" instead of "1 day 3 hours 5 minutes".

    Returns:
        Human readable duration, e.g. "2 hours 5 minutes".

    Raises:
        ValueError: If total_seconds is negative.
    """
    if total_seconds < 0:
        raise ValueError("total_seconds must be non-negative")

    if total_seconds < 1:
        return "0 seconds"

    remaining = int(total_seconds)
    parts: list[str] = []

    for unit_name, unit_seconds in DURATION_UNITS:
        unit_value, remaining = divmod(remaining, unit_seconds)
        if unit_value:
            plural = "s" if unit_value != 1 else ""
            parts.append(f"{unit_value} {unit_name}{plural}")

    return " ".join(parts[:max_units]) if parts else "0 seconds"


def readable_date(dt: datetime, reference: datetime | None = None) -> str:
    """
    Convert a datetime into a human readable relative or absolute string.

    Args:
        dt: The datetime to describe.
        reference: The datetime to compare against. Defaults to now.

    Returns:
        Relative description for recent dates, e.g. "3 hours ago" or
        "in 2 days"; falls back to an absolute "%b %d, %Y" date once
        the gap exceeds RELATIVE_DATE_THRESHOLD_DAYS.
    """
    reference = reference or datetime.now(dt.tzinfo)
    delta_seconds = (reference - dt).total_seconds()

    if abs(delta_seconds) >= RELATIVE_DATE_THRESHOLD_DAYS * 24 * 3600:
        return dt.strftime("%b %d, %Y")

    is_future = delta_seconds < 0
    duration_text = readable_duration(abs(delta_seconds), max_units=1)

    if duration_text == "0 seconds":
        return "just now"

    return f"in {duration_text}" if is_future else f"{duration_text} ago"


def readable_count(num: float, precision: int = 1) -> str:
    """
    Convert a large number into a compact human readable string.

    Args:
        num: The number to format.
        precision: Number of decimal places to show for scaled values.

    Returns:
        Human readable count, e.g. "1.2K", "3.4M", "980".
    """
    sign = "-" if num < 0 else ""
    num = abs(num)

    for unit, threshold in COMPACT_COUNT_UNITS:
        if num >= threshold:
            return f"{sign}{num / threshold:.{precision}f}{unit}"

    return f"{sign}{int(num)}"
