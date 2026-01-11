# {py:mod}`duck.utils.xsocket.io`

```{py:module} duck.utils.xsocket.io
```

```{autodocx-docstring} duck.utils.xsocket.io
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`SocketIO <duck.utils.xsocket.io.SocketIO>`
  - ```{autodocx-docstring} duck.utils.xsocket.io.SocketIO
    :summary:
    ```
````

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`check_socket <duck.utils.xsocket.io.check_socket>`
  - ```{autodocx-docstring} duck.utils.xsocket.io.check_socket
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`CONTENT_LENGTH_PATTERN <duck.utils.xsocket.io.CONTENT_LENGTH_PATTERN>`
  - ```{autodocx-docstring} duck.utils.xsocket.io.CONTENT_LENGTH_PATTERN
    :summary:
    ```
* - {py:obj}`REQUEST_TIMEOUT <duck.utils.xsocket.io.REQUEST_TIMEOUT>`
  - ```{autodocx-docstring} duck.utils.xsocket.io.REQUEST_TIMEOUT
    :summary:
    ```
* - {py:obj}`SEND_TIMEOUT <duck.utils.xsocket.io.SEND_TIMEOUT>`
  - ```{autodocx-docstring} duck.utils.xsocket.io.SEND_TIMEOUT
    :summary:
    ```
* - {py:obj}`SERVER_BUFFER <duck.utils.xsocket.io.SERVER_BUFFER>`
  - ```{autodocx-docstring} duck.utils.xsocket.io.SERVER_BUFFER
    :summary:
    ```
* - {py:obj}`STREAM_TIMEOUT <duck.utils.xsocket.io.STREAM_TIMEOUT>`
  - ```{autodocx-docstring} duck.utils.xsocket.io.STREAM_TIMEOUT
    :summary:
    ```
* - {py:obj}`TRANSFER_ENCODING_PATTERN <duck.utils.xsocket.io.TRANSFER_ENCODING_PATTERN>`
  - ```{autodocx-docstring} duck.utils.xsocket.io.TRANSFER_ENCODING_PATTERN
    :summary:
    ```
````

### API

````{py:data} CONTENT_LENGTH_PATTERN
:canonical: duck.utils.xsocket.io.CONTENT_LENGTH_PATTERN
:value: >
   'compile(...)'

```{autodocx-docstring} duck.utils.xsocket.io.CONTENT_LENGTH_PATTERN
```

````

````{py:data} REQUEST_TIMEOUT
:canonical: duck.utils.xsocket.io.REQUEST_TIMEOUT
:value: >
   None

```{autodocx-docstring} duck.utils.xsocket.io.REQUEST_TIMEOUT
```

````

````{py:data} SEND_TIMEOUT
:canonical: duck.utils.xsocket.io.SEND_TIMEOUT
:value: >
   None

```{autodocx-docstring} duck.utils.xsocket.io.SEND_TIMEOUT
```

````

````{py:data} SERVER_BUFFER
:canonical: duck.utils.xsocket.io.SERVER_BUFFER
:value: >
   None

```{autodocx-docstring} duck.utils.xsocket.io.SERVER_BUFFER
```

````

````{py:data} STREAM_TIMEOUT
:canonical: duck.utils.xsocket.io.STREAM_TIMEOUT
:value: >
   None

```{autodocx-docstring} duck.utils.xsocket.io.STREAM_TIMEOUT
```

````

