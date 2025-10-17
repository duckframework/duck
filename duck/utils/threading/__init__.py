"""
Threading utilities and helpers.
"""
import threading

from typing import Optional


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
