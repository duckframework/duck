"""
# Centralized Process Manager

This module provides a structured system for managing process-scoped
`ProcessPoolManager` instances with optional task-type protection. It enables
worker processs, request handlers, or subsystem processs to each maintain their own
dedicated process-pool manager, preventing concurrency issues caused by
cross-process state leakage.

## Features
1. **Multiple Manager Namespaces**
   Using the `id` parameter, processs can maintain several different logical
   managers simultaneously (e.g., CPU-bound pool, IO pool, component-render pool).
   Each namespace is isolated without requiring separate registry structures.

2. **Task-Type Protection**
   Each manager can enforce a single allowed `task_type` for submitted tasks.
   This prevents accidental or unsafe mixing of workloads—for example, ensuring
   that:
       - time-sensitive tasks run only in designated pools,
       - component rendering tasks never leak into background worker pools,
       - slow jobs cannot clog request-handling processs.

3. **Daemon and Non-Daemon Worker Control**
   Managers can start process pools with daemon processs (for non-blocking shutdown)
   or non-daemon processs (for guaranteed completion of jobs before exit).

## Typical Usage
```py
def worker_entrypoint():
    # Initialize or reuse the process's manager
    manager = get_or_create_process_manager(id="render")

    # Start a dedicated process pool for rendering tasks
    manager.start(max_workers=4, task_type="component_render")

    future = manager.submit_task(
        some_callable,
        task_type="component_render",
    )
    return future.result()
"""
import setproctitle
import multiprocessing
import concurrent.futures

from typing import (
    Union,
    Optional,
    Callable,
    Any,
    Dict,
    List,
)


REGISTRY: Dict[int, Dict[Any, "ProcessPoolManager"]] = {}


def get_or_create_process_manager(
    id: Optional[Any] = None,
    force_create: bool = False,
    strictly_get: bool = False,
) -> "ProcessPoolManager":
    """
    Retrieve or create the `ProcessPoolManager` instance bound to the current process.
    
    Returns:
        ProcessPoolManager: The resolved or newly created manager instance.
    """
    def resolve(process: multiprocessing.Process):
        managers = REGISTRY.get(process.ident)
        if managers:
            # Manager namespace found
            manager = managers.get(id)
            if manager is None and not strictly_get:
                manager = ProcessPoolManager(process)
                managers[id] = manager
            return manager
        return None

    if strictly_get and force_create:
        raise TypeError("Arguments 'strictly_get' and 'force_create' cannot be both True.")
        
    current = multiprocessing.current_process()
    manager = None
    
    if not force_create:
        manager = resolve(current)
    
    # If resolution failed (root), create a new entry
    if manager is None:
        if strictly_get:
            raise ManagerNotFound("Strict getting of manager is True yet the manager cannot be resolved.")
        manager = ProcessPoolManager(current)
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
            f"Task type '{task_type}' is not permitted in this process pool "
            f"(expected task_type: '{pool_task_type}').\n"
            "To safely submit this task, reinitialize the ProcessPoolManager or restart the pool with the proper task type."
        )
        super().__init__(message)
        self.task_type = task_type
        self.pool_task_type = pool_task_type


