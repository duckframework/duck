"""
# Centralized Thread Manager With Hierarchical Context Propagation

This module provides a structured system for managing thread-scoped
`ThreadPoolManager` instances with optional task-type protection. It enables
worker threads, request handlers, or subsystem threads to each maintain their own
dedicated thread-pool manager, preventing concurrency issues caused by
cross-thread state leakage.

Unlike a global thread pool, managers resolved through this module follow a
*thread lineage model*: child threads inherit their parent’s manager unless they
explicitly create or request a new one. This creates predictable, isolated
execution environments ideal for component-based rendering, request lifecycles,
and subsystems that must not share threadpools.

## Core Features

1. **Thread-Scoped Managers**
   Each thread may own its own `ThreadPoolManager` instance. This manager is
   automatically reused by all descendant threads unless a new instance is
   explicitly created. This eliminates the need for fragile global registries.

2. **Hierarchical Resolution (Thread Lineage Lookup)**
   Manager resolution behaves like a "thread context":
   - Start from the current thread.
   - If no manager exists for the specified ID, walk upward through the
     parent thread chain.
   - If none exists in the lineage, create a new manager and attach it to
     the current thread.

   This makes manager acquisition both deterministic and flexible.

3. **Multiple Manager Namespaces**
   Using the `id` parameter, threads can maintain several different logical
   managers simultaneously (e.g., CPU-bound pool, IO pool, component-render pool).
   Each namespace is isolated without requiring separate registry structures.

4. **Task-Type Protection**
   Each manager can enforce a single allowed `task_type` for submitted tasks.
   This prevents accidental or unsafe mixing of workloads—for example, ensuring
   that:
       - time-sensitive tasks run only in designated pools,
       - component rendering tasks never leak into background worker pools,
       - slow jobs cannot clog request-handling threads.

5. **Daemon and Non-Daemon Worker Control**
   Managers can start thread pools with daemon threads (for non-blocking shutdown)
   or non-daemon threads (for guaranteed completion of jobs before exit).

6. **Safe Integration With Worker Thread Models**
   When used inside worker threads, calling `get_or_create_thread_manager()`
   ensures that the thread and all of its descendants operate under the same
   manager instance. This prevents component registry mismatches and mixed
   execution contexts that occur when unrelated threads share global pools.

## Motivation

Frameworks that use component rendering, fine-grained request lifecycles, or
thread-local state (such as dynamic UI components or live-updating view systems)
often need isolated execution domains. Using traditional global
`ThreadPoolExecutor` instances can lead to:

- state bleeding across requests,
- mixed component registries,
- concurrency bugs when a task intended for one context is executed in another,
- performance degradation when slow tasks block high-priority ones.

This module solves these problems by binding pool managers to *thread identity*
and propagating them through thread hierarchies, ensuring that each task belongs
to the correct execution environment.

## Typical Usage
```py
def worker_entrypoint():
    # Initialize or reuse the thread's manager
    manager = get_or_create_thread_manager(id="render")

    # Start a dedicated thread pool for rendering tasks
    manager.start(max_workers=4, task_type="component_render")

    future = manager.submit_task(
        some_callable,
        task_type="component_render",
    )
    return future.result()

## Best Practices

- Always call `get_or_create_thread_manager()` *inside* worker threads, never
  in the main thread (unless global propagation is desired).
- Choose meaningful manager IDs to organize workloads (e.g., "io", "cpu",
  "request", "component-render").
- Use task-type protection to prevent misuse of specialized pools.
- Avoid accessing the internal `REGISTRY` directly; use the resolver instead.

This module is designed to be robust, extensible, and suitable for advanced
server architectures and dynamic component systems such as those in the Duck
Lively Component System.
"""

import threading
import concurrent.futures

from typing import (
    Union,
    Optional,
    Callable,
    Any,
    Dict,
    List,
)

from duck.utils.threading.patch import get_parent_thread


REGISTRY = {}


