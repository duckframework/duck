"""
# Asyncio Loop Manager With Thread-Based Context Propagation

This module provides a structured system for managing asyncio event loops that run
inside dedicated background threads. It enables synchronous code (including worker
threads, component systems, WSGI-like environments, and blocking server logic)
to safely submit and await asyncio coroutines without requiring a running loop
in the current thread.

Unlike globally shared event loops—which cause cross-context contamination,
unbounded concurrency, and invalid reentrancy—each loop manager created by this
module is *thread-scoped* and optional-task-type-protected, ensuring strong
isolation for component rendering, per-request async operations, and specialized
background jobs.

## Core Components

1. **AsyncioLoopManager**
   A manager that:
   - initializes a dedicated asyncio event loop,
   - runs it inside a background thread,
   - allows synchronous code to submit async tasks,
   - optionally restricts allowed task types (e.g., `"update"`, `"render"`),
   - supports blocking behavior via `SyncFuture`.

   This bridges synchronous and asynchronous subsystems safely, without requiring
   callers to understand asyncio internals or manage loops manually.

2. **SyncFuture**
   A thread-safe future that lets synchronous callers block until an async
   coroutine completes. This provides an ergonomic way to mix async/sync code
   without deadlocks or event-loop mismanagement.

3. **Thread-Scoped Manager Registry**
   Loop managers are registered per-thread (and per-ID), and automatically
   inherited by child threads via a lineage-resolution system. This ensures:
   - consistent async context for worker threads,
   - isolation of async operations across independent request handlers,
   - avoidance of global-state conflicts.

4. **Task-Type Protection**
   Optional enforcement that allows only a specific `task_type` to be submitted
   into a given loop. This prevents misrouting workloads—for example:
   - keeping component-rendering coroutines separate from background updates,
   - preventing slow tasks from being scheduled into latency-critical loops,
   - enforcing strict execution domains for sensitive operations.

## Motivation

Frameworks that must bridge the sync/async boundary—such as servers using
thread-per-request models, component rendering systems, hybrid blocking/
non-blocking architectures, or environments where loops cannot be run
directly—need a safe, isolated way to schedule coroutines.

## Typical pitfalls solved by this module:
- **Running async code inside random threads**: leads to `RuntimeError: no running event loop`.
- **Global event loop sharing**: creates race conditions and cross-context pollution.
- **Worker threads needing async helpers** without owning an event loop.
- **Component systems generating async work** inside sync call stacks.
- **Preventing unrelated tasks from entering specialized async domains**.

This module eliminates these pitfalls by providing predictable, isolated event
loops that behave like mini-ASGI environments local to each thread.

## Thread Lineage Model

Loop managers are resolved using a hierarchical lookup:

1. Start with the current thread.
2. If it has a manager for the requested ID, return it.
3. If not, recursively check its parent thread.
4. If none exist in the lineage, create and attach a new manager.

This mirrors context inheritance in modern frameworks and avoids global
state entirely.

## Multiple Manager Namespaces

Managers are identified by an optional `id`:

- Calling `get_or_create_loop_manager(id="render-loop")`
  creates or retrieves a loop dedicated to rendering operations.
- Calling `get_or_create_loop_manager(id="background-io")`
  yields an entirely separate loop for I/O-heavy async tasks.

This encourages clean separation of execution domains without rewriting
infrastructure.

Typical Usage

```py
def worker():
    loop_mgr = get_or_create_loop_manager(id="component")
    loop_mgr.start(task_type="render")

    # Submit coroutine and block for result
    value = loop_mgr.submit_task(
        some_async_function(),
        return_sync_future=True,
        task_type="render",
     )
     value = value.result()
     return value
```

## Best Practices

- Always resolve loop managers *inside* worker threads to avoid sharing the
  main thread’s manager unintentionally.
- Use task-type protection to ensure coroutine routing guarantees.
- Use unique IDs for logically distinct async domains.
- Never directly interact with the internal REGISTRY.

This module provides a safe, controlled, extensible foundation for mixing
async and synchronous workloads in complex frameworks such as the Duck
Lively Component system.
"""

import asyncio
import threading

from typing import (
    Union,
    Coroutine,
    Optional,
    Any,
    List,
    Dict,
)

from duck.utils.threading import SyncFuture, async_to_sync_future
from duck.utils.threading.patch import get_parent_thread


REGISTRY = {}


def get_or_create_loop_manager(
    id: Optional[Any] = None,
    force_create: bool = False,
    strictly_get: bool = False,
) -> "AsyncioLoopManager":
    """
    Retrieve or create an `AsyncioLoopManager` instance scoped to the current
    thread lineage, with optional namespace isolation.

    This function provides a hierarchical registry: each thread may own multiple
    managers, identified by user-supplied `id` namespaces. If a manager is not
    found in the current thread, its parent thread is searched recursively,
    allowing thread families to inherit managers unless isolation is explicitly
    requested.

    **Thread-scoped behavior**
    - Without `force_create`, the manager resolution walks upward through
      parent threads until it finds a matching manager for the given `id`.
    - With `force_create=True`, a new manager is always created for the
      current thread, regardless of parent managers.

    **Use cases**
    - Worker threads that must run async tasks in their own protected loop.
    - Request-scoped or component-scoped corruption-free async execution.
    - Shared background async loop across a thread tree, unless isolation is
      desired.

    Args:
        id (Optional[Any]):
            Optional namespace key. Managers with different `id` values can
            coexist within the same thread. Using the same `id` retrieves the
            same manager.  
            
            Examples:
            ```py
            default_mgr = get_or_create_loop_manager()
            io_mgr      = get_or_create_loop_manager(id="io")
            job_mgr     = get_or_create_loop_manager(id="job-executor")
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
    - Calling this function in the main thread makes the returned manager
      automatically inherited by all descendant threads unless they specify
      `force_create=True`.
    - The lookup chain stops at the root thread; if no manager is found,
      a new one is created and registered.
    - If you already have created manager, use `strictly_get` argument to strictly get your 
      created manager or raise an exception if manager not found without creating new one.

    Returns:
        AsyncioLoopManager: The resolved manager or a newly created instance.
    """
    def resolve(thread: threading.Thread):
        managers = REGISTRY.get(thread.ident)
        if managers:
            # Manager namespace found
            manager = managers.get(id, None)
            if manager is None and not strictly_get:
                manager = AsyncioLoopManager(thread)
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
        manager = AsyncioLoopManager(current)
        REGISTRY[current.ident] = {id: manager}
    return manager


