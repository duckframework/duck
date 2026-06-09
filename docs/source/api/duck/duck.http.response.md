# {py:mod}`duck.http.response`

```{py:module} duck.http.response
```

```{autodocx-docstring} duck.http.response
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`BaseResponse <duck.http.response.BaseResponse>`
  - ```{autodocx-docstring} duck.http.response.BaseResponse
    :summary:
    ```
* - {py:obj}`ComponentResponse <duck.http.response.ComponentResponse>`
  - ```{autodocx-docstring} duck.http.response.ComponentResponse
    :summary:
    ```
* - {py:obj}`FileResponse <duck.http.response.FileResponse>`
  - ```{autodocx-docstring} duck.http.response.FileResponse
    :summary:
    ```
* - {py:obj}`HttpBadGatewayResponse <duck.http.response.HttpBadGatewayResponse>`
  - ```{autodocx-docstring} duck.http.response.HttpBadGatewayResponse
    :summary:
    ```
* - {py:obj}`HttpBadRequestResponse <duck.http.response.HttpBadRequestResponse>`
  - ```{autodocx-docstring} duck.http.response.HttpBadRequestResponse
    :summary:
    ```
* - {py:obj}`HttpBadRequestSyntaxResponse <duck.http.response.HttpBadRequestSyntaxResponse>`
  - ```{autodocx-docstring} duck.http.response.HttpBadRequestSyntaxResponse
    :summary:
    ```
* - {py:obj}`HttpErrorRequestResponse <duck.http.response.HttpErrorRequestResponse>`
  - ```{autodocx-docstring} duck.http.response.HttpErrorRequestResponse
    :summary:
    ```
* - {py:obj}`HttpForbiddenRequestResponse <duck.http.response.HttpForbiddenRequestResponse>`
  - ```{autodocx-docstring} duck.http.response.HttpForbiddenRequestResponse
    :summary:
    ```
* - {py:obj}`HttpMethodNotAllowedResponse <duck.http.response.HttpMethodNotAllowedResponse>`
  - ```{autodocx-docstring} duck.http.response.HttpMethodNotAllowedResponse
    :summary:
    ```
* - {py:obj}`HttpNotFoundResponse <duck.http.response.HttpNotFoundResponse>`
  - ```{autodocx-docstring} duck.http.response.HttpNotFoundResponse
    :summary:
    ```
* - {py:obj}`HttpRangeNotSatisfiableResponse <duck.http.response.HttpRangeNotSatisfiableResponse>`
  - ```{autodocx-docstring} duck.http.response.HttpRangeNotSatisfiableResponse
    :summary:
    ```
* - {py:obj}`HttpRedirectResponse <duck.http.response.HttpRedirectResponse>`
  - ```{autodocx-docstring} duck.http.response.HttpRedirectResponse
    :summary:
    ```
* - {py:obj}`HttpRequestTimeoutResponse <duck.http.response.HttpRequestTimeoutResponse>`
  - ```{autodocx-docstring} duck.http.response.HttpRequestTimeoutResponse
    :summary:
    ```
* - {py:obj}`HttpResponse <duck.http.response.HttpResponse>`
  - ```{autodocx-docstring} duck.http.response.HttpResponse
    :summary:
    ```
* - {py:obj}`HttpServerErrorResponse <duck.http.response.HttpServerErrorResponse>`
  - ```{autodocx-docstring} duck.http.response.HttpServerErrorResponse
    :summary:
    ```
* - {py:obj}`HttpSwitchProtocolResponse <duck.http.response.HttpSwitchProtocolResponse>`
  - ```{autodocx-docstring} duck.http.response.HttpSwitchProtocolResponse
    :summary:
    ```
* - {py:obj}`HttpTooManyRequestsResponse <duck.http.response.HttpTooManyRequestsResponse>`
  - ```{autodocx-docstring} duck.http.response.HttpTooManyRequestsResponse
    :summary:
    ```
* - {py:obj}`HttpUnsupportedVersionResponse <duck.http.response.HttpUnsupportedVersionResponse>`
  - ```{autodocx-docstring} duck.http.response.HttpUnsupportedVersionResponse
    :summary:
    ```
* - {py:obj}`JsonResponse <duck.http.response.JsonResponse>`
  - ```{autodocx-docstring} duck.http.response.JsonResponse
    :summary:
    ```
* - {py:obj}`StreamingHttpResponse <duck.http.response.StreamingHttpResponse>`
  - ```{autodocx-docstring} duck.http.response.StreamingHttpResponse
    :summary:
    ```
* - {py:obj}`StreamingRangeHttpResponse <duck.http.response.StreamingRangeHttpResponse>`
  - ```{autodocx-docstring} duck.http.response.StreamingRangeHttpResponse
    :summary:
    ```
* - {py:obj}`TemplateResponse <duck.http.response.TemplateResponse>`
  - ```{autodocx-docstring} duck.http.response.TemplateResponse
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`NEGATIVE_RANGE_PATTERN <duck.http.response.NEGATIVE_RANGE_PATTERN>`
  - ```{autodocx-docstring} duck.http.response.NEGATIVE_RANGE_PATTERN
    :summary:
    ```
