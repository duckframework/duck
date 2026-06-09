# {py:mod}`duck.http.core.httpd.servers`

```{py:module} duck.http.core.httpd.servers
```

```{autodocx-docstring} duck.http.core.httpd.servers
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`HTTPServer <duck.http.core.httpd.servers.HTTPServer>`
  - ```{autodocx-docstring} duck.http.core.httpd.servers.HTTPServer
    :summary:
    ```
* - {py:obj}`MicroHTTPServer <duck.http.core.httpd.servers.MicroHTTPServer>`
  - ```{autodocx-docstring} duck.http.core.httpd.servers.MicroHTTPServer
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`BaseServer <duck.http.core.httpd.servers.BaseServer>`
  - ```{autodocx-docstring} duck.http.core.httpd.servers.BaseServer
    :summary:
    ```
````

### API

````{py:data} BaseServer
:canonical: duck.http.core.httpd.servers.BaseServer
:value: >
   None

```{autodocx-docstring} duck.http.core.httpd.servers.BaseServer
```

````

`````{py:class} HTTPServer(addr: typing.Tuple[str, int], application: typing.Union[App, MicroApp], domain: str = None, uses_ipv6: bool = False, enable_ssl: bool = False, ssl_params: typing.Optional[typing.Dict] = None, no_logs: bool = False, workers: typing.Optional[int] = None, force_worker_processes: bool = False)
:canonical: duck.http.core.httpd.servers.HTTPServer

Bases: {py:obj}`duck.http.core.httpd.servers.BaseServer`

```{autodocx-docstring} duck.http.core.httpd.servers.HTTPServer
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.http.core.httpd.servers.HTTPServer.__init__
```

````{py:attribute} __instances
:canonical: duck.http.core.httpd.servers.HTTPServer.__instances
:type: int
:value: >
   0

```{autodocx-docstring} duck.http.core.httpd.servers.HTTPServer.__instances
```

````

````{py:method} reload_ssl_context() -> bool
:canonical: duck.http.core.httpd.servers.HTTPServer.reload_ssl_context

```{autodocx-docstring} duck.http.core.httpd.servers.HTTPServer.reload_ssl_context
```

````

````{py:method} ssl_wrap_socket(client_socket: socket.socket) -> duck.utils.xsocket.ssl_xsocket
:canonical: duck.http.core.httpd.servers.HTTPServer.ssl_wrap_socket

```{autodocx-docstring} duck.http.core.httpd.servers.HTTPServer.ssl_wrap_socket
```

````

`````

````{py:class} MicroHTTPServer(addr: typing.Tuple[str, int], microapp: MicroApp, domain: str = None, uses_ipv6: bool = False, enable_ssl: bool = False, ssl_params: bool = None, no_logs: bool = True, workers: typing.Optional[int] = None, force_worker_processes: bool = False)
:canonical: duck.http.core.httpd.servers.MicroHTTPServer

Bases: {py:obj}`duck.http.core.httpd.httpd.BaseMicroServer`, {py:obj}`duck.http.core.httpd.servers.HTTPServer`

```{autodocx-docstring} duck.http.core.httpd.servers.MicroHTTPServer
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.http.core.httpd.servers.MicroHTTPServer.__init__
```

````
