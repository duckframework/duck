"""
Storage backends for static and media files with synchronous and async APIs.

All network traffic uses httpx. S3-compatible storage (AWS S3, Cloudflare R2,
MinIO, Backblaze B2) is called through httpx with a built-in AWS Signature V4
signer, and Cloudflare cache purging uses the same client. Downloads can be
streamed from every backend through `open_stream` and `async_open_stream`.
Local storage reads and writes through duck.utils.fileio. Uploads report
progress through callbacks at configurable percentage steps.
"""

from __future__ import annotations

import io
import os
import re
import hashlib
import inspect


from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import (
    Any,
    BinaryIO,
    Callable,
    Iterator,
    Union,
    AsyncIterator,
)
from pathlib import Path

from duck.settings import SETTINGS
from duck.http.mimes import guess_file_mimetype
from duck.contrib.sync import ensure_async
from duck.contrib.storage.backends.core.progress import (
    DEFAULT_PROGRESS_STEP,
    ProgressReporter,
    ProgressCallback,
)

from duck.utils.asyncio import raise_if_in_async_context
from duck.utils.fileio import AsyncFileIOStream, FileIOStream, to_async_fileio_stream


FileData = Union[bytes, BinaryIO, FileIOStream]
Processor = Callable[["UploadContext"], "UploadContext"]
KeyBuilder = Callable[["UploadContext"], str]
Callback = Callable[["StoredFile"], None]


SAFE_NAME_PATTERN = re.compile(r"[^A-Za-z0-9._-]+")
DEFAULT_CACHE_CONTROL = "public, max-age=31536000, immutable"
DEFAULT_CHUNK_SIZE = 64 * 1024
EMPTY_SHA256 = hashlib.sha256(b"").hexdigest()


@dataclass
class UploadContext:
    """
    Mutable state of a file as it moves through the save pipeline.

    Processors receive this object, may change any field, and return it.

    Attributes:
        payload: Raw file contents.
        filename: Sanitized original filename.
        folder: Folder the file is stored under, without slashes at the ends.
        content_type: MIME type recorded with the file.
        cache_control: Cache-Control header recorded with the file.
        metadata: Free-form data that custom logic can attach and read.
        sha256: Hex digest of the payload, computed after processing.
        key: Storage key, assigned by the key builder.
    """

    payload: bytes
    filename: str
    folder: str = ""
    content_type: str = "application/octet-stream"
    cache_control: str = DEFAULT_CACHE_CONTROL
    metadata: dict[str, Any] = field(default_factory=dict)
    sha256: str = ""
    key: str = ""


@dataclass(frozen=True)
class StoredFile:
    """
    Metadata describing a file saved in a storage backend.

    Attributes:
        key: Backend-relative path that identifies the file.
        url: Public URL the file can be served from.
        size: Size of the stored file in bytes.
        content_type: MIME type of the stored file.
    """

    key: str
    url: str
    size: int
    content_type: str



def iter_chunks(payload: bytes, chunk_size: int, reporter: ProgressReporter) -> Iterator[bytes]:
    """
    Splits a payload into chunks and reports progress as each chunk is consumed.

    Args:
        payload: Bytes to split.
        chunk_size: Maximum size of each chunk in bytes.
        reporter: Progress reporter to advance after each chunk.

    Yields:
        Consecutive slices of the payload.
    """
    for offset in range(0, len(payload), chunk_size):
        chunk = payload[offset : offset + chunk_size]

        # Yield chunk
        yield chunk

        # Advance
        reporter.advance(len(chunk))


async def async_iter_chunks(payload: bytes, chunk_size: int, reporter: ProgressReporter) -> AsyncIterator[bytes]:
    """
    Async version of `iter_chunks` for use with `httpx.AsyncClient`.

    Args:
        payload: Bytes to split.
        chunk_size: Maximum size of each chunk in bytes.
        reporter: Progress reporter to advance after each chunk.

    Yields:
        Consecutive slices of the payload.
    """
    for offset in range(0, len(payload), chunk_size):
        chunk = payload[offset : offset + chunk_size]

        # Yield chunk
        yield chunk

        # Advance
        await reporter.async_advance(len(chunk))


