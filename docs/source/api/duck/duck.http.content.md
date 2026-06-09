# {py:mod}`duck.http.content`

```{py:module} duck.http.content
```

```{autodocx-docstring} duck.http.content
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`Content <duck.http.content.Content>`
  - ```{autodocx-docstring} duck.http.content.Content
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`COMPRESSION_ENCODING <duck.http.content.COMPRESSION_ENCODING>`
  - ```{autodocx-docstring} duck.http.content.COMPRESSION_ENCODING
    :summary:
    ```
* - {py:obj}`COMPRESSION_LEVEL <duck.http.content.COMPRESSION_LEVEL>`
  - ```{autodocx-docstring} duck.http.content.COMPRESSION_LEVEL
    :summary:
    ```
* - {py:obj}`COMPRESSION_MAX_SIZE <duck.http.content.COMPRESSION_MAX_SIZE>`
  - ```{autodocx-docstring} duck.http.content.COMPRESSION_MAX_SIZE
    :summary:
    ```
* - {py:obj}`COMPRESSION_MIMETYPES <duck.http.content.COMPRESSION_MIMETYPES>`
  - ```{autodocx-docstring} duck.http.content.COMPRESSION_MIMETYPES
    :summary:
    ```
* - {py:obj}`COMPRESSION_MIN_SIZE <duck.http.content.COMPRESSION_MIN_SIZE>`
  - ```{autodocx-docstring} duck.http.content.COMPRESSION_MIN_SIZE
    :summary:
    ```
* - {py:obj}`COMPRESS_STREAMING_RESPONSES <duck.http.content.COMPRESS_STREAMING_RESPONSES>`
  - ```{autodocx-docstring} duck.http.content.COMPRESS_STREAMING_RESPONSES
    :summary:
    ```
* - {py:obj}`CONTENT_COMPRESSION <duck.http.content.CONTENT_COMPRESSION>`
  - ```{autodocx-docstring} duck.http.content.CONTENT_COMPRESSION
    :summary:
    ```
````

### API

````{py:data} COMPRESSION_ENCODING
:canonical: duck.http.content.COMPRESSION_ENCODING
:value: >
   'get(...)'

```{autodocx-docstring} duck.http.content.COMPRESSION_ENCODING
```

````

````{py:data} COMPRESSION_LEVEL
:canonical: duck.http.content.COMPRESSION_LEVEL
:value: >
   'get(...)'

```{autodocx-docstring} duck.http.content.COMPRESSION_LEVEL
```

````

````{py:data} COMPRESSION_MAX_SIZE
:canonical: duck.http.content.COMPRESSION_MAX_SIZE
:value: >
   'get(...)'

```{autodocx-docstring} duck.http.content.COMPRESSION_MAX_SIZE
```

````

````{py:data} COMPRESSION_MIMETYPES
:canonical: duck.http.content.COMPRESSION_MIMETYPES
:value: >
   'get(...)'

```{autodocx-docstring} duck.http.content.COMPRESSION_MIMETYPES
```

````

````{py:data} COMPRESSION_MIN_SIZE
:canonical: duck.http.content.COMPRESSION_MIN_SIZE
:value: >
   'get(...)'

```{autodocx-docstring} duck.http.content.COMPRESSION_MIN_SIZE
```

````

````{py:data} COMPRESS_STREAMING_RESPONSES
:canonical: duck.http.content.COMPRESS_STREAMING_RESPONSES
:value: >
   'get(...)'

```{autodocx-docstring} duck.http.content.COMPRESS_STREAMING_RESPONSES
```

````

````{py:data} CONTENT_COMPRESSION
:canonical: duck.http.content.CONTENT_COMPRESSION
:value: >
   None

```{autodocx-docstring} duck.http.content.CONTENT_COMPRESSION
```

````

