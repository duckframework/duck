# {py:mod}`duck.app.app`

```{py:module} duck.app.app
```

```{autodocx-docstring} duck.app.app
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`App <duck.app.app.App>`
  - ```{autodocx-docstring} duck.app.app.App
    :summary:
    ```
````

### API

`````{py:class} App(name: typing.Optional[str] = None, addr: str = DEFAULT_ADDR, port: int = DEFAULT_PORT, domain: typing.Optional[str] = None, server_url: typing.Optional[str] = None, uses_ipv6: bool = False, process_name: typing.Optional[str] = None, workers: typing.Optional[int] = None, force_worker_processes: bool = False, https_redirect_logs: bool = False, https_redirect_workers: typing.Optional[int] = None, https_redirect_force_worker_processes: bool = False, start_bg_eventloop_if_wsgi: bool = True, disable_signal_handler: bool = False, disable_ipc_handler: bool = False, no_checks: bool = False, skip_setup: bool = False, events: typing.Optional[typing.Dict[str, typing.Optional[typing.Callable]]] = None)
:canonical: duck.app.app.App

Bases: {py:obj}`duck.app.base.BaseApp`

```{autodocx-docstring} duck.app.app.App
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.app.app.App.__init__
```

````{py:attribute} DEFAULT_ADDR
:canonical: duck.app.app.App.DEFAULT_ADDR
:value: >
   'localhost'

```{autodocx-docstring} duck.app.app.App.DEFAULT_ADDR
```

````

````{py:attribute} DEFAULT_PORT
:canonical: duck.app.app.App.DEFAULT_PORT
:value: >
   8000

```{autodocx-docstring} duck.app.app.App.DEFAULT_PORT
```

````

````{py:attribute} __instances__
:canonical: duck.app.app.App.__instances__
:value: >
   0

```{autodocx-docstring} duck.app.app.App.__instances__
```

````

````{py:attribute} __mainapp__
:canonical: duck.app.app.App.__mainapp__
:value: >
   None

```{autodocx-docstring} duck.app.app.App.__mainapp__
```

````

````{py:method} _on_app_start()
:canonical: duck.app.app.App._on_app_start

```{autodocx-docstring} duck.app.app.App._on_app_start
```

````

````{py:method} _run(print_ansi_art: bool = True)
:canonical: duck.app.app.App._run

```{autodocx-docstring} duck.app.app.App._run
```

````

````{py:property} absolute_uri
:canonical: duck.app.app.App.absolute_uri
:type: str

```{autodocx-docstring} duck.app.app.App.absolute_uri
```

````

````{py:property} absolute_ws_uri
:canonical: duck.app.app.App.absolute_ws_uri
:type: str

```{autodocx-docstring} duck.app.app.App.absolute_ws_uri
```

````

````{py:method} check_ssl_credentials()
:canonical: duck.app.app.App.check_ssl_credentials
:staticmethod:

```{autodocx-docstring} duck.app.app.App.check_ssl_credentials
```

````

````{py:property} django_server_up
:canonical: duck.app.app.App.django_server_up
:type: bool

```{autodocx-docstring} duck.app.app.App.django_server_up
```

````

````{py:method} get_main_app() -> duck.app.app.App
:canonical: duck.app.app.App.get_main_app
:classmethod:

```{autodocx-docstring} duck.app.app.App.get_main_app
```

````

````{py:method} get_runtime_futures() -> typing.Dict[str, typing.Optional[concurrent.futures.Future]]
:canonical: duck.app.app.App.get_runtime_futures

```{autodocx-docstring} duck.app.app.App.get_runtime_futures
```

````

````{py:method} handle_ipc_messages()
:canonical: duck.app.app.App.handle_ipc_messages

```{autodocx-docstring} duck.app.app.App.handle_ipc_messages
```

````

````{py:method} handle_signal(sig, frame)
:canonical: duck.app.app.App.handle_signal

```{autodocx-docstring} duck.app.app.App.handle_signal
```

````

````{py:property} https_redirect_server_up
:canonical: duck.app.app.App.https_redirect_server_up
:type: bool

```{autodocx-docstring} duck.app.app.App.https_redirect_server_up
```

````

````{py:method} instances() -> int
:canonical: duck.app.app.App.instances
:classmethod:

```{autodocx-docstring} duck.app.app.App.instances
```

````

````{py:method} log_component_system_warnings()
:canonical: duck.app.app.App.log_component_system_warnings

