"""
Caching module built on top of the diskcache library.

Provides a hierarchy of cache backends ranging from pure in-memory LRU
caches to persistent file-backed caches with dynamic sharding and
key-as-folder storage strategies.

Every public method is safe to call from multiple threads or async tasks
simultaneously. Sync callers use threading.RLock; async callers use
asyncio.Lock via the async_* variants exposed on each class.
"""

import os
import uuid
import shutil
import asyncio
import datetime
import threading

from typing import Any
from pathlib import Path
from collections import OrderedDict, deque
from functools import lru_cache

import diskcache


# Sentinel used to detect "no default provided" without conflicting with None.
MISSING = object()


class CacheBase:
    """
    Abstract base class that all cache backends must implement.

    Subclasses must override set, get, delete, pop, and clear.
    The save() hook is optional and is a no-op by default.

    Locking strategy:
        Each subclass owns a threading.RLock (sync) and an asyncio.Lock
        (async). The RLock is reentrant so that methods which call other
        locking methods on the same instance do not deadlock.
    """

    def save(self):
        """
        Optional persistence hook. No-op unless overridden.
        """

    def set(self, key: str, value: Any, expiry: int | float | None = None) -> None:
        """
        Store a value under key with an optional TTL in seconds.

        Args:
            key: Cache key.
            value: Value to store.
            expiry: Seconds until the entry expires. None means no expiry.
        """
        raise NotImplementedError(
            f"'set' is not implemented on {self.__class__.__name__}."
        )

    def get(self, key: str, default: Any = None) -> Any:
        """
        Retrieve the value stored under key.

        Args:
            key: Cache key to look up.
            default: Returned when the key is absent or expired.

        Returns:
            The cached value or default.
        """
        raise NotImplementedError(
            f"'get' is not implemented on {self.__class__.__name__}."
        )

    def delete(self, key: str) -> None:
        """
        Remove key from the cache. Silent if the key does not exist.

        Args:
            key: Cache key to remove.
        """
        raise NotImplementedError(
            f"'delete' is not implemented on {self.__class__.__name__}."
        )

    def pop(self, key: str, default: Any = MISSING) -> Any:
        """
        Retrieve and atomically remove a value from the cache.

        Args:
            key: Cache key to retrieve and delete.
            default: Returned when the key is absent. Raises KeyError
                if omitted and the key does not exist.

        Returns:
            The cached value, or default when the key is absent.

        Raises:
            KeyError: When the key is missing and no default was given.
        """
        raise NotImplementedError(
            f"'pop' is not implemented on {self.__class__.__name__}."
        )

    def clear(self) -> None:
        """
        Evict all entries from the cache.
        """
        raise NotImplementedError(
            f"'clear' is not implemented on {self.__class__.__name__}."
        )


