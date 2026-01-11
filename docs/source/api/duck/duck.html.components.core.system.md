# {py:mod}`duck.html.components.core.system`

```{py:module} duck.html.components.core.system
```

```{autodocx-docstring} duck.html.components.core.system
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`LivelyComponentSystem <duck.html.components.core.system.LivelyComponentSystem>`
  - ```{autodocx-docstring} duck.html.components.core.system.LivelyComponentSystem
    :summary:
    ```
````

### API

`````{py:class} LivelyComponentSystem
:canonical: duck.html.components.core.system.LivelyComponentSystem

```{autodocx-docstring} duck.html.components.core.system.LivelyComponentSystem
```

````{py:method} add_to_registry(uid: str, component: duck.html.components.Component) -> None
:canonical: duck.html.components.core.system.LivelyComponentSystem.add_to_registry
:classmethod:

```{autodocx-docstring} duck.html.components.core.system.LivelyComponentSystem.add_to_registry
```

````

````{py:method} get_from_registry(root_uid: str, uid: str, default: typing.Optional[typing.Any] = None) -> typing.Optional[duck.html.components.Component]
:canonical: duck.html.components.core.system.LivelyComponentSystem.get_from_registry
:classmethod:

```{autodocx-docstring} duck.html.components.core.system.LivelyComponentSystem.get_from_registry
```

````

````{py:method} get_html_tags() -> typing.List[duck.html.components.templatetags.ComponentTag]
:canonical: duck.html.components.core.system.LivelyComponentSystem.get_html_tags
:classmethod:

```{autodocx-docstring} duck.html.components.core.system.LivelyComponentSystem.get_html_tags
```

````

````{py:method} get_urlpatterns() -> typing.List[duck.urls.URLPattern]
:canonical: duck.html.components.core.system.LivelyComponentSystem.get_urlpatterns
:classmethod:

```{autodocx-docstring} duck.html.components.core.system.LivelyComponentSystem.get_urlpatterns
```

````

````{py:method} get_websocket_view_cls() -> typing.Type
:canonical: duck.html.components.core.system.LivelyComponentSystem.get_websocket_view_cls
:classmethod:

```{autodocx-docstring} duck.html.components.core.system.LivelyComponentSystem.get_websocket_view_cls
```

````

````{py:method} is_active() -> bool
:canonical: duck.html.components.core.system.LivelyComponentSystem.is_active
:classmethod:

```{autodocx-docstring} duck.html.components.core.system.LivelyComponentSystem.is_active
```

````

````{py:attribute} registry
:canonical: duck.html.components.core.system.LivelyComponentSystem.registry
:type: duck.utils.caching.InMemoryCache
:value: >
   'InMemoryCache(...)'

```{autodocx-docstring} duck.html.components.core.system.LivelyComponentSystem.registry
```

````

````{py:attribute} registry_lock
:canonical: duck.html.components.core.system.LivelyComponentSystem.registry_lock
:value: >
   'Lock(...)'

```{autodocx-docstring} duck.html.components.core.system.LivelyComponentSystem.registry_lock
```

````

`````
