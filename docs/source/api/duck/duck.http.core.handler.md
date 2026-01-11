# {py:mod}`duck.http.core.handler`

```{py:module} duck.http.core.handler
```

```{autodocx-docstring} duck.http.core.handler
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`ResponseHandler <duck.http.core.handler.ResponseHandler>`
  - ```{autodocx-docstring} duck.http.core.handler.ResponseHandler
    :summary:
    ```
````

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`get_django_formatted_log <duck.http.core.handler.get_django_formatted_log>`
  - ```{autodocx-docstring} duck.http.core.handler.get_django_formatted_log
    :summary:
    ```
* - {py:obj}`get_duck_formatted_log <duck.http.core.handler.get_duck_formatted_log>`
  - ```{autodocx-docstring} duck.http.core.handler.get_duck_formatted_log
    :summary:
    ```
* - {py:obj}`get_status_code_debug_color <duck.http.core.handler.get_status_code_debug_color>`
  - ```{autodocx-docstring} duck.http.core.handler.get_status_code_debug_color
    :summary:
    ```
* - {py:obj}`get_status_debug_msg <duck.http.core.handler.get_status_debug_msg>`
  - ```{autodocx-docstring} duck.http.core.handler.get_status_debug_msg
    :summary:
    ```
* - {py:obj}`log_response <duck.http.core.handler.log_response>`
  - ```{autodocx-docstring} duck.http.core.handler.log_response
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`response_handler <duck.http.core.handler.response_handler>`
  - ```{autodocx-docstring} duck.http.core.handler.response_handler
    :summary:
    ```
````

### API

`````{py:class} ResponseHandler
:canonical: duck.http.core.handler.ResponseHandler

```{autodocx-docstring} duck.http.core.handler.ResponseHandler
```

````{py:method} _async_send_response(response: typing.Union[duck.http.response.BaseResponse, duck.http.response.HttpResponse], sock: duck.utils.xsocket.xsocket, suppress_errors: bool = False)
:canonical: duck.http.core.handler.ResponseHandler._async_send_response
:async:

```{autodocx-docstring} duck.http.core.handler.ResponseHandler._async_send_response
```

````

````{py:method} _send_response(response: typing.Union[duck.http.response.BaseResponse, duck.http.response.HttpResponse], sock: duck.utils.xsocket.xsocket, suppress_errors: bool = False)
:canonical: duck.http.core.handler.ResponseHandler._send_response

```{autodocx-docstring} duck.http.core.handler.ResponseHandler._send_response
```

````

````{py:method} async_close_streaming_response(response)
:canonical: duck.http.core.handler.ResponseHandler.async_close_streaming_response
:async:
:classmethod:

```{autodocx-docstring} duck.http.core.handler.ResponseHandler.async_close_streaming_response
```

````

````{py:method} async_send_http2_response(response: typing.Union[duck.http.response.BaseResponse, duck.http.response.HttpResponse], stream_id: int, sock: duck.utils.xsocket.xsocket, request: typing.Optional[duck.http.request.HttpRequest] = None, disable_logging: bool = False, suppress_errors: bool = False) -> None
:canonical: duck.http.core.handler.ResponseHandler.async_send_http2_response
:async:

```{autodocx-docstring} duck.http.core.handler.ResponseHandler.async_send_http2_response
```

````

````{py:method} async_send_response(response: typing.Union[duck.http.response.BaseResponse, duck.http.response.HttpResponse], sock: duck.utils.xsocket.xsocket, request: typing.Optional[duck.http.request.HttpRequest] = None, disable_logging: bool = False, suppress_errors: bool = False, strictly_http1: bool = False) -> None
:canonical: duck.http.core.handler.ResponseHandler.async_send_response
:async:

```{autodocx-docstring} duck.http.core.handler.ResponseHandler.async_send_response
```

````

````{py:method} auto_log_response(response, request)
:canonical: duck.http.core.handler.ResponseHandler.auto_log_response
:classmethod:

```{autodocx-docstring} duck.http.core.handler.ResponseHandler.auto_log_response
```

````

````{py:method} close_streaming_response(response)
:canonical: duck.http.core.handler.ResponseHandler.close_streaming_response
:classmethod:

```{autodocx-docstring} duck.http.core.handler.ResponseHandler.close_streaming_response
```

````

````{py:method} send_http2_response(response: typing.Union[duck.http.response.BaseResponse, duck.http.response.HttpResponse], stream_id: int, sock: duck.utils.xsocket.xsocket, request: typing.Optional[duck.http.request.HttpRequest] = None, disable_logging: bool = False, suppress_errors: bool = False, return_future: bool = False) -> typing.Optional[duck.utils.asyncio.eventloop.SyncFuture]
:canonical: duck.http.core.handler.ResponseHandler.send_http2_response

```{autodocx-docstring} duck.http.core.handler.ResponseHandler.send_http2_response
```

````

````{py:method} send_response(response: typing.Union[duck.http.response.BaseResponse, duck.http.response.HttpResponse], sock: duck.utils.xsocket.xsocket, request: typing.Optional[duck.http.request.HttpRequest] = None, disable_logging: bool = False, suppress_errors: bool = False, strictly_http1: bool = False) -> None
:canonical: duck.http.core.handler.ResponseHandler.send_response

```{autodocx-docstring} duck.http.core.handler.ResponseHandler.send_response
```

````

`````

````{py:function} get_django_formatted_log(response: duck.http.response.HttpResponse, request: typing.Optional[duck.http.request.HttpRequest] = None, debug_message: typing.Optional[typing.Union[str, typing.List[str]]] = None) -> str
:canonical: duck.http.core.handler.get_django_formatted_log

```{autodocx-docstring} duck.http.core.handler.get_django_formatted_log
```
````

````{py:function} get_duck_formatted_log(response: duck.http.response.HttpResponse, request: typing.Optional[duck.http.request.HttpRequest] = None, debug_message: typing.Optional[typing.Union[str, typing.List[str]]] = None) -> str
:canonical: duck.http.core.handler.get_duck_formatted_log

```{autodocx-docstring} duck.http.core.handler.get_duck_formatted_log
```
````

````{py:function} get_status_code_debug_color(status_code: int) -> str
:canonical: duck.http.core.handler.get_status_code_debug_color

```{autodocx-docstring} duck.http.core.handler.get_status_code_debug_color
```
````

````{py:function} get_status_debug_msg(response: duck.http.response.HttpResponse, request: duck.http.request.HttpRequest) -> typing.Optional[str]
:canonical: duck.http.core.handler.get_status_debug_msg

```{autodocx-docstring} duck.http.core.handler.get_status_debug_msg
```
````

````{py:function} log_response(response: typing.Union[duck.http.response.BaseResponse, duck.http.response.HttpResponse], request: typing.Optional[duck.http.request.HttpRequest] = None, debug_message: typing.Optional[typing.Union[str, typing.List[str]]] = None) -> None
:canonical: duck.http.core.handler.log_response

```{autodocx-docstring} duck.http.core.handler.log_response
```
````

````{py:data} response_handler
:canonical: duck.http.core.handler.response_handler
:value: >
   'ResponseHandler(...)'

```{autodocx-docstring} duck.http.core.handler.response_handler
```

````