class InMemoryCache(CacheBase):
    """
    Thread-safe in-memory cache with LRU eviction.

    Entries are stored in an OrderedDict so that the least-recently-used
    key can be evicted in O(1) when the cache is full. An optional expiry
    map records per-key TTLs and is checked on every read.

    Args:
        maxkeys: Maximum number of keys before LRU eviction kicks in.
            None means unbounded.
    """

    def __init__(self, maxkeys: int | None = None):
        self.maxkeys = maxkeys

        # Ordered mapping of key ➝ value (most-recently-used at the end).
        self.cache: OrderedDict[str, Any] = OrderedDict()

        # Per-key expiry timestamps.
        self.expiry_map: dict[str, datetime.datetime] = {}

        # RLock so that pop() (which calls get then delete) does not
        # deadlock when both methods acquire the same lock.
        self.lock = threading.RLock()
        self.async_lock = asyncio.Lock()

    # Internal helpers

    def _is_expired(self, key: str) -> bool:
        """
        Check whether a key has passed its expiry without side effects.

        Args:
            key: Cache key to inspect.

        Returns:
            True if the key has an expiry that has already elapsed.
        """
        expiry_dt = self.expiry_map.get(key)
        return expiry_dt is not None and datetime.datetime.now() >= expiry_dt

    def _evict(self, key: str) -> None:
        """
        Remove a key from both the cache and the expiry map.

        Args:
            key: Cache key to evict.
        """
        self.cache.pop(key, None)
        self.expiry_map.pop(key, None)

    # Public interface

    def set(self, key: str, value: Any, expiry: int | float | None = None) -> None:
        """
        Insert or update key with an optional TTL.

        Args:
            key: Cache key.
            value: Value to store.
            expiry: Seconds until expiry. None means the entry lives forever.
        """
        with self.lock:
            # Move existing key to the end (most-recently-used position).
            if key in self.cache:
                self.cache.move_to_end(key)

            self.cache[key] = value

            # Record or clear expiry.
            if expiry is not None:
                self.expiry_map[key] = (
                    datetime.datetime.now() + datetime.timedelta(seconds=expiry)
                )
            else:
                self.expiry_map.pop(key, None)

            # Evict the oldest entry when over capacity.
            if self.maxkeys and len(self.cache) > self.maxkeys:
                oldest_key, _ = self.cache.popitem(last=False)
                self.expiry_map.pop(oldest_key, None)

    def get(self, key: str, default: Any = None) -> Any:
        """
        Retrieve the value for key, evicting it first if expired.

        Args:
            key: Cache key to look up.
            default: Returned when the key is absent or expired.

        Returns:
            The cached value or default.
        """
        with self.lock:
            if self._is_expired(key):
                self._evict(key)
                return default

            if key in self.cache:
                self.cache.move_to_end(key)
                return self.cache[key]

            return default

    def has(self, key: str) -> bool:
        """
        Return True if key exists and has not expired.

        Args:
            key: Cache key to probe.

        Returns:
            True when the key is present and live.
        """
        with self.lock:
            if self._is_expired(key):
                self._evict(key)
                return False
            return key in self.cache

    def delete(self, key: str) -> None:
        """
        Remove key from the cache. Silent if absent.

        Args:
            key: Cache key to remove.
        """
        with self.lock:
            self._evict(key)

    def pop(self, key: str, default: Any = MISSING) -> Any:
        """
        Retrieve and atomically remove a value.

        The entire read-then-delete sequence is held under one lock
        acquisition so no concurrent caller can observe the key between
        the two operations.

        Args:
            key: Cache key to retrieve and delete.
            default: Returned when the key is absent. Raises KeyError
                if omitted and the key does not exist.

        Returns:
            The cached value, or default when absent.

        Raises:
            KeyError: When the key is missing and no default was provided.
        """
        with self.lock:
            # Honour TTL before the pop.
            if self._is_expired(key):
                self._evict(key)
                if default is MISSING:
                    raise KeyError(key)
                return default

            if key not in self.cache:
                if default is MISSING:
                    raise KeyError(key)
                return default

            value = self.cache[key]
            self._evict(key)
            return value

    def clear(self) -> None:
        """
        Evict all entries from the cache.
        """
        with self.lock:
            self.cache.clear()
            self.expiry_map.clear()

    # Async variants

    async def async_set(
        self, key: str, value: Any, expiry: int | float | None = None
    ) -> None:
        """
        Async-safe version of set.

        Args:
            key: Cache key.
            value: Value to store.
            expiry: TTL in seconds.
        """
        async with self.async_lock:
            self.set(key, value, expiry)

    async def async_get(self, key: str, default: Any = None) -> Any:
        """
        Async-safe version of get.

        Args:
            key: Cache key to look up.
            default: Returned when absent or expired.

        Returns:
            The cached value or default.
        """
        async with self.async_lock:
            return self.get(key, default)

    async def async_pop(self, key: str, default: Any = MISSING) -> Any:
        """
        Async-safe version of pop.

        Args:
            key: Cache key to retrieve and delete.
            default: Returned when absent. Raises KeyError if omitted.

        Returns:
            The cached value or default.

        Raises:
            KeyError: When the key is missing and no default was provided.
        """
        async with self.async_lock:
            return self.pop(key, default)

    async def async_delete(self, key: str) -> None:
        """
        Async-safe version of delete.

        Args:
            key: Cache key to remove.
        """
        async with self.async_lock:
            self.delete(key)

    async def async_clear(self) -> None:
        """
        Async-safe version of clear.
        """
        async with self.async_lock:
            self.clear()

    def close(self) -> None:
        """
        Release all resources held by this cache instance.
        """
        self.clear()


