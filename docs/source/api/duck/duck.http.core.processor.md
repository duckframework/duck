# {py:mod}`duck.http.core.processor`

```{py:module} duck.http.core.processor
```

```{autodocx-docstring} duck.http.core.processor
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`AsyncRequestProcessor <duck.http.core.processor.AsyncRequestProcessor>`
  - ```{autodocx-docstring} duck.http.core.processor.AsyncRequestProcessor
    :summary:
    ```
* - {py:obj}`RequestProcessor <duck.http.core.processor.RequestProcessor>`
  - ```{autodocx-docstring} duck.http.core.processor.RequestProcessor
    :summary:
    ```
````

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`is_django_side_url <duck.http.core.processor.is_django_side_url>`
  - ```{autodocx-docstring} duck.http.core.processor.is_django_side_url
    :summary:
    ```
* - {py:obj}`is_duck_explicit_url <duck.http.core.processor.is_duck_explicit_url>`
  - ```{autodocx-docstring} duck.http.core.processor.is_duck_explicit_url
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`DJANGO_SIDE_PATTERNS <duck.http.core.processor.DJANGO_SIDE_PATTERNS>`
  - ```{autodocx-docstring} duck.http.core.processor.DJANGO_SIDE_PATTERNS
    :summary:
    ```
* - {py:obj}`DUCK_EXPLICIT_PATTERNS <duck.http.core.processor.DUCK_EXPLICIT_PATTERNS>`
  - ```{autodocx-docstring} duck.http.core.processor.DUCK_EXPLICIT_PATTERNS
    :summary:
    ```
````

### API

`````{py:class} AsyncRequestProcessor(request: duck.http.request.HttpRequest)
:canonical: duck.http.core.processor.AsyncRequestProcessor

Bases: {py:obj}`duck.http.core.processor.RequestProcessor`

```{autodocx-docstring} duck.http.core.processor.AsyncRequestProcessor
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.http.core.processor.AsyncRequestProcessor.__init__
```

````{py:method} check_middlewares() -> tuple[str, typing.Optional[duck.http.middlewares.BaseMiddleware]]
:canonical: duck.http.core.processor.AsyncRequestProcessor.check_middlewares
:async:

```{autodocx-docstring} duck.http.core.processor.AsyncRequestProcessor.check_middlewares
```

````

````{py:method} get_django_response() -> duck.http.core.proxyhandler.HttpProxyResponse
:canonical: duck.http.core.processor.AsyncRequestProcessor.get_django_response
:async:

```{autodocx-docstring} duck.http.core.processor.AsyncRequestProcessor.get_django_response
```

````

````{py:method} get_middleware_error_response(middleware) -> duck.http.response.HttpResponse
:canonical: duck.http.core.processor.AsyncRequestProcessor.get_middleware_error_response
:async:

```{autodocx-docstring} duck.http.core.processor.AsyncRequestProcessor.get_middleware_error_response
```

````

````{py:method} get_response(request: duck.http.request.HttpRequest) -> duck.http.response.HttpResponse
:canonical: duck.http.core.processor.AsyncRequestProcessor.get_response
:async:

```{autodocx-docstring} duck.http.core.processor.AsyncRequestProcessor.get_response
```

````

````{py:method} get_view_response() -> duck.http.response.HttpResponse
:canonical: duck.http.core.processor.AsyncRequestProcessor.get_view_response
:async:

```{autodocx-docstring} duck.http.core.processor.AsyncRequestProcessor.get_view_response
```

````

````{py:method} process_django_request() -> typing.Union[duck.http.response.HttpResponse, duck.http.core.proxyhandler.HttpProxyResponse]
:canonical: duck.http.core.processor.AsyncRequestProcessor.process_django_request
:async:

```{autodocx-docstring} duck.http.core.processor.AsyncRequestProcessor.process_django_request
```

````

````{py:method} process_request() -> duck.http.response.HttpResponse
:canonical: duck.http.core.processor.AsyncRequestProcessor.process_request
:async:

```{autodocx-docstring} duck.http.core.processor.AsyncRequestProcessor.process_request
```

````

`````

````{py:data} DJANGO_SIDE_PATTERNS
:canonical: duck.http.core.processor.DJANGO_SIDE_PATTERNS
:value: >
   None

