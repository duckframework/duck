# {py:mod}`duck.http.core.httpd.http2`

```{py:module} duck.http.core.httpd.http2
```

```{autodocx-docstring} duck.http.core.httpd.http2
:allowtitles:
```

## Submodules

```{toctree}
:titlesonly:
:maxdepth: 1

duck.http.core.httpd.http2.event_handler
duck.http.core.httpd.http2.protocol
```

## Package Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`BaseHTTP2Server <duck.http.core.httpd.http2.BaseHTTP2Server>`
  - ```{autodocx-docstring} duck.http.core.httpd.http2.BaseHTTP2Server
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`H2_SETTINGS_REGEX <duck.http.core.httpd.http2.H2_SETTINGS_REGEX>`
  - ```{autodocx-docstring} duck.http.core.httpd.http2.H2_SETTINGS_REGEX
    :summary:
    ```
* - {py:obj}`H2_UPGRADE_REGEX <duck.http.core.httpd.http2.H2_UPGRADE_REGEX>`
  - ```{autodocx-docstring} duck.http.core.httpd.http2.H2_UPGRADE_REGEX
    :summary:
    ```
````

### API

`````{py:class} BaseHTTP2Server(addr: typing.Tuple[str, int], application: typing.Union[duck.app.app.App, duck.app.microapp.MicroApp], domain: str = None, uses_ipv6: bool = False, enable_ssl: bool = False, ssl_params: typing.Optional[typing.Dict] = None, no_logs: bool = False, workers: typing.Optional[int] = None, force_worker_processes: bool = False)
:canonical: duck.http.core.httpd.http2.BaseHTTP2Server

Bases: {py:obj}`duck.http.core.httpd.httpd.BaseServer`

```{autodocx-docstring} duck.http.core.httpd.http2.BaseHTTP2Server
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.http.core.httpd.http2.BaseHTTP2Server.__init__
```

````{py:method} async_handle_conn(sock: duck.utils.xsocket.xsocket, addr: typing.Tuple[str, int], flowinfo: typing.Optional = None, scopeid: typing.Optional = None, strictly_http2: bool = False) -> None
:canonical: duck.http.core.httpd.http2.BaseHTTP2Server.async_handle_conn
:async:

```{autodocx-docstring} duck.http.core.httpd.http2.BaseHTTP2Server.async_handle_conn
```

````

````{py:method} async_handle_request_data(sock: duck.utils.xsocket.xsocket, addr: typing.Tuple[str, int], request_data: duck.http.request_data.RequestData) -> None
:canonical: duck.http.core.httpd.http2.BaseHTTP2Server.async_handle_request_data
:async:

```{autodocx-docstring} duck.http.core.httpd.http2.BaseHTTP2Server.async_handle_request_data
```

````

````{py:method} async_start_http2_loop(sock: duck.utils.xsocket.xsocket, addr: typing.Tuple[str, int], h2_connection: h2.connection.H2Connection) -> None
:canonical: duck.http.core.httpd.http2.BaseHTTP2Server.async_start_http2_loop
:async:

```{autodocx-docstring} duck.http.core.httpd.http2.BaseHTTP2Server.async_start_http2_loop
```

````

````{py:method} handle_conn(sock: duck.utils.xsocket.xsocket, addr: typing.Tuple[str, int], flowinfo: typing.Optional = None, scopeid: typing.Optional = None, strictly_http2: bool = False) -> None
:canonical: duck.http.core.httpd.http2.BaseHTTP2Server.handle_conn

```{autodocx-docstring} duck.http.core.httpd.http2.BaseHTTP2Server.handle_conn
```

````

````{py:method} handle_request_data(sock: duck.utils.xsocket.xsocket, addr: typing.Tuple[str, int], request_data: duck.http.request_data.RequestData) -> None
:canonical: duck.http.core.httpd.http2.BaseHTTP2Server.handle_request_data

```{autodocx-docstring} duck.http.core.httpd.http2.BaseHTTP2Server.handle_request_data
```

````

````{py:method} set_h2_settings(h2_conn)
:canonical: duck.http.core.httpd.http2.BaseHTTP2Server.set_h2_settings

```{autodocx-docstring} duck.http.core.httpd.http2.BaseHTTP2Server.set_h2_settings
```

````

````{py:method} start_http2_loop(sock: duck.utils.xsocket.xsocket, addr: typing.Tuple[str, int], h2_connection: h2.connection.H2Connection) -> None
:canonical: duck.http.core.httpd.http2.BaseHTTP2Server.start_http2_loop

```{autodocx-docstring} duck.http.core.httpd.http2.BaseHTTP2Server.start_http2_loop
```

````

`````

````{py:data} H2_SETTINGS_REGEX
:canonical: duck.http.core.httpd.http2.H2_SETTINGS_REGEX
:value: >
   'compile(...)'

```{autodocx-docstring} duck.http.core.httpd.http2.H2_SETTINGS_REGEX
```

````

````{py:data} H2_UPGRADE_REGEX
:canonical: duck.http.core.httpd.http2.H2_UPGRADE_REGEX
:value: >
   'compile(...)'

```{autodocx-docstring} duck.http.core.httpd.http2.H2_UPGRADE_REGEX
```

````

````{py:exception} SyncH2ProtocolStartWarning()
:canonical: duck.http.core.httpd.http2.SyncH2ProtocolStartWarning

Bases: {py:obj}`UserWarning`

```{autodocx-docstring} duck.http.core.httpd.http2.SyncH2ProtocolStartWarning
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.http.core.httpd.http2.SyncH2ProtocolStartWarning.__init__
```

````
