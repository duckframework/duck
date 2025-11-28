
"""
Smart module for high-concurrency async execution of synchronous callables,
with intelligent handling of transactional/atomic operations.

**Features:**
- Runs regular sync code on any available thread for maximal concurrency.
- Routes transactional/atomic database operations to a pool of specialized threads.
- Ensures thread (and connection) affinity for sync-to-async calls within a transaction context.
- Dynamically scales up transactional threads as needed, up to max_threads.
- Reliable queueing and error handling; safe for production usage.

**Usage Example:**
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
            await smart_sync_to_async(some_db_func)()
    return results

async def main():
    print("Regular ops concurrently:")
    st_time = time.time()
    results = await asyncio.gather(
        *(smart_sync_to_async(regular_func)(i) for i in range(8))
    )
    print(results)

    st_time = time.time()
    print("\nAtomic ops sequentially (single transaction context):")
    atomic_results = await atomic_func(8)
    print(atomic_results)

asyncio.run(main())
```

The core principal of async responsiveness, use of small tasks rather than awaiting 
long running task or even converting to async.
"""

import os
import uuid
import time
import queue
import asyncio
import inspect
import threading
import contextvars

from math import ceil
from functools import wraps, partial
from typing import (
    Any,
    Callable,
    TypeVar,
    Optional,
    Dict,
    List,
)

from duck.exceptions.all import SettingsError


T = TypeVar("T")


class TaskTookTooLongWarning(UserWarning):
    """
    Warning when a task took too much time executing as this might exhaust the threadpool 
    and might cause significant performance degradation (hangs subsequently). 
    """
    

class TransactionThread(threading.Thread):
    """
    Dedicated thread for executing atomic/transactional database operations.
    Each thread maintains its own DB connection context.
    All tasks submitted are executed serially, preserving transaction context.
    
    Notes:
    - This thread can also be used in non-transactional general contexts.
    """
    def __init__(self, context_id=None):
        super().__init__(daemon=True)
        self.context_id = context_id
        self.task_queue = queue.Queue()
        self._busy = threading.Event()   # NEW: busy indicator
        self._current_task_executing = None
        self._max_task_duration = 0.2 # Seconds for optimal task duration
        self.start()

    def is_free(self) -> bool:
        """
        Returns True if the thread is idle (no task running and queue empty).
        """
        # _busy = False AND queue empty -> free
        return not self._busy.is_set() and self.task_queue.empty()

    def current_task_executing(self) -> Optional[Any]:
        """
        Returns the current task/callable being executed.
        """
        return self._current_task_executing
        
    def run(self):
        try:
            from duck.logging import logger
        except SettingsError:
            # Not in a Duck project
            from duck.logging import console as logger

        while True:
            item = self.task_queue.get() # This blocks until something is submitted
            
            if item is None:  # shutdown sentinel
                break

            func, args, kwargs, future, loop = item

            # Mark thread busy
            self._busy.set()
            
            # Set task
            task = partial(func, *args, **kwargs)
            start_time = time.time()
            
            # Execute task
            def set_result_or_exception(future, result):
                """
                Set result or exception for the future.
                
                This handles `asyncio.InvalidStateError` and `asyncio.CancelledError` by default.
                """
                is_error = False
                is_debug = True
                
                try:
                    from duck.settings import SETTINGS
                    is_debug = SETTINGS['DEBUG']
                except SettingsError:
                    pass # Not inside a Duck project.
                    
                if isinstance(result, BaseException):
                    is_error = True
                
                try:
                    if is_error:
                        future.set_exception(result)
                    else:
                        future.set_result(result)
                    exec_time = time.time() - start_time
                    
                    # Warn user if task too long
                    if exec_time > self._max_task_duration:
                        logger.warn(
                            (
                                f"Task took too long to finish: {exec_time:.2f} s, task: {task}. "
                                f"This might cause hanging or performance degradation. "
                                f"Max task duration: {self._max_task_duration: .2f} seconds. "
                                "Consider splitting task into smaller sub-tasks."
                            ),
                            TaskTookTooLongWarning,
                        )
                    
                except (asyncio.InvalidStateError, asyncio.CancelledError):
                    pass
                
            try:
                self._current_task_executing = task
                result = task()
                
                # Set future result
                loop.call_soon_threadsafe(set_result_or_exception, future, result)
                
            except Exception as e:
                # Set future exception
                loop.call_soon_threadsafe(set_result_or_exception, future, e)
                
            finally:
                # Mark thread free AFTER executing the task
                self._busy.clear()
                self._current_task_executing = None
                self.task_queue.task_done()

    def submit(self, func: Callable[..., T], *args, **kwargs) -> asyncio.Future:
        """
        Puts the task in queue for execution.
        
        Returns:
            asyncio.Fututure: An asynchronous future you can wait for in async context.
        """
        loop = asyncio.get_event_loop()
        future: asyncio.Future = loop.create_future()
        self.task_queue.put((func, args, kwargs, future, loop))
        return future

    def shutdown(self):
        """
        Shutsdown the thread but if no task is being executed or after current task finishes.
        """
        self.task_queue.put(None)
    
    def __str__(self):
        return (
            f"<[{self.__class__.__name__} \n"
            f'  name="{self.name}",  \n'
            f"  daemon={self.daemon}, \n"
            f"  is_alive={self.is_alive()}, \n"
            f"  is_free={self.is_free()},  \n"
            f"  context_id={self.context_id},  \n"
            f"  ident={self.ident}, \n"
            f"  current_task_executing={self.current_task_executing()}, \n"
            "]>"
        )

    def __repr__(self):
        return (
            f"<[{self.__class__.__name__} \n"
            f'  name="{self.name}",  \n'
            f"  daemon={self.daemon}, \n"
            f"  is_alive={self.is_alive()}, \n"
            f"  is_free={self.is_free()},  \n"
            f"  context_id={self.context_id},  \n"
            f"  ident={self.ident}, \n"
            f"  current_task_executing={self.current_task_executing()}, \n"
            "]>"
        )
        