```{autodocx-docstring} duck.http.core.processor.DJANGO_SIDE_PATTERNS
```

````

````{py:data} DUCK_EXPLICIT_PATTERNS
:canonical: duck.http.core.processor.DUCK_EXPLICIT_PATTERNS
:value: >
   None

```{autodocx-docstring} duck.http.core.processor.DUCK_EXPLICIT_PATTERNS
```

````

`````{py:class} RequestProcessor(request: duck.http.request.HttpRequest)
:canonical: duck.http.core.processor.RequestProcessor

```{autodocx-docstring} duck.http.core.processor.RequestProcessor
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.http.core.processor.RequestProcessor.__init__
```

````{py:attribute} __slots__
:canonical: duck.http.core.processor.RequestProcessor.__slots__
:value: >
   ('request', '_route_info')

```{autodocx-docstring} duck.http.core.processor.RequestProcessor.__slots__
```

````

````{py:method} check_base_errors()
:canonical: duck.http.core.processor.RequestProcessor.check_base_errors

```{autodocx-docstring} duck.http.core.processor.RequestProcessor.check_base_errors
```

````

````{py:method} check_errors()
:canonical: duck.http.core.processor.RequestProcessor.check_errors

```{autodocx-docstring} duck.http.core.processor.RequestProcessor.check_errors
```

````

````{py:method} check_middlewares() -> tuple[str, typing.Optional[duck.http.middlewares.BaseMiddleware]]
:canonical: duck.http.core.processor.RequestProcessor.check_middlewares

```{autodocx-docstring} duck.http.core.processor.RequestProcessor.check_middlewares
```

````

````{py:method} get_django_response() -> duck.http.core.proxyhandler.HttpProxyResponse
:canonical: duck.http.core.processor.RequestProcessor.get_django_response

```{autodocx-docstring} duck.http.core.processor.RequestProcessor.get_django_response
```

````

````{py:method} get_middleware_error_response(middleware) -> duck.http.response.HttpResponse
:canonical: duck.http.core.processor.RequestProcessor.get_middleware_error_response

```{autodocx-docstring} duck.http.core.processor.RequestProcessor.get_middleware_error_response
```

````

````{py:method} get_response(request: duck.http.request.HttpRequest) -> duck.http.response.HttpResponse
:canonical: duck.http.core.processor.RequestProcessor.get_response

```{autodocx-docstring} duck.http.core.processor.RequestProcessor.get_response
```

````

````{py:method} get_view_response() -> duck.http.response.HttpResponse
:canonical: duck.http.core.processor.RequestProcessor.get_view_response

```{autodocx-docstring} duck.http.core.processor.RequestProcessor.get_view_response
```

````

````{py:method} normalize_request()
:canonical: duck.http.core.processor.RequestProcessor.normalize_request

```{autodocx-docstring} duck.http.core.processor.RequestProcessor.normalize_request
```

````

````{py:method} process_django_request() -> typing.Union[duck.http.response.HttpResponse, duck.http.core.proxyhandler.HttpProxyResponse]
:canonical: duck.http.core.processor.RequestProcessor.process_django_request

```{autodocx-docstring} duck.http.core.processor.RequestProcessor.process_django_request
```

````

````{py:method} process_request() -> duck.http.response.HttpResponse
:canonical: duck.http.core.processor.RequestProcessor.process_request

```{autodocx-docstring} duck.http.core.processor.RequestProcessor.process_request
```

````

````{py:property} route_info
:canonical: duck.http.core.processor.RequestProcessor.route_info
:type: typing.Dict[str, typing.Any]

```{autodocx-docstring} duck.http.core.processor.RequestProcessor.route_info
```

````

`````

````{py:function} is_django_side_url(url: str) -> typing.Optional[re.Pattern]
:canonical: duck.http.core.processor.is_django_side_url

```{autodocx-docstring} duck.http.core.processor.is_django_side_url
```
````

````{py:function} is_duck_explicit_url(url: str) -> typing.Optional[re.Pattern]
:canonical: duck.http.core.processor.is_duck_explicit_url

```{autodocx-docstring} duck.http.core.processor.is_duck_explicit_url
```
````
