# {py:mod}`duck.http.session.engine`

```{py:module} duck.http.session.engine
```

```{autodocx-docstring} duck.http.session.engine
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`SessionStore <duck.http.session.engine.SessionStore>`
  - ```{autodocx-docstring} duck.http.session.engine.SessionStore
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`session_connector_mod <duck.http.session.engine.session_connector_mod>`
  - ```{autodocx-docstring} duck.http.session.engine.session_connector_mod
    :summary:
    ```
````

### API

````{py:exception} SessionError()
:canonical: duck.http.session.engine.SessionError

Bases: {py:obj}`Exception`

```{autodocx-docstring} duck.http.session.engine.SessionError
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.http.session.engine.SessionError.__init__
```

````

````{py:exception} SessionExpired()
:canonical: duck.http.session.engine.SessionExpired

Bases: {py:obj}`duck.http.session.engine.SessionError`

```{autodocx-docstring} duck.http.session.engine.SessionExpired
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.http.session.engine.SessionExpired.__init__
```

````

`````{py:class} SessionStore(session_key: str, disable_warnings: bool = False)
:canonical: duck.http.session.engine.SessionStore

Bases: {py:obj}`dict`

```{autodocx-docstring} duck.http.session.engine.SessionStore
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.http.session.engine.SessionStore.__init__
```

````{py:method} __delitem__(key)
:canonical: duck.http.session.engine.SessionStore.__delitem__

````

````{py:method} __getitem__(key)
:canonical: duck.http.session.engine.SessionStore.__getitem__

````

````{py:method} __repr__()
:canonical: duck.http.session.engine.SessionStore.__repr__

````

````{py:method} __setitem__(key, value)
:canonical: duck.http.session.engine.SessionStore.__setitem__

````

````{py:attribute} __slots__
:canonical: duck.http.session.engine.SessionStore.__slots__
:value: >
   None

```{autodocx-docstring} duck.http.session.engine.SessionStore.__slots__
```

````

````{py:method} check_session_storage_connector(method)
:canonical: duck.http.session.engine.SessionStore.check_session_storage_connector
:staticmethod:

```{autodocx-docstring} duck.http.session.engine.SessionStore.check_session_storage_connector
```

````

````{py:method} clear()
:canonical: duck.http.session.engine.SessionStore.clear

```{autodocx-docstring} duck.http.session.engine.SessionStore.clear
```

````

````{py:method} create()
:canonical: duck.http.session.engine.SessionStore.create

```{autodocx-docstring} duck.http.session.engine.SessionStore.create
```

````

````{py:method} delete(session_key: typing.Optional[str] = None)
:canonical: duck.http.session.engine.SessionStore.delete

```{autodocx-docstring} duck.http.session.engine.SessionStore.delete
```

````

````{py:method} exists(session_key: typing.Optional[str] = None) -> bool
:canonical: duck.http.session.engine.SessionStore.exists

```{autodocx-docstring} duck.http.session.engine.SessionStore.exists
```

````

````{py:method} generate_session_id() -> str
:canonical: duck.http.session.engine.SessionStore.generate_session_id
:staticmethod:

```{autodocx-docstring} duck.http.session.engine.SessionStore.generate_session_id
```

````

````{py:method} get_expiry_age()
:canonical: duck.http.session.engine.SessionStore.get_expiry_age

```{autodocx-docstring} duck.http.session.engine.SessionStore.get_expiry_age
```

````

````{py:method} get_expiry_date()
:canonical: duck.http.session.engine.SessionStore.get_expiry_date

```{autodocx-docstring} duck.http.session.engine.SessionStore.get_expiry_date
```

````

````{py:method} load() -> dict
:canonical: duck.http.session.engine.SessionStore.load

```{autodocx-docstring} duck.http.session.engine.SessionStore.load
```

````

````{py:property} modified
:canonical: duck.http.session.engine.SessionStore.modified
:type: bool

```{autodocx-docstring} duck.http.session.engine.SessionStore.modified
```

````

````{py:method} needs_update() -> bool
:canonical: duck.http.session.engine.SessionStore.needs_update

```{autodocx-docstring} duck.http.session.engine.SessionStore.needs_update
```

````

````{py:method} pop(*args, **kwargs)
:canonical: duck.http.session.engine.SessionStore.pop

```{autodocx-docstring} duck.http.session.engine.SessionStore.pop
```

````

````{py:method} popitem(*args, **kwargs)
:canonical: duck.http.session.engine.SessionStore.popitem

```{autodocx-docstring} duck.http.session.engine.SessionStore.popitem
```

````

````{py:method} save(*_)
:canonical: duck.http.session.engine.SessionStore.save

```{autodocx-docstring} duck.http.session.engine.SessionStore.save
```

````

````{py:property} session_key
:canonical: duck.http.session.engine.SessionStore.session_key

```{autodocx-docstring} duck.http.session.engine.SessionStore.session_key
```

````

````{py:method} set_expiry(expiry: typing.Optional[typing.Union[int, float, datetime.datetime, datetime.timedelta]] = None)
:canonical: duck.http.session.engine.SessionStore.set_expiry

```{autodocx-docstring} duck.http.session.engine.SessionStore.set_expiry
```

````

````{py:method} update(data: dict)
:canonical: duck.http.session.engine.SessionStore.update

```{autodocx-docstring} duck.http.session.engine.SessionStore.update
```

````

`````

````{py:data} session_connector_mod
:canonical: duck.http.session.engine.session_connector_mod
:value: >
   'import_module_once(...)'

```{autodocx-docstring} duck.http.session.engine.session_connector_mod
```

````
