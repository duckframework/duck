"""
Detects the current operating system and the package manager it favors.
"""

from __future__ import annotations

import os
import shutil
import platform

from pathlib import Path

from duck.cli.commands.sync.exceptions import UnsupportedPlatformError


# Backend names in priority order per OS family, used when several
# package managers could be present on the same machine
LINUX_BACKEND_PRIORITY = ["apt", "dnf", "pacman", "zypper", "apk"]


def is_root() -> bool:
    """
    Checks whether the current process is already running as root.

    Used to skip prefixing install commands with sudo, since sudo is
    unavailable or unnecessary inside most containers that already run
    as root.

    Returns:
        True on POSIX systems running as uid 0. Always False on Windows,
        since sudo does not apply there.
    """
    return hasattr(os, "geteuid") and os.geteuid() == 0


def is_termux() -> bool:
    """
    Checks whether Duck Sync is running inside Termux on Android.

    Termux reports itself as a normal Linux uname, so it needs its own
    check rather than falling through the generic Linux package manager
    detection. It also has no root and no sudo binary.

    Returns:
        True when the Termux environment and pkg command are both present.
    """
    prefix = os.environ.get("PREFIX", "")
    return "com.termux" in prefix and shutil.which("pkg") is not None


def read_linux_distro_id() -> str:
    """
    Reads the distro id from /etc/os-release.

    Returns:
        The lowercase distro id (e.g. "ubuntu", "fedora"), or an empty
        string when the file is unavailable.
    """
    os_release = Path("/etc/os-release")
    
    if not os_release.is_file():
        return ""

    for line in os_release.read_text(encoding="utf-8").splitlines():
        if line.startswith("ID="):
            return line.split("=", 1)[1].strip().strip('"').lower()
    return ""


def detect_os_family(raise_for_unknown: bool = True) -> str:
    """
    Classifies the host machine into a coarse OS family.

    Returns:
        One of "linux", "macos", "windows".
        
    Raises:
        UnsupportedPlatformError: If the platform cannot be classified (only is raise_for_uknown=True).
    """
    system = platform.system().lower()
    
    if system == "linux":
        return "linux"
    
    if system == "darwin":
        return "macos"
    
    if system == "windows":
        return "windows"
    
    if raise_for_unknown:
        raise UnsupportedPlatformError(f"Unrecognized platform: '{system}'")
    
    return system


def detect_backend_name() -> str:
    """
    Picks the best matching system package manager for this machine.

    Returns:
        A backend identifier such as "apt", "brew", "dnf", "pacman",
        "choco", or "termux" that `backends.get_backend` understands.

    Raises:
        UnsupportedPlatformError: If no known package manager is found.
    """
    # Termux reports as Linux but has no root and its own package tool,
    # so it must be checked before the generic Linux family below
    if is_termux():
        return "termux"

    # Detect os family
    family = detect_os_family()

    if family == "macos":
        if shutil.which("brew"):
            return "brew"
        
        # Raise an exception
        raise UnsupportedPlatformError("Homebrew not found. Install it from https://brew.sh first.")

    if family == "windows":
        if shutil.which("choco"):
            return "choco"
        
        # Raise an exception
        raise UnsupportedPlatformError("Chocolatey not found. Install it from https://chocolatey.org first.")

    # Linux: prefer whichever package manager is actually on PATH
    binary_by_backend = {
        "apt": "apt-get",
        "dnf": "dnf",
        "pacman": "pacman",
        "zypper": "zypper",
        "apk": "apk",
    }
    
    for backend in LINUX_BACKEND_PRIORITY:
        if shutil.which(binary_by_backend[backend]):
            return backend

    raise UnsupportedPlatformError("No supported Linux package manager found on PATH.")
