# {py:mod}`duck.html.components`

```{py:module} duck.html.components
```

```{autodocx-docstring} duck.html.components
:allowtitles:
```

## Subpackages

```{toctree}
:titlesonly:
:maxdepth: 3

duck.html.components.core
duck.html.components.extensions
duck.html.components.templatetags
duck.html.components.utils
```

## Submodules

```{toctree}
:titlesonly:
:maxdepth: 1

duck.html.components.button
duck.html.components.card
duck.html.components.checkbox
duck.html.components.code
duck.html.components.container
duck.html.components.duck
duck.html.components.fileinput
duck.html.components.footer
duck.html.components.form
duck.html.components.heading
duck.html.components.hero
duck.html.components.icon
duck.html.components.image
duck.html.components.input
duck.html.components.label
duck.html.components.link
duck.html.components.lively
duck.html.components.modal
duck.html.components.navbar
duck.html.components.page
duck.html.components.paragraph
duck.html.components.progressbar
duck.html.components.script
duck.html.components.section
duck.html.components.select
duck.html.components.snackbar
duck.html.components.style
duck.html.components.table_of_contents
duck.html.components.textarea
duck.html.components.video
```

## Package Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`HtmlComponent <duck.html.components.HtmlComponent>`
  - ```{autodocx-docstring} duck.html.components.HtmlComponent
    :summary:
    ```
* - {py:obj}`InnerHtmlComponent <duck.html.components.InnerHtmlComponent>`
  - ```{autodocx-docstring} duck.html.components.InnerHtmlComponent
    :summary:
    ```
* - {py:obj}`NoInnerHtmlComponent <duck.html.components.NoInnerHtmlComponent>`
  - ```{autodocx-docstring} duck.html.components.NoInnerHtmlComponent
    :summary:
    ```
* - {py:obj}`Theme <duck.html.components.Theme>`
  - ```{autodocx-docstring} duck.html.components.Theme
    :summary:
    ```
````

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`quote <duck.html.components.quote>`
  - ```{autodocx-docstring} duck.html.components.quote
    :summary:
    ```
* - {py:obj}`to_component <duck.html.components.to_component>`
  - ```{autodocx-docstring} duck.html.components.to_component
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`Component <duck.html.components.Component>`
  - ```{autodocx-docstring} duck.html.components.Component
    :summary:
    ```
* - {py:obj}`ComponentError <duck.html.components.ComponentError>`
  - ```{autodocx-docstring} duck.html.components.ComponentError
    :summary:
    ```
* - {py:obj}`ELEMENT_PATTERN <duck.html.components.ELEMENT_PATTERN>`
  - ```{autodocx-docstring} duck.html.components.ELEMENT_PATTERN
    :summary:
    ```
* - {py:obj}`InnerComponent <duck.html.components.InnerComponent>`
  - ```{autodocx-docstring} duck.html.components.InnerComponent
    :summary:
    ```
* - {py:obj}`NoInnerComponent <duck.html.components.NoInnerComponent>`
  - ```{autodocx-docstring} duck.html.components.NoInnerComponent
    :summary:
    ```
````

### API

````{py:data} Component
:canonical: duck.html.components.Component
:value: >
   None

```{autodocx-docstring} duck.html.components.Component
```

````

````{py:data} ComponentError
:canonical: duck.html.components.ComponentError
:value: >
   None

```{autodocx-docstring} duck.html.components.ComponentError
```

````

````{py:data} ELEMENT_PATTERN
:canonical: duck.html.components.ELEMENT_PATTERN
:value: >
   'compile(...)'

```{autodocx-docstring} duck.html.components.ELEMENT_PATTERN
```

````

`````{py:class} HtmlComponent(element: typing.Optional[str] = None, accept_inner_html: bool = False, inner_html: typing.Optional[typing.Union[str, int, float]] = None, properties: typing.Optional[typing.Dict[str, str]] = None, props: typing.Optional[typing.Dict[str, str]] = None, style: typing.Optional[typing.Dict[str, str]] = None, **kwargs)
:canonical: duck.html.components.HtmlComponent

```{autodocx-docstring} duck.html.components.HtmlComponent
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.html.components.HtmlComponent.__init__
```

````{py:method} __copy__()
:canonical: duck.html.components.HtmlComponent.__copy__

```{autodocx-docstring} duck.html.components.HtmlComponent.__copy__
```

````

````{py:method} __repr__() -> str
:canonical: duck.html.components.HtmlComponent.__repr__

````

````{py:method} __setattr__(key: str, value: typing.Any)
:canonical: duck.html.components.HtmlComponent.__setattr__

