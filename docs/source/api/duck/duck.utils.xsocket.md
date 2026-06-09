# {py:mod}`duck.utils.xsocket`

```{py:module} duck.utils.xsocket
```

```{autodocx-docstring} duck.utils.xsocket
:allowtitles:
```

## Submodules

```{toctree}
:titlesonly:
:maxdepth: 1

duck.utils.xsocket.io
```

## Package Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`SSLObjectReadOrWrite <duck.utils.xsocket.SSLObjectReadOrWrite>`
  - ```{autodocx-docstring} duck.utils.xsocket.SSLObjectReadOrWrite
    :summary:
    ```
* - {py:obj}`ssl_xsocket <duck.utils.xsocket.ssl_xsocket>`
  - ```{autodocx-docstring} duck.utils.xsocket.ssl_xsocket
    :summary:
    ```
* - {py:obj}`xsocket <duck.utils.xsocket.xsocket>`
  - ```{autodocx-docstring} duck.utils.xsocket.xsocket
    :summary:
    ```
````

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`create_xsocket <duck.utils.xsocket.create_xsocket>`
  - ```{autodocx-docstring} duck.utils.xsocket.create_xsocket
    :summary:
    ```
* - {py:obj}`ssl_wrap_socket <duck.utils.xsocket.ssl_wrap_socket>`
  - ```{autodocx-docstring} duck.utils.xsocket.ssl_wrap_socket
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`DEFAULT_BUFSIZE <duck.utils.xsocket.DEFAULT_BUFSIZE>`
  - ```{autodocx-docstring} duck.utils.xsocket.DEFAULT_BUFSIZE
    :summary:
    ```
````

### API

````{py:data} DEFAULT_BUFSIZE
:canonical: duck.utils.xsocket.DEFAULT_BUFSIZE
:value: >
   None

```{autodocx-docstring} duck.utils.xsocket.DEFAULT_BUFSIZE
```

````

`````{py:class} SSLObjectReadOrWrite()
:canonical: duck.utils.xsocket.SSLObjectReadOrWrite

Bases: {py:obj}`enum.IntEnum`

```{autodocx-docstring} duck.utils.xsocket.SSLObjectReadOrWrite
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.utils.xsocket.SSLObjectReadOrWrite.__init__
```

````{py:attribute} NOTHING
:canonical: duck.utils.xsocket.SSLObjectReadOrWrite.NOTHING
:value: >
   0

```{autodocx-docstring} duck.utils.xsocket.SSLObjectReadOrWrite.NOTHING
```

````

````{py:attribute} READING
:canonical: duck.utils.xsocket.SSLObjectReadOrWrite.READING
:value: >
   2

```{autodocx-docstring} duck.utils.xsocket.SSLObjectReadOrWrite.READING
```

````

````{py:attribute} WRITING
:canonical: duck.utils.xsocket.SSLObjectReadOrWrite.WRITING
:value: >
   1

```{autodocx-docstring} duck.utils.xsocket.SSLObjectReadOrWrite.WRITING
```

````

`````

````{py:function} create_xsocket(family: int = socket.AF_INET, type: int = socket.SOCK_STREAM, **kwargs) -> xsocket
:canonical: duck.utils.xsocket.create_xsocket

```{autodocx-docstring} duck.utils.xsocket.create_xsocket
```
````

````{py:function} ssl_wrap_socket(socket_obj: socket.socket, keyfile: str = None, certfile: str = None, version: int = ssl.PROTOCOL_TLS_SERVER, server_side: bool = True, ca_certs=None, ciphers=None, alpn_protocols: list[str] = None) -> ssl_xsocket
:canonical: duck.utils.xsocket.ssl_wrap_socket

```{autodocx-docstring} duck.utils.xsocket.ssl_wrap_socket
```
````

`````{py:class} ssl_xsocket(raw_socket: socket.socket, ssl_context: ssl.SSLContext, server_side: bool = True)
:canonical: duck.utils.xsocket.ssl_xsocket