`````{py:class} Content(data: bytes = b'', filepath: str = None, content_type: str = None, encoding: str = 'identity', compression_min_size: int = COMPRESSION_MIN_SIZE, compression_max_size: int = COMPRESSION_MAX_SIZE, compression_level: int = COMPRESSION_LEVEL, compression_mimetypes: list = COMPRESSION_MIMETYPES, suppress_errors: bool = False, auto_read_file: bool = True)
:canonical: duck.http.content.Content

```{autodocx-docstring} duck.http.content.Content
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.http.content.Content.__init__
```

````{py:method} __repr__()
:canonical: duck.http.content.Content.__repr__

````

````{py:attribute} __slots__
:canonical: duck.http.content.Content.__slots__
:value: >
   ('_Content__data', '_Content__filepath', '_Content__encoding', '_Content__content_type', '_force_siz...

```{autodocx-docstring} duck.http.content.Content.__slots__
```

````

````{py:method} _compress(data: bytes, encoding: str, **kwargs) -> typing.Tuple[bytes, bool]
:canonical: duck.http.content.Content._compress

```{autodocx-docstring} duck.http.content.Content._compress
```

````

````{py:method} _decompress(data: bytes) -> typing.Tuple[bytes, bool]
:canonical: duck.http.content.Content._decompress

```{autodocx-docstring} duck.http.content.Content._decompress
```

````

````{py:method} compress(encoding: str, **kwargs) -> bool
:canonical: duck.http.content.Content.compress

```{autodocx-docstring} duck.http.content.Content.compress
```

````

````{py:property} compressed
:canonical: duck.http.content.Content.compressed

```{autodocx-docstring} duck.http.content.Content.compressed
```

````

````{py:property} content_type
:canonical: duck.http.content.Content.content_type
:type: str

```{autodocx-docstring} duck.http.content.Content.content_type
```

````

````{py:method} correct_encoding()
:canonical: duck.http.content.Content.correct_encoding

```{autodocx-docstring} duck.http.content.Content.correct_encoding
```

````

````{py:property} data
:canonical: duck.http.content.Content.data

```{autodocx-docstring} duck.http.content.Content.data
```

````

````{py:method} decompress()
:canonical: duck.http.content.Content.decompress

```{autodocx-docstring} duck.http.content.Content.decompress
```

````

````{py:property} encoding
:canonical: duck.http.content.Content.encoding
:type: str

```{autodocx-docstring} duck.http.content.Content.encoding
```

````

````{py:property} filepath
:canonical: duck.http.content.Content.filepath
:type: str

```{autodocx-docstring} duck.http.content.Content.filepath
```

````

````{py:method} force_set_data(data)
:canonical: duck.http.content.Content.force_set_data

```{autodocx-docstring} duck.http.content.Content.force_set_data
```

````

````{py:method} mimetype_supported(mimetype: str) -> bool
:canonical: duck.http.content.Content.mimetype_supported

```{autodocx-docstring} duck.http.content.Content.mimetype_supported
```

````

````{py:method} parse_type(content_type=None)
:canonical: duck.http.content.Content.parse_type

```{autodocx-docstring} duck.http.content.Content.parse_type
```

````

````{py:property} raw
:canonical: duck.http.content.Content.raw

```{autodocx-docstring} duck.http.content.Content.raw
```

````

````{py:method} remove_fake_size() -> None
:canonical: duck.http.content.Content.remove_fake_size

```{autodocx-docstring} duck.http.content.Content.remove_fake_size
```

````

````{py:method} set_content(data: bytes = b'', filepath: str = None, content_type=None)
:canonical: duck.http.content.Content.set_content

```{autodocx-docstring} duck.http.content.Content.set_content
```

````

````{py:method} set_fake_size(size: int) -> None
:canonical: duck.http.content.Content.set_fake_size

```{autodocx-docstring} duck.http.content.Content.set_fake_size
```

````

````{py:property} size
:canonical: duck.http.content.Content.size
:type: int

```{autodocx-docstring} duck.http.content.Content.size
```

````

`````
