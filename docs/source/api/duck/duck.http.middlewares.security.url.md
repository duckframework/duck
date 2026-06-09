# {py:mod}`duck.http.middlewares.security.url`

```{py:module} duck.http.middlewares.security.url
```

```{autodocx-docstring} duck.http.middlewares.security.url
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`CommandInjectionMiddleware <duck.http.middlewares.security.url.CommandInjectionMiddleware>`
  - ```{autodocx-docstring} duck.http.middlewares.security.url.CommandInjectionMiddleware
    :summary:
    ```
* - {py:obj}`SQLInjectionMiddleware <duck.http.middlewares.security.url.SQLInjectionMiddleware>`
  - ```{autodocx-docstring} duck.http.middlewares.security.url.SQLInjectionMiddleware
    :summary:
    ```
* - {py:obj}`URLSecurityMiddleware <duck.http.middlewares.security.url.URLSecurityMiddleware>`
  - ```{autodocx-docstring} duck.http.middlewares.security.url.URLSecurityMiddleware
    :summary:
    ```
* - {py:obj}`XSSMiddleware <duck.http.middlewares.security.url.XSSMiddleware>`
  - ```{autodocx-docstring} duck.http.middlewares.security.url.XSSMiddleware
    :summary:
    ```
````

### API

`````{py:class} CommandInjectionMiddleware
:canonical: duck.http.middlewares.security.url.CommandInjectionMiddleware

Bases: {py:obj}`duck.http.middlewares.BaseMiddleware`

```{autodocx-docstring} duck.http.middlewares.security.url.CommandInjectionMiddleware
```

````{py:attribute} debug_message
:canonical: duck.http.middlewares.security.url.CommandInjectionMiddleware.debug_message
:type: str
:value: >
   'CommandInjectionMiddleware: Potential URL command injection'

```{autodocx-docstring} duck.http.middlewares.security.url.CommandInjectionMiddleware.debug_message
```

````

````{py:method} get_error_response(request)
:canonical: duck.http.middlewares.security.url.CommandInjectionMiddleware.get_error_response
:classmethod:

````

````{py:method} process_request(request)
:canonical: duck.http.middlewares.security.url.CommandInjectionMiddleware.process_request
:classmethod:

````

`````

`````{py:class} SQLInjectionMiddleware
:canonical: duck.http.middlewares.security.url.SQLInjectionMiddleware

Bases: {py:obj}`duck.http.middlewares.BaseMiddleware`

```{autodocx-docstring} duck.http.middlewares.security.url.SQLInjectionMiddleware
```

````{py:attribute} debug_message
:canonical: duck.http.middlewares.security.url.SQLInjectionMiddleware.debug_message
:type: str
:value: >
   'SQLInjectionMiddleware: Potential URL sql injection'

```{autodocx-docstring} duck.http.middlewares.security.url.SQLInjectionMiddleware.debug_message
```

````

````{py:method} get_error_response(request)
:canonical: duck.http.middlewares.security.url.SQLInjectionMiddleware.get_error_response
:classmethod:

````

````{py:method} process_request(request)
:canonical: duck.http.middlewares.security.url.SQLInjectionMiddleware.process_request
:classmethod:

````

`````

`````{py:class} URLSecurityMiddleware
:canonical: duck.http.middlewares.security.url.URLSecurityMiddleware

Bases: {py:obj}`duck.http.middlewares.BaseMiddleware`

```{autodocx-docstring} duck.http.middlewares.security.url.URLSecurityMiddleware
```

````{py:attribute} debug_message
:canonical: duck.http.middlewares.security.url.URLSecurityMiddleware.debug_message
:type: str
:value: >
   'URLSecurityMiddleware: Malformed URL'

```{autodocx-docstring} duck.http.middlewares.security.url.URLSecurityMiddleware.debug_message
```

````

````{py:method} get_error_response(request)
:canonical: duck.http.middlewares.security.url.URLSecurityMiddleware.get_error_response
:classmethod:

````

````{py:method} process_request(request)
:canonical: duck.http.middlewares.security.url.URLSecurityMiddleware.process_request
:classmethod:

````

`````

`````{py:class} XSSMiddleware
:canonical: duck.http.middlewares.security.url.XSSMiddleware

Bases: {py:obj}`duck.http.middlewares.BaseMiddleware`

```{autodocx-docstring} duck.http.middlewares.security.url.XSSMiddleware
```

````{py:attribute} debug_message
:canonical: duck.http.middlewares.security.url.XSSMiddleware.debug_message
:type: str
:value: >
   'XSSMiddleware: Potential url xss'

```{autodocx-docstring} duck.http.middlewares.security.url.XSSMiddleware.debug_message
```

````

````{py:method} get_error_response(request)
:canonical: duck.http.middlewares.security.url.XSSMiddleware.get_error_response
:classmethod:

````

````{py:method} process_request(request)
:canonical: duck.http.middlewares.security.url.XSSMiddleware.process_request
:classmethod:

````

`````