Bases: {py:obj}`duck.utils.xsocket.xsocket`

```{autodocx-docstring} duck.utils.xsocket.ssl_xsocket
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.utils.xsocket.ssl_xsocket.__init__
```

````{py:method} _set_ssl_attributes()
:canonical: duck.utils.xsocket.ssl_xsocket._set_ssl_attributes

```{autodocx-docstring} duck.utils.xsocket.ssl_xsocket._set_ssl_attributes
```

````

````{py:method} async_do_handshake(timeout: typing.Optional[float] = None)
:canonical: duck.utils.xsocket.ssl_xsocket.async_do_handshake
:async:

```{autodocx-docstring} duck.utils.xsocket.ssl_xsocket.async_do_handshake
```

````

````{py:method} async_recv(n: int = DEFAULT_BUFSIZE, timeout: float = None) -> bytes
:canonical: duck.utils.xsocket.ssl_xsocket.async_recv
:async:

```{autodocx-docstring} duck.utils.xsocket.ssl_xsocket.async_recv
```

````

````{py:method} async_recv_more_encrypted_data(n: int = DEFAULT_BUFSIZE, timeout: typing.Optional[float] = None) -> int
:canonical: duck.utils.xsocket.ssl_xsocket.async_recv_more_encrypted_data
:async:

```{autodocx-docstring} duck.utils.xsocket.ssl_xsocket.async_recv_more_encrypted_data
```

````

````{py:method} async_send(data: bytes, timeout: float = None) -> int
:canonical: duck.utils.xsocket.ssl_xsocket.async_send
:async:

```{autodocx-docstring} duck.utils.xsocket.ssl_xsocket.async_send
```

````

````{py:method} async_send_pending_data(timeout: typing.Optional[float] = None) -> int
:canonical: duck.utils.xsocket.ssl_xsocket.async_send_pending_data
:async:

```{autodocx-docstring} duck.utils.xsocket.ssl_xsocket.async_send_pending_data
```

````

````{py:method} close(shutdown: bool = True, shutdown_reason: int = socket.SHUT_RDWR)
:canonical: duck.utils.xsocket.ssl_xsocket.close

````

````{py:method} do_handshake(timeout: typing.Optional[float] = None)
:canonical: duck.utils.xsocket.ssl_xsocket.do_handshake

```{autodocx-docstring} duck.utils.xsocket.ssl_xsocket.do_handshake
```

````

````{py:method} handle_sock_close()
:canonical: duck.utils.xsocket.ssl_xsocket.handle_sock_close

```{autodocx-docstring} duck.utils.xsocket.ssl_xsocket.handle_sock_close
```

````

````{py:method} is_handshake_done() -> bool
:canonical: duck.utils.xsocket.ssl_xsocket.is_handshake_done

```{autodocx-docstring} duck.utils.xsocket.ssl_xsocket.is_handshake_done
```

````

````{py:method} recv(n: int = DEFAULT_BUFSIZE, timeout: float = None) -> bytes
:canonical: duck.utils.xsocket.ssl_xsocket.recv

```{autodocx-docstring} duck.utils.xsocket.ssl_xsocket.recv
```

````

````{py:method} recv_more_encrypted_data(n: int = DEFAULT_BUFSIZE, timeout: typing.Optional[float] = None) -> int
:canonical: duck.utils.xsocket.ssl_xsocket.recv_more_encrypted_data

```{autodocx-docstring} duck.utils.xsocket.ssl_xsocket.recv_more_encrypted_data
```

````

````{py:method} send(data: bytes, timeout: float = None) -> int
:canonical: duck.utils.xsocket.ssl_xsocket.send

```{autodocx-docstring} duck.utils.xsocket.ssl_xsocket.send
```

````

````{py:method} send_pending_data(timeout: typing.Optional[float] = None) -> int
:canonical: duck.utils.xsocket.ssl_xsocket.send_pending_data

