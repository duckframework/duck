# {py:mod}`duck.html.components.input`

```{py:module} duck.html.components.input
```

```{autodocx-docstring} duck.html.components.input
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`BaseInput <duck.html.components.input.BaseInput>`
  - ```{autodocx-docstring} duck.html.components.input.BaseInput
    :summary:
    ```
* - {py:obj}`CSRFInput <duck.html.components.input.CSRFInput>`
  - ```{autodocx-docstring} duck.html.components.input.CSRFInput
    :summary:
    ```
* - {py:obj}`Input <duck.html.components.input.Input>`
  - ```{autodocx-docstring} duck.html.components.input.Input
    :summary:
    ```
* - {py:obj}`InputWithLabel <duck.html.components.input.InputWithLabel>`
  - ```{autodocx-docstring} duck.html.components.input.InputWithLabel
    :summary:
    ```
````

### API

`````{py:class} BaseInput(element: typing.Optional[str] = None, properties: typing.Dict[str, str] = None, props: typing.Dict[str, str] = None, style: typing.Dict[str, str] = None, **kwargs)
:canonical: duck.html.components.input.BaseInput

Bases: {py:obj}`duck.html.components.NoInnerComponent`

```{autodocx-docstring} duck.html.components.input.BaseInput
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.html.components.input.BaseInput.__init__
```

````{py:method} get_element()
:canonical: duck.html.components.input.BaseInput.get_element

````

````{py:method} on_create()
:canonical: duck.html.components.input.BaseInput.on_create

````

`````

`````{py:class} CSRFInput(request: duck.http.request.HttpRequest)
:canonical: duck.html.components.input.CSRFInput

Bases: {py:obj}`duck.html.components.input.Input`

```{autodocx-docstring} duck.html.components.input.CSRFInput
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.html.components.input.CSRFInput.__init__
```

````{py:method} on_create()
:canonical: duck.html.components.input.CSRFInput.on_create

````

`````

`````{py:class} Input(element: typing.Optional[str] = None, properties: typing.Dict[str, str] = None, props: typing.Dict[str, str] = None, style: typing.Dict[str, str] = None, **kwargs)
:canonical: duck.html.components.input.Input

Bases: {py:obj}`duck.html.components.input.BaseInput`

```{autodocx-docstring} duck.html.components.input.Input
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.html.components.input.Input.__init__
```

````{py:method} on_create()
:canonical: duck.html.components.input.Input.on_create

````

`````

`````{py:class} InputWithLabel(element: typing.Optional[str] = None, properties: typing.Optional[typing.Dict[str, str]] = None, props: typing.Optional[typing.Dict[str, str]] = None, style: typing.Optional[typing.Dict[str, str]] = None, inner_html: typing.Optional[typing.Union[str, str, float]] = None, children: typing.Optional[typing.List[duck.html.components.HtmlComponent]] = None, **kwargs)
:canonical: duck.html.components.input.InputWithLabel

Bases: {py:obj}`duck.html.components.container.FlexContainer`

```{autodocx-docstring} duck.html.components.input.InputWithLabel
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.html.components.input.InputWithLabel.__init__
```

````{py:method} on_create()
:canonical: duck.html.components.input.InputWithLabel.on_create

````

`````