```{autodocx-docstring} duck.html.components.HtmlComponent.__setattr__
```

````

````{py:attribute} __str__
:canonical: duck.html.components.HtmlComponent.__str__
:value: >
   None

```{autodocx-docstring} duck.html.components.HtmlComponent.__str__
```

````

````{py:method} _copy(shallow: bool = False) -> duck.html.components.HtmlComponent
:canonical: duck.html.components.HtmlComponent._copy

```{autodocx-docstring} duck.html.components.HtmlComponent._copy
```

````

````{py:method} _get_raw_props()
:canonical: duck.html.components.HtmlComponent._get_raw_props

```{autodocx-docstring} duck.html.components.HtmlComponent._get_raw_props
```

````

````{py:method} _on_mutation(mutation: duck.html.components.core.mutation.Mutation)
:canonical: duck.html.components.HtmlComponent._on_mutation

```{autodocx-docstring} duck.html.components.HtmlComponent._on_mutation
```

````

````{py:method} _on_render_done()
:canonical: duck.html.components.HtmlComponent._on_render_done

```{autodocx-docstring} duck.html.components.HtmlComponent._on_render_done
```

````

````{py:method} _on_render_start()
:canonical: duck.html.components.HtmlComponent._on_render_start

```{autodocx-docstring} duck.html.components.HtmlComponent._on_render_start
```

````

````{py:method} assign_component_uids(root_component: duck.html.components.Component, base_uid: str = '0') -> None
:canonical: duck.html.components.HtmlComponent.assign_component_uids
:staticmethod:

```{autodocx-docstring} duck.html.components.HtmlComponent.assign_component_uids
```

````

````{py:method} async_wait_for_load(interval: float = 0.01)
:canonical: duck.html.components.HtmlComponent.async_wait_for_load
:async:

```{autodocx-docstring} duck.html.components.HtmlComponent.async_wait_for_load
```

````

````{py:method} bind(event: str, event_handler: typing.Callable, force_bind: bool = False, update_targets: typing.Optional[typing.List[duck.html.components.HtmlComponent]] = None, update_self: bool = True) -> None
:canonical: duck.html.components.HtmlComponent.bind

```{autodocx-docstring} duck.html.components.HtmlComponent.bind
```

````

````{py:method} check_component_system_active(inactive_msg: str = None)
:canonical: duck.html.components.HtmlComponent.check_component_system_active

```{autodocx-docstring} duck.html.components.HtmlComponent.check_component_system_active
```

````

````{py:method} copied_from() -> typing.Optional[duck.html.components.HtmlComponent]
:canonical: duck.html.components.HtmlComponent.copied_from

```{autodocx-docstring} duck.html.components.HtmlComponent.copied_from
```

````

````{py:method} copy(shallow: bool = False) -> duck.html.components.HtmlComponent
:canonical: duck.html.components.HtmlComponent.copy

```{autodocx-docstring} duck.html.components.HtmlComponent.copy
```

````

````{py:method} ensure_freeze(*args, **kwargs)
:canonical: duck.html.components.HtmlComponent.ensure_freeze

```{autodocx-docstring} duck.html.components.HtmlComponent.ensure_freeze
```

````

````{py:method} force_set_component_attr(key: str, value: typing.Any)
:canonical: duck.html.components.HtmlComponent.force_set_component_attr

```{autodocx-docstring} duck.html.components.HtmlComponent.force_set_component_attr
```

````

````{py:method} freeze()
:canonical: duck.html.components.HtmlComponent.freeze

```{autodocx-docstring} duck.html.components.HtmlComponent.freeze
```

````

````{py:method} get_children_string(childs: duck.html.components.core.children.ChildrenList) -> str
:canonical: duck.html.components.HtmlComponent.get_children_string

```{autodocx-docstring} duck.html.components.HtmlComponent.get_children_string
```

````

````{py:method} get_component_system_data_props() -> typing.Dict[str, str]
:canonical: duck.html.components.HtmlComponent.get_component_system_data_props

```{autodocx-docstring} duck.html.components.HtmlComponent.get_component_system_data_props
```

````

````{py:method} get_css_string(style: duck.html.components.core.props.StyleStore[str, str], add_to_prev_states: bool = True) -> str
:canonical: duck.html.components.HtmlComponent.get_css_string

```{autodocx-docstring} duck.html.components.HtmlComponent.get_css_string
```

````

````{py:method} get_element()
:canonical: duck.html.components.HtmlComponent.get_element
:abstractmethod:

