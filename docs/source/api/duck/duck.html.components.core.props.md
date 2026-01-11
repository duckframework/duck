# {py:mod}`duck.html.components.core.props`

```{py:module} duck.html.components.core.props
```

```{autodocx-docstring} duck.html.components.core.props
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`PropertyStore <duck.html.components.core.props.PropertyStore>`
  - ```{autodocx-docstring} duck.html.components.core.props.PropertyStore
    :summary:
    ```
* - {py:obj}`StyleStore <duck.html.components.core.props.StyleStore>`
  - ```{autodocx-docstring} duck.html.components.core.props.StyleStore
    :summary:
    ```
````

### API

`````{py:class} PropertyStore(initdict: typing.Optional[typing.Dict[typing.Any, typing.Any]] = None, on_set_item: typing.Optional[typing.Callable] = None, on_delete_item: typing.Optional[typing.Callable] = None)
:canonical: duck.html.components.core.props.PropertyStore

Bases: {py:obj}`dict`

```{autodocx-docstring} duck.html.components.core.props.PropertyStore
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.html.components.core.props.PropertyStore.__init__
```

````{py:method} __delitem__(key: str, call_on_delete_item_handler: bool = True) -> None
:canonical: duck.html.components.core.props.PropertyStore.__delitem__

```{autodocx-docstring} duck.html.components.core.props.PropertyStore.__delitem__
```

````

````{py:method} __repr__() -> str
:canonical: duck.html.components.core.props.PropertyStore.__repr__

```{autodocx-docstring} duck.html.components.core.props.PropertyStore.__repr__
```

````

````{py:method} __setitem__(key: str, value: str, call_on_set_item_handler: bool = True) -> None
:canonical: duck.html.components.core.props.PropertyStore.__setitem__

```{autodocx-docstring} duck.html.components.core.props.PropertyStore.__setitem__
```

````

````{py:attribute} __slots__
:canonical: duck.html.components.core.props.PropertyStore.__slots__
:value: >
   ('__version', '_on_set_item_func', '_on_delete_item_func')

```{autodocx-docstring} duck.html.components.core.props.PropertyStore.__slots__
```

````

````{py:method} _on_delete_item(k)
:canonical: duck.html.components.core.props.PropertyStore._on_delete_item

```{autodocx-docstring} duck.html.components.core.props.PropertyStore._on_delete_item
```

````

````{py:method} _on_set_item(k, v)
:canonical: duck.html.components.core.props.PropertyStore._on_set_item

```{autodocx-docstring} duck.html.components.core.props.PropertyStore._on_set_item
```

````

````{py:property} _version
:canonical: duck.html.components.core.props.PropertyStore._version
:type: int

```{autodocx-docstring} duck.html.components.core.props.PropertyStore._version
```

````

````{py:method} on_delete_item(key: str) -> None
:canonical: duck.html.components.core.props.PropertyStore.on_delete_item

```{autodocx-docstring} duck.html.components.core.props.PropertyStore.on_delete_item
```

````

````{py:method} on_set_item(key: str, value: typing.Any) -> None
:canonical: duck.html.components.core.props.PropertyStore.on_set_item

```{autodocx-docstring} duck.html.components.core.props.PropertyStore.on_set_item
```

````

````{py:method} pop(key: str, default: typing.Any = None) -> typing.Any
:canonical: duck.html.components.core.props.PropertyStore.pop

```{autodocx-docstring} duck.html.components.core.props.PropertyStore.pop
```

````

````{py:method} popitem() -> typing.Tuple[str, str]
:canonical: duck.html.components.core.props.PropertyStore.popitem

```{autodocx-docstring} duck.html.components.core.props.PropertyStore.popitem
```

````

````{py:method} setdefault(key: str, default: typing.Optional[str] = None, call_on_set_item_handler: bool = True) -> str
:canonical: duck.html.components.core.props.PropertyStore.setdefault

```{autodocx-docstring} duck.html.components.core.props.PropertyStore.setdefault
```

````

````{py:method} setdefaults(data: typing.Dict[str, str]) -> None
:canonical: duck.html.components.core.props.PropertyStore.setdefaults

```{autodocx-docstring} duck.html.components.core.props.PropertyStore.setdefaults
```

````

````{py:method} update(data: typing.Any = None, call_on_set_item_handler: bool = True, *args, **kwargs) -> None
:canonical: duck.html.components.core.props.PropertyStore.update

```{autodocx-docstring} duck.html.components.core.props.PropertyStore.update
```

````

`````

````{py:class} StyleStore(initdict: typing.Optional[typing.Dict[typing.Any, typing.Any]] = None, on_set_item: typing.Optional[typing.Callable] = None, on_delete_item: typing.Optional[typing.Callable] = None)
:canonical: duck.html.components.core.props.StyleStore

Bases: {py:obj}`duck.html.components.core.props.PropertyStore`

```{autodocx-docstring} duck.html.components.core.props.StyleStore
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.html.components.core.props.StyleStore.__init__
```

````
