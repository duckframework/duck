"""
Module containing RequestHandlingExecutor which handles execution of async coroutines and threaded tasks efficiently.
"""
import os
import asyncio
import platform
import threading
import concurrent.futures

from typing import (
    Optional,
    Union,
    Callable,
    Coroutine,
    Any,
)
from collections import deque

from duck.contrib.sync import (
    iscoroutine,
    iscoroutinefunction,
)
from duck.settings import SETTINGS
from duck.logging import logger
from duck.utils.asyncio import create_task
from duck.utils.asyncio.eventloop import AsyncioLoopManager
from duck.utils.threading.threadpool import ThreadPoolManager


class RequestHandlingExecutor:
    """
    A hybrid task executor for handling both async coroutines and
    blocking CPU-bound operations using threads efficiently.
    """

    def __init__(self):
        """
        Initialize the RequestHandlingExecutor.
        """
        pass
        
    def on_task_complete(self, future: Union[concurrent.futures.Future, asyncio.Future]):
        """
        Callback to handle completion or failure of a task.

        Args:
            future (Union[concurrent.futures.Future, asyncio.Future]): Future object for the task.
        """
        try:
            # Raises if the task failed
            future.result()
        except Exception as e:
            error_msg = f"Request handling task error: {e}"
            
            # Enhance the exception with task name for debugging
            if hasattr(future, 'name'):
                e.args = (f"{e.args[0]}: [{future.name}]", )
                error_msg = f"Request handling task error [{future.name}]: {e}"
                
            # Log exception.    
            logger.log(error_msg, level=logger.WARNING)
                
            if SETTINGS['DEBUG']:
                logger.log_exception(e)

    def execute(self, task: Union[Callable, Coroutine]):
        """
        Public interface to execute a task. It routes the task to either
        the async task queue or the thread pool, depending on its type.

        Args:
            task (Callable or Coroutine): The task to run.
                                          - If async, it's queued to run in event loop.
                                          - If sync, it's submitted to the thread pool.
        """
        if iscoroutine(task):
            # Schedule coroutine in the asyncio loop from another thread
            if not SETTINGS['ASYNC_HANDLING']:
                raise RuntimeError(
                    "ASYNC_HANDLING is set to False yet a coroutine task has been submitted. "
                    "Expected a synchronous callable."
                )
            
            async def request_handler_wrapper(task):
                create_task(task)
            future = AsyncioLoopManager.submit_task(request_handler_wrapper(task))
        else:
            if SETTINGS['ASYNC_HANDLING']:
                raise RuntimeError(
                    "ASYNC_HANDLING is set to True yet a non-coroutine task has been submitted. "
                    "Expected a coroutine."
                )
                
            # Submit blocking or CPU-bound task to the thread pool
            future = ThreadPoolManager.submit_task(task, task_type="request-handling")
            
        # Attach name and callback for error handling
        future.name = getattr(task, 'name', repr(task))
        future.add_done_callback(self.on_task_complete)
