"""
Loads and validates the [dependencies]/[development] sections of duck.toml.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


try:
    import tomllib
except ImportError:
    import tomli as tomllib


from duck.cli.commands.sync.exceptions import ConfigNotFoundError, ConfigParseError


# Default filename Duck Sync looks for at the project root
CONFIG_FILENAME = "duck.toml"


@dataclass
class DependencyGroup:
    """
    A named collection of python and system dependencies.

    Args:
        python:
            Python packages installable via pip/uv.
        
        system:
            System level packages resolved through the OS package manager.
        
        requirements:
            Path to a requirements.txt, relative to duck.toml.
            Installed alongside the python list rather than replacing it.
        
        python_args:
            Extra CLI args appended to every python install
            command in this group, e.g. ["--no-cache-dir"].
        
        python_package_args:
            Per-package extra args, keyed by package
            name, merged in after python_args.
        
        system_args:
            Extra CLI args appended to every system install
            command in this group, e.g. ["--no-install-recommends"].
        
        system_package_args:
            Per-package extra args for system installs,
            keyed by the generic name written in the system list.
    """
    python: list[str] = field(default_factory=list)
    system: list[str] = field(default_factory=list)
    requirements: str = ""
    python_args: list[str] = field(default_factory=list)
    python_package_args: dict[str, list[str]] = field(default_factory=dict)
    system_args: list[str] = field(default_factory=list)
    system_package_args: dict[str, list[str]] = field(default_factory=dict)


@dataclass
class DuckSyncConfig:
    """
    Fully parsed representation of a project's duck.toml file.

    Args:
        dependencies:
            Required runtime dependencies.
        
        development:
            Optional dependencies only needed for local development.
        
        overrides:
            Per package name overrides for system package names, keyed
            by backend name (apt, brew, dnf, pacman, choco).
        
        base_dir:
            Directory duck.toml lives in, used to resolve relative
            paths such as requirements.
        
        use_sudo: Whether system installs should be prefixed with sudo.
            None means auto-detect: skip sudo when already running as root.
    """
    dependencies: DependencyGroup = field(default_factory=DependencyGroup)
    development: DependencyGroup = field(default_factory=DependencyGroup)
    overrides: dict[str, dict[str, str]] = field(default_factory=dict)
    base_dir: Path = field(default_factory=Path.cwd)
    use_sudo: bool | None = None


def find_config(start: Path | None = None) -> Path:
    """
    Walks upward from start looking for duck.toml.

    Args:
        start: Directory to begin searching from. Defaults to the cwd.

    Returns:
        Path to the discovered duck.toml file.

    Raises:
        ConfigNotFoundError: If no duck.toml is found up to the filesystem root.
    """
    current = (start or Path.cwd()).resolve()
    
    for directory in [current, *current.parents]:
        candidate = directory / CONFIG_FILENAME
        if candidate.is_file():
            return candidate
    
    # Raise an exception
    raise ConfigNotFoundError(f"No {CONFIG_FILENAME} found in '{current}' or any parent directory.")


def load_config(path: Path | None = None) -> DuckSyncConfig:
    """
    Reads and validates a duck.toml file into a DuckSyncConfig.

    Args:
        path: Explicit path to a duck.toml file. Auto discovered when omitted.

    Returns:
        The parsed configuration.

    Raises:
        ConfigParseError: If the file exists but is malformed.
    """
    config_path = path or find_config()

    try:
        raw = tomllib.loads(config_path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as error:
        raise ConfigParseError(f"Invalid TOML in '{config_path}': {error}") from error

    # Get raw data
    dependencies_raw = raw.get("dependencies", {})
    development_raw = raw.get("development", {})
    sync_raw = raw.get("sync", {})

    return DuckSyncConfig(
        dependencies=parse_dependency_group(dependencies_raw),
        development=parse_dependency_group(development_raw),
        overrides=raw.get("overrides", {}),
        base_dir=config_path.parent,
        use_sudo=sync_raw.get("use_sudo"),
    )


def parse_dependency_group(raw: dict) -> DependencyGroup:
    """
    Builds a DependencyGroup from a [dependencies] or [development] table.

    Args:
        raw: The raw dict for that TOML table.

    Returns:
        The parsed DependencyGroup.
    """
    return DependencyGroup(
        python=list(raw.get("python", [])),
        system=list(raw.get("system", [])),
        requirements=raw.get("requirements", ""),
        python_args=list(raw.get("python_args", [])),
        python_package_args=raw.get("python_package_args", {}),
        system_args=list(raw.get("system_args", [])),
        system_package_args=raw.get("system_package_args", {}),
    )