* - {py:obj}`RANGE_HEADER_PATTERN <duck.http.response.RANGE_HEADER_PATTERN>`
  - ```{autodocx-docstring} duck.http.response.RANGE_HEADER_PATTERN
    :summary:
    ```
* - {py:obj}`StreamingType <duck.http.response.StreamingType>`
  - ```{autodocx-docstring} duck.http.response.StreamingType
    :summary:
    ```
````

### API

`````{py:class} BaseResponse(payload_obj: duck.http.response_payload.HttpResponsePayload, content_obj: typing.Optional[duck.http.content.Content] = None)
:canonical: duck.http.response.BaseResponse

```{autodocx-docstring} duck.http.response.BaseResponse
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.http.response.BaseResponse.__init__
```

````{py:method} __repr__()
:canonical: duck.http.response.BaseResponse.__repr__

````

````{py:property} content
:canonical: duck.http.response.BaseResponse.content
:type: bytes

```{autodocx-docstring} duck.http.response.BaseResponse.content
```

````

````{py:property} content_encoding
:canonical: duck.http.response.BaseResponse.content_encoding
:type: str

```{autodocx-docstring} duck.http.response.BaseResponse.content_encoding
```

````

````{py:property} content_length
:canonical: duck.http.response.BaseResponse.content_length
:type: int

```{autodocx-docstring} duck.http.response.BaseResponse.content_length
```

````

````{py:property} content_type
:canonical: duck.http.response.BaseResponse.content_type
:type: str

```{autodocx-docstring} duck.http.response.BaseResponse.content_type
```

````

````{py:property} cookies
:canonical: duck.http.response.BaseResponse.cookies
:type: http.cookies.SimpleCookie

```{autodocx-docstring} duck.http.response.BaseResponse.cookies
```

````

````{py:method} delete_cookie(key: str, path: str = '/', domain: typing.Optional[str] = None) -> None
:canonical: duck.http.response.BaseResponse.delete_cookie

```{autodocx-docstring} duck.http.response.BaseResponse.delete_cookie
```

````

````{py:method} delete_header(header: str, failsafe: bool = True)
:canonical: duck.http.response.BaseResponse.delete_header

```{autodocx-docstring} duck.http.response.BaseResponse.delete_header
```

````

````{py:method} get_all_cookies() -> typing.Dict[str, str]
:canonical: duck.http.response.BaseResponse.get_all_cookies

```{autodocx-docstring} duck.http.response.BaseResponse.get_all_cookies
```

````

````{py:method} get_cookie(name: str) -> str
:canonical: duck.http.response.BaseResponse.get_cookie

```{autodocx-docstring} duck.http.response.BaseResponse.get_cookie
```

````

````{py:method} get_cookie_obj(name: str) -> typing.Optional[http.cookies.Morsel]
:canonical: duck.http.response.BaseResponse.get_cookie_obj

```{autodocx-docstring} duck.http.response.BaseResponse.get_cookie_obj
```

````

````{py:method} get_cookie_str(name: str, include_cookie_name: bool = True) -> str
:canonical: duck.http.response.BaseResponse.get_cookie_str

```{autodocx-docstring} duck.http.response.BaseResponse.get_cookie_str
```

````

````{py:method} get_header(header: str, default_value: typing.Optional = None) -> typing.Optional[str]
:canonical: duck.http.response.BaseResponse.get_header

```{autodocx-docstring} duck.http.response.BaseResponse.get_header
```

````

````{py:property} headers
:canonical: duck.http.response.BaseResponse.headers
:type: duck.http.headers.Headers

```{autodocx-docstring} duck.http.response.BaseResponse.headers
```

````

````{py:property} raw
:canonical: duck.http.response.BaseResponse.raw
:type: bytes

```{autodocx-docstring} duck.http.response.BaseResponse.raw
```

````

````{py:method} set_content_type_header()
:canonical: duck.http.response.BaseResponse.set_content_type_header

```{autodocx-docstring} duck.http.response.BaseResponse.set_content_type_header
```

````

````{py:method} set_cookie(key: str, value: str = '', domain: typing.Optional[str] = None, path: str = '/', max_age: typing.Optional[typing.Union[int, datetime.timedelta]] = None, expires: typing.Optional[typing.Union[datetime.datetime, str]] = None, secure: bool = False, httponly: bool = False, samesite: typing.Optional[str] = 'Lax') -> None
:canonical: duck.http.response.BaseResponse.set_cookie

```{autodocx-docstring} duck.http.response.BaseResponse.set_cookie
```

````

````{py:method} set_header(header: str, value: str)
:canonical: duck.http.response.BaseResponse.set_header

```{autodocx-docstring} duck.http.response.BaseResponse.set_header
```

````

````{py:method} set_multiple_cookies(cookies: typing.Dict[str, typing.Dict[str, typing.Any]]) -> None
:canonical: duck.http.response.BaseResponse.set_multiple_cookies

```{autodocx-docstring} duck.http.response.BaseResponse.set_multiple_cookies
```

````

````{py:property} status
:canonical: duck.http.response.BaseResponse.status
:type: tuple[int, str]

```{autodocx-docstring} duck.http.response.BaseResponse.status
```

````

````{py:property} status_code
:canonical: duck.http.response.BaseResponse.status_code
:type: int

```{autodocx-docstring} duck.http.response.BaseResponse.status_code
```

````

````{py:property} status_explanation
:canonical: duck.http.response.BaseResponse.status_explanation
:type: str

```{autodocx-docstring} duck.http.response.BaseResponse.status_explanation
```

````

````{py:property} status_message
:canonical: duck.http.response.BaseResponse.status_message
:type: str

```{autodocx-docstring} duck.http.response.BaseResponse.status_message
```

````

````{py:property} title_headers
:canonical: duck.http.response.BaseResponse.title_headers
:type: dict

```{autodocx-docstring} duck.http.response.BaseResponse.title_headers
```

````

`````

