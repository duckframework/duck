"""
Thin wrappers around real package managers. Each backend only knows how
to check and install packages for one tool, so Duck Sync stays a thin
coordination layer instead of a package manager of its own.
"""

from __future__ import annotations

import shutil
import subprocess

from abc import ABC, abstractmethod
from pathlib import Path

from duck.cli.commands.sync.exceptions import InstallationError
from duck.logging import console


class PackageBackend(ABC):
    """
    Base interface every system package manager wrapper implements.

    Args:
        use_sudo: Whether to prefix install commands with sudo. Backends
            that never use sudo (brew, choco) ignore this flag.
    """
    name: str
    base_command: list[str]
    sudo_capable: bool = True

    def __init__(
        self,
        use_sudo: bool = True,
        on_install_started: Callable = None,
        on_install_finished: Callable = None,
        on_install_failed: Callable = None,
    ):
        self.use_sudo = use_sudo
        self.on_install_started_callback = on_install_started
        self.on_install_finished_callback = on_install_finished
        self.on_install_failed_callback = on_install_failed

    @property
    def install_command(self) -> list[str]:
        """
        Returns:
            The install command prefix, with sudo prepended only when
            this backend supports it and use_sudo is enabled.
        """
        if self.sudo_capable and self.use_sudo:
            return ["sudo", *self.base_command]
        return list(self.base_command)

    @abstractmethod
    def is_installed(self, package: str) -> bool:
        """
        Checks whether a package is already present on the system.

        Args:
            package: Backend-specific package name.

        Returns:
            True if the package appears to already be installed.
        """
        pass

    def on_install_started(self, package: str) -> None:
        """
        Called immediately before a dependency installation begins.

        Args:
            package: The package about to be installed.
        """
        self.on_install_started_callback(package)

    def on_install_finished(self, package: str) -> None:
        """
        Called after a dependency has been installed successfully.

        Args:
            package: The package that was installed.
        """
        self.on_install_finished_callback(package)

    def on_install_failed(self, package: str, reason: str) -> None:
        """
        Called when a dependency fails to install.

        Args:
            package: The package that failed.
            reason: Human-readable failure reason.
        """
        self.on_install_failed_callback(package, reason)
    
    def install(
        self,
        package: str,
        extra_args: list[str] | None = None,
        dry_run: bool = False,
    ) -> None:
        """
        Installs a package using this backend's native command.

        Args:
            package:
                Backend-specific package name. May contain multiple
                space-separated packages (e.g. "gdal-bin libgdal-dev").
            
            extra_args:
                Extra flags passed straight through to the
                underlying package manager, e.g. ["--no-install-recommends"].
            
            dry_run:
                When True, only prints the command without running it.

        Raises:
            InstallationError: If the install command exits non-zero.
        """
        command = [*self.install_command, *(extra_args or []), *package.split()]
        
        if dry_run:
            console.log_raw(f"[dry-run] {' '.join(command)}", level=console.DEBUG)
            return
        
        # Run the install command for package
        self.run(command, package)

    def run(self, command: list[str], package: str) -> None:
        """
        Executes an install command and translates failures.

        Args:
            command: Full command line to run.
            package: Name used in the raised error for context.

        Raises:
            InstallationError: If the command fails.
        """
        # Call on_install_started hook
        self.on_install_started(package)
        
        # Create command process
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        
        if process.stdout is None:
            raise RuntimeError("Failed to capture subprocess stdout.")
        
        for line in process.stdout:
            console.log_raw(line, end="")
        
        # Log a separator blank line
        console.log_raw("") if process.stdout else None
        
        # Wait for process to finish execution
        returncode = process.wait()
        
        if returncode != 0:
            error = (process.stderr.strip()  if process.stderr else None ) or "unknown error"
            
            # Call on_install_failed hook
            self.on_install_failed(package, error)
            
            # Raise the installation exception
            raise InstallationError(package, error)
            
        else:
            # Call on_install_finished hook
            self.on_install_finished(package)


