"""
This module defines HTML components that can be inserted into HTML pages or used to dynamically generate HTML.

These components can be embedded in templates or directly manipulated in Python code.

---

**Template Usage Examples**

*Jinja2 Template:*

```jinja
{{ Button(
      id="btn",
      text="Hello world",
    )
}}

{# Alternatively: #}

{{ Button(
      inner_html="Hello world",
      props={
         "id": "btn",
      },
    )
}}
```

*Django Template:*

```django
{% Button %}
    id="btn",
    text="Hello world",
{% endButton %}

{# Alternatively: #}

{% Button %}
    inner_html="Hello world",
    props={
        "id": "btn",
    },
{% endButton %}
```

To leverage these components, ensure the setting `ENABLE_COMPONENT_SYSTEM` is set to `True`.

---

**Direct Usage Example**

```py
from duck.html.components.button import Button
from duck.html.components.page import Page
from duck.html.core.websocket import LivelyWebSocketView
from duck.html.core.exceptions import JSExecutionError, JSExecutionTimedOut


async def on_click(btn: Button, event: str, value: str, websocket: LivelyWebSocketView):
    '''
    Button onclick event.
    
    Args:
        btn (Button): Button component which received the event.
        event (str): The event name.
        value (str): The current button value.
        websocket (LivelyWebSocketView): The current active websocket connection.
    '''
    # This handler can also be either asynchronous or synchronous.
    if btn.bg_color != "red":
        btn.bg_color = "red"
    else:
        btn.bg_color = "green"
    
    # You can also execute JS on client side like so.
    # but the execution will execute first before button changes color.
    try:
        await websocket.execute_js(
            code='alert(`Javascript execution success`);',
            timeout=2,
            wait_for_result=True, # This will wait for feedback on execution.
        ) # or you can use get_js_result() for retrieving a variable result after code execution.
    except (JSExecutionTimedOut, JSExecutionError):
        # JS execution timed out or the code raised an error on client side.
        pass

def home(request):
    page = Page(request)
    btn = Button(
        id="some-id",
        text="Hello world",
        bg_color="green",
        color="white",
    )
    
    # Add button to body
    page.add_to_body(btn)
    
    # Bind an event handler to the button
    btn.bind("click", on_click)
    
    print(btn.render())  # Outputs the corresponding HTML
    
    # Return component or ComponentResponee
    return page

```

You can render this component in a template or use it anywhere HTML output is needed.

---

**Defining Your Own Component**

Subclassing the component class allows you to create custom components easily.

```py
# This example uses a component that accepts an inner body.
# Use `NoInnerComponent` if you don’t need inner content.

from duck.html.components import InnerComponent
from duck.html.components.button import Button
from duck.shortcuts import to_response

class MyComponent(InnerComponent):
    def get_element(self):
        # Return the HTML tag name
        return "div"

    def on_create(self):
        # Called after initialization
        super().on_create()  # Useful for extending base behavior, don't leave this out
        
        # You can access provided extra keyword arguments provided to the component by 
        # accessing `self.kwargs`
        
        # Do some operations
        self.add_child(Button(text="Hi there"))

# In views.py
def home(request):
    comp = MyComponent(request=request) # you can provide extra keyword arguments here.
    print("request" in comp.kwargs) # Outputs: True
    response = to_response(comp)  # More control than just returning comp
    return response

# Instead of using to_response, you can use duck.http.response.ComponentResponse instead.
```
"""
import re
import secrets

from collections import deque, UserDict
from typing import (
    Dict,
    List,
    Optional,
    Callable,
    Any,
    Tuple,
    Union,
)

from duck.utils.lazy import Lazy, LiveResult
from duck.html.components.extensions import BasicExtension, StyleCompatibilityExtension
from duck.html.components.core.vdom import VDomNode
from duck.html.components.core.warnings import DeeplyNestedEventBindingWarning
from duck.html.components.core.force_update import ForceUpdate as ForceUpdate # Avoids this being removed as unused on when formatters touch this.
from duck.html.components.core.exceptions import (
    HtmlComponentError,
    AlreadyInRegistry,
    RedundantUpdate,
    UnknownEventError,
    InitializationError,
    EventAlreadyBound,
    ComponentAttributeProtection,
)


# Patten for matching an html tag/element.
ELEMENT_PATTERN = re.compile(r"\b[a-zA-Z0-9]+\b")


def quote(html: Optional[str] = None, element: str = 'span', no_closing_tag: bool = False, **kwargs) -> Union["InnerComponent", "NoInnerComponent"]:
    """
    Returns an html component quoting the provided html as its body.
    
    Args:
        html (str): The html to quote, to set as the new html component body.
        element (str): Element to quote with, Defaults to span.
        no_closing_tag (bool): Whether the returned html component does not need a closing tag.
        **kwargs: Keyword arguments to parse to component
        
    Returns:
        InnerComponent: The html component with closing tags.
        NoInnerComponent: The html component with no closing tags.
    """
    if no_closing_tag:
        if html:
            raise ComponentError("The argument `no_closing_tag=True` yet inner html is provided. Please set html to None instead.")
        return NoInnerComponent(element=element, **kwargs)
    return InnerComponent(inner_html=html or "", element=element, **kwargs)


def to_component(html: Optional[str] = None, tag: str = 'span', no_closing_tag: bool = False, **kwargs):
    """
    Returns an html component quoting the provided html as its body. (Same as `quote` function).
    
    Args:
        html (str): The html to quote, to set as the new html component body.
        tag (str): HTML tag to quote with, Defaults to span.
        no_closing_tag (bool): Whether the returned html component does not need a closing tag.
        **kwargs: Keyword arguments to parse to the component.
    
    Returns:
        InnerComponent: The html component with closing tags.
        NoInnerComponent: The html component with no closing tags.
    """
    return quote(html or "", tag, no_closing_tag, **kwargs)


