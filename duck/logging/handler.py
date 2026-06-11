"""
Handler module for intercepting Duck logs.
"""
import threading

from typing import Optional, Union
from collections.abc import Callable, Iterable


_HANDLER_LOCK = threading.Lock()
HANDLERS: dict[int | None, set[Callable[[int, str], None]]] = {}


def register_handler(
    callback: Callable[[int, str], None],
    levels: Optional[Union[Iterable[int], int]] = None,
):
    """
    Register a log handler.

    Args:
        callback: The callback to register.
        levels: Log levels to listen for. If None or empty, listens for all levels.
    """
    if isinstance(levels, int):
        levels = (levels, )
        
    selected_levels = tuple(levels or (None,))

    with _HANDLER_LOCK:
        for level in selected_levels:
            HANDLERS.setdefault(level, set()).add(callback)


def remove_handler(
    callback: Callable[[int, str], None],
    levels: Iterable[int] | None = None,
):
    """
    Remove a registered log handler.

    Args:
        callback: The callback to remove.
        levels: Log levels to remove from. If None or empty, removes from all levels.
    """
    with _HANDLER_LOCK:
        selected_levels = tuple(levels or HANDLERS.keys())

        for level in selected_levels:
            handlers = HANDLERS.get(level)

            if not handlers:
                continue
                
            handlers.discard(callback)

            if not handlers:
                HANDLERS.pop(level, None)


def emit(level: int, message: str):
    """
    Emit a log message to all matching handlers.
    """
    with _HANDLER_LOCK:
        handlers = (
            list(HANDLERS.get(None, ())) +
            list(HANDLERS.get(level, ()))
        )

    for callback in handlers:
        callback(level, message)
