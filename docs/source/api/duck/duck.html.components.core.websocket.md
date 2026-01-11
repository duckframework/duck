# {py:mod}`duck.html.components.core.websocket`

```{py:module} duck.html.components.core.websocket
```

```{autodocx-docstring} duck.html.components.core.websocket
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`EventHandler <duck.html.components.core.websocket.EventHandler>`
  - ```{autodocx-docstring} duck.html.components.core.websocket.EventHandler
    :summary:
    ```
* - {py:obj}`LivelyWebSocketView <duck.html.components.core.websocket.LivelyWebSocketView>`
  - ```{autodocx-docstring} duck.html.components.core.websocket.LivelyWebSocketView
    :summary:
    ```
````

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`generate_uid <duck.html.components.core.websocket.generate_uid>`
  - ```{autodocx-docstring} duck.html.components.core.websocket.generate_uid
    :summary:
    ```
````

### API

`````{py:class} EventHandler(ws_view: duck.html.components.core.websocket.LivelyWebSocketView)
:canonical: duck.html.components.core.websocket.EventHandler

```{autodocx-docstring} duck.html.components.core.websocket.EventHandler
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.html.components.core.websocket.EventHandler.__init__
```

````{py:attribute} __slots__
:canonical: duck.html.components.core.websocket.EventHandler.__slots__
:value: >
   ('ws_view', 'event_map')

```{autodocx-docstring} duck.html.components.core.websocket.EventHandler.__slots__
```

````

````{py:method} dispatch(opcode: duck.html.components.core.opcodes.EventOpCode, data: typing.List[typing.Any])
:canonical: duck.html.components.core.websocket.EventHandler.dispatch
:async:

```{autodocx-docstring} duck.html.components.core.websocket.EventHandler.dispatch
```

````

````{py:method} dispatch_component_event(data: typing.List[typing.Any])
:canonical: duck.html.components.core.websocket.EventHandler.dispatch_component_event
:async:

```{autodocx-docstring} duck.html.components.core.websocket.EventHandler.dispatch_component_event
```

````

````{py:method} handle_js_execution_result(data: typing.List[typing.Any])
:canonical: duck.html.components.core.websocket.EventHandler.handle_js_execution_result
:async:

```{autodocx-docstring} duck.html.components.core.websocket.EventHandler.handle_js_execution_result
```

````

````{py:method} handle_navigation(data: typing.List[typing.Any])
:canonical: duck.html.components.core.websocket.EventHandler.handle_navigation
:async:

```{autodocx-docstring} duck.html.components.core.websocket.EventHandler.handle_navigation
```

````

`````

`````{py:class} LivelyWebSocketView(request, **kwargs)
:canonical: duck.html.components.core.websocket.LivelyWebSocketView

Bases: {py:obj}`duck.contrib.websockets.WebSocketView`

```{autodocx-docstring} duck.html.components.core.websocket.LivelyWebSocketView
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.html.components.core.websocket.LivelyWebSocketView.__init__
```

````{py:attribute} RECEIVE_TIMEOUT
:canonical: duck.html.components.core.websocket.LivelyWebSocketView.RECEIVE_TIMEOUT
:value: >
   240

```{autodocx-docstring} duck.html.components.core.websocket.LivelyWebSocketView.RECEIVE_TIMEOUT
```

````

````{py:attribute} __slots__
:canonical: duck.html.components.core.websocket.LivelyWebSocketView.__slots__
:value: >
   ('request', 'execution_futures', 'event_handler')

```{autodocx-docstring} duck.html.components.core.websocket.LivelyWebSocketView.__slots__
```

````

````{py:method} execute_js(code: str, timeout: typing.Union[int, float] = None, wait_for_result: bool = False) -> typing.Optional[typing.Any]
:canonical: duck.html.components.core.websocket.LivelyWebSocketView.execute_js
:async:

```{autodocx-docstring} duck.html.components.core.websocket.LivelyWebSocketView.execute_js
```

````

````{py:method} get_js_result(code: str, variable: str, timeout: typing.Union[int, float, None] = None) -> typing.Any
:canonical: duck.html.components.core.websocket.LivelyWebSocketView.get_js_result
:async:

```{autodocx-docstring} duck.html.components.core.websocket.LivelyWebSocketView.get_js_result
```

````

````{py:method} on_close(frame)
:canonical: duck.html.components.core.websocket.LivelyWebSocketView.on_close
:async:

```{autodocx-docstring} duck.html.components.core.websocket.LivelyWebSocketView.on_close
```

````

````{py:method} on_open()
:canonical: duck.html.components.core.websocket.LivelyWebSocketView.on_open
:async:

```{autodocx-docstring} duck.html.components.core.websocket.LivelyWebSocketView.on_open
```

````

````{py:method} on_receive(data: bytes, opcode: int)
:canonical: duck.html.components.core.websocket.LivelyWebSocketView.on_receive
:async:

```{autodocx-docstring} duck.html.components.core.websocket.LivelyWebSocketView.on_receive
```

````

````{py:method} send_data(data: typing.Any)
:canonical: duck.html.components.core.websocket.LivelyWebSocketView.send_data
:async:

```{autodocx-docstring} duck.html.components.core.websocket.LivelyWebSocketView.send_data
```

````

````{py:method} send_patches(patches: typing.List)
:canonical: duck.html.components.core.websocket.LivelyWebSocketView.send_patches
:async:

```{autodocx-docstring} duck.html.components.core.websocket.LivelyWebSocketView.send_patches
```

````

````{py:method} serialize_data(data: typing.Any) -> bytes
:canonical: duck.html.components.core.websocket.LivelyWebSocketView.serialize_data
:staticmethod:

```{autodocx-docstring} duck.html.components.core.websocket.LivelyWebSocketView.serialize_data
```

````

````{py:method} unserialize_data(data: bytes) -> typing.Any
:canonical: duck.html.components.core.websocket.LivelyWebSocketView.unserialize_data
:staticmethod:

```{autodocx-docstring} duck.html.components.core.websocket.LivelyWebSocketView.unserialize_data
```

````

`````

````{py:function} generate_uid(length: int = 6) -> str
:canonical: duck.html.components.core.websocket.generate_uid

```{autodocx-docstring} duck.html.components.core.websocket.generate_uid
```
````
