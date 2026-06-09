# {py:mod}`duck.html.components.container`

```{py:module} duck.html.components.container
```

```{autodocx-docstring} duck.html.components.container
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`Container <duck.html.components.container.Container>`
  - ```{autodocx-docstring} duck.html.components.container.Container
    :summary:
    ```
* - {py:obj}`FixedContainer <duck.html.components.container.FixedContainer>`
  - ```{autodocx-docstring} duck.html.components.container.FixedContainer
    :summary:
    ```
* - {py:obj}`FlexContainer <duck.html.components.container.FlexContainer>`
  - ```{autodocx-docstring} duck.html.components.container.FlexContainer
    :summary:
    ```
* - {py:obj}`FluidContainer <duck.html.components.container.FluidContainer>`
  - ```{autodocx-docstring} duck.html.components.container.FluidContainer
    :summary:
    ```
* - {py:obj}`GridContainer <duck.html.components.container.GridContainer>`
  - ```{autodocx-docstring} duck.html.components.container.GridContainer
    :summary:
    ```
````

### API

`````{py:class} Container(element: typing.Optional[str] = None, properties: typing.Optional[typing.Dict[str, str]] = None, props: typing.Optional[typing.Dict[str, str]] = None, style: typing.Optional[typing.Dict[str, str]] = None, inner_html: typing.Optional[typing.Union[str, str, float]] = None, children: typing.Optional[typing.List[duck.html.components.HtmlComponent]] = None, **kwargs)
:canonical: duck.html.components.container.Container

Bases: {py:obj}`duck.html.components.InnerComponent`

```{autodocx-docstring} duck.html.components.container.Container
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.html.components.container.Container.__init__
```

````{py:method} get_element()
:canonical: duck.html.components.container.Container.get_element

````

````{py:method} set_background(component: duck.html.components.Component, bg_size: str = 'cover', repeat: str = 'no-repeat', position: str = 'center center', z_index: str = '-999')
:canonical: duck.html.components.container.Container.set_background

```{autodocx-docstring} duck.html.components.container.Container.set_background
```

````

`````

`````{py:class} FixedContainer(element: typing.Optional[str] = None, properties: typing.Optional[typing.Dict[str, str]] = None, props: typing.Optional[typing.Dict[str, str]] = None, style: typing.Optional[typing.Dict[str, str]] = None, inner_html: typing.Optional[typing.Union[str, str, float]] = None, children: typing.Optional[typing.List[duck.html.components.HtmlComponent]] = None, **kwargs)
:canonical: duck.html.components.container.FixedContainer

Bases: {py:obj}`duck.html.components.container.Container`

```{autodocx-docstring} duck.html.components.container.FixedContainer
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.html.components.container.FixedContainer.__init__
```

````{py:method} on_create()
:canonical: duck.html.components.container.FixedContainer.on_create

````

`````

`````{py:class} FlexContainer(element: typing.Optional[str] = None, properties: typing.Optional[typing.Dict[str, str]] = None, props: typing.Optional[typing.Dict[str, str]] = None, style: typing.Optional[typing.Dict[str, str]] = None, inner_html: typing.Optional[typing.Union[str, str, float]] = None, children: typing.Optional[typing.List[duck.html.components.HtmlComponent]] = None, **kwargs)
:canonical: duck.html.components.container.FlexContainer

Bases: {py:obj}`duck.html.components.container.Container`

```{autodocx-docstring} duck.html.components.container.FlexContainer
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.html.components.container.FlexContainer.__init__
```

````{py:method} on_create()
:canonical: duck.html.components.container.FlexContainer.on_create

````

`````

`````{py:class} FluidContainer(element: typing.Optional[str] = None, properties: typing.Optional[typing.Dict[str, str]] = None, props: typing.Optional[typing.Dict[str, str]] = None, style: typing.Optional[typing.Dict[str, str]] = None, inner_html: typing.Optional[typing.Union[str, str, float]] = None, children: typing.Optional[typing.List[duck.html.components.HtmlComponent]] = None, **kwargs)
:canonical: duck.html.components.container.FluidContainer

Bases: {py:obj}`duck.html.components.container.Container`

```{autodocx-docstring} duck.html.components.container.FluidContainer
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.html.components.container.FluidContainer.__init__
```

````{py:method} on_create()
:canonical: duck.html.components.container.FluidContainer.on_create

````

`````

`````{py:class} GridContainer(element: typing.Optional[str] = None, properties: typing.Optional[typing.Dict[str, str]] = None, props: typing.Optional[typing.Dict[str, str]] = None, style: typing.Optional[typing.Dict[str, str]] = None, inner_html: typing.Optional[typing.Union[str, str, float]] = None, children: typing.Optional[typing.List[duck.html.components.HtmlComponent]] = None, **kwargs)
:canonical: duck.html.components.container.GridContainer

Bases: {py:obj}`duck.html.components.container.Container`

```{autodocx-docstring} duck.html.components.container.GridContainer
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.html.components.container.GridContainer.__init__
```

````{py:method} on_create()
:canonical: duck.html.components.container.GridContainer.on_create

````

`````
