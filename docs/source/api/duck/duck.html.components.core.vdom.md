# {py:mod}`duck.html.components.core.vdom`

```{py:module} duck.html.components.core.vdom
```

```{autodocx-docstring} duck.html.components.core.vdom
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`LiveVDomNode <duck.html.components.core.vdom.LiveVDomNode>`
  - ```{autodocx-docstring} duck.html.components.core.vdom.LiveVDomNode
    :summary:
    ```
* - {py:obj}`VDomNode <duck.html.components.core.vdom.VDomNode>`
  - ```{autodocx-docstring} duck.html.components.core.vdom.VDomNode
    :summary:
    ```
````

### API

`````{py:class} LiveVDomNode(component)
:canonical: duck.html.components.core.vdom.LiveVDomNode

Bases: {py:obj}`duck.html.components.core.vdom.VDomNode`

```{autodocx-docstring} duck.html.components.core.vdom.LiveVDomNode
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.html.components.core.vdom.LiveVDomNode.__init__
```

````{py:attribute} __slots__
:canonical: duck.html.components.core.vdom.LiveVDomNode.__slots__
:value: >
   'component'

```{autodocx-docstring} duck.html.components.core.vdom.LiveVDomNode.__slots__
```

````

````{py:property} children
:canonical: duck.html.components.core.vdom.LiveVDomNode.children

```{autodocx-docstring} duck.html.components.core.vdom.LiveVDomNode.children
```

````

````{py:property} key
:canonical: duck.html.components.core.vdom.LiveVDomNode.key

```{autodocx-docstring} duck.html.components.core.vdom.LiveVDomNode.key
```

````

````{py:property} props
:canonical: duck.html.components.core.vdom.LiveVDomNode.props

```{autodocx-docstring} duck.html.components.core.vdom.LiveVDomNode.props
```

````

````{py:property} style
:canonical: duck.html.components.core.vdom.LiveVDomNode.style

```{autodocx-docstring} duck.html.components.core.vdom.LiveVDomNode.style
```

````

````{py:property} tag
:canonical: duck.html.components.core.vdom.LiveVDomNode.tag

```{autodocx-docstring} duck.html.components.core.vdom.LiveVDomNode.tag
```

````

````{py:property} text
:canonical: duck.html.components.core.vdom.LiveVDomNode.text

```{autodocx-docstring} duck.html.components.core.vdom.LiveVDomNode.text
```

````

`````

`````{py:class} VDomNode(tag: str, key: typing.Optional[typing.Union[str, int]] = None, props: typing.Optional[typing.Dict[str, str]] = None, style: typing.Optional[typing.Dict[str, str]] = None, children: typing.Optional[typing.List[duck.html.components.core.vdom.VDomNode]] = None, text: typing.Optional[str] = None, component=None)
:canonical: duck.html.components.core.vdom.VDomNode

```{autodocx-docstring} duck.html.components.core.vdom.VDomNode
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.html.components.core.vdom.VDomNode.__init__
```

````{py:method} __repr__()
:canonical: duck.html.components.core.vdom.VDomNode.__repr__

````

````{py:attribute} __slots__
:canonical: duck.html.components.core.vdom.VDomNode.__slots__
:value: >
   ('tag', 'key', 'props', 'style', 'children', 'text', 'component')

```{autodocx-docstring} duck.html.components.core.vdom.VDomNode.__slots__
```

````

````{py:attribute} __str__
:canonical: duck.html.components.core.vdom.VDomNode.__str__
:value: >
   None

```{autodocx-docstring} duck.html.components.core.vdom.VDomNode.__str__
```

````

````{py:method} diff(old: duck.html.components.core.vdom.VDomNode, new: duck.html.components.core.vdom.VDomNode) -> typing.List[list]
:canonical: duck.html.components.core.vdom.VDomNode.diff
:staticmethod:

```{autodocx-docstring} duck.html.components.core.vdom.VDomNode.diff
```

````

````{py:method} diff_and_act(action: typing.Callable, old: duck.html.components.core.vdom.VDomNode, new: duck.html.components.core.vdom.VDomNode) -> None
:canonical: duck.html.components.core.vdom.VDomNode.diff_and_act
:async:
:staticmethod:

```{autodocx-docstring} duck.html.components.core.vdom.VDomNode.diff_and_act
```

````

````{py:method} on_insert(node: duck.html.components.core.vdom.VDomNode, parent_node: duck.html.components.core.vdom.VDomNode, index: int)
:canonical: duck.html.components.core.vdom.VDomNode.on_insert

```{autodocx-docstring} duck.html.components.core.vdom.VDomNode.on_insert
```

````

````{py:method} on_remove(node: duck.html.components.core.vdom.VDomNode)
:canonical: duck.html.components.core.vdom.VDomNode.on_remove

```{autodocx-docstring} duck.html.components.core.vdom.VDomNode.on_remove
```

````

````{py:method} to_list() -> list
:canonical: duck.html.components.core.vdom.VDomNode.to_list

```{autodocx-docstring} duck.html.components.core.vdom.VDomNode.to_list
```

````

`````
