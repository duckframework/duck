# {py:mod}`duck.contrib.responses.simple_response`

```{py:module} duck.contrib.responses.simple_response
```

```{autodocx-docstring} duck.contrib.responses.simple_response
:allowtitles:
```

## Module Contents

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`_make_simple_response <duck.contrib.responses.simple_response._make_simple_response>`
  - ```{autodocx-docstring} duck.contrib.responses.simple_response._make_simple_response
    :summary:
    ```
* - {py:obj}`_simple_response <duck.contrib.responses.simple_response._simple_response>`
  - ```{autodocx-docstring} duck.contrib.responses.simple_response._simple_response
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`FAVICON <duck.contrib.responses.simple_response.FAVICON>`
  - ```{autodocx-docstring} duck.contrib.responses.simple_response.FAVICON
    :summary:
    ```
````

### API

````{py:data} FAVICON
:canonical: duck.contrib.responses.simple_response.FAVICON
:value: >
   None

```{autodocx-docstring} duck.contrib.responses.simple_response.FAVICON
```

````

````{py:exception} SimpleResponseError()
:canonical: duck.contrib.responses.simple_response.SimpleResponseError

Bases: {py:obj}`Exception`

```{autodocx-docstring} duck.contrib.responses.simple_response.SimpleResponseError
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.contrib.responses.simple_response.SimpleResponseError.__init__
```

````

````{py:function} _make_simple_response(response_class: typing.Type[duck.http.response.HttpResponse], title: str = None, heading: str = None, body: str = None, icon_link: str = None, icon_type='image/png') -> duck.http.response.HttpResponse
:canonical: duck.contrib.responses.simple_response._make_simple_response

```{autodocx-docstring} duck.contrib.responses.simple_response._make_simple_response
```
````

````{py:function} _simple_response(response_class: typing.Type[duck.http.response.HttpResponse], title: str = None, heading: str = None, body: str = None, icon_link=FAVICON, icon_type='image/png') -> duck.http.response.HttpResponse
:canonical: duck.contrib.responses.simple_response._simple_response

```{autodocx-docstring} duck.contrib.responses.simple_response._simple_response
```
````
