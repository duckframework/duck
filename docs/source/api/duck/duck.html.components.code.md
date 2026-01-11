# {py:mod}`duck.html.components.code`

```{py:module} duck.html.components.code
```

```{autodocx-docstring} duck.html.components.code
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`Code <duck.html.components.code.Code>`
  - ```{autodocx-docstring} duck.html.components.code.Code
    :summary:
    ```
* - {py:obj}`CodeInner <duck.html.components.code.CodeInner>`
  - ```{autodocx-docstring} duck.html.components.code.CodeInner
    :summary:
    ```
* - {py:obj}`EditableCode <duck.html.components.code.EditableCode>`
  - ```{autodocx-docstring} duck.html.components.code.EditableCode
    :summary:
    ```
````

### API

`````{py:class} Code(element: typing.Optional[str] = None, properties: typing.Optional[typing.Dict[str, str]] = None, props: typing.Optional[typing.Dict[str, str]] = None, style: typing.Optional[typing.Dict[str, str]] = None, inner_html: typing.Optional[typing.Union[str, str, float]] = None, children: typing.Optional[typing.List[duck.html.components.HtmlComponent]] = None, **kwargs)
:canonical: duck.html.components.code.Code

Bases: {py:obj}`duck.html.components.InnerComponent`

```{autodocx-docstring} duck.html.components.code.Code
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.html.components.code.Code.__init__
```

````{py:method} add_initial_components()
:canonical: duck.html.components.code.Code.add_initial_components

```{autodocx-docstring} duck.html.components.code.Code.add_initial_components
```

````

````{py:method} get_element()
:canonical: duck.html.components.code.Code.get_element

````

````{py:method} on_create()
:canonical: duck.html.components.code.Code.on_create

```{autodocx-docstring} duck.html.components.code.Code.on_create
```

````

`````

`````{py:class} CodeInner(element: typing.Optional[str] = None, properties: typing.Optional[typing.Dict[str, str]] = None, props: typing.Optional[typing.Dict[str, str]] = None, style: typing.Optional[typing.Dict[str, str]] = None, inner_html: typing.Optional[typing.Union[str, str, float]] = None, children: typing.Optional[typing.List[duck.html.components.HtmlComponent]] = None, **kwargs)
:canonical: duck.html.components.code.CodeInner

Bases: {py:obj}`duck.html.components.InnerComponent`

```{autodocx-docstring} duck.html.components.code.CodeInner
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.html.components.code.CodeInner.__init__
```

````{py:method} get_element()
:canonical: duck.html.components.code.CodeInner.get_element

````

`````

`````{py:class} EditableCode(element: typing.Optional[str] = None, properties: typing.Optional[typing.Dict[str, str]] = None, props: typing.Optional[typing.Dict[str, str]] = None, style: typing.Optional[typing.Dict[str, str]] = None, inner_html: typing.Optional[typing.Union[str, str, float]] = None, children: typing.Optional[typing.List[duck.html.components.HtmlComponent]] = None, **kwargs)
:canonical: duck.html.components.code.EditableCode

Bases: {py:obj}`duck.html.components.code.Code`

```{autodocx-docstring} duck.html.components.code.EditableCode
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.html.components.code.EditableCode.__init__
```

````{py:method} on_create()
:canonical: duck.html.components.code.EditableCode.on_create

```{autodocx-docstring} duck.html.components.code.EditableCode.on_create
```

````

`````