class ManagerNotFound(Exception):
    """
    Raised if manager cannot be resolved and user strictly wants to get the manager and user doesn't allow creating 
    it if it doesn't exist.
    """
    

class UnknownAsyncTaskError(Exception):
    """
    Raised when attempting to submit a coroutine of a disallowed or unexpected type
    to a protected asyncio loop.
    """
    def __init__(self, given_type, expected_type):
        message = (
            f"Async task type '{given_type}' is not permitted in this event loop "
            f"(required type: '{expected_type}').\n"
            "To safely submit this task, restart AsyncioLoopManager with the desired task_type, or reinitialize."
        )
        super().__init__(message)
        self.given_type = given_type
        self.expected_type = expected_type


class AsyncioLoopManager:
    """
    A manager that runs an asyncio event loop in a background thread,
    with optional task type protection.

    Notes:
    - This starts an asyncio event loop in a single global thread.
    - Allows submitting coroutines from synchronous code.
    - Supports synchronous result blocking via SyncFuture.
    - Can restrict tasks by type to prevent inappropriate coroutine submission to protected loops.
    - Using the event loop directly is not recommended and it seems not to work, use `submit_task` instead.
    """
    
    __instances = []
    """
    This is the list of created instances.
    """
    
    def __init__(self, creator_thread: Optional[threading.Thread] = None):
        """
        Initialize the threadpool.
        
        Args:
            creator_thread (Optional[threading.Thread]): This is the thread responsible for this manager.'
        """
        self._creator_thread = creator_thread
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._thread: Optional[threading.Thread] = None
        self._task_type: Optional[str] = None
        AsyncioLoopManager.__instances.append(self)
        
    @classmethod
    def all_instances(cls) -> List["AsyncioLoopManager"]:
        """
        Returns a list of all created instances so far.
        """
        return ThreadPoolManger.__instances
        
    @classmethod
    def registry(cls) -> Dict[int, Dict[Any, "AsyncioLoopManager"]]:
        """
        Returns the registry for created instances. Useful for tracking.
        """
        return REGISTRY
        
    def start(self, task_type: Optional[str] = None):
        """
        Starts the event loop in a background thread if it's not already running.

        Args:
            task_type (Optional[str]): The expected type of async tasks 
                for this loop. If set, only tasks with matching type will be accepted.
        
        Raises:
            RuntimeError: If event loop is not None and loop's thread is alive.
        """
        if self._loop is None:
            self._loop = asyncio.new_event_loop()
        self._task_type = task_type

        def run_loop():
            asyncio.set_event_loop(self._loop)
            self._loop.run_forever()

        if self._thread is None or not self._thread.is_alive():
            self._thread = threading.Thread(target=run_loop)
            self._thread.start()
        else:
            raise RuntimeError("Asyncio loop is not None and event loop's thread is alive.")
            
    def submit_task(
        self, 
        coro: Coroutine, 
        return_sync_future: bool = False, 
        task_type: Optional[str] = None
    ) -> Union[SyncFuture, asyncio.Future]:
        """
        Submit an asynchronous coroutine to the event loop, with optional task type protection.

        Args:
            coro (Coroutine): The coroutine to schedule.
            return_sync_future (bool): If True, wraps the result in a SyncFuture for blocking use.
            task_type (Optional[str]): The type of this async task; must match manager's required type if set.

        Returns:
            Union[SyncFuture, asyncio.Future]: A future representing the scheduled coroutine.

        Raises:
            UnknownAsyncTaskError: If the provided type doesn't match the loop's protected type.
            RuntimeError: If the event loop is not running.
        """
        if self._loop is not None and self._loop.is_running():
            # Enforce task type protection if set
            if self._task_type is not None:
                if task_type != self._task_type:
                    raise UnknownAsyncTaskError(task_type, self._task_type)
            future = asyncio.run_coroutine_threadsafe(coro, self._loop)
            if return_sync_future:
                future = async_to_sync_future(future)
            return future
        else:
            raise RuntimeError("Event loop is not running. Method start() must be called first.")
            
    def get_event_loop(self) -> asyncio.AbstractEventLoop:
        """
        Returns the running asyncio event loop.

        Returns:
            asyncio.AbstractEventLoop: The currently running event loop.

        Raises:
            RuntimeError: If the loop isn't running.
        """
        if self._loop is not None and self._loop.is_running():
            return self._loop
        else:
            raise RuntimeError("Event loop is not running. Call start() first.")
            
    def stop(self):
        """
        Stops the event loop and waits for the thread to finish.

        Notes:
            This should be called to clean up the background loop thread.
        """
        if self._loop:
            self._loop.call_soon_threadsafe(self._loop.stop)
            if self._thread:
                self._thread.join()
            self._loop = None
            self._thread = None
            self._task_type = None

    def __str__(self):
        return f"<{self.__class__.__name__} creator_thread={self._creator_thread}>"
    
    def __repr__(self):
        return f"<{self.__class__.__name__} creator_thread={self._creator_thread}>"
