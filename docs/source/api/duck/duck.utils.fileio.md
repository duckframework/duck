# {py:mod}`duck.utils.fileio`

```{py:module} duck.utils.fileio
```

```{autodocx-docstring} duck.utils.fileio
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`AsyncFileIOStream <duck.utils.fileio.AsyncFileIOStream>`
  - ```{autodocx-docstring} duck.utils.fileio.AsyncFileIOStream
    :summary:
    ```
* - {py:obj}`FileIOStream <duck.utils.fileio.FileIOStream>`
  - ```{autodocx-docstring} duck.utils.fileio.FileIOStream
    :summary:
    ```
````

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`to_async_fileio_stream <duck.utils.fileio.to_async_fileio_stream>`
  - ```{autodocx-docstring} duck.utils.fileio.to_async_fileio_stream
    :summary:
    ```
````

### API

`````{py:class} AsyncFileIOStream(*args, **kwargs)
:canonical: duck.utils.fileio.AsyncFileIOStream

Bases: {py:obj}`duck.utils.fileio.FileIOStream`

```{autodocx-docstring} duck.utils.fileio.AsyncFileIOStream
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.utils.fileio.AsyncFileIOStream.__init__
```

````{py:method} __aenter__()
:canonical: duck.utils.fileio.AsyncFileIOStream.__aenter__
:async:

```{autodocx-docstring} duck.utils.fileio.AsyncFileIOStream.__aenter__
```

````

````{py:method} __aexit__(exc_type, exc, tb)
:canonical: duck.utils.fileio.AsyncFileIOStream.__aexit__
:async:

```{autodocx-docstring} duck.utils.fileio.AsyncFileIOStream.__aexit__
```

````

````{py:method} async_open()
:canonical: duck.utils.fileio.AsyncFileIOStream.async_open
:async:

```{autodocx-docstring} duck.utils.fileio.AsyncFileIOStream.async_open
```

````

````{py:method} close()
:canonical: duck.utils.fileio.AsyncFileIOStream.close
:async:

```{autodocx-docstring} duck.utils.fileio.AsyncFileIOStream.close
```

````

````{py:method} read(size: int = -1) -> bytes
:canonical: duck.utils.fileio.AsyncFileIOStream.read
:async:

```{autodocx-docstring} duck.utils.fileio.AsyncFileIOStream.read
```

````

````{py:method} write(data: bytes) -> int
:canonical: duck.utils.fileio.AsyncFileIOStream.write
:async:

```{autodocx-docstring} duck.utils.fileio.AsyncFileIOStream.write
```

````

`````

`````{py:class} FileIOStream(filepath: str, chunk_size: int = 2 * 1024 * 1024, open_now: bool = False, mode: str = 'rb')
:canonical: duck.utils.fileio.FileIOStream

Bases: {py:obj}`io.IOBase`

```{autodocx-docstring} duck.utils.fileio.FileIOStream
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.utils.fileio.FileIOStream.__init__
```

````{py:method} __del__()
:canonical: duck.utils.fileio.FileIOStream.__del__

```{autodocx-docstring} duck.utils.fileio.FileIOStream.__del__
```

````

````{py:attribute} __slots__
:canonical: duck.utils.fileio.FileIOStream.__slots__
:value: >
   None

```{autodocx-docstring} duck.utils.fileio.FileIOStream.__slots__
```

````

````{py:method} close()
:canonical: duck.utils.fileio.FileIOStream.close

```{autodocx-docstring} duck.utils.fileio.FileIOStream.close
```

````

````{py:method} is_open() -> bool
:canonical: duck.utils.fileio.FileIOStream.is_open

```{autodocx-docstring} duck.utils.fileio.FileIOStream.is_open
```

````

````{py:method} open()
:canonical: duck.utils.fileio.FileIOStream.open

```{autodocx-docstring} duck.utils.fileio.FileIOStream.open
```

````

````{py:method} raise_if_in_async_context(message: str)
:canonical: duck.utils.fileio.FileIOStream.raise_if_in_async_context

```{autodocx-docstring} duck.utils.fileio.FileIOStream.raise_if_in_async_context
```

````

````{py:method} read(size: int = -1) -> bytes
:canonical: duck.utils.fileio.FileIOStream.read

```{autodocx-docstring} duck.utils.fileio.FileIOStream.read
```

````

````{py:method} seek(offset: int, whence: int = os.SEEK_SET)
:canonical: duck.utils.fileio.FileIOStream.seek

```{autodocx-docstring} duck.utils.fileio.FileIOStream.seek
```

````

````{py:method} tell() -> int
:canonical: duck.utils.fileio.FileIOStream.tell

```{autodocx-docstring} duck.utils.fileio.FileIOStream.tell
```

````

````{py:method} write(data: bytes) -> int
:canonical: duck.utils.fileio.FileIOStream.write

```{autodocx-docstring} duck.utils.fileio.FileIOStream.write
```

````

`````

````{py:function} to_async_fileio_stream(fileio_stream: FileIOStream) -> AsyncFileIOStream
:canonical: duck.utils.fileio.to_async_fileio_stream

```{autodocx-docstring} duck.utils.fileio.to_async_fileio_stream
```
````
