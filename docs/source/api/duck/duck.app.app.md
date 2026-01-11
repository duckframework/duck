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

`````{py:class} App(addr: str = 'localhost', port: int = 8000, domain: str = None, uses_ipv6: bool = False, no_checks: bool = False, disable_signal_handler: bool = False, disable_ipc_handler: bool = False, skip_setup: bool = False, enable_force_https_logs: bool = False, start_bg_event_loop_if_wsgi: bool = True, process_name: str = 'duck-server', workers: typing.Optional[int] = None, force_https_workers: typing.Optional[int] = None, force_worker_processes: bool = False, force_https_force_worker_processes: bool = False)
:canonical: duck.app.app.App

```{autodocx-docstring} duck.app.app.App
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.app.app.App.__init__
```

````{py:attribute} DJANGO_ADDR
:canonical: duck.app.app.App.DJANGO_ADDR
:type: tuple[str, int]
:value: >
   None

```{autodocx-docstring} duck.app.app.App.DJANGO_ADDR
```

````

````{py:attribute} DJANGO_SERVER_WAIT_TIME
:canonical: duck.app.app.App.DJANGO_SERVER_WAIT_TIME
:type: int
:value: >
   None

```{autodocx-docstring} duck.app.app.App.DJANGO_SERVER_WAIT_TIME
```

````

````{py:attribute} DOMAIN
:canonical: duck.app.app.App.DOMAIN
:type: str
:value: >
   None

```{autodocx-docstring} duck.app.app.App.DOMAIN
```

````

````{py:attribute} __instances__
:canonical: duck.app.app.App.__instances__
:type: int
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

````{py:method} build_absolute_uri(path: str) -> str
:canonical: duck.app.app.App.build_absolute_uri

```{autodocx-docstring} duck.app.app.App.build_absolute_uri
```

````

````{py:method} build_absolute_ws_uri(path: str) -> str
:canonical: duck.app.app.App.build_absolute_ws_uri

```{autodocx-docstring} duck.app.app.App.build_absolute_ws_uri
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

````{py:property} force_https_server_up
:canonical: duck.app.app.App.force_https_server_up
:type: bool

```{autodocx-docstring} duck.app.app.App.force_https_server_up
```

````

````{py:method} get_main_app() -> duck.app.app.App
:canonical: duck.app.app.App.get_main_app
:classmethod:

```{autodocx-docstring} duck.app.app.App.get_main_app
```

````

````{py:method} get_threadpool_futures() -> typing.Dict[str, typing.Optional[concurrent.futures.Future]]
:canonical: duck.app.app.App.get_threadpool_futures

```{autodocx-docstring} duck.app.app.App.get_threadpool_futures
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

````{py:method} instances() -> int
:canonical: duck.app.app.App.instances
:classmethod:

```{autodocx-docstring} duck.app.app.App.instances
```

````

````{py:property} meta
:canonical: duck.app.app.App.meta
:type: typing.Dict[str, typing.Any]

```{autodocx-docstring} duck.app.app.App.meta
```

````

````{py:method} on_app_start()
:canonical: duck.app.app.App.on_app_start

```{autodocx-docstring} duck.app.app.App.on_app_start
```

````

````{py:method} on_pre_stop()
:canonical: duck.app.app.App.on_pre_stop

```{autodocx-docstring} duck.app.app.App.on_pre_stop
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

````{py:property} running
:canonical: duck.app.app.App.running
:type: bool

```{autodocx-docstring} duck.app.app.App.running
```

````

````{py:property} server_up
:canonical: duck.app.app.App.server_up
:type: bool

```{autodocx-docstring} duck.app.app.App.server_up
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

````{py:method} start_background_workers(application: typing.Union[duck.app.app.App, MicroApp], start_threadpool: bool = True, start_asyncio_event_loop: bool = True, recreate_managers: bool = False, start_automations_event_loop: bool = False, start_component_bg_threadpool: bool = False)
:canonical: duck.app.app.App.start_background_workers
:staticmethod:

```{autodocx-docstring} duck.app.app.App.start_background_workers
```

````

````{py:method} start_django_server()
:canonical: duck.app.app.App.start_django_server

```{autodocx-docstring} duck.app.app.App.start_django_server
```

````

````{py:method} start_ducksight_reloader()
:canonical: duck.app.app.App.start_ducksight_reloader

```{autodocx-docstring} duck.app.app.App.start_ducksight_reloader
```

````

````{py:method} start_force_https_server(log_message: bool = True)
:canonical: duck.app.app.App.start_force_https_server

```{autodocx-docstring} duck.app.app.App.start_force_https_server
```

````

````{py:method} start_server()
:canonical: duck.app.app.App.start_server

```{autodocx-docstring} duck.app.app.App.start_server
```

````

````{py:method} stop(log_to_console: bool = True, no_exit: bool = False, call_on_pre_stop_handler: bool = True, kill_ducksight_reloader: bool = True, wait_for_thread_pool_executor_shutdown: bool = True, close_log_file: bool = True)
:canonical: duck.app.app.App.stop

```{autodocx-docstring} duck.app.app.App.stop
```

````

````{py:method} stop_servers(stop_force_https_server: bool = True, log_to_console: bool = True, wait: bool = True)
:canonical: duck.app.app.App.stop_servers

```{autodocx-docstring} duck.app.app.App.stop_servers
```

````

`````
