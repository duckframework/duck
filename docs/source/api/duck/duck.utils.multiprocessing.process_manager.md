# {py:mod}`duck.utils.multiprocessing.process_manager`

```{py:module} duck.utils.multiprocessing.process_manager
```

```{autodocx-docstring} duck.utils.multiprocessing.process_manager
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`HeartbeatHealthCheck <duck.utils.multiprocessing.process_manager.HeartbeatHealthCheck>`
  - ```{autodocx-docstring} duck.utils.multiprocessing.process_manager.HeartbeatHealthCheck
    :summary:
    ```
* - {py:obj}`WorkerProcessManager <duck.utils.multiprocessing.process_manager.WorkerProcessManager>`
  - ```{autodocx-docstring} duck.utils.multiprocessing.process_manager.WorkerProcessManager
    :summary:
    ```
````

### API

`````{py:class} HeartbeatHealthCheck(heartbeat_timeout: float)
:canonical: duck.utils.multiprocessing.process_manager.HeartbeatHealthCheck

```{autodocx-docstring} duck.utils.multiprocessing.process_manager.HeartbeatHealthCheck
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.utils.multiprocessing.process_manager.HeartbeatHealthCheck.__init__
```

````{py:method} __call__(process: multiprocessing.Process, idx: int) -> bool
:canonical: duck.utils.multiprocessing.process_manager.HeartbeatHealthCheck.__call__

```{autodocx-docstring} duck.utils.multiprocessing.process_manager.HeartbeatHealthCheck.__call__
```

````

````{py:method} check_health(process: multiprocessing.Process, idx: int) -> bool
:canonical: duck.utils.multiprocessing.process_manager.HeartbeatHealthCheck.check_health

```{autodocx-docstring} duck.utils.multiprocessing.process_manager.HeartbeatHealthCheck.check_health
```

````

````{py:method} update_heartbeat(idx: int)
:canonical: duck.utils.multiprocessing.process_manager.HeartbeatHealthCheck.update_heartbeat

```{autodocx-docstring} duck.utils.multiprocessing.process_manager.HeartbeatHealthCheck.update_heartbeat
```

````

`````

````{py:exception} HeartbeatUpdateNeverCalled()
:canonical: duck.utils.multiprocessing.process_manager.HeartbeatUpdateNeverCalled

Bases: {py:obj}`Exception`

```{autodocx-docstring} duck.utils.multiprocessing.process_manager.HeartbeatUpdateNeverCalled
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.utils.multiprocessing.process_manager.HeartbeatUpdateNeverCalled.__init__
```

````

`````{py:class} WorkerProcessManager(worker_fn: typing.Callable, num_workers: int, args_fn: typing.Optional[typing.Callable[[int], tuple]] = None, worker_name_fn: typing.Optional[typing.Callable[[int], str]] = None, health_check_fn: typing.Optional[typing.Union[typing.Callable[[multiprocessing.Process], bool], duck.utils.multiprocessing.process_manager.HeartbeatHealthCheck]] = None, restart_timeout: typing.Union[int, float] = 5, enable_logs: bool = True, verbose_logs: bool = True, enable_monitoring: bool = True, process_stop_timeout: typing.Optional[float] = 5.0, daemon: bool = False)
:canonical: duck.utils.multiprocessing.process_manager.WorkerProcessManager

```{autodocx-docstring} duck.utils.multiprocessing.process_manager.WorkerProcessManager
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.utils.multiprocessing.process_manager.WorkerProcessManager.__init__
```

````{py:method} _monitor_loop()
:canonical: duck.utils.multiprocessing.process_manager.WorkerProcessManager._monitor_loop

```{autodocx-docstring} duck.utils.multiprocessing.process_manager.WorkerProcessManager._monitor_loop
```

````

````{py:method} _restart_worker(idx: int)
:canonical: duck.utils.multiprocessing.process_manager.WorkerProcessManager._restart_worker

```{autodocx-docstring} duck.utils.multiprocessing.process_manager.WorkerProcessManager._restart_worker
```

````

````{py:method} running_pids()
:canonical: duck.utils.multiprocessing.process_manager.WorkerProcessManager.running_pids

```{autodocx-docstring} duck.utils.multiprocessing.process_manager.WorkerProcessManager.running_pids
```

````

````{py:method} start()
:canonical: duck.utils.multiprocessing.process_manager.WorkerProcessManager.start

```{autodocx-docstring} duck.utils.multiprocessing.process_manager.WorkerProcessManager.start
```

````

````{py:method} status()
:canonical: duck.utils.multiprocessing.process_manager.WorkerProcessManager.status

```{autodocx-docstring} duck.utils.multiprocessing.process_manager.WorkerProcessManager.status
```

````

````{py:method} stop(graceful: bool = True, wait: bool = True, monitor_stop_timeout: float = 0.5, no_logging: bool = False)
:canonical: duck.utils.multiprocessing.process_manager.WorkerProcessManager.stop

```{autodocx-docstring} duck.utils.multiprocessing.process_manager.WorkerProcessManager.stop
```

````

`````