class PropertyStore(dict):
    """
    A dictionary subclass to store properties for HTML components, with certain restrictions.

    Keys and values must both be strings. Certain methods (pop, popitem, update, setdefault, etc.)
    are overridden to ensure they utilize the custom __setitem__ and __delitem__ logic,
    including event hooks for set and delete operations.  
    
    **Args:**
    - `*args`: Arguments to initialize the dictionary.
    - `**kwargs`: Keyword arguments to initialize the dictionary.
    """
    __slots__ = ()

    def __setitem__(self, key: str, value: str, call_on_set_item_handler: bool = True) -> None:
        """
        Sets the value for the given key if the key is allowed.

        Args:
            key (str): The key to set the value for. Must be a string.
            value (str): The value to set. Must be a string.
            call_on_set_item_handler (bool): Whether to call `on_set_item` after the actual `__setitem__`.

        Raises:
            AssertionError: If the key or value is not a string.
        """
        assert isinstance(key, str), f"Keys for `PropertyStore` must be strings not {type(key)}"
        assert isinstance(value, str), f"Values for `PropertyStore` must be strings not {type(value)}"
        k = key.strip().lower()
        super().__setitem__(k, value)
        if call_on_set_item_handler:
            self.on_set_item(k, value)

    def __delitem__(self, key: str, call_on_delete_item_handler: bool = True) -> None:
        """
        Deletes a key from the property store.

        Args:
            key (str): The key to delete. Must be a string.
            call_on_delete_item_handler (bool): Whether to call `on_delete_item` after the actual `__delitem__`.
        """
        k = key.strip().lower()
        super().__delitem__(k)
        if call_on_delete_item_handler:
            self.on_delete_item(k)

    def __repr__(self) -> str:
        """
        Returns a string representation of PropertyStore.

        Returns:
            str: String representation of the PropertyStore.
        """
        return f"<{self.__class__.__name__} {dict(self).__repr__()}>"

    def update(self, data: Any = None, call_on_set_item_handler: bool = True, *args, **kwargs) -> None:
        """
        Updates the PropertyStore with the key/value pairs from data, ensuring setitem logic.

        Args:
            data (Any): Mapping or iterable to update from.
            call_on_set_item_handler (bool): Whether to call `on_set_item` for each item.
            *args, **kwargs: Additional data.
        """
        if data is not None:
            if hasattr(data, 'items'):
                items = data.items()
            else:
                items = data
            for key, value in items:
                self.__setitem__(key, value, call_on_set_item_handler)
        for key, value in dict(*args, **kwargs).items():
            self.__setitem__(key, value, call_on_set_item_handler)

    def setdefault(self, key: str, default: Optional[str] = None, call_on_set_item_handler: bool = True) -> str:
        """
        Inserts key with a value of default if key is not in the dictionary.

        Args:
            key (str): The key to check.
            default (str, optional): The default value to set if key is missing.
            call_on_set_item_handler (bool): Whether to call `on_set_item` if setting.

        Returns:
            str: The value for the key.
        """
        k = key.strip().lower()
        if k not in self:
            self.__setitem__(k, default if default is not None else '', call_on_set_item_handler)
            return default if default is not None else ''
        return self[k]

    def pop(self, key: str, default: Any = None) -> Any:
        """
        Removes the specified key and returns its value.
        If key is not found, default is returned if provided, otherwise KeyError is raised.

        Args:
            key (str): The key to remove.
            default (Any, optional): The value to return if key is not found.

        Returns:
            Any: The value associated with the key, or default.

        Raises:
            KeyError: If key is not found and default is not provided.
        """
        k = key.strip().lower()
        if k in self:
            value = self[k]
            self.__delitem__(k)
            return value
        elif default is not None:
            return default
        else:
            raise KeyError(k)

    def popitem(self) -> Tuple[str, str]:
        """
        Removes and returns a (key, value) pair from the dictionary.
        Pairs are returned in LIFO order.

        Returns:
            Tuple[str, str]: The removed (key, value) pair.

        Raises:
            KeyError: If the dictionary is empty.
        """
        try:
            k, v = next(reversed(self.items()))
        except StopIteration:
            raise KeyError(f"{self.__class__.__name__} is empty")
        self.__delitem__(k)
        return k, v

    def setdefaults(self, data: Dict[str, str]) -> None:
        """
        Calls setdefault on multiple items.

        Args:
            data (Dict[str, str]): The key-value pairs to set as defaults.
        """
        for key, value in data.items():
            self.setdefault(key, value)

    def on_set_item(self, key: str, value: Any) -> None:
        """
        Called after `__setitem__`.

        Args:
            key (str): The key set.
            value (Any): The value set.
        """
        pass

    def on_delete_item(self, key: str) -> None:
        """
        Called after `__delitem__`.

        Args:
            key (str): The key deleted.
        """
        pass


class StyleStore(PropertyStore):
    """
    PropertyStore dictionary for component styling.
    """


