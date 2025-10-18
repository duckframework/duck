import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor
import os
from functools import wraps
from typing import Any, Callable, TypeVar, Coroutine, Optional

T = TypeVar('T')

MAX_WORKERS = min(32, (os.cpu_count() or 1) + 4)
_thread_local = threading.local()
_executor = ThreadPoolExecutor(max_workers=MAX_WORKERS, thread_name_prefix="sync_to_async_worker")


def _register_child_thread(parent_thread: Optional[threading.Thread]) -> None:
    """
    Set the parent_thread in the thread-local storage for the current thread.
    """
    _thread_local.parent_thread = parent_thread


def _get_parent_thread() -> Optional[threading.Thread]:
    """
    Retrieve the parent_thread for the current thread from thread-local storage.
    Returns None if not set (i.e., the thread is a root or not set up yet).
    """
    return getattr(_thread_local, "parent_thread", None)


def sync_to_async(func: Callable[..., T]) -> Callable[..., Coroutine[Any, Any, T]]:
    """
    Decorator to run a sync function in a ThreadPoolExecutor while preserving
    parent-child thread relationships using thread-local storage.

    - If called from outside any sync_to_async context, the spawned thread's
      parent is set to None.
    - If called from within another sync_to_async context, the parent is set
      to the calling thread object.

    The thread-local storage is always explicitly set at the start of each task,
    ensuring no stale parent state leaks due to thread reuse.

    Args:
        func: Synchronous function to execute asynchronously.

    Returns:
        An async function that, when awaited, executes the sync function in a thread pool.
    """

    @wraps(func)
    async def async_wrapper(*args, **kwargs) -> T:
        # Get parent thread object from thread-local storage of the calling thread (if any)
        parent_thread = _get_parent_thread()
        
        # For the outermost sync_to_async call, parent_thread will be None

        def thread_func(*a, **kw):
            # Always set the parent relationship for every worker thread
            _register_child_thread(parent_thread)
            
            if parent_thread:
                # Make the thread-local for all child threads inherit from parent thread
                # This makes all child threads to have the same local data as parent
                # making this approach work as Django's thread_sensitive=True but with higher concurrency 
                parent_local = parent_thread.local()
                for attr in dir(parent_thread_local):
                    val = getattr(parent_thread_local, attr)
                    setattr(_thread_local, attr, val)
            
            else:
                # This is called at outermost start of execution so lets reset the thread local
                for attr in dir(_thread_local):
                    delattr(_thread_local, attr)
                    
            return func(*a, **kw)

        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(_executor, thread_func, *args, **kwargs)

    return async_wrapper

# Example usage
if __name__ == "__main__":
    import time

    @sync_to_async
    def blocking_task(depth=0):
        tid = threading.current_thread().ident
        parent = _get_parent_thread()
        print(f"Thread {tid} (parent {parent.ident if parent else None}) running at depth {depth}")
        time.sleep(0.1)
        if depth < 2:
            import asyncio
            asyncio.run(nested(depth + 1))

    @sync_to_async
    def nested(depth):
        blocking_task(depth=depth)

    async def main():
        await blocking_task()

    asyncio.run(main())
    