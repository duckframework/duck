"""
Centralized Thread Manager with Task Type Protection and Sync Future Support.

This module provides `ThreadPoolManager`, a singleton thread pool manager for managing
and submitting synchronous tasks with fine-grained protection by `task_type`. It supports:

- A centralized thread pool for executing callable sync tasks in parallel.
- Task type protection: prevents submission of unknown or disallowed task types to the pool
  (e.g., avoids running long-running background jobs in a pool reserved for time-sensitive requests).
- Daemon thread support (safer shutdown, reliable cleanup).
- Simple API for starting, submitting, retrieving, and stopping the thread pool.
- Extensible for integration with Duck Framework and advanced server workloads.
"""

import threading
import concurrent.futures

from typing import (
    Union,
    Optional,
    Callable,
)

from duck.utils.threading import get_max_workers


class UnknownTaskError(Exception):
    """
    Raised when attempting to submit a task of a disallowed or unknown type.

    This error indicates a task type was provided (or omitted) that does not match
    the pool's configured protection. Typical use is to prevent accidental or
    inappropriate task submission to specialized or critical pools. If you need
    to run a different type of task, consider subclassing or reconfiguring the pool.
    """
    def __init__(self, task_type, pool_task_type):
        message = (
            f"Task type '{task_type}' is not permitted in this thread pool "
            f"(expected task_type: '{pool_task_type}').\n"
            "To safely submit this task, subclass ThreadPoolManager or restart the pool with the proper task type."
        )
        super().__init__(message)
        self.task_type = task_type
        self.pool_task_type = pool_task_type


class ThreadPoolManager:
    """
    Thread pool manager with task type protection.

    Use `start()` to initialize a centralized threadpool for sync tasks.
    Restrict submitted tasks by their `task_type`, preventing inappropriate jobs in critical worker pools.
    """
    _pool: Optional[concurrent.futures.ThreadPoolExecutor] = None
    _max_workers: Optional[int] = None
    _daemon: Optional[bool] = None
    _task_type: Optional[str] = None

    @classmethod
    def start(
        cls,
        max_workers: Optional[int] = None,
        task_type: Optional[str] = None,
        daemon: bool = False,
        thread_name_prefix: Optional[str] = None
    ):
        """
        Starts the threadpool, ready to accept tasks.

        Args:
            max_workers (Optional[int]): Maximum threads for pool.
            task_type (Optional[str]): Only allows tasks with this type to be submitted.
                Useful for protecting pools handling critical jobs (e.g., request_handling only).
            daemon (bool): Whether pool worker threads should be daemon threads.
            thread_name_prefix (Optional[str]): Thread naming prefix (optional).
        
        Raises:
            RuntimeError: If thread pool already available and initialized.
        """
        if cls._pool is None:
            cls._max_workers = max_workers or get_max_workers()
            cls._daemon = daemon
            cls._task_type = task_type

            def thread_factory(*args, **kwargs):
                t = threading.Thread(*args, **kwargs)
                t.daemon = daemon
                return t

            cls._pool = concurrent.futures.ThreadPoolExecutor(
                max_workers=cls._max_workers,
                thread_name_prefix=thread_name_prefix,
                initializer=None
            )

            # Mark threads daemon if requested
            if daemon:
                for t in list(cls._pool._threads):
                    t.daemon = True
        else:
            raise RuntimeError("Thread pool already available and initialized.")
                            
    @classmethod
    def submit_task(
        cls,
        task: Callable,
        task_type: Optional[str] = None,
    ) -> concurrent.futures.Future:
        """
        Submit a task to the threadpool.

        Args:
            task (Callable): Callable to execute.
            task_type (Optional[str]): Type/flag of this task. If manager was initialized with
                a specific allowed task_type, this must match or raise UnknownTaskError.

        Raises:
            UnknownTaskError: If task_type mismatches the pool's allowed type.
            RuntimeError: If the thread pool is None/not running.

        Returns:
            concurrent.futures.Future: Future for the executing task.
        """
        pool = cls.get_pool()
        
        # If protection by task_type is active, enforce it
        if cls._task_type is not None:
            if task_type != cls._task_type:
                raise UnknownTaskError(task_type, cls._task_type)

        future = pool.submit(task)
        return future

    @classmethod
    def get_pool(cls) -> concurrent.futures.ThreadPoolExecutor:
        """
        Returns the running threadpool.

        Returns:
            concurrent.futures.ThreadPoolExecutor: Running thread pool.

        Raises:
            RuntimeError: If the threadpool is not running.
        """
        if cls._pool is not None:
            return cls._pool
        else:
            raise RuntimeError("Threadpool is not running. Call start() first.")

    @classmethod
    def stop(cls, wait: bool = True):
        """
        Shutdowns the threadpool.

        Args:
            wait (bool): Whether to wait for running tasks to finish.
        """
        if cls._pool is not None:
            cls._pool.shutdown(wait=wait)
            cls._pool = None
