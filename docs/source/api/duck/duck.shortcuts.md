# {py:mod}`duck.shortcuts`

```{py:module} duck.shortcuts
```

```{autodocx-docstring} duck.shortcuts
:allowtitles:
```

## Package Contents

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`async_render <duck.shortcuts.async_render>`
  - ```{autodocx-docstring} duck.shortcuts.async_render
    :summary:
    ```
* - {py:obj}`content_replace <duck.shortcuts.content_replace>`
  - ```{autodocx-docstring} duck.shortcuts.content_replace
    :summary:
    ```
* - {py:obj}`csrf_token <duck.shortcuts.csrf_token>`
  - ```{autodocx-docstring} duck.shortcuts.csrf_token
    :summary:
    ```
* - {py:obj}`django_render <duck.shortcuts.django_render>`
  - ```{autodocx-docstring} duck.shortcuts.django_render
    :summary:
    ```
* - {py:obj}`jinja2_render <duck.shortcuts.jinja2_render>`
  - ```{autodocx-docstring} duck.shortcuts.jinja2_render
    :summary:
    ```
* - {py:obj}`jsonify <duck.shortcuts.jsonify>`
  - ```{autodocx-docstring} duck.shortcuts.jsonify
    :summary:
    ```
* - {py:obj}`media <duck.shortcuts.media>`
  - ```{autodocx-docstring} duck.shortcuts.media
    :summary:
    ```
* - {py:obj}`merge <duck.shortcuts.merge>`
  - ```{autodocx-docstring} duck.shortcuts.merge
    :summary:
    ```
* - {py:obj}`not_found404 <duck.shortcuts.not_found404>`
  - ```{autodocx-docstring} duck.shortcuts.not_found404
    :summary:
    ```
* - {py:obj}`redirect <duck.shortcuts.redirect>`
  - ```{autodocx-docstring} duck.shortcuts.redirect
    :summary:
    ```
* - {py:obj}`render <duck.shortcuts.render>`
  - ```{autodocx-docstring} duck.shortcuts.render
    :summary:
    ```
* - {py:obj}`replace_response <duck.shortcuts.replace_response>`
  - ```{autodocx-docstring} duck.shortcuts.replace_response
    :summary:
    ```
* - {py:obj}`resolve <duck.shortcuts.resolve>`
  - ```{autodocx-docstring} duck.shortcuts.resolve
    :summary:
    ```
* - {py:obj}`static <duck.shortcuts.static>`
  - ```{autodocx-docstring} duck.shortcuts.static
    :summary:
    ```
* - {py:obj}`streaming_content_replace <duck.shortcuts.streaming_content_replace>`
  - ```{autodocx-docstring} duck.shortcuts.streaming_content_replace
    :summary:
    ```
