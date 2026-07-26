"""
Exceptions raised by Duck Sync.
"""


class DuckSyncError(Exception):
    """
    Base class for all Duck Sync errors.

    Catch this to handle any failure Duck Sync can raise without
    importing each subclass individually.
    """


class ConfigNotFoundError(DuckSyncError):
    """
    Raised when no duck.toml can be located.

    Typically thrown by :func:`~duck_sync.config.find_config` after
    walking up to the filesystem root without finding the config file.
    """


class ConfigParseError(DuckSyncError):
    """
    Raised when duck.toml exists but cannot be parsed.

    Wraps a :class:`tomllib.TOMLDecodeError` with a message that
    includes the offending file path.
    """


class UnsupportedPlatformError(DuckSyncError):
    """
    Raised when no supported package manager can be found on the host.

    Thrown by :func:`~duck_sync.platform_utils.detect_backend_name`
    when the OS family is unrecognised or none of the known package
    manager binaries are on ``PATH``.
    """


class InstallationError(DuckSyncError):
    """
    Raised when a package manager command exits non-zero.

    Args:
        package: The package name (or requirements file label) that
            failed to install.
        reason: The stderr output from the failed command, or a short
            fallback string when stderr was empty.
    """

    def __init__(self, package: str, reason: str) -> None:
        self.package = package
        self.reason = reason
        super().__init__(f"Failed to install '{package}': {reason}")
