# {py:mod}`duck.http.middlewares`

```{py:module} duck.http.middlewares
```

```{autodocx-docstring} duck.http.middlewares
:allowtitles:
```

## Subpackages

```{toctree}
:titlesonly:
:maxdepth: 3

duck.http.middlewares.contrib
duck.http.middlewares.security
```

## Package Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`BaseMiddleware <duck.http.middlewares.BaseMiddleware>`
  - ```{autodocx-docstring} duck.http.middlewares.BaseMiddleware
    :summary:
    ```
````

### API

`````{py:class} BaseMiddleware
:canonical: duck.http.middlewares.BaseMiddleware

```{autodocx-docstring} duck.http.middlewares.BaseMiddleware
```

````{py:method} __getattr__(key)
:canonical: duck.http.middlewares.BaseMiddleware.__getattr__
:classmethod:

```{autodocx-docstring} duck.http.middlewares.BaseMiddleware.__getattr__
```

````

````{py:method} __setattr__(key, value)
:canonical: duck.http.middlewares.BaseMiddleware.__setattr__
:classmethod:

````

````{py:attribute} _class_attrs
:canonical: duck.http.middlewares.BaseMiddleware._class_attrs
:value: >
   None

```{autodocx-docstring} duck.http.middlewares.BaseMiddleware._class_attrs
```

````

````{py:attribute} debug_message
:canonical: duck.http.middlewares.BaseMiddleware.debug_message
:type: str
:value: >
   'Middleware error'

```{autodocx-docstring} duck.http.middlewares.BaseMiddleware.debug_message
```

````

````{py:method} get_error_response(request)
:canonical: duck.http.middlewares.BaseMiddleware.get_error_response
:classmethod:

```{autodocx-docstring} duck.http.middlewares.BaseMiddleware.get_error_response
```

````

````{py:method} process_request(request: duck.http.request.HttpRequest) -> int
:canonical: duck.http.middlewares.BaseMiddleware.process_request
:abstractmethod:
:classmethod:

```{autodocx-docstring} duck.http.middlewares.BaseMiddleware.process_request
```

````

````{py:method} process_response(response: duck.http.response.HttpResponse, request: duck.http.request.HttpRequest) -> None
:canonical: duck.http.middlewares.BaseMiddleware.process_response
:classmethod:

```{autodocx-docstring} duck.http.middlewares.BaseMiddleware.process_response
```

````

````{py:attribute} request_bad
:canonical: duck.http.middlewares.BaseMiddleware.request_bad
:type: int
:value: >
   0

```{autodocx-docstring} duck.http.middlewares.BaseMiddleware.request_bad
```

````

````{py:attribute} request_ok
:canonical: duck.http.middlewares.BaseMiddleware.request_ok
:type: int
:value: >
   1

```{autodocx-docstring} duck.http.middlewares.BaseMiddleware.request_ok
```

````

`````
