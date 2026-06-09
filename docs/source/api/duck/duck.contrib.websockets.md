# {py:mod}`duck.contrib.websockets`

```{py:module} duck.contrib.websockets
```

```{autodocx-docstring} duck.contrib.websockets
:allowtitles:
```

## Submodules

```{toctree}
:titlesonly:
:maxdepth: 1

duck.contrib.websockets.exceptions
duck.contrib.websockets.extensions
duck.contrib.websockets.frame
duck.contrib.websockets.logging
duck.contrib.websockets.opcodes
```

## Package Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`State <duck.contrib.websockets.State>`
  - ```{autodocx-docstring} duck.contrib.websockets.State
    :summary:
    ```
* - {py:obj}`WebSocketView <duck.contrib.websockets.WebSocketView>`
  - ```{autodocx-docstring} duck.contrib.websockets.WebSocketView
    :summary:
    ```
````

### API

`````{py:class} State()
:canonical: duck.contrib.websockets.State

Bases: {py:obj}`enum.IntEnum`

```{autodocx-docstring} duck.contrib.websockets.State
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.contrib.websockets.State.__init__
```

````{py:attribute} CLOSED
:canonical: duck.contrib.websockets.State.CLOSED
:value: >
   0

```{autodocx-docstring} duck.contrib.websockets.State.CLOSED
```

````

````{py:attribute} INITIATED
:canonical: duck.contrib.websockets.State.INITIATED
:value: >
   2

```{autodocx-docstring} duck.contrib.websockets.State.INITIATED
```

````

````{py:attribute} INITIATING
:canonical: duck.contrib.websockets.State.INITIATING
:value: >
   None

```{autodocx-docstring} duck.contrib.websockets.State.INITIATING
```

````

````{py:attribute} OPEN
:canonical: duck.contrib.websockets.State.OPEN
:value: >
   1

```{autodocx-docstring} duck.contrib.websockets.State.OPEN
```

````

`````

