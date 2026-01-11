# {py:mod}`duck.http.middlewares.contrib.session`

```{py:module} duck.http.middlewares.contrib.session
```

```{autodocx-docstring} duck.http.middlewares.contrib.session
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`SessionMiddleware <duck.http.middlewares.contrib.session.SessionMiddleware>`
  - ```{autodocx-docstring} duck.http.middlewares.contrib.session.SessionMiddleware
    :summary:
    ```
````

### API

`````{py:class} SessionMiddleware
:canonical: duck.http.middlewares.contrib.session.SessionMiddleware

Bases: {py:obj}`duck.http.middlewares.BaseMiddleware`

```{autodocx-docstring} duck.http.middlewares.contrib.session.SessionMiddleware
```

````{py:attribute} debug_message
:canonical: duck.http.middlewares.contrib.session.SessionMiddleware.debug_message
:type: str
:value: >
   'SessionMiddleware: Session Error'

```{autodocx-docstring} duck.http.middlewares.contrib.session.SessionMiddleware.debug_message
```

````

````{py:method} process_request(request: duck.http.request.HttpRequest) -> int
:canonical: duck.http.middlewares.contrib.session.SessionMiddleware.process_request
:classmethod:

```{autodocx-docstring} duck.http.middlewares.contrib.session.SessionMiddleware.process_request
```

````

````{py:method} process_response(response, request)
:canonical: duck.http.middlewares.contrib.session.SessionMiddleware.process_response
:classmethod:

````

`````
