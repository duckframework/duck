# {py:mod}`duck.http.middlewares.contrib.jwt`

```{py:module} duck.http.middlewares.contrib.jwt
```

```{autodocx-docstring} duck.http.middlewares.contrib.jwt
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`JWTMiddleware <duck.http.middlewares.contrib.jwt.JWTMiddleware>`
  - ```{autodocx-docstring} duck.http.middlewares.contrib.jwt.JWTMiddleware
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`TRANSPORT_COOKIE <duck.http.middlewares.contrib.jwt.TRANSPORT_COOKIE>`
  - ```{autodocx-docstring} duck.http.middlewares.contrib.jwt.TRANSPORT_COOKIE
    :summary:
    ```
* - {py:obj}`TRANSPORT_HEADER <duck.http.middlewares.contrib.jwt.TRANSPORT_HEADER>`
  - ```{autodocx-docstring} duck.http.middlewares.contrib.jwt.TRANSPORT_HEADER
    :summary:
    ```
* - {py:obj}`VALID_TRANSPORTS <duck.http.middlewares.contrib.jwt.VALID_TRANSPORTS>`
  - ```{autodocx-docstring} duck.http.middlewares.contrib.jwt.VALID_TRANSPORTS
    :summary:
    ```
````

### API

`````{py:class} JWTMiddleware
:canonical: duck.http.middlewares.contrib.jwt.JWTMiddleware

Bases: {py:obj}`duck.http.middlewares.BaseMiddleware`

```{autodocx-docstring} duck.http.middlewares.contrib.jwt.JWTMiddleware
```

````{py:attribute} debug_message
:canonical: duck.http.middlewares.contrib.jwt.JWTMiddleware.debug_message
:type: str
:value: >
   'JWTMiddleware: JWT Error'

```{autodocx-docstring} duck.http.middlewares.contrib.jwt.JWTMiddleware.debug_message
```

````

````{py:method} get_raw_token_from_request(request: duck.http.request.HttpRequest, token_type: str = 'access') -> typing.Optional[str]
:canonical: duck.http.middlewares.contrib.jwt.JWTMiddleware.get_raw_token_from_request
:classmethod:

```{autodocx-docstring} duck.http.middlewares.contrib.jwt.JWTMiddleware.get_raw_token_from_request
```

````

````{py:method} process_request(request: duck.http.request.HttpRequest) -> int
:canonical: duck.http.middlewares.contrib.jwt.JWTMiddleware.process_request
:classmethod:

```{autodocx-docstring} duck.http.middlewares.contrib.jwt.JWTMiddleware.process_request
```

````

````{py:method} process_response(response, request: duck.http.request.HttpRequest)
:canonical: duck.http.middlewares.contrib.jwt.JWTMiddleware.process_response
:classmethod:

```{autodocx-docstring} duck.http.middlewares.contrib.jwt.JWTMiddleware.process_response
```

````

````{py:method} resolve_transport() -> str
:canonical: duck.http.middlewares.contrib.jwt.JWTMiddleware.resolve_transport
:classmethod:

```{autodocx-docstring} duck.http.middlewares.contrib.jwt.JWTMiddleware.resolve_transport
```

````

````{py:method} write_cookie(response: duck.http.response.HttpResponse, request: duck.http.request.HttpRequest, token: str, token_type: str = 'access')
:canonical: duck.http.middlewares.contrib.jwt.JWTMiddleware.write_cookie
:classmethod:

```{autodocx-docstring} duck.http.middlewares.contrib.jwt.JWTMiddleware.write_cookie
```

````

`````

````{py:data} TRANSPORT_COOKIE
:canonical: duck.http.middlewares.contrib.jwt.TRANSPORT_COOKIE
:value: >
   'cookie'

```{autodocx-docstring} duck.http.middlewares.contrib.jwt.TRANSPORT_COOKIE
```

````

````{py:data} TRANSPORT_HEADER
:canonical: duck.http.middlewares.contrib.jwt.TRANSPORT_HEADER
:value: >
   'header'

```{autodocx-docstring} duck.http.middlewares.contrib.jwt.TRANSPORT_HEADER
```

````

````{py:data} VALID_TRANSPORTS
:canonical: duck.http.middlewares.contrib.jwt.VALID_TRANSPORTS
:value: >
   ()

```{autodocx-docstring} duck.http.middlewares.contrib.jwt.VALID_TRANSPORTS
```

````
