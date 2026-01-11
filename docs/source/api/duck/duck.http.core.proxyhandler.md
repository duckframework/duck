# {py:mod}`duck.http.core.proxyhandler`

```{py:module} duck.http.core.proxyhandler
```

```{autodocx-docstring} duck.http.core.proxyhandler
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`AsyncHttpProxyHandler <duck.http.core.proxyhandler.AsyncHttpProxyHandler>`
  - ```{autodocx-docstring} duck.http.core.proxyhandler.AsyncHttpProxyHandler
    :summary:
    ```
* - {py:obj}`HttpProxyHandler <duck.http.core.proxyhandler.HttpProxyHandler>`
  - ```{autodocx-docstring} duck.http.core.proxyhandler.HttpProxyHandler
    :summary:
    ```
* - {py:obj}`HttpProxyResponse <duck.http.core.proxyhandler.HttpProxyResponse>`
  - ```{autodocx-docstring} duck.http.core.proxyhandler.HttpProxyResponse
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`CONNECT_TIMEOUT <duck.http.core.proxyhandler.CONNECT_TIMEOUT>`
  - ```{autodocx-docstring} duck.http.core.proxyhandler.CONNECT_TIMEOUT
    :summary:
    ```
* - {py:obj}`DJANGO_REQUEST_FIXER_MIDDLEWARE <duck.http.core.proxyhandler.DJANGO_REQUEST_FIXER_MIDDLEWARE>`
  - ```{autodocx-docstring} duck.http.core.proxyhandler.DJANGO_REQUEST_FIXER_MIDDLEWARE
    :summary:
    ```
* - {py:obj}`PAYLOAD_BUFFER_SIZE <duck.http.core.proxyhandler.PAYLOAD_BUFFER_SIZE>`
  - ```{autodocx-docstring} duck.http.core.proxyhandler.PAYLOAD_BUFFER_SIZE
    :summary:
    ```
* - {py:obj}`READ_TIMEOUT <duck.http.core.proxyhandler.READ_TIMEOUT>`
  - ```{autodocx-docstring} duck.http.core.proxyhandler.READ_TIMEOUT
    :summary:
    ```
* - {py:obj}`STREAM_CHUNK_SIZE <duck.http.core.proxyhandler.STREAM_CHUNK_SIZE>`
  - ```{autodocx-docstring} duck.http.core.proxyhandler.STREAM_CHUNK_SIZE
    :summary:
    ```
````

### API

`````{py:class} AsyncHttpProxyHandler(target_host: str, target_port: int, uses_ipv6: bool = False, uses_ssl: bool = False)
:canonical: duck.http.core.proxyhandler.AsyncHttpProxyHandler

Bases: {py:obj}`duck.http.core.proxyhandler.HttpProxyHandler`

```{autodocx-docstring} duck.http.core.proxyhandler.AsyncHttpProxyHandler
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.http.core.proxyhandler.AsyncHttpProxyHandler.__init__
```

````{py:method} connect_to_target() -> duck.utils.xsocket.xsocket
:canonical: duck.http.core.proxyhandler.AsyncHttpProxyHandler.connect_to_target
:async:

```{autodocx-docstring} duck.http.core.proxyhandler.AsyncHttpProxyHandler.connect_to_target
```

````

````{py:method} fetch_response_payload(target_socket: duck.utils.xsocket.xsocket) -> typing.Tuple[duck.http.response_payload.SimpleHttpResponsePayload, bytes]
:canonical: duck.http.core.proxyhandler.AsyncHttpProxyHandler.fetch_response_payload
:async:

```{autodocx-docstring} duck.http.core.proxyhandler.AsyncHttpProxyHandler.fetch_response_payload
```

````

````{py:method} forward_request_to_target(request: duck.http.request.HttpRequest, client_socket: duck.utils.xsocket.xsocket, target_socket: duck.utils.xsocket.xsocket)
:canonical: duck.http.core.proxyhandler.AsyncHttpProxyHandler.forward_request_to_target
:async:

```{autodocx-docstring} duck.http.core.proxyhandler.AsyncHttpProxyHandler.forward_request_to_target
```

````

````{py:method} get_response(request: duck.http.request.HttpRequest, client_socket: socket.socket) -> duck.http.core.proxyhandler.HttpProxyResponse
:canonical: duck.http.core.proxyhandler.AsyncHttpProxyHandler.get_response
:async:

```{autodocx-docstring} duck.http.core.proxyhandler.AsyncHttpProxyHandler.get_response
```

````

`````

````{py:exception} BadGatewayError()
:canonical: duck.http.core.proxyhandler.BadGatewayError

Bases: {py:obj}`duck.http.core.proxyhandler.ReverseProxyError`

```{autodocx-docstring} duck.http.core.proxyhandler.BadGatewayError
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.http.core.proxyhandler.BadGatewayError.__init__
```

````

````{py:data} CONNECT_TIMEOUT
:canonical: duck.http.core.proxyhandler.CONNECT_TIMEOUT
:value: >
   None

```{autodocx-docstring} duck.http.core.proxyhandler.CONNECT_TIMEOUT
```

````

````{py:data} DJANGO_REQUEST_FIXER_MIDDLEWARE
:canonical: duck.http.core.proxyhandler.DJANGO_REQUEST_FIXER_MIDDLEWARE
:value: >
   'x_import(...)'

```{autodocx-docstring} duck.http.core.proxyhandler.DJANGO_REQUEST_FIXER_MIDDLEWARE
```

