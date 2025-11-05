"""
Compatibility module for applying backward compatibility especially for `python <= 3.13`.
"""
import sys

def apply_backward_compatibility():
    # Patch datetime module
    # Only patch if Python < 3.11
    if sys.version_info < (3, 11):
        import datetime, timezone
        datetime.UTC = timezone.utc
