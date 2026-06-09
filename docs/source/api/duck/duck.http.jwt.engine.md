# {py:mod}`duck.http.jwt.engine`

```{py:module} duck.http.jwt.engine
```

```{autodocx-docstring} duck.http.jwt.engine
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`JWTStore <duck.http.jwt.engine.JWTStore>`
  - ```{autodocx-docstring} duck.http.jwt.engine.JWTStore
    :summary:
    ```
````

### API

`````{py:class} JWTStore(raw_token: typing.Optional[str] = None)
:canonical: duck.http.jwt.engine.JWTStore

```{autodocx-docstring} duck.http.jwt.engine.JWTStore
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.http.jwt.engine.JWTStore.__init__
```

````{py:method} __contains__(key)
:canonical: duck.http.jwt.engine.JWTStore.__contains__

```{autodocx-docstring} duck.http.jwt.engine.JWTStore.__contains__
```

````

````{py:method} __delitem__(key)
:canonical: duck.http.jwt.engine.JWTStore.__delitem__

```{autodocx-docstring} duck.http.jwt.engine.JWTStore.__delitem__
```

````

````{py:method} __getitem__(key)
:canonical: duck.http.jwt.engine.JWTStore.__getitem__

```{autodocx-docstring} duck.http.jwt.engine.JWTStore.__getitem__
```

````

````{py:method} __iter__()
:canonical: duck.http.jwt.engine.JWTStore.__iter__

```{autodocx-docstring} duck.http.jwt.engine.JWTStore.__iter__
```

````

````{py:method} __repr__()
:canonical: duck.http.jwt.engine.JWTStore.__repr__

````

````{py:method} __setitem__(key, value)
:canonical: duck.http.jwt.engine.JWTStore.__setitem__

```{autodocx-docstring} duck.http.jwt.engine.JWTStore.__setitem__
```

````

````{py:attribute} __slots__
:canonical: duck.http.jwt.engine.JWTStore.__slots__
:value: >
   ('raw_token', 'payload', 'loaded', 'modified')

```{autodocx-docstring} duck.http.jwt.engine.JWTStore.__slots__
```

````

````{py:method} clear()
:canonical: duck.http.jwt.engine.JWTStore.clear

```{autodocx-docstring} duck.http.jwt.engine.JWTStore.clear
```

````

````{py:method} delete(key: str)
:canonical: duck.http.jwt.engine.JWTStore.delete

```{autodocx-docstring} duck.http.jwt.engine.JWTStore.delete
```

````

````{py:method} encode() -> str
:canonical: duck.http.jwt.engine.JWTStore.encode

```{autodocx-docstring} duck.http.jwt.engine.JWTStore.encode
```

````

````{py:method} encode_all() -> typing.Dict[str, str]
:canonical: duck.http.jwt.engine.JWTStore.encode_all

```{autodocx-docstring} duck.http.jwt.engine.JWTStore.encode_all
```

````

````{py:method} encode_refresh_token() -> str
:canonical: duck.http.jwt.engine.JWTStore.encode_refresh_token

```{autodocx-docstring} duck.http.jwt.engine.JWTStore.encode_refresh_token
```

````

````{py:method} ensure_loaded(method)
:canonical: duck.http.jwt.engine.JWTStore.ensure_loaded
:staticmethod:

```{autodocx-docstring} duck.http.jwt.engine.JWTStore.ensure_loaded
```

````

````{py:property} expiry_secs
:canonical: duck.http.jwt.engine.JWTStore.expiry_secs
:type: typing.Optional[float]

```{autodocx-docstring} duck.http.jwt.engine.JWTStore.expiry_secs
```

````

````{py:method} get(key: str, default=None)
:canonical: duck.http.jwt.engine.JWTStore.get

```{autodocx-docstring} duck.http.jwt.engine.JWTStore.get
```

````

````{py:method} is_expired() -> bool
:canonical: duck.http.jwt.engine.JWTStore.is_expired

```{autodocx-docstring} duck.http.jwt.engine.JWTStore.is_expired
```

````

````{py:method} items()
:canonical: duck.http.jwt.engine.JWTStore.items

```{autodocx-docstring} duck.http.jwt.engine.JWTStore.items
```

````

````{py:method} keys()
:canonical: duck.http.jwt.engine.JWTStore.keys

```{autodocx-docstring} duck.http.jwt.engine.JWTStore.keys
```

````

````{py:method} load() -> dict
:canonical: duck.http.jwt.engine.JWTStore.load

```{autodocx-docstring} duck.http.jwt.engine.JWTStore.load
```

````

````{py:method} mark_updated()
:canonical: duck.http.jwt.engine.JWTStore.mark_updated

```{autodocx-docstring} duck.http.jwt.engine.JWTStore.mark_updated
```

````

````{py:method} needs_update() -> bool
:canonical: duck.http.jwt.engine.JWTStore.needs_update

```{autodocx-docstring} duck.http.jwt.engine.JWTStore.needs_update
```

````

````{py:method} reset()
:canonical: duck.http.jwt.engine.JWTStore.reset

```{autodocx-docstring} duck.http.jwt.engine.JWTStore.reset
```

````

````{py:method} reset_expiry()
:canonical: duck.http.jwt.engine.JWTStore.reset_expiry

```{autodocx-docstring} duck.http.jwt.engine.JWTStore.reset_expiry
```

````

````{py:method} set(key: str, value)
:canonical: duck.http.jwt.engine.JWTStore.set

```{autodocx-docstring} duck.http.jwt.engine.JWTStore.set
```

````

````{py:method} set_expiry(expiry: typing.Optional[typing.Union[int, float, datetime.datetime, datetime.timedelta]] = None)
:canonical: duck.http.jwt.engine.JWTStore.set_expiry

```{autodocx-docstring} duck.http.jwt.engine.JWTStore.set_expiry
```

````

````{py:method} update(data: dict)
:canonical: duck.http.jwt.engine.JWTStore.update

```{autodocx-docstring} duck.http.jwt.engine.JWTStore.update
```

````

````{py:method} values()
:canonical: duck.http.jwt.engine.JWTStore.values

```{autodocx-docstring} duck.http.jwt.engine.JWTStore.values
```

````

`````
