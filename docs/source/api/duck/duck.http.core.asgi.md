# {py:mod}`duck.http.core.asgi`

```{py:module} duck.http.core.asgi
```

```{autodocx-docstring} duck.http.core.asgi
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`ASGI <duck.http.core.asgi.ASGI>`
  - ```{autodocx-docstring} duck.http.core.asgi.ASGI
    :summary:
    ```
````

### API

`````{py:class} ASGI(settings: typing.Dict[str, typing.Any])
:canonical: duck.http.core.asgi.ASGI

```{autodocx-docstring} duck.http.core.asgi.ASGI
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.http.core.asgi.ASGI.__init__
```

````{py:method} __call__(application, client_socket: socket.socket, client_address: typing.Tuple[str, int], request_data: duck.http.request_data.RequestData) -> typing.Optional[duck.http.request.HttpRequest]
:canonical: duck.http.core.asgi.ASGI.__call__
:async:

```{autodocx-docstring} duck.http.core.asgi.ASGI.__call__
```

````

````{py:method} apply_middlewares_to_response(response, request)
:canonical: duck.http.core.asgi.ASGI.apply_middlewares_to_response
:async:

```{autodocx-docstring} duck.http.core.asgi.ASGI.apply_middlewares_to_response
```

````

````{py:method} django_apply_middlewares_to_response(response: duck.http.core.proxyhandler.HttpProxyResponse, request)
:canonical: duck.http.core.asgi.ASGI.django_apply_middlewares_to_response
:async:

```{autodocx-docstring} duck.http.core.asgi.ASGI.django_apply_middlewares_to_response
```

````

````{py:method} finalize_response(response, request: typing.Optional[duck.http.request.HttpRequest] = None)
:canonical: duck.http.core.asgi.ASGI.finalize_response
:async:

```{autodocx-docstring} duck.http.core.asgi.ASGI.finalize_response
```

````

````{py:method} get_request(client_socket: duck.utils.xsocket.xsocket, client_address: typing.Tuple[str, int], request_data: duck.http.request_data.RequestData) -> duck.http.request.HttpRequest
:canonical: duck.http.core.asgi.ASGI.get_request
:async:
:staticmethod:

```{autodocx-docstring} duck.http.core.asgi.ASGI.get_request
```

````

````{py:method} get_response(request: duck.http.request.HttpRequest) -> duck.http.response.HttpResponse
:canonical: duck.http.core.asgi.ASGI.get_response
:async:

```{autodocx-docstring} duck.http.core.asgi.ASGI.get_response
```

````

````{py:method} handle_django_connection_upgrade(upgrade_request: duck.http.request.HttpRequest, upgrade_response: duck.http.core.proxyhandler.HttpProxyResponse, protocol_receive_timeout: typing.Union[int, float] = 10, protocol_receive_buffer: int = 4096)
:canonical: duck.http.core.asgi.ASGI.handle_django_connection_upgrade
:async:

```{autodocx-docstring} duck.http.core.asgi.ASGI.handle_django_connection_upgrade
```

````

````{py:method} produce_final_response_failsafe(request: duck.http.request.HttpRequest, response_producer_callable: typing.Callable, processor: typing.Optional[AsyncRequestProcessor] = None) -> duck.http.response.HttpResponse
:canonical: duck.http.core.asgi.ASGI.produce_final_response_failsafe
:async:

```{autodocx-docstring} duck.http.core.asgi.ASGI.produce_final_response_failsafe
```

````

````{py:method} send_response(response, client_socket: duck.utils.xsocket.xsocket, request: typing.Optional[duck.http.request.HttpRequest] = None, disable_logging: bool = False)
:canonical: duck.http.core.asgi.ASGI.send_response
:async:

```{autodocx-docstring} duck.http.core.asgi.ASGI.send_response
```

````

````{py:method} start_response(request: duck.http.request.HttpRequest, response: typing.Optional[duck.http.response.HttpResponse] = None)
:canonical: duck.http.core.asgi.ASGI.start_response
:async:

```{autodocx-docstring} duck.http.core.asgi.ASGI.start_response
```

````

`````
