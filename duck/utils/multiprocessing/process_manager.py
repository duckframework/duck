"""
`WorkerProcessManager` manages and monitors a pool of worker processes.
    
**Features:**
- Automatic restart of dead or unhealthy workers.
- Customizable health-check hooks per worker.
- Threaded non-blocking monitoring loop.
- Configurable logging and verbosity.
- Status inspection and graceful shutdown.
    
Example use cases:
- WSGI/ASGI server worker orchestration.
- ML/AI multi-process task runner watchdog.
- Long-running web backend with process self-repair.

Usage Example:
```py
def sample_worker(idx, *args):
    import time, random
    print(f"Worker {idx} started...")
    
    while True:
        time.sleep(1)
        print(f"[Worker {idx}] Sleeping")
        
        # Simulate random crash; restart will occur
        if random.random() < 0.03:
            print(f"[Worker {idx}] Simulating crash")
            exit(1)

def health_check_fn(proc, idx):
    # Returns True if alive; override for custom checks
    return proc.is_alive()

manager = WorkerProcessManager(
    worker_fn=sample_worker,
    num_workers=4,
    args_fn=lambda idx: (...),
    worker_name_fn=lambda idx: f"duck-worker-{idx}",
    health_check_fn=health_check_fn, # Or use HeartbeatHeathCheck object.
    restart_timeout=2,
    enable_logs=True, verbose_logs=False,
    enable_monitoring=True,
    process_stop_timeout=3,
)

try:
    manager.start()
    for _ in range(20):  # Monitor for a while
        print("Worker status:", manager.status())
        time.sleep(2)
finally:
    manager.stop()
```
"""
import os
import time
import logging
import threading
import multiprocessing
import setproctitle

from typing import (
    Callable,
    Optional,
    Union,
    Iterable,
)

from duck.exceptions.all import SettingsError

try:
    from duck.logging import logger
except SettingsError:
    from duck.logging import console as logger


class HeartbeatUpdateNeverCalled(Exception):
    """
    Raised by `HeartbeatHealthCheck.check_health` if heartbeats are empty.
    """
    

class HeartbeatHealthCheck:
    """
    Process Health Check using heartbeat approach.  
    
    Example:
    ```py
    healthcheck = HeartbeatHealthCheck(...)
                
    def worker_fn(idx, healthcheck, ...):
        while True:
            healthcheck.update_heartbeat(idx)
            # Some tasks here
            ...
    ``` 
    """
    def __init__(self, heartbeat_timeout: float):
        """
        Initialize heartbeat health check.
        """
        self.heartbeat_timeout = heartbeat_timeout
        self._multiprocessing_manager = multiprocessing.Manager()
        self._heartbeats = self._multiprocessing_manager.dict()
        
    def update_heartbeat(self, idx: int):
        """
        Update last heartbeat.
        
        Args:
            idx (int): Index of the process, usually provided to `worker_fn`.
         
        Raises:
            RuntimeError: If the function is called in main process or not in a child process.
        """
        if not multiprocessing.parent_process():
            raise RuntimeError("This method must be used in a child process, not main process.")
        self._heartbeats[idx] = time.time()
       
    def check_health(self, process: multiprocessing.Process, idx: int) -> bool:
         """
         Checks if last heartbeat hasn't reached a timeout. This may indicate an unhealthy process.
         
         Returns:
             bool: True if last heartbeat hasn't reached a timeout else False.
         
         Raises:
             HeartbeatUpdateNeverCalled: Raised if no heartbeat update has never been called. 
                 This avoids mistakenly using this approach but not upating heartbeats by calling `update_heartbeat`. 
                 In a process loop, heartbeat update must be called initialialy before handling any tasks.  
                 
                 Example:
                 ```py
                 healthcheck = HeartbeatHealthCheck(...)
                 
                 def worker_fn(idx, healthcheck, ...):
                     while True:
                         healthcheck.update_heartbeat(idx)
                         # Some tasks here
                         ...
                 ``` 
         """
         if not self._heartbeats:
             raise HeartbeatUpdateNeverCalled("Heartbeats are empty, meaning you may not be calling `update_heartbeat` in your child process.")
         last_beat = self._heartbeats.get(idx, 0)
         if time.time() - last_beat > self.heartbeat_timeout:
             return False  # Too long since last heartbeat
         return True    
        
    def __call__(self, process: multiprocessing.Process, idx: int) -> bool:
        """
        Checks if last heartbeat hasn't reached a timeout. This may indicate an unhealthy process.
        
        Returns:
            bool: True if last heartbeat hasn't reached a timeout else False.
        
        Raises:
            HeartbeatUpdateNeverCalled: Raised if no heartbeat update has never been updated. 
                This avoids mistakenly using this approach but not upating heartbeats by calling `update_heartbeat`. 
                In a process loop, heartbeat update must be called initialialy before handling any tasks.  
                
                Example:
                ```py
                healthcheck = HeartbeatHealthCheck(...)
                
                manager = WorkerProcessManager(
                    health_check_fn=healthcheck,
                    ...
                )
                
                def worker_fn(idx, healthcheck, ...):
                    while True:
                        healthcheck.update_heartbeat(idx)
                        # Some tasks here
                        ...
                ``` 
        """
        return self.check_health(process, idx)
        

