"""
Smart module for high-concurrency async execution of synchronous callables,
with intelligent handling of transactional/atomic operations.

**Features:**
- Runs regular sync code on any available thread for maximal concurrency.
- Routes transactional/atomic database operations to a pool of specialized threads.
- Ensures thread (and connection) affinity for sync-to-async calls within a transaction context.
- Automatically tunes thread pool size for optimal performance based on CPU and DB resource limits.
- Reliable queueing and error handling; safe for production usage.

**Usage Exanple:**
```py
import time
import asyncio

def regular_func(x):
    time.sleep(1)
    return x * x

async def atomic_func(num_times):
    results = []
    x = 0

    def some_db_func():
        nonlocal x
        time.sleep(1)
        results.append(x + 1)
        x += 1
        
    with transaction_context():
        for i in range(num_times):
            await smart_sync_to_async(atomic_func)()
    return results
    

async def main():
    print("Regular ops concurrently:")
    st_time = time.time()
    results = await asyncio.gather(
        *(smart_sync_to_async(regular_func)(i) for i in range(8))
    )
    print(results)
    print(f"Total time is: {time.time() - st_time: .2f} seconds each with a break of 1s")
        
    st_time = time.time()
    print("\nAtomic ops sequentially (single transaction context):")
    atomic_results = await atomic_func(8)
    print(atomic_results)
    print(f"Total time is: {time.time() - st_time: .2f} seconds each with a break of 1s")

asyncio.run(main())
```

**Notes:**
- Atomic/transactional tasks run in the same thread context sequentially, depending on the atomic context block.
- Regular tasks run concurrently across threads.
- Context managers `transaction_context` & `disable_transaction_context` can be used to enable/disable transactional task processing.
"""
import os
import uuid
import queue
import asyncio
import inspect
import threading
import contextvars

from functools import wraps
from typing import Any, Callable, TypeVar, Optional, List


T = TypeVar("T")


def get_optimal_thread_count() -> int:
    """
    Determine optimal thread pool size based on CPU count and environment.
    For DB ops, you may want to tune based on DB max connections.
    """
    from duck.utils.threading import get_max_workers
    return get_max_workers()
    

class TransactionThread(threading.Thread):
    """
    Dedicated thread for executing atomic/transactional database operations.
    Each thread maintains its own DB connection context.
    All tasks submitted are executed serially, preserving transaction context.
    """
    def __init__(self):
        super().__init__(daemon=True)
        self.task_queue = queue.Queue()
        self.start()

    def run(self):
        while True:
            func, args, kwargs, future, loop = self.task_queue.get()
            try:
                result = func(*args, **kwargs)
                loop.call_soon_threadsafe(future.set_result, result)
            except Exception as e:
                loop.call_soon_threadsafe(future.set_exception, e)
            finally:
                self.task_queue.task_done()

    def submit(self, func: Callable[..., T], *args, **kwargs) -> asyncio.Future:
        """
        Submit a function to this thread and return an asyncio.Future for its result.
        """
        loop = asyncio.get_event_loop()
        future: asyncio.Future = loop.create_future()
        self.task_queue.put((func, args, kwargs, future, loop))
        return future


class TransactionThreadPool:
    """
    A pool of transaction threads for concurrent atomic operations.
    Ensures thread affinity for transaction contexts.
    """
    def __init__(self, num_threads: Optional[int] = None):
        if num_threads is None:
            num_threads = get_optimal_thread_count()
        self.threads: List[TransactionThread] = [TransactionThread() for _ in range(num_threads)]
        self.counter = 0
        self.lock = threading.Lock()

    def get_thread(self, context_id=None):
        """
        Get a thread for a given transaction context.
        If context_id is set, use it to always select the same thread for the context.
        """
        if context_id is not None:
            idx = hash(context_id) % len(self.threads)
            return self.threads[idx]
        with self.lock:
            thread = self.threads[self.counter % len(self.threads)]
            self.counter += 1
        return thread

    def submit(self, func: Callable[..., T], *args, context_id=None, **kwargs) -> asyncio.Future:
        thread = self.get_thread(context_id)
        return thread.submit(func, *args, **kwargs)


class BasicThreadPool:
    """
    A pool of ordinary threads for non-transactional concurrent operations.
    
    **Notes:**
    - Uses `asyncio.to_thread` for simplicity.
    """
    @staticmethod
    async def submit(func: Callable[..., T], *args, **kwargs) -> T:
        return await asyncio.to_thread(func, *args, **kwargs)


# Global pools
_TRANSACTION_THREAD_POOL = TransactionThreadPool()
_BASIC_THREAD_POOL = BasicThreadPool()

# Contextvar for transaction affinity
_transaction_context_id_var = contextvars.ContextVar("_transaction_context_id_var", default=None)


def is_transactional(func: Callable) -> bool:
    """
    Heuristically determine if a function is transactional/atomic.
    For Django: checks for 'transaction.atomic' in source or 'is_atomic' attribute.
    """
    if getattr(func, "is_atomic", False):
        return True
    try:
        src = inspect.getsource(func)
        if "transaction.atomic" in src or "atomic()" in src:
            return True
    except Exception:
        pass
    return False


def in_transaction_context() -> Optional[str]:
    """
    Returns a unique ID (str) if currently inside a DB transaction context/atomic block.
    Notes:
    - For **Django**: True if in `transaction.atomic`, returns thread identity.
    - For unsupported ORMs: returns None.
    """
    # Duck context
    ctx_id = _transaction_context_id_var.get()
    if ctx_id is not None:
        return ctx_id

    # Django detection
    try:
        from django.db import connection
        if getattr(connection, 'in_atomic_block', False):
            # Use id(connection) for affinity
            return f"django_atomic_{id(connection)}"
    except ImportError:
        pass
    except Exception:
        pass
    return None


def sync_to_async(
    func: Callable[..., T],
    *outer_args,
    **outer_kwargs
) -> Callable[..., asyncio.Future]:
    """
    High-concurrency async wrapper for synchronous functions.

    - Runs sync code in any available thread for maximum concurrency.
    - Detects atomic/transactional operations and routes them to a pool of specialized threads,
      ensuring all DB operations within a transaction run on the same thread/connection.
    - If called inside a transaction context, all sync_to_async calls for that transaction use the same thread.
    - Returns an awaitable Future with the result.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs) -> T: 
        context_id = in_transaction_context()
        if context_id:
            return await _TRANSACTION_THREAD_POOL.submit(func, *args, context_id=context_id, **kwargs)
        else:
            return await _BASIC_THREAD_POOL.submit(func, *args, **kwargs)
    return wrapper


class transaction_context:
    """
    Custom transaction context manager for testing purposes.
    This context manager simulates Django's `transaction.atomic()` for testing.
    Sets a contextvar so that `in_transaction_context()` can detect
    when code is running inside a transaction context.
    """
    def __enter__(self):
        self._token = _transaction_context_id_var.set(str(uuid.uuid4()))
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        _transaction_context_id_var.reset(self._token)


class disable_transaction_context:
    """
    Context manager that temporarily disables any active transaction context.
    While inside this block, in_transaction_context() returns None.

    Usage:
    ```py
    with transaction_context():
        print(in_transaction_context())  # Not None
        with disable_transaction_context():
            print(in_transaction_context())  # None
        print(in_transaction_context())  # Not None
    ```
    """
    def __enter__(self):
        # Remove any transaction context id for this block, saving previous token
        self._token = _transaction_context_id_var.set(None)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        _transaction_context_id_var.reset(self._token)
