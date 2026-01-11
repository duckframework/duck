# {py:mod}`duck.http.middlewares.security.requestslimit`

```{py:module} duck.http.middlewares.security.requestslimit
```

```{autodocx-docstring} duck.http.middlewares.security.requestslimit
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`RequestsLimitMiddleware <duck.http.middlewares.security.requestslimit.RequestsLimitMiddleware>`
  - ```{autodocx-docstring} duck.http.middlewares.security.requestslimit.RequestsLimitMiddleware
    :summary:
    ```
````

### API

`````{py:class} RequestsLimitMiddleware
:canonical: duck.http.middlewares.security.requestslimit.RequestsLimitMiddleware

Bases: {py:obj}`duck.http.middlewares.BaseMiddleware`

```{autodocx-docstring} duck.http.middlewares.security.requestslimit.RequestsLimitMiddleware
```

````{py:attribute} _clients
:canonical: duck.http.middlewares.security.requestslimit.RequestsLimitMiddleware._clients
:value: >
   'InMemoryCache(...)'

```{autodocx-docstring} duck.http.middlewares.security.requestslimit.RequestsLimitMiddleware._clients
```

````

````{py:method} _process_request(request)
:canonical: duck.http.middlewares.security.requestslimit.RequestsLimitMiddleware._process_request
:classmethod:

```{autodocx-docstring} duck.http.middlewares.security.requestslimit.RequestsLimitMiddleware._process_request
```

````

````{py:attribute} debug_message
:canonical: duck.http.middlewares.security.requestslimit.RequestsLimitMiddleware.debug_message
:type: str
:value: >
   'RequestsLimitMiddleware: Too many requests'

```{autodocx-docstring} duck.http.middlewares.security.requestslimit.RequestsLimitMiddleware.debug_message
```

````

````{py:method} get_error_response(request)
:canonical: duck.http.middlewares.security.requestslimit.RequestsLimitMiddleware.get_error_response
:classmethod:

```{autodocx-docstring} duck.http.middlewares.security.requestslimit.RequestsLimitMiddleware.get_error_response
```

````

````{py:method} get_readable_limit() -> str
:canonical: duck.http.middlewares.security.requestslimit.RequestsLimitMiddleware.get_readable_limit
:classmethod:

```{autodocx-docstring} duck.http.middlewares.security.requestslimit.RequestsLimitMiddleware.get_readable_limit
```

````

````{py:attribute} max_requests
:canonical: duck.http.middlewares.security.requestslimit.RequestsLimitMiddleware.max_requests
:type: int
:value: >
   200

```{autodocx-docstring} duck.http.middlewares.security.requestslimit.RequestsLimitMiddleware.max_requests
```

````

````{py:method} process_request(request)
:canonical: duck.http.middlewares.security.requestslimit.RequestsLimitMiddleware.process_request
:classmethod:

```{autodocx-docstring} duck.http.middlewares.security.requestslimit.RequestsLimitMiddleware.process_request
```

````

````{py:attribute} requests_delay
:canonical: duck.http.middlewares.security.requestslimit.RequestsLimitMiddleware.requests_delay
:type: float
:value: >
   60

```{autodocx-docstring} duck.http.middlewares.security.requestslimit.RequestsLimitMiddleware.requests_delay
```

````

`````