`````{py:class} ComponentResponse(component: duck.html.components.Component, status_code: int = 200, headers: typing.Optional[typing.Dict[str, str]] = None, content_type: typing.Optional[str] = 'text/html')
:canonical: duck.http.response.ComponentResponse

Bases: {py:obj}`duck.http.response.StreamingHttpResponse`

```{autodocx-docstring} duck.http.response.ComponentResponse
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.http.response.ComponentResponse.__init__
```

````{py:method} async_iter_content() -> collections.abc.AsyncGenerator[bytes, None]
:canonical: duck.http.response.ComponentResponse.async_iter_content
:async:

````

````{py:method} iter_content() -> collections.abc.Generator[bytes, None, None]
:canonical: duck.http.response.ComponentResponse.iter_content

````

`````

````{py:class} FileResponse(filepath: str, headers: typing.Dict = {}, status_code: int = 206, content_type: typing.Optional[str] = None, chunk_size: int = 2 * 1024 * 1024, start_pos: int = 0, end_pos: typing.Optional[int] = -1)
:canonical: duck.http.response.FileResponse

Bases: {py:obj}`duck.http.response.StreamingRangeHttpResponse`

```{autodocx-docstring} duck.http.response.FileResponse
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.http.response.FileResponse.__init__
```

````

````{py:class} HttpBadGatewayResponse(content: typing.Optional[typing.Union[str, bytes]] = None, headers: typing.Dict = {}, content_type: typing.Optional[str] = None)
:canonical: duck.http.response.HttpBadGatewayResponse

Bases: {py:obj}`duck.http.response.HttpErrorRequestResponse`

```{autodocx-docstring} duck.http.response.HttpBadGatewayResponse
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.http.response.HttpBadGatewayResponse.__init__
```

````

````{py:class} HttpBadRequestResponse(content: typing.Optional[typing.Union[str, bytes]] = None, headers: typing.Dict = {}, content_type: typing.Optional[str] = None)
:canonical: duck.http.response.HttpBadRequestResponse

