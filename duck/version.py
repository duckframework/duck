"""
Version information for the Duck package.
"""

import sys


# Package version
version_info = (2, 2, 0)
version = ".".join(map(str, version_info))

# Server identification string
python_version = ".".join(map(str, sys.version_info[:3]))
server_version = f"Duck/{version} Python/{python_version}"

# Public package version
__version__ = version


# Expose some tools
__all__ = [
    "version_info",
    "version",
    "server_version",
    "__version__",
]
