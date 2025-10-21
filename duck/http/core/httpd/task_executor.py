"""
Module containing RequestHandlingExecutor which handles execution of async coroutines and threaded tasks efficiently.
"""
import os
import psutil
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
from duck.utils.threading import get_max_workers


class RequestHandlingExecutor:
    """
    A hybrid task executor for handling both async coroutines and
    blocking CPU-bound operations using threads efficiently.
    """

    def __init__(self, max_workers: int = None):
        """
        Initialize the RequestHandlingExecutor.

        Args:
            max_workers (int): Maximum number of threads for CPU-bound tasks.
                               If None, it is determined automatically.
        """
        self.max_workers = max_workers or get_max_workers()

        # Thread pool executor for blocking (CPU-bound or I/O-bound) work
        self._thread_pool = concurrent.futures.ThreadPoolExecutor(self.max_workers)

        if SETTINGS['ASYNC_HANDLING']:
            # Async task queue for coroutine execution (uses asyncio.Queue)
            self._task_queue = asyncio.Queue()

            # Start a new thread to run an asyncio event loop
            self._async_thread = threading.Thread(target=self._start_loop)
            self._async_thread.start()

    def _start_loop(self):
        """
        Internal method to initialize and run the asyncio event loop
        in a dedicated background thread.
        """
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)

        # Start the async task consumer
        self._loop.create_task(self._task_consumer())

        # Keep the loop running forever
        self._loop.run_forever()

    async def _task_consumer(self):
        """
        Coroutine that continuously consumes and executes async tasks
        from the async task queue.
        """
        while True:
            task = await self._task_queue.get()
            try:
                # We are using duck.utils.asyncio.create_task as it is better than default asyncio.create_task as it
                # avoids silent failures but it raises all exceptions by default.
                if asyncio.iscoroutinefunction(task):
                    # If it's a coroutine function, schedule it
                    create_task(task()) # raises errors if any compared to default asyncio.create_task
                    
                elif asyncio.iscoroutine(task):
                    # If it's already a coroutine object, schedule it directly
                    create_task(task) # raises errors if any compared to default asyncio.create_task
                
                else:
                    raise TypeError(f"Invalid task type: must be coroutine or coroutine function not {type(task)}")
            
            except Exception as e:
                error_msg = f"Request handling task error: {e}"
                
                if hasattr(task, "name"):
                    error_msg = f"Request handling task error [{task.name}]: {e}"
                
                # Log exception.    
                logger.log(error_msg, level=logger.WARNING)
                
                if SETTINGS['DEBUG']:
                    logger.log_exception(e)

    def on_thread_task_complete(self, future: concurrent.futures.Future):
        """
        Callback to handle completion or failure of a thread-based task.

        Args:
            future (concurrent.futures.Future): Future object for the task.
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
        if asyncio.iscoroutinefunction(task) or asyncio.iscoroutine(task):
            # Schedule coroutine in the asyncio loop from another thread
            if not hasattr(self, '_loop'):
                raise RuntimeError("Async loop is not initialized or ASYNC_HANDLING is disabled.")
            
            # Run the request handling task.
            asyncio.run_coroutine_threadsafe(self._task_queue.put(task), self._loop)

        else:
            # Submit blocking or CPU-bound task to the thread pool
            try:
                future = self._thread_pool.submit(task)
            except RuntimeError as e:
                if "cannot schedule new futures after interpreter shutdown" in str(e):
                    raise RuntimeError(f"{e}. This may occur if the application is shutting down.") from e

            # Attach name and callback for error handling
            future.name = getattr(task, 'name', repr(task))
            future.add_done_callback(self.on_thread_task_complete)