def read_payload(data: FileData) -> bytes:
    """
    Reads the full contents of an upload synchronously.

    Accepts raw bytes, a FileIOStream, or any binary file-like object.

    Args:
        data: The upload source.

    Returns:
        The file contents as bytes.
    """
    # Bytes are already in memory
    if isinstance(data, bytes):
        return data

    # FileIOStream and file-like objects both expose read
    return data.read()


async def async_read_payload(data: FileData) -> bytes:
    """
    Reads the full contents of an upload without blocking the event loop.

    Native async streams are awaited directly. Sync FileIOStream objects are
    converted to AsyncFileIOStream, and other file-like objects are read in a
    worker thread through `ensure_async`.

    Args:
        data: The upload source.

    Returns:
        The file contents as bytes.
    """
    # Bytes are already in memory
    if isinstance(data, bytes):
        return data

    # Native async stream
    if isinstance(data, AsyncFileIOStream):
        return await data.read()

    # Sync FileIOStream is converted so its read is awaited
    if isinstance(data, FileIOStream):
        if not data.is_open():
            data.open()

        stream = to_async_fileio_stream(data)

        try:
            return await stream.read()
        finally:
            await stream.close()

    # Other file-like objects are read in a worker thread
    return await ensure_async(data.read)()


def default_key_builder(context: UploadContext) -> str:
    """
    Builds a content-addressed key from the folder, a hash and the filename.

    Args:
        context: Upload state with the payload already processed.

    Returns:
        A key such as `"images/3f2a9c1b8d7e6f40/logo.png"`.
    """
    parts = [context.folder, context.sha256[:16], context.filename]
    return "/".join(part for part in parts if part)


def resolve_credentials(
    access_key_id: str | None,
    secret_access_key: str | None,
    access_env: str,
    secret_env: str,
) -> tuple[str, str]:
    """
    Returns credentials from arguments, falling back to environment variables.

    Args:
        access_key_id: Access key passed explicitly, or None.
        secret_access_key: Secret key passed explicitly, or None.
        access_env: Environment variable holding the access key.
        secret_env: Environment variable holding the secret key.

    Returns:
        A tuple of access key ID and secret access key.

    Raises:
        ValueError: If either credential is missing.
    """
    access = access_key_id or os.environ.get(access_env)
    secret = secret_access_key or os.environ.get(secret_env)

    if not (access and secret):
        raise ValueError(f"Set {access_env} and {secret_env} or pass the credentials explicitly")

    return access, secret