class TransactionThreadPool:
    """
    Dynamically scalable pool of TransactionThread objects.

    Features:
    - Context-affinity: threads created with a context_id are stored and reused for that context.
      These threads are NOT auto-freed, because callers may rely on persistent context-affinity.
    - General threads: threads without context_id are pooled and may be auto-freed when there are
      more idle general threads than the configured 'general_threads_free_level' percentage.
    - Thread creation is bounded by max_threads. max_threads applies to both context and general threads.
    """

    def __init__(
        self,
        max_threads: Optional[int] = None,
        auto_free_general_threads: bool = True,
        general_threads_free_level: int = 50,
    ):
        """
        Initialize the thread pool.

        Args:
            max_threads (Optional[int]): Maximum number of threads to create (per context/non-context threads). If None will
                use a reasonable default from `duck.utils.threading.get_max_workers()`.
            auto_free_general_threads (bool): If True, extra idle general threads will be automatically
                shut down when the pool has more idle threads than the configured free level.
            general_threads_free_level (int): percentage (0-100) of general threads to keep free before
                freeing additional idle threads. For example, 50 keeps at least half of the general
                free threads; any extra idle threads will be candidates for freeing.
        """
        from duck.utils.threading import get_max_workers
        
        self.max_threads = max_threads or get_max_workers()
        self.threads: Dict[str, TransactionThread] = {}  # context_id -> thread
        self.general_threads: List[TransactionThread] = []                  # threads for non-context tasks
        self.auto_free_general_threads = auto_free_general_threads
        self.general_threads_free_level = min(max(int(general_threads_free_level), 0), 100) # Clamp free level to [0, 100]
        self.lock = threading.Lock()
        self.counter = 0

    def _maybe_free_general_threads(self, ignore_threads: Optional[List[TransactionThread]] = None) -> None:
        """
        Free extra idle general threads to respect `general_threads_free_level`.
        
        Args:
            ignore_threads (Optional[List[TransactionThread]]): This is a list of threads to ignore when freeing threads. This 
                may be useful in cases, you want to free but excluding some thread you wanna use.
                
        Calculation:
        ```py
        desired_free_threads = ceil(max_threads * (free_level / 100))
        if current_free_threads > desired_free_threads:
            free (current_free_threads - desired_free_threads) # (but keep at least one general thread).
        ```
        """
        ignore_threads = ignore_threads or []
        
        # Never use nested `with lock` on same lock 
        if not self.auto_free_general_threads:
            return

        total = len(self.general_threads)
            
        if total <= 1:
            # Always keep at least one general thread to avoid constant recreation
            return
            
        current_free_threads = [t for t in self.general_threads if t.is_free()]
        current_free_threads = len(current_free_threads)
        desired_free_threads = ceil(self.max_threads * (self.general_threads_free_level / 100.0))
        
        # Ensure at least 1 desired free
        desired_free_threads = max(1, desired_free_threads)
        
        if current_free_threads <= desired_free_threads:
            return  # nothing to free
                
        # Calculate number to free
        num_to_free = current_free_threads - desired_free_threads
        
        # Avoid freeing so many that we'd end up with zero general threads
        max_removable = total - 1
        num_to_free = min(num_to_free, max_removable)
        removed = 0 # Initialize removed threads
        
        # Prefer to remove the oldest idle threads (iterate in list order)
        for t in self.general_threads:
            if removed < num_to_free and t not in ignore_threads and t.is_free():
                try:
                    t.shutdown()
                    t.join(.01)
                    self.general_threads.remove(t)
                except Exception:
                    raise # reraise any exception
                
                # Increment removed and continue     
                removed += 1
                continue
                
    def get_thread(self, context_id: Optional[str] = None) -> TransactionThread:
        """
        Return a `TransactionThread` appropriate for the provided `context_id`.

        If a `context_id` is given, the pool attempts to return a dedicated thread for that context,
        creating one if necessary (and if under `max_threads`). Context-bound threads are not
        auto-freed by the pool.

        If `context_id` is None, returns an available general thread if free, otherwise may create a
        new general thread (subject to `max_threads`). This method may trigger auto-freeing of
        extra general threads when appropriate.
        
        Args:
            context_id (Optional[str]): This is the context ID of the thread that is needed to run the task.
        
        Returns:
            TransactionThread: The thread matching the context ID or any free/appropriate thread if no context_id provided.
        """
        with self.lock:
            if context_id:
                thread = self.threads.get(context_id)
                if thread and thread.is_alive():
                    return thread
                
                # Remove dead thread if necessary
                if thread and not thread.is_alive():
                    del self.threads[context_id]
                
                # Create new thread for context_id if under max_threads
                if len(self.threads) < self.max_threads:
                    thread = TransactionThread(context_id)
                    self.threads[context_id] = thread
                    return thread
                
                # Fall back: pick existing thread round robin
                rr_idx = hash(context_id) % len(self.threads)
                reused_context = list(self.threads.values())[rr_idx]
                return reused_context
            
            # Handle general threads (no context)
            if len(self.general_threads) == 0:
                # No available threads yet, create one
                thread = TransactionThread()
                self.general_threads.append(thread)
                return thread
                    
            # Round robin over available general threads. If thread is not free try other ones if any is free.
            thread = self.general_threads[self.counter % len(self.general_threads)]
            
            # If chosen thread is busy, attempt to find another free one
            if not thread.is_free():
                for t in self.general_threads:
                    if t.is_free():
                        return t
                
                # Chosen thread is not free yet there is no available free thread.
                # No free general thread found; create another if allowed
                # Non-context: use/reuse thread (max max_threads for fairness)
                if len(self.general_threads) < self.max_threads:
                    thread = TransactionThread()
                    self.general_threads.append(thread)
                    
                    # After adding, see if we should free any extras (keeps pool from growing uncontrolled)
                    self._maybe_free_general_threads(ignore_threads=[thread])
                    
                    # Return the new thread.
                    return thread
            
            # Return round-robined thread
            self.counter += 1
            
            # After returning a thread, we can attempt to free extras (this call is safe and fast)
            self._maybe_free_general_threads(ignore_threads=[thread])
            
            # Return respective thread.
            return thread

    def submit(self, func: Callable[..., T], *args, context_id=None, **kwargs) -> asyncio.Future:
        """
        Puts the task in queue for execution in correct thread according to context ID or just any free/appropriate 
        thread if no context ID provided.
        
        Returns:
            asyncio.Fututure: An asynchronous future you can wait for in async context.
        
        Raises:
            AssertionError: If the returned thread from `get_thread` is dead/not running.
        """
        thread = self.get_thread(context_id)
        assert thread.is_alive(), f"Expected a running thread, but got a dead thread."
        return thread.submit(func, *args, **kwargs)

    def shutdown(self, wait: bool = True):
        """
        Stop all running threads attached to this pool.
        
        Args:
            wait (bool): Whether to wait for all threads to stop. Defaults to True.
        """
        # Cleanly stop all threads (poison pill)
        for t in list(self.threads.values()) + self.general_threads:
            t.shutdown()
        
        if wait:
            for t in list(self.threads.values()) + self.general_threads:
                t.join()
        
        # Clear all threads
        self.threads.clear()
        self.general_threads.clear()


# Global pool
_TRANSACTION_THREAD_POOL = TransactionThreadPool()

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
            return await _TRANSACTION_THREAD_POOL.submit(func, *args, context_id=None, **kwargs) # Using None as context_id will use round-robin for threads
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
