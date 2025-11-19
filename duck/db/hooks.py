"""
Database connection lifecycle hooks for Duck or Django views.

This module provides explicit, manually-invoked hooks to manage the database
connection lifecycle, mirroring Django's behavior. These are especially useful
in views, background tasks, or custom frameworks where automatic connection
cleanup may not apply or fine-grained control is required.

Supports both synchronous and asynchronous execution contexts.
"""

from django.core.exceptions import ImproperlyConfigured

from duck.contrib.sync import (
    convert_to_async_if_needed,
    transaction_context,
    disable_transaction_context,
)


def close_old_connections():
    """
    Close any unusable or obsolete database connections.

    This function safely closes any DB connections that are:
    - broken,
    - timed out (exceeded CONN_MAX_AGE),
    - or associated with outdated threads or processes.

    Should be called at the end of a request or task, mimicking what Django does.
    """
    try:
        from django.db import close_old_connections as _close_old_connections
        _close_old_connections()
    except (ImproperlyConfigured, KeyError, ImportError):
        # User not using Django DB models, keyerror is raised when importing Django settings
        # Importing Django settings module failed, partially means the Django DB is not being used by the user    
        pass


def close_current_connection():
    """
    Closes current DB connection if available.
    """
    try:
        from django.db import connection
        connection.close()
    except (ImproperlyConfigured, KeyError, ImportError):
        # User not using Django DB models, keyerror is raised when importing Django settings
        # Importing Django settings module failed, partially means the Django DB is not being used by the user    
        pass
    

def view_wrapper(handler):
    """
    Wraps a synchronous view or handler with DB connection lifecycle cleanup.

    Ensures `close_old_connections()` is called both before and after
    the view is executed.

    Args:
        handler (Callable): The synchronous view or function to wrap.

    Returns:
        Callable: A wrapped view that handles DB connection cleanup.
    """
    def wrapped_db_hook(*args, **kwargs):
        try:
            close_old_connections() # Before request hook
            return handler(*args, **kwargs)
        finally:
            close_current_connection()  # After request hook
    return wrapped_db_hook


def async_view_wrapper(handler):
    """
    Wraps an asynchronous view or handler with DB connection lifecycle cleanup.

    Ensures `close_old_connections()` is called both before and after
    the view is executed, using `convert_to_async_if_needed()` to avoid
    blocking the event loop.

    Args:
        handler (Callable): The async view or function to wrap.

    Returns:
        Awaitable: A wrapped coroutine with DB connection cleanup.
    """
    async def wrapped_db_hook(*args, **kwargs):
        # This wrapper only close db connections for any thread the sync_to_async code.
        # doesn't mean the handler will use the current thread connection. As threads 
        # are reused, the thread's connection may be used by another sync_to_async db function.
        # This mean the reused threads' connections get a chance for cleanup at different intervals.
        try:
            await async_close_old_connections() # Before request hook
            return await handler(*args, **kwargs)
        finally:
            # Ignore the next line as it may close important connections as the func
            # is run in any thread
            pass
            #await async_close_current_connection()  # After request hook
    return wrapped_db_hook


# Define some async functions
async_close_old_connections = convert_to_async_if_needed(close_old_connections)
async_close_current_connection = convert_to_async_if_needed(close_current_connection)