class WorkerProcessManager:
    """
    WorkerProcessManager manages and monitors a pool of worker processes.
    
    **Features:**
    - Automatic restart of dead or unhealthy workers.
    - Customizable health-check hooks per worker.
    - Threaded non-blocking monitoring loop.
    - Configurable logging and verbosity.
    - Status inspection and graceful shutdown.
    
    Example use cases:
    - WSGI/ASGI server worker orchestration.
    - ML/AI multi-process task runner watchdog.
    - Long-running web backend with process self-repair.
    """
    def __init__(
        self,
        worker_fn: Callable,
        num_workers: int,
        args_fn: Optional[Callable[[int], tuple]] = None,
        worker_name_fn: Optional[Callable[[int], str]] = None,
        health_check_fn: Optional[Union[Callable[[multiprocessing.Process], bool], HeartbeatHealthCheck]] = None,
        restart_timeout: Union[int, float] = 5,
        enable_logs: bool = True,
        verbose_logs: bool = True,
        enable_monitoring: bool = True,
        process_stop_timeout: Optional[float] = 5.0,
        daemon: bool = False,
    ):
        """
        Args:
            worker_fn (Callable): Function executed by each worker process.
            num_workers (int): Number of worker processes to spawn.
            args_fn (Optional[Callable]): Callable (idx) => tuple for args per worker.
            worker_name_fn (Optional[Callable]): Callable (idx) => str; worker process name.
            health_check_fn (Optional[Union[Callable[[multiprocessing.Process], bool], HeartbeatHealthCheck): Callable (Process) => bool: Function to check health; must return True if worker healthy, False otherwise. 
                You can just supply `HeartbeatHealthCheck` object instead to use heartbeat health check.
            restart_timeout (int|float): Seconds to wait before restart on process death.
            enable_logs (bool): Enable info/warning logging.
            verbose_logs (bool): Enable full exception trace logs.
            enable_monitoring (bool): Start monitor thread automatically.
            process_stop_timeout (Optional[float]): Maximum seconds to wait for worker to stop. Will be parsed to `join()` method.
            daemon (bool): Whether to start daemon processes. Defaults to False.
        """
        self.worker_fn = worker_fn
        self.num_workers = num_workers
        self.args_fn = args_fn or (lambda idx: ())
        self.worker_name_fn = worker_name_fn or (lambda idx: f"worker-{idx}")
        self.health_check_fn = health_check_fn
        self.restart_timeout = restart_timeout
        self.enable_logs = enable_logs
        self.verbose_logs = verbose_logs
        self.enable_monitoring = enable_monitoring
        self.process_stop_timeout = process_stop_timeout
        self.daemon = daemon
        self.worker_processes = []
        self.worker_locks = [threading.Lock() for _ in range(num_workers)]
        self.running = False
        self.monitor_thread = None
        
        def worker_fn_wrapper(*args, **kwargs):
            # Set process title
            p = multiprocessing.current_process()
            setproctitle.setproctitle(p.name)
            self.worker_fn(*args, **kwargs)
        
        # Assign wrapper; will be called for starting child process
        self.worker_fn_wrapper = worker_fn_wrapper

    def start(self):
        """
        Start worker processes and non-blocking monitor loop.
        """
        self.running = True
        self.worker_processes = []

        for i in range(self.num_workers):
            args = self.args_fn(i)
            args = (i, *args) if isinstance(args, Iterable) else (i, args) # Always include index in args
            
            if len(args) == 2:
                if args[1] is None:
                    args = (i, )
            
            if isinstance(self.health_check_fn, HeartbeatHealthCheck):
                # Parse HeartbeatHealthCheck object in worker_fn
                args = list(args)
                args.insert(1, self.health_check_fn) 
            
            # Start the child process
            name = self.worker_name_fn(i)
            p = multiprocessing.Process(
                target=self.worker_fn_wrapper,
                args=args,
                name=name,
            )
            p.start()
            self.worker_processes.append(p)
            
        if self.enable_monitoring:
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
        
        if self.enable_logs:
            logger.log(
                f"Spawned {self.num_workers} worker {'processes' if self.num_workers != 1 else 'process'}; Monitoring: {'ON' if self.enable_monitoring else 'OFF'}",
                level=logger.DEBUG,
            )

    def stop(
        self,
        graceful: bool = True,
        wait: bool = True,
        monitor_stop_timeout: float = 0.5,
        no_logging: bool = False,
    ):
        """
        Stop all worker processes and monitoring thread.
        
        Args:
            graceful (bool): Use terminate() for workers (soft shutdown).
            wait (bool): Whether to wait for processes to finish stopping. Defaults to True.
            monitor_stop_timeout (float): Timeout for waiting on monitor thread.
            no_logging (bool): Whether to log stop message. Use this to temporarily disable logging of stop message.
        """
        self.running = False
        
        # Stop monitoring thread first.
        if wait and self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=monitor_stop_timeout)
        
        # Now terminate alive processes
        for i, p in enumerate(self.worker_processes):
            if p.is_alive():
                if graceful:
                    p.terminate()
                else:
                    try:
                        p.kill()
                    except AttributeError:
                        p.terminate()
        
        if wait:
            for i, p in enumerate(self.worker_processes):
                p.join(timeout=self.process_stop_timeout)
                if p.is_alive():
                    # Force kill if possible (note: kill only on Unix)
                    try:
                        p.kill()
                    except AttributeError:
                        p.terminate()
    
                if self.enable_logs and p.is_alive() and not no_logging:
                    logger.log(
                        f"Worker process {p.name} (pid={p.pid}) did not shut down gracefully.",
                        level=logger.WARNING,
                    )
        
        if self.enable_logs and not no_logging:
            logger.log(
                "All workers and monitor stopped." if wait else "Stopped worker process manager.",
                level=logger.INFO,
                custom_color=logger.Fore.MAGENTA,
            )

    def _restart_worker(self, idx: int):
        """
        Restart a worker process by index.
        """
        with self.worker_locks[idx]:
            old_p = self.worker_processes[idx]
            if old_p.is_alive():
                old_p.terminate()
                old_p.join(timeout=5)
                
            # Start new process
            args = self.args_fn(idx)
            args = (idx, *args) if isinstance(args, Iterable) else (idx, args) # Always include index in args
            if len(args) == 2:
                if args[1] is None:
                    args = (idx, )
                    
            if isinstance(self.health_check_fn, HeartbeatHealthCheck):
                # Parse HeartbeatHealthCheck object in worker_fn
                args = list(args)
                args.insert(1, self.health_check_fn) 
            
            # Start the child process
            name = self.worker_name_fn(idx)
            new_p = multiprocessing.Process(
                target=self.worker_fn_wrapper,
                args=args,
                name=name,
                daemon=self.daemon,
            )
            
            # Start and update worker process
            new_p.start()
            self.worker_processes[idx] = new_p
            
            # Log something if logs enabled.
            if self.enable_logs:
                logger.log(
                    f"Restarted worker process {name} (pid={new_p.pid})\n",
                    level=logger.WARNING,
                )

    def _monitor_loop(self):
        """
        Monitor thread: checks worker health/liveness and restarts unhealthy/dead workers.
        Non-blocking for main thread.
        """
        time.sleep(2) # Sleep a little
        heartbeat_never_called_counter = 0
        
        while self.running:
            try:
                for idx, p in enumerate(list(self.worker_processes)):
                    healthy = p.is_alive()
                    if healthy and self.health_check_fn:
                        try:
                            healthy = self.health_check_fn(p, idx)
                        except HeartbeatUpdateNeverCalled as e:
                            healthy = False
                            
                            if self.enable_logs and heartbeat_never_called_counter > 0:
                                # Don't log first error of this type, give .
                                logger.log(f"Exception during health_check_fn: {e}", level=logger.WARNING)
                                if self.verbose_logs:
                                    logger.log_exception(e)
                                    
                            # Wait for heartbeat_timeout and continue
                            heartbeat_never_called_counter += 1
                            time.sleep(self.health_check_fn.heartbeat_timeout)
                            continue
                             
                        except (KeyboardInterrupt, BrokenPipeError):
                            # Process might be terminated
                            break
                            
                        except Exception as e:
                            healthy = False
                            if self.enable_logs:
                                logger.log(f"Exception during health_check_fn: {e}", level=logger.WARNING)
                                if self.verbose_logs:
                                    logger.log_exception(e)
                            time.sleep(2)
                            continue
                             
                    # Process is not healthy
                    if not healthy:
                        if self.enable_logs:
                            logger.log(
                                f"Detected unhealthy/dead worker ({p.name}, pid={p.pid}), restarting...",
                                level=logger.WARNING,
                            )
                        self._restart_worker(idx)
                        time.sleep(self.restart_timeout)
                
                # Sleep a little
                time.sleep(2)
                
            except Exception as e:
                if self.enable_logs:
                    logger.log(f"Error in monitor loop: {e}", level=logger.WARNING)
                    if self.verbose_logs:
                        logger.log_exception(e)

    def running_pids(self):
        """
        Returns a list of PIDs for currently alive worker processes.
        """
        return [p.pid for p in self.worker_processes if p.is_alive()]

    def status(self):
        """
        Returns status list for all worker processes.
        Each dict contains (name, pid, alive).
        """
        status = []
        for i, p in enumerate(self.worker_processes):
            status.append({
                "name": p.name,
                "pid": p.pid,
                "alive": p.is_alive()
            })
        return status
