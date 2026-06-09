# {py:mod}`duck.http.core.httpd.httpd`

```{py:module} duck.http.core.httpd.httpd
```

```{autodocx-docstring} duck.http.core.httpd.httpd
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`BaseMicroServer <duck.http.core.httpd.httpd.BaseMicroServer>`
  - ```{autodocx-docstring} duck.http.core.httpd.httpd.BaseMicroServer
    :summary:
    ```
* - {py:obj}`BaseServer <duck.http.core.httpd.httpd.BaseServer>`
  - ```{autodocx-docstring} duck.http.core.httpd.httpd.BaseServer
    :summary:
    ```
````

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`call_request_handling_executor <duck.http.core.httpd.httpd.call_request_handling_executor>`
  - ```{autodocx-docstring} duck.http.core.httpd.httpd.call_request_handling_executor
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`CONNECTION_MODE <duck.http.core.httpd.httpd.CONNECTION_MODE>`
  - ```{autodocx-docstring} duck.http.core.httpd.httpd.CONNECTION_MODE
    :summary:
    ```
* - {py:obj}`KEEP_ALIVE_PATTERN <duck.http.core.httpd.httpd.KEEP_ALIVE_PATTERN>`
  - ```{autodocx-docstring} duck.http.core.httpd.httpd.KEEP_ALIVE_PATTERN
    :summary:
    ```
* - {py:obj}`KEEP_ALIVE_TIMEOUT <duck.http.core.httpd.httpd.KEEP_ALIVE_TIMEOUT>`
  - ```{autodocx-docstring} duck.http.core.httpd.httpd.KEEP_ALIVE_TIMEOUT
    :summary:
    ```
* - {py:obj}`SSL_HANDSHAKE_TIMEOUT <duck.http.core.httpd.httpd.SSL_HANDSHAKE_TIMEOUT>`
  - ```{autodocx-docstring} duck.http.core.httpd.httpd.SSL_HANDSHAKE_TIMEOUT
    :summary:
    ```
````

### API

`````{py:class} BaseMicroServer(addr: typing.Tuple[str, int], application: typing.Union[duck.app.app.App, duck.app.microapp.MicroApp], domain: str = None, uses_ipv6: bool = False, enable_ssl: bool = False, ssl_params: typing.Optional[typing.Dict] = None, no_logs: bool = False, workers: typing.Optional[int] = None, force_worker_processes: bool = False)
:canonical: duck.http.core.httpd.httpd.BaseMicroServer

Bases: {py:obj}`duck.http.core.httpd.httpd.BaseServer`

```{autodocx-docstring} duck.http.core.httpd.httpd.BaseMicroServer
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.http.core.httpd.httpd.BaseMicroServer.__init__
```

````{py:method} async_handle_request_data(sock: duck.utils.xsocket.xsocket, addr: typing.Tuple[str, int], request_data: duck.http.request_data.RequestData) -> None
:canonical: duck.http.core.httpd.httpd.BaseMicroServer.async_handle_request_data
:async:

```{autodocx-docstring} duck.http.core.httpd.httpd.BaseMicroServer.async_handle_request_data
```

````

````{py:method} handle_request_data(sock: duck.utils.xsocket.xsocket, addr: typing.Tuple[str, int], request_data: duck.http.request_data.RequestData) -> None
:canonical: duck.http.core.httpd.httpd.BaseMicroServer.handle_request_data

```{autodocx-docstring} duck.http.core.httpd.httpd.BaseMicroServer.handle_request_data
```

````

````{py:method} set_microapp(microapp)
:canonical: duck.http.core.httpd.httpd.BaseMicroServer.set_microapp

```{autodocx-docstring} duck.http.core.httpd.httpd.BaseMicroServer.set_microapp
```

````

`````