```{autodocx-docstring} duck.html.components.HtmlComponent.get_element
```

````

````{py:method} get_event_info(event: str) -> typing.Tuple[typing.Callable, typing.Set[duck.html.components.HtmlComponent]]
:canonical: duck.html.components.HtmlComponent.get_event_info

```{autodocx-docstring} duck.html.components.HtmlComponent.get_event_info
```

````

````{py:method} get_partial_string()
:canonical: duck.html.components.HtmlComponent.get_partial_string

```{autodocx-docstring} duck.html.components.HtmlComponent.get_partial_string
```

````

````{py:method} get_props_string(props: duck.html.components.core.props.PropertyStore[str, str], add_to_prev_states: bool = True) -> str
:canonical: duck.html.components.HtmlComponent.get_props_string

```{autodocx-docstring} duck.html.components.HtmlComponent.get_props_string
```

````

````{py:method} get_raw_root() -> duck.html.components.Component
:canonical: duck.html.components.HtmlComponent.get_raw_root

```{autodocx-docstring} duck.html.components.HtmlComponent.get_raw_root
```

````

````{py:method} has_local_updates()
:canonical: duck.html.components.HtmlComponent.has_local_updates

```{autodocx-docstring} duck.html.components.HtmlComponent.has_local_updates
```

````

````{py:property} inner_html
:canonical: duck.html.components.HtmlComponent.inner_html
:type: str

```{autodocx-docstring} duck.html.components.HtmlComponent.inner_html
```

````

````{py:method} is_a_copy() -> bool
:canonical: duck.html.components.HtmlComponent.is_a_copy

```{autodocx-docstring} duck.html.components.HtmlComponent.is_a_copy
```

````

````{py:method} is_from_cache() -> bool
:canonical: duck.html.components.HtmlComponent.is_from_cache

```{autodocx-docstring} duck.html.components.HtmlComponent.is_from_cache
```

````

````{py:method} is_frozen() -> bool
:canonical: duck.html.components.HtmlComponent.is_frozen

```{autodocx-docstring} duck.html.components.HtmlComponent.is_frozen
```

````

````{py:method} is_loaded() -> bool
:canonical: duck.html.components.HtmlComponent.is_loaded

```{autodocx-docstring} duck.html.components.HtmlComponent.is_loaded
```

````

````{py:method} is_loading() -> bool
:canonical: duck.html.components.HtmlComponent.is_loading

```{autodocx-docstring} duck.html.components.HtmlComponent.is_loading
```

````

````{py:method} isroot() -> bool
:canonical: duck.html.components.HtmlComponent.isroot

```{autodocx-docstring} duck.html.components.HtmlComponent.isroot
```

````

````{py:method} load()
:canonical: duck.html.components.HtmlComponent.load

```{autodocx-docstring} duck.html.components.HtmlComponent.load
```

````

````{py:method} on_create()
:canonical: duck.html.components.HtmlComponent.on_create

```{autodocx-docstring} duck.html.components.HtmlComponent.on_create
```

````

````{py:method} on_mutation(mutation: duck.html.components.core.mutation.Mutation)
:canonical: duck.html.components.HtmlComponent.on_mutation

```{autodocx-docstring} duck.html.components.HtmlComponent.on_mutation
```

````

````{py:method} on_parent(parent: duck.html.components.Component)
:canonical: duck.html.components.HtmlComponent.on_parent

```{autodocx-docstring} duck.html.components.HtmlComponent.on_parent
```

````

````{py:method} on_root_finalized(root: duck.html.components.Component)
:canonical: duck.html.components.HtmlComponent.on_root_finalized

```{autodocx-docstring} duck.html.components.HtmlComponent.on_root_finalized
```

````

````{py:property} parent
:canonical: duck.html.components.HtmlComponent.parent
:type: typing.Optional[duck.html.components.Component]

```{autodocx-docstring} duck.html.components.HtmlComponent.parent
```

````

````{py:method} pre_render() -> None
:canonical: duck.html.components.HtmlComponent.pre_render

```{autodocx-docstring} duck.html.components.HtmlComponent.pre_render
```

````

````{py:property} properties
:canonical: duck.html.components.HtmlComponent.properties

```{autodocx-docstring} duck.html.components.HtmlComponent.properties
```

````

````{py:property} props
:canonical: duck.html.components.HtmlComponent.props

```{autodocx-docstring} duck.html.components.HtmlComponent.props
```

````

````{py:method} raise_if_not_loaded(message: str)
:canonical: duck.html.components.HtmlComponent.raise_if_not_loaded