class HtmlComponent:
    """
    Base class for all HTML components.

    This class provides the foundational structure for defining HTML-based UI components
    in the Lively component system.

    Notes:
    - If the Lively Component System is active, each component is lazily registered.
          A component is only added to the component registry after `render()` or `to_string()` 
          has been called.
    - To improve performance and reduce re-rendering overhead, heavy components can be 
          pre-rendered. Once pre-rendered, subsequent renders are faster due to internal caching. You 
          can do this by using method `pre_render`.
    - All Lively components are validated before any event is sent to the server, this is disabled by adding prop `data-validate=false` in props.
          Empty props without `data-validate=false`, default is validation.
          You can even toggle this by using method `toggle_validation`.
    """
    def __init__(
        self,
        element: Optional[str] = None,
        accept_inner_html: bool = False,
        inner_html: Optional[Union[str, LiveResult, Lazy]] = None,
        properties: Optional[Dict[str, str]] = None,
        props: Optional[Dict[str, str]] = None,
        style: Optional[Dict[str, str]] = None,
        **kwargs,
    ):
        """
        Initialize an HTML component.

        Args:
            element (Optional[str]): The HTML element tag name (e.g., textarea, input, button). Can be None, but make sure element is returned by get_element method.
            accept_inner_html (bool): Whether the HTML component accepts an inner body (e.g., <strong>inner-body-here</strong>).
            inner_html (Union[str, LiveResult, Lazy]): Inner body to add to the HTML component. Defaults to None.
            properties (dict, optional): Dictionary for properties to initialize the component with.
            props (dict, optional): Just same as properties argument (added for simplicity).
            style (dict, optional): Dictionary for style to initialize the component with.
            **kwargs: Extra keyword arguments
        
        Raises:
            HtmlComponentError: If 'element' is not a string or 'inner_html' is set but 'accept_inner_html' is False.
        """
        # Note: id, bg_color, color is handled by the BasicExtension
        
        element = element or self.get_element()
        
        assert len(element) < 24, f"HTML tags should not be longer than 24 characters. Got tag: `{element}`, len={len(element)}."
        
        if not isinstance(element, str):
            raise HtmlComponentError(
                f"Argument 'element' should be a valid string representing the HTML element tag name not \"{element}\": {type(element)}."
            )
            
        if not ELEMENT_PATTERN.findall(element):
            raise HtmlComponentError(
                f"Argument 'element' is has invalid format, change the element to something else."
            )

        if inner_html and not accept_inner_html:
            raise HtmlComponentError(
                "Argument 'inner_html' is set yet 'accept_inner_html' is False."
            )
        
        if "children" in kwargs and not isinstance(self, InnerHtmlComponent):
            raise HtmlComponentError(
                "Argument 'children' is not supported for this type of component, use `InnerComponent` instead."
            )
        
        if "tag" in kwargs:
            raise HtmlComponentError(
                "Argument 'tag' is not supported, use `element` instead. Tag argument is only limited to `to_component` function."
            )
            
        # Set some private attributes
        self.__properties = PropertyStore() # Basic properties
        self.__style = StyleStore()  # Properties for CSS styling
        self.__parent = None
        self.__root = self
        self.__render_done = False
        self.__inner_html = inner_html or ""
        self.__uid = None
        
        # Other private attributes
        cls = self.__class__.__name__ 
        self._event_bindings = {}
        self._event_bindings_changed = False # Whether event bindings changed.
        self._on_create_check_passed = False
        self._deeply_nested_event_binding_warned = False
        self._on_root_finalized_called = False
        self._must_validate_on_event = True
        self._ignore_setting_data_validate_if_true = True # Ignore setting data-validate prop if its True
        self._component_attr_protection = True # Whether to protect attributes referring to Component instance from modification.
        self._component_attr_protection_targets = {} # Target attributes to protect, will be set automatically when __setattr__ is called.  
        self._component_attr_protection_exceptions = [
            "root",
            "parent",
            "_HtmlComponent__root",
            "_HtmlComponent__parent",
            f"_{cls}__root",
            f"_{cls}__parent",
        ] # List of attributes to ignore when enforcing Component Attribute Protection
        
        # Add public attributes
        self.element = element
        self.accept_inner_html = accept_inner_html
        self.add_to_registry = kwargs.get('add_to_registry', True)
        self.kwargs = kwargs
        self.escape_on_text = kwargs.get('escape_on_text', True) # Whether to escape if modifying component text prop
        self.disable_lively = kwargs.get('disable_lively', False) # Whether to disable lively for this component
        
        # Make some updates and assertions.
        properties = properties or {}
        props = props or {}
        style = style or {}
        
        assert isinstance(properties, dict) == True, f"Properties for the Html component must be a dictionary not '{type(properties)}' "
        assert isinstance(style, dict) == True, f"Style for the Html component must be a dictionary not '{type(properties)}'"
        assert not (props and properties), "Properties and props cannot be provided at the same time. Provide one of them instead." 
        
        # Update some styles and properties
        self.__properties.update(properties or props)
        self.__style.update(style)
        
        # Create some previous states e.g. {prev_props: (obj, "rendered_data")}
        self._prev_states = {
          "prev_props": ({}, ""),
          "prev_style": ({}, ""),
          "prev_inner_html": (""),
        } # Don't look at children as they may change any moment deep within the DOM tree.
        
        # Sets the previous rendered partial string, which may include style, props & inner body strings
        self._prev_partial_string = ""
        
        # Finally, call the component entry method.
        self.on_create() # If super().on_create() is called then _on_create_check_passed will be True.
        
        if not self._on_create_check_passed:
            raise InitializationError(
                f"Method `on_create` of component {repr(self)} was overridden somehow but `super().on_create()` was not called. "
                "This may result in some component extensions not being properly applied or inconsistences within the component."
              )
          
    @property
    def properties(self):
        """
        Returns the properties store for the HTML component.

        Returns:
            PropertyStore: The properties store for the HTML component.
        """
        from duck.html.components.core.system import LivelyComponentSystem
        
        lively_data_props = {"data-uid", "data-events", "data-document-events", "data-validate"}
        
        if LivelyComponentSystem.is_active() and not self.disable_lively:
            current_lively_props = self.get_component_system_data_props()
            self.__properties.update(current_lively_props)
            
            # Remove data-* props if not present anymore.
            for prop in lively_data_props:
                if prop not in current_lively_props and prop in self.__properties.keys():
                    # Delete prop from __properties
                    del self.__properties[prop]
        else:
            for prop in lively_data_props:
                if prop in self.__properties.keys():
                    del self.__properties[prop]
        return self.__properties

    @property
    def props(self):
        """
        Returns the properties store for the HTML component. (same as `properties` property)

        Returns:
            PropertyStore: The properties store for the HTML component.
        """
        return self.properties
        
    @property
    def style(self):
        """
        Returns the style store for the HTML component.

        Returns:
            PropertyStore: The style store for the HTML component.
        """
        return self.__style

    @property
    def root(self) -> Optional["Component"]:
        """
        Returns the root html component.
        """
        if self.__root == self:
            return None
        return self.__root
        
    @root.setter
    def root(self, root: "Component"):
        """
        Sets the root html component.
        """
        self.__root = root
        
    @property
    def parent(self) -> Optional["Component"]:
        """
        Returns the parent for the html component. This is only resolved if this html component has been added to some html component children.
        """
        return self.__parent
        
    @parent.setter
    def parent(self, parent):
        """
        Sets the parent for the html component.
        """
        self.__parent = parent
    
    @property
    def uid(self) -> str:
        """
        Returns the UID for the component based on the component position.
        
        Returns:
            str: An assigned component UID based on component position in component tree
                   or a random 64-bit string.
            
        Notes:
        - This will be auto-assigned on render or when `to_vdom` is called. These methods 
               call `assign_component_uids` for assigning determinable UID's.
        - If a component is a root component, a unique ID will be generated whenever the `uid` property is accessed.
        """
        if self.isroot() and not self.__uid:
            self.__uid = secrets.token_urlsafe(8) # Will return a 64bit uid
        if not self.__uid:
            raise ComponentError("Property `uid` is not assigned yet, `assign_component_uids` must be called first.")
        return self.__uid
        
    @uid.setter
    def uid(self, uid: str):
        """
        Sets the component UID.
        """
        self.__uid = uid
        
    @property
    def inner_html(self):
        """
        Returns the inner body (innerHTML) for the component.
        """
        inner_html = self.__inner_html
        
        if isinstance(inner_html, Lazy):
            # These objects tries to resolve live updated result
            return str(inner_html)
        return inner_html
    
    @inner_html.setter
    def inner_html(self, inner_html: Union[str, LiveResult, Lazy]):
        """
        Set the component innerHTML.
        
        Args:
            inner_html (Union[str, LiveResult, Lazy]): This can be a string, LiveResult or Lazy object. The LiveResult
                object lets you compute the live or the updated text instead of static text and the Lazy object is the super class
                of the LiveResult object but it caches results by default compared to LiveResult.
                
                Example:
                
                ```py
                from duck.utils.lazy import LiveResult
                from duck.html.components.button import Button
                
                btn = Button()
                btn.counter = 0
                live_str = LiveResult(lambda comp: f"{comp.counter}", btn)
                btn.inner_html = live_str
                
                print(btn.inner_html) # Outputs: 0
                
                # Increment counter
                btn.counter += 1
                
                print(btn.inner_html) # Outputs: 1 instead of 0
                
                ```
        """
        if not self.accept_inner_html:
            raise ComponentError("This component doesn't accept inner body, use InnerComponent instance instead.")
            
        if not isinstance(inner_html, (str, Lazy)):
            raise ComponentError("The inner_html should be an instance of string, LiveResult or Lazy object.")
        self.__inner_html = inner_html
        
    @property
    def render_done(self):
        """
        Returns if rendering is done on the component.
        """
        return self.__render_done
        
    def _get_raw_props(self):
        """
        Returns the component properties.
        """
        return self.__properties
        
    def get_raw_root(self) -> "Component":
        """
        Returns the raw root reference without evaluation,
        even if the root is self (unlike the `root` property).
        """
        return self.__root
            
    def isroot(self) -> bool:
        """
        Returns a boolean on whether if the component is a root component.
        """
        return True if (not self.root and not self.parent) else False
        
    def get_element(self):
        """
        Fallback method to retrieve the html element tag.
        """
        raise NotImplementedError(f"Method `get_element` is not implemented yet the element argument is empty or None. This is a fallback method.")
    
    def on_create(self):
        """
        Called on component creation or initialization
        """
        # Set the following to True, to mark this method to have been called.
        self._on_create_check_passed = True
        
    def on_parent(self, parent: "Component"):
        """
        Called when the component has got a parent attached.
        """
        pass
    
    def on_root_finalized(self, root: "Component"):
        """
        Called when the component's root element is permanently assigned.
    
        This method is invoked once the component is fully integrated into its
        final root within the application's structure, and this root will
        not change for the lifetime of the component.  Use this hook to perform
        any final setup or initialization that requires access to the
        fully realized root element, such as registering with the root's
        event system, performing final layout adjustments, or establishing
        contextual relationships within the application.
    
        Args:
            root: The root element to which this component is now permanently attached.
                  This is the final root and will not be reassigned.
        """
        pass
        
    @staticmethod
    def vdom_diff(old: VDomNode, new: VDomNode) -> List[list]:
        """
        Compute a minimal set of patches to transform one virtual DOM tree into another.

        This method performs key-based diffing on children and emits compact patch lists
        using `vdom.PatchCodes`. Each patch is a list optimized for fast encoding with MessagePack.

        Args:
            old (VDomNode): The previous virtual DOM node.
            new (VDomNode): The updated virtual DOM node.

        Returns:
            List[list]: A list of compact patch operations (lists) in the format:
                [opcode, key, ...data]
        """
        return VDomNode.diff(old, new)
        
    @staticmethod
    async def vdom_diff_and_act(action: Callable, old: VDomNode, new: VDomNode) -> None:
        """
        Compute a minimal set of patches to transform one virtual DOM tree into another.
    
        This method performs key-based diffing on children and emits compact patch lists
        using PatchCode. Each patch is a list optimized for fast encoding with MessagePack.
        
        This method diffs and perform an action on every patch rather than returning a list of all 
        computed patches.
        
        Args:
            action (Callable): A synchronous/asynchronous callable to perform on every patch.
                The first argument to this must be the patch.
            old (VDomNode): The previous virtual DOM node.
            new (VDomNode): The updated virtual DOM node.
    
        Returns:
            None: Nothing to return.
        """
        await VDomNode.diff_and_act(action, old, new)
        
    @staticmethod
    def assign_component_uids(root_component: "Component", base_uid: str = "0") -> None:
        """
        Assigns deterministic UIDs to the entire component tree using a non-recursive traversal.
    
        Args:
            root_component (HtmlComponent): The root component to start from.
            base_uid (str): The base UID for the root (default is "0").
        """
        from duck.logging import logger
        from duck.html.components.core.system import LivelyComponentSystem
        
        if not root_component.isroot():
            raise ComponentError("Root component is required for `uid` assignment, not a child component.")
            
        queue = deque()
        queue.append((root_component, root_component.uid))
        
        # The max nesting level for component with event bindings
        max_nesting_level = 9
        
        while queue:
            component, uid = queue.popleft()
            component.uid = uid
            
            # Call on_parent event.
            if not component._on_root_finalized_called:
                component.on_root_finalized(component.root)
                component._on_root_finalized_called = True
                
            # Check for deep nesting for components with event bindings
            if component._event_bindings and not component._deeply_nested_event_binding_warned:
                 level = uid.count(".")
                 if level > max_nesting_level:
                     logger.warn(
                         f"Warning: The component {component} is deeply nested at level {level} "
                         "and has event bindings attached. Updates to this component may be slow due to increased DOM traversal, "
                        "layout recalculations, and event propagation overhead. "
                        f"Consider reducing nesting depth to {max_nesting_level} or optimizing event handling.\n",
                        DeeplyNestedEventBindingWarning,
                    )
                                                  
            # Add component to the registry
            if LivelyComponentSystem.is_active() and component.add_to_registry:
                try:
                    LivelyComponentSystem.add_to_registry(uid, component)
                except AlreadyInRegistry:
                    pass
                    
            if component == root_component:
                # This is the first iteration
                # Don't use root component uid as base_uid because it will make every
                # child's uid unique therefore leading to unneccessary patches.
                uid = base_uid
                
            children = getattr(component, "children", [])
            for index, child in enumerate(children):
                # Use (.) dot separator to avoid ambiguity in cases index is like the {uid}
                child_uid = f"{uid}.{index}"
                queue.append((child, child_uid))
                
    def to_vdom(self) -> VDomNode:
        """
        Converts the HtmlComponent into a virtual DOM node.
    
        Returns:
            VDomNode: A virtual DOM representation of the HTML component.
        """
        if self.isroot():
            # Assign component UID's
            self.assign_component_uids(self)
                
        # Make sure we use copies of the real component so that further changes will impose a difference
        try:
            _ = self.uid # Check if uid assigned yet.
        except ComponentError:
            # Property uid not assigned yet
            # This component might have been inserted after an event e.g. onclick.
            # Reassign component tree UID's to avoid messing up the structure thereby avoiding
            # unnecessary patches
            root = self.root
            if root:
                self.assign_component_uids(root)
            
        return VDomNode(
            tag="%s"%self.element,
            key=self.uid,
            props=self.props.copy(),
            style=self.style.copy(),
            text="%s"%self.inner_html if self.accept_inner_html else None,
            children=[child.to_vdom() for child in getattr(self, "children", [])],
            component=self,
        )
    
    def check_component_system_active(self, inactive_msg: str = None):
        """
        Checks if the component system responsible for `WebSocket` communication
        with the client is active.
        
        Notes:
            The component system sends DOM patches to client using `WebSocket` protocol.
            It also receives component events so that they can be executed on the server.
            Sends signals to perform an action to the JS client WebSocket.
        """
        from duck.html.components.core.system import LivelyComponentSystem
        
        if not LivelyComponentSystem.is_active():
            raise HtmlComponentError(inactive_msg or "Lively Component System is not active.")
        
    def toggle_validation(self, must_validate: bool):
        """
        Whether to enable/disable validation on component before server receives an event.
        
        Notes:
        - Validation is only applied if the JS element has both `checkValidity` and `reportValidity`.
        """
        self._must_validate_on_event = must_validate
        
    def bind(
        self,
        event: str,
        event_handler: Callable,
        force_bind: bool = False,
        update_targets: Optional[List["HtmlComponent"]] = None,
        update_self: bool = True,
    ) -> None:
        """
        Bind an event handler to this component for the specified event type.
    
        Args:
            event (str): The name of the event to bind (e.g., "click", "input").
            event_handler (Callable): A callable (preferably async) that handles the event.
            force_bind (bool): If True, binds the event even if it's not in the recognized set.
            update_targets (List[HtmlComponent], optional): Other components whose state may be modified 
                when this event is triggered. Defaults to None.
            update_self (bool): Whether this component’s state may change as a result of the event. 
                If False, only other components will be considered for DOM updates. Defaults to True.
    
        Raises:
            UnknownEventError: If the event is not recognized and `force_bind` is False.
            AssertionError: If the event handler is not a callable.
            RedundantUpdate: If any component pair in `update_targets` share the same root/parent.
            EventAlreadyBound: If event is already bound before.
            
        Notes:
            - If `update_self` is False and no `update_targets` are provided, no DOM patch will be sent to the client.
            - This method requires the Lively Component System to be active (i.e., running within a WebSocket context).
        """
        # Check if component system active
        self.check_component_system_active(
            "Lively Component System is not active. "
            "This is required to enable WebSocket communication for managing lively components."
        )
        
        known_events = {
            # Mouse Events
            "click", "dblclick", "mousedown", "mouseup", "mouseenter",
            "mouseleave", "mousemove", "mouseover", "mouseout", "contextmenu",
        
            # Keyboard Events
            "keydown", "keypress", "keyup",
        
            # Form Events
            "input", "change", "submit", "reset", "invalid", "select",
        
            # Focus Events
            "focus", "blur", "focusin", "focusout",
        
            # Drag Events
            "drag", "dragstart", "dragend", "dragenter", "dragleave",
            "dragover", "drop",
        
            # Clipboard Events
            "copy", "cut", "paste",
        
            # Media Events
            "abort", "canplay", "canplaythrough", "cuechange", "durationchange",
            "emptied", "ended", "error", "loadeddata", "loadedmetadata",
            "loadstart", "pause", "play", "playing", "progress", "ratechange",
            "seeked", "seeking", "stalled", "suspend", "timeupdate", "volumechange",
            "waiting",
        
            # Touch Events
            "touchstart", "touchmove", "touchend", "touchcancel",
        
            # Pointer Events
            "pointerdown", "pointerup", "pointermove", "pointerover", "pointerout",
            "pointerenter", "pointerleave", "gotpointercapture", "lostpointercapture",
            "pointercancel",
        
            # Wheel and Scroll
            "wheel", "scroll",
        
            # Animation and Transition Events
            "animationstart", "animationend", "animationiteration",
            "transitionstart", "transitionend", "transitionrun", "transitioncancel",
        
            # Other Global Events
            "resize", "error", "load", "unload", "beforeunload", "hashchange",
            "popstate", "storage", "pagehide", "pageshow",
        }
        
        if event in self._event_bindings:
            raise EventAlreadyBound(f"Event `{event}` already bound, please call `unbind` first before rebinding.")
            
        if not force_bind and event not in known_events:
            raise UnknownEventError(
                f"Event `{event}` not recognized. Set `force_bind=True` to bind anyway. Supported: {known_events}."
            )
    
        assert callable(event_handler), "Event handler must be a callable."
        
        sync_targets = set(update_targets or []) # same as update_targets
        
        if update_self:
            sync_targets.add(self)
        
        # Checking for repetitive unnecessary updates.
        for target in sync_targets:
            for other in sync_targets:
                if target is not other:
                    if target.parent == other.parent:
                        raise RedundantUpdate(
                            f"Conflicting updates detected: {repr(target)} and {repr(other)} share the same parent. "
                            "Use only one top-level update target."
                        )
                        
                    if target.get_raw_root() == other.get_raw_root(): # Use get_raw_root() instead of root property for the raw explicit root.
                        raise RedundantUpdate(
                            f"Conflicting updates detected: {repr(target)} and {repr(other)} share the same root. "
                            "Use only one top-level update target."
                        )
                    
        self._event_bindings[event] = (
            event_handler,
            update_targets or [],
            update_self,
        )
        
        # Flag that event bindings changed.
        self._event_bindings_changed = True
    
    def unbind(self, event: str, failsafe: bool = True):
        """
        Remove/unbind an event from this component.
        
        Args:
            event (str): The event name to unbind.
            failsafe (bool, optional): If True (default), silently ignore if the event was never bound.
                If False, raise UnknownEventError if the event does not exist.
    
        Raises
            UnknownEventError: If failsafe is False and the event is not bound.
        """
        try:
            # Delete event binding
            del self._event_bindings[event]
            # Set that event bindings somehow changed.
            self._event_bindings_changed = True
        except KeyError:
            if not failsafe:
                raise UnknownEventError(f"Event '{event}' is not bound to this component: {self}.")
               
    def get_event_info(self, event: str) -> Tuple[Callable, List["HtmlComponent"], bool]:
        """
        Returns the event info in form: (event_handler, sync_changes_with, sync_changes_with_self).
        """
        event_info = self._event_bindings.get(event, None)
        
        if not event_info:
            raise UnknownEventError(f"Event `{event}` is not bound to this component: {self}.")
        return event_info
        
    def get_component_system_data_props(self) -> Dict[str, str]:
        """
        Returns the `data-*` properties for events, actions, and other attributes
        used internally by the `Lively` component system (e.g., for client-server sync via WebSocket).
    
        This typically includes:
         - `data-uid`: The stable component ID or unique ID if a component is a root component.
         - `data-events`: A comma-separated list of bound event names. (if available)
         - `data-validate`: Boolean on whether validation must be applied.
            
        Returns:
            Dict[str, str]: A dictionary of `data-*` attributes and their corresponding values.
        """
        data_props = {}
        uid = None
        
        try:
            uid = self.uid # UID not assigned yet.
        except ComponentError:
            # UID not assigned yet
            return {}
            
        # Ensure component has a unique ID
        data_props["data-uid"] = uid
    
        # Include bound events
        if self._event_bindings:
            data_props["data-events"] = ",".join(self._event_bindings.keys())
        
        # Include validity
        if self._must_validate_on_event:
            if not self._ignore_setting_data_validate_if_true:
                # This avoids redundant data-validate props because lively assumes
                # that if not explicitly `data-validate=false`, then data-validate is always true.
                data_props["data-validate"] = "true"
        else:
            data_props["data-validate"] = "false"
            
        # Also include events bound to the document directly.
        # Page component already implement these.
        if hasattr(self, "_document_event_bindings") and self._document_event_bindings:
            data_props["data-document-events"] = ",".join(self._document_event_bindings.keys())
            
        return data_props
        
    def get_css_string(self, style: Dict[str, str], add_to_prev_states: bool = False) -> str:
        """
        Returns a CSS style string from a dictionary of style attributes.
    
        Args:
            style (Dict[str, str]): The style attributes (e.g., {"color": "red", "font-size": "12px"}).
            add_to_prev_states (bool): If True, the resulting style string is cached in the component's previous state.
    
        Returns:
            str: The computed CSS string.
        """
        prev_style, prev_style_string = self._prev_states.get("prev_style", ({}, ""))
        
        if prev_style == style:
            return prev_style_string
    
        css = "; ".join(f"{k}: {v}" for k, v in style.items())
        
        if style:
            css = css.join(['style="', '"'])
        else:
            css = ""
                
        if add_to_prev_states:
            self._prev_states["prev_style"] = (style, css)
    
        return css
        
    def get_props_string(self, props: Dict[str, str], add_to_prev_states: bool = False) -> str:
        """
        Returns an HTML property string from a dictionary of attributes.
    
        Args:
            props (Dict[str, str]): HTML attributes (e.g., {"id": "main", "class": "container"}).
            add_to_prev_states (bool): If True, the resulting style string is cached in the component's previous state.
            
        Returns:
            str: A string of HTML element properties.
        """
        prev_props, prev_props_string = self._prev_states.get("prev_props", ({}, ""))
            
        if prev_props == props:
            return prev_props_string
        
        props_string = " ".join(f'{k}="{v}"' for k, v in props.items())
        
        if not props:
            props_string = ""
            
        if add_to_prev_states:
            self._prev_states["prev_props"] = (props, props_string)
        
        return props_string
        
    def get_children_string(self, childs: "ChildrenList") -> str:
        """
        Renders and joins the HTML strings of child components.
    
        Args:
            childs (ChildrenList): The child components to render.
            
        Returns:
            str: The rendered HTML string of all children.
        """
        output = "".join(child.render() for child in childs)
        return output
        
    def get_partial_string(self):
        """
        Returns the partial string containing the style, props & inner body (if applicable).
        """
        # Don't look at children as they may be deeply nested and doing a tree traversal may be time consuming.
        
        if not self.has_local_updates() and self._prev_partial_string:
            return self._prev_partial_string
        
        props = self.props
        style = self.style
        inner_html = self.inner_html
        
        if self.accept_inner_html:
            strings = [f"<{self.element}>" if not props and not style else f"<{self.element}"]
        else:
            strings = [f"<{self.element}/>" if not props and not style else f"<{self.element}"]
        
        if props:
            if not style:
                if self.accept_inner_html:
                    strings.append(f"{self.get_props_string(props, True)}>")
                else:
                    strings.append(f"{self.get_props_string(props, True)}/>")
            else:
                strings.append(self.get_props_string(props, True))
                
        if style:
            if self.accept_inner_html:
                strings.append(f"{self.get_css_string(style, True)}>") 
            else:
                strings.append(f"{self.get_css_string(style, True)}/>")
                
        self._prev_partial_string = " ".join(strings)
            
        if self.accept_inner_html:
            self._prev_partial_string = self._prev_partial_string.join(["", self.inner_html])
            self._prev_states["prev_inner_html"] = (self.inner_html)
        
        return self._prev_partial_string 
        
    def has_local_updates(self):
        """
        Checks if the component itself has local updates excluding those of the children.
        
        Notes:
            This doesn't look for any changes to the children but only itself.
        """
        prev_props, _ = self._prev_states.get('prev_props', ({}, ""))
        prev_style, _ = self._prev_states.get('prev_style', ({}, ""))
        prev_inner_html = self._prev_states.get('prev_inner_html', (""))
        
        new_props = self.props
        new_style = self.style
        new_inner_html = self.inner_html
        
        if prev_props != new_props:
            return True
            
        elif prev_style != new_style:
            return True
            
        elif prev_inner_html != new_inner_html:
            return True
            
        else:
            return False
            
    def to_string(self):
        """
        Returns the string representation of the HTML component.
        
        Returns:
            str: The string representation of the HTML component.
        """
        from duck.html.components.core.system import LivelyComponentSystem
        
        self.__render_done = False
        self._on_render_start()
        
        if (LivelyComponentSystem.is_active() and
            self.add_to_registry and not self.disable_lively):
            
            if self.isroot():
                # Assign component UID's
                self.assign_component_uids(self)
                    
            # Make sure we use copies of the real component so that further changes will impose a difference
            try:
                _ = self.uid # Check if uid assigned yet.
            except ComponentError:
                # Property uid not assigned yet
                # This component might have been inserted after an event e.g. onclick.
                # Reassign component tree UID's to avoid messing up the structure thereby avoiding
                # unnecessary patches
                root = self.root
                if root:
                    self.assign_component_uids(root)
                
        # Do some staff
        output = [self.get_partial_string()]
        
        if self.accept_inner_html:
            output.append(f"{self.get_children_string(self.children)}</{self.element}>")
        else:
            if not output[0].endswith('>'):
                output.append("/>")
                
        output = "".join(output)
        self.__render_done = True
        
        # Finally return rendered output
        return output
    
    def _on_render_start(self):
        """
        Internal callback triggered at the beginning of component rendering.
        
        This is typically used internally by `pre_render` or the render system
        to indicate that rendering has started.
        """
        self._render_started = True
    
    def pre_render(
        self,
        pre_render_children: bool = True,
        deep_traversal: bool = False,
        reverse_traversal: bool = False,
    ) -> None:
        """
        Pre-renders this component and optionally its children to optimize future rendering.
    
        This method caches the output of `get_partial_string()` (which includes the
        component's props, styles, and inner HTML) to avoid redundant rendering work.
    
        Optionally, it can also pre-render child components, either shallowly or deeply,
        to reduce initial load time for complex component trees.
    
        Args:
            pre_render_children (bool): Whether to pre-render direct children.
            deep_traversal (bool): If True, recursively pre-renders all child components.
                Use with caution on large trees due to performance impact.
            reverse_traversal (bool): If True, children are pre-rendered from last to first.
                This can help with components like `Page` that benefit from reverse warming.
    
        Notes:
            Pre-rendering is most effective when scheduled in a background thread,
            typically after receiving a request:
    
            Example:
                ```py
                from duck.html.components.page import Page
                from duck.shortcuts import to_response
    
                def home(request):
                    page = Page(request=request)
                    background_thread.submit_task(
                        lambda: page.pre_render(deep_traversal=True, reverse_traversal=True)
                    )
                    return to_response(page)
                ```
        """
        if self.isroot():
            # Assign component UID's
            self.assign_component_uids(self)
        
        # Pre-render self (style, props, inner body)
        _ = self.get_partial_string()
    
        if self.accept_inner_html and pre_render_children:
            children = self.children.copy()
    
            if reverse_traversal:
                children = reversed(children)
    
            for child in children:
                if self._render_started and self.render_done:
                    # Rendering already started elsewhere; stop to avoid duplication.
                    break
    
                if deep_traversal:
                    child.pre_render(
                        pre_render_children=True,
                        deep_traversal=True,
                        reverse_traversal=reverse_traversal,
                    )
                else:
                    _ = child.get_partial_string()
    
        # Reset render state so as to detect if was render method started elsewhere. 
        # Usually, render is done at this point
        self._render_started = False
                    
    def render(self) -> str:
        """
        Render the component to produce html.
        """
        output = self.to_string()
        return output
        
    def force_set_component_attr(self, key: str, value: Any):
        """
        Forcefully sets an attribute on the component, bypassing attribute protection.
    
        Args:
            key (str): The attribute name to set.
            value (Any): The value to assign to the attribute.
    
        This method temporarily disables component attribute protection,
        allowing internal code to set or overwrite protected attributes.
        """
        component_attr_protection = getattr(self, "_component_attr_protection", False)
        try:
            self._component_attr_protection = False
            setattr(self, key, value)
        finally:
            self._component_attr_protection = component_attr_protection
    
    def __setattr__(self, key: str, value: Any):
        """
        Custom attribute setter that protects component references from being overwritten.
    
        Args:
            key (str): The attribute name.
            value (Any): The value to set.
    
        Raises:
            ComponentAttributeProtection: If protected component attribute is being modified.
        """
        component_attr_protection = getattr(self, "_component_attr_protection", False)
        component_attr_protection_targets = getattr(self, "_component_attr_protection_targets", {})
        component_attr_protection_exceptions = getattr(self, "_component_attr_protection_exceptions", [])
        
        if (
            component_attr_protection and
            key in component_attr_protection_targets and
            key not in component_attr_protection_exceptions
        ):
            old_value = component_attr_protection_targets.get(key, None)
            
            # Only protect if the old value exists and is a HtmlComponent,
            # and the new value is different (allows setting attribute first time).
            if old_value is not None and isinstance(old_value, HtmlComponent) and old_value is not value:
                raise ComponentAttributeProtection(
                    f"Modification of the protected component attribute '{key}' is not allowed. "
                    f"Existing value: {old_value!r}, attempted new value: {value!r}. "
                    "Please use `force_set_component_attr` to bypass this protection."
                )
        
        # Continue
        super().__setattr__(key, value)
        
        if (
            component_attr_protection and
            isinstance(value, HtmlComponent) and
            key not in self._component_attr_protection_targets and
            key not in component_attr_protection_exceptions
        ):
            self._component_attr_protection_targets[key] = value
        
    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return (
            f"<[{self.__class__.__name__} element='{self.element}' "
            f"children={len(self.children)}]>" if hasattr(self, "children") 
            else f"<[{self.__class__.__name__} element='{self.element}']>" 
        )
        