class AptBackend(PackageBackend):
    """
    Debian/Ubuntu package manager backend.
    """
    name = "apt"
    base_command = ["apt-get", "install", "-y"]

    def is_installed(self, package: str) -> bool:
        for single_package in package.split():
            result = subprocess.run(["dpkg", "-s", single_package], capture_output=True)
            if result.returncode != 0:
                return False
        return True


class BrewBackend(PackageBackend):
    """
    Homebrew backend for macOS.
    """
    name = "brew"
    base_command = ["brew", "install"]
    sudo_capable = False

    def is_installed(self, package: str) -> bool:
        for single_package in package.split():
            result = subprocess.run(["brew", "list", single_package], capture_output=True)
            if result.returncode != 0:
                return False
        return True


class DnfBackend(PackageBackend):
    """
    Fedora/RHEL package manager backend.
    """
    name = "dnf"
    base_command = ["dnf", "install", "-y"]

    def is_installed(self, package: str) -> bool:
        for single_package in package.split():
            result = subprocess.run(["rpm", "-q", single_package], capture_output=True)
            if result.returncode != 0:
                return False
        return True


class PacmanBackend(PackageBackend):
    """
    Arch Linux package manager backend.
    """
    name = "pacman"
    base_command = ["pacman", "-S", "--noconfirm"]

    def is_installed(self, package: str) -> bool:
        for single_package in package.split():
            result = subprocess.run(["pacman", "-Q", single_package], capture_output=True)
            if result.returncode != 0:
                return False
        return True


class ChocoBackend(PackageBackend):
    """
    Chocolatey backend for Windows.
    """
    name = "choco"
    base_command = ["choco", "install", "-y"]
    sudo_capable = False

    def is_installed(self, package: str) -> bool:
        for single_package in package.split():
            result = subprocess.run(
                ["choco", "list", "--local-only", single_package],
                capture_output=True,
                text=True,
            )
            if single_package.lower() not in result.stdout.lower():
                return False
        return True


class TermuxBackend(PackageBackend):
    """
    Backend for Termux on Android, which wraps apt/dpkg through its own
    pkg command and runs as an unprivileged user with no sudo binary.
    """
    name = "termux"
    base_command = ["pkg", "install", "-y"]
    sudo_capable = False

    def is_installed(self, package: str) -> bool:
        for single_package in package.split():
            result = subprocess.run(["dpkg", "-s", single_package], capture_output=True)
            if result.returncode != 0:
                return False
        return True


class PythonBackend(PackageBackend):
    """
    Installs python packages, preferring uv when present since it is
    faster and already used across Duck Framework projects.
    """
    name = "python"
    
    def __init__(self, use_sudo: bool = False, **kwargs):
        super().__init__(use_sudo=False, **kwargs)
        self.tool = "uv" if shutil.which("uv") else "pip"

    @property
    def base_command(self) -> list[str]:
        """
        Returns:
            The install command prefix for whichever tool is active,
            e.g. ["uv", "pip", "install"] or ["pip", "install"].
        """
        return ["uv", "pip", "install"] if self.tool == "uv" else ["pip", "install"]
        
    def is_installed(self, package: str) -> bool:
        """
        Check whether a Python package is installed and satisfies the
        requested version constraint.
    
        Args:
            package:
                Package requirement string, e.g. ``"django>=5.0"`` or
                ``"requests[socks]"``.
    
        Returns:
            True if the package is installed and satisfies the requirement.
        """
        from importlib import metadata
        from packaging.requirements import Requirement
    
        try:
            requirement = Requirement(package)
            distribution = metadata.distribution(requirement.name)
    
        except (metadata.PackageNotFoundError, ValueError):
            return False
    
        # No version constraint means existence is enough
        if not requirement.specifier:
            return True
    
        return distribution.version in requirement.specifier
        
    def install_requirements(
        self,
        path: Path,
        extra_args: list[str] | None = None,
        dry_run: bool = False,
    ) -> None:
        """
        Installs every package listed in a requirements.txt file.

        Args:
            path: Resolved path to the requirements file.
            extra_args: Extra flags such as ["--no-cache-dir"].
            dry_run: When True, only prints the command without running it.

        Raises:
            InstallationError: If the install command exits non-zero.
        """
        command = [*self.base_command, "-r", str(path), *(extra_args or [])]
        
        if dry_run:
            console.log_raw(f"[dry-run] {' '.join(command)}", level=console.DEBUG)
            return
            
        # Run the command
        self.run(command, package=str(path))
        

