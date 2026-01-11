# {py:mod}`duck.contrib.responses.errors`

```{py:module} duck.contrib.responses.errors
```

```{autodocx-docstring} duck.contrib.responses.errors
:allowtitles:
```

## Module Contents

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`get_404_error_response <duck.contrib.responses.errors.get_404_error_response>`
  - ```{autodocx-docstring} duck.contrib.responses.errors.get_404_error_response
    :summary:
    ```
* - {py:obj}`get_bad_gateway_error_response <duck.contrib.responses.errors.get_bad_gateway_error_response>`
  - ```{autodocx-docstring} duck.contrib.responses.errors.get_bad_gateway_error_response
    :summary:
    ```
* - {py:obj}`get_bad_request_error_response <duck.contrib.responses.errors.get_bad_request_error_response>`
  - ```{autodocx-docstring} duck.contrib.responses.errors.get_bad_request_error_response
    :summary:
    ```
* - {py:obj}`get_debug_error_as_html <duck.contrib.responses.errors.get_debug_error_as_html>`
  - ```{autodocx-docstring} duck.contrib.responses.errors.get_debug_error_as_html
    :summary:
    ```
* - {py:obj}`get_method_not_allowed_error_response <duck.contrib.responses.errors.get_method_not_allowed_error_response>`
  - ```{autodocx-docstring} duck.contrib.responses.errors.get_method_not_allowed_error_response
    :summary:
    ```
* - {py:obj}`get_server_error_response <duck.contrib.responses.errors.get_server_error_response>`
  - ```{autodocx-docstring} duck.contrib.responses.errors.get_server_error_response
    :summary:
    ```
* - {py:obj}`get_timeout_error_response <duck.contrib.responses.errors.get_timeout_error_response>`
  - ```{autodocx-docstring} duck.contrib.responses.errors.get_timeout_error_response
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`debug_error_style <duck.contrib.responses.errors.debug_error_style>`
  - ```{autodocx-docstring} duck.contrib.responses.errors.debug_error_style
    :summary:
    ```
````

### API

````{py:data} debug_error_style
:canonical: duck.contrib.responses.errors.debug_error_style
:value: <Multiline-String>

```{autodocx-docstring} duck.contrib.responses.errors.debug_error_style
```

````

````{py:function} get_404_error_response(request: duck.http.request.HttpRequest)
:canonical: duck.contrib.responses.errors.get_404_error_response

```{autodocx-docstring} duck.contrib.responses.errors.get_404_error_response
```
````

````{py:function} get_bad_gateway_error_response(exception: typing.Optional[Exception], request: typing.Optional = None)
:canonical: duck.contrib.responses.errors.get_bad_gateway_error_response

```{autodocx-docstring} duck.contrib.responses.errors.get_bad_gateway_error_response
```
````

````{py:function} get_bad_request_error_response(exception: Exception, request: typing.Optional[duck.http.request.HttpRequest] = None)
:canonical: duck.contrib.responses.errors.get_bad_request_error_response

```{autodocx-docstring} duck.contrib.responses.errors.get_bad_request_error_response
```
````

````{py:function} get_debug_error_as_html(exception: Exception, request: typing.Optional = None)
:canonical: duck.contrib.responses.errors.get_debug_error_as_html

```{autodocx-docstring} duck.contrib.responses.errors.get_debug_error_as_html
```
````

````{py:function} get_method_not_allowed_error_response(request: duck.http.request.HttpRequest, route_info: typing.Optional[typing.Dict[str, typing.Any]] = None)
:canonical: duck.contrib.responses.errors.get_method_not_allowed_error_response

```{autodocx-docstring} duck.contrib.responses.errors.get_method_not_allowed_error_response
```
````

````{py:function} get_server_error_response(exception: Exception, request: typing.Optional = None)
:canonical: duck.contrib.responses.errors.get_server_error_response

```{autodocx-docstring} duck.contrib.responses.errors.get_server_error_response
```
````

````{py:function} get_timeout_error_response(timeout: typing.Optional[typing.Union[int, float]]) -> duck.http.response.HttpRequestTimeoutResponse
:canonical: duck.contrib.responses.errors.get_timeout_error_response

```{autodocx-docstring} duck.contrib.responses.errors.get_timeout_error_response
```
````
