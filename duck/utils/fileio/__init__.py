"""
FileIOStream module.

Provides both synchronous and asynchronous file streaming interfaces.
Ideal for efficient reading of large files using chunked reads and supporting
standard `seek`, `tell`, and `close` operations in both environments.

**Methods that do not need to be async:**
Even in async context, the below methods don't necessarily need to be async:

1. `open` - Time complexity is O(1)
2. `seek` - Time complexity is O(1)
3. `tell` - Time complexity is O(1)

In async context, only `read`, `write`, and `close` need to be asynchronous.

**Caching:**
Read results are cached in a shared LRU ``InMemoryCache`` keyed by
``filepath:pos:size``. Each unique ``(file, offset, length)`` triple has its
own independent cache slot, so reads from different positions are all
cache-warm without interfering with each other — beneficial in environments
that seek frequently. Stale entries (detected via mtime) are evicted on
access. On write, overlapping cache entries are patched in memory without a
disk round-trip: entries fully covered by the write are spliced directly;
entries whose content is entirely inside the write range are reconstructed
in place; boundary-partial overlaps are evicted. The exact slice just
written is always stored in a new cache entry.

**Events:**
Hooks can be attached to ``on_read`` and ``on_write`` events via ``hook()``.
Each hook receives ``(stream, data, byte_count)`` and can be a plain callable
or an async coroutine function. Async hooks on a sync stream are scheduled
fire-and-forget on the running event loop when one is available.

Example::

    stream = FileIOStream("data.bin", open_now=True)

    def log_read(stream, data, n):
        print(f"read {n} bytes from {stream.filepath}")

    stream.hook("on_read", log_read)
    stream.read()
"""

import asyncio
import io
import os
from typing import Callable, Optional

from duck.exceptions.all import AsyncViolationError
from duck.utils.asyncio import in_async_context
from duck.utils.threading import async_to_sync_future
from duck.utils.caching import InMemoryCache
from duck.contrib.sync import convert_to_async_if_needed


# Shared LRU read cache — stores (data: bytes, mtime: float) per filepath.
# 1 024-entry cap matches the original TODO recommendation; LRU eviction is
# handled by InMemoryCache internally.
FILE_CACHE: InMemoryCache = InMemoryCache(maxkeys=1024)

# Valid event names accepted by hook()
VALID_EVENTS = frozenset({"on_read", "on_write"})


def to_async_fileio_stream(fileio_stream: "FileIOStream") -> "AsyncFileIOStream":
    """
    Converts a FileIOStream to an AsyncFileIOStream if not already async.

    Args:
        fileio_stream: The synchronous stream to convert.

    Returns:
        An AsyncFileIOStream wrapping the same underlying file descriptor.
    """
    assert isinstance(fileio_stream, FileIOStream), (
        f"Provided file io stream not recognized, expected an instance of "
        f"FileIOStream not {type(fileio_stream)}."
    )

    if isinstance(fileio_stream, AsyncFileIOStream):
        return fileio_stream

    new_stream = AsyncFileIOStream(
        filepath=fileio_stream.filepath,
        chunk_size=fileio_stream.chunk_size,
        open_now=False,
        mode=fileio_stream._mode,
    )

    if not new_stream._file_size:
        # Carry file size across so it is not re-stat'd unnecessarily
        new_stream._file_size = fileio_stream._file_size

    # Transfer descriptor and position
    new_stream._file = fileio_stream._file
    new_stream._pos = fileio_stream._pos

    # Copy the cached mtime so is_modified stays accurate on the new stream
    new_stream._cache_mtime = fileio_stream._cache_mtime

    # Transfer any hooks registered on the original stream
    new_stream._on_read_hooks = list(fileio_stream._on_read_hooks)
    new_stream._on_write_hooks = list(fileio_stream._on_write_hooks)

    # Prevent the old stream's __del__ from raising "file not closed"
    fileio_stream.ignore_file_open_on_delete = True

    return new_stream


