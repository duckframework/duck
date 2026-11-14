"""
Storage backend utilities.
"""
from typing import Any

from duck.contrib.storage.backends import StorageBackend
from duck.contrib.storage.backends.local import LocalStorage
from duck.contrib.storage.backends.s3 import S3Storage
from duck.contrib.storage.backends.cloudflare import CloudflareR2Storage


BACKEND_REGISTRY: dict[str, type[StorageBackend]] = {
    "local": LocalStorage,
    "s3": S3Storage,
    "cloudflare_r2": CloudflareR2Storage,
}


def register_backend(name: str, backend_class: type[StorageBackend]) -> None:
    """
    Makes a custom backend class available to `create_backend`.

    Args:
        name: Value of the `type` key used in configuration.
        backend_class: Subclass of StorageBackend.
    """
    BACKEND_REGISTRY[name] = backend_class


def create_backend(config: dict[str, Any]) -> StorageBackend:
    """
    Builds a storage backend from a configuration dictionary.

    Args:
        config: Dictionary with a `type` key naming a registered backend,
            plus the keyword arguments for that backend.

    Returns:
        An initialized StorageBackend.

    Raises:
        ValueError: If the backend type is not registered.
    """
    options = dict(config)
    backend_type = options.pop("type", None)

    if backend_type not in BACKEND_REGISTRY:
        raise ValueError(f"Unknown storage backend type: {backend_type!r}")
    
    return BACKEND_REGISTRY[backend_type](**options)
