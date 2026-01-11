# {py:mod}`duck.http.core.response_finalizer`

```{py:module} duck.http.core.response_finalizer
```

```{autodocx-docstring} duck.http.core.response_finalizer
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`AsyncResponseFinalizer <duck.http.core.response_finalizer.AsyncResponseFinalizer>`
  - ```{autodocx-docstring} duck.http.core.response_finalizer.AsyncResponseFinalizer
    :summary:
    ```
* - {py:obj}`ResponseFinalizer <duck.http.core.response_finalizer.ResponseFinalizer>`
  - ```{autodocx-docstring} duck.http.core.response_finalizer.ResponseFinalizer
    :summary:
    ```
````

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`set_compressable_iter_content <duck.http.core.response_finalizer.set_compressable_iter_content>`
  - ```{autodocx-docstring} duck.http.core.response_finalizer.set_compressable_iter_content
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`CUSTOM_TEMPLATES <duck.http.core.response_finalizer.CUSTOM_TEMPLATES>`
  - ```{autodocx-docstring} duck.http.core.response_finalizer.CUSTOM_TEMPLATES
    :summary:
    ```
* - {py:obj}`async_response_finalizer <duck.http.core.response_finalizer.async_response_finalizer>`
  - ```{autodocx-docstring} duck.http.core.response_finalizer.async_response_finalizer
    :summary:
    ```
* - {py:obj}`response_finalizer <duck.http.core.response_finalizer.response_finalizer>`
  - ```{autodocx-docstring} duck.http.core.response_finalizer.response_finalizer
    :summary:
    ```
````

### API

`````{py:class} AsyncResponseFinalizer
:canonical: duck.http.core.response_finalizer.AsyncResponseFinalizer

Bases: {py:obj}`duck.http.core.response_finalizer.ResponseFinalizer`

```{autodocx-docstring} duck.http.core.response_finalizer.AsyncResponseFinalizer
```

````{py:method} do_content_compression(response, request) -> None
:canonical: duck.http.core.response_finalizer.AsyncResponseFinalizer.do_content_compression
:async:

```{autodocx-docstring} duck.http.core.response_finalizer.AsyncResponseFinalizer.do_content_compression
```

````

````{py:method} do_set_streaming_range(response, request)
:canonical: duck.http.core.response_finalizer.AsyncResponseFinalizer.do_set_streaming_range
:async:

```{autodocx-docstring} duck.http.core.response_finalizer.AsyncResponseFinalizer.do_set_streaming_range
```

````

````{py:method} finalize_response(response: duck.http.response.HttpResponse, request: duck.http.request.HttpRequest, do_set_streaming_range: bool = True, do_content_compression: bool = True)
:canonical: duck.http.core.response_finalizer.AsyncResponseFinalizer.finalize_response
:async:

```{autodocx-docstring} duck.http.core.response_finalizer.AsyncResponseFinalizer.finalize_response
```

````

`````

````{py:data} CUSTOM_TEMPLATES
:canonical: duck.http.core.response_finalizer.CUSTOM_TEMPLATES
:type: typing.Dict[int, typing.Callable]
:value: >
   None

```{autodocx-docstring} duck.http.core.response_finalizer.CUSTOM_TEMPLATES
```

````

`````{py:class} ResponseFinalizer
:canonical: duck.http.core.response_finalizer.ResponseFinalizer

```{autodocx-docstring} duck.http.core.response_finalizer.ResponseFinalizer
```

````{py:method} do_content_compression(response, request) -> None
:canonical: duck.http.core.response_finalizer.ResponseFinalizer.do_content_compression

```{autodocx-docstring} duck.http.core.response_finalizer.ResponseFinalizer.do_content_compression
```

````

````{py:method} do_request_response_transformation(response: duck.http.response.HttpResponse, request: duck.http.request.HttpRequest)
:canonical: duck.http.core.response_finalizer.ResponseFinalizer.do_request_response_transformation

```{autodocx-docstring} duck.http.core.response_finalizer.ResponseFinalizer.do_request_response_transformation
```

````

````{py:method} do_set_connection_mode(response, request) -> None
:canonical: duck.http.core.response_finalizer.ResponseFinalizer.do_set_connection_mode

```{autodocx-docstring} duck.http.core.response_finalizer.ResponseFinalizer.do_set_connection_mode
```

````

````{py:method} do_set_content_headers(response, request) -> None
:canonical: duck.http.core.response_finalizer.ResponseFinalizer.do_set_content_headers

```{autodocx-docstring} duck.http.core.response_finalizer.ResponseFinalizer.do_set_content_headers
```

````

````{py:method} do_set_extra_headers(response, request) -> None
:canonical: duck.http.core.response_finalizer.ResponseFinalizer.do_set_extra_headers

```{autodocx-docstring} duck.http.core.response_finalizer.ResponseFinalizer.do_set_extra_headers
```

````

````{py:method} do_set_fixed_headers(response, request) -> None
:canonical: duck.http.core.response_finalizer.ResponseFinalizer.do_set_fixed_headers

```{autodocx-docstring} duck.http.core.response_finalizer.ResponseFinalizer.do_set_fixed_headers
```

````

````{py:method} do_set_streaming_range(response, request)
:canonical: duck.http.core.response_finalizer.ResponseFinalizer.do_set_streaming_range

```{autodocx-docstring} duck.http.core.response_finalizer.ResponseFinalizer.do_set_streaming_range
```

````

````{py:method} finalize_response(response: duck.http.response.HttpResponse, request: duck.http.request.HttpRequest, do_set_streaming_range: bool = True, do_content_compression: bool = True)
:canonical: duck.http.core.response_finalizer.ResponseFinalizer.finalize_response

```{autodocx-docstring} duck.http.core.response_finalizer.ResponseFinalizer.finalize_response
```

````

`````

````{py:data} async_response_finalizer
:canonical: duck.http.core.response_finalizer.async_response_finalizer
:value: >
   'AsyncResponseFinalizer(...)'

```{autodocx-docstring} duck.http.core.response_finalizer.async_response_finalizer
```

````

````{py:data} response_finalizer
:canonical: duck.http.core.response_finalizer.response_finalizer
:value: >
   'ResponseFinalizer(...)'

```{autodocx-docstring} duck.http.core.response_finalizer.response_finalizer
```

````

````{py:function} set_compressable_iter_content(response)
:canonical: duck.http.core.response_finalizer.set_compressable_iter_content

```{autodocx-docstring} duck.http.core.response_finalizer.set_compressable_iter_content
```
````
