"""
Django storage backend that wraps a Duck storage backend.
"""

from __future__ import annotations

from datetime import datetime, timezone

from django.conf import settings
from django.core.files.base import ContentFile, File
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible

from duck.contrib.storage.backends import StorageBackend
from duck.settings.loaded import get_storage_backend


@deconstructible
class DuckStorage(Storage):
    """
    Django storage that delegates every operation to a Duck StorageBackend.

    Django picks the final name, Duck stores the file under exactly that key,
    so Duck's unchanged-file check applies to every save.
    """

    def __init__(
        self,
        backend_key: str,
        file_overwrite: bool = True,
    ) -> None:
        """
        Initializes the wrapper.

        Args:
            backend_key: Key of the Duck to use, defined in STORAGE_BACKENDS in Duck settings e.g., `staticfiles`,  `mediafiles`, `default`, etc.
            file_overwrite: Reuse the requested name instead of adding a random suffix.
        """
        self.backend: StorageBackend = get_storage_backend(backend_key) # type: ignore
        self.file_overwrite = file_overwrite
        self.backend_key = backend_key

    def get_available_name(self, name: str, max_length: int | None = None) -> str:
        """
        Returns the key to save under.

        Args:
            name: Requested name, including the upload_to path.
            max_length: Maximum allowed length of the name.

        Returns:
            The same name when overwriting, otherwise a unique name.
        """
        name = name.replace("\\", "/")

        if self.file_overwrite:
            if max_length is not None and len(name) > max_length:
                raise ValueError(f"Name exceeds max_length ({max_length}): {name}")
            
            return name

        return super().get_available_name(name, max_length)

    def _open(self, name: str, mode: str = "rb") -> File:
        """
        Reads a stored file into a Django File.

        Args:
            name: Backend-relative path.
            mode: Only read modes are supported.

        Returns:
            A File holding the contents.
        """
        if "w" in mode or "a" in mode or "+" in mode:
            raise ValueError("DuckStorage only supports read mode")

        return ContentFile(self.backend.get(name), name=name)

    def _save(self, name: str, content: File) -> str:
        """
        Saves content under the exact name through Duck's pipeline.

        Args:
            name: Final key chosen by Django.
            content: Django File with the data.

        Returns:
            The stored key.
        """
        if hasattr(content, "seek"):
            content.seek(0)

        # Pass bytes so Duck never mistakes content.name for a real source path
        stored = self.backend.save_as(content.read(), name)

        return stored.key

    def delete(self, name: str) -> None:
        """
        Deletes a stored file. Missing files are ignored.

        Args:
            name: Backend-relative path.
        """
        self.backend.delete(name)

    def exists(self, name: str) -> bool:
        """
        Checks whether a file exists.

        Args:
            name: Backend-relative path.

        Returns:
            True if the file exists.
        """
        return self.backend.exists(name)

    def size(self, name: str) -> int:
        """
        Returns the file size in bytes.

        Args:
            name: Backend-relative path.

        Returns:
            The size in bytes.
        """
        return self.backend.size(name)

    def url(self, name: str | None) -> str:
        """
        Returns the public URL of a file.

        Args:
            name: Backend-relative path.

        Returns:
            The URL.
        """
        if not name:
            raise ValueError("The file has no name")

        return self.backend.url_for(name)

    def get_modified_time(self, name: str) -> datetime | None:
        """
        Returns the last modified time.

        Args:
            name: Backend-relative path.

        Returns:
            Aware datetime when USE_TZ is on, otherwise naive local time. 
        """
        timestamp = self.backend.modified_time(name)

        if timestamp is None:
            return None
        
        if settings.USE_TZ:
            return datetime.fromtimestamp(timestamp, tz=timezone.utc)

        return datetime.fromtimestamp(timestamp)

    def listdir(self, path: str) -> tuple[list[str], list[str]]:
        """
        Not supported, Duck backends have no listing primitive.
        """
        raise NotImplementedError("DuckStorage does not support listdir")
