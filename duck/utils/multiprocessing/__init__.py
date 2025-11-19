"""
ProcessSafeLRUCache: A process-safe, shared-memory LRU cache for Python multi-process applications.

This class allows multiple processes to share and update a central in-memory cache,
with Least Recently Used (LRU) eviction and optional per-key expiry, using Python's
`multiprocessing.Manager` for process safety.

Features:
- Process-safe via Manager-proxied dicts and lists.
- True LRU eviction: oldest unused entry is removed once maxkeys is exceeded.
- Optional per-key expiry: keys are removed after a set time.
- API is similar to standard in-memory LRU cache: get, set, delete, has, clear.
- Locking ensures atomicity for compound operations.
- Suitable for multi-process WSGI/ASGI, background jobs, ML/AI workers, caching across service forks.

Example use cases:
- Share a cache between worker processes in Gunicorn, Uvicorn, or multiprocessing scripts.
- Protect frequently-accessed data with expiry and auto-eviction.
- Use in ML/AI pipeline for process-wide memoization or inference result caching.

Usage Example:
```py
import time
import multiprocessing

from duck.utils.multiprocesing import ProcessSafeLRUCache

# Must be called in __main__ for Windows fork support!
if __name__ == "__main__":
    manager = multiprocessing.Manager()
    cache = ProcessSafeLRUCache(maxkeys=5)

    def store_and_read(cache, key, value):
        cache.set(key, value, expiry=10)
        print("Stored", key, "got back", cache.get(key))

    ps = []
    for i in range(10):
        p = multiprocessing.Process(target=store_and_read, args=(cache, str(i), i * 2))
        p.start()
        ps.append(p)
        time.sleep(1)
    
    for p in ps:
        p.join()

    print("Final shared cache:", dict(cache.cache))
"""

import datetime
import multiprocessing


class ProcessSafeLRUCache:
    """
    ProcessSafeLRUCache(maxkeys=None)

    A process-safe, shared-memory LRU cache with per-key expiry time.

    Uses multiprocessing.Manager for process-safe shared dict/list storage.

    Args:
        maxkeys (int): Optional maximum number of cache entries (evicts oldest if exceeded).

    **Methods:**
    - set(key, value, expiry=None): Set key to value, optionally with expiry time in seconds.
    - get(key, default=None, pop=False): Get value for key (None/default if missing), optionally popping it.
    - has(key): Check if key exists (not evicted/expired).
    - delete(key): Delete a cache entry.
    - clear(): Remove all cache and expiry data.
    - close(): Aliased to clear.
    """
    __slots__ = {
        "manager",
        "expiry_map",
        "cache",
        "lru_order",
        "maxkeys",
        "lock",
    }
    
    def __init__(self, maxkeys=None):
        self.manager = multiprocessing.Manager()
        self.expiry_map = self.manager.dict()
        self.cache = self.manager.dict()
        self.lru_order = self.manager.list()
        self.maxkeys = maxkeys
        self.lock = self.manager.Lock()

    def set(self, key: str, value, expiry=None):
        """
        Set a value in the cache, marking it as most recently used.

        Args:
            key: Key to set.
            value: Value to associate with key.
            expiry: Seconds until key expires (None disables expiry).
        """
        with self.lock:
            if key in self.cache:
                try:
                    self.lru_order.remove(key)
                except ValueError:
                    pass
            self.cache[key] = value
            self.lru_order.append(key)
            if expiry:
                self.expiry_map[key] = datetime.datetime.now() + datetime.timedelta(seconds=expiry)
            
            # LRU eviction (preserves maxkeys)
            while self.maxkeys and len(self.cache) > self.maxkeys:
                oldest_key = self.lru_order.pop(0)
                self.cache.pop(oldest_key, None)
                self.expiry_map.pop(oldest_key, None)

    def get(self, key: str, default=None, pop=False):
        """
        Get a value from the cache (or default if missing/expired).

        Args:
            key: Cache key.
            default: Value to return if key not present.
            pop: If True, remove the key after retrieval.

        Returns:
            Cached value, or default/None.
        """
        with self.lock:
            # Expiry check
            if key in self.expiry_map:
                expiry_date = self.expiry_map[key]
                if datetime.datetime.now() >= expiry_date:
                    self.cache.pop(key, None)
                    self.expiry_map.pop(key, None)
                    try: self.lru_order.remove(key)
                    except ValueError: pass
                    return None
            
            # LRU update (if not popping)
            if key in self.cache:
                try:
                    self.lru_order.remove(key)
                except ValueError:
                    pass
                if not pop:
                    self.lru_order.append(key)
                    return self.cache[key]
                else:
                    value = self.cache.pop(key)
                    self.expiry_map.pop(key, None)
                    return value
            return default

    def has(self, key: str):
        """
        Check if the cache has a key (not expired/evicted).
        """
        with self.lock:
            return key in self.cache

    def delete(self, key: str):
        """
        Remove a key from the cache.
        """
        with self.lock:
            self.cache.pop(key, None)
            self.expiry_map.pop(key, None)
            try: self.lru_order.remove(key)
            except ValueError: pass

    def clear(self):
        """
        Clear the entire cache and expiry info.
        """
        with self.lock:
            self.cache.clear()
            self.expiry_map.clear()
            self.lru_order[:] = []

    def close(self):
        """
        Alias for clear().
        """
        self.clear()

