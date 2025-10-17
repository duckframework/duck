"""
Utilities for managing and executing coroutines on available asyncio event loops.

This module provides functions for submitting coroutines to an available asyncio event loop, 
which is useful in applications where multiple execution contexts (e.g., ASGI, WSGI) might be running. 
The utility functions ensure compatibility with both synchronous and asynchronous workflows.

**Functions:**
- run_on_available_loop: Submits a coroutine to the currently available event loop.
- get_available_event_loop: Retrieves an appropriate event loop depending on the application's context.
"""
import asyncio
from typing import Coroutine, Union

from duck.utils.asyncio.eventloop import AsyncioLoopManager, SyncFuture


def run_on_available_loop(
    coro: Coroutine, return_sync_future: bool = False
) -> Union["SyncFuture", asyncio.Future]:
    """
    Submit an asynchronous coroutine to an available asyncio event loop.

    This function ensures that the provided coroutine is executed on an appropriate asyncio event loop.
    It supports both synchronous and asynchronous workflows by optionally wrapping the result in a 
    `SyncFuture`. 

    Args:
        coro (Coroutine): The coroutine to schedule for execution.
        return_sync_future (bool): If True, wraps the result in a `SyncFuture` to allow blocking 
                                   operations in synchronous contexts.

    Returns:
        Union[SyncFuture, asyncio.Future]: 
            - If `return_sync_future` is False, returns an `asyncio.Future` representing the scheduled coroutine.
            - If `return_sync_future` is True, returns a `SyncFuture` that can be used for blocking operations.

    Raises:
        RuntimeError: If no event loop is available or the event loop is not currently running.

    Example:
        >>> async def my_coroutine():
        >>>     return "Hello, asyncio!"
        >>> future = run_on_available_loop(my_coroutine())
        >>> print(future.result())  # Blocks until the coroutine completes
    """
    event_loop = get_available_event_loop()

    if event_loop is not None and event_loop.is_running():
        # Schedule the coroutine on the event loop
        future = asyncio.run_coroutine_threadsafe(coro, event_loop)

        if return_sync_future:
            # Wrap the result in a SyncFuture for blocking use
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
        raise RuntimeError("Event loop is None or not running.")


def get_available_event_loop():
    """
    Retrieve an available asyncio event loop depending on the application's execution context.

    This function determines the appropriate asyncio event loop to use based on the application's
    configuration. For example:
        - In an ASGI context, it retrieves the default event loop from the `REQUEST_HANDLING_EXECUTOR`.
        - In a WSGI context, it retrieves a background event from `AsyncioLoopManager`.

    Returns:
        asyncio.AbstractEventLoop: The available asyncio event loop.

    Example:
        >>> loop = get_available_event_loop()
        >>> print(loop.is_running())  # Check if the event loop is running
    """
    from duck.settings import SETTINGS
    from duck.settings.loaded import SETTINGS, REQUEST_HANDLING_TASK_EXECUTOR
    
    if SETTINGS['ASYNC_HANDLING']:
        # Retrieve the event loop from the request handling executor in ASGI
        event_loop = REQUEST_HANDLING_TASK_EXECUTOR._loop
    else:
        # Retrieve the loop from the AsyncioLoopManager in non-async contexts
        event_loop = AsyncioLoopManager._loop
    return event_loop