`````{py:class} WebSocketView(upgrade_request: duck.http.request.HttpRequest, **kwargs)
:canonical: duck.contrib.websockets.WebSocketView

Bases: {py:obj}`duck.views.View`

```{autodocx-docstring} duck.contrib.websockets.WebSocketView
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.contrib.websockets.WebSocketView.__init__
```

````{py:attribute} MAGIC_STRING
:canonical: duck.contrib.websockets.WebSocketView.MAGIC_STRING
:value: >
   '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'

```{autodocx-docstring} duck.contrib.websockets.WebSocketView.MAGIC_STRING
```

````

````{py:attribute} MAX_BACKOFF
:canonical: duck.contrib.websockets.WebSocketView.MAX_BACKOFF
:value: >
   45

```{autodocx-docstring} duck.contrib.websockets.WebSocketView.MAX_BACKOFF
```

````

````{py:attribute} MAX_FRAME_SIZE
:canonical: duck.contrib.websockets.WebSocketView.MAX_FRAME_SIZE
:value: >
   None

```{autodocx-docstring} duck.contrib.websockets.WebSocketView.MAX_FRAME_SIZE
```

````

````{py:attribute} PING_INTERVAL
:canonical: duck.contrib.websockets.WebSocketView.PING_INTERVAL
:value: >
   20

```{autodocx-docstring} duck.contrib.websockets.WebSocketView.PING_INTERVAL
```

````

````{py:attribute} PONG_TIMEOUT
:canonical: duck.contrib.websockets.WebSocketView.PONG_TIMEOUT
:value: >
   10

```{autodocx-docstring} duck.contrib.websockets.WebSocketView.PONG_TIMEOUT
```

````

````{py:attribute} RECEIVE_TIMEOUT
:canonical: duck.contrib.websockets.WebSocketView.RECEIVE_TIMEOUT
:value: >
   120

```{autodocx-docstring} duck.contrib.websockets.WebSocketView.RECEIVE_TIMEOUT
```

````

````{py:method} _heartbeat_loop()
:canonical: duck.contrib.websockets.WebSocketView._heartbeat_loop
:async:

```{autodocx-docstring} duck.contrib.websockets.WebSocketView._heartbeat_loop
```

````

````{py:method} _receive_loop()
:canonical: duck.contrib.websockets.WebSocketView._receive_loop
:async:

```{autodocx-docstring} duck.contrib.websockets.WebSocketView._receive_loop
```

````

````{py:method} get_sec_accept_key(sec_websocket_key: str) -> str
:canonical: duck.contrib.websockets.WebSocketView.get_sec_accept_key

```{autodocx-docstring} duck.contrib.websockets.WebSocketView.get_sec_accept_key
```

````

````{py:method} initiate_upgrade_to_ws() -> bool
:canonical: duck.contrib.websockets.WebSocketView.initiate_upgrade_to_ws
:async:

```{autodocx-docstring} duck.contrib.websockets.WebSocketView.initiate_upgrade_to_ws
```

````

````{py:method} on_close(frame: duck.contrib.websockets.frame.Frame = None)
:canonical: duck.contrib.websockets.WebSocketView.on_close
:async:

```{autodocx-docstring} duck.contrib.websockets.WebSocketView.on_close
```

````

````{py:method} on_new_frame(frame: duck.contrib.websockets.frame.Frame)
:canonical: duck.contrib.websockets.WebSocketView.on_new_frame
:async:

```{autodocx-docstring} duck.contrib.websockets.WebSocketView.on_new_frame
```

````

````{py:method} on_open()
:canonical: duck.contrib.websockets.WebSocketView.on_open
:async:

```{autodocx-docstring} duck.contrib.websockets.WebSocketView.on_open
```

````

````{py:method} on_receive(message: bytes, opcode, **kwargs)
:canonical: duck.contrib.websockets.WebSocketView.on_receive
:abstractmethod:
:async:

```{autodocx-docstring} duck.contrib.websockets.WebSocketView.on_receive
```

````

````{py:method} read_frame() -> duck.contrib.websockets.frame.Frame
:canonical: duck.contrib.websockets.WebSocketView.read_frame
:async:

```{autodocx-docstring} duck.contrib.websockets.WebSocketView.read_frame
```

````

````{py:method} run() -> None
:canonical: duck.contrib.websockets.WebSocketView.run
:async:

```{autodocx-docstring} duck.contrib.websockets.WebSocketView.run
```

````

````{py:method} run_forever()
:canonical: duck.contrib.websockets.WebSocketView.run_forever
:async:

```{autodocx-docstring} duck.contrib.websockets.WebSocketView.run_forever
```

````

````{py:method} safe_close(disable_logging: bool = False, call_on_close_handler: bool = True)
:canonical: duck.contrib.websockets.WebSocketView.safe_close
:async:

```{autodocx-docstring} duck.contrib.websockets.WebSocketView.safe_close
```

````

````{py:method} send(data: typing.Union[str, bytes], opcode: int = OpCode.TEXT)
:canonical: duck.contrib.websockets.WebSocketView.send
:async:

```{autodocx-docstring} duck.contrib.websockets.WebSocketView.send
```

````

````{py:method} send_binary(data: bytes)
:canonical: duck.contrib.websockets.WebSocketView.send_binary
:async:

```{autodocx-docstring} duck.contrib.websockets.WebSocketView.send_binary
```

````

````{py:method} send_close(code: int = CloseCode.NORMAL_CLOSURE, reason: str = '')
:canonical: duck.contrib.websockets.WebSocketView.send_close
:async:

```{autodocx-docstring} duck.contrib.websockets.WebSocketView.send_close
```

````

````{py:method} send_frame(frame: duck.contrib.websockets.frame.Frame)
:canonical: duck.contrib.websockets.WebSocketView.send_frame
:async:

```{autodocx-docstring} duck.contrib.websockets.WebSocketView.send_frame
```

````

````{py:method} send_json(data: typing.Union[dict, list])
:canonical: duck.contrib.websockets.WebSocketView.send_json
:async:

```{autodocx-docstring} duck.contrib.websockets.WebSocketView.send_json
```

````

````{py:method} send_ping(data: bytes = b'')
:canonical: duck.contrib.websockets.WebSocketView.send_ping
:async:

```{autodocx-docstring} duck.contrib.websockets.WebSocketView.send_ping
```

````

````{py:method} send_pong(data: bytes = b'')
:canonical: duck.contrib.websockets.WebSocketView.send_pong
:async:

```{autodocx-docstring} duck.contrib.websockets.WebSocketView.send_pong
```

````

````{py:method} send_text(data: str)
:canonical: duck.contrib.websockets.WebSocketView.send_text
:async:

```{autodocx-docstring} duck.contrib.websockets.WebSocketView.send_text
```

````

````{py:property} server
:canonical: duck.contrib.websockets.WebSocketView.server

```{autodocx-docstring} duck.contrib.websockets.WebSocketView.server
```

````

````{py:property} sock
:canonical: duck.contrib.websockets.WebSocketView.sock

```{autodocx-docstring} duck.contrib.websockets.WebSocketView.sock
```

````

````{py:method} strictly_async()
:canonical: duck.contrib.websockets.WebSocketView.strictly_async

````

`````