class PersistentFileCache(CacheBase):
    """
    Persistent file-backed cache powered by the diskcache library.

    All operations are serialised behind a threading.RLock so the
    underlying SQLite connection is never accessed from two threads
    simultaneously. diskcache itself is thread-safe, but the RLock
    also makes our own pop() atomic at the Python level.

    Args:
        path: Directory path used as the cache store.
        cache_size: Maximum size in bytes. None means unlimited.
    """

    def __init__(self, path: str, cache_size: int | None = None):
        if os.path.isfile(path):
            raise FileExistsError(
                f"Path must be a directory, not a file: {path}"
            )

        self.path = path
        self.cache_size = cache_size

        self.closed = False
        self.lock = threading.RLock()
        self.async_lock = asyncio.Lock()

        # Open the diskcache store.
        kwargs: dict[str, Any] = {"sqlite_timeout": 30}
        if cache_size is not None:
            kwargs["size_limit"] = cache_size

        self.inner_cache = diskcache.Cache(path, **kwargs)

    def _require_open(self) -> None:
        """
        Guard that raises RuntimeError when the cache has been closed.
        """
        if self.closed:
            raise RuntimeError(
                f"Operation on a closed PersistentFileCache at {self.path!r}."
            )

    def set(self, key: str, value: Any, expiry: int | float | None = None) -> None:
        """
        Store a value under key with an optional TTL.

        Args:
            key: Cache key (must be a str).
            value: Value to persist.
            expiry: Seconds until the entry expires.

        Raises:
            KeyError: When key is not a string.
            RuntimeError: When the cache is closed.
        """
        if not isinstance(key, str):
            raise KeyError(f"Key must be str, got {type(key).__name__}.")

        with self.lock:
            self._require_open()
            self.inner_cache.set(key, value, expire=expiry)

    def get(self, key: str, default: Any = None) -> Any:
        """
        Retrieve the value stored under key.

        Args:
            key: Cache key (must be a str).
            default: Returned when the key is absent or expired.

        Returns:
            The cached value or default.

        Raises:
            KeyError: When key is not a string.
            RuntimeError: When the cache is closed.
        """
        if not isinstance(key, str):
            raise KeyError(f"Key must be str, got {type(key).__name__}.")

        with self.lock:
            self._require_open()
            # diskcache.Cache.get accepts a default and returns it on miss.
            return self.inner_cache.get(key, default=default)

    def delete(self, key: str) -> None:
        """
        Remove key from the cache. Silent if absent.

        Args:
            key: Cache key to remove.

        Raises:
            RuntimeError: When the cache is closed.
        """
        with self.lock:
            self._require_open()
            self.inner_cache.delete(key)

    def pop(self, key: str, default: Any = MISSING) -> Any:
        """
        Retrieve and atomically remove a value.

        Uses diskcache's own pop() which is atomic at the SQLite level,
        then falls back to KeyError / default handling.

        Args:
            key: Cache key to retrieve and delete.
            default: Returned when absent. Raises KeyError if omitted.

        Returns:
            The cached value or default.

        Raises:
            KeyError: When the key is missing and no default was provided.
            RuntimeError: When the cache is closed.
        """
        with self.lock:
            self._require_open()

            # diskcache.Cache.pop accepts a default sentinel.
            value = self.inner_cache.pop(key, default=MISSING)

            if value is MISSING:
                if default is MISSING:
                    raise KeyError(key)
                return default

            return value

    def clear(self) -> None:
        """
        Evict all entries from the cache.

        Raises:
            RuntimeError: When the cache is closed.
        """
        with self.lock:
            self._require_open()
            self.inner_cache.clear()

    # Async variants

    async def async_set(
        self, key: str, value: Any, expiry: int | float | None = None
    ) -> None:
        """
        Async-safe version of set.

        Args:
            key: Cache key.
            value: Value to persist.
            expiry: TTL in seconds.
        """
        async with self.async_lock:
            self.set(key, value, expiry)

    async def async_get(self, key: str, default: Any = None) -> Any:
        """
        Async-safe version of get.

        Args:
            key: Cache key to look up.
            default: Returned when absent or expired.

        Returns:
            The cached value or default.
        """
        async with self.async_lock:
            return self.get(key, default)

    async def async_pop(self, key: str, default: Any = MISSING) -> Any:
        """
        Async-safe version of pop.

        Args:
            key: Cache key to retrieve and delete.
            default: Returned when absent. Raises KeyError if omitted.

        Returns:
            The cached value or default.

        Raises:
            KeyError: When the key is missing and no default was provided.
        """
        async with self.async_lock:
            return self.pop(key, default)

    async def async_delete(self, key: str) -> None:
        """
        Async-safe version of delete.

        Args:
            key: Cache key to remove.
        """
        async with self.async_lock:
            self.delete(key)

    async def async_clear(self) -> None:
        """
        Async-safe version of clear.
        """
        async with self.async_lock:
            self.clear()

    def close(self) -> None:
        """
        Flush pending writes and close the underlying diskcache store.
        """
        with self.lock:
            if not self.closed:
                self.closed = True
                self.inner_cache.close()


