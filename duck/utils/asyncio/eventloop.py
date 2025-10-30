"""
Asyncio Threaded Loop Manager with Sync Future Support.

This module provides tools for running asyncio coroutines from synchronous code
by managing an asyncio event loop in a background thread. It includes:

- `SyncFuture`: A thread-safe future for blocking synchronous code.
- `AsyncioLoopManager`: A singleton-style class for managing an asyncio loop
  in a separate thread and submitting async tasks from sync contexts.

Useful for bridging synchronous environments like WSGI or threaded systems with async code.
"""

import asyncio
import threading

from typing import Union, Coroutine

from duck.utils.threading import SyncFuture


class AsyncioLoopManager:
    """
    A manager that runs an asyncio event loop in a background thread.

    Notes:
        - This starts an asyncio event loop in a single global thread.
        - Allows submitting coroutines from synchronous code.
        - Supports synchronous result blocking via SyncFuture.
    """
    _loop = None
    _thread = None

    @classmethod
    def start(cls):
        """
        Starts the event loop in a background thread if it's not already running.
        """
        if cls._loop is None:
            cls._loop = asyncio.new_event_loop()

        def run_loop():
            asyncio.set_event_loop(cls._loop)
            cls._loop.run_forever()

        if cls._thread is None or not cls._thread.is_alive():
            cls._thread = threading.Thread(target=run_loop)
            cls._thread.start()

    @classmethod
    def submit_task(cls, coro: Coroutine, return_sync_future: bool = False) -> Union[SyncFuture, asyncio.Future]:
        """
        Submit an asynchronous coroutine to the event loop.

        Args:
            coro (Coroutine): The coroutine to schedule.
            return_sync_future (bool): If True, wraps the result in a SyncFuture for blocking use.

        Returns:
            Union[SyncFuture, asyncio.Future]: A future representing the scheduled coroutine.

        Raises:
            RuntimeError: If the event loop is not running.
        """
        if cls._loop is not None and cls._loop.is_running():
            future = asyncio.run_coroutine_threadsafe(coro, cls._loop)
            
            if return_sync_future:
                sync_future = SyncFuture()
                def _transfer_result(fut: asyncio.Future):
                    try:
                        result = fut.result()
                        sync_future.set_result(result)
                    except Exception as e:
                        sync_future.set_exception(e)
                future.add_done_callback(_transfer_result)
                return sync_future
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
