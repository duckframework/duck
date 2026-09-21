"""
Loads and validates the native configuration in duck.toml.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

try:
    import tomllib
except ImportError:
    import tomli as tomllib

from duck.cli.commands.sync.config import (
    DuckSyncConfig,
    find_config,
    load_config as load_sync_config,
    merge_dependencies,
)


@dataclass
class AndroidNativeConfig:
    """
    Android native configuration.

    Args:
        deps:
            Dependencies required by Android builds and runtime.

        dev_deps:
            Dependencies required only during Android development.
    """

    deps: list[str] = field(default_factory=list)
    dev_deps: list[str] = field(default_factory=list)


@dataclass
class NativeConfig:
    """
    Native application configuration.

    Args:
        platforms:
            Native platforms enabled for the project.

        android:
            Android native configuration.
    """

    platforms: list[str] = field(default_factory=list)
    android: AndroidNativeConfig = field(
        default_factory=AndroidNativeConfig
    )


@dataclass
class DuckNativeConfig(DuckSyncConfig):
    """
    Duck project configuration extended with native settings.

    Args:
        native:
            Native application configuration.
    """

    native: NativeConfig = field(default_factory=NativeConfig)


def load_config(path: Path | None = None) -> DuckNativeConfig:
    """
    Reads duck.toml into a DuckNativeConfig.

    Existing Duck Sync configuration and dependency handling are reused.
    Native dependencies are automatically added to the appropriate
    system dependency groups.

    Args:
        path:
            Explicit path to duck.toml. Auto discovered when omitted.

    Returns:
        The parsed native configuration.
    """
    config_path = path or find_config()

    sync_config = load_sync_config(config_path)

    raw = tomllib.loads(config_path.read_text(encoding="utf-8"))
    native_raw = raw.get("native", {})

    native = NativeConfig(
        platforms=list(native_raw.get("platforms", [])),
    )

    if "android" in native.platforms:
        android_raw = native_raw.get("android", {})

        native.android = AndroidNativeConfig(
            deps=list(android_raw.get("deps", [])),
            dev_deps=list(android_raw.get("dev_deps", [])),
        )

    # Native runtime dependencies are required in both environments.
    sync_config.dependencies.system = merge_dependencies(
        sync_config.dependencies.system,
        native.android.deps,
    )

    sync_config.development.system = merge_dependencies(
        sync_config.development.system,
        native.android.deps,
    )

    # Native development dependencies are only required in development.
    sync_config.development.system = merge_dependencies(
        sync_config.development.system,
        native.android.dev_deps,
    )

    return DuckNativeConfig(
        dependencies=sync_config.dependencies,
        development=sync_config.development,
        overrides=sync_config.overrides,
        base_dir=sync_config.base_dir,
        use_sudo=sync_config.use_sudo,
        native=native,
    )