class FileIOStream(io.IOBase):
    """
    Synchronous file streaming class that mimics ``io.IOBase``.

    Provides chunked reading and writing with a shared LRU cache and a
    simple event-hook system for ``on_read`` and ``on_write``.

    Read results are served from cache when the file is unchanged since the
    last read. Writes update the cache directly with the written bytes so the
    next full read is served from cache without an extra disk round-trip.

    Hooks are registered with :meth:`hook` and fired after every read or write.
    """

    __slots__ = {
        "filepath",
        "chunk_size",
        "open_now",
        "ignore_file_open_on_delete",
        "close_on_delete",
        "_file",
        "_pos",
        "_mode",
        "_file_size",
        "_lock",
        "_total_read_bytes",
        "_cache_mtime",     # mtime recorded when this stream last populated the cache
        "_on_read_hooks",   # list[Callable] fired after every read
        "_on_write_hooks",  # list[Callable] fired after every write
    }

    def __init__(
        self,
        filepath: str,
        chunk_size: int = 2 * 1024 * 1024,
        open_now: bool = False,
        mode: str = "rb",
    ):
        """
        Initialize the FileIOStream object.

        Args:
            filepath: Path to the file to be streamed.
            chunk_size: Maximum number of bytes to read or write at once.
                Defaults to 2 MB.
            open_now: Whether to open the file immediately. Defaults to False.
            mode: File open mode. Defaults to ``'rb'``.
        """
        # NOTE: FD must always be opened on read/write - to catch FileNotFoundError if file is nolonger available rather than just returning cached data.
        self.filepath = filepath
        self.chunk_size = chunk_size
        self.ignore_file_open_on_delete = False
        self.close_on_delete = True
        self._file: Optional[io.BufferedIOBase] = None
        self._pos = 0
        self._mode = mode
        self._file_size = os.path.getsize(filepath) if os.path.exists(filepath) else 0
        self._total_read_bytes: Optional[bytes] = None
        self._cache_mtime: Optional[float] = None
        self._on_read_hooks: list[Callable] = []
        self._on_write_hooks: list[Callable] = []

        if open_now:
            self.open()

    # Public API

    @property
    def is_modified(self) -> bool:
        """
        Whether the file has been modified since this stream last read it.

        Returns ``False`` when no read has occurred yet — there is no
        baseline mtime to compare against.

        Returns:
            ``True`` if the file's current mtime differs from the mtime
            recorded during the last read, ``False`` otherwise.
        """
        if self._cache_mtime is None:
            # No read has happened yet — no baseline to compare against
            return False
        return self.current_mtime() != self._cache_mtime

    def is_open(self) -> bool:
        """
        Check if the file is currently open.
        """
        return self._file is not None

    def raise_if_in_async_context(self, message: str) -> None:
        """
        Raise an error if used inside an async context.
        """
        if in_async_context():
            raise AsyncViolationError(message)

    def open(self) -> None:
        """
        Open the file using the provided mode.
        """
        if not self._file:
            self._file = open(self.filepath, self._mode)
            
    def get_pos(self) -> int:
        """
        Get the stream pos.
        """
        return self._pos
        
    def update_pos(self, pos: int):
        """
        Update the fileio pos - this does not seek to the pos at all.
        """
        self._pos = pos
        
    def increment_pos(self, pos: int):
        """
        Increment the fileio pos - this does not seek to the pos at all.
        """
        self._pos += pos
    
    def read(self, size: int = -1) -> bytes:
        """
        Synchronously read data from the file.

        Results are served from the LRU cache when the file has not been
        modified since the last read. On a cache miss the file is read
        normally and the result is stored in the cache for future calls.

        Fires all ``on_read`` hooks after a successful read.

        Args:
            size: Number of bytes to read. ``-1`` reads all content.

        Returns:
            File data as bytes.
        """
        self.raise_if_in_async_context(
            "This method must be used in a synchronous environment. "
            "Consider using `AsyncFileIOStream.read` instead."
        )

        if not self.is_open():
            raise ValueError("File not opened. Call `open()` first.")

        # Serve from cache when the file is unchanged
        cached = self.cache_get(size)
        
        if cached is not None:
            self.increment_pos(len(cached))
            self._accumulate_read_bytes(cached)
            self.fire_hooks(self._on_read_hooks, cached)
            return cached

        # Capture position before advancing so cache_set uses the read start offset
        read_pos = self.get_pos()

        # Cache miss — read from the actual file descriptor
        data = self._file.read() if size == -1 else self._file.read(min(size, self.chunk_size))
        self.increment_pos(len(data))
        self._accumulate_read_bytes(data)

        # Store in cache keyed by the offset this read started at
        self.cache_set(read_pos, size, data)
        
        # Fire hooks
        self.fire_hooks(self._on_read_hooks, data)
        
        # Return data
        return data

    def write(self, data: bytes) -> int:
        """
        Synchronously write data to the file.

        The written bytes are flushed to disk immediately, then stored in
        the cache under the full-read key (``size=-1``) with the post-write
        mtime. This means the next full read is served from cache without a
        disk round-trip.

        Fires all ``on_write`` hooks after a successful write.

        Args:
            data: Data to write.

        Returns:
            Number of bytes written.
        """
        self.raise_if_in_async_context(
            "This method must be used in a synchronous environment. "
            "Consider using `AsyncFileIOStream.write` instead."
        )

        if not self.is_open():
            raise ValueError("File not opened. Call `open()` first.")

        # Write to actual FD
        written = self._file.write(data)

        # Record the write start position before advancing _pos
        write_pos = self.get_pos()
        self.increment_pos(written)

        # Flush so the OS updates mtime before we re-stat in cache_patch_on_write
        self._file.flush()

        # Patch all cached entries that overlap the written region
        self.cache_patch_on_write(write_pos, data)
        
        # Fire hooks
        self.fire_hooks(self._on_write_hooks, data)
        
        # Return written data.
        return written

    def seek(self, offset: int, whence: int = os.SEEK_SET) -> None:
        """
        Move the file pointer to a new location.
        """
        if not self.is_open():
            raise ValueError("File not opened. Call `open()` first.")
        
        # Seek to the offset
        self._file.seek(offset, whence)
        
        # Update the pos
        self.update_pos(self._file.tell())

    def tell(self) -> int:
        """
        Get the current position in the file.
        """
        return self._pos

    def close(self) -> None:
        """
        Close the file.
        """
        self.raise_if_in_async_context(
            "This method must be used in a synchronous environment. "
            "Consider using `AsyncFileIOStream.close` instead."
        )
        if self._file:
            self._file.close()
            self._file = None
            
    # Event system

    def hook(self, event: str, fn: Callable) -> None:
        """
        Registers a hook function for the given event.

        The hook is called after every matching operation with the signature::

            fn(stream, data, byte_count)

        where ``stream`` is this ``FileIOStream``, ``data`` is the bytes that
        were read or written, and ``byte_count`` is ``len(data)``.

        Both plain callables and async coroutine functions are accepted.
        Async hooks on a synchronous stream are scheduled fire-and-forget on
        the running event loop when one is available.

        Args:
            event: One of ``"on_read"`` or ``"on_write"``.
            fn: The callable to register.

        Raises:
            ValueError: When ``event`` is not a recognised event name.
        """
        if event not in VALID_EVENTS:
            raise ValueError(
                f"Unknown event {event!r}. Valid events: {sorted(VALID_EVENTS)}"
            )
        if event == "on_read":
            self._on_read_hooks.append(fn)
        else:
            self._on_write_hooks.append(fn)

    def fire_hooks(self, hooks: list[Callable], data: bytes) -> None:
        """
        Fires all hooks in the given list with ``(self, data, len(data))``.

        Sync hooks are called inline. Async hooks are scheduled as
        fire-and-forget tasks on the running loop, or run in a new loop
        when none is active.

        Args:
            hooks: The list of callables to fire.
            data: The bytes that triggered this event.
        """
        for fn in hooks:
            if asyncio.iscoroutinefunction(fn):
                # Best-effort: schedule on the running loop or spin a new one
                try:
                    loop = asyncio.get_running_loop()
                    loop.create_task(fn(self, data, len(data)))
                except RuntimeError:
                    asyncio.run(fn(self, data, len(data)))
            else:
                fn(self, data, len(data))

    # Cache helpers

    def current_mtime(self) -> float:
        """
        Returns the file's current modification time from the OS.

        Returns:
            The ``st_mtime`` value for this stream's filepath, or 0.0
            if the file does not exist.
        """
        try:
            return os.stat(self.filepath).st_mtime
        except FileNotFoundError:
            return 0.0

    def make_cache_key(self, pos: int, size: int) -> str:
        """
        Builds the cache key for a read starting at ``pos`` of length ``size``.

        The key encodes the filepath, position, and size so that reads
        from different offsets occupy independent cache slots.

        Args:
            pos: The file offset at which the read starts.
            size: Number of bytes requested, or ``-1`` for a full read.

        Returns:
            A string cache key of the form ``"filepath:pos:size"``.
        """
        return f"{self.filepath}:{pos}:{size}"

    def cache_get(self, size: int) -> Optional[bytes]:
        """
        Returns cached bytes for the current position and size, or ``None``.

        Each ``(filepath, pos, size)`` triple has its own independent cache
        slot, so reads from different offsets are served correctly without
        interfering with each other. Stale entries (mtime mismatch) are
        evicted on access.

        Args:
            size: The read size passed to ``read()``, or ``-1`` for a full read.

        Returns:
            Cached bytes if the entry exists and is fresh, else ``None``.
        """
        cache_key = self.make_cache_key(self._pos, size)
        entry = FILE_CACHE.get(cache_key)
        
        if entry is None:
            return None

        cached_data, cached_mtime = entry

        # Evict the entry if the file has been modified on disk since caching
        if cached_mtime != self.current_mtime():
            FILE_CACHE.delete(cache_key)
            return None

        return cached_data

    def cache_set(self, pos: int, size: int, data: bytes) -> None:
        """
        Stores a read result in the cache keyed by position and size.

        Records the mtime on the instance so ``is_modified`` can compare
        against it later without an extra cache lookup.

        Args:
            pos: The file offset at which the read started.
            size: The read size used to build the cache key.
            data: The bytes to cache.
        """
        mtime = self.current_mtime()
        FILE_CACHE.set(self.make_cache_key(pos, size), (data, mtime))
        self._cache_mtime = mtime

    def cache_patch_on_write(self, write_pos: int, data: bytes) -> None:
        """
        Surgically updates every cached entry that overlaps the written region.

        Rather than flushing all cached entries or re-reading the whole file,
        this method iterates over existing cache keys for this filepath and
        patches any entry whose byte range overlaps ``[write_pos, write_pos +
        len(data))``.  Entries that do not overlap are left untouched — they
        remain valid because their byte ranges were not affected by the write.

        A new entry is always written for ``(write_pos, len(data))`` so the
        exact slice just written is immediately cache-warm.

        Entries that overlap but cannot be fully reconstructed from the
        in-memory write (e.g. partial overlaps at the boundary of a cached
        chunk) are evicted rather than storing incorrect data.
        
        Args:
            write_pos: The file offset at which the write started.
            data: The bytes that were just written.
        """
        write_end = write_pos + len(data)
        mtime = self.current_mtime()

        # Collect all cache keys belonging to this filepath.
        # InMemoryCache exposes its internal store as _store.
        prefix = f"{self.filepath}:"
        keys_to_check = [
            k for k in list(FILE_CACHE.cache.keys())
            if k.startswith(prefix)
        ]

        for key in keys_to_check:
            # Key format: "filepath:pos:size"
            rest = key[len(prefix):]
            parts = rest.split(":")
            
            if len(parts) != 2:
                continue

            try:
                cached_pos  = int(parts[0])
                cached_size = int(parts[1])
            except ValueError:
                continue

            # Get entry
            entry = FILE_CACHE.get(key)
            
            if entry is None:
                continue

            cached_data, _ = entry
            actual_len = len(cached_data)
            cached_end = cached_pos + actual_len

            # No overlap — entry is unaffected; keep it unchanged
            if write_end <= cached_pos or write_pos >= cached_end:
                continue

            if write_pos <= cached_pos and write_end >= cached_end:
                # Write completely covers this cached range — replace with the
                # relevant slice of the written data
                slice_start = cached_pos - write_pos
                new_data = data[slice_start: slice_start + actual_len]
                FILE_CACHE.set(key, (new_data, mtime))

            elif write_pos >= cached_pos and write_end <= cached_end:
                # Write is entirely inside the cached range — patch in place
                patch_offset = write_pos - cached_pos
                new_data = (
                    cached_data[:patch_offset]
                    + data
                    + cached_data[patch_offset + len(data):]
                )
                FILE_CACHE.set(key, (new_data, mtime))

            else:
                # Partial boundary overlap — evict rather than store wrong data
                FILE_CACHE.delete(key)

        # Always warm the cache for the exact slice just written
        FILE_CACHE.set(
            self.make_cache_key(write_pos, len(data)),
            (data, mtime),
        )
        self._cache_mtime = mtime
        
    def _accumulate_read_bytes(self, data: bytes) -> None:
        """
        Appends newly read bytes to the running ``_total_read_bytes`` buffer.

        Args:
            data: The bytes returned from the most recent read operation.
        """
        if self._total_read_bytes:
            self._total_read_bytes = b"".join([self._total_read_bytes, data])
        else:
            self._total_read_bytes = data

    def __del__(self) -> None:
        """
        Ensure the file is closed on delete else it raises a RuntimeError.

        Always calls the synchronous base ``close`` directly — ``__del__``
        can never be a coroutine, so we must not dispatch to the async
        override on ``AsyncFileIOStream``.
        """
        if self.is_open() and not self.ignore_file_open_on_delete:
            if self.close_on_delete:
                try:
                    # Call the base sync close explicitly so we never
                    # accidentally invoke the async override
                    FileIOStream.close(self)
                    return
                except Exception:
                    pass
            raise RuntimeError(
                "File is not closed yet, please ensure the file is closed before deletion."
            )


