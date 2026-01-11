# {py:mod}`duck.contrib.websockets.frame`

```{py:module} duck.contrib.websockets.frame
```

```{autodocx-docstring} duck.contrib.websockets.frame
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`Frame <duck.contrib.websockets.frame.Frame>`
  - ```{autodocx-docstring} duck.contrib.websockets.frame.Frame
    :summary:
    ```
````

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`apply_mask <duck.contrib.websockets.frame.apply_mask>`
  - ```{autodocx-docstring} duck.contrib.websockets.frame.apply_mask
    :summary:
    ```
````

### API

`````{py:class} Frame(opcode: int, fin: typing.Optional[bool] = True, payload: bytes = b'', rsv1: bool = False, rsv2: bool = False, rsv3: bool = False)
:canonical: duck.contrib.websockets.frame.Frame

```{autodocx-docstring} duck.contrib.websockets.frame.Frame
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.contrib.websockets.frame.Frame.__init__
```

````{py:method} __repr__()
:canonical: duck.contrib.websockets.frame.Frame.__repr__

````

````{py:attribute} __slots__
:canonical: duck.contrib.websockets.frame.Frame.__slots__
:value: >
   ('opcode', 'fin', 'payload', 'rsv1', 'rsv2', 'rsv3')

```{autodocx-docstring} duck.contrib.websockets.frame.Frame.__slots__
```

````

````{py:attribute} __str__
:canonical: duck.contrib.websockets.frame.Frame.__str__
:value: >
   None

```{autodocx-docstring} duck.contrib.websockets.frame.Frame.__str__
```

````

````{py:method} check() -> None
:canonical: duck.contrib.websockets.frame.Frame.check

```{autodocx-docstring} duck.contrib.websockets.frame.Frame.check
```

````

````{py:method} parse(read_exact: typing.Callable[[int], bytes], mask_required: bool = True, max_size: typing.Optional[int] = None, extensions: typing.Optional[typing.Sequence[duck.contrib.websockets.extensions.Extension]] = None) -> duck.contrib.websockets.frame.Frame
:canonical: duck.contrib.websockets.frame.Frame.parse
:async:
:classmethod:

```{autodocx-docstring} duck.contrib.websockets.frame.Frame.parse
```

````

````{py:method} serialize(mask: bool = False, extensions: typing.Optional[typing.Sequence[duck.contrib.websockets.extensions.Extension]] = None) -> bytes
:canonical: duck.contrib.websockets.frame.Frame.serialize

```{autodocx-docstring} duck.contrib.websockets.frame.Frame.serialize
```

````

`````

````{py:function} apply_mask(data: bytes, mask: bytes) -> bytes
:canonical: duck.contrib.websockets.frame.apply_mask

```{autodocx-docstring} duck.contrib.websockets.frame.apply_mask
```
````