`````{py:class} SocketIO
:canonical: duck.utils.xsocket.io.SocketIO

```{autodocx-docstring} duck.utils.xsocket.io.SocketIO
```

````{py:method} async_connect(sock: duck.utils.xsocket.xsocket, target: typing.Tuple[str, int], timeout: float = None)
:canonical: duck.utils.xsocket.io.SocketIO.async_connect
:async:
:classmethod:

```{autodocx-docstring} duck.utils.xsocket.io.SocketIO.async_connect
```

````

````{py:method} async_receive(sock: duck.utils.xsocket.xsocket, timeout: float = REQUEST_TIMEOUT, bufsize: int = SERVER_BUFFER) -> bytes
:canonical: duck.utils.xsocket.io.SocketIO.async_receive
:async:
:classmethod:

```{autodocx-docstring} duck.utils.xsocket.io.SocketIO.async_receive
```

````

````{py:method} async_receive_full_request(sock: duck.utils.xsocket.xsocket, timeout: float = REQUEST_TIMEOUT, stream_timeout: float = STREAM_TIMEOUT) -> bytes
:canonical: duck.utils.xsocket.io.SocketIO.async_receive_full_request
:async:
:classmethod:

```{autodocx-docstring} duck.utils.xsocket.io.SocketIO.async_receive_full_request
```

````

````{py:method} async_send(sock: duck.utils.xsocket.xsocket, data: bytes, timeout: float = SEND_TIMEOUT, suppress_errors: bool = False, ignore_error_list: typing.List[typing.Type[Exception]] = [ssl.SSLError, BrokenPipeError, OSError]) -> int
:canonical: duck.utils.xsocket.io.SocketIO.async_send
:async:
:classmethod:

```{autodocx-docstring} duck.utils.xsocket.io.SocketIO.async_send
```

````

````{py:method} close(sock: duck.utils.xsocket.xsocket, shutdown: bool = True, shutdown_reason: int = socket.SHUT_RDWR, ignore_xsocket_error: bool = False)
:canonical: duck.utils.xsocket.io.SocketIO.close
:classmethod:

```{autodocx-docstring} duck.utils.xsocket.io.SocketIO.close
```

````

````{py:method} connect(sock: duck.utils.xsocket.xsocket, target: typing.Tuple[str, int], timeout: float = None)
:canonical: duck.utils.xsocket.io.SocketIO.connect
:classmethod:

```{autodocx-docstring} duck.utils.xsocket.io.SocketIO.connect
```

````

````{py:method} receive(sock: duck.utils.xsocket.xsocket, timeout: float = REQUEST_TIMEOUT, bufsize: int = SERVER_BUFFER) -> bytes
:canonical: duck.utils.xsocket.io.SocketIO.receive
:classmethod:

```{autodocx-docstring} duck.utils.xsocket.io.SocketIO.receive
```

````

````{py:method} receive_full_request(sock: duck.utils.xsocket.xsocket, timeout: float = REQUEST_TIMEOUT, stream_timeout: float = STREAM_TIMEOUT) -> bytes
:canonical: duck.utils.xsocket.io.SocketIO.receive_full_request
:classmethod:

```{autodocx-docstring} duck.utils.xsocket.io.SocketIO.receive_full_request
```

````

````{py:method} send(sock: duck.utils.xsocket.xsocket, data: bytes, timeout: float = SEND_TIMEOUT, suppress_errors: bool = False, ignore_error_list: typing.List[typing.Type[Exception]] = [ssl.SSLError, BrokenPipeError, OSError, ConnectionError]) -> int
:canonical: duck.utils.xsocket.io.SocketIO.send
:classmethod:

```{autodocx-docstring} duck.utils.xsocket.io.SocketIO.send
```

````

`````

````{py:exception} SocketIOError()
:canonical: duck.utils.xsocket.io.SocketIOError

Bases: {py:obj}`Exception`

```{autodocx-docstring} duck.utils.xsocket.io.SocketIOError
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.utils.xsocket.io.SocketIOError.__init__
```

````

````{py:data} TRANSFER_ENCODING_PATTERN
:canonical: duck.utils.xsocket.io.TRANSFER_ENCODING_PATTERN
:value: >
   'compile(...)'

```{autodocx-docstring} duck.utils.xsocket.io.TRANSFER_ENCODING_PATTERN
```

````

````{py:function} check_socket(func)
:canonical: duck.utils.xsocket.io.check_socket

```{autodocx-docstring} duck.utils.xsocket.io.check_socket
```
````
