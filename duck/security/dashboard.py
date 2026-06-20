"""
Security utilities and validation helpers for the built-in Dashboard.
"""
import os


DEFAULT_USERNAME = "admin"
DEFAULT_PASSWORD = "admin"


def get_dashboard_security_issues() -> list[str]:
    """
    Return a list of dashboard security configuration issues.

    Returns:
        list[str]:
            A list of human-readable validation messages. An empty list
            indicates that the dashboard is securely configured.
    """
    from duck.settings import SETTINGS
    from duck.security.passwords import validate_password_strength, PasswordValidationError
    
    # Only retrieve credentials from environment in production - it's more sure that way.
    if SETTINGS["DEBUG"]:
        return []

    # We are in production at this point.
    issues = []
    username = os.getenv("DASHBOARD_USERNAME", "").strip()
    password = os.getenv("DASHBOARD_PWD", "").strip()

    if not username:
        issues.append(
            "DASHBOARD_USERNAME is not configured in environment."
        )
    elif username == DEFAULT_USERNAME:
        issues.append(
            "DASHBOARD_USERNAME is using the default value."
        )

    if not password:
        issues.append(
            "DASHBOARD_PWD is not configured in environment."
        )
    elif password == DEFAULT_PASSWORD:
        issues.append(
            "DASHBOARD_PWD is using the default value."
        )
    
    # Check for password strength
    if password and username and os.getenv("DASHBOARD_IGNORE_PWD_VALIDATION", None) not in ("true", "1"):
        try:
            validate_password_strength(password, user_attributes=(username, ))
        except PasswordValidationError as e:
            issues.append(f"Dashboard {e} To ignore validation set environment variable 'DASHBOARD_IGNORE_PWD_VALIDATION' to '1'.")
            
    return issues


def is_dashboard_securely_configured() -> bool:
    """
    Determine whether the dashboard is securely configured.

    Returns:
        bool:
            ``True`` if the dashboard is securely configured,
            otherwise ``False``.
    """
    return not get_dashboard_security_issues()


class InsecureDashboardWarning(UserWarning):
    """
    Warning flagged when dashboard is not securely configured.
    """
