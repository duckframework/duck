# {py:mod}`duck.http.middlewares.contrib.metashare`

```{py:module} duck.http.middlewares.contrib.metashare
```

```{autodocx-docstring} duck.http.middlewares.contrib.metashare
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`MetaShareMiddleware <duck.http.middlewares.contrib.metashare.MetaShareMiddleware>`
  - ```{autodocx-docstring} duck.http.middlewares.contrib.metashare.MetaShareMiddleware
    :summary:
    ```
````

### API

`````{py:class} MetaShareMiddleware
:canonical: duck.http.middlewares.contrib.metashare.MetaShareMiddleware

Bases: {py:obj}`duck.http.middlewares.BaseMiddleware`

```{autodocx-docstring} duck.http.middlewares.contrib.metashare.MetaShareMiddleware
```

````{py:method} compile_meta_to_headers(meta: typing.Dict)
:canonical: duck.http.middlewares.contrib.metashare.MetaShareMiddleware.compile_meta_to_headers
:classmethod:

```{autodocx-docstring} duck.http.middlewares.contrib.metashare.MetaShareMiddleware.compile_meta_to_headers
```

````

````{py:method} process_request(request)
:canonical: duck.http.middlewares.contrib.metashare.MetaShareMiddleware.process_request
:classmethod:

````

````{py:method} resolve_meta_from_headers(headers: typing.Dict) -> typing.Dict
:canonical: duck.http.middlewares.contrib.metashare.MetaShareMiddleware.resolve_meta_from_headers
:classmethod:

```{autodocx-docstring} duck.http.middlewares.contrib.metashare.MetaShareMiddleware.resolve_meta_from_headers
```

````

`````
