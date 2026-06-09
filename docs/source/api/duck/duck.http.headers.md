# {py:mod}`duck.http.headers`

```{py:module} duck.http.headers
```

```{autodocx-docstring} duck.http.headers
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`Headers <duck.http.headers.Headers>`
  - ```{autodocx-docstring} duck.http.headers.Headers
    :summary:
    ```
````

### API

`````{py:class} Headers()
:canonical: duck.http.headers.Headers

Bases: {py:obj}`dict`

```{autodocx-docstring} duck.http.headers.Headers
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.http.headers.Headers.__init__
```

````{py:method} __delitem__(key)
:canonical: duck.http.headers.Headers.__delitem__

````

````{py:method} __repr__()
:canonical: duck.http.headers.Headers.__repr__

````

````{py:method} __setitem__(key: str, value: str)
:canonical: duck.http.headers.Headers.__setitem__

````

````{py:attribute} __slots__
:canonical: duck.http.headers.Headers.__slots__
:value: >
   ()

```{autodocx-docstring} duck.http.headers.Headers.__slots__
```

````

````{py:method} _get_header(header: str, default_value=None) -> typing.Optional[str]
:canonical: duck.http.headers.Headers._get_header

```{autodocx-docstring} duck.http.headers.Headers._get_header
```

````

````{py:method} delete_header(header: str, failsafe: bool = True)
:canonical: duck.http.headers.Headers.delete_header

```{autodocx-docstring} duck.http.headers.Headers.delete_header
```

````

````{py:method} get(header: str, default=None)
:canonical: duck.http.headers.Headers.get

```{autodocx-docstring} duck.http.headers.Headers.get
```

````

````{py:method} parse_from_bytes(data: bytes, delimeter='\r\n')
:canonical: duck.http.headers.Headers.parse_from_bytes

```{autodocx-docstring} duck.http.headers.Headers.parse_from_bytes
```

````

````{py:method} set_header(header: str, value: str)
:canonical: duck.http.headers.Headers.set_header

```{autodocx-docstring} duck.http.headers.Headers.set_header
```

````

````{py:method} setdefault(key: str, value: str)
:canonical: duck.http.headers.Headers.setdefault

````

````{py:method} titled_headers()
:canonical: duck.http.headers.Headers.titled_headers

```{autodocx-docstring} duck.http.headers.Headers.titled_headers
```

````

````{py:method} update(data: dict)
:canonical: duck.http.headers.Headers.update

````

````{py:method} validate_key_value(key: str, value: str)
:canonical: duck.http.headers.Headers.validate_key_value

```{autodocx-docstring} duck.http.headers.Headers.validate_key_value
```

````

`````
