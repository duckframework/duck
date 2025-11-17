"""
Asyncio utilities and helpers.
"""
import asyncio

from typing import Coroutine, Callable, List, Type, Optional


def create_task(
    coro: Coroutine,
    on_complete: Optional[Callable[[asyncio.Task], None]] = None,
    raise_on_exception: bool = True,
    ignore_errors: Optional[List[Type[BaseException]]] = None,
    loop: Optional = None,
) -> asyncio.Task:
    """
    Create an asyncio task and handle exceptions, optionally ignoring specified errors.

    Args:
        coro (Coroutine): The coroutine to run.
        on_complete (Callable): Called with the task when finished.
        raise_on_exception (bool): Raises exceptions from the task unless ignored.
        ignore_errors (List[Type[BaseException]]): Exception types to ignore.
        loop (Optional): Custom event loop to use for creating task.
         
    Raises:
        RuntimeError: If the loop is provided and is not running.
        Exception or CancelledError: If not ignored and raise_on_exception is True.
    """
    if ignore_errors is None:
        ignore_errors = [asyncio.CancelledError]
    
    if loop and not loop.is_running():
        raise RuntimeError("Event loop provided yet it is not running.")

    task = loop.create_task(coro) if loop else asyncio.create_task(coro)
    
    def on_task_done(t: asyncio.Task):
        try:
            if raise_on_exception:
                try:
                    exc = t.exception()  # May raise CancelledError!
                except BaseException as e:
                    # Handle CancelledError and other ignored exceptions
                    ignore_exception = any(issubclass(type(e), ignore) for ignore in ignore_errors)
                    if not ignore_exception:
                        raise
                else:
                    if exc and not any(issubclass(type(exc), ignore) for ignore in ignore_errors):
                        raise exc
        finally:
            if on_complete:
                try:
                    on_complete(t)
                except Exception as e:
                    logger.log_exception(e)  # Optionally log
    task.add_done_callback(on_task_done)
    return task


def in_async_context() -> bool:
    """
    Check if the current code is running inside an asynchronous context.

    Returns:
        bool: True if called within an `async def` coroutine (i.e., there's a running event loop),
              False otherwise.

    Example:
    ```
    >>> in_async_context()
    False

    >>> async def main():
    ...     print(in_async_context())
    >>> asyncio.run(main())
    True
    ```
    """
    try:
        asyncio.get_running_loop()
        return True
    except RuntimeError:
        return False
