# {py:mod}`duck.http.request`

```{py:module} duck.http.request
```

```{autodocx-docstring} duck.http.request
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`Request <duck.http.request.Request>`
  - ```{autodocx-docstring} duck.http.request.Request
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`HttpRequest <duck.http.request.HttpRequest>`
  - ```{autodocx-docstring} duck.http.request.HttpRequest
    :summary:
    ```
* - {py:obj}`SUPPORTED_HTTP_VERSIONS <duck.http.request.SUPPORTED_HTTP_VERSIONS>`
  - ```{autodocx-docstring} duck.http.request.SUPPORTED_HTTP_VERSIONS
    :summary:
    ```
````

### API

````{py:data} HttpRequest
:canonical: duck.http.request.HttpRequest
:value: >
   None

```{autodocx-docstring} duck.http.request.HttpRequest
```

````

`````{py:class} Request(**kwargs)
:canonical: duck.http.request.Request

```{autodocx-docstring} duck.http.request.Request
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.http.request.Request.__init__
```

````{py:property} ID
:canonical: duck.http.request.Request.ID

```{autodocx-docstring} duck.http.request.Request.ID
```

````

````{py:property} META
:canonical: duck.http.request.Request.META
:type: dict

```{autodocx-docstring} duck.http.request.Request.META
```

````

````{py:property} SESSION
:canonical: duck.http.request.Request.SESSION

```{autodocx-docstring} duck.http.request.Request.SESSION
```

````

````{py:attribute} SUPPORTED_HTTP_VERSIONS
:canonical: duck.http.request.Request.SUPPORTED_HTTP_VERSIONS
:type: list
:value: >
   None

```{autodocx-docstring} duck.http.request.Request.SUPPORTED_HTTP_VERSIONS
```

````

````{py:method} __repr__()
:canonical: duck.http.request.Request.__repr__

````

````{py:method} _build_headers() -> bytes
:canonical: duck.http.request.Request._build_headers

```{autodocx-docstring} duck.http.request.Request._build_headers
```

````

````{py:method} _build_request_line() -> bytes
:canonical: duck.http.request.Request._build_request_line

```{autodocx-docstring} duck.http.request.Request._build_request_line
```

````

````{py:method} _extract_and_process_request_data()
:canonical: duck.http.request.Request._extract_and_process_request_data

```{autodocx-docstring} duck.http.request.Request._extract_and_process_request_data
```

````

````{py:method} _parse_content(raw_content: bytes)
:canonical: duck.http.request.Request._parse_content

```{autodocx-docstring} duck.http.request.Request._parse_content
```

````

````{py:method} _parse_raw_headers(raw_headers: bytes)
:canonical: duck.http.request.Request._parse_raw_headers

```{autodocx-docstring} duck.http.request.Request._parse_raw_headers
```

````

````{py:method} _parse_raw_request(raw_request: bytes)
:canonical: duck.http.request.Request._parse_raw_request

```{autodocx-docstring} duck.http.request.Request._parse_raw_request
```

````

````{py:method} _parse_request(topheader: str, headers: typing.Dict[str, str], content: bytes)
:canonical: duck.http.request.Request._parse_request

```{autodocx-docstring} duck.http.request.Request._parse_request
```

````

````{py:method} _set_auth_headers()
:canonical: duck.http.request.Request._set_auth_headers

```{autodocx-docstring} duck.http.request.Request._set_auth_headers
```

````

````{py:property} absolute_uri
:canonical: duck.http.request.Request.absolute_uri
:type: str

```{autodocx-docstring} duck.http.request.Request.absolute_uri
```

````

````{py:property} absolute_ws_uri
:canonical: duck.http.request.Request.absolute_ws_uri
:type: str

```{autodocx-docstring} duck.http.request.Request.absolute_ws_uri
```

````

````{py:method} add_queries_to_url(url: str, queries: typing.Dict) -> str
:canonical: duck.http.request.Request.add_queries_to_url
:staticmethod:

```{autodocx-docstring} duck.http.request.Request.add_queries_to_url
```

````

````{py:method} build_absolute_uri(path: str = None) -> str
:canonical: duck.http.request.Request.build_absolute_uri

```{autodocx-docstring} duck.http.request.Request.build_absolute_uri
```

````

````{py:method} build_absolute_ws_uri(path: str = None) -> str
:canonical: duck.http.request.Request.build_absolute_ws_uri

```{autodocx-docstring} duck.http.request.Request.build_absolute_ws_uri
```

````

````{py:method} build_meta() -> typing.Dict
:canonical: duck.http.request.Request.build_meta

```{autodocx-docstring} duck.http.request.Request.build_meta
```

````

````{py:property} connection
:canonical: duck.http.request.Request.connection
:type: str

```{autodocx-docstring} duck.http.request.Request.connection
```

````

````{py:property} content
:canonical: duck.http.request.Request.content

```{autodocx-docstring} duck.http.request.Request.content
```

````

````{py:property} domain
:canonical: duck.http.request.Request.domain
:type: str

```{autodocx-docstring} duck.http.request.Request.domain
```

````

````{py:method} extract_auth_from_request(request) -> typing.Dict[str, str]
:canonical: duck.http.request.Request.extract_auth_from_request
:staticmethod:

```{autodocx-docstring} duck.http.request.Request.extract_auth_from_request
```

````

````{py:method} extract_content_queries(request) -> duck.http.querydict.QueryDict
:canonical: duck.http.request.Request.extract_content_queries
:staticmethod:

```{autodocx-docstring} duck.http.request.Request.extract_content_queries
```

````

````{py:method} extract_cookies_from_request(request) -> typing.Dict[str, str]
:canonical: duck.http.request.Request.extract_cookies_from_request
:staticmethod:

```{autodocx-docstring} duck.http.request.Request.extract_cookies_from_request
```

````

````{py:method} extract_url_queries(url: str) -> typing.Tuple[str, duck.http.querydict.QueryDict]
:canonical: duck.http.request.Request.extract_url_queries
:staticmethod:

```{autodocx-docstring} duck.http.request.Request.extract_url_queries
```

````

````{py:property} fullpath
:canonical: duck.http.request.Request.fullpath

```{autodocx-docstring} duck.http.request.Request.fullpath
```

````

````{py:method} get_header(header: str, default_value: typing.Optional[str] = None) -> typing.Optional[str]
:canonical: duck.http.request.Request.get_header

```{autodocx-docstring} duck.http.request.Request.get_header
```

````

````{py:property} has_error
:canonical: duck.http.request.Request.has_error
:type: bool

```{autodocx-docstring} duck.http.request.Request.has_error
```

````

````{py:property} headers
:canonical: duck.http.request.Request.headers
:type: dict

```{autodocx-docstring} duck.http.request.Request.headers
```

````

````{py:property} host
:canonical: duck.http.request.Request.host
:type: str

```{autodocx-docstring} duck.http.request.Request.host
```

````

````{py:property} hostname
:canonical: duck.http.request.Request.hostname
:type: str

```{autodocx-docstring} duck.http.request.Request.hostname
```

````

````{py:property} json
:canonical: duck.http.request.Request.json

```{autodocx-docstring} duck.http.request.Request.json
```

````

````{py:property} origin
:canonical: duck.http.request.Request.origin
:type: typing.Optional[str]

```{autodocx-docstring} duck.http.request.Request.origin
```

````

````{py:method} parse(request_data: duck.http.request_data.RequestData)
:canonical: duck.http.request.Request.parse

```{autodocx-docstring} duck.http.request.Request.parse
```

````

````{py:method} parse_raw_request(raw_request: bytes)
:canonical: duck.http.request.Request.parse_raw_request

```{autodocx-docstring} duck.http.request.Request.parse_raw_request
```

````

````{py:method} parse_request(topheader: str, headers: typing.Dict[str, str], content: bytes)
:canonical: duck.http.request.Request.parse_request

```{autodocx-docstring} duck.http.request.Request.parse_request
```

````

````{py:property} path
:canonical: duck.http.request.Request.path
:type: typing.Optional[str]

```{autodocx-docstring} duck.http.request.Request.path
```

````

````{py:property} port
:canonical: duck.http.request.Request.port
:type: typing.Optional[int]

```{autodocx-docstring} duck.http.request.Request.port
```

````

````{py:property} protocol
:canonical: duck.http.request.Request.protocol
:type: typing.Optional[str]

```{autodocx-docstring} duck.http.request.Request.protocol
```

````

````{py:property} raw
:canonical: duck.http.request.Request.raw
:type: bytes

```{autodocx-docstring} duck.http.request.Request.raw
```

````

````{py:property} referer
:canonical: duck.http.request.Request.referer
:type: typing.Optional[str]

```{autodocx-docstring} duck.http.request.Request.referer
```

````

````{py:property} remote_addr
:canonical: duck.http.request.Request.remote_addr
:type: typing.Tuple[str, int]

```{autodocx-docstring} duck.http.request.Request.remote_addr
```

````

````{py:property} scheme
:canonical: duck.http.request.Request.scheme
:type: str

```{autodocx-docstring} duck.http.request.Request.scheme
```

````

````{py:property} session
:canonical: duck.http.request.Request.session

```{autodocx-docstring} duck.http.request.Request.session
```

````

````{py:method} set_connection(mode: str)
:canonical: duck.http.request.Request.set_connection

```{autodocx-docstring} duck.http.request.Request.set_connection
```

````

````{py:method} set_content(data: bytes, auto_add_content_headers: bool = True)
:canonical: duck.http.request.Request.set_content

```{autodocx-docstring} duck.http.request.Request.set_content
```

````

````{py:method} set_header(header: str, value: str)
:canonical: duck.http.request.Request.set_header

```{autodocx-docstring} duck.http.request.Request.set_header
```

````

````{py:property} title_headers
:canonical: duck.http.request.Request.title_headers
:type: dict

```{autodocx-docstring} duck.http.request.Request.title_headers
```

````

````{py:property} uses_https
:canonical: duck.http.request.Request.uses_https

```{autodocx-docstring} duck.http.request.Request.uses_https
```

````

````{py:property} version_number
:canonical: duck.http.request.Request.version_number
:type: typing.Optional[str]

```{autodocx-docstring} duck.http.request.Request.version_number
```

````

`````

````{py:data} SUPPORTED_HTTP_VERSIONS
:canonical: duck.http.request.SUPPORTED_HTTP_VERSIONS
:value: >
   ['HTTP/1.0', 'HTTP/1.1']

```{autodocx-docstring} duck.http.request.SUPPORTED_HTTP_VERSIONS
```

````