class DynamicFileCache(CacheBase):
    """
    Sharded persistent cache that automatically creates new shard
    directories when existing ones reach a configured size limit.

    Each shard is a PersistentFileCache instance. Shards are created
    lazily and are never deleted. Reads scan shards from newest to
    oldest so the most-recently-written value is returned first.

    The lru_cache on get_cache_obj is intentionally not used here
    because closed PersistentFileCache objects must not be returned
    from a cache. Shard instances are tracked in a plain dict instead.

    Args:
        cache_dir: Root directory that will hold shard subdirectories.
        cache_limit: Maximum size in bytes per shard. Defaults to 1 GB.
        cached_objs_limit: Maximum number of shard objects kept open
            simultaneously. Oldest is closed when the limit is exceeded.
    """

    DEFAULT_SHARD_SIZE: int = 1_000_000_000  # 1 GB

    def __init__(
        self,
        cache_dir: str,
        cache_limit: int = DEFAULT_SHARD_SIZE,
        cached_objs_limit: int = 128,
    ):
        if not os.path.isdir(cache_dir):
            raise FileNotFoundError(f"Directory not found: {cache_dir}")

        self.cache_dir = cache_dir
        self.cache_limit = cache_limit

        # Ordered mapping of shard path ➝ PersistentFileCache.
        # Using an OrderedDict so we can evict the oldest open shard
        # when cached_objs_limit is reached.
        self.open_shards: OrderedDict[str, PersistentFileCache] = OrderedDict()
        self.cached_objs_limit = cached_objs_limit

        self.lock = threading.RLock()
        self.async_lock = asyncio.Lock()

        # Discover pre-existing shard directories.
        self.shard_paths: list[Path] = []
        self.reload_shard_paths()

    def reload_shard_paths(self) -> None:
        """
        Scan cache_dir and refresh the ordered list of shard paths.

        Called at construction time and whenever a new shard is created
        so the shard list is always current.
        """
        paths = [
            Path(entry.path)
            for entry in os.scandir(self.cache_dir)
            if entry.is_dir()
        ]
        paths.sort()
        self.shard_paths = paths

    def get_writable_shard_path(self) -> str:
        """
        Return the path of a shard that has not yet reached cache_limit.

        Creates a new shard directory if all existing shards are full.

        Returns:
            Absolute path string of the target shard directory.
        """
        for shard_path in self.shard_paths:
            try:
                size = sum(f.stat().st_size for f in shard_path.iterdir())
            except OSError:
                continue
            if size < self.cache_limit:
                return str(shard_path)

        # All shards full — create a new one.
        return self.create_new_shard()

    def create_new_shard(self) -> str:
        """
        Create a new uniquely named shard directory inside cache_dir.

        Returns:
            Absolute path string of the newly created shard directory.
        """
        name = f"{len(self.shard_paths)}-{uuid.uuid4().hex[:6]}"
        path = os.path.join(self.cache_dir, name)
        os.makedirs(path, exist_ok=True)

        # Keep the shard list up to date.
        self.shard_paths.append(Path(path))
        return path

    def get_shard(self, path: str) -> PersistentFileCache:
        """
        Return an open PersistentFileCache for the given shard path.

        Evicts the least-recently-used open shard when the open-shard
        limit is exceeded to avoid unbounded file-handle accumulation.

        Args:
            path: Absolute shard directory path.

        Returns:
            An open PersistentFileCache instance for that path.
        """
        if path in self.open_shards:
            # Move to end so it is the most-recently-used.
            self.open_shards.move_to_end(path)
            return self.open_shards[path]

        # Evict the oldest open shard if we are at the limit.
        if len(self.open_shards) >= self.cached_objs_limit:
            _, oldest = self.open_shards.popitem(last=False)
            if not oldest.closed:
                oldest.close()

        shard = PersistentFileCache(path)
        self.open_shards[path] = shard
        return shard

    def set(self, key: str, value: Any, expiry: int | float | None = None) -> None:
        """
        Write key to the current writable shard.

        Args:
            key: Cache key.
            value: Value to persist.
            expiry: TTL in seconds.
        """
        with self.lock:
            path = self.get_writable_shard_path()
            self.get_shard(path).set(key, value, expiry)

    def get(self, key: str, default: Any = None) -> Any:
        """
        Search all shards from newest to oldest and return the first hit.

        Args:
            key: Cache key to look up.
            default: Returned when the key is not found in any shard.

        Returns:
            The cached value or default.
        """
        with self.lock:
            for shard_path in reversed(self.shard_paths):
                shard = self.get_shard(str(shard_path))
                value = shard.get(key)
                if value is not None:
                    return value
            return default

    def delete(self, key: str) -> None:
        """
        Delete key from every shard that holds it.

        Args:
            key: Cache key to remove.
        """
        with self.lock:
            for shard_path in self.shard_paths:
                try:
                    self.get_shard(str(shard_path)).delete(key)
                except Exception:
                    pass

    def pop(self, key: str, default: Any = MISSING) -> Any:
        """
        Retrieve the first occurrence of key (newest shard first) and
        delete it from all shards atomically under the instance lock.

        Args:
            key: Cache key to retrieve and delete.
            default: Returned when absent. Raises KeyError if omitted.

        Returns:
            The cached value, or default when absent.

        Raises:
            KeyError: When the key is missing and no default was provided.
        """
        with self.lock:
            # Find the value from the newest shard first.
            value = MISSING
            for shard_path in reversed(self.shard_paths):
                candidate = self.get_shard(str(shard_path)).get(key)
                if candidate is not None:
                    value = candidate
                    break

            if value is MISSING:
                if default is MISSING:
                    raise KeyError(key)
                return default

            # Remove from all shards so no stale copies remain.
            self.delete(key)
            return value

    def clear(self) -> None:
        """
        Evict all entries from every shard.
        """
        with self.lock:
            for shard_path in self.shard_paths:
                try:
                    self.get_shard(str(shard_path)).clear()
                except Exception:
                    pass

    # Async variants

    async def async_set(
        self, key: str, value: Any, expiry: int | float | None = None
    ) -> None:
        """
        Async-safe version of set.

        Args:
            key: Cache key.
            value: Value to persist.
            expiry: TTL in seconds.
        """
        async with self.async_lock:
            self.set(key, value, expiry)

    async def async_get(self, key: str, default: Any = None) -> Any:
        """
        Async-safe version of get.

        Args:
            key: Cache key to look up.
            default: Returned when absent.

        Returns:
            The cached value or default.
        """
        async with self.async_lock:
            return self.get(key, default)

    async def async_pop(self, key: str, default: Any = MISSING) -> Any:
        """
        Async-safe version of pop.

        Args:
            key: Cache key to retrieve and delete.
            default: Returned when absent. Raises KeyError if omitted.

        Returns:
            The cached value or default.

        Raises:
            KeyError: When the key is missing and no default was provided.
        """
        async with self.async_lock:
            return self.pop(key, default)

    async def async_delete(self, key: str) -> None:
        """
        Async-safe version of delete.

        Args:
            key: Cache key to remove.
        """
        async with self.async_lock:
            self.delete(key)

    async def async_clear(self) -> None:
        """
        Async-safe version of clear.
        """
        async with self.async_lock:
            self.clear()

    def close(self) -> None:
        """
        Close all open shard handles in a background daemon thread.

        Returns immediately; actual closing happens asynchronously so
        that long-running shard close operations do not block the caller.
        """
        with self.lock:
            shards_to_close = list(self.open_shards.values())
            self.open_shards.clear()

        def close_all(shards: list[PersistentFileCache]) -> None:
            for shard in shards:
                try:
                    if not shard.closed:
                        shard.close()
                except Exception:
                    pass

        thread = threading.Thread(target=close_all, args=(shards_to_close,), daemon=True)
        thread.start()