class StorageBackend(ABC):
    """
    Base class for storage backends.

    Subclasses implement the synchronous primitives `put`, `get`,
    `delete`, `exists` and `url_for`. Each primitive has an `async_`
    counterpart that defaults to running the sync version through
    `ensure_async`. Backends that talk to the network override the async
    versions with native httpx calls. `open_stream` and `async_open_stream`
    provide chunked downloads; the defaults load the file into memory, so
    backends should override them for large files. `save` and `async_save`
    share the same pipeline.
    """

    def __init__(
        self,
        cache_control: str = DEFAULT_CACHE_CONTROL,
        key_builder: KeyBuilder = default_key_builder,
        processors: list[Processor] | None = None,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        progress_step: float = DEFAULT_PROGRESS_STEP,
    ) -> None:
        """
        Initializes the backend.

        Args:
            cache_control: Cache-Control header applied to every stored file.
            key_builder: Function that assigns the storage key to an upload.
            processors: Processors to run, in order, before every save.
            chunk_size: Bytes sent per chunk during uploads and streamed per chunk during downloads.
            progress_step: Percentage increment between progress events.

        Raises:
            ValueError: If `progress_step` is not positive.
        """
        if progress_step <= 0:
            raise ValueError("progress_step must be greater than 0")

        # Set some attributes
        self.cache_control = cache_control
        self.key_builder = key_builder
        self.processors: list[Processor] = list(processors or [])
        self.callbacks: list[Callback] = []
        self.progress_callbacks: list[ProgressCallback] = []
        self.chunk_size = chunk_size
        self.progress_step = progress_step

    def processor(self, func: Processor) -> Processor:
        """
        Registers a processor. Usable as a decorator.

        Args:
            func: Function that accepts and returns an UploadContext.

        Returns:
            The same function, so it can still be called directly.
        """
        self.processors.append(func)

        return func

    def on_saved(self, func: Callback) -> Callback:
        """
        Registers a callback that runs after each successful save. Usable as a decorator.

        Args:
            func: Function that accepts a StoredFile.

        Returns:
            The same function, so it can still be called directly.
        """
        self.callbacks.append(func)

        return func

    def on_progress(self, func: ProgressCallback) -> ProgressCallback:
        """
        Registers a progress callback for every upload. Usable as a decorator.

        Args:
            func: Function that accepts a ProgressEvent.

        Returns:
            The same function, so it can still be called directly.
        """
        self.progress_callbacks.append(func)

        return func

    def prepare_context(
        self,
        payload: bytes,
        filename: str,
        folder: str,
        metadata: dict[str, Any] | None,
    ) -> UploadContext:
        """
        Runs processors and assigns the storage key to an already-read payload.

        This step does no file I/O, so it can run in a worker thread.

        Args:
            payload: Raw file contents.
            filename: Original filename, used for the key and MIME detection.
            folder: Optional folder such as `"images"`.
            metadata: Optional data made available to processors and to `put`.

        Returns:
            The fully prepared UploadContext.
        """
        # Create safe name
        safe_name = SAFE_NAME_PATTERN.sub("-", Path(filename).name).strip("-") or "file"

        # Build context
        context = UploadContext(
            payload=payload,
            filename=safe_name,
            folder=folder.strip("/"),
            content_type=guess_file_mimetype(safe_name)[0] or "application/octet-stream",
            cache_control=self.cache_control,
            metadata=dict(metadata or {}),
        )

        for func in self.processors:
            context = func(context)

        # Set some context attrs
        context.sha256 = hashlib.sha256(context.payload).hexdigest()
        context.key = self.key_builder(context)

        # Return final context
        return context

    def build_context(
        self,
        data: FileData,
        filename: str,
        folder: str,
        metadata: dict[str, Any] | None,
    ) -> UploadContext:
        """
        Reads the input synchronously, then prepares the upload.

        Args:
            data: Raw bytes, a FileIOStream, or a binary file-like object.
            filename: Original filename, used for the key and MIME detection.
            folder: Optional folder such as `"images"`.
            metadata: Optional data made available to processors and to `put`.

        Returns:
            The fully prepared UploadContext.
        """
        # Read file contents
        payload = read_payload(data)

        return self.prepare_context(payload, filename, folder, metadata)

    async def async_build_context(
        self,
        data: FileData,
        filename: str,
        folder: str,
        metadata: dict[str, Any] | None,
    ) -> UploadContext:
        """
        Async version of `build_context` that reads the input without blocking.

        Args:
            data: Raw bytes, a FileIOStream, or a binary file-like object.
            filename: Original filename, used for the key and MIME detection.
            folder: Optional folder such as `"images"`.
            metadata: Optional data made available to processors and to `put`.

        Returns:
            The fully prepared UploadContext.
        """
        # Read file contents without blocking the event loop
        payload = await async_read_payload(data)

        return await ensure_async(self.prepare_context)(payload, filename, folder, metadata)

    def make_reporter(self, context: UploadContext, on_progress: ProgressCallback | None) -> ProgressReporter:
        """
        Creates a reporter that sends events to global and per-call callbacks.

        Args:
            context: Prepared upload state.
            on_progress: Optional callback for this save only.

        Returns:
            A ProgressReporter ready to start.
        """
        callbacks = list(self.progress_callbacks)

        if on_progress is not None:
            callbacks.append(on_progress)

        return ProgressReporter(
            total=len(context.payload),
            step=self.progress_step,
            callbacks=callbacks,
            key=context.key,
            filename=context.filename,
        )

    def build_result(self, context: UploadContext) -> StoredFile:
        """
        Builds the metadata returned to the caller.

        Args:
            context: Final upload state.

        Returns:
            A StoredFile describing the saved file.
        """
        return StoredFile(
            key=context.key,
            url=self.url_for(context.key),
            size=len(context.payload),
            content_type=context.content_type,
        )

    def save(
        self,
        data: FileData,
        filename: str,
        folder: str = "",
        metadata: dict[str, Any] | None = None,
        on_progress: ProgressCallback | None = None,
    ) -> StoredFile:
        """
        Runs the pipeline, stores the file, reports progress and fires callbacks.

        Args:
            data: Raw bytes, a FileIOStream, or a binary file-like object.
            filename: Original filename, used for the key and MIME detection.
            folder: Optional folder such as `"images"` or `"video"`.
            metadata: Optional data made available to processors and to `put`.
            on_progress: Optional callback that receives ProgressEvent objects
                for this save, in addition to global callbacks.

        Returns:
            A StoredFile describing where the file was stored.
        """
        raise_if_in_async_context(f"Calling this method in async context not allowed, try using `async_save` instead.")

        # Build and make reporter
        context = self.build_context(data, filename, folder, metadata)
        reporter = self.make_reporter(context, on_progress)

        # Start reporter
        reporter.start()

        # Put data
        self.put(context.key, context, reporter)

        # Finish reporter
        reporter.finish()

        # Build result
        stored = self.build_result(context)

        for callback in self.callbacks:
            callback(stored)

        return stored

    async def async_save(
        self,
        data: FileData,
        filename: str,
        folder: str = "",
        metadata: dict[str, Any] | None = None,
        on_progress: ProgressCallback | None = None,
    ) -> StoredFile:
        """
        Async version of `save` that uses the backend's async primitives.

        Args:
            data: Raw bytes, a FileIOStream, or a binary file-like object.
            filename: Original filename, used for the key and MIME detection.
            folder: Optional folder such as `"images"` or `"video"`.
            metadata: Optional data made available to processors and to `put`.
            on_progress: Optional callback that receives ProgressEvent objects
                for this save, in addition to global callbacks.

        Returns:
            A StoredFile describing where the file was stored.
        """
        context = await self.async_build_context(data, filename, folder, metadata)
        reporter = self.make_reporter(context, on_progress)

        # Start reporter
        await reporter.async_start()

        # Put data
        await self.async_put(context.key, context, reporter)

        # Finish reporter
        await reporter.async_finish()

        # Build result
        stored = self.build_result(context)

        # Notify saved
        await self.async_notify_saved(stored)

        # Return the stored file
        return stored

    async def async_notify_saved(self, stored: StoredFile) -> None:
        """
        Calls every `on_saved` callback, awaiting coroutine callbacks.

        Args:
            stored: Metadata of the saved file.
        """
        for callback in self.callbacks:
            result = callback(stored)

            if inspect.isawaitable(result):
                # Callback is an async callback so await it
                await result  # type: ignore

    def save_as(
        self,
        data: FileData,
        key: str,
        folder: str = "",
        metadata: dict[str, Any] | None = None,
        on_progress: ProgressCallback | None = None,
    ) -> StoredFile:
        """
        Stores a file under an exact key, keeping the pipeline and progress reporting.

        Args:
            data: Raw bytes, a FileIOStream, or a binary file-like object.
            key: Exact storage key, such as `"css/app.css"`.
            folder: Optional folder such as `"images"` or `"video"`.
            metadata: Optional data made available to processors and to `put`.
            on_progress: Optional callback that receives ProgressEvent objects
                for this save, in addition to global callbacks.

        Returns:
            A StoredFile describing where the file was stored.
        """
        raise_if_in_async_context(f"Calling this method in async context not allowed, try using `async_save_as` instead.")
        
        # Run the pipeline, then keep the caller's key
        context = self.build_context(data, Path(key).name, folder, metadata)
        context.key = key

        # Make reporter
        reporter = self.make_reporter(context, on_progress)

        # Start reporter
        reporter.start()

        # Put data
        self.put(key, context, reporter)

        # Finish reporter
        reporter.finish()

        # Build result
        stored = self.build_result(context)

        for callback in self.callbacks:
            callback(stored)

        return stored

    async def async_save_as(
        self,
        data: FileData,
        key: str,
        folder: str = "",
        metadata: dict[str, Any] | None = None,
        on_progress: ProgressCallback | None = None,
    ) -> StoredFile:
        """
        Async version of `save_as`.

        Args:
            data: Raw bytes, a FileIOStream, or a binary file-like object.
            key: Exact storage key, such as `"css/app.css"`.
            folder: Optional folder such as `"images"` or `"video"`.
            metadata: Optional data made available to processors and to `put`.
            on_progress: Optional callback that receives ProgressEvent objects
                for this save, in addition to global callbacks.

        Returns:
            A StoredFile describing where the file was stored.
        """
        # Run the pipeline, then keep the caller's key
        context = await self.async_build_context(data, Path(key).name, folder, metadata)
        context.key = key

        # Make reporter
        reporter = self.make_reporter(context, on_progress)

        # Start reporter
        await reporter.async_start()

        # Put data
        await self.async_put(key, context, reporter)

        # Finish reporter
        await reporter.async_finish()

        # Build result
        stored = self.build_result(context)

        # Notify saved
        await self.async_notify_saved(stored)

        # Return the final stored file
        return stored

    async def async_put(self, key: str, context: UploadContext, reporter: ProgressReporter) -> None:
        """
        Async version of `put`. Runs the sync version through `ensure_async` by default.

        Args:
            key: Backend-relative path.
            context: Final upload state.
            reporter: Progress reporter to advance as bytes are sent.
        """
        await ensure_async(self.put)(key, context, reporter)

    async def async_get(self, key: str) -> bytes:
        """
        Async version of `get`.

        Args:
            key: Backend-relative path.

        Returns:
            The file contents as bytes.
        """
        return await ensure_async(self.get)(key)

    def open_stream(self, key: str) -> Any:
        """
        Opens a stored file for chunked reading. The caller must close it.

        The default loads the whole file into memory. Backends should override
        this to stream from their storage.

        Args:
            key: Backend-relative path.

        Returns:
            A readable stream positioned at the start of the file.
        """
        return io.BytesIO(self.get(key))

    async def async_open_stream(self, key: str) -> Any:
        """
        Async version of `open_stream`. The caller must close it.

        The default loads the whole file into memory. Backends should override
        this to stream from their storage.

        Args:
            key: Backend-relative path.

        Returns:
            An async readable stream positioned at the start of the file.
        """
        from duck.contrib.storage.backends.core.streams import AsyncBytesStream

        return AsyncBytesStream(await self.async_get(key))

    async def async_delete(self, key: str) -> None:
        """
        Async version of `delete`.

        Args:
            key: Backend-relative path.
        """
        await ensure_async(self.delete)(key)

    async def async_exists(self, key: str) -> bool:
        """
        Async version of `exists`.

        Args:
            key: Backend-relative path.

        Returns:
            True if the file exists, otherwise False.
        """
        return await ensure_async(self.exists)(key)

    @abstractmethod
    def put(self, key: str, context: UploadContext, reporter: ProgressReporter) -> None:
        """
        Writes a processed upload to the given key.

        Implementations should call `reporter.advance(size)` as bytes are
        sent. `save` already emits the 0% and 100% events.

        Args:
            key: Backend-relative path.
            context: Final upload state, including payload, content type and metadata.
            reporter: Progress reporter to advance as bytes are sent.
        """

    @abstractmethod
    def get(self, key: str) -> bytes:
        """
        Reads the contents of a stored file.

        Args:
            key: Backend-relative path.

        Returns:
            The file contents as bytes.
        """

    @abstractmethod
    def delete(self, key: str) -> None:
        """
        Deletes a stored file. Missing files are ignored.

        Args:
            key: Backend-relative path.
        """

    @abstractmethod
    def exists(self, key: str) -> bool:
        """
        Checks whether a file exists.

        Args:
            key: Backend-relative path.

        Returns:
            True if the file exists, otherwise False.
        """

    @abstractmethod
    def url_for(self, key: str) -> str:
        """
        Builds the public URL for a stored file.

        Args:
            key: Backend-relative path.

        Returns:
            The URL clients use to fetch the file.
        """
