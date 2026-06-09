# {py:mod}`duck.utils.threading.thread_manager`

```{py:module} duck.utils.threading.thread_manager
```

```{autodocx-docstring} duck.utils.threading.thread_manager
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`HeartbeatHealthCheck <duck.utils.threading.thread_manager.HeartbeatHealthCheck>`
  - ```{autodocx-docstring} duck.utils.threading.thread_manager.HeartbeatHealthCheck
    :summary:
    ```
* - {py:obj}`WorkerThreadManager <duck.utils.threading.thread_manager.WorkerThreadManager>`
  - ```{autodocx-docstring} duck.utils.threading.thread_manager.WorkerThreadManager
    :summary:
    ```
````

### API

`````{py:class} HeartbeatHealthCheck(heartbeat_timeout: float)
:canonical: duck.utils.threading.thread_manager.HeartbeatHealthCheck

```{autodocx-docstring} duck.utils.threading.thread_manager.HeartbeatHealthCheck
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.utils.threading.thread_manager.HeartbeatHealthCheck.__init__
```

````{py:method} __call__(thread: threading.Thread, idx: int) -> bool
:canonical: duck.utils.threading.thread_manager.HeartbeatHealthCheck.__call__

```{autodocx-docstring} duck.utils.threading.thread_manager.HeartbeatHealthCheck.__call__
```

````

````{py:method} check_health(thread: threading.Thread, idx: int) -> bool
:canonical: duck.utils.threading.thread_manager.HeartbeatHealthCheck.check_health

```{autodocx-docstring} duck.utils.threading.thread_manager.HeartbeatHealthCheck.check_health
```

````

````{py:method} update_heartbeat(idx: int)
:canonical: duck.utils.threading.thread_manager.HeartbeatHealthCheck.update_heartbeat

```{autodocx-docstring} duck.utils.threading.thread_manager.HeartbeatHealthCheck.update_heartbeat
```

````

`````

````{py:exception} HeartbeatUpdateNeverCalled()
:canonical: duck.utils.threading.thread_manager.HeartbeatUpdateNeverCalled

Bases: {py:obj}`Exception`

```{autodocx-docstring} duck.utils.threading.thread_manager.HeartbeatUpdateNeverCalled
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.utils.threading.thread_manager.HeartbeatUpdateNeverCalled.__init__
```

````

`````{py:class} WorkerThreadManager(worker_fn: typing.Callable, num_workers: int, args_fn: typing.Optional[typing.Callable[[int], tuple]] = None, worker_name_fn: typing.Optional[typing.Callable[[int], str]] = None, health_check_fn: typing.Optional[typing.Union[typing.Callable[[threading.Thread], bool], duck.utils.threading.thread_manager.HeartbeatHealthCheck]] = None, restart_timeout: typing.Union[int, float] = 5, enable_logs: bool = True, verbose_logs: bool = True, enable_monitoring: bool = True, thread_stop_timeout: typing.Optional[float] = 5.0, daemon: bool = False)
:canonical: duck.utils.threading.thread_manager.WorkerThreadManager

```{autodocx-docstring} duck.utils.threading.thread_manager.WorkerThreadManager
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.utils.threading.thread_manager.WorkerThreadManager.__init__
```

````{py:method} _monitor_loop()
:canonical: duck.utils.threading.thread_manager.WorkerThreadManager._monitor_loop

```{autodocx-docstring} duck.utils.threading.thread_manager.WorkerThreadManager._monitor_loop
```

````

````{py:method} _restart_worker(idx: int)
:canonical: duck.utils.threading.thread_manager.WorkerThreadManager._restart_worker

```{autodocx-docstring} duck.utils.threading.thread_manager.WorkerThreadManager._restart_worker
```

````

````{py:method} start()
:canonical: duck.utils.threading.thread_manager.WorkerThreadManager.start

```{autodocx-docstring} duck.utils.threading.thread_manager.WorkerThreadManager.start
```

````

````{py:method} status()
:canonical: duck.utils.threading.thread_manager.WorkerThreadManager.status

```{autodocx-docstring} duck.utils.threading.thread_manager.WorkerThreadManager.status
```

````

````{py:method} stop(wait: bool = True, monitor_stop_timeout: float = 0.5, no_logging: bool = False)
:canonical: duck.utils.threading.thread_manager.WorkerThreadManager.stop

```{autodocx-docstring} duck.utils.threading.thread_manager.WorkerThreadManager.stop
```

````

`````
