# {py:mod}`duck.http.session.connector`

```{py:module} duck.http.session.connector
```

```{autodocx-docstring} duck.http.session.connector
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`SessionStorageConnector <duck.http.session.connector.SessionStorageConnector>`
  - ```{autodocx-docstring} duck.http.session.connector.SessionStorageConnector
    :summary:
    ```
````

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`get_session_storage_connector <duck.http.session.connector.get_session_storage_connector>`
  - ```{autodocx-docstring} duck.http.session.connector.get_session_storage_connector
    :summary:
    ```
````

### API

`````{py:class} SessionStorageConnector(session_storage_cls: type[duck.utils.caching.CacheBase])
:canonical: duck.http.session.connector.SessionStorageConnector

```{autodocx-docstring} duck.http.session.connector.SessionStorageConnector
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.http.session.connector.SessionStorageConnector.__init__
```

````{py:attribute} CACHED_SESSIONS
:canonical: duck.http.session.connector.SessionStorageConnector.CACHED_SESSIONS
:value: >
   'InMemoryCache(...)'

```{autodocx-docstring} duck.http.session.connector.SessionStorageConnector.CACHED_SESSIONS
```

````

````{py:method} __new__(session_storage_cls: type[duck.utils.caching.CacheBase])
:canonical: duck.http.session.connector.SessionStorageConnector.__new__

```{autodocx-docstring} duck.http.session.connector.SessionStorageConnector.__new__
```

````

````{py:method} clear_all_sessions() -> None
:canonical: duck.http.session.connector.SessionStorageConnector.clear_all_sessions

```{autodocx-docstring} duck.http.session.connector.SessionStorageConnector.clear_all_sessions
```

````

````{py:method} close() -> None
:canonical: duck.http.session.connector.SessionStorageConnector.close

```{autodocx-docstring} duck.http.session.connector.SessionStorageConnector.close
```

````

````{py:method} delete_session(session_id: str) -> None
:canonical: duck.http.session.connector.SessionStorageConnector.delete_session

```{autodocx-docstring} duck.http.session.connector.SessionStorageConnector.delete_session
```

````

````{py:method} generate_session_id() -> str
:canonical: duck.http.session.connector.SessionStorageConnector.generate_session_id
:staticmethod:

```{autodocx-docstring} duck.http.session.connector.SessionStorageConnector.generate_session_id
```

````

````{py:method} get_session(session_id: str) -> dict | None
:canonical: duck.http.session.connector.SessionStorageConnector.get_session

```{autodocx-docstring} duck.http.session.connector.SessionStorageConnector.get_session
```

````

````{py:attribute} initialized
:canonical: duck.http.session.connector.SessionStorageConnector.initialized
:value: >
   False

```{autodocx-docstring} duck.http.session.connector.SessionStorageConnector.initialized
```

````

````{py:attribute} instance
:canonical: duck.http.session.connector.SessionStorageConnector.instance
:value: >
   None

```{autodocx-docstring} duck.http.session.connector.SessionStorageConnector.instance
```

````

````{py:method} save() -> None
:canonical: duck.http.session.connector.SessionStorageConnector.save

```{autodocx-docstring} duck.http.session.connector.SessionStorageConnector.save
```

````

````{py:method} set_session(session_id: str, data: dict, expiry: int | float | None = None) -> None
:canonical: duck.http.session.connector.SessionStorageConnector.set_session

```{autodocx-docstring} duck.http.session.connector.SessionStorageConnector.set_session
```

````

````{py:method} update_session(session_id: str, data: dict) -> None
:canonical: duck.http.session.connector.SessionStorageConnector.update_session

```{autodocx-docstring} duck.http.session.connector.SessionStorageConnector.update_session
```

````

````{py:property} using_memory_backend
:canonical: duck.http.session.connector.SessionStorageConnector.using_memory_backend
:type: bool

```{autodocx-docstring} duck.http.session.connector.SessionStorageConnector.using_memory_backend
```

````

`````

````{py:exception} SessionStorageConnectorError()
:canonical: duck.http.session.connector.SessionStorageConnectorError

Bases: {py:obj}`Exception`

```{autodocx-docstring} duck.http.session.connector.SessionStorageConnectorError
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.http.session.connector.SessionStorageConnectorError.__init__
```

````

````{py:function} get_session_storage_connector()
:canonical: duck.http.session.connector.get_session_storage_connector

```{autodocx-docstring} duck.http.session.connector.get_session_storage_connector
```
````