def get_or_create_thread_manager(
    id: Optional[Any] = None,
    force_create: bool = False,
    strictly_get: bool = False,
) -> "ThreadPoolManager":
    """
    Retrieve or create the `ThreadPoolManager` instance bound to the current thread
    (or inherited from its parent thread).

    This function attaches the manager to the current thread's identity so that all
    child and sub-child threads automatically share the same manager unless they
    explicitly call this function with `force_create=True` to create an isolated one.

    This is especially useful in systems where each worker thread requires its own
    dedicated thread-pool manager (e.g., to isolate request-scoped or component-scoped
    work) while still allowing thread trees to share a consistent state.

    Args:
        id (Optional[Any]):
            Optional namespace/identifier for the manager.  
            - Using the same `id` returns the same manager instance for this
              thread lineage.
            - Using a different `id` allows multiple managers to coexist
              per thread.  

            Example:
            ```py
            default_mgr = get_or_create_thread_manager()  # default
            job_mgr = get_or_create_thread_manager(id="job-executor")  # separate manager
            ```
        
        force_create (bool):
            If True, bypasses lineage resolution and creates a fresh manager
            bound to the current thread. This is required inside worker threads
            where isolated loops are needed.
            
        strictly_get (bool): 
            Whether to strictly get the loop manager or raise an exception if manager not found.
            
    Raises:
        ManagerNotFound: Raised if manager not found and `strictly_get=True`.
        TypeError: If arguments `strictly_get` and `force_create` are both True.
                
    Notes:
    - When using worker threads, this function **must** be called inside
      each worker thread, not in the main thread.  
      Calling it in the main thread will cause the manager to propagate
      to all descendant threads, resulting in one shared instance.

    - The manager resolves using a thread lineage lookup:  
      if the current thread has no manager for the given ``id``, its parent
      thread is checked recursively until the root thread is reached.
    
    - If you already have created manager, use `strictly_get` argument to strictly get your 
      created manager or raise an exception if manager not found without creating new one.

    Returns:
        ThreadPoolManager: The resolved or newly created manager instance.
    """
    def resolve(thread: threading.Thread):
        managers = REGISTRY.get(thread.ident)
        if managers:
            # Manager namespace found
            manager = managers.get(id)
            if manager is None and not strictly_get:
                manager = ThreadPoolManager()
                managers[id] = manager
            return manager

        # No managers registered for this thread; check parent
        parent = get_parent_thread(thread)
        if parent is not None:
            return resolve(parent)
        return None

    if strictly_get and force_create:
        raise TypeError("Arguments 'strictly_get' and 'force_create' cannot be both True.")
        
    current = threading.current_thread()
    manager = None
    
    if not force_create:
        manager = resolve(current)
    
    # If resolution failed (root), create a new entry
    if manager is None:
        if strictly_get:
            raise ManagerNotFound("Strict getting of manager is True yet the manager cannot be resolved.")
        manager = ThreadPoolManager()
        REGISTRY[current.ident] = {id: manager}
    return manager


class ManagerNotFound(Exception):
    """
    Raised if manager cannot be resolved and user strictly wants to get the manager and user doesn't allow creating 
    it if it doesn't exist.
    """
   

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
            "To safely submit this task, reinitialize the ThreadPoolManager or restart the pool with the proper task type."
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
    
    __instances = []
    """
    This is the list of created instances.
    """
    def __init__(self):
        self._pool: Optional[concurrent.futures.ThreadPoolExecutor] = None
        self._max_workers: Optional[int] = None
        self._daemon: Optional[bool] = None
        self._task_type: Optional[str] = None
        ThreadPoolManager.__instances.append(self)
    
    @classmethod
    def all_instances(cls) -> List["ThreadPoolManager"]:
        """
        Returns a list of all created instances so far.
        """
        return ThreadPoolManager.__instances
        
    @classmethod
    def registry(cls) -> Dict[int, Dict[Any, "ThreadPoolManager"]]:
        """
        Returns the registry for created instances. Useful for tracking.
        """
        return REGISTRY
        
    def start(
        self,
        max_workers: int,
        task_type: Optional[str] = None,
        daemon: bool = False,
        thread_name_prefix: Optional[str] = None
    ):
        """
        Starts the threadpool, ready to accept tasks.

        Args:
            max_workers (int): Maximum threads for pool.
            task_type (Optional[str]): Only allows tasks with this type to be submitted.
                Useful for protecting pools handling critical jobs (e.g., request_handling only).
            daemon (bool): Whether pool worker threads should be daemon threads.
            thread_name_prefix (Optional[str]): Thread naming prefix (optional).
        
        Raises:
            RuntimeError: If thread pool already available and initialized.
        """
        def is_pool_active():
            dummy_task = lambda: None
            try:
                self._pool.submit(dummy_task)
                return True
            except RuntimeError:
                # Likely pool is not active
                return False
                
        if self._pool is None or not is_pool_active():
            self._max_workers = max_workers
            self._daemon = daemon
            self._task_type = task_type

            def thread_factory(*args, **kwargs):
                t = threading.Thread(*args, **kwargs)
                t.daemon = daemon
                return t

            self._pool = concurrent.futures.ThreadPoolExecutor(
                max_workers=self._max_workers,
                thread_name_prefix=thread_name_prefix,
                initializer=None
            )

            # Mark threads daemon if requested
            if daemon:
                for t in list(self._pool._threads):
                    t.daemon = True
        else:
            raise RuntimeError("Thread pool already active or running.")
            
    def submit_task(
        self,
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
        pool = self.get_pool()
        
        # If protection by task_type is active, enforce it
        if self._task_type is not None:
            if task_type != self._task_type:
                raise UnknownTaskError(task_type, self._task_type)

        future = pool.submit(task)
        return future
        
    def get_pool(self) -> concurrent.futures.ThreadPoolExecutor:
        """
        Returns the running threadpool.

        Returns:
            concurrent.futures.ThreadPoolExecutor: Running thread pool.

        Raises:
            RuntimeError: If the threadpool is not running.
        """
        if self._pool is not None:
            return self._pool
        else:
            raise RuntimeError("Threadpool is not running. Call start() first.")
            
    def stop(self, wait: bool = True):
        """
        Shutdowns the threadpool.

        Args:
            wait (bool): Whether to wait for running tasks to finish.
        """
        if self._pool is not None:
            self._pool.shutdown(wait=wait)
            self._pool = None