class CustomBackend(PackageBackend):
    """
    Escape hatch for package managers not natively supported by Duck Sync.

    Accepts any install command string such as ``"nix-env -iA nixpkgs"`` or
    ``"some_command -i"``. The package name is appended as a trailing
    positional argument when :meth:`install` is called.

    ``is_installed`` always returns ``False`` so every package is attempted
    on every run. Override ``is_installed`` by subclassing if you need a
    smarter check.

    Args:
        command:
            Shell-style install command prefix, e.g. ``"brew install"``
            or ``"some_command -i"``. Split with :func:`shlex.split`.
        
        use_sudo:
            Whether to prepend ``sudo`` to the resolved command. Only
            applied when :attr:`sudo_capable` is ``True`` on this instance.
        
        sudo_capable:
            Whether the custom command supports sudo. Defaults to
            ``True`` so callers can opt in or out explicitly.
    """
    name = "custom"

    def __init__(
        self,
        command: str,
        use_sudo: bool = False,
        sudo_capable: bool = True,
        **kwargs,
    ):
        import shlex as _shlex

        super().__init__(use_sudo=use_sudo, **kwargs)
        self.sudo_capable = sudo_capable
        self.base_command = _shlex.split(command)

    def is_installed(self, package: str) -> bool:
        """
        Args:
            package: Package name (unused; always returns False).

        Returns:
            Always ``False``; the custom backend never skips an install.
        """
        return False


# Register backends
BACKEND_REGISTRY: dict[str, type[PackageBackend]] = {
    "apt": AptBackend,
    "brew": BrewBackend,
    "dnf": DnfBackend,
    "pacman": PacmanBackend,
    "choco": ChocoBackend,
    "termux": TermuxBackend,
    "python": PythonBackend,
}


def get_backend(name: str, use_sudo: bool = True, **backend_kwargs) -> PackageBackend:
    """
    Instantiates a system package backend by name or custom command string.

    When `name` is a key in `BACKEND_REGISTRY` the matching built-in
    backend is returned. Otherwise the value is treated as a raw shell-style
    install command and wrapped in a `CustomBackend`, letting callers
    force any arbitrary tool:
    
    ```python
        get_backend("apt")             # built-in AptBackend
        get_backend("brew")                # built-in BrewBackend
        get_backend("some_command -i")     # CustomBackend("some_command -i")
        get_backend("nix-env -iA nixpkgs") # CustomBackend("nix-env -iA nixpkgs")
    ```
    
    Args:
        name:
            Backend identifier (``"apt"``, ``"brew"`` …) **or** a
            shell-style install command prefix (``"some_command -i"``).
        
        use_sudo:
            Whether install commands should be prefixed with sudo.
            Ignored by built-in backends that are never sudo-capable, and
            forwarded to :class:`CustomBackend` for raw commands.
        
        **backend_kwargs:
            Extra keyword arguments to provide to backend class.
            
    Returns:
        A ready-to-use :class:`PackageBackend` instance.
    """
    if name in BACKEND_REGISTRY:
        return BACKEND_REGISTRY[name](use_sudo=use_sudo, **backend_kwargs)
        
    # Return the custom backend.
    return CustomBackend(command=name, use_sudo=use_sudo, **backend_kwargs)
