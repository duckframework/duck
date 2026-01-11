# {py:mod}`duck.http.request_data`

```{py:module} duck.http.request_data
```

```{autodocx-docstring} duck.http.request_data
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`RawRequestData <duck.http.request_data.RawRequestData>`
  - ```{autodocx-docstring} duck.http.request_data.RawRequestData
    :summary:
    ```
* - {py:obj}`RequestData <duck.http.request_data.RequestData>`
  - ```{autodocx-docstring} duck.http.request_data.RequestData
    :summary:
    ```
````

### API

`````{py:class} RawRequestData(data: bytes)
:canonical: duck.http.request_data.RawRequestData

Bases: {py:obj}`duck.http.request_data.RequestData`

```{autodocx-docstring} duck.http.request_data.RawRequestData
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.http.request_data.RawRequestData.__init__
```

````{py:method} __repr__()
:canonical: duck.http.request_data.RawRequestData.__repr__

````

````{py:attribute} __slots__
:canonical: duck.http.request_data.RawRequestData.__slots__
:value: >
   ('data', 'request_store')

```{autodocx-docstring} duck.http.request_data.RawRequestData.__slots__
```

````

`````

`````{py:class} RequestData(headers: typing.Dict[str, str], content: bytes = b'')
:canonical: duck.http.request_data.RequestData

```{autodocx-docstring} duck.http.request_data.RequestData
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.http.request_data.RequestData.__init__
```

````{py:method} __repr__()
:canonical: duck.http.request_data.RequestData.__repr__

````

````{py:attribute} __slots__
:canonical: duck.http.request_data.RequestData.__slots__
:value: >
   ('headers', 'content', 'request_store')

```{autodocx-docstring} duck.http.request_data.RequestData.__slots__
```

````

`````
