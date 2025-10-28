"""
Threading utilities and helpers.
"""
import os
import platform
import threading

from typing import Optional


def get_max_workers() -> int:
    """
    Dynamically calculate a safe max_workers value for ThreadPoolExecutor,
    based on CPU count, available memory, stack size, and current system usage.
    Works cross-platform (Linux, Windows, macOS). No root required.

    Returns:
        int: Suggested max_workers value (min 8, max 2000)
    """
    import psutil
    
    # --- System info ---
    cpu_count = os.cpu_count() or 1

    try:
        total_memory = psutil.virtual_memory().total
        used_memory = psutil.virtual_memory().used
        available_memory = psutil.virtual_memory().available
    except Exception:
        total_memory = 4 * 1024**3  # fallback to 4 GB
        available_memory = total_memory * 0.5  # fallback to 50% available

    try:
        all_threads = sum(p.num_threads() for p in psutil.process_iter())
    except Exception:
        all_threads = 500  # fallback if counting fails

    # --- Estimate stack size ---
    try:
        if platform.system() == "Windows":
            stack_size = 1 * 1024 * 1024  # 1 MB
        else:
            import resource
            stack_size = resource.getrlimit(resource.RLIMIT_STACK)[0]
            if stack_size <= 0 or stack_size > 1024**3:
                stack_size = 8 * 1024 * 1024  # fallback
    except Exception:
        stack_size = 8 * 1024 * 1024  # fallback

    # --- Limits ---
    # 1. CPU limit
    cpu_limit = cpu_count * 4

    # 2. Memory limit (use only portion of available RAM)
    mem_limit = int(available_memory * 0.75 / stack_size)

    # 3. Adjust for running threads (leave room)
    thread_adjustment = max(0, 2000 - all_threads)

    # --- Final decision ---
    max_workers = min(cpu_limit, mem_limit, thread_adjustment, 2000)
    return max(8, max_workers)


class SyncFuture:
    """
    A thread-safe future that blocks until a result is set or an exception is raised.

    This class mimics a subset of the behavior of asyncio.Future, but for use in
    synchronous (threaded) code. It allows one thread to wait for a value or error
    that will be provided by another thread.
    """

    def __init__(self):
        """
        Initializes the SyncFuture with no result or exception.
        """
        self._event = threading.Event()
        self._result = None
        self._exception = None

    def exception(self) -> Optional[Exception]:
        """
        Returns the future exception if set.
        """
        return self._exception
        
    def set_result(self, value):
        """
        Sets the result of the future and unblocks any waiting thread.

        Args:
            value (Any): The result to return from the `result()` method.
        """
        self._result = value
        self._event.set()

    def set_exception(self, exception):
        """
        Sets an exception for the future and unblocks any waiting thread.

        Args:
            exception (Exception): The exception to raise when `result()` is called.
        """
        self._exception = exception
        self._event.set()

    def result(self):
        """
        Blocks until a result or exception is set, then returns or raises it.

        Returns:
            Any: The result value previously set by `set_result()`.

        Raises:
            Exception: If an exception was set using `set_exception()`.
        """
        self._event.wait()
        
        if self.exception():
            raise self.exception()
        return self._result
