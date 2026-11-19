"""
Caching backends for Duck.

Provides an in-memory LRU cache and persistent file-backed caches (plain,
dynamically sharded, and key-as-folder), plus sync and async caching
decorators.

Backends subclass CacheBase and override the public methods (set, get,
delete, pop, clear, and optionally has / close). CacheBase supplies a
reentrant lock (self.lock) that each backend holds while touching its own
state, the async_* wrappers (sync methods run in a worker thread) and the
decorators.
"""

import re
import os
import uuid
import time
import shutil
import asyncio
import hashlib
import inspect
import threading
import diskcache

from typing import Any, Callable
from functools import wraps
from pathlib import Path
from collections import OrderedDict

from duck.utils.path import joinpaths


# Sentinel meaning "no value / no default", so None stays a storable value.
MISSING = object()

# diskcache culls entries beyond a 1 GB default size_limit. Used when the
# caller asks for no limit.
UNLIMITED_SIZE: int = 2**62

# Resolved lazily by ensure_async (None means duck's version is unavailable).
_duck_ensure_async: Any = MISSING


def ensure_async(func: Callable) -> Callable:
    """
    Return an awaitable-returning version of func.

    Uses duck's implementation when available. Otherwise (for example
    outside a project folder, where importing duck raises SettingsError)
    sync functions run in a worker thread.

    Args:
        func: Function to wrap.

    Returns:
        Callable that returns an awaitable.
    """
    global _duck_ensure_async

    # NOTE: duck.utils modules must not depend on duck.settings because they
    # may be imported outside of a project folder, so import lazily.
    if _duck_ensure_async is MISSING:
        try:
            from duck.contrib.sync import ensure_async as duck_impl
        except Exception:
            duck_impl = None
        _duck_ensure_async = duck_impl

    if _duck_ensure_async is not None:
        return _duck_ensure_async(func)

    if inspect.iscoroutinefunction(func):
        return func

    @wraps(func)
    async def wrapper(*args, **kwargs):
        return await asyncio.to_thread(func, *args, **kwargs)

    return wrapper