```{autodocx-docstring} duck.app.app.App.log_component_system_warnings
```

````

````{py:method} log_startup_warnings()
:canonical: duck.app.app.App.log_startup_warnings

```{autodocx-docstring} duck.app.app.App.log_startup_warnings
```

````

````{py:property} meta
:canonical: duck.app.app.App.meta
:type: typing.Dict[str, typing.Any]

```{autodocx-docstring} duck.app.app.App.meta
```

````

````{py:property} process_id
:canonical: duck.app.app.App.process_id
:type: int

```{autodocx-docstring} duck.app.app.App.process_id
```

````

````{py:method} record_metadata()
:canonical: duck.app.app.App.record_metadata

```{autodocx-docstring} duck.app.app.App.record_metadata
```

````

````{py:method} register_ports()
:canonical: duck.app.app.App.register_ports

```{autodocx-docstring} duck.app.app.App.register_ports
```

````

````{py:method} register_signals()
:canonical: duck.app.app.App.register_signals

```{autodocx-docstring} duck.app.app.App.register_signals
```

````

````{py:method} run(print_ansi_art: bool = True)
:canonical: duck.app.app.App.run

```{autodocx-docstring} duck.app.app.App.run
```

````

````{py:method} run_checks()
:canonical: duck.app.app.App.run_checks

```{autodocx-docstring} duck.app.app.App.run_checks
```

````

````{py:method} set_process_name()
:canonical: duck.app.app.App.set_process_name

```{autodocx-docstring} duck.app.app.App.set_process_name
```

````

````{py:method} start_automations_dispatcher(log_message: bool = True)
:canonical: duck.app.app.App.start_automations_dispatcher

```{autodocx-docstring} duck.app.app.App.start_automations_dispatcher
```

````

````{py:method} start_background_event_loop()
:canonical: duck.app.app.App.start_background_event_loop

```{autodocx-docstring} duck.app.app.App.start_background_event_loop
```

````

````{py:method} start_background_workers(application: duck.app.base.BaseApp, start_request_handling_threadpool_manager, start_request_handling_eventloop_manager, start_component_threadpool_manager: bool = True, start_automations_eventloop_manager: bool = False, recreate_managers: bool = False)
:canonical: duck.app.app.App.start_background_workers
:staticmethod:

```{autodocx-docstring} duck.app.app.App.start_background_workers
```

````

````{py:method} start_django_if_needed() -> bool
:canonical: duck.app.app.App.start_django_if_needed

```{autodocx-docstring} duck.app.app.App.start_django_if_needed
```

````

````{py:method} start_django_server() -> None
:canonical: duck.app.app.App.start_django_server

```{autodocx-docstring} duck.app.app.App.start_django_server
```

````

````{py:method} start_ducksight_reloader()
:canonical: duck.app.app.App.start_ducksight_reloader

```{autodocx-docstring} duck.app.app.App.start_ducksight_reloader
```

````

````{py:method} start_https_redirect_if_needed(start_failure_msg: str) -> bool
:canonical: duck.app.app.App.start_https_redirect_if_needed

```{autodocx-docstring} duck.app.app.App.start_https_redirect_if_needed
```

````

````{py:method} start_https_redirect_server(log_message: bool = True)
:canonical: duck.app.app.App.start_https_redirect_server

```{autodocx-docstring} duck.app.app.App.start_https_redirect_server
```

````

````{py:method} start_server() -> None
:canonical: duck.app.app.App.start_server

```{autodocx-docstring} duck.app.app.App.start_server
```

````

````{py:method} stop(log_to_console: bool = True, no_exit: bool = False, dispatch_pre_stop_event: bool = True, kill_ducksight_reloader: bool = True, wait_for_runtime_executor_shutdown: bool = True, close_log_file: bool = True)
:canonical: duck.app.app.App.stop

```{autodocx-docstring} duck.app.app.App.stop
```

````

````{py:method} stop_servers(stop_https_redirect_server: bool = True, log_to_console: bool = True, wait: bool = True)
:canonical: duck.app.app.App.stop_servers

```{autodocx-docstring} duck.app.app.App.stop_servers
```

````

````{py:method} wait_for_main_server(start_failure_msg: str) -> bool
:canonical: duck.app.app.App.wait_for_main_server

```{autodocx-docstring} duck.app.app.App.wait_for_main_server
```

````

`````
