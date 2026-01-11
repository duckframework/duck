# {py:mod}`duck.http.fileuploads.handlers`

```{py:module} duck.http.fileuploads.handlers
```

```{autodocx-docstring} duck.http.fileuploads.handlers
:allowtitles:
```

## Package Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`BaseFileUpload <duck.http.fileuploads.handlers.BaseFileUpload>`
  - ```{autodocx-docstring} duck.http.fileuploads.handlers.BaseFileUpload
    :summary:
    ```
* - {py:obj}`PersistentFileUpload <duck.http.fileuploads.handlers.PersistentFileUpload>`
  - ```{autodocx-docstring} duck.http.fileuploads.handlers.PersistentFileUpload
    :summary:
    ```
* - {py:obj}`TemporaryFileUpload <duck.http.fileuploads.handlers.TemporaryFileUpload>`
  - ```{autodocx-docstring} duck.http.fileuploads.handlers.TemporaryFileUpload
    :summary:
    ```
````

### API

`````{py:class} BaseFileUpload(filename: str, initial_bytes: bytes = b'', **kw)
:canonical: duck.http.fileuploads.handlers.BaseFileUpload

Bases: {py:obj}`io.BytesIO`

```{autodocx-docstring} duck.http.fileuploads.handlers.BaseFileUpload
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.http.fileuploads.handlers.BaseFileUpload.__init__
```

````{py:method} __repr__()
:canonical: duck.http.fileuploads.handlers.BaseFileUpload.__repr__

````

````{py:method} getsize()
:canonical: duck.http.fileuploads.handlers.BaseFileUpload.getsize

```{autodocx-docstring} duck.http.fileuploads.handlers.BaseFileUpload.getsize
```

````

````{py:method} guess_mimetype() -> typing.Optional[str]
:canonical: duck.http.fileuploads.handlers.BaseFileUpload.guess_mimetype

```{autodocx-docstring} duck.http.fileuploads.handlers.BaseFileUpload.guess_mimetype
```

````

````{py:method} save()
:canonical: duck.http.fileuploads.handlers.BaseFileUpload.save
:abstractmethod:

```{autodocx-docstring} duck.http.fileuploads.handlers.BaseFileUpload.save
```

````

````{py:method} save_to_file(filepath: str)
:canonical: duck.http.fileuploads.handlers.BaseFileUpload.save_to_file

```{autodocx-docstring} duck.http.fileuploads.handlers.BaseFileUpload.save_to_file
```

````

````{py:method} verify()
:canonical: duck.http.fileuploads.handlers.BaseFileUpload.verify

```{autodocx-docstring} duck.http.fileuploads.handlers.BaseFileUpload.verify
```

````

`````

````{py:exception} FileUploadError()
:canonical: duck.http.fileuploads.handlers.FileUploadError

Bases: {py:obj}`Exception`

```{autodocx-docstring} duck.http.fileuploads.handlers.FileUploadError
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.http.fileuploads.handlers.FileUploadError.__init__
```

````

````{py:exception} FileVerificationError()
:canonical: duck.http.fileuploads.handlers.FileVerificationError

Bases: {py:obj}`duck.http.fileuploads.handlers.FileUploadError`

```{autodocx-docstring} duck.http.fileuploads.handlers.FileVerificationError
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.http.fileuploads.handlers.FileVerificationError.__init__
```

````

`````{py:class} PersistentFileUpload(filename: str, initial_bytes: bytes = b'', directory: str = SETTINGS['FILE_UPLOAD_DIR'], overwrite_existing_file=True, **kw)
:canonical: duck.http.fileuploads.handlers.PersistentFileUpload

Bases: {py:obj}`duck.http.fileuploads.handlers.BaseFileUpload`

```{autodocx-docstring} duck.http.fileuploads.handlers.PersistentFileUpload
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.http.fileuploads.handlers.PersistentFileUpload.__init__
```

````{py:method} save()
:canonical: duck.http.fileuploads.handlers.PersistentFileUpload.save

```{autodocx-docstring} duck.http.fileuploads.handlers.PersistentFileUpload.save
```

````

````{py:method} save_to_file()
:canonical: duck.http.fileuploads.handlers.PersistentFileUpload.save_to_file

```{autodocx-docstring} duck.http.fileuploads.handlers.PersistentFileUpload.save_to_file
```

````

`````

`````{py:class} TemporaryFileUpload(filename: str, initial_bytes: bytes = b'', **kw)
:canonical: duck.http.fileuploads.handlers.TemporaryFileUpload

Bases: {py:obj}`duck.http.fileuploads.handlers.BaseFileUpload`

```{autodocx-docstring} duck.http.fileuploads.handlers.TemporaryFileUpload
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.http.fileuploads.handlers.TemporaryFileUpload.__init__
```

````{py:method} save()
:canonical: duck.http.fileuploads.handlers.TemporaryFileUpload.save

```{autodocx-docstring} duck.http.fileuploads.handlers.TemporaryFileUpload.save
```

````

`````
