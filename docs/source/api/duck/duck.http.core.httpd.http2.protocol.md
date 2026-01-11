# {py:mod}`duck.http.core.httpd.http2.protocol`

```{py:module} duck.http.core.httpd.http2.protocol
```

```{autodocx-docstring} duck.http.core.httpd.http2.protocol
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`H2Protocol <duck.http.core.httpd.http2.protocol.H2Protocol>`
  - ```{autodocx-docstring} duck.http.core.httpd.http2.protocol.H2Protocol
    :summary:
    ```
````

### API

`````{py:class} H2Protocol(sock: duck.utils.xsocket.xsocket, addr: typing.Tuple[str, int], conn: h2.connection.H2Connection, event_handler: duck.http.core.httpd.http2.event_handler.EventHandler, event_loop: asyncio.BaseEventLoop = None, sync_queue: typing.Optional[queue.Queue] = None)
:canonical: duck.http.core.httpd.http2.protocol.H2Protocol

```{autodocx-docstring} duck.http.core.httpd.http2.protocol.H2Protocol
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.http.core.httpd.http2.protocol.H2Protocol.__init__
```

````{py:attribute} __slots__
:canonical: duck.http.core.httpd.http2.protocol.H2Protocol.__slots__
:value: >
   ('sock', 'addr', 'conn', 'server', 'event_handler', 'event_loop', 'sync_queue', '__closing')

```{autodocx-docstring} duck.http.core.httpd.http2.protocol.H2Protocol.__slots__
```

````

````{py:method} async_flush_response_data(data: bytes, stream_id: int, end_stream: bool = False)
:canonical: duck.http.core.httpd.http2.protocol.H2Protocol.async_flush_response_data
:async:

```{autodocx-docstring} duck.http.core.httpd.http2.protocol.H2Protocol.async_flush_response_data
```

````

````{py:method} async_send_data(data: bytes, stream_id: int, end_stream: bool = False, on_data_sent: typing.Callable = None, flow_control_timeout: float = 30.0)
:canonical: duck.http.core.httpd.http2.protocol.H2Protocol.async_send_data
:async:

```{autodocx-docstring} duck.http.core.httpd.http2.protocol.H2Protocol.async_send_data
```

````

````{py:method} async_send_goaway(error_code, debug_message: bytes = None)
:canonical: duck.http.core.httpd.http2.protocol.H2Protocol.async_send_goaway
:async:

```{autodocx-docstring} duck.http.core.httpd.http2.protocol.H2Protocol.async_send_goaway
```

````

````{py:method} async_send_pending_data()
:canonical: duck.http.core.httpd.http2.protocol.H2Protocol.async_send_pending_data
:async:

```{autodocx-docstring} duck.http.core.httpd.http2.protocol.H2Protocol.async_send_pending_data
```

````

````{py:method} async_send_response(response: typing.Union[duck.http.response.BaseResponse, duck.http.response.HttpResponse], stream_id: int, request: typing.Optional[duck.http.request.HttpRequest] = None, disable_logging: bool = False, suppress_errors: bool = False) -> None
:canonical: duck.http.core.httpd.http2.protocol.H2Protocol.async_send_response
:async:

```{autodocx-docstring} duck.http.core.httpd.http2.protocol.H2Protocol.async_send_response
```

````

````{py:method} close_connection(error_code: int = 0, debug_message: bytes = None)
:canonical: duck.http.core.httpd.http2.protocol.H2Protocol.close_connection

```{autodocx-docstring} duck.http.core.httpd.http2.protocol.H2Protocol.close_connection
```

````

````{py:property} closing
:canonical: duck.http.core.httpd.http2.protocol.H2Protocol.closing
:type: bool

```{autodocx-docstring} duck.http.core.httpd.http2.protocol.H2Protocol.closing
```

````

````{py:method} connection_lost(*_)
:canonical: duck.http.core.httpd.http2.protocol.H2Protocol.connection_lost

```{autodocx-docstring} duck.http.core.httpd.http2.protocol.H2Protocol.connection_lost
```

````

````{py:method} run_forever()
:canonical: duck.http.core.httpd.http2.protocol.H2Protocol.run_forever
:async:

```{autodocx-docstring} duck.http.core.httpd.http2.protocol.H2Protocol.run_forever
```

````

````{py:method} send_pending_data()
:canonical: duck.http.core.httpd.http2.protocol.H2Protocol.send_pending_data

```{autodocx-docstring} duck.http.core.httpd.http2.protocol.H2Protocol.send_pending_data
```

````

````{py:method} send_response(response: typing.Union[duck.http.response.BaseResponse, duck.http.response.HttpResponse], stream_id: int, request: typing.Optional[duck.http.request.HttpRequest] = None, disable_logging: bool = False, suppress_errors: bool = False, return_future: bool = False) -> typing.Optional[duck.utils.asyncio.eventloop.SyncFuture]
:canonical: duck.http.core.httpd.http2.protocol.H2Protocol.send_response

```{autodocx-docstring} duck.http.core.httpd.http2.protocol.H2Protocol.send_response
```

````

`````