class KeyAsFolderCache(CacheBase):
    """
    Persistent cache that stores each key's data in a dedicated
    subdirectory named after the key itself.

    This makes it trivially easy to inspect, backup, or delete a single
    cache entry on disk. Each subdirectory is managed by its own
    PersistentFileCache instance.

    Unlike DynamicFileCache, the per-key shard mapping is rebuilt from
    disk on every operation via a fresh os.scandir(), so new entries
    written by other processes are always visible.

    Args:
        cache_dir: Root directory under which per-key subdirectories
            will be created.
        cached_objs_limit: Maximum number of PersistentFileCache
            instances to keep open at once.
    """

    DEFAULT_CACHE_OBJ_LIMIT: int = 128

    def __init__(
        self,
        cache_dir: str,
        cached_objs_limit: int = DEFAULT_CACHE_OBJ_LIMIT,
    ):
        if not os.path.isdir(cache_dir):
            raise FileNotFoundError(f"Directory not found: {cache_dir}")

        self.cache_dir = cache_dir
        self.cached_objs_limit = cached_objs_limit

        # LRU mapping of shard path ➝ PersistentFileCache.
        self.open_shards: OrderedDict[str, PersistentFileCache] = OrderedDict()

        self.lock = threading.RLock()
        self.async_lock = asyncio.Lock()

    def get_key_dir(self, key: str) -> str:
        """
        Return the absolute path of the subdirectory for key.

        Args:
            key: Cache key.

        Returns:
            Absolute directory path string.
        """
        return os.path.join(self.cache_dir, key)

    def get_shard(self, path: str) -> PersistentFileCache:
        """
        Return an open PersistentFileCache for the given directory path.

        Evicts the least-recently-used shard when the open-shard limit
        is exceeded.

        Args:
            path: Absolute directory path for the shard.

        Returns:
            An open PersistentFileCache for that path.
        """
        if path in self.open_shards:
            self.open_shards.move_to_end(path)
            return self.open_shards[path]

        if len(self.open_shards) >= self.cached_objs_limit:
            _, oldest = self.open_shards.popitem(last=False)
            if not oldest.closed:
                oldest.close()

        shard = PersistentFileCache(path)
        self.open_shards[path] = shard
        return shard

    def live_key_dirs(self) -> list[Path]:
        """
        Return a snapshot of all current per-key subdirectories.

        Performs a fresh os.scandir() on every call so newly created
        keys (including those from other processes) are always included.

        Returns:
            List of Path objects, one per existing key subdirectory.
        """
        return [
            Path(entry.path)
            for entry in os.scandir(self.cache_dir)
            if entry.is_dir()
        ]

    def set(self, key: str, value: Any, expiry: int | float | None = None) -> None:
        """
        Store value in a subdirectory named after key.

        Creates the subdirectory if it does not already exist.

        Args:
            key: Cache key (used as the subdirectory name).
            value: Value to persist.
            expiry: TTL in seconds.
        """
        with self.lock:
            key_dir = self.get_key_dir(key)
            os.makedirs(key_dir, exist_ok=True)
            self.get_shard(key_dir).set(key, value, expiry)

    def get(self, key: str, default: Any = None) -> Any:
        """
        Retrieve the value stored under key.

        Removes the on-disk subdirectory if the key has expired so that
        stale directories do not accumulate.

        Args:
            key: Cache key to look up.
            default: Returned when the key is absent or expired.

        Returns:
            The cached value or default.
        """
        with self.lock:
            key_dir = self.get_key_dir(key)

            if not os.path.isdir(key_dir):
                return default

            shard = self.get_shard(key_dir)
            value = shard.get(key)

            if value is None:
                # Key has expired — clean up the on-disk remnant.
                self._remove_key_dir(key_dir)
                return default

            return value

    def delete(self, key: str) -> None:
        """
        Remove key's subdirectory from disk. Silent if absent.

        Args:
            key: Cache key to remove.
        """
        with self.lock:
            key_dir = self.get_key_dir(key)
            if os.path.isdir(key_dir):
                self._remove_key_dir(key_dir)

    def pop(self, key: str, default: Any = MISSING) -> Any:
        """
        Retrieve and atomically remove a value and its on-disk folder.

        Args:
            key: Cache key to retrieve and delete.
            default: Returned when absent. Raises KeyError if omitted.

        Returns:
            The cached value or default.

        Raises:
            KeyError: When the key is missing and no default was provided.
        """
        with self.lock:
            value = self.get(key)

            if value is None:
                if default is MISSING:
                    raise KeyError(key)
                return default

            self.delete(key)
            return value

    def clear(self) -> None:
        """
        Evict all entries by clearing every per-key shard.
        """
        with self.lock:
            for key_dir in self.live_key_dirs():
                try:
                    shard = self.get_shard(str(key_dir))
                    shard.clear()
                except Exception:
                    pass

    def _remove_key_dir(self, key_dir: str) -> None:
        """
        Close the shard for key_dir, evict it from open_shards, and
        remove the directory tree from disk.

        Args:
            key_dir: Absolute path of the per-key directory to remove.
        """
        # Close the shard before deleting its files.
        shard = self.open_shards.pop(key_dir, None)
        if shard and not shard.closed:
            try:
                shard.close()
            except Exception:
                pass

        try:
            shutil.rmtree(key_dir)
        except OSError:
            pass

    # Async variants

    async def async_set(
        self, key: str, value: Any, expiry: int | float | None = None
    ) -> None:
        """
        Async-safe version of set.

        Args:
            key: Cache key.
            value: Value to persist.
            expiry: TTL in seconds.
        """
        async with self.async_lock:
            self.set(key, value, expiry)

    async def async_get(self, key: str, default: Any = None) -> Any:
        """
        Async-safe version of get.

        Args:
            key: Cache key to look up.
            default: Returned when absent or expired.

        Returns:
            The cached value or default.
        """
        async with self.async_lock:
            return self.get(key, default)

    async def async_pop(self, key: str, default: Any = MISSING) -> Any:
        """
        Async-safe version of pop.

        Args:
            key: Cache key to retrieve and delete.
            default: Returned when absent. Raises KeyError if omitted.

        Returns:
            The cached value or default.

        Raises:
            KeyError: When the key is missing and no default was provided.
        """
        async with self.async_lock:
            return self.pop(key, default)

    async def async_delete(self, key: str) -> None:
        """
        Async-safe version of delete.

        Args:
            key: Cache key to remove.
        """
        async with self.async_lock:
            self.delete(key)

    async def async_clear(self) -> None:
        """
        Async-safe version of clear.
        """
        async with self.async_lock:
            self.clear()

    def close(self) -> None:
        """
        Close all open shard handles in a background daemon thread.
        """
        with self.lock:
            shards_to_close = list(self.open_shards.values())
            self.open_shards.clear()

        def close_all(shards: list[PersistentFileCache]) -> None:
            for shard in shards:
                try:
                    if not shard.closed:
                        shard.close()
                except Exception:
                    pass

        thread = threading.Thread(target=close_all, args=(shards_to_close,), daemon=True)
        thread.start()


