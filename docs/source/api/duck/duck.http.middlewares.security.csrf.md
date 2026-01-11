# {py:mod}`duck.http.middlewares.security.csrf`

```{py:module} duck.http.middlewares.security.csrf
```

```{autodocx-docstring} duck.http.middlewares.security.csrf
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`CSRFMiddleware <duck.http.middlewares.security.csrf.CSRFMiddleware>`
  - ```{autodocx-docstring} duck.http.middlewares.security.csrf.CSRFMiddleware
    :summary:
    ```
````

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`add_new_csrf_cookie <duck.http.middlewares.security.csrf.add_new_csrf_cookie>`
  - ```{autodocx-docstring} duck.http.middlewares.security.csrf.add_new_csrf_cookie
    :summary:
    ```
* - {py:obj}`generate_csrf_secret <duck.http.middlewares.security.csrf.generate_csrf_secret>`
  - ```{autodocx-docstring} duck.http.middlewares.security.csrf.generate_csrf_secret
    :summary:
    ```
* - {py:obj}`generate_dynamic_secret_key <duck.http.middlewares.security.csrf.generate_dynamic_secret_key>`
  - ```{autodocx-docstring} duck.http.middlewares.security.csrf.generate_dynamic_secret_key
    :summary:
    ```
* - {py:obj}`get_csrf_token <duck.http.middlewares.security.csrf.get_csrf_token>`
  - ```{autodocx-docstring} duck.http.middlewares.security.csrf.get_csrf_token
    :summary:
    ```
* - {py:obj}`mask_cipher_secret <duck.http.middlewares.security.csrf.mask_cipher_secret>`
  - ```{autodocx-docstring} duck.http.middlewares.security.csrf.mask_cipher_secret
    :summary:
    ```
* - {py:obj}`unmask_cipher_token <duck.http.middlewares.security.csrf.unmask_cipher_token>`
  - ```{autodocx-docstring} duck.http.middlewares.security.csrf.unmask_cipher_token
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`ALLOWED_CHARACTERS <duck.http.middlewares.security.csrf.ALLOWED_CHARACTERS>`
  - ```{autodocx-docstring} duck.http.middlewares.security.csrf.ALLOWED_CHARACTERS
    :summary:
    ```
* - {py:obj}`CSRF_SECRET_LENGTH <duck.http.middlewares.security.csrf.CSRF_SECRET_LENGTH>`
  - ```{autodocx-docstring} duck.http.middlewares.security.csrf.CSRF_SECRET_LENGTH
    :summary:
    ```
* - {py:obj}`CSRF_SESSION_KEY <duck.http.middlewares.security.csrf.CSRF_SESSION_KEY>`
  - ```{autodocx-docstring} duck.http.middlewares.security.csrf.CSRF_SESSION_KEY
    :summary:
    ```
* - {py:obj}`CSRF_TOKEN_LENGTH <duck.http.middlewares.security.csrf.CSRF_TOKEN_LENGTH>`
  - ```{autodocx-docstring} duck.http.middlewares.security.csrf.CSRF_TOKEN_LENGTH
    :summary:
    ```
* - {py:obj}`CSRF_USE_SESSIONS <duck.http.middlewares.security.csrf.CSRF_USE_SESSIONS>`
  - ```{autodocx-docstring} duck.http.middlewares.security.csrf.CSRF_USE_SESSIONS
    :summary:
    ```
````

### API

````{py:data} ALLOWED_CHARACTERS
:canonical: duck.http.middlewares.security.csrf.ALLOWED_CHARACTERS
:value: >
   None

```{autodocx-docstring} duck.http.middlewares.security.csrf.ALLOWED_CHARACTERS
```

````

````{py:exception} CSRFCookieError()
:canonical: duck.http.middlewares.security.csrf.CSRFCookieError

Bases: {py:obj}`Exception`

```{autodocx-docstring} duck.http.middlewares.security.csrf.CSRFCookieError
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.http.middlewares.security.csrf.CSRFCookieError.__init__
```

````

