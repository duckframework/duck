"""
Orchestrates a full duck sync run: load config, detect the environment,
diff installed vs required dependencies, then install what is missing.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from duck.cli.commands.sync.backends import PythonBackend, get_backend
from duck.cli.commands.sync.config import DependencyGroup, DuckSyncConfig, load_config
from duck.cli.commands.sync.exceptions import InstallationError
from duck.cli.commands.sync.platform_utils import detect_backend_name, is_root
from duck.cli.commands.sync.registry import resolve_package_name
from duck.logging import console


@dataclass
class SyncReport:
    """
    Summary of what a sync run found and did.

    Args:
        already_satisfied: Dependencies that were already installed.
        installed: Dependencies successfully installed this run.
        failed: Mapping of dependency name to failure reason.
    """
    already_satisfied: list[str] = field(default_factory=list)
    installed: list[str] = field(default_factory=list)
    failed: dict[str, str] = field(default_factory=dict)

    def ok(self) -> bool:
        """
        Returns:
            True when nothing failed to install.
        """
        return not self.failed


class DuckSync:
    """
    Reads a project's duck.toml and brings the local environment in
    line with it.

    Args:
        config_path:
            Explicit duck.toml path, auto discovered when omitted.
        
        include_dev:
            Whether to also sync the [development] group.
        
        dev_only:
            Whether to also sync the [development] group.
            
        dry_run:
            When True, prints planned actions without installing.
        
        python_extra_args:
            Extra CLI args appended on top of duck.toml's
            python_args, useful for one-off runs (e.g. --extra-index-url).
        
        system_extra_args:
            Extra CLI args appended on top of duck.toml's
            system_args.
        
        use_sudo:
            Whether system installs should be prefixed with sudo.
            None defers to duck.toml's [sync] setting, which itself
            defaults to auto-detect (skip sudo when already root).
        
        force_backend:
            Override auto-detection with a specific backend.
            Accepts any value recognised by :func:`~duck_sync.backends.get_backend`:
            a known identifier (``"apt"``, ``"brew"``, ``"pacman"`` …) **or** a
            raw shell-style install command (``"some_command -i"``).
            When omitted, the backend is detected from the host platform.
    """

    def __init__(
        self,
        config_path: Path | None = None,
        include_dev: bool = False,
        dev_only: bool = False,
        dry_run: bool = False,
        python_extra_args: list[str] | None = None,
        system_extra_args: list[str] | None = None,
        use_sudo: bool | None = None,
        force_backend: str | None = None,
    ) -> None:
        
        # Setup some hooks
        hooks = {
            "on_install_started": self.on_install_started,
            "on_install_finished": self.on_install_finished,
            "on_install_failed": self.on_install_failed,
        }
        
        # Set some attributes
        self.config: DuckSyncConfig = load_config(config_path)
        self.include_dev = include_dev
        self.dev_only = dev_only
        self.dry_run = dry_run
        self.python_extra_args = python_extra_args or []
        self.system_extra_args = system_extra_args or []
        self.system_backend_name = force_backend or detect_backend_name()
        self.system_backend = get_backend(self.system_backend_name, use_sudo=self.resolve_use_sudo(use_sudo), **hooks)
        self.python_backend = get_backend("python", **hooks)
        
    def on_install_started(self, package: str) -> None:
        """
        Called immediately before a dependency installation begins.

        Args:
            package: The package about to be installed.
        """
        console.log(f"Installing package: {package}\n", level=console.DEBUG)

    def on_install_finished(self, package: str) -> None:
        """
        Called after a dependency has been installed successfully.

        Args:
            package: The package that was installed.
        """
        console.log(f"Installed package: {package}\n", level=console.DEBUG)

    def on_install_failed(self, package: str, reason: str) -> None:
        """
        Called when a dependency fails to install.

        Args:
            package: The package that failed.
            reason: Human-readable failure reason.
        """
        console.log(f"Installation failed for package: {package}\n", level=console.ERROR)
    
    def resolve_use_sudo(self, use_sudo: bool | None) -> bool:
        """
        Decides whether sudo should prefix system install commands.

        Precedence: an explicit use_sudo argument wins, then duck.toml's
        [sync] use_sudo setting, then auto-detection based on the
        current user.

        Args:
            use_sudo: The explicit override passed to DuckSync, if any.

        Returns:
            True if install commands should be prefixed with sudo.
        """
        if use_sudo is not None:
            return use_sudo
        
        if self.config.use_sudo is not None:
            return self.config.use_sudo
        
        return not is_root()

    def active_groups(self) -> list[DependencyGroup]:
        """
        Returns:
            The active dependency groups based on the selected mode.
        """
        if self.dev_only:
            return [self.config.development]
        
        if self.include_dev:
            return [self.config.dependencies, self.config.development]
        
        return [self.config.dependencies]

    def collect_targets(self) -> tuple[list[str], list[str]]:
        """
        Flattens the active groups' python and system package lists.

        Returns:
            A (python_packages, system_packages) tuple with duplicates removed.
        """
        python_packages: list[str] = []
        system_packages: list[str] = []

        for group in self.active_groups():
            python_packages += group.python
            system_packages += group.system

        # Preserve order while dropping duplicates
        return list(dict.fromkeys(python_packages)), list(
            dict.fromkeys(system_packages)
        )

    def python_args_for(self, package: str) -> list[str]:
        """
        Builds the full extra-args list for one python package install.

        Order is duck.toml group args, then that package's own override,
        then CLI-supplied args, so CLI flags always win last.

        Args:
            package: Python package name.

        Returns:
            The merged list of extra CLI args to pass to pip/uv.
        """
        args: list[str] = []
        
        for group in self.active_groups():
            args += group.python_args
            args += group.python_package_args.get(package, [])
        
        # Extend args
        args += self.python_extra_args
        
        # Return final args
        return args

    def system_args_for(self, generic_name: str) -> list[str]:
        """
        Builds the full extra-args list for one system package install.

        Args:
            generic_name: Name as written in duck.toml, e.g. "gdal".

        Returns:
            The merged list of extra CLI args to pass to the OS package manager.
        """
        args: list[str] = []
        
        for group in self.active_groups():
            args += group.system_args
            args += group.system_package_args.get(generic_name, [])
       
        # Extend args
        args += self.system_extra_args
        
        # Return final args
        return args
        
    def sync_system_package(self, generic_name: str, report: SyncReport) -> None:
        """
        Ensures a single system package is installed, updating report in place.

        Args:
            generic_name: Name as written in duck.toml, e.g. "gdal".
            report: Report accumulator for this sync run.
        """
        resolved_name = resolve_package_name(generic_name, self.system_backend_name, self.config.overrides)
        
        if self.system_backend.is_installed(resolved_name):
            report.already_satisfied.append(generic_name)
            return

        try:
            # Install the system level package
            self.system_backend.install(
                resolved_name,
                extra_args=self.system_args_for(generic_name),
                dry_run=self.dry_run,
            )
            
            # Append package to installed packages
            report.installed.append(generic_name)
            
        except InstallationError as error:
            report.failed[generic_name] = error.reason

    def sync_python_package(self, package: str, report: SyncReport) -> None:
        """
        Ensures a single python package is installed, updating report in place.

        Args:
            package: Python package name.
            report: Report accumulator for this sync run.
        """
        if self.python_backend.is_installed(package):
            report.already_satisfied.append(f"[python] {package}")
            return

        try:
            # Install python package
            self.python_backend.install(package, extra_args=self.python_args_for(package), dry_run=self.dry_run)
            
            # Append installed package
            report.installed.append(package)
            
        except InstallationError as error:
            report.failed[package] = error.reason
            
    def sync_requirements_file(self, group: DependencyGroup, report: SyncReport) -> None:
        """
        Installs a group's requirements.txt, if one is declared.

        pip/uv already skip packages that satisfy pinned versions, so this
        always runs rather than pre-checking each line individually.

        Args:
            group: The dependency group that may declare a requirements file.
            report: Report accumulator for this sync run.
        """
        if not group.requirements:
            return

        path = (self.config.base_dir / group.requirements).resolve()
        label = f"requirements ({path.name})"

        if not path.is_file():
            report.failed[label] = f"file not found: {path}"
            return

        try:
            self.python_backend.install_requirements(
                path,
                extra_args=group.python_args + self.python_extra_args,
                dry_run=self.dry_run,
            )
            
            # Append the requirements file to installed
            report.installed.append(label)
            
        except InstallationError as error:
            report.failed[label] = error.reason

    def run(self) -> SyncReport:
        """
        Executes the full sync: system packages, then python packages,
        then requirements files.

        Returns:
            A SyncReport describing what happened.
        """
        report = SyncReport()
        
        # Resolve packages
        python_packages, system_packages = self.collect_targets()
        
        for package in system_packages:
            self.sync_system_package(package, report)
        
        for package in python_packages:
            self.sync_python_package(package, report)
            
        for group in self.active_groups():
            self.sync_requirements_file(group, report)
            
        # Return the final report
        return report
