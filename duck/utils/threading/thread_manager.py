"""
`WorkerThreadManager` manages and monitors a pool of worker threads.
    
**Features:**
- Automatic restart of dead or unhealthy workers.
- Customizable health-check hooks per worker.
- Threaded non-blocking monitoring loop.
- Configurable logging and verbosity.
- Status inspection and graceful shutdown.
    
Example use cases:
- WSGI/ASGI server worker orchestration.
- ML/AI multi-threaded task runner watchdog.
- Long-running web backend with thread self-repair.

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

def health_check_fn(thread, idx):
    # Returns True if alive; override for custom checks
    return thread.is_alive()

manager = WorkerThreadManager(
    worker_fn=sample_worker,
    num_workers=4,
    args_fn=lambda idx: (...),
    worker_name_fn=lambda idx: f"duck-worker-{idx}",
    health_check_fn=health_check_fn, # Or use HeartbeatHeathCheck object.
    restart_timeout=2,
    enable_logs=True, verbose_logs=False,
    enable_monitoring=True,
    thread_stop_timeout=3,
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
    Thread Health Check using heartbeat approach.  
    
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
        self._heartbeats = {}
        
    def update_heartbeat(self, idx: int):
        """
        Update last heartbeat.
        
        Args:
            idx (int): Index of the thread, usually provided to `worker_fn`.
         
        Raises:
            RuntimeError: If the function is called in main thread or not in a child thread.
        """
        if threading.current_thread() == threading.main_thread():
            raise RuntimeError("This method must be used in a child thread, not main thread.")
        self._heartbeats[idx] = time.time()
       
    def check_health(self, thread: threading.Thread, idx: int) -> bool:
         """
         Checks if last heartbeat hasn't reached a timeout. This may indicate an unhealthy thread.
         
         Returns:
             bool: True if last heartbeat hasn't reached a timeout else False.
         
         Raises:
             HeartbeatUpdateNeverCalled: Raised if no heartbeat update has never been called. 
                 This avoids mistakenly using this approach but not upating heartbeats by calling `update_heartbeat`. 
                 In a thread loop, heartbeat update must be called initialialy before handling any tasks.  
                 
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
             raise HeartbeatUpdateNeverCalled("Heartbeats are empty, meaning you may not be calling `update_heartbeat` in your child thread.")
         last_beat = self._heartbeats.get(idx, 0)
         if time.time() - last_beat > self.heartbeat_timeout:
             return False  # Too long since last heartbeat
         return True    
        
    def __call__(self, thread: threading.Thread, idx: int) -> bool:
        """
        Checks if last heartbeat hasn't reached a timeout. This may indicate an unhealthy thread.
        
        Returns:
            bool: True if last heartbeat hasn't reached a timeout else False.
        
        Raises:
            HeartbeatUpdateNeverCalled: Raised if no heartbeat update has never been updated. 
                This avoids mistakenly using this approach but not upating heartbeats by calling `update_heartbeat`. 
                In a thread loop, heartbeat update must be called initialialy before handling any tasks.  
                
                Example:
                ```py
                healthcheck = HeartbeatHealthCheck(...)
                
                manager = WorkerThreadManager(
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
        return self.check_health(thread, idx)
        

class WorkerThreadManager:
    """
    WorkerThreadManager manages and monitors a pool of worker threads.
    
    **Features:**
    - Automatic restart of dead or unhealthy workers.
    - Customizable health-check hooks per worker.
    - Threaded non-blocking monitoring loop.
    - Configurable logging and verbosity.
    - Status inspection and graceful shutdown.
    
    Example use cases:
    - WSGI/ASGI server worker orchestration.
    - ML/AI multi-thread task runner watchdog.
    - Long-running web backend with thread self-repair.
    """
    def __init__(
        self,
        worker_fn: Callable,
        num_workers: int,
        args_fn: Optional[Callable[[int], tuple]] = None,
        worker_name_fn: Optional[Callable[[int], str]] = None,
        health_check_fn: Optional[Union[Callable[[threading.Thread], bool], HeartbeatHealthCheck]] = None,
        restart_timeout: Union[int, float] = 5,
        enable_logs: bool = True,
        verbose_logs: bool = True,
        enable_monitoring: bool = True,
        thread_stop_timeout: Optional[float] = 5.0,
        daemon: bool = False,
    ):
        """
        Args:
            worker_fn (Callable): Function executed by each worker thread.
            num_workers (int): Number of worker threads to start.
            args_fn (Optional[Callable]): Callable (idx) => tuple for args per worker.
            worker_name_fn (Optional[Callable]): Callable (idx) => str; worker thread name.
            health_check_fn (Optional[Union[Callable[[threading.Thread], bool], HeartbeatHealthCheck): Callable (Thread) => bool: Function to check health; must return True if worker healthy, False otherwise. 
                You can just supply `HeartbeatHealthCheck` object instead to use heartbeat health check.
            restart_timeout (int|float): Seconds to wait before restart on thread death.
            enable_logs (bool): Enable info/warning logging.
            verbose_logs (bool): Enable full exception trace logs.
            enable_monitoring (bool): Start monitor thread automatically.
            thread_stop_timeout (Optional[float]): Maximum seconds to wait for worker to stop. Will be parsed to `join()` method.
            daemon (bool): Whether to start daemon threads. Defaults to False.
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
        self.thread_stop_timeout = thread_stop_timeout
        self.daemon = daemon
        self.worker_threads = []
        self.worker_locks = [threading.Lock() for _ in range(num_workers)]
        self.running = False
        self.monitor_thread = None
        
        def worker_fn_wrapper(*args, **kwargs):
            self.worker_fn(*args, **kwargs)
        
        # Assign wrapper; will be called for starting child thread
        self.worker_fn_wrapper = worker_fn_wrapper

    def start(self):
        """
        Start worker threads and non-blocking monitor loop.
        """
        self.running = True
        self.worker_threads = []

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
            
            # Start the child thread
            name = self.worker_name_fn(i)
            t = threading.Thread(
                target=self.worker_fn_wrapper,
                args=args,
                name=name,
            )
            t.start()
            self.worker_threads.append(t)
            
        if self.enable_monitoring:
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
        
        if self.enable_logs:
            logger.log(
                f"Started {self.num_workers} worker {'threads' if self.num_workers != 1 else 'thread'}; Monitoring: {'ON' if self.enable_monitoring else 'OFF'}",
                level=logger.DEBUG,
            )

    def stop(
        self,
        wait: bool = True,
        monitor_stop_timeout: float = 0.5,
        no_logging: bool = False,
    ):
        """
        Stop all worker threads and monitoring thread.
        
        Args:
            wait (bool): Whether to wait for threads to finish stopping. Defaults to True.
            monitor_stop_timeout (float): Timeout for waiting on monitor thread.
            no_logging (bool): Whether to log stop message. Use this to temporarily disable logging of stop message.
        """
        self.running = False
        
        # Stop monitoring thread first.
        if wait and self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=monitor_stop_timeout)
        
        if wait:
            for i, t in enumerate(self.worker_threads):
                t.join(timeout=self.thread_stop_timeout)
                
                if self.enable_logs and t.is_alive() and not no_logging:
                    logger.log(
                        f"Worker thread {t.name} did not shut down gracefully.",
                        level=logger.WARNING,
                    )
        
        if self.enable_logs and not no_logging:
            logger.log(
                "All workers and monitor stopped." if wait else "Stopped worker thread manager.",
                level=logger.INFO,
                custom_color=logger.Fore.MAGENTA,
            )

    def _restart_worker(self, idx: int):
        """
        Restart a worker thread by index.
        """
        with self.worker_locks[idx]:
            old_t = self.worker_threads[idx]
            if old_t.is_alive():
                old_t.join(timeout=5)
                
            # Start new thread
            args = self.args_fn(idx)
            args = (idx, *args) if isinstance(args, Iterable) else (idx, args) # Always include index in args
            if len(args) == 2:
                if args[1] is None:
                    args = (idx, )
                    
            if isinstance(self.health_check_fn, HeartbeatHealthCheck):
                # Parse HeartbeatHealthCheck object in worker_fn
                args = list(args)
                args.insert(1, self.health_check_fn) 
            
            # Start the child thread
            name = self.worker_name_fn(idx)
            new_t = threading.Thread(
                target=self.worker_fn_wrapper,
                args=args,
                name=name,
                daemon=self.daemon,
            )
            
            # Start and update worker threads
            new_t.start()
            self.worker_threads[idx] = new_t
            
            # Log something if logs enabled.
            if self.enable_logs:
                logger.log(
                    f"Restarted worker thread {name} \n",
                    level=logger.WARNING,
                )

    def _monitor_loop(self):
        """
        Monitor thread: checks worker health/liveness and restarts unhealthy/dead workers.
        Non-blocking for main thread.
        """
        heartbeat_never_called_counter = 0
        
        while self.running:
            try:
                for idx, t in enumerate(list(self.worker_threads)):
                    healthy = t.is_alive()
                    if healthy and self.health_check_fn:
                        try:
                            healthy = self.health_check_fn(t, idx)
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
                            # Thread might be terminated
                            break
                            
                        except Exception as e:
                            healthy = False
                            if self.enable_logs:
                                logger.log(f"Exception during health_check_fn: {e}", level=logger.WARNING)
                                if self.verbose_logs:
                                    logger.log_exception(e)
                            time.sleep(2)
                            continue
                             
                    # Thread is not healthy
                    if not healthy:
                        if self.enable_logs:
                            logger.log(
                                f"Detected unhealthy/dead worker {t.name}, restarting...",
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
                        
    def status(self):
        """
        Returns status list for all worker threads.
        Each dict contains (name, alive).
        """
        status = []
        for i, t in enumerate(self.worker_threads):
            status.append({
                "name": t.name,
                "alive": t.is_alive()
            })
        return status
