"""
Asyncio utilities and helpers.
"""
import asyncio

from typing import Coroutine, Callable, Dict, List, Tuple, Type, Optional
from duck.exceptions.all import AsyncViolationError, SettingsError
from duck.utils.importer import import_module_once


try:
    from duck.logging import logger

except Exception:
    from duck.logging import console as logger 


# Type alias for modules that are required to create an event loop. This is a string representing the module name.
LoopCreatorDependency = str


# Default loop creators
ASYNCIO_LOOP_CREATORS: Dict[str, Tuple[LoopCreatorDependency, Callable]] = {
    "asyncio": ("", lambda: asyncio.new_event_loop()),
    "uvloop": ("uvloop", lambda: import_module_once("uvloop").new_event_loop()),
    "trio": ("trio", lambda: import_module_once("trio").open_nursery()),
}


def create_task(
    coro: Coroutine,
    on_complete: Optional[Callable[[asyncio.Task], None]] = None,
    raise_on_exception: bool = True,
    ignore_errors: Optional[List[Type[BaseException]]] = None,
    loop: Optional[asyncio.AbstractEventLoop] = None,
) -> asyncio.Task:
    """
    Create an asyncio task and handle exceptions, optionally ignoring specified errors.

    Args:
        coro (Coroutine): The coroutine to run.
        on_complete (Callable): Called with the task when finished.
        raise_on_exception (bool): Raises exceptions from the task unless ignored.
        ignore_errors (List[Type[BaseException]]): Exception types to ignore.
        loop (Optional[asyncio.AbstractEventLoop]): Custom event loop to use for creating task.
         
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

    # Attach the done callback to handle completion and exceptions
    task.add_done_callback(on_task_done)

    # Return the created task
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
        # Attempt to get the current running event loop. If this succeeds, we are in an async context.
        asyncio.get_running_loop()

    except RuntimeError:
        return False

    return True


def raise_if_in_async_context(message):
    """
    Raises AsyncViolationError if in async context
    """
    if in_async_context():
        raise AsyncViolationError(message)
    

def new_event_loop(set_as_asyncio_loop: bool = True, loop_type: str = "asyncio") -> asyncio.AbstractEventLoop:
    """
    Create a new asyncio event loop and optionally set it as the current event loop.

    Args:
        set_as_asyncio_loop (bool): If True, the new event loop will be set as the current event loop.

    Returns:
        asyncio.AbstractEventLoop: The newly created event loop.
    """

    loop_creator = validate_event_loop(loop_type, return_loop_creator=True)

    try:
        loop = loop_creator() # type: ignore

    except ImportError as e:
        raise ImportError(
            f"Failed to create event loop of type '{loop_type}'. "
            "Ensure the required package is installed."
        ) from e
    
    if set_as_asyncio_loop:
        asyncio.set_event_loop(loop)

    return loop


def validate_event_loop(loop_type: str, return_loop_creator: bool = False) -> Optional[Callable[[], asyncio.AbstractEventLoop]]:
    """
    Validate that the specified loop type is supported and can be created.

    Args:
        loop_type (str): The name of the loop type to validate.
        return_loop_creator (bool): If True, returns the loop creator function instead of None.

    Raises:
        ValueError: If the loop type is not supported or cannot be created.
        ImportError: If the required module for the loop type is not installed.
    """
    try:
        dependency, loop_creator = ASYNCIO_LOOP_CREATORS[loop_type]

    except KeyError:
        raise ValueError(
            f"Unsupported loop_type '{loop_type}'. "
            f"Supported types are: {list(ASYNCIO_LOOP_CREATORS.keys())}. "
            "Try registering using `register_event_loop_creator`."
        )

    try:
        # Try importing module
        import_module_once(dependency) if dependency else None

    except ImportError as e:
        raise ImportError(
            f"Failed to import required module '{dependency}' for loop type '{loop_type}'. "
            "Ensure the required package is installed."
        ) from e
    
    if return_loop_creator:
        return loop_creator

    return None


def register_event_loop_creator(loop_type: str, creator: Callable[[], asyncio.AbstractEventLoop], dependency: Optional[str] = None):
    """
    Register a new event loop creator function for a given loop type.

    Args:
        loop_type (str): The name of the loop type (e.g., "asyncio", "uvloop").
        creator (Callable): A callable that returns a new event loop instance.
        dependency (Optional[str]): The module name that must be imported for this loop type.
    """
    if not callable(creator):
        raise ValueError("The creator must be a callable that returns an event loop.")

    # Normalize dependency
    dependency = dependency or ""

    # Register the new loop type and its creator
    ASYNCIO_LOOP_CREATORS[loop_type] = (dependency, creator)
