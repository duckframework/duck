# {py:mod}`duck.http.core.wsgi`

```{py:module} duck.http.core.wsgi
```

```{autodocx-docstring} duck.http.core.wsgi
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`WSGI <duck.http.core.wsgi.WSGI>`
  - ```{autodocx-docstring} duck.http.core.wsgi.WSGI
    :summary:
    ```
````

### API

`````{py:class} WSGI(settings: typing.Dict[str, typing.Any])
:canonical: duck.http.core.wsgi.WSGI

```{autodocx-docstring} duck.http.core.wsgi.WSGI
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.http.core.wsgi.WSGI.__init__
```

````{py:method} __call__(application, client_socket: socket.socket, client_address: typing.Tuple[str, int], request_data: duck.http.request_data.RequestData) -> typing.Optional[duck.http.request.HttpRequest]
:canonical: duck.http.core.wsgi.WSGI.__call__

```{autodocx-docstring} duck.http.core.wsgi.WSGI.__call__
```

````

````{py:method} apply_middlewares_to_response(response, request)
:canonical: duck.http.core.wsgi.WSGI.apply_middlewares_to_response

```{autodocx-docstring} duck.http.core.wsgi.WSGI.apply_middlewares_to_response
```

````

````{py:method} django_apply_middlewares_to_response(response: duck.http.core.proxyhandler.HttpProxyResponse, request)
:canonical: duck.http.core.wsgi.WSGI.django_apply_middlewares_to_response

```{autodocx-docstring} duck.http.core.wsgi.WSGI.django_apply_middlewares_to_response
```

````

````{py:method} finalize_response(response, request: typing.Optional[duck.http.request.HttpRequest] = None) -> None
:canonical: duck.http.core.wsgi.WSGI.finalize_response

```{autodocx-docstring} duck.http.core.wsgi.WSGI.finalize_response
```

````

````{py:method} get_request(client_socket: duck.utils.xsocket.xsocket, client_address: typing.Tuple[str, int], request_data: duck.http.request_data.RequestData) -> duck.http.request.HttpRequest
:canonical: duck.http.core.wsgi.WSGI.get_request
:staticmethod:

```{autodocx-docstring} duck.http.core.wsgi.WSGI.get_request
```

````

````{py:method} get_response(request: duck.http.request.HttpRequest) -> duck.http.response.HttpResponse
:canonical: duck.http.core.wsgi.WSGI.get_response

```{autodocx-docstring} duck.http.core.wsgi.WSGI.get_response
```

````

````{py:method} produce_final_response_failsafe(request: duck.http.request.HttpRequest, response_producer_callable: typing.Callable, processor: typing.Optional[RequestProcessor] = None) -> duck.http.response.HttpResponse
:canonical: duck.http.core.wsgi.WSGI.produce_final_response_failsafe

```{autodocx-docstring} duck.http.core.wsgi.WSGI.produce_final_response_failsafe
```

````

````{py:method} send_response(response, client_socket: duck.utils.xsocket.xsocket, request: typing.Optional[duck.http.request.HttpRequest] = None, disable_logging: bool = False)
:canonical: duck.http.core.wsgi.WSGI.send_response

```{autodocx-docstring} duck.http.core.wsgi.WSGI.send_response
```

````

````{py:method} start_response(request: duck.http.request.HttpRequest, response: typing.Optional[duck.http.response.HttpResponse] = None)
:canonical: duck.http.core.wsgi.WSGI.start_response

```{autodocx-docstring} duck.http.core.wsgi.WSGI.start_response
```

````

`````
