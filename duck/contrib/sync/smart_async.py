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
        self._max_task_duration = 0.3 # Seconds for optimal task duration
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
                        taskname = getattr(task, "__name__", None)
                        
                        if not taskname:
                            taskname = getattr(task, "__qualname__", None)
                    
                        if not taskname:
                            taskname = task.__class__.__name__
                        
                        # Warn user - ignore for now
                        """
                        logger.warn(
                            (
                                f"Task took too long to finish: {exec_time:.2f} s, task: {taskname}. "
                                f"This might cause hanging or performance degradation. "
                                f"Max task duration: {self._max_task_duration: .2f} seconds. "
                                "Consider splitting task into smaller sub-tasks."
                            ),
                            TaskTookTooLongWarning,
                        )
                        """
                    
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
    - Context-affinity: threads created with a context_id are stored and reused for
      that context. These threads are NOT auto-freed, since callers may rely on
      persistent context-affinity.
    - General threads: threads without context_id are pooled and freed adaptively,
      based on recent concurrency rather than a fixed percentage, so the pool
      stays warm through a busy period and only shrinks once load has genuinely
      settled.
    - Thread creation is bounded by max_threads, which applies to both context and
      general threads.
    """

    def __init__(
        self,
        max_threads: Optional[int] = None,
        auto_free_general_threads: bool = True,
        general_threads_free_level: Optional[int] = None,
        headroom_factor: float = 1.5,
        idle_grace_period: float = 30.0,
        load_decay: float = 0.9,
        max_free_per_cycle: int = 1,
        load_check_interval: float = 0.05,
        enable_background_sweep: bool = True,
        sweep_interval: Optional[float] = None,
    ):
        """
        Initialize the thread pool.

        Args:
            max_threads:
                Maximum number of threads to create (per context/general
                threads). If None, uses a reasonable default from
                `duck.utils.threading.get_max_workers()`.

            auto_free_general_threads:
                If True, idle general threads beyond the
                target size are automatically shut down.

            general_threads_free_level:
                Percentage (0-100) of general threads to
                keep free before freeing extra idle ones. If None (default), the
                pool instead sizes itself adaptively from recent load (see
                headroom_factor, idle_grace_period, load_decay). Set this to an
                int to opt back into the old fixed-percentage behavior.

            headroom_factor:
                Only used when general_threads_free_level is None.
                Multiplier applied to the estimated concurrent load to size the
                pool, e.g. 1.5 keeps 50% spare capacity above recent usage so a
                following burst doesn't immediately need new threads.

            idle_grace_period:
                Only used when general_threads_free_level is None.
                Seconds a general thread must sit idle before it becomes eligible
                for freeing. Protects against freeing a thread that a following
                request would have reused.

            load_decay:
                Only used when general_threads_free_level is None. Decay
                factor (0-1) for the load estimate once demand drops. Closer to 1
                means the pool stays warm longer after a peak.

            max_free_per_cycle:
                Maximum number of general threads freed per call,
                to avoid thrashing (rapid free/recreate cycles) under bursty load.

            load_check_interval:
                Minimum seconds between recomputing the load
                estimate and running a free check. get_thread is called on every
                request, so under high call rates this throttles that O(n) work
                to at most once per interval instead of every single call.
                Thread selection itself is never throttled, only this
                bookkeeping.

            enable_background_sweep:
                If True, a daemon thread periodically runs
                the free check on its own, so idle general threads still get
                freed after a load spike even if no further get_thread calls
                arrive to trigger it. Set False to only free on demand, as part
                of get_thread.

            sweep_interval:
                Seconds between background sweeps. If None, defaults
                to max(idle_grace_period, 5.0).
        """
        from duck.utils.threading import get_max_workers

        self.max_threads = max_threads or get_max_workers()
        self.threads: Dict[str, TransactionThread] = {}  # context_id -> thread
        self.general_threads: List[TransactionThread] = []
        self.auto_free_general_threads = auto_free_general_threads
        self.general_threads_free_level = (
            None
            if general_threads_free_level is None
            else min(max(int(general_threads_free_level), 0), 100)
        )
        self.headroom_factor = max(1.0, headroom_factor)
        self.idle_grace_period = max(0.0, idle_grace_period)
        self.load_decay = min(max(load_decay, 0.0), 1.0)
        self.max_free_per_cycle = max(1, max_free_per_cycle)
        self.load_check_interval = max(0.0, load_check_interval)
        self.load_estimate = 0.0
        self.last_load_check = 0.0
        self.thread_last_active: Dict[int, float] = {}  # id(thread) -> timestamp
        self.lock = threading.Lock()
        self.counter = 0
        self.enable_background_sweep = enable_background_sweep
        self.sweep_interval = sweep_interval if sweep_interval is not None else max(self.idle_grace_period, 5.0)
        self.sweep_stop_event = threading.Event()
        self.sweep_thread: Optional[threading.Thread] = None

        # Kick off the sweeper so idle threads free themselves even without traffic
        if self.enable_background_sweep:
            self.start_background_sweep()

    def start_background_sweep(self) -> None:
        """
        Start the daemon thread that periodically frees idle general threads.

        This runs independently of get_thread calls, so a pool that grew during
        a burst still shrinks back down even if no further requests arrive to
        trigger the check.
        """
        self.sweep_thread = threading.Thread(target=self.run_background_sweep, daemon=True)
        self.sweep_thread.start()

    def run_background_sweep(self) -> None:
        """
        Loop that recomputes the load estimate and runs a free check every
        sweep_interval seconds, until sweep_stop_event is set.
        """
        while not self.sweep_stop_event.wait(self.sweep_interval):
            with self.lock:
                self.update_load_estimate()
                self.maybe_free_general_threads()

    def update_load_estimate(self) -> None:
        """
        Update the EWMA estimate of concurrent general-thread usage.

        Rises immediately to match a new peak, so a burst is captured without
        lag, then decays slowly via `load_decay` once demand drops. This keeps
        extra threads warm for a while after a spike instead of freeing them
        right before the next spike arrives.
        """
        active = sum(1 for t in self.general_threads if not t.is_free())

        if active >= self.load_estimate:
            self.load_estimate = active
        else:
            self.load_estimate = (self.load_decay * self.load_estimate) + (
                (1 - self.load_decay) * active
            )

    def mark_active(self, thread: "TransactionThread") -> None:
        """
        Record that a general thread was just handed out to a caller.

        Args:
            thread: The general thread that is about to be used.
        """
        self.thread_last_active[id(thread)] = time.time()

    def should_run_load_check(self) -> bool:
        """
        Decide whether enough time has passed to recompute load and run a free
        check, per load_check_interval.

        Returns:
            bool: True if the check should run now, in which case the internal
                timestamp is advanced so the next call waits a full interval.
        """
        now = time.time()

        if now - self.last_load_check < self.load_check_interval:
            return False

        # Update state
        self.last_load_check = now

        # Finally, return True
        return True

    def maybe_free_general_threads(self, ignore_threads: Optional[List["TransactionThread"]] = None) -> None:
        """
        Free extra idle general threads, using whichever sizing strategy is
        configured.

        If general_threads_free_level was set, the pool targets a fixed
        percentage of free threads. Otherwise it sizes itself adaptively from
        recent concurrency via free_general_threads_by_load.

        Args:
            ignore_threads: Threads to exclude from freeing, e.g. a thread about
                to be returned to a caller.
        """
        if not self.auto_free_general_threads:
            return

        if len(self.general_threads) <= 1:
            # Always keep at least one general thread to avoid constant recreation
            return

        if self.general_threads_free_level is not None:
            self.free_general_threads_by_level(ignore_threads)
        else:
            self.free_general_threads_by_load(ignore_threads)

    def free_general_threads_by_level(self, ignore_threads: Optional[List["TransactionThread"]] = None) -> None:
        """
        Free idle general threads to respect the fixed general_threads_free_level
        percentage.

        Calculation:
        ```py
        desired_free_threads = ceil(max_threads * (free_level / 100))

        if current_free_threads > desired_free_threads:
            free (current_free_threads - desired_free_threads)  # keep >= 1
        ```

        Args:
            ignore_threads: Threads to exclude from freeing.
        """
        ignore_threads = ignore_threads or []
        total = len(self.general_threads)
        
        current_free_threads = len([t for t in self.general_threads if t.is_free()])
        desired_free_threads = ceil(self.max_threads * (self.general_threads_free_level / 100.0))
        desired_free_threads = max(1, desired_free_threads)

        if current_free_threads <= desired_free_threads:
            return

        # Do some math
        num_to_free = current_free_threads - desired_free_threads
        max_removable = total - 1
        num_to_free = min(num_to_free, max_removable)
        removed = 0

        # Prefer to remove the oldest idle threads (iterate in list order)
        for t in self.general_threads:
            if removed < num_to_free and t not in ignore_threads and t.is_free():
                try:
                    t.shutdown()
                    t.join(0.01)
                    self.general_threads.remove(t)
                except Exception:
                    raise

                # Increment removed
                removed += 1
                continue

    def free_general_threads_by_load(self, ignore_threads: Optional[List["TransactionThread"]] = None) -> None:
        """
        Free idle general threads that exceed the load-adjusted target size.

        The target pool size is `load_estimate * headroom_factor`, clamped to
        [1, max_threads]. Only threads idle for at least `idle_grace_period`
        seconds are eligible, and at most `max_free_per_cycle` threads are freed
        per call, so the pool shrinks gradually rather than in one big drop.

        Args:
            ignore_threads: Threads to exclude from freeing, e.g. a thread about
                to be returned to a caller.
        """
        ignore_threads = ignore_threads or []
        total = len(self.general_threads)

        # Calculate target size
        target_size = ceil(self.load_estimate * self.headroom_factor)
        target_size = max(1, min(target_size, self.max_threads))

        if total <= target_size:
            return

        # Some more math
        max_removable = total - 1
        num_to_free = min(total - target_size, self.max_free_per_cycle, max_removable)
        now = time.time()
        removed = 0

        # Prefer the oldest idle threads, and only once they've earned their rest
        for t in self.general_threads:
            if removed >= num_to_free:
                break

            if t in ignore_threads or not t.is_free():
                continue

            # Set last active
            last_active = self.thread_last_active.get(id(t), 0.0)

            if now - last_active < self.idle_grace_period:
                continue

            try:
                t.shutdown()
                t.join(0.01)
                self.general_threads.remove(t)
                self.thread_last_active.pop(id(t), None)
            except Exception:
                raise

            # Increment removed
            removed += 1

    def get_thread(self, context_id: Optional[str] = None) -> "TransactionThread":
        """
        Return a TransactionThread appropriate for the provided context_id.

        If a context_id is given, the pool attempts to return a dedicated thread
        for that context, creating one if necessary (and if under max_threads).
        Context-bound threads are not auto-freed by the pool.

        If context_id is None, returns an available general thread if free,
        otherwise may create a new one (subject to max_threads). This may
        trigger freeing of extra general threads once load has settled.

        Args:
            context_id: The context ID of the thread that is needed to run the
                task.

        Returns:
            TransactionThread: The thread matching the context ID, or any
                free/appropriate general thread if no context_id was provided.
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
                self.mark_active(thread)
                if self.should_run_load_check():
                    self.update_load_estimate()
                return thread

            # Round robin over available general threads, falling back to any
            # free one if the chosen thread is busy
            thread = self.general_threads[self.counter % len(self.general_threads)]

            if not thread.is_free():
                for t in self.general_threads:
                    if t.is_free():
                        self.mark_active(t)
                        if self.should_run_load_check():
                            self.update_load_estimate()
                            self.maybe_free_general_threads(ignore_threads=[t])
                        return t

                # No free general thread found; create another if allowed
                if len(self.general_threads) < self.max_threads:
                    thread = TransactionThread()
                    self.general_threads.append(thread)
                    self.mark_active(thread)
                    if self.should_run_load_check():
                        self.update_load_estimate()
                        self.maybe_free_general_threads(ignore_threads=[thread])
                    return thread

            # Increment and mark active thread
            self.counter += 1
            self.mark_active(thread)

            if self.should_run_load_check():
                self.update_load_estimate()
                self.maybe_free_general_threads(ignore_threads=[thread])

            # Return final thread
            return thread

    def submit(self, func: Callable[..., T], *args, context_id=None, **kwargs) -> asyncio.Future:
        """
        Queue a task for execution on the thread matching context_id, or any
        free/appropriate thread if no context_id is provided.

        Args:
            func: The callable to run on the selected thread.
            *args: Positional arguments passed through to func.
            context_id: Context ID used to pick a dedicated thread. If None, a
                general thread is used instead.
            **kwargs: Keyword arguments passed through to func.

        Returns:
            asyncio.Future: An asynchronous future you can await in async context.

        Raises:
            AssertionError: If the returned thread from get_thread is dead.
        """
        thread = self.get_thread(context_id)

        if not thread.is_alive():
            thread = self.get_thread(context_id)  # Re-fetch thread

        # Do some checks
        assert thread.is_alive(), "Expected a running thread, but got a dead thread."

        # Return asyncio.Future
        return thread.submit(func, *args, **kwargs)

    def shutdown(self, wait: bool = True):
        """
        Stop all running threads attached to this pool.

        Args:
            wait: Whether to wait for all threads to stop. Defaults to True.
        """
        self.sweep_stop_event.set()

        if wait and self.sweep_thread:
            self.sweep_thread.join()

        # Cleanly stop all threads (poison pill)
        for t in list(self.threads.values()) + self.general_threads:
            t.shutdown()

        if wait:
            for t in list(self.threads.values()) + self.general_threads:
                t.join()

        # Clear all threads
        self.threads.clear()
        self.general_threads.clear()
        self.thread_last_active.clear()


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
