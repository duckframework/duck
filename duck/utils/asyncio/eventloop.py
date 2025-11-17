"""
Centralized Asyncio Threaded Loop Manager with Task Type Protection and Sync Future Support.

This module provides tools for running asyncio coroutines from synchronous code
by managing an asyncio event loop in a background thread. It includes:

- `SyncFuture`: A thread-safe future for blocking synchronous code.
- `AsyncioLoopManager`: A singleton-style class for managing an asyncio loop
  in a separate thread and submitting async tasks from sync contexts, 
  with optional task type protection to ensure only specific task types are allowed to run.
  
Features:
- Centralized asyncio event loop dedicated for background async operations.
- Protects critical loops from unknown/disallowed async tasks via task_type enforcement.
- Useful for bridging synchronous environments like WSGI or ASGI systems with async code in a safe, controlled manner.
"""

import asyncio
import threading

from typing import (
    Union,
    Coroutine,
    Optional,
)

from duck.utils.threading import SyncFuture, async_to_sync_future


class UnknownAsyncTaskError(Exception):
    """
    Raised when attempting to submit a coroutine of a disallowed or unexpected type
    to a protected asyncio loop.
    """
    def __init__(self, given_type, expected_type):
        message = (
            f"Async task type '{given_type}' is not permitted in this event loop "
            f"(required type: '{expected_type}').\n"
            "To safely submit this task, restart AsyncioLoopManager with the desired task_type, or subclass."
        )
        super().__init__(message)
        self.given_type = given_type
        self.expected_type = expected_type


class AsyncioLoopManager:
    """
    A manager that runs an asyncio event loop in a background thread,
    with optional task type protection.

    Notes:
    - This starts an asyncio event loop in a single global thread.
    - Allows submitting coroutines from synchronous code.
    - Supports synchronous result blocking via SyncFuture.
    - Can restrict tasks by type to prevent inappropriate coroutine submission to protected loops.
    """
    _loop: Optional[asyncio.AbstractEventLoop] = None
    _thread: Optional[threading.Thread] = None
    _task_type: Optional[str] = None

    @classmethod
    def start(cls, task_type: Optional[str] = None):
        """
        Starts the event loop in a background thread if it's not already running.

        Args:
            task_type (Optional[str]): The expected type of async tasks 
                for this loop. If set, only tasks with matching type will be accepted.
        
        Raises:
            RuntimeError: If event loop is not None and loop's thread is alive.
        """
        if cls._loop is None:
            cls._loop = asyncio.new_event_loop()
        cls._task_type = task_type

        def run_loop():
            asyncio.set_event_loop(cls._loop)
            cls._loop.run_forever()

        if cls._thread is None or not cls._thread.is_alive():
            cls._thread = threading.Thread(target=run_loop)
            cls._thread.start()
        else:
            raise RuntimeError("Asyncio loop is not None and event loop's thread is alive.")
            
    @classmethod
    def submit_task(
        cls, 
        coro: Coroutine, 
        return_sync_future: bool = False, 
        task_type: Optional[str] = None
    ) -> Union[SyncFuture, asyncio.Future]:
        """
        Submit an asynchronous coroutine to the event loop, with optional task type protection.

        Args:
            coro (Coroutine): The coroutine to schedule.
            return_sync_future (bool): If True, wraps the result in a SyncFuture for blocking use.
            task_type (Optional[str]): The type of this async task; must match manager's required type if set.

        Returns:
            Union[SyncFuture, asyncio.Future]: A future representing the scheduled coroutine.

        Raises:
            UnknownAsyncTaskError: If the provided type doesn't match the loop's protected type.
            RuntimeError: If the event loop is not running.
        """
        if cls._loop is not None and cls._loop.is_running():
            # Enforce task type protection if set
            if cls._task_type is not None:
                if task_type != cls._task_type:
                    raise UnknownAsyncTaskError(task_type, cls._task_type)
            future = asyncio.run_coroutine_threadsafe(coro, cls._loop)
            if return_sync_future:
                future = async_to_sync_future(future)
            return future
        else:
            raise RuntimeError("Event loop is not running. Method start() must be called first.")

    @classmethod
    def get_event_loop(cls) -> asyncio.AbstractEventLoop:
        """
        Returns the running asyncio event loop.

        Returns:
            asyncio.AbstractEventLoop: The currently running event loop.

        Raises:
            RuntimeError: If the loop isn't running.
        """
        if cls._loop is not None and cls._loop.is_running():
            return cls._loop
        else:
            raise RuntimeError("Event loop is not running. Call start() first.")

    @classmethod
    def stop(cls):
        """
        Stops the event loop and waits for the thread to finish.

        Notes:
            This should be called to clean up the background loop thread.
        """
        if cls._loop:
            cls._loop.call_soon_threadsafe(cls._loop.stop)
            if cls._thread:
                cls._thread.join()
            cls._loop = None
            cls._thread = None
            cls._task_type = None
