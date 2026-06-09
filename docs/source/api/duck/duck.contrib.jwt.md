# {py:mod}`duck.contrib.jwt`

```{py:module} duck.contrib.jwt
```

```{autodocx-docstring} duck.contrib.jwt
:allowtitles:
```

## Package Contents

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`decode_token <duck.contrib.jwt.decode_token>`
  - ```{autodocx-docstring} duck.contrib.jwt.decode_token
    :summary:
    ```
* - {py:obj}`encode_token <duck.contrib.jwt.encode_token>`
  - ```{autodocx-docstring} duck.contrib.jwt.encode_token
    :summary:
    ```
* - {py:obj}`get_access_lifetime <duck.contrib.jwt.get_access_lifetime>`
  - ```{autodocx-docstring} duck.contrib.jwt.get_access_lifetime
    :summary:
    ```
* - {py:obj}`get_algorithm <duck.contrib.jwt.get_algorithm>`
  - ```{autodocx-docstring} duck.contrib.jwt.get_algorithm
    :summary:
    ```
* - {py:obj}`get_jwt_lib <duck.contrib.jwt.get_jwt_lib>`
  - ```{autodocx-docstring} duck.contrib.jwt.get_jwt_lib
    :summary:
    ```
* - {py:obj}`get_refresh_lifetime <duck.contrib.jwt.get_refresh_lifetime>`
  - ```{autodocx-docstring} duck.contrib.jwt.get_refresh_lifetime
    :summary:
    ```
* - {py:obj}`get_secret_key <duck.contrib.jwt.get_secret_key>`
  - ```{autodocx-docstring} duck.contrib.jwt.get_secret_key
    :summary:
    ```
* - {py:obj}`issue_token_pair <duck.contrib.jwt.issue_token_pair>`
  - ```{autodocx-docstring} duck.contrib.jwt.issue_token_pair
    :summary:
    ```
````

### API

````{py:exception} JWTError()
:canonical: duck.contrib.jwt.JWTError

Bases: {py:obj}`Exception`

```{autodocx-docstring} duck.contrib.jwt.JWTError
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.contrib.jwt.JWTError.__init__
```

````

````{py:exception} JWTExpired()
:canonical: duck.contrib.jwt.JWTExpired

Bases: {py:obj}`duck.contrib.jwt.JWTError`

```{autodocx-docstring} duck.contrib.jwt.JWTExpired
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.contrib.jwt.JWTExpired.__init__
```

````

````{py:exception} JWTInvalid()
:canonical: duck.contrib.jwt.JWTInvalid

Bases: {py:obj}`duck.contrib.jwt.JWTError`

```{autodocx-docstring} duck.contrib.jwt.JWTInvalid
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.contrib.jwt.JWTInvalid.__init__
```

````

````{py:function} decode_token(token: str, verify_expiry: bool = True) -> typing.Dict[str, typing.Any]
:canonical: duck.contrib.jwt.decode_token

```{autodocx-docstring} duck.contrib.jwt.decode_token
```
````

````{py:function} encode_token(payload: dict[str, typing.Any], token_type: str = 'access') -> str
:canonical: duck.contrib.jwt.encode_token

```{autodocx-docstring} duck.contrib.jwt.encode_token
```
````

````{py:function} get_access_lifetime() -> datetime.timedelta
:canonical: duck.contrib.jwt.get_access_lifetime

```{autodocx-docstring} duck.contrib.jwt.get_access_lifetime
```
````

````{py:function} get_algorithm() -> str
:canonical: duck.contrib.jwt.get_algorithm

```{autodocx-docstring} duck.contrib.jwt.get_algorithm
```
````

````{py:function} get_jwt_lib()
:canonical: duck.contrib.jwt.get_jwt_lib

```{autodocx-docstring} duck.contrib.jwt.get_jwt_lib
```
````

````{py:function} get_refresh_lifetime() -> float
:canonical: duck.contrib.jwt.get_refresh_lifetime

```{autodocx-docstring} duck.contrib.jwt.get_refresh_lifetime
```
````

````{py:function} get_secret_key() -> str
:canonical: duck.contrib.jwt.get_secret_key

```{autodocx-docstring} duck.contrib.jwt.get_secret_key
```
````

````{py:function} issue_token_pair(payload: dict[str, typing.Any] | None = None) -> dict[str, str]
:canonical: duck.contrib.jwt.issue_token_pair

```{autodocx-docstring} duck.contrib.jwt.issue_token_pair
```
````
