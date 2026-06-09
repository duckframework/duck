# {py:mod}`duck.app.base`

```{py:module} duck.app.base
```

```{autodocx-docstring} duck.app.base
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`BaseApp <duck.app.base.BaseApp>`
  - ```{autodocx-docstring} duck.app.base.BaseApp
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`APPS_REGISTRY <duck.app.base.APPS_REGISTRY>`
  - ```{autodocx-docstring} duck.app.base.APPS_REGISTRY
    :summary:
    ```
````

### API

````{py:data} APPS_REGISTRY
:canonical: duck.app.base.APPS_REGISTRY
:type: typing.Dict[str, duck.app.base.BaseApp]
:value: >
   None

```{autodocx-docstring} duck.app.base.APPS_REGISTRY
```

````

`````{py:class} BaseApp(name: typing.Optional[str] = None, addr: str = DEFAULT_ADDR, port: int = DEFAULT_PORT, domain: typing.Optional[str] = None, server_url: typing.Optional[str] = None, uses_ipv6: bool = False, enable_https: bool = False, no_checks: bool = False, workers: typing.Optional[int] = None, force_worker_processes: bool = False, events: typing.Optional[typing.Dict[str, typing.Optional[typing.Callable]]] = None)
:canonical: duck.app.base.BaseApp

```{autodocx-docstring} duck.app.base.BaseApp
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.app.base.BaseApp.__init__
```

````{py:attribute} DEFAULT_ADDR
:canonical: duck.app.base.BaseApp.DEFAULT_ADDR
:value: >
   'localhost'

```{autodocx-docstring} duck.app.base.BaseApp.DEFAULT_ADDR
```

````

````{py:attribute} DEFAULT_PORT
:canonical: duck.app.base.BaseApp.DEFAULT_PORT
:value: >
   8000

```{autodocx-docstring} duck.app.base.BaseApp.DEFAULT_PORT
```

````

````{py:method} _on_app_start()
:canonical: duck.app.base.BaseApp._on_app_start

```{autodocx-docstring} duck.app.base.BaseApp._on_app_start
```

````

````{py:property} absolute_uri
:canonical: duck.app.base.BaseApp.absolute_uri
:type: str

```{autodocx-docstring} duck.app.base.BaseApp.absolute_uri
```

````

````{py:property} absolute_ws_uri
:canonical: duck.app.base.BaseApp.absolute_ws_uri
:type: str

```{autodocx-docstring} duck.app.base.BaseApp.absolute_ws_uri
```

````

````{py:method} build_absolute_uri(path: str = '') -> str
:canonical: duck.app.base.BaseApp.build_absolute_uri

```{autodocx-docstring} duck.app.base.BaseApp.build_absolute_uri
```

````

````{py:method} build_absolute_ws_uri(path: str = '') -> str
:canonical: duck.app.base.BaseApp.build_absolute_ws_uri

```{autodocx-docstring} duck.app.base.BaseApp.build_absolute_ws_uri
```

````

````{py:method} dispatch_event(event: str)
:canonical: duck.app.base.BaseApp.dispatch_event

```{autodocx-docstring} duck.app.base.BaseApp.dispatch_event
```

````

````{py:method} get_all_apps() -> typing.Dict[str, duck.app.base.BaseApp]
:canonical: duck.app.base.BaseApp.get_all_apps
:classmethod:

```{autodocx-docstring} duck.app.base.BaseApp.get_all_apps
```

````

````{py:method} get_app_by_name()
:canonical: duck.app.base.BaseApp.get_app_by_name
:classmethod:

```{autodocx-docstring} duck.app.base.BaseApp.get_app_by_name
```

````

````{py:method} register_app(name: str, app: duck.app.base.BaseApp)
:canonical: duck.app.base.BaseApp.register_app
:classmethod:

```{autodocx-docstring} duck.app.base.BaseApp.register_app
```

````

````{py:method} register_event(event: str, handler: typing.Optional[typing.Callable] = None)
:canonical: duck.app.base.BaseApp.register_event

```{autodocx-docstring} duck.app.base.BaseApp.register_event
```

````

````{py:method} register_ports() -> None
:canonical: duck.app.base.BaseApp.register_ports

```{autodocx-docstring} duck.app.base.BaseApp.register_ports
```

````

````{py:method} resolve_domain(addr: str, domain: typing.Optional[str] = None, uses_ipv6: bool = False) -> str
:canonical: duck.app.base.BaseApp.resolve_domain
:staticmethod:

```{autodocx-docstring} duck.app.base.BaseApp.resolve_domain
```

````

````{py:method} resolve_name(name: typing.Optional[str] = None) -> str
:canonical: duck.app.base.BaseApp.resolve_name

```{autodocx-docstring} duck.app.base.BaseApp.resolve_name
```

````

````{py:method} resolve_server_url(server_url: typing.Optional[str] = None) -> str
:canonical: duck.app.base.BaseApp.resolve_server_url

```{autodocx-docstring} duck.app.base.BaseApp.resolve_server_url
```

````

````{py:method} run()
:canonical: duck.app.base.BaseApp.run
:abstractmethod:

```{autodocx-docstring} duck.app.base.BaseApp.run
```

````

````{py:method} run_checks()
:canonical: duck.app.base.BaseApp.run_checks

```{autodocx-docstring} duck.app.base.BaseApp.run_checks
```

````

````{py:property} running
:canonical: duck.app.base.BaseApp.running
:type: bool

```{autodocx-docstring} duck.app.base.BaseApp.running
```

````

````{py:property} server_up
:canonical: duck.app.base.BaseApp.server_up
:type: bool

```{autodocx-docstring} duck.app.base.BaseApp.server_up
```

````

````{py:method} stop()
:canonical: duck.app.base.BaseApp.stop
:abstractmethod:

```{autodocx-docstring} duck.app.base.BaseApp.stop
```

````

````{py:method} validate_addr(addr: str, uses_ipv6: bool = False) -> None
:canonical: duck.app.base.BaseApp.validate_addr
:staticmethod:

```{autodocx-docstring} duck.app.base.BaseApp.validate_addr
```

````

`````
