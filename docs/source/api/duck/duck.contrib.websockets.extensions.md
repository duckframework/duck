# {py:mod}`duck.contrib.websockets.extensions`

```{py:module} duck.contrib.websockets.extensions
```

```{autodocx-docstring} duck.contrib.websockets.extensions
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`Extension <duck.contrib.websockets.extensions.Extension>`
  - ```{autodocx-docstring} duck.contrib.websockets.extensions.Extension
    :summary:
    ```
* - {py:obj}`PerMessageDeflate <duck.contrib.websockets.extensions.PerMessageDeflate>`
  - ```{autodocx-docstring} duck.contrib.websockets.extensions.PerMessageDeflate
    :summary:
    ```
````

### API

`````{py:class} Extension(name: str)
:canonical: duck.contrib.websockets.extensions.Extension

```{autodocx-docstring} duck.contrib.websockets.extensions.Extension
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.contrib.websockets.extensions.Extension.__init__
```

````{py:method} check_frame(frame)
:canonical: duck.contrib.websockets.extensions.Extension.check_frame

```{autodocx-docstring} duck.contrib.websockets.extensions.Extension.check_frame
```

````

````{py:method} decode(frame) -> Frame
:canonical: duck.contrib.websockets.extensions.Extension.decode
:abstractmethod:

```{autodocx-docstring} duck.contrib.websockets.extensions.Extension.decode
```

````

````{py:method} encode(frame) -> Frame
:canonical: duck.contrib.websockets.extensions.Extension.encode
:abstractmethod:

```{autodocx-docstring} duck.contrib.websockets.extensions.Extension.encode
```

````

`````

`````{py:class} PerMessageDeflate(name: str, client_no_context_takeover: bool = False, server_no_context_takeover: bool = False, client_max_window_bits: int = 15)
:canonical: duck.contrib.websockets.extensions.PerMessageDeflate

Bases: {py:obj}`duck.contrib.websockets.extensions.Extension`

```{autodocx-docstring} duck.contrib.websockets.extensions.PerMessageDeflate
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.contrib.websockets.extensions.PerMessageDeflate.__init__
```

````{py:method} __repr__()
:canonical: duck.contrib.websockets.extensions.PerMessageDeflate.__repr__

```{autodocx-docstring} duck.contrib.websockets.extensions.PerMessageDeflate.__repr__
```

````

````{py:method} decode(frame) -> Frame
:canonical: duck.contrib.websockets.extensions.PerMessageDeflate.decode

```{autodocx-docstring} duck.contrib.websockets.extensions.PerMessageDeflate.decode
```

````

````{py:method} encode(frame) -> Frame
:canonical: duck.contrib.websockets.extensions.PerMessageDeflate.encode

```{autodocx-docstring} duck.contrib.websockets.extensions.PerMessageDeflate.encode
```

````

`````
