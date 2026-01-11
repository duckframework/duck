# {py:mod}`duck.html.components.navbar`

```{py:module} duck.html.components.navbar
```

```{autodocx-docstring} duck.html.components.navbar
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`Navbar <duck.html.components.navbar.Navbar>`
  - ```{autodocx-docstring} duck.html.components.navbar.Navbar
    :summary:
    ```
* - {py:obj}`NavbarBrand <duck.html.components.navbar.NavbarBrand>`
  - ```{autodocx-docstring} duck.html.components.navbar.NavbarBrand
    :summary:
    ```
* - {py:obj}`NavbarContainer <duck.html.components.navbar.NavbarContainer>`
  - ```{autodocx-docstring} duck.html.components.navbar.NavbarContainer
    :summary:
    ```
* - {py:obj}`NavbarLinks <duck.html.components.navbar.NavbarLinks>`
  - ```{autodocx-docstring} duck.html.components.navbar.NavbarLinks
    :summary:
    ```
````

### API

`````{py:class} Navbar(element: typing.Optional[str] = None, properties: typing.Optional[typing.Dict[str, str]] = None, props: typing.Optional[typing.Dict[str, str]] = None, style: typing.Optional[typing.Dict[str, str]] = None, inner_html: typing.Optional[typing.Union[str, str, float]] = None, children: typing.Optional[typing.List[duck.html.components.HtmlComponent]] = None, **kwargs)
:canonical: duck.html.components.navbar.Navbar

Bases: {py:obj}`duck.html.components.InnerComponent`

```{autodocx-docstring} duck.html.components.navbar.Navbar
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.html.components.navbar.Navbar.__init__
```

````{py:method} get_element()
:canonical: duck.html.components.navbar.Navbar.get_element

````

````{py:method} on_create()
:canonical: duck.html.components.navbar.Navbar.on_create

```{autodocx-docstring} duck.html.components.navbar.Navbar.on_create
```

````

`````

`````{py:class} NavbarBrand(url: str = None, *args, **kwargs)
:canonical: duck.html.components.navbar.NavbarBrand

Bases: {py:obj}`duck.html.components.link.Link`

```{autodocx-docstring} duck.html.components.navbar.NavbarBrand
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.html.components.navbar.NavbarBrand.__init__
```

````{py:method} add_navbar_image()
:canonical: duck.html.components.navbar.NavbarBrand.add_navbar_image

```{autodocx-docstring} duck.html.components.navbar.NavbarBrand.add_navbar_image
```

````

````{py:method} on_create()
:canonical: duck.html.components.navbar.NavbarBrand.on_create

```{autodocx-docstring} duck.html.components.navbar.NavbarBrand.on_create
```

````

`````

`````{py:class} NavbarContainer(element: typing.Optional[str] = None, properties: typing.Optional[typing.Dict[str, str]] = None, props: typing.Optional[typing.Dict[str, str]] = None, style: typing.Optional[typing.Dict[str, str]] = None, inner_html: typing.Optional[typing.Union[str, str, float]] = None, children: typing.Optional[typing.List[duck.html.components.HtmlComponent]] = None, **kwargs)
:canonical: duck.html.components.navbar.NavbarContainer

Bases: {py:obj}`duck.html.components.container.FlexContainer`

```{autodocx-docstring} duck.html.components.navbar.NavbarContainer
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.html.components.navbar.NavbarContainer.__init__
```

````{py:method} on_create()
:canonical: duck.html.components.navbar.NavbarContainer.on_create

```{autodocx-docstring} duck.html.components.navbar.NavbarContainer.on_create
```

````

`````

`````{py:class} NavbarLinks(element: typing.Optional[str] = None, properties: typing.Optional[typing.Dict[str, str]] = None, props: typing.Optional[typing.Dict[str, str]] = None, style: typing.Optional[typing.Dict[str, str]] = None, inner_html: typing.Optional[typing.Union[str, str, float]] = None, children: typing.Optional[typing.List[duck.html.components.HtmlComponent]] = None, **kwargs)
:canonical: duck.html.components.navbar.NavbarLinks

Bases: {py:obj}`duck.html.components.InnerComponent`

```{autodocx-docstring} duck.html.components.navbar.NavbarLinks
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.html.components.navbar.NavbarLinks.__init__
```

````{py:method} add_links()
:canonical: duck.html.components.navbar.NavbarLinks.add_links

```{autodocx-docstring} duck.html.components.navbar.NavbarLinks.add_links
```

````

````{py:method} get_element()
:canonical: duck.html.components.navbar.NavbarLinks.get_element

````

````{py:method} on_create()
:canonical: duck.html.components.navbar.NavbarLinks.on_create

```{autodocx-docstring} duck.html.components.navbar.NavbarLinks.on_create
```

````

`````