Bases: {py:obj}`duck.http.response.HttpErrorRequestResponse`

```{autodocx-docstring} duck.http.response.HttpBadRequestResponse
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.http.response.HttpBadRequestResponse.__init__
```

````

````{py:class} HttpBadRequestSyntaxResponse(content: typing.Optional[typing.Union[str, bytes]] = 'Bad Request Syntax', headers: typing.Dict = {}, content_type: typing.Optional[str] = None)
:canonical: duck.http.response.HttpBadRequestSyntaxResponse

Bases: {py:obj}`duck.http.response.HttpErrorRequestResponse`

```{autodocx-docstring} duck.http.response.HttpBadRequestSyntaxResponse
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.http.response.HttpBadRequestSyntaxResponse.__init__
```

````

````{py:class} HttpErrorRequestResponse(content: typing.Optional[typing.Union[str, bytes]] = None, status_code: int = 400, headers: typing.Dict = {}, content_type: typing.Optional[str] = None)
:canonical: duck.http.response.HttpErrorRequestResponse

Bases: {py:obj}`duck.http.response.HttpResponse`

```{autodocx-docstring} duck.http.response.HttpErrorRequestResponse
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.http.response.HttpErrorRequestResponse.__init__
```

````

````{py:class} HttpForbiddenRequestResponse(content: typing.Optional[typing.Union[str, bytes]] = None, headers: typing.Dict = {}, content_type: typing.Optional[str] = None)
:canonical: duck.http.response.HttpForbiddenRequestResponse

Bases: {py:obj}`duck.http.response.HttpErrorRequestResponse`

```{autodocx-docstring} duck.http.response.HttpForbiddenRequestResponse
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.http.response.HttpForbiddenRequestResponse.__init__
```

````

````{py:class} HttpMethodNotAllowedResponse(content: typing.Optional[typing.Union[str, bytes]] = None, headers: typing.Dict = {}, content_type: typing.Optional[str] = None)
:canonical: duck.http.response.HttpMethodNotAllowedResponse

Bases: {py:obj}`duck.http.response.HttpErrorRequestResponse`

```{autodocx-docstring} duck.http.response.HttpMethodNotAllowedResponse
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.http.response.HttpMethodNotAllowedResponse.__init__
```

````

````{py:class} HttpNotFoundResponse(content: typing.Optional[typing.Union[str, bytes]] = None, headers: typing.Dict = {}, content_type: typing.Optional[str] = None)
:canonical: duck.http.response.HttpNotFoundResponse

Bases: {py:obj}`duck.http.response.HttpErrorRequestResponse`

```{autodocx-docstring} duck.http.response.HttpNotFoundResponse
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.http.response.HttpNotFoundResponse.__init__
```

````

````{py:class} HttpRangeNotSatisfiableResponse(content: typing.Optional[typing.Union[str, bytes]] = None, headers: typing.Dict = {}, content_type: typing.Optional[str] = None)
:canonical: duck.http.response.HttpRangeNotSatisfiableResponse

Bases: {py:obj}`duck.http.response.HttpErrorRequestResponse`

```{autodocx-docstring} duck.http.response.HttpRangeNotSatisfiableResponse
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.http.response.HttpRangeNotSatisfiableResponse.__init__
```

````

````{py:class} HttpRedirectResponse(location: str, headers: typing.Dict = {}, content_type: typing.Optional[str] = None, permanent: bool = False)
:canonical: duck.http.response.HttpRedirectResponse

Bases: {py:obj}`duck.http.response.HttpResponse`

```{autodocx-docstring} duck.http.response.HttpRedirectResponse
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.http.response.HttpRedirectResponse.__init__
```

````

````{py:class} HttpRequestTimeoutResponse(content: typing.Optional[typing.Union[str, bytes]] = None, headers: typing.Dict = {}, content_type: typing.Optional[str] = None)
:canonical: duck.http.response.HttpRequestTimeoutResponse

Bases: {py:obj}`duck.http.response.HttpErrorRequestResponse`

```{autodocx-docstring} duck.http.response.HttpRequestTimeoutResponse
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.http.response.HttpRequestTimeoutResponse.__init__
```

````

````{py:class} HttpResponse(content: typing.Optional[typing.Union[str, bytes]] = None, status_code: int = 200, headers: dict = {}, content_type: typing.Optional[str] = None)
:canonical: duck.http.response.HttpResponse