`````{py:class} BaseServer(addr: typing.Tuple[str, int], application: typing.Union[duck.app.app.App, duck.app.microapp.MicroApp], domain: str = None, uses_ipv6: bool = False, enable_ssl: bool = False, ssl_params: typing.Optional[typing.Dict] = None, no_logs: bool = False, workers: typing.Optional[int] = None, force_worker_processes: bool = False)
:canonical: duck.http.core.httpd.httpd.BaseServer

```{autodocx-docstring} duck.http.core.httpd.httpd.BaseServer
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.http.core.httpd.httpd.BaseServer.__init__
```

````{py:method} accept_and_handle() -> socket.socket
:canonical: duck.http.core.httpd.httpd.BaseServer.accept_and_handle

```{autodocx-docstring} duck.http.core.httpd.httpd.BaseServer.accept_and_handle
```

````

````{py:method} async_do_request_timeout(sock: duck.utils.xsocket.xsocket, addr: typing.Tuple[str, int])
:canonical: duck.http.core.httpd.httpd.BaseServer.async_do_request_timeout
:async:

```{autodocx-docstring} duck.http.core.httpd.httpd.BaseServer.async_do_request_timeout
```

````

````{py:method} async_handle_conn(sock: duck.utils.xsocket.xsocket, addr: typing.Tuple[str, int], flowinfo: typing.Optional = None, scopeid: typing.Optional = None) -> None
:canonical: duck.http.core.httpd.httpd.BaseServer.async_handle_conn
:async:

```{autodocx-docstring} duck.http.core.httpd.httpd.BaseServer.async_handle_conn
```

````

````{py:method} async_handle_keep_alive_conn(sock: duck.utils.xsocket.xsocket, addr: typing.Tuple[str, int]) -> None
:canonical: duck.http.core.httpd.httpd.BaseServer.async_handle_keep_alive_conn
:async:

```{autodocx-docstring} duck.http.core.httpd.httpd.BaseServer.async_handle_keep_alive_conn
```

````

````{py:method} async_handle_request_data(sock: duck.utils.xsocket.xsocket, addr: typing.Tuple[str, int], request_data: duck.http.request_data.RequestData) -> None
:canonical: duck.http.core.httpd.httpd.BaseServer.async_handle_request_data
:async:

```{autodocx-docstring} duck.http.core.httpd.httpd.BaseServer.async_handle_request_data
```

````

````{py:method} async_process_data(sock: duck.utils.xsocket.xsocket, addr: typing.Tuple[str, int], request_data: duck.http.request_data.RequestData) -> None
:canonical: duck.http.core.httpd.httpd.BaseServer.async_process_data
:async:

```{autodocx-docstring} duck.http.core.httpd.httpd.BaseServer.async_process_data
```

````

````{py:method} do_request_timeout(sock: duck.utils.xsocket.xsocket, addr: typing.Tuple[str, int])
:canonical: duck.http.core.httpd.httpd.BaseServer.do_request_timeout

```{autodocx-docstring} duck.http.core.httpd.httpd.BaseServer.do_request_timeout
```

````

````{py:method} handle_conn(sock: duck.utils.xsocket.xsocket, addr: typing.Tuple[str, int], flowinfo: typing.Optional = None, scopeid: typing.Optional = None) -> None
:canonical: duck.http.core.httpd.httpd.BaseServer.handle_conn

```{autodocx-docstring} duck.http.core.httpd.httpd.BaseServer.handle_conn
```

````

````{py:method} handle_keep_alive_conn(sock: duck.utils.xsocket.xsocket, addr: typing.Tuple[str, int]) -> None
:canonical: duck.http.core.httpd.httpd.BaseServer.handle_keep_alive_conn

```{autodocx-docstring} duck.http.core.httpd.httpd.BaseServer.handle_keep_alive_conn
```

````

````{py:method} handle_request_data(sock: duck.utils.xsocket.xsocket, addr: typing.Tuple[str, int], request_data: duck.http.request_data.RequestData) -> None
:canonical: duck.http.core.httpd.httpd.BaseServer.handle_request_data

```{autodocx-docstring} duck.http.core.httpd.httpd.BaseServer.handle_request_data
```

````

````{py:method} process_data(sock: duck.utils.xsocket.xsocket, addr: typing.Tuple[str, int], request_data: duck.http.request_data.RequestData) -> None
:canonical: duck.http.core.httpd.httpd.BaseServer.process_data

```{autodocx-docstring} duck.http.core.httpd.httpd.BaseServer.process_data
```

````

````{py:property} running
:canonical: duck.http.core.httpd.httpd.BaseServer.running

```{autodocx-docstring} duck.http.core.httpd.httpd.BaseServer.running
```

````

````{py:property} sock
:canonical: duck.http.core.httpd.httpd.BaseServer.sock

```{autodocx-docstring} duck.http.core.httpd.httpd.BaseServer.sock
```

````

````{py:method} start_server(on_server_start_fn: typing.Optional[typing.Callable] = None)
:canonical: duck.http.core.httpd.httpd.BaseServer.start_server

```{autodocx-docstring} duck.http.core.httpd.httpd.BaseServer.start_server
```

````

````{py:method} start_server_loop(interval_fn: typing.Optional[typing.Callable] = None)
:canonical: duck.http.core.httpd.httpd.BaseServer.start_server_loop

```{autodocx-docstring} duck.http.core.httpd.httpd.BaseServer.start_server_loop
```

````

````{py:method} stop_server(log_to_console: bool = True, wait: bool = True)
:canonical: duck.http.core.httpd.httpd.BaseServer.stop_server

```{autodocx-docstring} duck.http.core.httpd.httpd.BaseServer.stop_server
```

````

````{py:property} worker_processes
:canonical: duck.http.core.httpd.httpd.BaseServer.worker_processes
:type: typing.List[multiprocessing.Process]

```{autodocx-docstring} duck.http.core.httpd.httpd.BaseServer.worker_processes
```

````

````{py:property} worker_threads
:canonical: duck.http.core.httpd.httpd.BaseServer.worker_threads
:type: typing.List[threading.Thread]

```{autodocx-docstring} duck.http.core.httpd.httpd.BaseServer.worker_threads
```

````

`````

````{py:data} CONNECTION_MODE
:canonical: duck.http.core.httpd.httpd.CONNECTION_MODE
:value: >
   None

```{autodocx-docstring} duck.http.core.httpd.httpd.CONNECTION_MODE
```

````

````{py:data} KEEP_ALIVE_PATTERN
:canonical: duck.http.core.httpd.httpd.KEEP_ALIVE_PATTERN
:value: >
   'compile(...)'

```{autodocx-docstring} duck.http.core.httpd.httpd.KEEP_ALIVE_PATTERN
```

````

````{py:data} KEEP_ALIVE_TIMEOUT
:canonical: duck.http.core.httpd.httpd.KEEP_ALIVE_TIMEOUT
:value: >
   None

```{autodocx-docstring} duck.http.core.httpd.httpd.KEEP_ALIVE_TIMEOUT
```

````

````{py:data} SSL_HANDSHAKE_TIMEOUT
:canonical: duck.http.core.httpd.httpd.SSL_HANDSHAKE_TIMEOUT
:value: >
   0.3

```{autodocx-docstring} duck.http.core.httpd.httpd.SSL_HANDSHAKE_TIMEOUT
```

````

````{py:function} call_request_handling_executor(task: typing.Union[typing.Callable, typing.Coroutine])
:canonical: duck.http.core.httpd.httpd.call_request_handling_executor

```{autodocx-docstring} duck.http.core.httpd.httpd.call_request_handling_executor
```
````
