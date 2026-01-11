# {py:mod}`duck.html.components.table_of_contents`

```{py:module} duck.html.components.table_of_contents
```

```{autodocx-docstring} duck.html.components.table_of_contents
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`TableOfContents <duck.html.components.table_of_contents.TableOfContents>`
  - ```{autodocx-docstring} duck.html.components.table_of_contents.TableOfContents
    :summary:
    ```
* - {py:obj}`TableOfContentsSection <duck.html.components.table_of_contents.TableOfContentsSection>`
  - ```{autodocx-docstring} duck.html.components.table_of_contents.TableOfContentsSection
    :summary:
    ```
````

### API

`````{py:class} TableOfContents(element: typing.Optional[str] = None, properties: typing.Optional[typing.Dict[str, str]] = None, props: typing.Optional[typing.Dict[str, str]] = None, style: typing.Optional[typing.Dict[str, str]] = None, inner_html: typing.Optional[typing.Union[str, str, float]] = None, children: typing.Optional[typing.List[duck.html.components.HtmlComponent]] = None, **kwargs)
:canonical: duck.html.components.table_of_contents.TableOfContents

Bases: {py:obj}`duck.html.components.container.FlexContainer`

```{autodocx-docstring} duck.html.components.table_of_contents.TableOfContents
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.html.components.table_of_contents.TableOfContents.__init__
```

````{py:method} add_child(child: duck.html.components.table_of_contents.TableOfContentsSection, list_style: str = 'circle')
:canonical: duck.html.components.table_of_contents.TableOfContents.add_child

```{autodocx-docstring} duck.html.components.table_of_contents.TableOfContents.add_child
```

````

````{py:method} add_section(section: duck.html.components.table_of_contents.TableOfContentsSection, list_style: str = 'circle')
:canonical: duck.html.components.table_of_contents.TableOfContents.add_section

```{autodocx-docstring} duck.html.components.table_of_contents.TableOfContents.add_section
```

````

````{py:method} on_create()
:canonical: duck.html.components.table_of_contents.TableOfContents.on_create

````

`````

`````{py:class} TableOfContentsSection(element: typing.Optional[str] = None, properties: typing.Optional[typing.Dict[str, str]] = None, props: typing.Optional[typing.Dict[str, str]] = None, style: typing.Optional[typing.Dict[str, str]] = None, inner_html: typing.Optional[typing.Union[str, str, float]] = None, children: typing.Optional[typing.List[duck.html.components.HtmlComponent]] = None, **kwargs)
:canonical: duck.html.components.table_of_contents.TableOfContentsSection

Bases: {py:obj}`duck.html.components.container.FlexContainer`

```{autodocx-docstring} duck.html.components.table_of_contents.TableOfContentsSection
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.html.components.table_of_contents.TableOfContentsSection.__init__
```

````{py:method} on_create()
:canonical: duck.html.components.table_of_contents.TableOfContentsSection.on_create

````

`````
