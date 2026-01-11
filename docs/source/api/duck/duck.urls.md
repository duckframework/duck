# {py:mod}`duck.urls`

```{py:module} duck.urls
```

```{autodocx-docstring} duck.urls
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`URLPattern <duck.urls.URLPattern>`
  - ```{autodocx-docstring} duck.urls.URLPattern
    :summary:
    ```
````

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`path <duck.urls.path>`
  - ```{autodocx-docstring} duck.urls.path
    :summary:
    ```
* - {py:obj}`re_path <duck.urls.re_path>`
  - ```{autodocx-docstring} duck.urls.re_path
    :summary:
    ```
````

### API

`````{py:class} URLPattern(url: str, handler: typing.Callable, name: typing.Optional[str], methods: typing.List[str], regex: bool = False)
:canonical: duck.urls.URLPattern

Bases: {py:obj}`dict`

```{autodocx-docstring} duck.urls.URLPattern
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.urls.URLPattern.__init__
```

````{py:method} __repr__()
:canonical: duck.urls.URLPattern.__repr__

```{autodocx-docstring} duck.urls.URLPattern.__repr__
```

````

````{py:attribute} __slots__
:canonical: duck.urls.URLPattern.__slots__
:value: >
   ()

```{autodocx-docstring} duck.urls.URLPattern.__slots__
```

````

````{py:property} regex
:canonical: duck.urls.URLPattern.regex

```{autodocx-docstring} duck.urls.URLPattern.regex
```

````

`````

````{py:function} path(url: str, view: typing.Callable, name: typing.Optional[str] = None, methods: typing.Optional[typing.List[str]] = None) -> duck.urls.URLPattern
:canonical: duck.urls.path

```{autodocx-docstring} duck.urls.path
```
````

````{py:function} re_path(re_url: str, view: typing.Callable, name: typing.Optional[str] = None, methods: typing.Optional[typing.List[str]] = None) -> duck.urls.URLPattern
:canonical: duck.urls.re_path

```{autodocx-docstring} duck.urls.re_path
```
````
