# {py:mod}`duck.contrib.auth.helpers`

```{py:module} duck.contrib.auth.helpers
```

```{autodocx-docstring} duck.contrib.auth.helpers
:allowtitles:
```

## Module Contents

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`async_authenticate <duck.contrib.auth.helpers.async_authenticate>`
  - ```{autodocx-docstring} duck.contrib.auth.helpers.async_authenticate
    :summary:
    ```
* - {py:obj}`async_get_user_from_jwt <duck.contrib.auth.helpers.async_get_user_from_jwt>`
  - ```{autodocx-docstring} duck.contrib.auth.helpers.async_get_user_from_jwt
    :summary:
    ```
* - {py:obj}`async_get_user_from_session <duck.contrib.auth.helpers.async_get_user_from_session>`
  - ```{autodocx-docstring} duck.contrib.auth.helpers.async_get_user_from_session
    :summary:
    ```
* - {py:obj}`async_login <duck.contrib.auth.helpers.async_login>`
  - ```{autodocx-docstring} duck.contrib.auth.helpers.async_login
    :summary:
    ```
* - {py:obj}`async_logout <duck.contrib.auth.helpers.async_logout>`
  - ```{autodocx-docstring} duck.contrib.auth.helpers.async_logout
    :summary:
    ```
* - {py:obj}`authenticate <duck.contrib.auth.helpers.authenticate>`
  - ```{autodocx-docstring} duck.contrib.auth.helpers.authenticate
    :summary:
    ```
* - {py:obj}`get_user_from_jwt <duck.contrib.auth.helpers.get_user_from_jwt>`
  - ```{autodocx-docstring} duck.contrib.auth.helpers.get_user_from_jwt
    :summary:
    ```
* - {py:obj}`get_user_from_session <duck.contrib.auth.helpers.get_user_from_session>`
  - ```{autodocx-docstring} duck.contrib.auth.helpers.get_user_from_session
    :summary:
    ```
* - {py:obj}`login <duck.contrib.auth.helpers.login>`
  - ```{autodocx-docstring} duck.contrib.auth.helpers.login
    :summary:
    ```
* - {py:obj}`logout <duck.contrib.auth.helpers.logout>`
  - ```{autodocx-docstring} duck.contrib.auth.helpers.logout
    :summary:
    ```
* - {py:obj}`set_default_auth_backend <duck.contrib.auth.helpers.set_default_auth_backend>`
  - ```{autodocx-docstring} duck.contrib.auth.helpers.set_default_auth_backend
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`BACKEND_KEY <duck.contrib.auth.helpers.BACKEND_KEY>`
  - ```{autodocx-docstring} duck.contrib.auth.helpers.BACKEND_KEY
    :summary:
    ```
* - {py:obj}`DEFAULT_AUTH_BACKEND <duck.contrib.auth.helpers.DEFAULT_AUTH_BACKEND>`
  - ```{autodocx-docstring} duck.contrib.auth.helpers.DEFAULT_AUTH_BACKEND
    :summary:
    ```
* - {py:obj}`SUPPORTED_BACKENDS <duck.contrib.auth.helpers.SUPPORTED_BACKENDS>`
  - ```{autodocx-docstring} duck.contrib.auth.helpers.SUPPORTED_BACKENDS
    :summary:
    ```
* - {py:obj}`USER_ID_KEY <duck.contrib.auth.helpers.USER_ID_KEY>`
  - ```{autodocx-docstring} duck.contrib.auth.helpers.USER_ID_KEY
    :summary:
    ```
````

### API

````{py:data} BACKEND_KEY
:canonical: duck.contrib.auth.helpers.BACKEND_KEY
:value: >
   '_auth_backend'

```{autodocx-docstring} duck.contrib.auth.helpers.BACKEND_KEY
```

````

````{py:data} DEFAULT_AUTH_BACKEND
:canonical: duck.contrib.auth.helpers.DEFAULT_AUTH_BACKEND
:value: >
   'session'

```{autodocx-docstring} duck.contrib.auth.helpers.DEFAULT_AUTH_BACKEND
```

````

````{py:data} SUPPORTED_BACKENDS
:canonical: duck.contrib.auth.helpers.SUPPORTED_BACKENDS
:value: >
   ('session', 'jwt')

```{autodocx-docstring} duck.contrib.auth.helpers.SUPPORTED_BACKENDS
```

````

````{py:data} USER_ID_KEY
:canonical: duck.contrib.auth.helpers.USER_ID_KEY
:value: >
   '_auth_user_id'

```{autodocx-docstring} duck.contrib.auth.helpers.USER_ID_KEY
```

````

````{py:function} async_authenticate(request: typing.Any, username: str, password: str) -> typing.Any
:canonical: duck.contrib.auth.helpers.async_authenticate
:async:

```{autodocx-docstring} duck.contrib.auth.helpers.async_authenticate
```
````

````{py:function} async_get_user_from_jwt(request: typing.Any) -> typing.Any | None
:canonical: duck.contrib.auth.helpers.async_get_user_from_jwt
:async:

```{autodocx-docstring} duck.contrib.auth.helpers.async_get_user_from_jwt
```
````

````{py:function} async_get_user_from_session(request: typing.Any) -> typing.Any | None
:canonical: duck.contrib.auth.helpers.async_get_user_from_session
:async:

```{autodocx-docstring} duck.contrib.auth.helpers.async_get_user_from_session
```
````

````{py:function} async_login(request: typing.Any, user: typing.Any, backend: str | None = None) -> None
:canonical: duck.contrib.auth.helpers.async_login
:async:

```{autodocx-docstring} duck.contrib.auth.helpers.async_login
```
````

````{py:function} async_logout(request: typing.Any, backend: str | None = None) -> None
:canonical: duck.contrib.auth.helpers.async_logout
:async:

```{autodocx-docstring} duck.contrib.auth.helpers.async_logout
```
````

````{py:function} authenticate(request: typing.Any, username: str, password: str) -> typing.Any
:canonical: duck.contrib.auth.helpers.authenticate

```{autodocx-docstring} duck.contrib.auth.helpers.authenticate
```
````

````{py:function} get_user_from_jwt(request: typing.Any) -> typing.Any | None
:canonical: duck.contrib.auth.helpers.get_user_from_jwt

```{autodocx-docstring} duck.contrib.auth.helpers.get_user_from_jwt
```
````

````{py:function} get_user_from_session(request: typing.Any) -> typing.Any | None
:canonical: duck.contrib.auth.helpers.get_user_from_session

```{autodocx-docstring} duck.contrib.auth.helpers.get_user_from_session
```
````

````{py:function} login(request: typing.Any, user: typing.Any, backend: str | None = None) -> None
:canonical: duck.contrib.auth.helpers.login

```{autodocx-docstring} duck.contrib.auth.helpers.login
```
````

````{py:function} logout(request: typing.Any, backend: str | None = None) -> None
:canonical: duck.contrib.auth.helpers.logout

```{autodocx-docstring} duck.contrib.auth.helpers.logout
```
````

````{py:function} set_default_auth_backend(backend: str) -> None
:canonical: duck.contrib.auth.helpers.set_default_auth_backend

```{autodocx-docstring} duck.contrib.auth.helpers.set_default_auth_backend
```
````