```{autodocx-docstring} duck.html.components.HtmlComponent.raise_if_not_loaded
```

````

````{py:method} render() -> str
:canonical: duck.html.components.HtmlComponent.render

```{autodocx-docstring} duck.html.components.HtmlComponent.render
```

````

````{py:property} root
:canonical: duck.html.components.HtmlComponent.root
:type: typing.Optional[duck.html.components.Component]

```{autodocx-docstring} duck.html.components.HtmlComponent.root
```

````

````{py:method} set_mutation_callbacks()
:canonical: duck.html.components.HtmlComponent.set_mutation_callbacks

```{autodocx-docstring} duck.html.components.HtmlComponent.set_mutation_callbacks
```

````

````{py:property} style
:canonical: duck.html.components.HtmlComponent.style

```{autodocx-docstring} duck.html.components.HtmlComponent.style
```

````

````{py:method} to_string()
:canonical: duck.html.components.HtmlComponent.to_string

```{autodocx-docstring} duck.html.components.HtmlComponent.to_string
```

````

````{py:method} to_vdom() -> duck.html.components.core.vdom.VDomNode
:canonical: duck.html.components.HtmlComponent.to_vdom

```{autodocx-docstring} duck.html.components.HtmlComponent.to_vdom
```

````

````{py:method} toggle_validation(must_validate: bool)
:canonical: duck.html.components.HtmlComponent.toggle_validation

```{autodocx-docstring} duck.html.components.HtmlComponent.toggle_validation
```

````

````{py:method} traverse(func: callable, algorithm: str = 'depth_first_search', reverse: bool = False, include_self: bool = True) -> None
:canonical: duck.html.components.HtmlComponent.traverse

```{autodocx-docstring} duck.html.components.HtmlComponent.traverse
```

````

````{py:method} traverse_ancestors(func: callable, include_self: bool = True) -> None
:canonical: duck.html.components.HtmlComponent.traverse_ancestors

```{autodocx-docstring} duck.html.components.HtmlComponent.traverse_ancestors
```

````

````{py:property} uid
:canonical: duck.html.components.HtmlComponent.uid
:type: str

```{autodocx-docstring} duck.html.components.HtmlComponent.uid
```

````

````{py:method} unbind(event: str, failsafe: bool = True)
:canonical: duck.html.components.HtmlComponent.unbind

```{autodocx-docstring} duck.html.components.HtmlComponent.unbind
```

````

````{py:method} vdom_diff(old: duck.html.components.core.vdom.VDomNode, new: duck.html.components.core.vdom.VDomNode) -> typing.List[list]
:canonical: duck.html.components.HtmlComponent.vdom_diff
:staticmethod:

```{autodocx-docstring} duck.html.components.HtmlComponent.vdom_diff
```

````

````{py:method} vdom_diff_and_act(action: typing.Callable, old: duck.html.components.core.vdom.VDomNode, new: duck.html.components.core.vdom.VDomNode) -> None
:canonical: duck.html.components.HtmlComponent.vdom_diff_and_act
:async:
:staticmethod:

```{autodocx-docstring} duck.html.components.HtmlComponent.vdom_diff_and_act
```

````

````{py:method} wait_for_load(interval: float = 0.01)
:canonical: duck.html.components.HtmlComponent.wait_for_load

```{autodocx-docstring} duck.html.components.HtmlComponent.wait_for_load
```

````

`````

````{py:data} InnerComponent
:canonical: duck.html.components.InnerComponent
:value: >
   None

```{autodocx-docstring} duck.html.components.InnerComponent
```

````

`````{py:class} InnerHtmlComponent(element: typing.Optional[str] = None, properties: typing.Optional[typing.Dict[str, str]] = None, props: typing.Optional[typing.Dict[str, str]] = None, style: typing.Optional[typing.Dict[str, str]] = None, inner_html: typing.Optional[typing.Union[str, str, float]] = None, children: typing.Optional[typing.List[duck.html.components.HtmlComponent]] = None, **kwargs)
:canonical: duck.html.components.InnerHtmlComponent

Bases: {py:obj}`duck.html.components.extensions.BasicExtension`, {py:obj}`duck.html.components.extensions.StyleCompatibilityExtension`, {py:obj}`duck.html.components.HtmlComponent`

```{autodocx-docstring} duck.html.components.InnerHtmlComponent
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.html.components.InnerHtmlComponent.__init__
```

````{py:method} add_child(child: duck.html.components.HtmlComponent)
:canonical: duck.html.components.InnerHtmlComponent.add_child

