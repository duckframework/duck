# {py:mod}`duck.http.response_payload`

```{py:module} duck.http.response_payload
```

```{autodocx-docstring} duck.http.response_payload
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`BaseResponsePayload <duck.http.response_payload.BaseResponsePayload>`
  - ```{autodocx-docstring} duck.http.response_payload.BaseResponsePayload
    :summary:
    ```
* - {py:obj}`HttpResponsePayload <duck.http.response_payload.HttpResponsePayload>`
  - ```{autodocx-docstring} duck.http.response_payload.HttpResponsePayload
    :summary:
    ```
* - {py:obj}`SimpleHttpResponsePayload <duck.http.response_payload.SimpleHttpResponsePayload>`
  - ```{autodocx-docstring} duck.http.response_payload.SimpleHttpResponsePayload
    :summary:
    ```
````

### API

`````{py:class} BaseResponsePayload
:canonical: duck.http.response_payload.BaseResponsePayload

```{autodocx-docstring} duck.http.response_payload.BaseResponsePayload
```

````{py:property} cookies
:canonical: duck.http.response_payload.BaseResponsePayload.cookies
:type: http.cookies.SimpleCookie

```{autodocx-docstring} duck.http.response_payload.BaseResponsePayload.cookies
```

````

````{py:method} delete_cookie(key: str, path: str = '/', domain: typing.Optional[str] = None) -> None
:canonical: duck.http.response_payload.BaseResponsePayload.delete_cookie

```{autodocx-docstring} duck.http.response_payload.BaseResponsePayload.delete_cookie
```

````

````{py:method} get_all_cookies() -> typing.Dict[str, str]
:canonical: duck.http.response_payload.BaseResponsePayload.get_all_cookies

```{autodocx-docstring} duck.http.response_payload.BaseResponsePayload.get_all_cookies
```

````

````{py:method} get_cookie(name: str) -> str
:canonical: duck.http.response_payload.BaseResponsePayload.get_cookie

```{autodocx-docstring} duck.http.response_payload.BaseResponsePayload.get_cookie
```

````

````{py:method} get_cookie_obj(name: str) -> typing.Optional[http.cookies.Morsel]
:canonical: duck.http.response_payload.BaseResponsePayload.get_cookie_obj

```{autodocx-docstring} duck.http.response_payload.BaseResponsePayload.get_cookie_obj
```

````

````{py:method} get_cookie_str(name: str, include_cookie_name: bool = True) -> str
:canonical: duck.http.response_payload.BaseResponsePayload.get_cookie_str

```{autodocx-docstring} duck.http.response_payload.BaseResponsePayload.get_cookie_str
```

````

````{py:property} raw
:canonical: duck.http.response_payload.BaseResponsePayload.raw
:abstractmethod:

```{autodocx-docstring} duck.http.response_payload.BaseResponsePayload.raw
```

````

````{py:method} set_cookie(key: str, value: str = '', domain: typing.Optional[str] = None, path: str = '/', max_age: typing.Optional[typing.Union[int, datetime.timedelta]] = None, expires: typing.Optional[typing.Union[datetime.datetime, str]] = None, secure: bool = False, httponly: bool = False, samesite: typing.Optional[str] = 'Lax') -> None
:canonical: duck.http.response_payload.BaseResponsePayload.set_cookie

```{autodocx-docstring} duck.http.response_payload.BaseResponsePayload.set_cookie
```

````

````{py:method} set_multiple_cookies(cookies: typing.Dict[str, typing.Dict[str, typing.Any]]) -> None
:canonical: duck.http.response_payload.BaseResponsePayload.set_multiple_cookies

```{autodocx-docstring} duck.http.response_payload.BaseResponsePayload.set_multiple_cookies
```

````

`````

`````{py:class} HttpResponsePayload(**kwargs)
:canonical: duck.http.response_payload.HttpResponsePayload

Bases: {py:obj}`duck.http.response_payload.BaseResponsePayload`

```{autodocx-docstring} duck.http.response_payload.HttpResponsePayload
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.http.response_payload.HttpResponsePayload.__init__
```

````{py:method} __repr__()
:canonical: duck.http.response_payload.HttpResponsePayload.__repr__

````

````{py:method} get_header(header: str, default_value=None) -> typing.Optional[str]
:canonical: duck.http.response_payload.HttpResponsePayload.get_header

```{autodocx-docstring} duck.http.response_payload.HttpResponsePayload.get_header
```

````

````{py:method} parse_status(code: int, msg: str = None, explanation: str = None)
:canonical: duck.http.response_payload.HttpResponsePayload.parse_status

```{autodocx-docstring} duck.http.response_payload.HttpResponsePayload.parse_status
```

````

````{py:property} raw
:canonical: duck.http.response_payload.HttpResponsePayload.raw
:type: bytes

```{autodocx-docstring} duck.http.response_payload.HttpResponsePayload.raw
```

````

````{py:method} set_header(header: str, value: str)
:canonical: duck.http.response_payload.HttpResponsePayload.set_header

```{autodocx-docstring} duck.http.response_payload.HttpResponsePayload.set_header
```

````

`````

`````{py:class} SimpleHttpResponsePayload(topheader: str = '', headers: typing.Optional[typing.Dict] = None)
:canonical: duck.http.response_payload.SimpleHttpResponsePayload

Bases: {py:obj}`duck.http.response_payload.BaseResponsePayload`

```{autodocx-docstring} duck.http.response_payload.SimpleHttpResponsePayload
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.http.response_payload.SimpleHttpResponsePayload.__init__
```

````{py:method} __repr__()
:canonical: duck.http.response_payload.SimpleHttpResponsePayload.__repr__

````

````{py:property} explanation
:canonical: duck.http.response_payload.SimpleHttpResponsePayload.explanation
:type: str

```{autodocx-docstring} duck.http.response_payload.SimpleHttpResponsePayload.explanation
```

````

````{py:method} get_header(header: str, default_value=None) -> typing.Optional[str]
:canonical: duck.http.response_payload.SimpleHttpResponsePayload.get_header

```{autodocx-docstring} duck.http.response_payload.SimpleHttpResponsePayload.get_header
```

````

````{py:property} http_version
:canonical: duck.http.response_payload.SimpleHttpResponsePayload.http_version
:type: str

```{autodocx-docstring} duck.http.response_payload.SimpleHttpResponsePayload.http_version
```

````

````{py:property} raw
:canonical: duck.http.response_payload.SimpleHttpResponsePayload.raw
:type: bytes

```{autodocx-docstring} duck.http.response_payload.SimpleHttpResponsePayload.raw
```

````

````{py:method} set_header(header: str, value: str)
:canonical: duck.http.response_payload.SimpleHttpResponsePayload.set_header

```{autodocx-docstring} duck.http.response_payload.SimpleHttpResponsePayload.set_header
```

````

````{py:method} set_topheader(topheader: str)
:canonical: duck.http.response_payload.SimpleHttpResponsePayload.set_topheader

```{autodocx-docstring} duck.http.response_payload.SimpleHttpResponsePayload.set_topheader
```

````

````{py:property} status_code
:canonical: duck.http.response_payload.SimpleHttpResponsePayload.status_code
:type: int

```{autodocx-docstring} duck.http.response_payload.SimpleHttpResponsePayload.status_code
```

````

````{py:property} status_message
:canonical: duck.http.response_payload.SimpleHttpResponsePayload.status_message
:type: str

```{autodocx-docstring} duck.http.response_payload.SimpleHttpResponsePayload.status_message
```

````

`````
