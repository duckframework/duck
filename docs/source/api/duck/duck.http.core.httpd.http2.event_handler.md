# {py:mod}`duck.http.core.httpd.http2.event_handler`

```{py:module} duck.http.core.httpd.http2.event_handler
```

```{autodocx-docstring} duck.http.core.httpd.http2.event_handler
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`EventHandler <duck.http.core.httpd.http2.event_handler.EventHandler>`
  - ```{autodocx-docstring} duck.http.core.httpd.http2.event_handler.EventHandler
    :summary:
    ```
````

### API

`````{py:class} EventHandler(protocol, server)
:canonical: duck.http.core.httpd.http2.event_handler.EventHandler

```{autodocx-docstring} duck.http.core.httpd.http2.event_handler.EventHandler
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.http.core.httpd.http2.event_handler.EventHandler.__init__
```

````{py:attribute} __slots__
:canonical: duck.http.core.httpd.http2.event_handler.EventHandler.__slots__
:value: >
   None

```{autodocx-docstring} duck.http.core.httpd.http2.event_handler.EventHandler.__slots__
```

````

````{py:method} dispatch_events(events: typing.List)
:canonical: duck.http.core.httpd.http2.event_handler.EventHandler.dispatch_events
:async:

```{autodocx-docstring} duck.http.core.httpd.http2.event_handler.EventHandler.dispatch_events
```

````

````{py:method} entry(data: bytes)
:canonical: duck.http.core.httpd.http2.event_handler.EventHandler.entry
:async:

```{autodocx-docstring} duck.http.core.httpd.http2.event_handler.EventHandler.entry
```

````

````{py:method} execute_synchronously_in_current_thread(func: typing.Callable)
:canonical: duck.http.core.httpd.http2.event_handler.EventHandler.execute_synchronously_in_current_thread
:async:

```{autodocx-docstring} duck.http.core.httpd.http2.event_handler.EventHandler.execute_synchronously_in_current_thread
```

````

````{py:method} on_connection_terminated(event)
:canonical: duck.http.core.httpd.http2.event_handler.EventHandler.on_connection_terminated

```{autodocx-docstring} duck.http.core.httpd.http2.event_handler.EventHandler.on_connection_terminated
```

````

````{py:method} on_new_request(event)
:canonical: duck.http.core.httpd.http2.event_handler.EventHandler.on_new_request

```{autodocx-docstring} duck.http.core.httpd.http2.event_handler.EventHandler.on_new_request
```

````

````{py:method} on_remote_settings_changed(event)
:canonical: duck.http.core.httpd.http2.event_handler.EventHandler.on_remote_settings_changed

```{autodocx-docstring} duck.http.core.httpd.http2.event_handler.EventHandler.on_remote_settings_changed
```

````

````{py:method} on_request_body(event)
:canonical: duck.http.core.httpd.http2.event_handler.EventHandler.on_request_body
:async:

```{autodocx-docstring} duck.http.core.httpd.http2.event_handler.EventHandler.on_request_body
```

````

````{py:method} on_request_complete(event)
:canonical: duck.http.core.httpd.http2.event_handler.EventHandler.on_request_complete
:async:

```{autodocx-docstring} duck.http.core.httpd.http2.event_handler.EventHandler.on_request_complete
```

````

````{py:method} on_stream_reset(stream_id: int)
:canonical: duck.http.core.httpd.http2.event_handler.EventHandler.on_stream_reset

```{autodocx-docstring} duck.http.core.httpd.http2.event_handler.EventHandler.on_stream_reset
```

````

````{py:method} on_window_updated(stream_id, delta)
:canonical: duck.http.core.httpd.http2.event_handler.EventHandler.on_window_updated

```{autodocx-docstring} duck.http.core.httpd.http2.event_handler.EventHandler.on_window_updated
```

````

````{py:method} wait_for_flow_control(stream_id: int)
:canonical: duck.http.core.httpd.http2.event_handler.EventHandler.wait_for_flow_control
:async:

```{autodocx-docstring} duck.http.core.httpd.http2.event_handler.EventHandler.wait_for_flow_control
```

````

`````
