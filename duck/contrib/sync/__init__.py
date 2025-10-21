"""
Sync + Asynchronous helper tools.

This module provides utility functions to convert between synchronous and asynchronous 
functions using **asgiref's** `async_to_sync` and custom **Duck's** `sync_to_async`, with optional LRU caching 
to improve performance in high-frequency conversion scenarios.
"""

from typing import Callable, Any
from functools import lru_cache
from asyncio import iscoroutine
from asgiref.sync import (
    async_to_sync as _async_to_sync,
    iscoroutinefunction,
    AsyncToSync,
)

from duck.contrib.sync.smart_async import (
    sync_to_async,
    transaction_context,
    disable_transaction_context,
)


__all__ = [
    "iscoroutine",
    "iscoroutinefunction",
    "sync_to_async",
    "async_to_sync",
    "convert_to_async_if_needed",
    "convert_to_sync_if_needed",
    "ensure_async",
    "ensure_sync",
    "transaction_context",
    "disable_transaction_context",
]


@lru_cache(maxsize=256)
def async_to_sync(func: Callable) -> AsyncToSync:
    """
    Converts an asynchronous function into a synchronous one, with optional LRU caching.

    Args:
        func (Callable): The asynchronous function to convert.

    Returns:
        AsyncToSync: A synchronous version of the input async function.
    """
    return _async_to_sync(func)


def convert_to_async_if_needed(func: Callable) -> Callable:
    """
    Automatically converts a function to asynchronous if it's synchronous,
    or returns it unchanged if it's already a coroutine function.

    Args:
        func (Callable): The function to convert if needed.
        
    Returns:
        Callable: An async function if `func` was sync, otherwise the original.
    """
    from asgiref.sync import SyncToAsync
    
    if iscoroutinefunction(func) or isinstance(func, SyncToAsync):
        return func
    func = sync_to_async(func)
    return func


def convert_to_sync_if_needed(func: Callable) -> Callable:
    """
    Automatically converts a coroutine function to synchronous if it's asynchronous,
    or returns it unchanged if it's already a non-coroutine function.

    Args:
        func (Callable): The function to convert if needed.
        
    Returns:
        Callable: A sync function if `func` was async, otherwise the original.
    """
    if not iscoroutinefunction(func) or isinstance(func, AsyncToSync):
        return func
    return async_to_sync(func)


# Helper aliases
ensure_async = convert_to_async_if_needed
ensure_sync = convert_to_sync_if_needed
