"""
Module containing the SyncCommand class for Duck project dependency sync.
"""
import shlex
import click

from pathlib import Path

from duck.logging import console
from duck.version import python_version
from duck.cli.commands.sync.exceptions import DuckSyncError
from duck.cli.commands.sync.sync import DuckSync, SyncReport
from duck.cli.commands.sync.platform_utils import (
    detect_os_family,
    is_termux,
    is_root,
)


class SyncCommand:
    """
    CLI command group for syncing project dependencies from duck.toml.
    """
    
    @classmethod
    def print_header(
        cls,
        distro: str,
        package_manager: str,
        py_package_manager: str,
        config: str,
        is_root: bool,
        py_version: str,
    ) -> None:
        """
        Prints the detected system environment and selected backend.
    
        Args:
            distro: Detected operating system distribution.
            package_manager: Package manager backend selected by Duck Sync.
            py_package_manager: Python package manager backend selected by Duck Sync.
            config: The config path or name relative to cwd.
            is_root: Whether we are in root environment.
            py_version: The python version.
        """
        console.log(f" Python version: {py_version}", level=console.DEBUG)
        console.log(f" Environment: {distro}", level=console.DEBUG)
        console.log(f" Root: {is_root}", level=console.DEBUG)
        console.log(f" Backend: {package_manager}", level=console.DEBUG)
        console.log(f" Python backend: {py_package_manager}", level=console.DEBUG)
        console.log(f" Configuration: {config}\n", level=console.DEBUG)
        
    @classmethod
    def print_report(cls, report: SyncReport):
        """
        Prints a sync run summary to the console.
    
        Args:
            report: The report returned by DuckSync.run().
        """
        total = (
            len(report.already_satisfied)
            + len(report.installed)
            + len(report.failed)
        )
    
        console.log_raw(
            f"Sync complete: {total} dependencies checked",
            custom_color=console.Fore.CYAN,
        )
    
        if report.already_satisfied:
            console.log_raw(
                f"\nAlready satisfied ({len(report.already_satisfied)}):",
                level=console.DEBUG,
            )
    
            for package in report.already_satisfied:
                console.log_raw(
                    f"  ✓ {package}",
                    custom_color=console.Fore.GREEN,
                )
    
        if report.installed:
            console.log_raw(
                f"\nInstalled ({len(report.installed)}):",
                level=console.DEBUG,
            )
    
            for package in report.installed:
                console.log_raw(
                    f"  + {package}",
                    custom_color=console.Fore.GREEN,
                )
    
        if report.failed:
            console.log_raw(
                f"\nFailed ({len(report.failed)}):",
                level=console.ERROR,
            )
    
            for package, reason in report.failed.items():
                console.log_raw(
                    f"  ✗ {package}: {reason}",
                    level=console.ERROR,
                )
    
        if report.ok():
            console.log_raw(
                "\n✓ All dependencies are synced.",
                custom_color=console.Fore.GREEN,
            )
        else:
            console.log_raw(
                "\n✗ Sync completed with errors.",
                level=console.ERROR,
            )
    
    @classmethod
    def main(
        cls,
        include_dev: bool = False,
        dev_only: bool = False,
        dry_run: bool = False,
        config: str = "",
        pip_args: str = "",
        system_args: str = "",
        sudo: bool | None = None,
        backend: str = "",
    ):
        """
        Run a full dependency sync using duck.toml.

        Args:
            include_dev:
                Whether to also sync the [development] group.
            
            dev_only:
                Whether to also sync the [development] group.
                
            dry_run:
                Print planned installs without changing the system.
                
            config:
                Explicit path to duck.toml, auto discovered when empty.
            
            pip_args:
                Extra args appended to every pip/uv install, e.g.
                "--extra-index-url https://download.pytorch.org/whl/cu118".
            
            system_args:
                Extra args appended to every system package install,
                e.g. "--no-install-recommends".
            
            sudo:
                Force sudo on or off for system installs. Left as None,
                duck.toml's [sync] setting is used, falling back to
                auto-detect (skip sudo when already root).
            
            backend:
                Override the auto-detected system package manager. Accepts
                a known identifier (``apt``, ``brew``, ``pacman`` …) or a raw
                install command such as ``"some_command -i"``. Left empty, the
                backend is detected from the host platform.
        """
        from duck.cli.commands.sync.config import CONFIG_FILENAME
        
        config_path = Path(config) if config else None

        try:
            duck_sync = DuckSync(
                config_path=config_path,
                include_dev=include_dev,
                dev_only=dev_only,
                dry_run=dry_run,
                python_extra_args=shlex.split(pip_args),
                system_extra_args=shlex.split(system_args),
                use_sudo=sudo,
                force_backend=backend or None,
            )
            
            # Print header first
            distro = detect_os_family(raise_for_unknown=False)
            
            if is_termux():
                distro = f"{distro} [Termux]".capitalize()
            
            cls.print_header(
                distro=distro,
                package_manager=duck_sync.system_backend.base_command[0],
                py_package_manager=duck_sync.python_backend.base_command[0],
                config=config_path or CONFIG_FILENAME,
                is_root=is_root(),
                py_version=python_version,
            )
            
            # Generate report
            report = duck_sync.run()
            
        except DuckSyncError as error:
            console.log(f"duck sync failed: {error}", level=console.ERROR)
            console.log_exception(error)
            return

        cls.print_report(report)

        if not report.ok():
            console.log_raw("One or more dependencies failed.", level=console.WARNING)
