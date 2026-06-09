# {py:mod}`duck.http.middlewares.contrib.www_redirect`

```{py:module} duck.http.middlewares.contrib.www_redirect
```

```{autodocx-docstring} duck.http.middlewares.contrib.www_redirect
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`WWWRedirectMiddleware <duck.http.middlewares.contrib.www_redirect.WWWRedirectMiddleware>`
  - ```{autodocx-docstring} duck.http.middlewares.contrib.www_redirect.WWWRedirectMiddleware
    :summary:
    ```
````

### API

`````{py:class} WWWRedirectMiddleware
:canonical: duck.http.middlewares.contrib.www_redirect.WWWRedirectMiddleware

Bases: {py:obj}`duck.http.middlewares.BaseMiddleware`

```{autodocx-docstring} duck.http.middlewares.contrib.www_redirect.WWWRedirectMiddleware
```

````{py:attribute} debug_message
:canonical: duck.http.middlewares.contrib.www_redirect.WWWRedirectMiddleware.debug_message
:type: str
:value: >
   'WWWRedirectMiddleware: Redirecting to non-www domain'

```{autodocx-docstring} duck.http.middlewares.contrib.www_redirect.WWWRedirectMiddleware.debug_message
```

````

````{py:method} get_error_response(request)
:canonical: duck.http.middlewares.contrib.www_redirect.WWWRedirectMiddleware.get_error_response
:classmethod:

```{autodocx-docstring} duck.http.middlewares.contrib.www_redirect.WWWRedirectMiddleware.get_error_response
```

````

````{py:method} process_request(request)
:canonical: duck.http.middlewares.contrib.www_redirect.WWWRedirectMiddleware.process_request
:classmethod:

````

`````
