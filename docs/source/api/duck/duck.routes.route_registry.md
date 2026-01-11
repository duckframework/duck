# {py:mod}`duck.routes.route_registry`

```{py:module} duck.routes.route_registry
```

```{autodocx-docstring} duck.routes.route_registry
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`BaseRouteRegistry <duck.routes.route_registry.BaseRouteRegistry>`
  - ```{autodocx-docstring} duck.routes.route_registry.BaseRouteRegistry
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`RouteRegistry <duck.routes.route_registry.RouteRegistry>`
  - ```{autodocx-docstring} duck.routes.route_registry.RouteRegistry
    :summary:
    ```
````

### API

`````{py:class} BaseRouteRegistry()
:canonical: duck.routes.route_registry.BaseRouteRegistry

```{autodocx-docstring} duck.routes.route_registry.BaseRouteRegistry
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.routes.route_registry.BaseRouteRegistry.__init__
```

````{py:method} extract_kwargs_from_url(url: str, registered_url: str) -> dict
:canonical: duck.routes.route_registry.BaseRouteRegistry.extract_kwargs_from_url

```{autodocx-docstring} duck.routes.route_registry.BaseRouteRegistry.extract_kwargs_from_url
```

````

````{py:method} fetch_route_info_by_name(name: str) -> typing.Dict
:canonical: duck.routes.route_registry.BaseRouteRegistry.fetch_route_info_by_name

```{autodocx-docstring} duck.routes.route_registry.BaseRouteRegistry.fetch_route_info_by_name
```

````

````{py:method} fetch_route_info_by_url(url_path: str) -> typing.Dict
:canonical: duck.routes.route_registry.BaseRouteRegistry.fetch_route_info_by_url

```{autodocx-docstring} duck.routes.route_registry.BaseRouteRegistry.fetch_route_info_by_url
```

````

````{py:method} regex_register(re_url: str, handler: typing.Callable, name: typing.Optional[str] = None, methods: typing.Optional[typing.List[str]] = None, **kw)
:canonical: duck.routes.route_registry.BaseRouteRegistry.regex_register

```{autodocx-docstring} duck.routes.route_registry.BaseRouteRegistry.regex_register
```

````

````{py:method} register(url_path: str, handler: typing.Callable, name: typing.Optional[str] = None, methods: typing.Optional[typing.List[str]] = None)
:canonical: duck.routes.route_registry.BaseRouteRegistry.register

```{autodocx-docstring} duck.routes.route_registry.BaseRouteRegistry.register
```

````

````{py:attribute} url_map
:canonical: duck.routes.route_registry.BaseRouteRegistry.url_map
:value: >
   'defaultdict(...)'

```{autodocx-docstring} duck.routes.route_registry.BaseRouteRegistry.url_map
```

````

`````

````{py:data} RouteRegistry
:canonical: duck.routes.route_registry.RouteRegistry
:value: >
   'Lazy(...)'

```{autodocx-docstring} duck.routes.route_registry.RouteRegistry
```

````