class AsyncFileIOStream(FileIOStream):
    """
    Asynchronous file streaming class.

    Provides async-compatible methods for reading and writing files in a
    non-blocking way. Shares the same LRU cache and event-hook system as
    ``FileIOStream``.

    Writes update the cache directly with the written bytes, matching the
    synchronous behaviour. Async hooks registered on this stream are
    awaited inside the lock; sync hooks are called inline.

    Notes:
        Compatible with async context managers (``async with``).
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._lock = asyncio.Lock()

    async def async_open(self) -> None:
        """
        Asynchronously open the file.
        """
        if not self.is_open():
            await convert_to_async_if_needed(super().open)()

    async def fire_hooks_async(self, hooks: list[Callable], data: bytes) -> None:
        """
        Fires all hooks, awaiting async ones and calling sync ones inline.

        Unlike the base :meth:`fire_hooks`, this variant is itself a
        coroutine so it can be awaited inside the async lock without
        scheduling fire-and-forget tasks.

        Args:
            hooks: The list of callables to fire.
            data: The bytes that triggered this event.
        """
        for fn in hooks:
            if asyncio.iscoroutinefunction(fn):
                await fn(self, data, len(data))
            else:
                fn(self, data, len(data))

    async def read(self, size: int = -1) -> bytes:
        """
        Asynchronously read from the file.

        Results are served from the LRU cache when the file has not been
        modified since the last read. On a cache miss the file is read in a
        thread and the result is stored in the cache.

        Fires all ``on_read`` hooks after a successful read.

        Args:
            size: Max bytes to read. ``-1`` reads full content.

        Returns:
            Data read from file.
        """
        if not self.is_open():
            raise ValueError("File not opened. Call `open()` first.")
            
        async with self._lock:
            # Serve from cache when the file is unchanged
            cached = self.cache_get(size)
            
            if cached is not None:
                self.increment_pos(len(cached))
                self._accumulate_read_bytes(cached)
                await self.fire_hooks_async(self._on_read_hooks, cached)
                return cached
                
            # Seek is very fast, no need to make it async
            self._file.seek(self.get_pos())

            # Capture position before advancing so cache_set uses the read start offset
            read_pos = self.get_pos()

            if size == -1:
                data = await convert_to_async_if_needed(self._file.read)()
            else:
                data = await convert_to_async_if_needed(self._file.read)(
                    min(size, self.chunk_size)
                )

            self.increment_pos(len(data))
            self._accumulate_read_bytes(data)

            # Store in cache keyed by the offset this read started at
            self.cache_set(read_pos, size, data)
            
            # Fire hooks
            await self.fire_hooks_async(self._on_read_hooks, data)
            
            # Return the final data.
            return data

    async def write(self, data: bytes) -> int:
        """
        Asynchronously write data to the file.

        The written bytes are flushed to disk then stored in the cache
        under the full-read key with the post-write mtime, so the next
        full read is served from cache without a disk round-trip.

        Fires all ``on_write`` hooks after a successful write.

        Args:
            data: Bytes to write.

        Returns:
            Number of bytes written.
        """
        if not self.is_open():
            raise ValueError("File not opened. Call `open()` first.")
            
        async with self._lock:
            # Seek mustn't be async, it's very fast
            self._file.seek(self.get_pos())
            
            # Do the actual write
            written = await convert_to_async_if_needed(self._file.write)(data)

            # Record the write start position before advancing _pos
            write_pos = self.get_pos()
            self.increment_pos(written)

            # Flush so the OS updates mtime before we re-stat
            await convert_to_async_if_needed(self._file.flush)()

            # Patch all cached entries that overlap the written region
            self.cache_patch_on_write(write_pos, data)
            
            # Fire hooks
            await self.fire_hooks_async(self._on_write_hooks, data)
            
            # Return written
            return written

    async def close(self) -> None:
        """
        Asynchronously close the file.
        """
        async with self._lock:
            if self.is_open():
                await convert_to_async_if_needed(super().close)()

    async def __aenter__(self):
        await self.async_open()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()