class ProcessPoolManager:
    """
    Process pool manager with task type protection.

    Use `start()` to initialize a centralized processpool for sync tasks.
    Restrict submitted tasks by their `task_type`, preventing inappropriate jobs in critical worker pools.
    """
    
    __instances = []
    """
    This is the list of created instances.
    """
    def __init__(self, creator_process: Optional[multiprocessing.Process] = None):
        """
        Initialize the processpool.
        
        Args:
            creator_process (Optional[processing.Process]): This is the process responsible for this manager.'
        """
        self._creator_process = creator_process
        self._pool: Optional[concurrent.futures.ProcessPoolExecutor] = None
        self._max_workers: Optional[int] = None
        self._daemon: Optional[bool] = None
        self._task_type: Optional[str] = None
        self._process_name_prefix = None
        self._mp_context = None
        self._id = id(self)
        ProcessPoolManager.__instances.append(self)
    
    @classmethod
    def all_instances(cls) -> List["ProcessPoolManager"]:
        """
        Returns a list of all created instances so far.
        """
        return ProcessPoolManager.__instances
        
    @classmethod
    def registry(cls) -> Dict[int, Dict[Any, "ProcessPoolManager"]]:
        """
        Returns the registry for created instances. Useful for tracking.
        """
        return REGISTRY
        
    def start(
        self,
        max_workers: int,
        task_type: Optional[str] = None,
        daemon: bool = False,
        process_name_prefix: Optional[str] = None,
        mp_context: Optional[multiprocessing.context.BaseContext] = None,
    ):
        """
        Starts the processpool, ready to accept tasks.

        Args:
            max_workers (int): Maximum processs for pool.
            task_type (Optional[str]): Only allows tasks with this type to be submitted.
                Useful for protecting pools handling critical jobs (e.g., request_handling only).
            daemon (bool): Whether pool worker processs should be daemon processs.
            process_name_prefix (Optional[str]): The prefix for each worker process.
            mp_context: optional multiprocessing context (get_context('spawn'|'fork'|...))
            
        Raises:
            RuntimeError: If process pool already available and initialized.
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
            self._mp_context = mp_context
            self._process_name_prefix = process_name_prefix
            
            self._pool = concurrent.futures.ProcessPoolExecutor(
                max_workers=self._max_workers,
                initializer=self._worker_init,
                mp_context=self._mp_context,
            )

            # Mark processs daemon if requested
            if daemon:
                for t in list(self._pool._processes):
                    t.daemon = True
        else:
            raise RuntimeError("Process pool already active or running.")
            
    def submit_task(
        self,
        task: Callable,
        *args,
        task_type: Optional[str] = None,
        **kwargs,
    ) -> concurrent.futures.Future:
        """
        Submit a task to the process pool.

        Args:
            task (Callable): Callable to execute.
            task_type (Optional[str]): Type/flag of this task. If manager was initialized with
                a specific allowed task_type, this must match or raise UnknownTaskError.

        Raises:
            UnknownTaskError: If task_type mismatches the pool's allowed type.
            RuntimeError: If the process pool is None/not running.

        Returns:
            concurrent.futures.Future: Future for the executing task.
        """
        pool = self.get_pool()
        
        # If protection by task_type is active, enforce it
        if self._task_type is not None:
            if task_type != self._task_type:
                raise UnknownTaskError(task_type, self._task_type)
                
        # Submit task for execution
        future = pool.submit(task, *args, **kwargs)
        return future
        
    def get_pool(self) -> concurrent.futures.ProcessPoolExecutor:
        """
        Returns the running process pool.

        Returns:
            concurrent.futures.ProcessPoolExecutor: Running process pool.

        Raises:
            RuntimeError: If the process pool is not running.
        """
        if self._pool is not None:
            return self._pool
        else:
            raise RuntimeError("Process pool is not running. Call start() first.")
            
    def stop(self, wait: bool = True):
        """
        Shutdowns the process pool.

        Args:
            wait (bool): Whether to wait for running tasks to finish.
        """
        if self._pool is not None:
            self._pool.shutdown(wait=wait)
            self._pool = None
    
    def _worker_init(self):
        """
        Method called when process worker is initialized.
        """
        current = multiprocessing.current_process()
        pname = current.name
        idx = pname.split('-')[-1]
        
        # Set daemon
        current.daemon = self._daemon
        
        if not self._process_name_prefix:
            return
             
        # Prefer setproctitle (shows in ps/top), else set Python-level process name.
        new_pname = "%s-%s"%(self._process_name_prefix, idx)
        
        # Fallback: set Python-level name (visible via multiprocessing.current_process().name)
        try:
            current.name = new_pname
        except Exception:
            pass
            
    def __str__(self):
        return f"<{self.__class__.__name__} id='{self._id}', max_workers={self._max_workers}, creator_process={self._creator_process}>"
    
    def __repr__(self):
        return f"<{self.__class__.__name__} id='{self._id}', max_workers={self._max_workers}, creator_process={self._creator_process}>"