class NoInnerHtmlComponent(BasicExtension, StyleCompatibilityExtension, HtmlComponent):
    """
    This is the HTML component with no Inner Body.

    Example:
    
    ```html
    <input> <!--Input element does not accept inner html (inner body)-->
    <b/> <!--Same applies with the bold tag-->
    ```
   
    Notes:
    - The html components that fall in this category are usually HTML Input elements.
    """

    def __init__(
        self,
        element: Optional[str] = None,
        properties: Dict[str, str] = None,
        props: Dict[str, str] = None,
        style: Dict[str, str] = None,
        **kwargs,
    ):
        super().__init__(
            element,
            accept_inner_html=False,
            properties=properties,
            props=props,
            style=style,
            **kwargs,
        )


class InnerHtmlComponent(BasicExtension, StyleCompatibilityExtension, HtmlComponent):
    """
    This is the HTML component with Inner Body presence.

    Form:
    
    ```html
    <mytag>Text here</mytag>
    ```
    
    Example:
    
    ```html
    <p>Text here</p>
    <h2>Text here</h2>
    <ol>List elements here</ol>
    ```
    
    Notes:
    - The html components that fall in this category are usually basic HTML elements.
    """

    def __init__(
        self,
        element: Optional[str] = None,
        properties: Optional[Dict[str, str]] = None,
        props: Optional[Dict[str, str]] = None,
        style: Optional[Dict[str, str]] = None,
        inner_html: Optional[Union[str, LiveResult, Lazy]] = None,
        children: Optional[List["HtmlComponent"]] = None,
        **kwargs,
    ):
        from duck.html.components.core.children import ChildrenList
        
        # Initialize the children list
        self.children = ChildrenList(parent=self)
        
        super().__init__(
            element,
            accept_inner_html=True,
            inner_html=inner_html,
            properties=properties,
            props=props,
            style=style,
            **kwargs,
        )
        
        # Add children.
        self.children.extend(children or [])
        
    def add_child(self, child: HtmlComponent):
        """
        Adds a child component to this HTML component.

        Args:
            child (HtmlComponent): The child component to add.
        """
        self.children.append(child) 
        
    def add_children(self, children: List[HtmlComponent]):
        """
        Adds multiple child components to this HTML component.

        Args:
            children (list): The list of child components to add.
        """
        for child in children:
            self.add_child(child)
    
    def remove_child(self, child: HtmlComponent):
        """
        Removes a child component from this HTML component.

        Args:
            child (HtmlComponent): The child component to remove.
        """
        self.children.remove(child)
            
    def remove_children(self, children: List[HtmlComponent]):
        """
        Removes multiple child components to this HTML component.

        Args:
            children (list): The list of child components to remove.
        """
        for child in children:
            self.remove_child(child)
            
    def clear_children(self):
        """
        Clears all component's children.
        """
        self.children.clear()
        
    
class Theme:
    """
    Default Duck theme.
    """
    primary_color = "#4B4E75"  # Dark Blue
    secondary_color = "#A6B48B"  # Soft Green
    background_color = "#FFFFFF"  # White
    text_color = "#333333"  # Dark Grey for readability
    font_family = "Arial, sans-serif"
    border_radius = "15px"
    padding = "10px"
    button_style = {
        "background": primary_color,
        "text_color": "#FFFFFF",
        "border_radius": "5px",
        "padding": "10px 20px"
    }
    normal_font_size = "16px"


# Create some aliases
Component = HtmlComponent
InnerComponent = InnerHtmlComponent
NoInnerComponent = NoInnerHtmlComponent
ComponentError = HtmlComponentError