class CacheSpeedTest:
    """
    This class performs speed test of Cache classes.
    """
    
    instances = [
        InMemoryCache,
        DynamicFileCache,
        KeyAsFolderCache,
    ]

    def __init__(self, repeat: int = 1):
        self.repeat = repeat
        self.key = self.generate_random_string(32)
        self.results = {}  # Store results for comparison

    @staticmethod
    def generate_random_string(length):
        letters = string.ascii_lowercase
        return "".join(random.choice(letters) for _ in range(length))

    def test_create(self, instance):
        start = time.time()
        instance = instance("./test")
        stop = time.time()
        elapse = stop - start
        # cleanup
        instance.clear()
        return elapse

    def test_set(self, instance):
        data = self.generate_random_string(1024)
        instance = instance("./test")
        start = time.time()
        instance.set(self.key, data)
        stop = time.time()
        elapse = stop - start
        return elapse

    def test_get(self, instance):
        instance = instance("./test")
        start = time.time()
        _ = instance.get(self.key)
        stop = time.time()
        elapse = stop - start
        return elapse

    def test_del(self, instance):
        instance = instance("./test")
        start = time.time()
        _ = instance.delete(self.key)
        stop = time.time()
        elapse = stop - start
        return elapse

    def test_clear(self, instance):
        instance = instance("./test")
        start = time.time()
        _ = instance.clear()
        stop = time.time()
        elapse = stop - start
        return elapse

    def run_test(self, instance):
        create_t = 0
        set_t = 0
        get_t = 0
        del_t = 0
        clear_t = 0

        for i in range(self.repeat):
            create_t += self.test_create(instance)
            set_t += self.test_set(instance)
            get_t += self.test_get(instance)
            del_t += self.test_del(instance)
            clear_t += self.test_clear(instance)
            self.key = self.generate_random_string(32)

        # Store results
        self.results[instance.__name__] = {
            "create": create_t / self.repeat,
            "set": set_t / self.repeat,
            "get": get_t / self.repeat,
            "delete": del_t / self.repeat,
            "clear": clear_t / self.repeat,
        }

    def execute_all(self):
        print("Running caching speed tests...")
        os.makedirs("./test", exist_ok=True)
        for instance in self.instances:
            self.run_test(instance)
        self.print_summary()
        self.compare_performance()

    def print_summary(self):
        print("\nOverall Performance Summary:")
        for instance_name, result in self.results.items():
            print(f"\n[{instance_name}]")
            print(
                f"Create  for {self.repeat} item(s): {result['create']} seconds"
            )
            print(
                f"Set     for {self.repeat} item(s): {result['set']} seconds")
            print(
                f"Get     for {self.repeat} item(s): {result['get']} seconds")
            print(
                f"Delete  for {self.repeat} item(s): {result['delete']} seconds"
            )
            print(
                f"Clear   for {self.repeat} item(s): {result['clear']} seconds"
            )

    def compare_performance(self):
        fastest_instance = {}

        for operation in ["create", "set", "get", "delete", "clear"]:
            min_time = float("inf")
            fastest = None

            for instance_name, times in self.results.items():
                if times[operation] < min_time:
                    min_time = times[operation]
                    fastest = instance_name

            fastest_instance[operation] = (fastest, min_time)

        print("\nFastest Instances for Each Operation:")
        for operation, (instance_name, min_time) in fastest_instance.items():
            print(
                f"{operation.capitalize():<6}: {instance_name} with {min_time:.6f} seconds"
            )