`````{py:class} CSRFMiddleware
:canonical: duck.http.middlewares.security.csrf.CSRFMiddleware

Bases: {py:obj}`duck.http.middlewares.BaseMiddleware`

```{autodocx-docstring} duck.http.middlewares.security.csrf.CSRFMiddleware
```

````{py:method} _check_origin_ok(request)
:canonical: duck.http.middlewares.security.csrf.CSRFMiddleware._check_origin_ok
:classmethod:

```{autodocx-docstring} duck.http.middlewares.security.csrf.CSRFMiddleware._check_origin_ok
```

````

````{py:method} _check_referer_ok(request)
:canonical: duck.http.middlewares.security.csrf.CSRFMiddleware._check_referer_ok
:classmethod:

```{autodocx-docstring} duck.http.middlewares.security.csrf.CSRFMiddleware._check_referer_ok
```

````

````{py:method} check_csrf_cookie(request)
:canonical: duck.http.middlewares.security.csrf.CSRFMiddleware.check_csrf_cookie
:classmethod:

```{autodocx-docstring} duck.http.middlewares.security.csrf.CSRFMiddleware.check_csrf_cookie
```

````

````{py:attribute} debug_message
:canonical: duck.http.middlewares.security.csrf.CSRFMiddleware.debug_message
:type: str
:value: >
   'CSRFMiddleware: CSRF token missing or invalid'

```{autodocx-docstring} duck.http.middlewares.security.csrf.CSRFMiddleware.debug_message
```

````

````{py:method} get_error_response(request)
:canonical: duck.http.middlewares.security.csrf.CSRFMiddleware.get_error_response
:classmethod:

````

````{py:method} process_request(request: duck.http.request.HttpRequest)
:canonical: duck.http.middlewares.security.csrf.CSRFMiddleware.process_request
:classmethod:

````

````{py:method} process_response(response, request)
:canonical: duck.http.middlewares.security.csrf.CSRFMiddleware.process_response
:classmethod:

````

````{py:method} rotate_csrf_token()
:canonical: duck.http.middlewares.security.csrf.CSRFMiddleware.rotate_csrf_token
:classmethod:

```{autodocx-docstring} duck.http.middlewares.security.csrf.CSRFMiddleware.rotate_csrf_token
```

````

`````

````{py:data} CSRF_SECRET_LENGTH
:canonical: duck.http.middlewares.security.csrf.CSRF_SECRET_LENGTH
:value: >
   None

```{autodocx-docstring} duck.http.middlewares.security.csrf.CSRF_SECRET_LENGTH
```

````

````{py:data} CSRF_SESSION_KEY
:canonical: duck.http.middlewares.security.csrf.CSRF_SESSION_KEY
:value: >
   None

```{autodocx-docstring} duck.http.middlewares.security.csrf.CSRF_SESSION_KEY
```

````

````{py:data} CSRF_TOKEN_LENGTH
:canonical: duck.http.middlewares.security.csrf.CSRF_TOKEN_LENGTH
:value: >
   None

```{autodocx-docstring} duck.http.middlewares.security.csrf.CSRF_TOKEN_LENGTH
```

````

````{py:data} CSRF_USE_SESSIONS
:canonical: duck.http.middlewares.security.csrf.CSRF_USE_SESSIONS
:value: >
   None

```{autodocx-docstring} duck.http.middlewares.security.csrf.CSRF_USE_SESSIONS
```

````

````{py:exception} OriginError()
:canonical: duck.http.middlewares.security.csrf.OriginError

Bases: {py:obj}`Exception`

```{autodocx-docstring} duck.http.middlewares.security.csrf.OriginError
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.http.middlewares.security.csrf.OriginError.__init__
```

````

````{py:exception} RefererError()
:canonical: duck.http.middlewares.security.csrf.RefererError

Bases: {py:obj}`Exception`

```{autodocx-docstring} duck.http.middlewares.security.csrf.RefererError
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.http.middlewares.security.csrf.RefererError.__init__
```

````

````{py:function} add_new_csrf_cookie(request)
:canonical: duck.http.middlewares.security.csrf.add_new_csrf_cookie

```{autodocx-docstring} duck.http.middlewares.security.csrf.add_new_csrf_cookie
```
````

````{py:function} generate_csrf_secret() -> str
:canonical: duck.http.middlewares.security.csrf.generate_csrf_secret

```{autodocx-docstring} duck.http.middlewares.security.csrf.generate_csrf_secret
```
````

````{py:function} generate_dynamic_secret_key() -> bytes
:canonical: duck.http.middlewares.security.csrf.generate_dynamic_secret_key

```{autodocx-docstring} duck.http.middlewares.security.csrf.generate_dynamic_secret_key
```
````

````{py:function} get_csrf_token(request)
:canonical: duck.http.middlewares.security.csrf.get_csrf_token

```{autodocx-docstring} duck.http.middlewares.security.csrf.get_csrf_token
```
````

````{py:function} mask_cipher_secret(secret: str) -> str
:canonical: duck.http.middlewares.security.csrf.mask_cipher_secret

```{autodocx-docstring} duck.http.middlewares.security.csrf.mask_cipher_secret
```
````

````{py:function} unmask_cipher_token(token: str) -> str
:canonical: duck.http.middlewares.security.csrf.unmask_cipher_token

```{autodocx-docstring} duck.http.middlewares.security.csrf.unmask_cipher_token
```
````