class CacheBase:
    """
    Base class for all cache backends.

    Subclasses must override set, get, delete, pop and clear. They may
    override has and close (call super().close() last) and save.

    Locking:
        self.lock is a reentrant lock created here. Subclasses hold it in
        their public methods while touching internal state, so methods may
        call each other freely without deadlocking.

    Class attributes:
        BLOCKING: When True, async_* methods run in a worker thread. Set to
            False for backends that never touch disk or network.
    """

    BLOCKING: bool = True
    """
    Whether async_* methods run in a worker thread. Set to False for backends that never touch disk or network (no I/O).
    """

    def __init__(self):
        self.lock = threading.RLock()
        self.closed = False

    @staticmethod
    def _make_key(func: Callable, key_prefix: str | None, args: tuple, kwargs: dict) -> str:
        """
        Build a deterministic cache key for a call, hashing it when long.
        """
        raw = (
            f"{key_prefix or func.__module__}.{func.__qualname__}:"
            f"{args!r}:{sorted(kwargs.items())!r}"
        )

        if len(raw) <= 200:
            return raw
        
        return f"{raw[:100]}-{hashlib.sha256(raw.encode()).hexdigest()}"

    # Decorators
    
    def cache(self, expiry: int | float | None = None, key_prefix: str | None = None):
        """
        Decorate a synchronous function with caching. None results are cached.

        The wrapper gains invalidate(*args, **kwargs) to drop one entry.

        Args:
            expiry: Cache expiry time in seconds.
            key_prefix: Optional namespace prefix for generated cache keys.

        Returns:
            Decorator for synchronous functions.

        Example:

        ```python
        cache = InMemoryCache()

        @cache.cache(expiry=3600)
        def get_city_choices():
            return list(City.objects.all())
        ```
        """
        def decorator(func: Callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                key = self._make_key(func, key_prefix, args, kwargs)

                # MISSING (not None) marks a miss so None results are cached.
                cached = self.get(key, MISSING)

                if cached is not MISSING:
                    return cached

                # Compute the result
                result = func(*args, **kwargs)

                # Cache computed result
                self.set(key, result, expiry=expiry)

                # Return the result to the caller
                return result

            # Invalidate one entry by key, not by function call.
            wrapper.invalidate = lambda *a, **kw: self.delete(
                self._make_key(func, key_prefix, a, kw)
            )

            # Return the wrapper
            return wrapper

        return decorator

    def async_cache(self, expiry: int | float | None = None, key_prefix: str | None = None):
        """
        Decorate an asynchronous function with caching. None results are cached.

        Concurrent calls with the same arguments are collapsed: the first
        computes while the others wait and reuse its result. The wrapper
        gains an async invalidate(*args, **kwargs).

        Args:
            expiry: Cache expiry time in seconds.
            key_prefix: Optional namespace prefix for generated cache keys.

        Returns:
            Decorator for asynchronous functions.

        Example:

        ```python
        cache = InMemoryCache()

        @cache.async_cache(expiry=3600)
        async def async_get_city_choices():
            return await City.objects.all()
        ```

        """
        # (event loop id, key) -> [lock, waiter count]. asyncio locks are bound
        # to one loop, hence the loop id. Entries are removed once idle.
        locks: dict[tuple[int, str], list] = {}

        def decorator(func: Callable):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                key = self._make_key(func, key_prefix, args, kwargs)
                lock_key = (id(asyncio.get_running_loop()), key)

                # Acquire the lock for this key
                entry = locks.setdefault(lock_key, [asyncio.Lock(), 0])
                entry[1] += 1

                try:
                    async with entry[0]:
                        cached = await self.async_get(key, MISSING)

                        if cached is not MISSING:
                            return cached

                        # Compute the result
                        result = await func(*args, **kwargs)

                        # Cache computed result
                        await self.async_set(key, result, expiry=expiry)

                        # Return the result to the caller
                        return result
                    
                finally:
                    entry[1] -= 1

                    if entry[1] == 0:
                        locks.pop(lock_key, None)

            async def invalidate(*args, **kwargs) -> None:
                """
                Drop one entry from the cache.
                """
                await self.async_delete(self._make_key(func, key_prefix, args, kwargs))

            # Attach the invalidate method to the wrapper
            wrapper.invalidate = invalidate

            # Return the wrapper
            return wrapper

        return decorator
    
    def require_open(self) -> None:
        """
        Raise RuntimeError if the cache has been closed.
        """
        if self.closed:
            raise RuntimeError(f"Operation on a closed {type(self).__name__}.")

    def save(self) -> None:
        """
        Optional persistence hook. No-op unless overridden.
        """

    def set(self, key: str, value: Any, expiry: int | float | None = None) -> None:
        """
        Store a value under key with an optional TTL.

        Args:
            key: Cache key.
            value: Value to store.
            expiry: Seconds until expiry. None means no expiry.
        """
        raise NotImplementedError(f"'set' is not implemented on {type(self).__name__}.")

    def get(self, key: str, default: Any = None) -> Any:
        """
        Retrieve the value stored under key.

        Args:
            key: Cache key.
            default: Returned when the key is absent or expired.

        Returns:
            The cached value or default.
        """
        raise NotImplementedError(f"'get' is not implemented on {type(self).__name__}.")

    def has(self, key: str) -> bool:
        """
        Return True if key exists and has not expired.

        Args:
            key: Cache key.
        """
        return self.get(key, MISSING) is not MISSING

    def delete(self, key: str) -> None:
        """
        Remove key from the cache. Silent if absent.

        Args:
            key: Cache key.
        """
        raise NotImplementedError(f"'delete' is not implemented on {type(self).__name__}.")

    def pop(self, key: str, default: Any = MISSING) -> Any:
        """
        Retrieve and atomically remove a value.

        Args:
            key: Cache key.
            default: Returned when absent. Raises KeyError if omitted.

        Raises:
            KeyError: When the key is missing and no default was given.
        """
        raise NotImplementedError(f"'pop' is not implemented on {type(self).__name__}.")

    def clear(self) -> None:
        """
        Evict all entries from the cache.
        """
        raise NotImplementedError(f"'clear' is not implemented on {type(self).__name__}.")

    def close(self) -> None:
        """
        Mark the cache closed. Subclasses release resources first, then
        call super().close(). Further operations raise RuntimeError.
        """

        with self.lock:
            self.closed = True

    # Async API

    async def async_run(self, func: Callable, *args) -> Any:
        """
        Run a sync method inline or in a worker thread, per BLOCKING.
        """
        if not self.BLOCKING:
            return func(*args)

        # Run in a worker thread so disk or network I/O does not block the event loop.
        return await ensure_async(func)(*args)

    async def async_set(self, key: str, value: Any, expiry: int | float | None = None) -> None:
        """
        Async version of set.
        """
        await self.async_run(self.set, key, value, expiry)

    async def async_get(self, key: str, default: Any = None) -> Any:
        """
        Async version of get.
        """
        return await self.async_run(self.get, key, default)

    async def async_has(self, key: str) -> bool:
        """
        Async version of has.
        """
        return await self.async_run(self.has, key)

    async def async_delete(self, key: str) -> None:
        """
        Async version of delete.
        """
        await self.async_run(self.delete, key)

    async def async_pop(self, key: str, default: Any = MISSING) -> Any:
        """
        Async version of pop.
        """
        return await self.async_run(self.pop, key, default)

    async def async_clear(self) -> None:
        """
        Async version of clear.
        """
        await self.async_run(self.clear)

    def __contains__(self, key: str) -> bool:
            return self.has(key)
    
    def __enter__(self):
        return self

    def __exit__(self, *exc_info) -> None:
            self.close()


class InMemoryCache(CacheBase):
    """
    In-memory cache with LRU eviction and per-key TTL.

    Uses time.monotonic() so wall-clock changes never affect expiry.
    Expired entries are purged when the cache is over capacity and every
    PURGE_INTERVAL writes, so unread ones cannot accumulate forever.

    Args:
        maxkeys: Maximum number of keys before LRU eviction. None is unbounded.
    """

    BLOCKING = False

    PURGE_INTERVAL: int = 1024

    def __init__(self, maxkeys: int | None = None):
        super().__init__()

        if maxkeys is not None and maxkeys < 1:
            raise ValueError("maxkeys must be >= 1 or None.")

        self.maxkeys = maxkeys

        # key -> value, most recently used at the end.
        self._cache: OrderedDict[str, Any] = OrderedDict()

        # key -> monotonic deadline.
        self.expiry_map: dict[str, float] = {}

        # Write counter that triggers periodic purges.
        self.writes = 0

    def purge_expired(self) -> None:
        """
        Remove all expired entries now.
        """

        with self.lock:
            self.require_open()

            # Calculate the current monotonic time
            now = time.monotonic()

            # Delete expired keys from the cache and expiry_map
            for key in [k for k, t in self.expiry_map.items() if t <= now]:
                del self._cache[key]
                del self.expiry_map[key]

    def set(self, key: str, value: Any, expiry: int | float | None = None) -> None:
        """
        Insert or update key with an optional TTL, evicting LRU keys if full.

        Args:
            key: Cache key.
            value: Value to store.
            expiry: Seconds until expiry. None means the entry lives forever.

        Raises:
            ValueError: When expiry is negative.
        """
        if expiry is not None and expiry < 0:
            raise ValueError(f"expiry must be >= 0 or None, got {expiry!r}.")

        with self.lock:
            self.require_open()

            # Insert or update the value
            self._cache[key] = value

            # Mark the key as most recently used.
            self._cache.move_to_end(key)  # Mark as most recently used.

            if expiry is None:
                self.expiry_map.pop(key, None)

            else:
                self.expiry_map[key] = time.monotonic() + expiry

            # Increment the write counter
            self.writes += 1

            # Determine max capacity
            over_capacity = self.maxkeys is not None and len(self._cache) > self.maxkeys

            # Drop dead entries first so live ones are not evicted needlessly.
            if over_capacity or self.writes % self.PURGE_INTERVAL == 0:
                self.purge_expired()

            while self.maxkeys is not None and len(self._cache) > self.maxkeys:
                oldest, _ = self._cache.popitem(last=False)

                # Remove the oldest key from the expiry map as well
                self.expiry_map.pop(oldest, None)

    def get(self, key: str, default: Any = None) -> Any:
        """
        Retrieve the value for key, evicting it first if expired.

        Args:
            key: Cache key.
            default: Returned when the key is absent or expired.
        """
        with self.lock:
            self.require_open()

            if not self.has(key):
                return default

            # Move an existing element to the end (or beginning if last is false).
            self._cache.move_to_end(key)

            # Return the value
            return self._cache[key]

    def has(self, key: str) -> bool:
        """
        Return True if key exists and has not expired (does not touch LRU order).

        Args:
            key: Cache key.
        """
        with self.lock:
            self.require_open()

            # Get deadline
            deadline = self.expiry_map.get(key)

            if deadline is not None and time.monotonic() >= deadline:
                # Delete key
                self.delete(key)

                # Return False flag
                return False

            return key in self._cache

    def delete(self, key: str) -> None:
        """
        Remove key from the cache. Silent if absent.

        Args:
            key: Cache key.
        """
        with self.lock:
            self.require_open()

            # Remove the key from both the cache
            self._cache.pop(key, None)

            # Remove the key from the expiry map
            self.expiry_map.pop(key, None)

    def pop(self, key: str, default: Any = MISSING) -> Any:
        """
        Retrieve and remove a value under a single lock acquisition.

        Args:
            key: Cache key.
            default: Returned when absent. Raises KeyError if omitted.

        Raises:
            KeyError: When the key is missing and no default was given.
        """
        with self.lock:
            self.require_open()

            if not self.has(key):
                if default is MISSING:
                    raise KeyError(key)
                return default
            
            # Remove the key from both the cache and expiry map
            self.expiry_map.pop(key, None)

            # Return the value from the cache
            return self._cache.pop(key)

    def clear(self) -> None:
        """
        Evict all entries.
        """
        with self.lock:
            self.require_open()

            # Clear cache
            self._cache.clear()

            # Clear expiry map
            self.expiry_map.clear()

    def close(self) -> None:
        """
        Release all entries and mark the cache closed.
        """
        with self.lock:
            self._cache.clear()

            # Clear expiry map
            self.expiry_map.clear()

            # Mark the cache as closed
            super().close()


class PersistentFileCache(CacheBase):
    """
    Persistent file-backed cache powered by diskcache.

    diskcache is itself thread-safe; the lock here guards the closed state
    and keeps close() from racing in-flight operations. diskcache keeps one
    SQLite connection per thread and close() only closes the calling
    thread's connection.

    Args:
        path:
            Directory used as the cache store (created if missing).

        cache_size:
            Maximum size in bytes. None means unlimited, which
            overrides diskcache's silent 1 GB default.
    """

    def __init__(self, path: str, cache_size: int | None = None):
        super().__init__()

        if os.path.isfile(path):
            raise FileExistsError(f"Path must be a directory, not a file: {path}")

        # Set some attributes
        self.path = path
        self.cache_size = cache_size

        # Initialize the diskcache
        self._cache = diskcache.Cache(
            path,
            timeout=30,  # SQLite busy timeout in seconds.
            size_limit=cache_size if cache_size is not None else UNLIMITED_SIZE,
        )

    @staticmethod
    def _check_key(key: Any) -> None:
        """
        Raise TypeError unless key is a string.
        """
        if not isinstance(key, str):
            raise TypeError(f"Key must be str, got {type(key).__name__}.")

    def volume(self) -> int:
        """
        Estimated size of the store on disk, in bytes.
        """
        with self.lock:
            self.require_open()

            # Return the volume of the underlying diskcache
            return self._cache.volume()

    def set(self, key: str, value: Any, expiry: int | float | None = None) -> None:
        """
        Store a value under key with an optional TTL.

        Args:
            key: Cache key.
            value: Value to persist.
            expiry: Seconds until expiry. None means no expiry.

        Raises:
            TypeError: When key is not a string.
            ValueError: When expiry is negative.
        """
        self._check_key(key)

        if expiry is not None and expiry < 0:
            raise ValueError(f"expiry must be >= 0 or None, got {expiry!r}.")

        with self.lock:
            self.require_open()

            # Store the value in the underlying diskcache with the specified expiry
            self._cache.set(key, value, expire=expiry)

    def get(self, key: str, default: Any = None) -> Any:
        """
        Retrieve the value stored under key.

        Args:
            key: Cache key.
            default: Returned when the key is absent or expired.

        Raises:
            TypeError: When key is not a string.
        """
        self._check_key(key)

        with self.lock:
            self.require_open()

            # Return the value from the underlying diskcache, or default if not found
            return self._cache.get(key, default=default)

    def has(self, key: str) -> bool:
        """
        Return True if key exists and has not expired.

        Args:
            key: Cache key.
        """
        self._check_key(key)

        with self.lock:
            self.require_open()

            # Return True if the key exists in the underlying diskcache, otherwise False
            return key in self._cache

    def delete(self, key: str) -> None:
        """
        Remove key from the cache. Silent if absent.

        Args:
            key: Cache key.
        """
        self._check_key(key)

        with self.lock:
            self.require_open()

            # Delete the key from the underlying diskcache
            self._cache.delete(key)

    def pop(self, key: str, default: Any = MISSING) -> Any:
        """
        Retrieve and remove a value (atomic at the SQLite level).

        Args:
            key: Cache key.
            default: Returned when absent. Raises KeyError if omitted.

        Raises:
            KeyError: When the key is missing and no default was given.
        """
        self._check_key(key)

        with self.lock:
            self.require_open()

            # Pop the value from the underlying diskcache, returning default if not found
            value = self._cache.pop(key, default=MISSING)

        if value is MISSING:
            if default is MISSING:
                raise KeyError(key)
            return default
        
        return value

    def clear(self) -> None:
        """
        Evict all entries.
        """
        with self.lock:
            self.require_open()

            # Clear the underlying diskcache
            self._cache.clear()

    def close(self) -> None:
        """
        Flush pending writes and close the underlying store. Idempotent.
        """
        with self.lock:
            if not self.closed:
                self._cache.close()

            # Mark the cache as closed
            super().close()


class ShardedCache(CacheBase):
    """
    Base for caches that spread entries over many PersistentFileCache
    shards, keeping an LRU pool of open shards to bound file handles.

    Args:
        cache_dir: Existing root directory that holds the shards.
        cached_objs_limit: Maximum number of shards kept open at once.
    """

    def __init__(self, cache_dir: str, cached_objs_limit: int = 128):
        super().__init__()

        if not os.path.isdir(cache_dir):
            raise FileNotFoundError(f"Directory not found: {cache_dir}")
        
        if cached_objs_limit < 1:
            raise ValueError("cached_objs_limit must be >= 1.")

        # Set some attributes
        self.cache_dir = cache_dir
        self.cached_objs_limit = cached_objs_limit

        # shard path -> open shard, most recently used at the end.
        self.open_shards: OrderedDict[str, PersistentFileCache] = OrderedDict()

    def get_shard(self, path: str) -> PersistentFileCache:
        """
        Return an open shard for path, closing the least-recently-used
        open shard when the pool is full.

        Args:
            path: Shard directory path.
        """
        with self.lock:
            shard = self.open_shards.get(path)

            if shard is not None and not shard.closed:
                self.open_shards.move_to_end(path)
                return shard

            # Close the shard if it was open but closed, then remove it from the LRU.
            self.open_shards.pop(path, None)

            while len(self.open_shards) >= self.cached_objs_limit:
                _, oldest = self.open_shards.popitem(last=False)

                # Close the oldest shard
                oldest.close()

            # Open a new shard and add it to the LRU
            shard = self.open_shards[path] = PersistentFileCache(path)

            # Return the newly opened shard
            return shard

    def close(self) -> None:
        """
        Close every open shard synchronously. Idempotent.
        """
        with self.lock:
            if not self.closed:
                for shard in self.open_shards.values():
                    try:
                        shard.close()
                    except Exception:
                        pass

                # Clear the open shards dictionary
                self.open_shards.clear()

            # Mark the cache as closed
            super().close()


class DynamicFileCache(ShardedCache):
    """
    Sharded persistent cache that creates a new shard when the newest one
    reaches cache_limit.

    Writes go to the newest shard and reads scan newest to oldest. A write
    deletes the key's copies in older shards, so stale values can never
    shadow a fresh one or reappear after the fresh one expires.

    Args:
        cache_dir: Existing root directory that holds the shard subdirectories.
        cache_limit: Size in bytes at which a shard is considered full.
        cached_objs_limit: Maximum number of shards kept open at once.
    """

    DEFAULT_SHARD_SIZE: int = 1_000_000_000  # 1 GB

    # Shard directories are named '<index>-<hex>'; anything else is ignored.
    SHARD_NAME = re.compile(r"^(\d+)-[0-9a-f]+$")

    def __init__(
        self,
        cache_dir: str,
        cache_limit: int = DEFAULT_SHARD_SIZE,
        cached_objs_limit: int = 128,
    ):
        super().__init__(cache_dir, cached_objs_limit)

        if cache_limit < 1:
            raise ValueError("cache_limit must be >= 1.")

        # Set some attributes
        self.cache_limit = cache_limit
        self.shard_paths: list[Path] = []

        # Rescan cache_dir and refresh shard_paths
        self.reload_shard_paths()

    def reload_shard_paths(self) -> None:
        """
        Rescan cache_dir and refresh shard_paths, ordered numerically
        (oldest first) so index 10 sorts after index 2.
        """
        with self.lock:
            with os.scandir(self.cache_dir) as entries:
                paths = [
                    Path(e.path)
                    for e in entries
                    if e.is_dir() and self.SHARD_NAME.match(e.name)
                ]

            # Sort by numeric index extracted from the directory name, oldest first.
            paths.sort(key=lambda p: int(self.SHARD_NAME.match(p.name).group(1)))

            # Update the shard_paths attribute with the sorted list of shard paths
            self.shard_paths = paths

    def create_new_shard(self) -> str:
        """
        Create a new shard directory and return its path.
        """
        with self.lock:
            last = self.shard_paths[-1].name if self.shard_paths else None
            index = int(self.SHARD_NAME.match(last).group(1)) + 1 if last else 0

            # Get shard directory
            path = Path(self.cache_dir) / f"{index}-{uuid.uuid4().hex[:6]}"

            # Create the directory on disk, including any necessary parent directories
            path.mkdir(parents=True, exist_ok=True)

            # Append the new shard path to the list of shard paths
            self.shard_paths.append(path)

            # Return the string representation of the new shard path
            return str(path)

    def get_writable_shard_path(self) -> str:
        """
        Return the newest shard's path if it has room, else a new shard's.
        """
        with self.lock:
            if self.shard_paths:
                newest = str(self.shard_paths[-1])

                if self.get_shard(newest).volume() < self.cache_limit:
                    return newest

            # Return a new shard path
            return self.create_new_shard()

    def set(self, key: str, value: Any, expiry: int | float | None = None) -> None:
        """
        Write key to the newest shard and remove its copies elsewhere.

        Args:
            key: Cache key.
            value: Value to persist.
            expiry: Seconds until expiry. None means no expiry.
        """
        with self.lock:
            self.require_open()

            # Determine the writable shard path (newest or new shard)
            newest = self.get_writable_shard_path()

            # Newest is always last, so every other shard may hold a stale copy.
            for path in self.shard_paths:
                if str(path) != newest:
                    self.get_shard(str(path)).delete(key)

            # Write the key-value pair to the newest shard with the specified expiry
            self.get_shard(newest).set(key, value, expiry)

    def get(self, key: str, default: Any = None) -> Any:
        """
        Search shards newest to oldest and return the first hit.

        Args:
            key: Cache key.
            default: Returned when the key is not found in any shard.
        """
        with self.lock:
            self.require_open()

            for path in reversed(self.shard_paths):
                value = self.get_shard(str(path)).get(key, MISSING)

                if value is not MISSING:
                    return value

            # Return the default value if the key was not found in any shard
            return default

    def delete(self, key: str) -> None:
        """
        Delete key from every shard.

        Args:
            key: Cache key.
        """
        with self.lock:
            self.require_open()

            for path in self.shard_paths:
                self.get_shard(str(path)).delete(key)

    def pop(self, key: str, default: Any = MISSING) -> Any:
        """
        Remove key from every shard and return its newest value.

        Args:
            key: Cache key.
            default: Returned when absent. Raises KeyError if omitted.

        Raises:
            KeyError: When the key is missing and no default was given.
        """
        with self.lock:
            self.require_open()

            # Set the sentinel value to indicate that the key was not found in any shard
            found = MISSING

            for path in reversed(self.shard_paths):
                value = self.get_shard(str(path)).pop(key, MISSING)

                # Keep the newest value; older hits are stale copies.
                if found is MISSING:
                    found = value

        if found is MISSING:
            if default is MISSING:
                raise KeyError(key)
            return default

        # Return the newest value found in the shards
        return found

    def clear(self) -> None:
        """
        Evict all entries from every shard.
        """
        with self.lock:
            self.require_open()

            for path in self.shard_paths:
                self.get_shard(str(path)).clear()


class KeyAsFolderCache(ShardedCache):
    """
    Persistent cache storing each key in its own subdirectory.

    Folders are named '<sanitized-key>-<sha256 prefix>', so any key is
    safe (slashes, '..', unicode, very long keys) and cannot escape
    cache_dir. The original key is stored inside the folder's cache.

    Folders are discovered on demand, so entries written by other
    processes are visible. clear() only removes folders matching this
    naming scheme.

    Args:
        cache_dir: Existing root directory for per-key subdirectories.
        cached_objs_limit: Maximum number of shards kept open at once.
    """

    DEFAULT_CACHE_OBJ_LIMIT: int = 128
    DIR_NAME = re.compile(r"^.*-[0-9a-f]{16}$")

    def __init__(self, cache_dir: str, cached_objs_limit: int = DEFAULT_CACHE_OBJ_LIMIT):
        super().__init__(cache_dir, cached_objs_limit)

    def get_key_dir(self, key: str) -> str:
        """
        Return the filesystem-safe subdirectory path for key.

        Args:
            key: Cache key.
        """
        slug = re.sub(r"[^\w\-]", "_", key)[:60]
        digest = hashlib.sha256(key.encode()).hexdigest()[:16]

        # Return the path to the subdirectory for the given key, combining the cache directory, slug, and digest.
        return joinpaths(self.cache_dir, f"{slug}-{digest}")

    def live_key_dirs(self) -> list[Path]:
        """
        Return a fresh snapshot of all per-key subdirectories on disk.
        """
        with os.scandir(self.cache_dir) as entries:
            return [
                Path(e.path)
                for e in entries
                if e.is_dir() and self.DIR_NAME.match(e.name)
            ]

    def remove_key_dir(self, key_dir: str) -> None:
        """
        Close the shard for key_dir and delete the directory from disk.

        Args:
            key_dir: Per-key directory path.
        """
        with self.lock:
            shard = self.open_shards.pop(key_dir, None)

            if shard is not None:
                shard.close()  # Close before deleting its files.
            
            # Remove the directory and its contents from disk, ignoring errors if it doesn't exist.
            shutil.rmtree(key_dir, ignore_errors=True)

    def set(self, key: str, value: Any, expiry: int | float | None = None) -> None:
        """
        Store value in the subdirectory for key.

        Args:
            key: Cache key.
            value: Value to persist.
            expiry: Seconds until expiry. None means no expiry.
        """
        with self.lock:
            self.require_open()

            # Determine the directory path for the given key
            key_dir = self.get_key_dir(key)

            # Create the directory on disk if it doesn't exist, including any necessary parent directories
            os.makedirs(key_dir, exist_ok=True)

            # Store the key-value pair in the shard corresponding to the key's directory, with the specified expiry
            self.get_shard(key_dir).set(key, value, expiry)

    def get(self, key: str, default: Any = None) -> Any:
        """
        Retrieve the value for key, removing its folder if it has expired
        so stale directories do not accumulate.

        Args:
            key: Cache key.
            default: Returned when the key is absent or expired.
        """
        with self.lock:
            self.require_open()

            # Determine the directory path for the given key
            key_dir = self.get_key_dir(key)

            if not os.path.isdir(key_dir):
                return default

            # Retrieve the value from the shard corresponding to the key's directory, returning MISSING if not found
            value = self.get_shard(key_dir).get(key, MISSING)

            if value is MISSING:
                self.remove_key_dir(key_dir)
                return default

            return value

    def delete(self, key: str) -> None:
        """
        Remove the key's folder from disk. Silent if absent.

        Args:
            key: Cache key.
        """
        with self.lock:
            self.require_open()

            # Determine the directory path for the given key
            key_dir = self.get_key_dir(key)

            if os.path.isdir(key_dir):
                # Remove the key's directory and its contents from disk
                self.remove_key_dir(key_dir)

    def pop(self, key: str, default: Any = MISSING) -> Any:
        """
        Retrieve a value and remove its folder.

        Args:
            key: Cache key.
            default: Returned when absent. Raises KeyError if omitted.

        Raises:
            KeyError: When the key is missing and no default was given.
        """
        with self.lock:
            value = self.get(key, MISSING)

            if value is MISSING:
                if default is MISSING:
                    raise KeyError(key)
                return default

            # Remove the key's directory and its contents from disk
            self.delete(key)

            # Return the retrieved value
            return value

    def clear(self) -> None:
        """
        Remove every per-key folder.
        """
        with self.lock:
            self.require_open()

            for key_dir in self.live_key_dirs():
                self.remove_key_dir(str(key_dir))
