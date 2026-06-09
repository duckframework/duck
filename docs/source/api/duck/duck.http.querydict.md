# {py:mod}`duck.http.querydict`

```{py:module} duck.http.querydict
```

```{autodocx-docstring} duck.http.querydict
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`FixedQueryDict <duck.http.querydict.FixedQueryDict>`
  - ```{autodocx-docstring} duck.http.querydict.FixedQueryDict
    :summary:
    ```
* - {py:obj}`QueryDict <duck.http.querydict.QueryDict>`
  - ```{autodocx-docstring} duck.http.querydict.QueryDict
    :summary:
    ```
````

### API

`````{py:class} FixedQueryDict(data: dict)
:canonical: duck.http.querydict.FixedQueryDict

Bases: {py:obj}`duck.http.querydict.QueryDict`

```{autodocx-docstring} duck.http.querydict.FixedQueryDict
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.http.querydict.FixedQueryDict.__init__
```

````{py:method} __delitem__(key)
:canonical: duck.http.querydict.FixedQueryDict.__delitem__

```{autodocx-docstring} duck.http.querydict.FixedQueryDict.__delitem__
```

````

````{py:method} __getitem__(key)
:canonical: duck.http.querydict.FixedQueryDict.__getitem__

```{autodocx-docstring} duck.http.querydict.FixedQueryDict.__getitem__
```

````

````{py:method} __repr__()
:canonical: duck.http.querydict.FixedQueryDict.__repr__

```{autodocx-docstring} duck.http.querydict.FixedQueryDict.__repr__
```

````

````{py:method} __setitem__(key, value)
:canonical: duck.http.querydict.FixedQueryDict.__setitem__

```{autodocx-docstring} duck.http.querydict.FixedQueryDict.__setitem__
```

````

````{py:attribute} __slots__
:canonical: duck.http.querydict.FixedQueryDict.__slots__
:value: >
   ('_data', '_keys')

```{autodocx-docstring} duck.http.querydict.FixedQueryDict.__slots__
```

````

````{py:method} get(key)
:canonical: duck.http.querydict.FixedQueryDict.get

```{autodocx-docstring} duck.http.querydict.FixedQueryDict.get
```

````

````{py:method} update(other: dict)
:canonical: duck.http.querydict.FixedQueryDict.update

```{autodocx-docstring} duck.http.querydict.FixedQueryDict.update
```

````

`````

`````{py:class} QueryDict()
:canonical: duck.http.querydict.QueryDict

Bases: {py:obj}`dict`

```{autodocx-docstring} duck.http.querydict.QueryDict
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.http.querydict.QueryDict.__init__
```

````{py:method} __delitem__(key: str) -> None
:canonical: duck.http.querydict.QueryDict.__delitem__

```{autodocx-docstring} duck.http.querydict.QueryDict.__delitem__
```

````

````{py:method} __getitem__(key: str)
:canonical: duck.http.querydict.QueryDict.__getitem__

```{autodocx-docstring} duck.http.querydict.QueryDict.__getitem__
```

````

````{py:method} __repr__()
:canonical: duck.http.querydict.QueryDict.__repr__

````

````{py:method} __setitem__(key: str, value) -> None
:canonical: duck.http.querydict.QueryDict.__setitem__

```{autodocx-docstring} duck.http.querydict.QueryDict.__setitem__
```

````

````{py:attribute} __slots__
:canonical: duck.http.querydict.QueryDict.__slots__
:value: >
   ()

```{autodocx-docstring} duck.http.querydict.QueryDict.__slots__
```

````

````{py:method} appendlist(key: str, value) -> None
:canonical: duck.http.querydict.QueryDict.appendlist

```{autodocx-docstring} duck.http.querydict.QueryDict.appendlist
```

````

````{py:method} clear() -> None
:canonical: duck.http.querydict.QueryDict.clear

```{autodocx-docstring} duck.http.querydict.QueryDict.clear
```

````

````{py:method} copy()
:canonical: duck.http.querydict.QueryDict.copy

```{autodocx-docstring} duck.http.querydict.QueryDict.copy
```

````

````{py:method} get(key: str, default=None)
:canonical: duck.http.querydict.QueryDict.get

```{autodocx-docstring} duck.http.querydict.QueryDict.get
```

````

````{py:method} getlist(key: str, default=None)
:canonical: duck.http.querydict.QueryDict.getlist

```{autodocx-docstring} duck.http.querydict.QueryDict.getlist
```

````

````{py:method} items()
:canonical: duck.http.querydict.QueryDict.items

```{autodocx-docstring} duck.http.querydict.QueryDict.items
```

````

````{py:method} keys()
:canonical: duck.http.querydict.QueryDict.keys

```{autodocx-docstring} duck.http.querydict.QueryDict.keys
```

````

````{py:method} pop(key: str, default=None)
:canonical: duck.http.querydict.QueryDict.pop

```{autodocx-docstring} duck.http.querydict.QueryDict.pop
```

````

````{py:method} poplist(key: str, default=None)
:canonical: duck.http.querydict.QueryDict.poplist

```{autodocx-docstring} duck.http.querydict.QueryDict.poplist
```

````

````{py:method} setlist(key: str, values: list) -> None
:canonical: duck.http.querydict.QueryDict.setlist

```{autodocx-docstring} duck.http.querydict.QueryDict.setlist
```

````

````{py:method} update(other=None, **kwargs) -> None
:canonical: duck.http.querydict.QueryDict.update

```{autodocx-docstring} duck.http.querydict.QueryDict.update
```

````

````{py:method} values()
:canonical: duck.http.querydict.QueryDict.values

```{autodocx-docstring} duck.http.querydict.QueryDict.values
```

````

`````
