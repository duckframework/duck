"""
Local storage backend.
"""

import hashlib

import os
from typing import Any
from pathlib import Path

from duck.contrib.sync import ensure_async
from duck.contrib.storage.backends import (
    StorageBackend,
    UploadContext,
    ProgressReporter,
    iter_chunks,
    async_iter_chunks,
)
from duck.utils.fileio import FileIOStream, AsyncFileIOStream
from duck.utils.caching import InMemoryCache


FILE_CACHE = InMemoryCache(maxkeys=1024)


class LocalStorage(StorageBackend):
    """
    Stores files on the local filesystem through FileIOStream.

    Useful for development or for servers that expose the directory directly.
    Writes go through FileIOStream so the shared read cache stays consistent,
    and progress is reported per chunk.
    """

    def __init__(self, root: str | Path, base_url: str = "/media", **kwargs: Any) -> None:
        """
        Initializes the local backend.

        Args:
            root: Directory where files are written.
            base_url: URL prefix that the web server maps to ``root``.
            **kwargs: Extra arguments passed to StorageBackend.
        """
        super().__init__(**kwargs)

        # Set some attributes
        self.root = Path(root)
        self.base_url = base_url.rstrip("/")

    def put(self, key: str, context: UploadContext, reporter: ProgressReporter) -> None:
        """
        Writes the payload to disk through FileIOStream, creating parent directories.

        Args:
            key: Backend-relative path.
            context: Final upload state. Only the payload is written.
            reporter: Progress reporter advanced after each chunk.
        """
        path = self.root / key
        
        # Make directory
        path.parent.mkdir(parents=True, exist_ok=True)

        # Write chunk by chunk so progress is reported
        stream = FileIOStream(str(path), mode="wb", open_now=True, cache_backend=FILE_CACHE)

        try:
            for chunk in iter_chunks(context.payload, self.chunk_size, reporter):
                stream.write(chunk)
            
            # Change mtime if provided.
            if context.source_mtime is not None:
                os.utime(path, times=(context.source_mtime, context.source_mtime))

        finally:
            stream.close()

    async def async_put(self, key: str, context: UploadContext, reporter: ProgressReporter) -> None:
        """
        Async write through AsyncFileIOStream, creating parent directories.

        Args:
            key: Backend-relative path.
            context: Final upload state. Only the payload is written.
            reporter: Progress reporter advanced after each chunk.
        """
        path = self.root / key

        # Make directory asynchronously
        await ensure_async(path.parent.mkdir)(parents=True, exist_ok=True)
        
        async with AsyncFileIOStream(str(path), mode="wb", cache_backend=FILE_CACHE, open_now=True) as stream:
            async for chunk in async_iter_chunks(context.payload, self.chunk_size, reporter):
                await stream.write(chunk)

            # Change mtime if provided.
            if context.source_mtime is not None:
                await ensure_async(os.utime)(str(path), times=(context.source_mtime, context.source_mtime))

    def get(self, key: str) -> bytes:
        """
        Reads a file through FileIOStream.

        Args:
            key: Backend-relative path.

        Returns:
            The file contents as bytes.
        """
        stream = FileIOStream(str(self.root / key), open_now=True, cache_backend=FILE_CACHE)

        try:
            return stream.read()
        
        finally:
            stream.close()

    async def async_get(self, key: str) -> bytes:
        """
        Async read through AsyncFileIOStream.

        Args:
            key: Backend-relative path.

        Returns:
            The file contents as bytes.
        """
        async with AsyncFileIOStream(str(self.root / key)) as stream:
            return await stream.read()

    def open_stream(self, key: str) -> FileIOStream:
        """
        Opens a stored file for chunked reading. The caller must close it.

        Args:
            key: Backend-relative path.

        Returns:
            An open FileIOStream positioned at the start of the file.
        """
        return FileIOStream(str(self.root / key), open_now=True)

    async def async_open_stream(self, key: str) -> AsyncFileIOStream:
        """
        Async version of ``open_stream``. The caller must close it.

        Args:
            key: Backend-relative path.

        Returns:
            An open AsyncFileIOStream positioned at the start of the file.
        """
        stream = AsyncFileIOStream(str(self.root / key))

        # Open stream
        await stream.async_open()

        # Return the final stream
        return stream

    def delete(self, key: str) -> None:
        """
        Removes a file from disk if it exists.

        Args:
            key: Backend-relative path.
        """
        (self.root / key).unlink(missing_ok=True)

    def exists(self, key: str) -> bool:
        """
        Checks whether a file exists on disk.

        Args:
            key: Backend-relative path.

        Returns:
            True if the file exists, otherwise False.
        """
        return (self.root / key).exists()

    def size(self, key: str) -> int:
        """
        Returns the size of a stored file in bytes using a file stat.

        Args:
            key: Backend-relative path.

        Returns:
            The file size in bytes.

        Raises:
            FileNotFoundError: If the file does not exist.
        """
        path = self.root / key

        # Missing or not a regular file
        if not path.is_file():
            raise FileNotFoundError(key)

        return path.stat().st_size

    def modified_time(self, key: str) -> float:
        """
        Returns the file's mtime from a stat.

        Args:
            key: Backend-relative path.

        Returns:
            Seconds since the epoch.

        Raises:
            FileNotFoundError: If the file does not exist.
        """
        path = self.root / key

        if not path.is_file():
            raise FileNotFoundError(key)

        return path.stat().st_mtime

    def is_unchanged(self, key: str, context: UploadContext) -> bool:
        """
        Compares mtime when clearly newer, then size, then the content hash.

        Args:
            key: Backend-relative path.
            context: Final upload state.

        Returns:
            True if the file on disk has the same content.
        """
        if not self.exists(key):
            return False

        # Trust mtime only when available and clearly newer
        if context.source_mtime is not None:
            stored = self.modified_time(key)

            if stored is not None and stored == context.source_mtime:
                return True

        if self.size(key) != len(context.payload):
            return False
        
        # Same size, confirm by hash
        return hashlib.sha256(self.get(key)).hexdigest() == context.sha256

    async def async_is_unchanged(self, key: str, context: UploadContext) -> bool:
        """
        Async version of ``is_unchanged``.

        Args:
            key: Backend-relative path.
            context: Final upload state.

        Returns:
            True if the file on disk has the same content.
        """
        if not await self.async_exists(key):
            return False

        # Trust mtime only when available and clearly newer
        if context.source_mtime is not None:
            stored = await self.async_modified_time(key)

            if stored is not None and stored == context.source_mtime:
                return True

        if await self.async_size(key) != len(context.payload):
            return False
        
        # Same size, confirm by hash
        return hashlib.sha256(await self.async_get(key)).hexdigest() == context.sha256

    def url_for(self, key: str) -> str:
        """
        Builds a URL under the configured base path.

        Args:
            key: Backend-relative path.

        Returns:
            The URL for the file.
        """
        return f"{self.base_url}/{key}"
