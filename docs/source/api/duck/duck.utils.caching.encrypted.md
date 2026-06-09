# {py:mod}`duck.utils.caching.encrypted`

```{py:module} duck.utils.caching.encrypted
```

```{autodocx-docstring} duck.utils.caching.encrypted
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`EncryptedCache <duck.utils.caching.encrypted.EncryptedCache>`
  - ```{autodocx-docstring} duck.utils.caching.encrypted.EncryptedCache
    :summary:
    ```
* - {py:obj}`NaClEncryptor <duck.utils.caching.encrypted.NaClEncryptor>`
  - ```{autodocx-docstring} duck.utils.caching.encrypted.NaClEncryptor
    :summary:
    ```
````

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`generate_secret_key <duck.utils.caching.encrypted.generate_secret_key>`
  - ```{autodocx-docstring} duck.utils.caching.encrypted.generate_secret_key
    :summary:
    ```
* - {py:obj}`resolve_nacl_key <duck.utils.caching.encrypted.resolve_nacl_key>`
  - ```{autodocx-docstring} duck.utils.caching.encrypted.resolve_nacl_key
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`DUCK_NACL_DERIVE_KEY_ENV <duck.utils.caching.encrypted.DUCK_NACL_DERIVE_KEY_ENV>`
  - ```{autodocx-docstring} duck.utils.caching.encrypted.DUCK_NACL_DERIVE_KEY_ENV
    :summary:
    ```
* - {py:obj}`NACL_KEY_SIZE <duck.utils.caching.encrypted.NACL_KEY_SIZE>`
  - ```{autodocx-docstring} duck.utils.caching.encrypted.NACL_KEY_SIZE
    :summary:
    ```
* - {py:obj}`NONCE_SIZE <duck.utils.caching.encrypted.NONCE_SIZE>`
  - ```{autodocx-docstring} duck.utils.caching.encrypted.NONCE_SIZE
    :summary:
    ```
````

### API

````{py:data} DUCK_NACL_DERIVE_KEY_ENV
:canonical: duck.utils.caching.encrypted.DUCK_NACL_DERIVE_KEY_ENV
:value: >
   'DUCK_NACL_DERIVE_KEY'

```{autodocx-docstring} duck.utils.caching.encrypted.DUCK_NACL_DERIVE_KEY_ENV
```

````

`````{py:class} EncryptedCache(backend: duck.utils.caching.CacheBase, secret_key: bytes)
:canonical: duck.utils.caching.encrypted.EncryptedCache

Bases: {py:obj}`duck.utils.caching.CacheBase`

```{autodocx-docstring} duck.utils.caching.encrypted.EncryptedCache
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.utils.caching.encrypted.EncryptedCache.__init__
```

````{py:method} async_clear() -> None
:canonical: duck.utils.caching.encrypted.EncryptedCache.async_clear
:async:

```{autodocx-docstring} duck.utils.caching.encrypted.EncryptedCache.async_clear
```

````

````{py:method} async_delete(key: str) -> None
:canonical: duck.utils.caching.encrypted.EncryptedCache.async_delete
:async:

```{autodocx-docstring} duck.utils.caching.encrypted.EncryptedCache.async_delete
```

````

````{py:method} async_get(key: str, default: typing.Any = None) -> typing.Any
:canonical: duck.utils.caching.encrypted.EncryptedCache.async_get
:async:

```{autodocx-docstring} duck.utils.caching.encrypted.EncryptedCache.async_get
```

````

````{py:method} async_pop(key: str, default: typing.Any = MISSING) -> typing.Any
:canonical: duck.utils.caching.encrypted.EncryptedCache.async_pop
:async:

```{autodocx-docstring} duck.utils.caching.encrypted.EncryptedCache.async_pop
```

````

````{py:method} async_set(key: str, value: typing.Any, expiry: int | float | None = None) -> None
:canonical: duck.utils.caching.encrypted.EncryptedCache.async_set
:async:

```{autodocx-docstring} duck.utils.caching.encrypted.EncryptedCache.async_set
```

````

````{py:method} clear() -> None
:canonical: duck.utils.caching.encrypted.EncryptedCache.clear

```{autodocx-docstring} duck.utils.caching.encrypted.EncryptedCache.clear
```

````

````{py:method} close() -> None
:canonical: duck.utils.caching.encrypted.EncryptedCache.close

```{autodocx-docstring} duck.utils.caching.encrypted.EncryptedCache.close
```

````

````{py:method} delete(key: str) -> None
:canonical: duck.utils.caching.encrypted.EncryptedCache.delete

```{autodocx-docstring} duck.utils.caching.encrypted.EncryptedCache.delete
```

````

````{py:method} get(key: str, default: typing.Any = None) -> typing.Any
:canonical: duck.utils.caching.encrypted.EncryptedCache.get

```{autodocx-docstring} duck.utils.caching.encrypted.EncryptedCache.get
```

````

````{py:method} pop(key: str, default: typing.Any = MISSING) -> typing.Any
:canonical: duck.utils.caching.encrypted.EncryptedCache.pop

```{autodocx-docstring} duck.utils.caching.encrypted.EncryptedCache.pop
```

````

````{py:method} set(key: str, value: typing.Any, expiry: int | float | None = None) -> None
:canonical: duck.utils.caching.encrypted.EncryptedCache.set

```{autodocx-docstring} duck.utils.caching.encrypted.EncryptedCache.set
```

````

`````

````{py:data} NACL_KEY_SIZE
:canonical: duck.utils.caching.encrypted.NACL_KEY_SIZE
:value: >
   None

```{autodocx-docstring} duck.utils.caching.encrypted.NACL_KEY_SIZE
```

````

````{py:data} NONCE_SIZE
:canonical: duck.utils.caching.encrypted.NONCE_SIZE
:type: int
:value: >
   None

```{autodocx-docstring} duck.utils.caching.encrypted.NONCE_SIZE
```

````

`````{py:class} NaClEncryptor(secret_key: bytes)
:canonical: duck.utils.caching.encrypted.NaClEncryptor

```{autodocx-docstring} duck.utils.caching.encrypted.NaClEncryptor
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.utils.caching.encrypted.NaClEncryptor.__init__
```

````{py:method} decrypt(data: bytes) -> typing.Any
:canonical: duck.utils.caching.encrypted.NaClEncryptor.decrypt

```{autodocx-docstring} duck.utils.caching.encrypted.NaClEncryptor.decrypt
```

````

````{py:method} encrypt(value: typing.Any) -> bytes
:canonical: duck.utils.caching.encrypted.NaClEncryptor.encrypt

```{autodocx-docstring} duck.utils.caching.encrypted.NaClEncryptor.encrypt
```

````

`````

````{py:function} generate_secret_key() -> bytes
:canonical: duck.utils.caching.encrypted.generate_secret_key

```{autodocx-docstring} duck.utils.caching.encrypted.generate_secret_key
```
````

````{py:function} resolve_nacl_key(secret_key: bytes) -> bytes
:canonical: duck.utils.caching.encrypted.resolve_nacl_key

```{autodocx-docstring} duck.utils.caching.encrypted.resolve_nacl_key
```
````
