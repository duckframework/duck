# {py:mod}`duck.app.microapp`

```{py:module} duck.app.microapp
```

```{autodocx-docstring} duck.app.microapp
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`HttpsRedirectMicroApp <duck.app.microapp.HttpsRedirectMicroApp>`
  - ```{autodocx-docstring} duck.app.microapp.HttpsRedirectMicroApp
    :summary:
    ```
* - {py:obj}`MicroApp <duck.app.microapp.MicroApp>`
  - ```{autodocx-docstring} duck.app.microapp.MicroApp
    :summary:
    ```
````

### API

`````{py:class} HttpsRedirectMicroApp(name: typing.Optional[str] = None, addr: str = DEFAULT_ADDR, port: int = DEFAULT_PORT, domain: typing.Optional[str] = None, server_url: typing.Optional[str] = None, uses_ipv6: bool = False, enable_https: bool = False, no_checks: bool = False, no_logs: bool = True, workers: typing.Optional[int] = None, force_worker_processes: bool = False, events: typing.Optional[typing.Dict[str, typing.Optional[typing.Callable]]] = None)
:canonical: duck.app.microapp.HttpsRedirectMicroApp

Bases: {py:obj}`duck.app.microapp.MicroApp`

```{autodocx-docstring} duck.app.microapp.HttpsRedirectMicroApp
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.app.microapp.HttpsRedirectMicroApp.__init__
```

````{py:method} async_view(request: duck.http.request.HttpRequest, request_processor: duck.http.core.processor.AsyncRequestProcessor) -> duck.http.response.HttpResponse
:canonical: duck.app.microapp.HttpsRedirectMicroApp.async_view
:async:

```{autodocx-docstring} duck.app.microapp.HttpsRedirectMicroApp.async_view
```

````

````{py:method} view(request: duck.http.request.HttpRequest, request_processor: duck.http.core.processor.RequestProcessor) -> duck.http.response.HttpResponse
:canonical: duck.app.microapp.HttpsRedirectMicroApp.view

```{autodocx-docstring} duck.app.microapp.HttpsRedirectMicroApp.view
```

````

`````

`````{py:class} MicroApp(name: typing.Optional[str] = None, addr: str = DEFAULT_ADDR, port: int = DEFAULT_PORT, domain: typing.Optional[str] = None, server_url: typing.Optional[str] = None, uses_ipv6: bool = False, enable_https: bool = False, no_checks: bool = False, no_logs: bool = True, workers: typing.Optional[int] = None, force_worker_processes: bool = False, events: typing.Optional[typing.Dict[str, typing.Optional[typing.Callable]]] = None)
:canonical: duck.app.microapp.MicroApp

Bases: {py:obj}`duck.app.base.BaseApp`

```{autodocx-docstring} duck.app.microapp.MicroApp
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.app.microapp.MicroApp.__init__
```

````{py:attribute} DEFAULT_ADDR
:canonical: duck.app.microapp.MicroApp.DEFAULT_ADDR
:value: >
   'localhost'

```{autodocx-docstring} duck.app.microapp.MicroApp.DEFAULT_ADDR
```

````

````{py:attribute} DEFAULT_PORT
:canonical: duck.app.microapp.MicroApp.DEFAULT_PORT
:value: >
   8000

```{autodocx-docstring} duck.app.microapp.MicroApp.DEFAULT_PORT
```

````

````{py:method} _async_view(request: duck.http.request.HttpRequest, processor: duck.http.core.processor.AsyncRequestProcessor) -> duck.http.response.HttpResponse
:canonical: duck.app.microapp.MicroApp._async_view
:async:

```{autodocx-docstring} duck.app.microapp.MicroApp._async_view
```

````

````{py:method} _view(request: duck.http.request.HttpRequest, processor: duck.http.core.processor.RequestProcessor) -> duck.http.response.HttpResponse
:canonical: duck.app.microapp.MicroApp._view

```{autodocx-docstring} duck.app.microapp.MicroApp._view
```

````

````{py:method} async_view(request: duck.http.request.HttpRequest, processor: duck.http.core.processor.AsyncRequestProcessor) -> duck.http.response.HttpResponse
:canonical: duck.app.microapp.MicroApp.async_view
:abstractmethod:
:async:

```{autodocx-docstring} duck.app.microapp.MicroApp.async_view
```

````

````{py:method} run(run_forever: bool = True)
:canonical: duck.app.microapp.MicroApp.run

```{autodocx-docstring} duck.app.microapp.MicroApp.run
```

````

````{py:method} start_server()
:canonical: duck.app.microapp.MicroApp.start_server

```{autodocx-docstring} duck.app.microapp.MicroApp.start_server
```

````

````{py:method} stop()
:canonical: duck.app.microapp.MicroApp.stop

```{autodocx-docstring} duck.app.microapp.MicroApp.stop
```

````

````{py:method} view(request: duck.http.request.HttpRequest, processor: typing.Union[duck.http.core.processor.AsyncRequestProcessor, duck.http.core.processor.RequestProcessor]) -> duck.http.response.HttpResponse
:canonical: duck.app.microapp.MicroApp.view
:abstractmethod:

```{autodocx-docstring} duck.app.microapp.MicroApp.view
```

````

`````