* - {py:obj}`to_response <duck.shortcuts.to_response>`
  - ```{autodocx-docstring} duck.shortcuts.to_response
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`__all__ <duck.shortcuts.__all__>`
  - ```{autodocx-docstring} duck.shortcuts.__all__
    :summary:
    ```
````

### API

````{py:exception} URLResolveError()
:canonical: duck.shortcuts.URLResolveError

Bases: {py:obj}`Exception`

```{autodocx-docstring} duck.shortcuts.URLResolveError
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.shortcuts.URLResolveError.__init__
```

````

````{py:data} __all__
:canonical: duck.shortcuts.__all__
:value: >
   ['simple_response', 'template_response', 'URLResolveError', 'jinja2_render', 'django_render', 'rende...

```{autodocx-docstring} duck.shortcuts.__all__
```

````

````{py:function} async_render(request, template: str, context: typing.Dict[typing.Any, typing.Any] = {}, status_code: int = 200, engine: str = 'django', **kw) -> duck.http.response.TemplateResponse
:canonical: duck.shortcuts.async_render
:async:

```{autodocx-docstring} duck.shortcuts.async_render
```
````

````{py:function} content_replace(response: duck.http.response.HttpResponse, new_data: typing.Union[bytes, str], new_content_type: str = 'auto', new_content_filepath: str = 'use_existing')
:canonical: duck.shortcuts.content_replace

```{autodocx-docstring} duck.shortcuts.content_replace
```
````

````{py:function} csrf_token(request) -> str
:canonical: duck.shortcuts.csrf_token

```{autodocx-docstring} duck.shortcuts.csrf_token
```
````

````{py:function} django_render(request: duck.http.request.HttpRequest, template: str, context: typing.Dict[typing.Any, typing.Any] = {}, status_code: int = 200, **kw) -> duck.http.response.TemplateResponse
:canonical: duck.shortcuts.django_render

```{autodocx-docstring} duck.shortcuts.django_render
```
````

````{py:function} jinja2_render(request: duck.http.request.HttpRequest, template: str, context: typing.Dict[typing.Any, typing.Any] = {}, status_code: int = 200, **kw) -> duck.http.response.TemplateResponse
:canonical: duck.shortcuts.jinja2_render

```{autodocx-docstring} duck.shortcuts.jinja2_render
```
````

````{py:function} jsonify(data: typing.Any, status_code: int = 200, **kw)
:canonical: duck.shortcuts.jsonify

```{autodocx-docstring} duck.shortcuts.jsonify
```
````

````{py:function} media(resource_path: str) -> str
:canonical: duck.shortcuts.media

```{autodocx-docstring} duck.shortcuts.media
```
````

````{py:function} merge(base_response: duck.http.response.HttpResponse, take_response: duck.http.response.HttpResponse, merge_headers: bool = False) -> duck.http.response.HttpResponse
:canonical: duck.shortcuts.merge

```{autodocx-docstring} duck.shortcuts.merge
```
````

````{py:function} not_found404(request: typing.Optional[duck.http.request.HttpRequest] = None, body: str = None) -> duck.http.response.HttpResponse
:canonical: duck.shortcuts.not_found404

```{autodocx-docstring} duck.shortcuts.not_found404
```
````

````{py:function} redirect(location: str, permanent: bool = False, content_type='text/html', **kw)
:canonical: duck.shortcuts.redirect

```{autodocx-docstring} duck.shortcuts.redirect
```
````

````{py:function} render(request, template: str, context: typing.Dict[typing.Any, typing.Any] = {}, status_code: int = 200, engine: str = 'django', **kw) -> duck.http.response.TemplateResponse
:canonical: duck.shortcuts.render

```{autodocx-docstring} duck.shortcuts.render
```
````

````{py:function} replace_response(old_response: duck.http.response.HttpResponse, new_response: duck.http.response.HttpResponse, full_replacement: bool = True) -> duck.http.response.HttpResponse
:canonical: duck.shortcuts.replace_response

```{autodocx-docstring} duck.shortcuts.replace_response
```
````

````{py:function} resolve(name: str, absolute: bool = True, fallback_url: typing.Optional[str] = None) -> str
:canonical: duck.shortcuts.resolve

```{autodocx-docstring} duck.shortcuts.resolve
```
````

````{py:function} static(resource_path: str) -> str
:canonical: duck.shortcuts.static

```{autodocx-docstring} duck.shortcuts.static
```
````

````{py:function} streaming_content_replace(response: duck.http.response.StreamingHttpResponse, stream: typing.Union[typing.Callable, collections.abc.Iterable[bytes]], chunk_size: int = 2 * 1024 * 1024) -> None
:canonical: duck.shortcuts.streaming_content_replace

```{autodocx-docstring} duck.shortcuts.streaming_content_replace
```
````

````{py:function} to_response(value: typing.Any, **kwargs) -> typing.Union[duck.http.response.BaseResponse, duck.http.response.HttpResponse]
:canonical: duck.shortcuts.to_response

```{autodocx-docstring} duck.shortcuts.to_response
```
````
