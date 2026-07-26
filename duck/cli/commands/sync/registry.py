"""
Maps generic dependency names (e.g. "gdal") to the package name each
system package manager actually expects. Keeps duck.toml portable across
machines since project authors only write the generic name.
"""

from __future__ import annotations


# Built-in mappings for common native dependencies. Extend via the
# [overrides] section in duck.toml rather than editing this file directly.
SYSTEM_PACKAGE_REGISTRY: dict[str, dict[str, str]] = {
    "build-essential": {
        "apt": "build-essential",
        "brew": "gcc",
        "dnf": "gcc gcc-c++ make",
        "pacman": "base-devel",
        "choco": "visualstudio2022buildtools",
        "termux": "build-essential",
    },
    "python-dev": {
        "apt": "python3-dev",
        "brew": "python3",
        "dnf": "python3-devel",
        "pacman": "python",
        "choco": "python3",
        "termux": "python",
    },
    "openssl": {
        "apt": "libssl-dev",
        "brew": "openssl",
        "dnf": "openssl-devel",
        "pacman": "openssl",
        "choco": "openssl",
        "termux": "openssl",
    },
    "zlib": {
        "apt": "zlib1g-dev",
        "brew": "zlib",
        "dnf": "zlib-devel",
        "pacman": "zlib",
        "choco": "zlib",
        "termux": "zlib",
    },
    "bzip2": {
        "apt": "libbz2-dev",
        "brew": "bzip2",
        "dnf": "bzip2-devel",
        "pacman": "bzip2",
        "choco": "bzip2",
        "termux": "bzip2",
    },
    "libxml2": {
        "apt": "libxml2-dev",
        "brew": "libxml2",
        "dnf": "libxml2-devel",
        "pacman": "libxml2",
        "choco": "libxml2",
        "termux": "libxml2",
    },
    "libxslt": {
        "apt": "libxslt-dev",
        "brew": "libxslt",
        "dnf": "libxslt-devel",
        "pacman": "libxslt",
        "choco": "libxslt",
        "termux": "libxslt",
    },
    "postgresql-client": {
        "apt": "libpq-dev",
        "brew": "libpq",
        "dnf": "libpq-devel",
        "pacman": "postgresql-libs",
        "choco": "postgresql",
        "termux": "postgresql",
    },
    "redis": {
        "apt": "redis-server",
        "brew": "redis",
        "dnf": "redis",
        "pacman": "redis",
        "choco": "redis-64",
        "termux": "redis",
    },
    "gdal": {
        "apt": "gdal-bin libgdal-dev",
        "brew": "gdal",
        "dnf": "gdal gdal-devel",
        "pacman": "gdal",
        "choco": "gdal",
        "termux": "gdal",
    },
    "geos": {
        "apt": "libgeos-dev",
        "brew": "geos",
        "dnf": "geos geos-devel",
        "pacman": "geos",
        "choco": "geos",
        "termux": "libgeos",
    },
    "spatialite": {
        "apt": "libsqlite3-mod-spatialite",
        "brew": "libspatialite",
        "dnf": "libspatialite",
        "pacman": "libspatialite",
        "choco": "spatialite",
        "termux": "libspatialite",
    },
    "jpeg": {
        "apt": "libjpeg-dev",
        "brew": "jpeg",
        "dnf": "libjpeg-turbo-devel",
        "pacman": "libjpeg-turbo",
        "choco": "libjpeg-turbo",
        "termux": "libjpeg-turbo",
    },
    "libpng": {
        "apt": "libpng-dev",
        "brew": "libpng",
        "dnf": "libpng-devel",
        "pacman": "libpng",
        "choco": "libpng",
        "termux": "libpng",
    },
    "libwebp": {
        "apt": "libwebp-dev",
        "brew": "webp",
        "dnf": "libwebp-devel",
        "pacman": "libwebp",
        "choco": "webp",
        "termux": "libwebp",
    },
    "libtiff": {
        "apt": "libtiff-dev",
        "brew": "libtiff",
        "dnf": "libtiff-devel",
        "pacman": "libtiff",
        "choco": "libtiff",
        "termux": "libtiff",
    },
    "freetype": {
        "apt": "libfreetype-dev",
        "brew": "freetype",
        "dnf": "freetype-devel",
        "pacman": "freetype2",
        "choco": "freetype",
        "termux": "freetype",
    },
    "ffmpeg": {
        "apt": "ffmpeg",
        "brew": "ffmpeg",
        "dnf": "ffmpeg-free",
        "pacman": "ffmpeg",
        "choco": "ffmpeg",
        "termux": "ffmpeg",
    },
    "postfix": {
        "apt": "postfix",
        "brew": "postfix",
        "dnf": "postfix",
        "pacman": "postfix",
        "choco": "postfix",
        "termux": "postfix",
    },
}


def resolve_package_name(
    generic_name: str, backend: str, overrides: dict[str, dict[str, str]]
) -> str:
    """
    Finds the correct package name for a given backend.

    Args:
        generic_name:
            The name written in duck.toml, e.g. "gdal".
        
        backend:
            The active backend identifier, e.g. "apt".
        
        overrides:
            Project-supplied overrides from duck.toml's
            [overrides] section, checked before the built-in registry.

    Returns:
        The backend-specific package name. Falls back to generic_name
        unchanged when no mapping is known, since many packages share
        the same name across managers (e.g. "ffmpeg").
    """
    project_override = overrides.get(generic_name, {}).get(backend)
    
    if project_override:
        return project_override

    # Try resolving builtin package backend name
    built_in = SYSTEM_PACKAGE_REGISTRY.get(generic_name, {}).get(backend)
    
    if built_in:
        return built_in

    # Returns generic name
    return generic_name
