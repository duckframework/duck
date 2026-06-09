# {py:mod}`duck.secrets`

```{py:module} duck.secrets
```

```{autodocx-docstring} duck.secrets
:allowtitles:
```

## Module Contents

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`generate_ascii_secret <duck.secrets.generate_ascii_secret>`
  - ```{autodocx-docstring} duck.secrets.generate_ascii_secret
    :summary:
    ```
* - {py:obj}`generate_secret <duck.secrets.generate_secret>`
  - ```{autodocx-docstring} duck.secrets.generate_secret
    :summary:
    ```
* - {py:obj}`get_or_create_secret <duck.secrets.get_or_create_secret>`
  - ```{autodocx-docstring} duck.secrets.get_or_create_secret
    :summary:
    ```
* - {py:obj}`secure_mkdir <duck.secrets.secure_mkdir>`
  - ```{autodocx-docstring} duck.secrets.secure_mkdir
    :summary:
    ```
* - {py:obj}`secure_read <duck.secrets.secure_read>`
  - ```{autodocx-docstring} duck.secrets.secure_read
    :summary:
    ```
* - {py:obj}`secure_write <duck.secrets.secure_write>`
  - ```{autodocx-docstring} duck.secrets.secure_write
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`IS_WINDOWS <duck.secrets.IS_WINDOWS>`
  - ```{autodocx-docstring} duck.secrets.IS_WINDOWS
    :summary:
    ```
* - {py:obj}`SECRETS_DIR <duck.secrets.SECRETS_DIR>`
  - ```{autodocx-docstring} duck.secrets.SECRETS_DIR
    :summary:
    ```
* - {py:obj}`SECRET_DIR_MODE <duck.secrets.SECRET_DIR_MODE>`
  - ```{autodocx-docstring} duck.secrets.SECRET_DIR_MODE
    :summary:
    ```
* - {py:obj}`SECRET_FILE_MODE <duck.secrets.SECRET_FILE_MODE>`
  - ```{autodocx-docstring} duck.secrets.SECRET_FILE_MODE
    :summary:
    ```
````

### API

````{py:data} IS_WINDOWS
:canonical: duck.secrets.IS_WINDOWS
:value: >
   None

```{autodocx-docstring} duck.secrets.IS_WINDOWS
```

````

````{py:data} SECRETS_DIR
:canonical: duck.secrets.SECRETS_DIR
:value: >
   'Path(...)'

```{autodocx-docstring} duck.secrets.SECRETS_DIR
```

````

````{py:data} SECRET_DIR_MODE
:canonical: duck.secrets.SECRET_DIR_MODE
:value: >
   None

```{autodocx-docstring} duck.secrets.SECRET_DIR_MODE
```

````

````{py:data} SECRET_FILE_MODE
:canonical: duck.secrets.SECRET_FILE_MODE
:value: >
   None

```{autodocx-docstring} duck.secrets.SECRET_FILE_MODE
```

````

````{py:function} generate_ascii_secret(length: int = 16) -> str
:canonical: duck.secrets.generate_ascii_secret

```{autodocx-docstring} duck.secrets.generate_ascii_secret
```
````

````{py:function} generate_secret() -> str
:canonical: duck.secrets.generate_secret

```{autodocx-docstring} duck.secrets.generate_secret
```
````

````{py:function} get_or_create_secret(name: str, generator: callable = generate_secret) -> str
:canonical: duck.secrets.get_or_create_secret

```{autodocx-docstring} duck.secrets.get_or_create_secret
```
````

````{py:function} secure_mkdir(path: pathlib.Path) -> None
:canonical: duck.secrets.secure_mkdir

```{autodocx-docstring} duck.secrets.secure_mkdir
```
````

````{py:function} secure_read(path: pathlib.Path) -> str
:canonical: duck.secrets.secure_read

```{autodocx-docstring} duck.secrets.secure_read
```
````

````{py:function} secure_write(path: pathlib.Path, secret: str) -> None
:canonical: duck.secrets.secure_write

```{autodocx-docstring} duck.secrets.secure_write
```
````