````

`````{py:class} HttpProxyHandler(target_host: str, target_port: int, uses_ipv6: bool = False, uses_ssl: bool = False)
:canonical: duck.http.core.proxyhandler.HttpProxyHandler

```{autodocx-docstring} duck.http.core.proxyhandler.HttpProxyHandler
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.http.core.proxyhandler.HttpProxyHandler.__init__
```

````{py:attribute} __slots__
:canonical: duck.http.core.proxyhandler.HttpProxyHandler.__slots__
:value: >
   ('uses_ipv6', 'target_host', 'target_port', 'uses_ssl')

```{autodocx-docstring} duck.http.core.proxyhandler.HttpProxyHandler.__slots__
```

````

````{py:method} connect_to_target() -> duck.utils.xsocket.xsocket
:canonical: duck.http.core.proxyhandler.HttpProxyHandler.connect_to_target

```{autodocx-docstring} duck.http.core.proxyhandler.HttpProxyHandler.connect_to_target
```

````

````{py:method} fetch_response_payload(target_socket: duck.utils.xsocket.xsocket) -> typing.Tuple[duck.http.response_payload.SimpleHttpResponsePayload, bytes]
:canonical: duck.http.core.proxyhandler.HttpProxyHandler.fetch_response_payload

```{autodocx-docstring} duck.http.core.proxyhandler.HttpProxyHandler.fetch_response_payload
```

````

````{py:method} forward_request_to_target(request: duck.http.request.HttpRequest, client_socket: duck.utils.xsocket.xsocket, target_socket: duck.utils.xsocket.xsocket)
:canonical: duck.http.core.proxyhandler.HttpProxyHandler.forward_request_to_target

```{autodocx-docstring} duck.http.core.proxyhandler.HttpProxyHandler.forward_request_to_target
```

````

````{py:method} get_response(request: duck.http.request.HttpRequest, client_socket: socket.socket) -> duck.http.core.proxyhandler.HttpProxyResponse
:canonical: duck.http.core.proxyhandler.HttpProxyHandler.get_response

```{autodocx-docstring} duck.http.core.proxyhandler.HttpProxyHandler.get_response
```

````

````{py:method} modify_client_request(request: duck.http.request.HttpRequest)
:canonical: duck.http.core.proxyhandler.HttpProxyHandler.modify_client_request

```{autodocx-docstring} duck.http.core.proxyhandler.HttpProxyHandler.modify_client_request
```

````

`````

`````{py:class} HttpProxyResponse(target_socket: duck.utils.xsocket.xsocket, payload_obj: duck.http.response_payload.BaseResponsePayload, content_obj: typing.Optional[duck.http.content.Content] = None, chunk_size: int = STREAM_CHUNK_SIZE)
:canonical: duck.http.core.proxyhandler.HttpProxyResponse

Bases: {py:obj}`duck.http.response.StreamingHttpResponse`

```{autodocx-docstring} duck.http.core.proxyhandler.HttpProxyResponse
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.http.core.proxyhandler.HttpProxyResponse.__init__
```

````{py:method} __repr__()
:canonical: duck.http.core.proxyhandler.HttpProxyResponse.__repr__

````

````{py:method} async_iter_content() -> typing.AsyncGenerator[bytes, None]
:canonical: duck.http.core.proxyhandler.HttpProxyResponse.async_iter_content
:async:

```{autodocx-docstring} duck.http.core.proxyhandler.HttpProxyResponse.async_iter_content
```

````

````{py:method} async_recv_more(buffer: int = 4096) -> bytes
:canonical: duck.http.core.proxyhandler.HttpProxyResponse.async_recv_more
:async:

```{autodocx-docstring} duck.http.core.proxyhandler.HttpProxyResponse.async_recv_more
```

````

````{py:method} iter_content() -> typing.Generator[bytes, None, None]
:canonical: duck.http.core.proxyhandler.HttpProxyResponse.iter_content

```{autodocx-docstring} duck.http.core.proxyhandler.HttpProxyResponse.iter_content
```

````

````{py:method} recv_more(buffer: int = 4096) -> bytes
:canonical: duck.http.core.proxyhandler.HttpProxyResponse.recv_more

```{autodocx-docstring} duck.http.core.proxyhandler.HttpProxyResponse.recv_more
```

````

`````

````{py:data} PAYLOAD_BUFFER_SIZE
:canonical: duck.http.core.proxyhandler.PAYLOAD_BUFFER_SIZE
:value: >
   None

```{autodocx-docstring} duck.http.core.proxyhandler.PAYLOAD_BUFFER_SIZE
```

````

````{py:data} READ_TIMEOUT
:canonical: duck.http.core.proxyhandler.READ_TIMEOUT
:value: >
   None

```{autodocx-docstring} duck.http.core.proxyhandler.READ_TIMEOUT
```

````

````{py:exception} ReverseProxyError()
:canonical: duck.http.core.proxyhandler.ReverseProxyError

Bases: {py:obj}`Exception`

```{autodocx-docstring} duck.http.core.proxyhandler.ReverseProxyError
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.http.core.proxyhandler.ReverseProxyError.__init__
```

````

````{py:data} STREAM_CHUNK_SIZE
:canonical: duck.http.core.proxyhandler.STREAM_CHUNK_SIZE
:value: >
   None

```{autodocx-docstring} duck.http.core.proxyhandler.STREAM_CHUNK_SIZE
```

````
