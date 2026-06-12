"""
Provides utilities for generating and managing secure secrets and tokens for Duck applications.

This module generates and manages various secrets, including URL-safe tokens, ASCII-based secrets,
and randomized domain names. The secrets are stored in environment variables to ensure they
remain accessible and secure throughout the application lifecycle.

Main Components:
- `generate_secret()`: Generates a URL-safe, cryptographically secure token.
- `generate_ascii_secret()`: Generates a secure ASCII-only token for specific cases.
- `generate_random_domain()`: Provides a randomized domain name for secure communication.
- `get_or_create_secret()`: Retrieves or creates a named secret, persisting it to a secured file.

Environment Variables:
- `DXS`: Stores a URL-safe token, generated if not already set.
- `RXS`: Stores an ASCII-based token, generated if not already set, used in secret headers.
- `DXSD`: Stores a randomized domain name, generated if not already set.

These environment variables are intended to enhance security by obfuscating sensitive values.
When variables are not set initially, secure values are generated and assigned to them dynamically.
"""

import hashlib
import os
import random
import stat
import string
import sys

from pathlib import Path
from duck.utils.rand_domain import generate_random_domain


# Secrets are stored in a .duck directory relative to the project root
SECRETS_DIR = Path(os.environ.get("DUCK_SECRETS_DIR", ".duck/secrets"))
    
# POSIX: owner read+write only (0o600 file, 0o700 dir)
SECRET_FILE_MODE = stat.S_IRUSR | stat.S_IWUSR
SECRET_DIR_MODE = stat.S_IRWXU

IS_WINDOWS = sys.platform == "win32"


def secure_mkdir(path: Path) -> None:
    """
    Creates a directory with the tightest permissions available on the current OS.

    On POSIX systems, the directory is created with mode 0o700 (owner access only).
    On Windows, the directory is created normally and then locked down via icacls,
    removing all inherited and explicit ACEs except for the current user (full control).

    Args:
        path: The directory path to create and secure.

    Raises:
        OSError: If the directory cannot be created or secured.
    """
    path.mkdir(parents=True, exist_ok=True)

    if IS_WINDOWS:
        # Strip inherited permissions and grant the current user full control only
        username = os.environ.get("USERNAME", os.environ.get("USER", ""))
        os.system(f'icacls "{path}" /inheritance:r /grant:r "{username}:(OI)(CI)F" /T /Q')
    else:
        os.chmod(path, SECRET_DIR_MODE)


def secure_write(path: Path, secret: str) -> None:
    """
    Writes a secret to disk atomically with restricted file permissions.

    The secret is written to a temporary file first, permissions are applied,
    and then the file is renamed to its final path. This prevents any window
    where the file exists with loose permissions.

    On POSIX, the file is set to 0o600 (owner read/write only).
    On Windows, icacls removes all inherited ACEs and grants only the current
    user read/write access.

    Args:
        path: The final destination path for the secret file.
        secret: The secret string to write.

    Raises:
        OSError: If the file cannot be written, secured, or renamed.
    """
    tmp_path = path.with_suffix(".tmp")
    tmp_path.write_text(secret, encoding="utf-8")

    if IS_WINDOWS:
        username = os.environ.get("USERNAME", os.environ.get("USER", ""))
        os.system(f'icacls "{tmp_path}" /inheritance:r /grant:r "{username}:(R,W)" /Q')
    else:
        os.chmod(tmp_path, SECRET_FILE_MODE)

    tmp_path.rename(path)


def secure_read(path: Path) -> str:
    """
    Enforces correct permissions on an existing secret file then reads it.

    This corrects permissions in case the file was created externally or copied
    without the expected ACL/mode, ensuring every read is from a locked-down file.

    Args:
        path: Path to the secret file to read.

    Returns:
        str: The secret value with surrounding whitespace stripped.

    Raises:
        OSError: If permissions cannot be applied or the file cannot be read.
    """
    if IS_WINDOWS:
        username = os.environ.get("USERNAME", os.environ.get("USER", ""))
        os.system(f'icacls "{path}" /inheritance:r /grant:r "{username}:(R,W)" /Q')
    else:
        os.chmod(path, SECRET_FILE_MODE)

    return path.read_text(encoding="utf-8").strip()


def generate_ascii_secret(length: int = 16) -> str:
    """
    Generates a secure random ASCII-only token.

    Uses only letters to ensure compatibility with contexts that require
    plain ASCII, such as secret header construction.

    Args:
        length: Number of characters in the generated token.

    Returns:
        str: A random ASCII letter token of the specified length.
    """
    letters = string.ascii_letters
    return "".join(random.choice(letters) for _ in range(length))


def generate_secret() -> str:
    """
    Generates a secure random URL-safe token.

    Returns:
        str: A URL-safe token for use as a secret.
    """
    randstr = str(random.random())
    return hashlib.md5(randstr.encode("utf-8")).hexdigest()


def get_or_create_secret(name: str, generator: callable = generate_secret) -> str:
    """
    Retrieves a named secret from its persisted file, or creates and stores it.

    Lookup order:
    1. Environment variable matching `name` — returned immediately if set.
    2. Persisted file at `SECRETS_DIR / name` — read, permissions enforced, then returned.
    3. Freshly generated via `generator` — written securely to disk, then returned.

    File security per platform:
    - POSIX: file mode 0o600, directory mode 0o700.
    - Windows: icacls strips all inherited ACEs and grants only the current user R/W on
      files and full control on the directory.

    Args:
        name: Identifier for the secret. Used as the env var key and the filename.
        generator: Callable that returns a new secret string when creation is needed.

    Returns:
        str: The secret value.

    Raises:
        OSError: If the secrets directory or file cannot be created or secured.
    """
    # Fast path — already in the environment from a prior call or external injection
    existing = os.environ.get(name)
    
    if existing:
        return existing

    secret_path = SECRETS_DIR / name

    # Ensure the secrets directory exists and is locked down
    if not SECRETS_DIR.exists():
        secure_mkdir(SECRETS_DIR)
    else:
        # Re-apply permissions in case they drifted (e.g. manual copy, umask change)
        if IS_WINDOWS:
            username = os.environ.get("USERNAME", os.environ.get("USER", ""))
            os.system(
                f'icacls "{SECRETS_DIR}" /inheritance:r '
                f'/grant:r "{username}:(OI)(CI)F" /T /Q'
            )
        else:
            os.chmod(SECRETS_DIR, SECRET_DIR_MODE)

    if secret_path.exists():
        secret = secure_read(secret_path)
    else:
        secret = generator()
        secure_write(secret_path, secret)

    # Cache in the environment for in-process reuse
    os.environ[name] = secret
    return secret


# Check if the environment variable 'DXS' is set, if not, generate a new secret
if not os.environ.get("DXS"):
    # Use a variable name that doesn't make sense for improved security
    DUCK_SECRET = os.environ["DXS"] = get_or_create_secret(name="DXS", generator=generate_secret)
else:
    DUCK_SECRET = os.environ["DXS"]

# Check if the environment variable 'RXS' is set, if not, generate a new secret
if not os.environ.get("RXS"):
    # ASCII only — will be used to construct secret headers
    RAND_SECRET = os.environ["RXS"] = generate_ascii_secret()
else:
    RAND_SECRET = os.environ["RXS"]

# Check if the environment variable 'DXSD' is set, if not, generate a new secret
if not os.environ.get("DXSD"):
    # Use a variable name that doesn't make sense for improved security
    SECRET_DOMAIN = os.environ["DXSD"] = generate_random_domain()
else:
    SECRET_DOMAIN = os.environ["DXSD"]
