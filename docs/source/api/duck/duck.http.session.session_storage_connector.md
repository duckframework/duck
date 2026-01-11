# {py:mod}`duck.http.session.session_storage_connector`

```{py:module} duck.http.session.session_storage_connector
```

```{autodocx-docstring} duck.http.session.session_storage_connector
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`SessionStorageConnector <duck.http.session.session_storage_connector.SessionStorageConnector>`
  - ```{autodocx-docstring} duck.http.session.session_storage_connector.SessionStorageConnector
    :summary:
    ```
````

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`get_session_storage_connector <duck.http.session.session_storage_connector.get_session_storage_connector>`
  - ```{autodocx-docstring} duck.http.session.session_storage_connector.get_session_storage_connector
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`globals <duck.http.session.session_storage_connector.globals>`
  - ```{autodocx-docstring} duck.http.session.session_storage_connector.globals
    :summary:
    ```
````

### API

```{py:exception} NonPersistentStorageError()
:canonical: duck.http.session.session_storage_connector.NonPersistentStorageError

Bases: {py:obj}`Exception`

```

`````{py:class} SessionStorageConnector(session_storage_cls: typing.Callable)
:canonical: duck.http.session.session_storage_connector.SessionStorageConnector

```{autodocx-docstring} duck.http.session.session_storage_connector.SessionStorageConnector
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.http.session.session_storage_connector.SessionStorageConnector.__init__
```

````{py:method} __new__(session_storage_cls: duck.utils.caching.CacheBase)
:canonical: duck.http.session.session_storage_connector.SessionStorageConnector.__new__

```{autodocx-docstring} duck.http.session.session_storage_connector.SessionStorageConnector.__new__
```

````

````{py:method} clear_all_sessions()
:canonical: duck.http.session.session_storage_connector.SessionStorageConnector.clear_all_sessions

```{autodocx-docstring} duck.http.session.session_storage_connector.SessionStorageConnector.clear_all_sessions
```

````

````{py:method} close()
:canonical: duck.http.session.session_storage_connector.SessionStorageConnector.close

```{autodocx-docstring} duck.http.session.session_storage_connector.SessionStorageConnector.close
```

````

````{py:method} delete_session(session_id: str)
:canonical: duck.http.session.session_storage_connector.SessionStorageConnector.delete_session

```{autodocx-docstring} duck.http.session.session_storage_connector.SessionStorageConnector.delete_session
```

````

````{py:method} generate_session_id() -> str
:canonical: duck.http.session.session_storage_connector.SessionStorageConnector.generate_session_id
:staticmethod:

```{autodocx-docstring} duck.http.session.session_storage_connector.SessionStorageConnector.generate_session_id
```

````

````{py:method} get_session(session_id: str)
:canonical: duck.http.session.session_storage_connector.SessionStorageConnector.get_session

```{autodocx-docstring} duck.http.session.session_storage_connector.SessionStorageConnector.get_session
```

````

````{py:method} save()
:canonical: duck.http.session.session_storage_connector.SessionStorageConnector.save

```{autodocx-docstring} duck.http.session.session_storage_connector.SessionStorageConnector.save
```

````

````{py:method} set_session(session_id: str, data: dict, expiry: int | float = None)
:canonical: duck.http.session.session_storage_connector.SessionStorageConnector.set_session

```{autodocx-docstring} duck.http.session.session_storage_connector.SessionStorageConnector.set_session
```

````

````{py:method} update_session(session_id: str, data: dict)
:canonical: duck.http.session.session_storage_connector.SessionStorageConnector.update_session

```{autodocx-docstring} duck.http.session.session_storage_connector.SessionStorageConnector.update_session
```

````

`````

````{py:function} get_session_storage_connector()
:canonical: duck.http.session.session_storage_connector.get_session_storage_connector

```{autodocx-docstring} duck.http.session.session_storage_connector.get_session_storage_connector
```
````

````{py:data} globals
:canonical: duck.http.session.session_storage_connector.globals
:value: >
   'import_module_once(...)'

```{autodocx-docstring} duck.http.session.session_storage_connector.globals
```

````
