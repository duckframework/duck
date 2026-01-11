# {py:mod}`duck.meta`

```{py:module} duck.meta
```

```{autodocx-docstring} duck.meta
:allowtitles:
```

## Package Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`Meta <duck.meta.Meta>`
  - ```{autodocx-docstring} duck.meta.Meta
    :summary:
    ```
````

### API

`````{py:class} Meta
:canonical: duck.meta.Meta

```{autodocx-docstring} duck.meta.Meta
```

````{py:method} compile() -> dict
:canonical: duck.meta.Meta.compile
:classmethod:

```{autodocx-docstring} duck.meta.Meta.compile
```

````

````{py:attribute} exceptional_keys
:canonical: duck.meta.Meta.exceptional_keys
:type: list
:value: >
   ['DUCK_SERVER_DOMAIN', 'DUCK_SERVER_ADDR', 'DUCK_DJANGO_ADDR']

```{autodocx-docstring} duck.meta.Meta.exceptional_keys
```

````

````{py:method} get_absolute_server_url() -> str
:canonical: duck.meta.Meta.get_absolute_server_url
:classmethod:

```{autodocx-docstring} duck.meta.Meta.get_absolute_server_url
```

````

````{py:method} get_absolute_ws_server_url() -> str
:canonical: duck.meta.Meta.get_absolute_ws_server_url
:classmethod:

```{autodocx-docstring} duck.meta.Meta.get_absolute_ws_server_url
```

````

````{py:method} get_metadata(key: str, default_value: typing.Any = None) -> typing.Any
:canonical: duck.meta.Meta.get_metadata
:classmethod:

```{autodocx-docstring} duck.meta.Meta.get_metadata
```

````

````{py:attribute} meta_keys
:canonical: duck.meta.Meta.meta_keys
:type: list
:value: >
   []

```{autodocx-docstring} duck.meta.Meta.meta_keys
```

````

````{py:method} set_metadata(key: str, value: typing.Any)
:canonical: duck.meta.Meta.set_metadata
:classmethod:

```{autodocx-docstring} duck.meta.Meta.set_metadata
```

````

````{py:method} update_meta(data: dict)
:canonical: duck.meta.Meta.update_meta
:classmethod:

```{autodocx-docstring} duck.meta.Meta.update_meta
```

````

`````

````{py:exception} MetaError()
:canonical: duck.meta.MetaError

Bases: {py:obj}`Exception`

```{autodocx-docstring} duck.meta.MetaError
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.meta.MetaError.__init__
```

````