```{autodocx-docstring} duck.html.components.InnerHtmlComponent.add_child
```

````

````{py:method} add_children(children: typing.List[duck.html.components.HtmlComponent])
:canonical: duck.html.components.InnerHtmlComponent.add_children

```{autodocx-docstring} duck.html.components.InnerHtmlComponent.add_children
```

````

````{py:property} children
:canonical: duck.html.components.InnerHtmlComponent.children
:type: duck.html.components.core.children.ChildrenList[duck.html.components.HtmlComponent]

```{autodocx-docstring} duck.html.components.InnerHtmlComponent.children
```

````

````{py:method} clear_children()
:canonical: duck.html.components.InnerHtmlComponent.clear_children

```{autodocx-docstring} duck.html.components.InnerHtmlComponent.clear_children
```

````

````{py:method} remove_child(child: duck.html.components.HtmlComponent)
:canonical: duck.html.components.InnerHtmlComponent.remove_child

```{autodocx-docstring} duck.html.components.InnerHtmlComponent.remove_child
```

````

````{py:method} remove_children(children: typing.List[duck.html.components.HtmlComponent])
:canonical: duck.html.components.InnerHtmlComponent.remove_children

```{autodocx-docstring} duck.html.components.InnerHtmlComponent.remove_children
```

````

`````

````{py:data} NoInnerComponent
:canonical: duck.html.components.NoInnerComponent
:value: >
   None

```{autodocx-docstring} duck.html.components.NoInnerComponent
```

````

````{py:class} NoInnerHtmlComponent(element: typing.Optional[str] = None, properties: typing.Dict[str, str] = None, props: typing.Dict[str, str] = None, style: typing.Dict[str, str] = None, **kwargs)
:canonical: duck.html.components.NoInnerHtmlComponent

Bases: {py:obj}`duck.html.components.extensions.BasicExtension`, {py:obj}`duck.html.components.extensions.StyleCompatibilityExtension`, {py:obj}`duck.html.components.HtmlComponent`

```{autodocx-docstring} duck.html.components.NoInnerHtmlComponent
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.html.components.NoInnerHtmlComponent.__init__
```

````

`````{py:class} Theme
:canonical: duck.html.components.Theme

```{autodocx-docstring} duck.html.components.Theme
```

````{py:attribute} background_color
:canonical: duck.html.components.Theme.background_color
:value: >
   '#FFFFFF'

```{autodocx-docstring} duck.html.components.Theme.background_color
```

````

````{py:attribute} border_radius
:canonical: duck.html.components.Theme.border_radius
:value: >
   '15px'

```{autodocx-docstring} duck.html.components.Theme.border_radius
```

````

````{py:attribute} button_style
:canonical: duck.html.components.Theme.button_style
:value: >
   None

```{autodocx-docstring} duck.html.components.Theme.button_style
```

````

````{py:attribute} font_family
:canonical: duck.html.components.Theme.font_family
:value: >
   'Arial, sans-serif'

```{autodocx-docstring} duck.html.components.Theme.font_family
```

````

````{py:attribute} normal_font_size
:canonical: duck.html.components.Theme.normal_font_size
:value: >
   '16px'

```{autodocx-docstring} duck.html.components.Theme.normal_font_size
```

````

````{py:attribute} padding
:canonical: duck.html.components.Theme.padding
:value: >
   '10px'

```{autodocx-docstring} duck.html.components.Theme.padding
```

````

````{py:attribute} primary_color
:canonical: duck.html.components.Theme.primary_color
:value: >
   '#4B4E75'

```{autodocx-docstring} duck.html.components.Theme.primary_color
```

````

````{py:attribute} secondary_color
:canonical: duck.html.components.Theme.secondary_color
:value: >
   '#A6B48B'

```{autodocx-docstring} duck.html.components.Theme.secondary_color
```

````

````{py:attribute} text_color
:canonical: duck.html.components.Theme.text_color
:value: >
   '#333333'

```{autodocx-docstring} duck.html.components.Theme.text_color
```

````

`````

````{py:function} quote(html: typing.Optional[str] = None, element: str = 'span', no_closing_tag: bool = False, **kwargs) -> typing.Union[InnerComponent, NoInnerComponent]
:canonical: duck.html.components.quote

```{autodocx-docstring} duck.html.components.quote
```
````

````{py:function} to_component(html: typing.Optional[str] = None, tag: str = 'span', no_closing_tag: bool = False, **kwargs)
:canonical: duck.html.components.to_component

```{autodocx-docstring} duck.html.components.to_component
```
````