```{autodocx-docstring} duck.utils.xsocket.ssl_xsocket.send_pending_data
```

````

````{py:method} transport_readable(timeout: typing.Optional[float]) -> bool
:canonical: duck.utils.xsocket.ssl_xsocket.transport_readable

```{autodocx-docstring} duck.utils.xsocket.ssl_xsocket.transport_readable
```

````

`````

`````{py:class} xsocket(raw_socket: typing.Union[socket.socket, duck.utils.xsocket.xsocket])
:canonical: duck.utils.xsocket.xsocket

```{autodocx-docstring} duck.utils.xsocket.xsocket
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.utils.xsocket.xsocket.__init__
```

````{py:method} __getattribute__(attr: str) -> typing.Any
:canonical: duck.utils.xsocket.xsocket.__getattribute__

```{autodocx-docstring} duck.utils.xsocket.xsocket.__getattribute__
```

````

````{py:method} __repr__()
:canonical: duck.utils.xsocket.xsocket.__repr__

````

````{py:method} __setattr__(key: str, value: typing.Any) -> None
:canonical: duck.utils.xsocket.xsocket.__setattr__

```{autodocx-docstring} duck.utils.xsocket.xsocket.__setattr__
```

````

````{py:method} async_connect(target=Tuple[str, int], timeout: float = None) -> None
:canonical: duck.utils.xsocket.xsocket.async_connect
:async:

```{autodocx-docstring} duck.utils.xsocket.xsocket.async_connect
```

````

````{py:method} async_recv(n: int = DEFAULT_BUFSIZE, timeout: typing.Optional[float] = None) -> bytes
:canonical: duck.utils.xsocket.xsocket.async_recv
:async:

```{autodocx-docstring} duck.utils.xsocket.xsocket.async_recv
```

````

````{py:method} async_send(data: bytes, timeout: typing.Optional[float] = None) -> int
:canonical: duck.utils.xsocket.xsocket.async_send
:async:

```{autodocx-docstring} duck.utils.xsocket.xsocket.async_send
```

````

````{py:method} close(shutdown: bool = True, shutdown_reason: int = socket.SHUT_RDWR)
:canonical: duck.utils.xsocket.xsocket.close

```{autodocx-docstring} duck.utils.xsocket.xsocket.close
```

````

````{py:method} connect(target=Tuple[str, int], timeout: float = None) -> None
:canonical: duck.utils.xsocket.xsocket.connect

```{autodocx-docstring} duck.utils.xsocket.xsocket.connect
```

````

````{py:property} loop
:canonical: duck.utils.xsocket.xsocket.loop
:type: asyncio.AbstractEventLoop

```{autodocx-docstring} duck.utils.xsocket.xsocket.loop
```

````

````{py:method} raise_if_blocking()
:canonical: duck.utils.xsocket.xsocket.raise_if_blocking

```{autodocx-docstring} duck.utils.xsocket.xsocket.raise_if_blocking
```

````

````{py:method} raise_if_in_async_context(message: str)
:canonical: duck.utils.xsocket.xsocket.raise_if_in_async_context

```{autodocx-docstring} duck.utils.xsocket.xsocket.raise_if_in_async_context
```

````

````{py:method} recv(n: int = DEFAULT_BUFSIZE, timeout: float = None)
:canonical: duck.utils.xsocket.xsocket.recv

```{autodocx-docstring} duck.utils.xsocket.xsocket.recv
```

````

````{py:method} send(data: bytes, timeout: float = None) -> int
:canonical: duck.utils.xsocket.xsocket.send

```{autodocx-docstring} duck.utils.xsocket.xsocket.send
```

````

`````

````{py:exception} xsocketError()
:canonical: duck.utils.xsocket.xsocketError

Bases: {py:obj}`Exception`

```{autodocx-docstring} duck.utils.xsocket.xsocketError
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.utils.xsocket.xsocketError.__init__
```

````