Bases: {py:obj}`duck.http.response.BaseResponse`

```{autodocx-docstring} duck.http.response.HttpResponse
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.http.response.HttpResponse.__init__
```

````

````{py:class} HttpServerErrorResponse(content: typing.Optional[typing.Union[str, bytes]] = None, headers: typing.Dict = {}, content_type: typing.Optional[str] = None)
:canonical: duck.http.response.HttpServerErrorResponse

Bases: {py:obj}`duck.http.response.HttpErrorRequestResponse`

```{autodocx-docstring} duck.http.response.HttpServerErrorResponse
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.http.response.HttpServerErrorResponse.__init__
```

````

````{py:class} HttpSwitchProtocolResponse(upgrade_to: str, headers: typing.Dict = {}, content_type: typing.Optional[str] = None)
:canonical: duck.http.response.HttpSwitchProtocolResponse

Bases: {py:obj}`duck.http.response.HttpResponse`

```{autodocx-docstring} duck.http.response.HttpSwitchProtocolResponse
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.http.response.HttpSwitchProtocolResponse.__init__
```

````

````{py:class} HttpTooManyRequestsResponse(content: typing.Optional[typing.Union[str, bytes]] = 'Too many requests', headers: typing.Dict = {}, content_type: typing.Optional[str] = None)
:canonical: duck.http.response.HttpTooManyRequestsResponse

Bases: {py:obj}`duck.http.response.HttpErrorRequestResponse`

```{autodocx-docstring} duck.http.response.HttpTooManyRequestsResponse
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.http.response.HttpTooManyRequestsResponse.__init__
```

````

````{py:class} HttpUnsupportedVersionResponse(content: typing.Optional[typing.Union[str, bytes]] = None, headers: typing.Dict = {}, content_type: typing.Optional[str] = None)
:canonical: duck.http.response.HttpUnsupportedVersionResponse

Bases: {py:obj}`duck.http.response.HttpErrorRequestResponse`

```{autodocx-docstring} duck.http.response.HttpUnsupportedVersionResponse
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.http.response.HttpUnsupportedVersionResponse.__init__
```

````

````{py:class} JsonResponse(content: typing.Optional[typing.Dict[str, str]] = None, status_code: int = 200, headers: typing.Dict = {}, content_type='application/json')
:canonical: duck.http.response.JsonResponse

Bases: {py:obj}`duck.http.response.HttpResponse`

```{autodocx-docstring} duck.http.response.JsonResponse
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.http.response.JsonResponse.__init__
```

````

````{py:data} NEGATIVE_RANGE_PATTERN
:canonical: duck.http.response.NEGATIVE_RANGE_PATTERN
:value: >
   'compile(...)'

```{autodocx-docstring} duck.http.response.NEGATIVE_RANGE_PATTERN
```

````

````{py:data} RANGE_HEADER_PATTERN
:canonical: duck.http.response.RANGE_HEADER_PATTERN
:value: >
   'compile(...)'

```{autodocx-docstring} duck.http.response.RANGE_HEADER_PATTERN
```

````

`````{py:class} StreamingHttpResponse(stream: duck.http.response.StreamingType, status_code: int = 200, headers: typing.Dict = {}, content_type: typing.Optional[str] = 'application/octet-stream', chunk_size: int = 2 * 1024 * 1024)
:canonical: duck.http.response.StreamingHttpResponse

Bases: {py:obj}`duck.http.response.HttpResponse`

```{autodocx-docstring} duck.http.response.StreamingHttpResponse
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.http.response.StreamingHttpResponse.__init__
```

````{py:method} __repr__()
:canonical: duck.http.response.StreamingHttpResponse.__repr__

````

````{py:method} _async_read_from_file(file_obj: io.IOBase, chunk_size: int = 2 * 1024 * 1024) -> collections.abc.Generator
:canonical: duck.http.response.StreamingHttpResponse._async_read_from_file
:async:

```{autodocx-docstring} duck.http.response.StreamingHttpResponse._async_read_from_file
```

````

````{py:method} _read_from_file(file_obj: io.IOBase, chunk_size: int = 2 * 1024 * 1024) -> collections.abc.Generator
:canonical: duck.http.response.StreamingHttpResponse._read_from_file

```{autodocx-docstring} duck.http.response.StreamingHttpResponse._read_from_file
```

````

````{py:method} async_file_io_stream(filepath: str, chunk_size: int = 2 * 1024 * 1024) -> duck.utils.fileio.AsyncFileIOStream
:canonical: duck.http.response.StreamingHttpResponse.async_file_io_stream
:classmethod:

```{autodocx-docstring} duck.http.response.StreamingHttpResponse.async_file_io_stream
```

````

````{py:method} async_iter_content() -> typing.Awaitable[collections.abc.Iterable[bytes]]
:canonical: duck.http.response.StreamingHttpResponse.async_iter_content
:async:

```{autodocx-docstring} duck.http.response.StreamingHttpResponse.async_iter_content
```

````

````{py:method} file_io_stream(filepath: str, chunk_size: int = 2 * 1024 * 1024) -> duck.utils.fileio.FileIOStream
:canonical: duck.http.response.StreamingHttpResponse.file_io_stream
:classmethod:

```{autodocx-docstring} duck.http.response.StreamingHttpResponse.file_io_stream
```

````

````{py:method} iter_content() -> collections.abc.Iterable[bytes]
:canonical: duck.http.response.StreamingHttpResponse.iter_content

```{autodocx-docstring} duck.http.response.StreamingHttpResponse.iter_content
```

````

`````

