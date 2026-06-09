# {py:mod}`duck.html.components.utils.caching`

```{py:module} duck.html.components.utils.caching
```

```{autodocx-docstring} duck.html.components.utils.caching
:allowtitles:
```

## Module Contents

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`CachedComponent <duck.html.components.utils.caching.CachedComponent>`
  - ```{autodocx-docstring} duck.html.components.utils.caching.CachedComponent
    :summary:
    ```
* - {py:obj}`cached_component <duck.html.components.utils.caching.cached_component>`
  - ```{autodocx-docstring} duck.html.components.utils.caching.cached_component
    :summary:
    ```
* - {py:obj}`make_cache_key <duck.html.components.utils.caching.make_cache_key>`
  - ```{autodocx-docstring} duck.html.components.utils.caching.make_cache_key
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`DEFAULT_CACHE_BACKEND <duck.html.components.utils.caching.DEFAULT_CACHE_BACKEND>`
  - ```{autodocx-docstring} duck.html.components.utils.caching.DEFAULT_CACHE_BACKEND
    :summary:
    ```
````

### API

````{py:function} CachedComponent(component_cls: typing.Type, **cache_options)
:canonical: duck.html.components.utils.caching.CachedComponent

```{autodocx-docstring} duck.html.components.utils.caching.CachedComponent
```
````

````{py:exception} ComponentCachingError()
:canonical: duck.html.components.utils.caching.ComponentCachingError

Bases: {py:obj}`Exception`

```{autodocx-docstring} duck.html.components.utils.caching.ComponentCachingError
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.html.components.utils.caching.ComponentCachingError.__init__
```

````

````{py:data} DEFAULT_CACHE_BACKEND
:canonical: duck.html.components.utils.caching.DEFAULT_CACHE_BACKEND
:value: >
   'InMemoryCache(...)'

```{autodocx-docstring} duck.html.components.utils.caching.DEFAULT_CACHE_BACKEND
```

````

````{py:function} cached_component(targets: typing.Optional[typing.List[typing.Union[str, typing.Callable]]] = None, cache_backend: typing.Optional[typing.Any] = None, expiry: typing.Optional[float] = None, namespace: typing.Optional[typing.Union[str, typing.Callable]] = None, ignore_args: typing.Optional[typing.List[int]] = None, ignore_kwargs: typing.Optional[typing.List[str]] = None, skip_cache_attr: str = 'skip_cache', on_cache_result: typing.Optional[typing.Callable] = None, freeze: bool = False, return_copy: bool = True, _no_caching: bool = False)
:canonical: duck.html.components.utils.caching.cached_component

```{autodocx-docstring} duck.html.components.utils.caching.cached_component
```
````

````{py:function} make_cache_key(component_cls, args: typing.Any, kwargs: typing.Dict[str, typing.Any], namespace: typing.Optional[str] = None) -> typing.Tuple
:canonical: duck.html.components.utils.caching.make_cache_key

```{autodocx-docstring} duck.html.components.utils.caching.make_cache_key
```
````
