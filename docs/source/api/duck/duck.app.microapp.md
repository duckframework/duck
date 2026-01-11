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

`````{py:class} HttpsRedirectMicroApp(location_root_url: str, *args, **kwargs)
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

`````{py:class} MicroApp(addr: str = 'localhost', port: int = 8080, parent_app: App = None, domain: str = None, uses_ipv6: bool = False, enable_https: bool = False, no_logs: bool = True, workers: typing.Optional[int] = None, force_worker_processes: bool = False)
:canonical: duck.app.microapp.MicroApp

```{autodocx-docstring} duck.app.microapp.MicroApp
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.app.microapp.MicroApp.__init__
```

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

````{py:property} absolute_uri
:canonical: duck.app.microapp.MicroApp.absolute_uri
:type: str

```{autodocx-docstring} duck.app.microapp.MicroApp.absolute_uri
```

````

````{py:method} async_view(request: duck.http.request.HttpRequest, processor: duck.http.core.processor.AsyncRequestProcessor) -> duck.http.response.HttpResponse
:canonical: duck.app.microapp.MicroApp.async_view
:abstractmethod:
:async:

```{autodocx-docstring} duck.app.microapp.MicroApp.async_view
```

````

````{py:method} build_absolute_uri(path: str) -> str
:canonical: duck.app.microapp.MicroApp.build_absolute_uri

```{autodocx-docstring} duck.app.microapp.MicroApp.build_absolute_uri
```

````

````{py:method} on_app_start()
:canonical: duck.app.microapp.MicroApp.on_app_start

```{autodocx-docstring} duck.app.microapp.MicroApp.on_app_start
```

````

````{py:method} run(run_forever: bool = True)
:canonical: duck.app.microapp.MicroApp.run

```{autodocx-docstring} duck.app.microapp.MicroApp.run
```

````

````{py:property} server_up
:canonical: duck.app.microapp.MicroApp.server_up
:type: bool

```{autodocx-docstring} duck.app.microapp.MicroApp.server_up
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