`````{py:class} StreamingRangeHttpResponse(stream: io.IOBase, status_code: int = 206, headers: typing.Dict = {}, content_type: typing.Optional[str] = 'application/octet-stream', chunk_size: int = 2 * 1024 * 1024, start_pos: int = 0, end_pos: typing.Optional[int] = -1)
:canonical: duck.http.response.StreamingRangeHttpResponse

Bases: {py:obj}`duck.http.response.StreamingHttpResponse`

```{autodocx-docstring} duck.http.response.StreamingRangeHttpResponse
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.http.response.StreamingRangeHttpResponse.__init__
```

````{py:method} __repr__()
:canonical: duck.http.response.StreamingRangeHttpResponse.__repr__

````

````{py:method} _async_get_range_stream() -> collections.abc.AsyncGenerator
:canonical: duck.http.response.StreamingRangeHttpResponse._async_get_range_stream
:async:

```{autodocx-docstring} duck.http.response.StreamingRangeHttpResponse._async_get_range_stream
```

````

````{py:method} _get_range_stream() -> collections.abc.Generator
:canonical: duck.http.response.StreamingRangeHttpResponse._get_range_stream

```{autodocx-docstring} duck.http.response.StreamingRangeHttpResponse._get_range_stream
```

````

````{py:method} clear_content_range_headers()
:canonical: duck.http.response.StreamingRangeHttpResponse.clear_content_range_headers

```{autodocx-docstring} duck.http.response.StreamingRangeHttpResponse.clear_content_range_headers
```

````

````{py:method} extract_range(range_header: str) -> typing.Optional[typing.Tuple[int, int]]
:canonical: duck.http.response.StreamingRangeHttpResponse.extract_range
:classmethod:

```{autodocx-docstring} duck.http.response.StreamingRangeHttpResponse.extract_range
```

````

````{py:method} parse_range(start_pos: int, end_pos: int) -> int
:canonical: duck.http.response.StreamingRangeHttpResponse.parse_range

```{autodocx-docstring} duck.http.response.StreamingRangeHttpResponse.parse_range
```

````

````{py:method} set_content_range_headers()
:canonical: duck.http.response.StreamingRangeHttpResponse.set_content_range_headers

```{autodocx-docstring} duck.http.response.StreamingRangeHttpResponse.set_content_range_headers
```

````

````{py:method} validate_stream(stream)
:canonical: duck.http.response.StreamingRangeHttpResponse.validate_stream

```{autodocx-docstring} duck.http.response.StreamingRangeHttpResponse.validate_stream
```

````

`````

````{py:data} StreamingType
:canonical: duck.http.response.StreamingType
:value: >
   None

```{autodocx-docstring} duck.http.response.StreamingType
```

````

````{py:class} TemplateResponse(request: duck.http.request.HttpRequest, template: str, context: typing.Dict = {}, status_code: int = 200, headers: typing.Dict = {}, content_type: str = 'text/html', engine: typing.Optional[duck.template.environment.Engine] = None)
:canonical: duck.http.response.TemplateResponse

Bases: {py:obj}`duck.http.response.HttpResponse`

```{autodocx-docstring} duck.http.response.TemplateResponse
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.http.response.TemplateResponse.__init__
```

````
