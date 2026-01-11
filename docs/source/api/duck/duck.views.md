# {py:mod}`duck.views`

```{py:module} duck.views
```

```{autodocx-docstring} duck.views
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`View <duck.views.View>`
  - ```{autodocx-docstring} duck.views.View
    :summary:
    ```
````

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`cached_view <duck.views.cached_view>`
  - ```{autodocx-docstring} duck.views.cached_view
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`DEFAULT_VIEW_CACHE <duck.views.DEFAULT_VIEW_CACHE>`
  - ```{autodocx-docstring} duck.views.DEFAULT_VIEW_CACHE
    :summary:
    ```
````

### API

````{py:data} DEFAULT_VIEW_CACHE
:canonical: duck.views.DEFAULT_VIEW_CACHE
:value: >
   'InMemoryCache(...)'

```{autodocx-docstring} duck.views.DEFAULT_VIEW_CACHE
```

````

````{py:exception} SkipViewCaching()
:canonical: duck.views.SkipViewCaching

Bases: {py:obj}`Exception`

```{autodocx-docstring} duck.views.SkipViewCaching
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.views.SkipViewCaching.__init__
```

````

`````{py:class} View(request: duck.http.request.HttpRequest, **kwargs)
:canonical: duck.views.View

```{autodocx-docstring} duck.views.View
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.views.View.__init__
```

````{py:method} run() -> typing.Optional[duck.http.response.HttpResponse]
:canonical: duck.views.View.run
:abstractmethod:

```{autodocx-docstring} duck.views.View.run
```

````

````{py:method} strictly_async() -> bool
:canonical: duck.views.View.strictly_async

```{autodocx-docstring} duck.views.View.strictly_async
```

````

`````

````{py:exception} ViewCachingError()
:canonical: duck.views.ViewCachingError

Bases: {py:obj}`Exception`

```{autodocx-docstring} duck.views.ViewCachingError
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.views.ViewCachingError.__init__
```

````

````{py:exception} ViewCachingWarning()
:canonical: duck.views.ViewCachingWarning

Bases: {py:obj}`UserWarning`

```{autodocx-docstring} duck.views.ViewCachingWarning
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.views.ViewCachingWarning.__init__
```

````

````{py:function} cached_view(targets: typing.Union[typing.Dict[typing.Union[str, typing.Callable], typing.Dict[str, typing.Any]], typing.List[str]], expiry: typing.Optional[float] = None, cache_backend: typing.Optional = None, namespace: typing.Optional[typing.Union[str, typing.Callable]] = None, skip_cache_attr: str = 'skip_cache', on_cache_result: typing.Optional[typing.Callable] = None, returns_static_response: bool = False, freeze_if_component_response: bool = True)
:canonical: duck.views.cached_view

```{autodocx-docstring} duck.views.cached_view
```
````
