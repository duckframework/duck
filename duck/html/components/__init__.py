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
import time
import copy
import asyncio
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
    Set,
    Iterable,
)

from duck.utils.string import smart_truncate
from duck.contrib.sync import convert_to_async_if_needed
from duck.html.components.extensions import (
    BasicExtension,
    StyleCompatibilityExtension,
)
from duck.html.components.core.props import PropertyStore, StyleStore
from duck.html.components.core.children import ChildrenList
from duck.html.components.core.vdom import VDomNode
from duck.html.components.core.warnings import DeeplyNestedEventBindingWarning
from duck.html.components.core.force_update import ForceUpdate as ForceUpdate # Avoids this being removed as unused on when formatters touch this.
from duck.html.components.core.mutation import (
    on_mutation,
    Mutation,
    MutationCode,
)
from duck.html.components.core.exceptions import (
    HtmlComponentError,
    AlreadyInRegistry,
    RedundantUpdate,
    UnknownEventError,
    InitializationError,
    EventAlreadyBound,
    ComponentAttributeProtection,
    ComponentCopyError,
    ComponentNotLoadedError,
    FrozenComponentError,
)


# Patten for matching an html tag/element.
ELEMENT_PATTERN = re.compile(r"\b[a-zA-Z0-9]+\b")


# TODO: Need to improve component load(). It's slow, especially for huge component trees like Page component tree


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
        inner_html: Optional[Union[str, int, float]] = None,
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
            inner_html (Union[str, int, float]): Inner html to add to the HTML component. Defaults to None.
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
        self.__uid = None
        self.__is_loading = False
        self.__loaded = False
        self.__inner_html = ""
        self.__is_frozen: bool = False
        
        # Other private attributes
        cls = self.__class__.__name__
        self._mutation_version = 0 # Global mutation version
        self._children_structure_mutation_version = 0 # Mutation version for the children structure/position
        self._render_started = False
        self._render_done = False
        self._is_from_cache = False
        self._is_a_copy = False
        self._copied_from = None
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
        
        # Container attrs are just attributes pointing to a container like a tuple, list, etc.
        # So that when copy is used, then this container attributes won't reference to the same 
        # container i.e. tuple/list/set .etc
        self._copy_container_attrs = [
            '_component_attr_protection_exceptions',
            '_component_attr_protection_targets',
            '_event_bindings',
            '_document_event_bindings',
            'fullpage_reload_headers',
            '_prev_states',
            'compatibility_keys',
            'kwargs',
        ] # __style, __properties, __children are already copied independantly, no need for them to be in here.
             
        # Add public attributes
        self.element = element
        self.accept_inner_html = accept_inner_html
        self.add_to_registry = kwargs.get('add_to_registry', True)
        self.kwargs = kwargs
        self.escape_on_text = kwargs.get('escape_on_text', True) # Whether to escape if modifying component text prop
        self.disable_lively = kwargs.get('disable_lively', False) # Whether to disable lively for this component
        
        # Update inner html if available
        if inner_html:
            self.inner_html = inner_html
            
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
        
        # Create some previous states e.g. {prev_props: (props_version, obj, "rendered_data")}
        # Format: version, value, rendered_string
        self._prev_states = {
          "prev_props": (None, {}, ""),
          "prev_style": (None, {}, ""),
          "prev_inner_html": (None, ""),
          "prev_rendered_output": (None, ""),
          "prev_vdom_node": (None, None),
          "prev_uid_assignment_mutation_version": (None, None), # version, uid
        } # Don't look at children as they may change any moment deep within the DOM tree.
        
        # Sets the previous rendered partial string, which may include style, props & inner body strings
        self._prev_partial_string = ""
        
        # Set mutation callbacks
        self.set_mutation_callbacks()
        
        # Load component or skip loading if Page component.
        lazy = kwargs.get("lazy", False)
        
        if not lazy: 
            self.load()
        else:
            from duck.html.components.page import Page
            
            if not isinstance(self, Page):
                raise ComponentError("Lazy loading is set to True on non-page component. Lazy option is only limited to Page components.")
            
    @property
    def properties(self):
        """
        Returns the properties store for the HTML component.

        Returns:
            PropertyStore: The properties store for the HTML component.
        """
        from duck.html.components.core.system import LivelyComponentSystem
        
        lively_data_props = {"data-uid", "data-events", "data-document-events", "data-validate"}
        
        if (LivelyComponentSystem.is_active()
            and not self.disable_lively
            and not self.get_raw_root().disable_lively
        ):
            # Update lively props
            current_lively_props = self.get_component_system_data_props()
            
            # Update lively props without trigger on_mutation handler
            # Useful if componenent is frozen, avoids FrozenComponentError.
            self.__properties.update(current_lively_props, call_on_set_item_handler=False)
            
            if self.is_frozen():
                return self.__properties
                
            # Remove data-* props if not present anymore.
            for prop in lively_data_props:
                if prop not in current_lively_props and prop in self.__properties.keys():
                    # Delete prop from __properties
                    del self.__properties[prop]
                    
        else:
            if not self.is_frozen():
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
                   or a random string.
            
        Notes:
        - This will be auto-assigned on render or when `to_vdom` is called. These methods 
               call `assign_component_uids` for assigning determinable UID's.
        - If a component is a root component, a unique ID will be generated whenever the `uid` property is accessed.
        """
        if self.isroot() and not self.__uid:
            self.__uid = f"{id(self)}" # Using id() is faster than secrets.token_urlsafe(8)
            
        if not self.__uid:
            raise ComponentError("Property `uid` is not assigned yet, `assign_component_uids` must be called first.")
        
        # Retuen the final UID
        return self.__uid
        
    @uid.setter
    def uid(self, uid: str):
        """
        Sets the component UID.
        """
        self.__uid = uid
        
    @property
    def inner_html(self) -> str:
        """
        Returns the inner body (innerHTML) for the component.
        """
        return self.__inner_html
    
    @inner_html.setter
    def inner_html(self, inner_html: Union[str, int, float]):
        """
        Set the component innerHTML.
        
        Args:
            inner_html (Union[str, int, float]): This can be a string, int or float. 
        """
        # NOTE: We supported LiveResult as input but it's causing problems when we are 
        # are caching component outputs, any modifications that can result in LiveResult to change can't
        # be detected so this may skip on_mutation handler being called leading to 
        # inconsistent results
        if not self.accept_inner_html:
            raise ComponentError("This component doesn't accept inner html, use InnerComponent instance instead.")
            
        if not isinstance(inner_html, (str, int, float)):
            raise ComponentError("The inner_html should be an instance of string, integer or a float.")
        
        # Convert data to right format
        inner_html = str(inner_html) if not isinstance(inner_html, str) else inner_html
        
        if self.__inner_html != inner_html:
            self.__inner_html = inner_html
            on_mutation(self, Mutation(target=self, code=MutationCode.SET_INNER_HTML, payload={"inner_html": inner_html}))
                
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
    def assign_component_uids(root_component: "Component", base_uid: str = "0", force: bool = False) -> None:
        """
        Assigns deterministic UIDs to the entire component tree using a non-recursive traversal.
    
        Args:
            root_component (HtmlComponent): The root component to start from.
            base_uid (str): The base UID for the root (default is "0").
            force (bool): Whether to force assign component uid's. By default, if no children structure mutation has happened, 
                no uid assignment is done. This argument overrides this behavior. Defaults to False. 
        """
        from duck.logging import logger
        from duck.html.components.core.system import LivelyComponentSystem
        
        if not root_component.isroot():
            raise ComponentError("Root component is required for `uid` assignment, not a child component.")
            
        prev_uid_assignment_mutation_version, prev_uid = root_component._prev_states["prev_uid_assignment_mutation_version"]
        
        if (
            not force
            and prev_uid_assignment_mutation_version is root_component._children_structure_mutation_version
            and prev_uid == root_component.uid
        ):
            # Do nothing because the children structure didn't change, no new child/no delete child
            return
            
        # Continue
        queue = deque()
        queue.append((root_component, root_component.uid))
        
        # The max nesting level for component with event bindings
        max_nesting_level = 9
        
        while queue:
            component, uid = queue.popleft()
            
            # Assign component UID
            if component._HtmlComponent__uid != uid:
                component.uid = uid
                
            # Call on_root_finalized event.
            if not component.isroot() and not component._on_root_finalized_called:
                component.on_root_finalized(component.root)
                component._on_root_finalized_called = True
                
            # Check for deep nesting for components with event bindings
            if component._event_bindings and not component._deeply_nested_event_binding_warned:
                 level = uid.count(".")
                 if level > max_nesting_level:
                     logger.warn(
                         f"The component {component} is deeply nested at level {level} "
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
                
        # Record the uid assignment action
        root_component._prev_states["prev_uid_assignment_mutation_version"] = (root_component._children_structure_mutation_version, root_component.uid)
    
    def is_loaded(self) -> bool:
        """
        Returns a boolean on whether if the component is loaded.
        """
        return self.__loaded
        
    def is_loading(self) -> bool:
        """
        Returns a boolean on whether if the component is loading or not.
        """
        return self.__is_loading
        
    def is_frozen(self) -> bool:
        """
        Returns boolean on whether if the component is frozen or not.
        """
        if self.parent:
            return (
                self.__is_frozen
                or self.parent.is_frozen()
                or self.root.is_frozen()
            )
        else:
            return self.__is_frozen
            
    def is_a_copy(self) -> bool:
        """
        Returns a boolean on whether this component is a copy from another component.
        """
        return self._is_a_copy
        
    def is_from_cache(self) -> bool:
        """
        Returns a boolean on whether this component has been retrieved from cache.
        """
        return self._is_from_cache
        
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
        raise NotImplementedError(f"Fallback method `get_element` is not implemented yet the 'element' argument is empty or None.")
    
    def set_mutation_callbacks(self):
        """
        This sets the callbacks that will be executed on prop/style mutation.
        """
        # Props mutation
        self.props._on_set_item_func = lambda key, value: \
            on_mutation(self, Mutation(target=self, code=MutationCode.SET_PROP, payload={"key": key, "value": value}))
        
        self.props._on_delete_item_func = lambda key: \
            on_mutation(self, Mutation(target=self, code=MutationCode.DELETE_PROP, payload={"key": key}))
        
        # Style mutation
        self.style._on_set_item_func = lambda key, value: \
            on_mutation(self, Mutation(target=self, code=MutationCode.SET_STYLE, payload={"key": key, "value": value}))
            
        self.style._on_delete_item_func = lambda key: \
            on_mutation(self, Mutation(target=self, code=MutationCode.DELETE_STYLE, payload={"key": key}))
        
    def on_mutation(self, mutation: Mutation):
        """
        This is called on component mutation. Either from props, style or children.
        
        Notes:
        - This is only called if the component itself is a root component
        """
        pass
        
    def _on_mutation(self, mutation: Mutation):
        """
        Private entry method to `on_mutation` event.
        """
        if self.is_frozen():
            raise FrozenComponentError(f"Mutation not allowed on frozen component: \n{mutation}")
            
        # TODO: Use better fine-grained mutation versions instead of this global one
        # For example children_mutation_version, props_mutation_version & style_mutation_version
        self._mutation_version += 1
        
        if mutation.code in {MutationCode.INSERT_CHILD, MutationCode.DELETE_CHILD}:
            if mutation.payload["parent"] is self:
                self._children_structure_mutation_version += 1
        
        # Call the customizable mutation handler
        self.on_mutation(mutation)
        
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
    
    def traverse(
        self,
        func: callable,
        algorithm: str = "depth_first_search",
        reverse: bool = False,
        include_self: bool = True,
    ) -> None:
        """
        Traverses the component tree and executes a callable on each node.
    
        Args:
            func (callable): Function to execute on each component (takes the component as argument).
            algorithm (str): 'depth_first_search' or 'breadth_first_search'.
            reverse (bool): If True, DFS visits children from last to first.
            include_self (bool): If True, traversal starts at self; otherwise, starts at children.
    
        Notes:
            - Iterative traversal is used to avoid recursion limits.
            - BFS ignores reverse.
            - func can read or modify nodes.
        """
        if algorithm not in ("depth_first_search", "breadth_first_search"):
            raise ValueError("Traversal algorithm must be 'depth_first_search' or 'breadth_first_search'")
    
        # Prepare initial nodes based on include_self
        initial_nodes = [self] if include_self else ((self.children) if self.accept_inner_html else [])
    
        if algorithm == "depth_first_search":
            stack = initial_nodes
            
            # Continue with dfs
            while stack:
                node = stack.pop()
                func(node)
    
                if node.accept_inner_html and node.children:
                    children = reversed(node.children) if reverse else node.children
                    stack.extend(children)
    
        else:  # breadth_first_search
            from collections import deque
            
            # Continue with bfs
            queue = deque(initial_nodes)
            
            while queue:
                node = queue.popleft()
                func(node)
    
                if node.accept_inner_html and node.children:
                    queue.extend(node.children)

    def traverse_ancestors(self, func: callable, include_self: bool = True) -> None:
        """
        Traverses upward from this component to the root, executing a callable on each ancestor.
    
        Args:
            func (callable): A function that takes a single argument (the component) and executes logic.
            include_self (bool): If True, starts at the current component; 
                                 if False, starts at the parent.
        
        Notes:
        - Stops when the root component (no parent) is reached.
        - Useful for propagating mutations, marking caches dirty, or other upward operations.
        """
        node = self if include_self else getattr(self, "parent", None)
        
        while node is not None:
            func(node)
            node = getattr(node, "parent", None)

    def load(self):
        """
        Load the component, pack all descendants (if available).
        
        Raises:
            ComponentError: If this method is used on non-root component or if component `is_loading()` is True.
        """
        if self.__is_loading and not self.__loaded:
            raise ComponentError("The component is already being loaded somewhere. Component `is_loading()` is True.")
            
        if not self.isroot():
            raise ComponentError("This method is only applicable to root components.")
        
        if not self.__loaded:
            # Finally, call the component entry method.
            try:
                self.__is_loading = True
                self.on_create() # If super().on_create() is called then _on_create_check_passed will be True.
                self.__loaded = True # Set component loaded flag immediately
                
                if not self._on_create_check_passed:
                    raise InitializationError(
                        f"Method `on_create` of component {repr(self)} was overridden somehow but `super().on_create()` was not called. "
                        "This may result in some component extensions not being properly applied or inconsistences within the component."
                      )
                
                # Maybe `ensure_freeze` was called using the FrozenComponent extension.
                # If so, it was called to make component frozen right after load, so lets do just that.
                ensure_freeze_callback = getattr(self, "_ensure_freeze_callback", None)
                
                if ensure_freeze_callback is not None and not self.is_frozen():
                    ensure_freeze_callback()
                
            except Exception as e:
                raise e # Reraise exception
            
            finally:
                self.__is_loading = False
                
        else:
            # Already loaded.
            # Maybe `ensure_freeze` was called using the FrozenComponent extension.
            # If so, it was called to make component frozen right after load, so lets do just that.
            ensure_freeze_callback = getattr(self, "_ensure_freeze_callback", None)
            if ensure_freeze_callback is not None and not self.is_frozen():
                ensure_freeze_callback()
                
    async def async_load(self):
        """
        Load the component asynchronously.
        """
        await convert_to_async_if_needed(self.load)()
        
    def wait_for_load(self, interval: float = 0.01):
        """
        This waits for the component to complete loading (if component is already being loaded somewhere).
        """
        if not self.is_loading():
            raise ComponentError("Component is not being loaded anywhere, use the 'load()' method.")
        
        while not self.is_loaded():
           time.sleep(interval)
       
    async def async_wait_for_load(self, interval: float = 0.01):
        """
        This asynchronously waits for the component to complete loading (if component is already being loaded somewhere).
        """
        if not self.is_loading():
            raise ComponentError("Component is not being loaded anywhere, use the 'load()' method.")
            
        while not self.is_loaded():
            await asyncio.sleep(interval)
           
    def raise_if_not_loaded(self, message: str):
        """
        Decorator which raises an exception if component is not loaded.
        
        Args:
            message (str): A custom error message for the exception.
        
        Raises:
            ComponentNotLoadedError: Raised if component is not loaded.
        """
        if not self.__loaded:
            raise ComponentNotLoadedError(message)
            
    def copied_from(self) -> Optional["HtmlComponent"]:
        """
        Returns the original component that this component was copied from (if applicable else None).
        """
        return self._copied_from
        
    def copy(self, shallow: bool = False) -> "HtmlComponent":
        """
        Returns a copy of the component.
    
        Notes:
        - Props, style, children are copied.
        - Iterative copy avoids recursion depth issues.
        - Shallow copy allowed only on frozen components.
        """
        try:
            return self._copy(shallow=shallow)
        
        except ComponentCopyError as e:
            raise e # Reraise exception
            
        except Exception as e:
            raise ComponentCopyError(f"Error copying component: {e}") from e
            
    def _copy(self, shallow: bool = False) -> "HtmlComponent":
        """
        Returns a copy of the component.
    
        Notes:
        - Props, style, children are copied.
        - Iterative copy avoids recursion depth issues.
        - Shallow copy allowed only on frozen components.
        """
        def _copy(component):
             cls = component.__class__
             new_component = object.__new__(cls)
             new_component.__dict__ = component.__dict__.copy()
             
             # Copy props/style
             new_props = PropertyStore(new_component.props)
             new_style = StyleStore(new_component.style)
             
             object.__setattr__(new_props, "_PropertyStore__version", component.style._version)
             object.__setattr__(new_style, "_PropertyStore__version", component.props._version)
             
             object.__setattr__(
                 new_component,
                 "_HtmlComponent__properties",
                 new_props,
             )
             
             # Copy style
             object.__setattr__(
                 new_component,
                 "_HtmlComponent__style",
                 new_style,
             )
             
             # Set other important attributes
             object.__setattr__(new_component, "_is_a_copy", True)
             object.__setattr__(new_component, "_copied_from", component)
             
             for i in component._copy_container_attrs:
                 try:
                     value = getattr(new_component, i)
                 except AttributeError:
                     continue
                     
                 except Exception as e:
                     raise ComponentCopyError(f"Error resolving copy container attribute '{i}': {e}")
                     
                 if isinstance(value, Iterable):
                     object.__setattr__(new_component, i, copy.copy(value))
             
             # Return the new component
             if hasattr(new_component, "apply_extension"):
                 new_component.apply_extension()
             return new_component
        
        # Perform some checks     
        if shallow:   
            def check_frozen(c):
                if not c.is_frozen():
                    raise ComponentCopyError(
                        "Shallow copy only allowed on frozen components."
                    )
                    
            # Check if component is frozen
            check_frozen(self)
            
        if self.is_a_copy():
            raise ComponentCopyError("Component is already a copy, can only copy original components.")
        
        # Stack for iterative copy: (original_node, copied_node)
        stack = []
    
        # Copy root component
        root_copy = _copy(self)
        
        if self.isroot():
            # This is very important!!!
            # Not updating the root to a copied one will cause issues like incorrect root leading 
            # to issues like very slow render (because assign_component_uids keep being called many times because root_component.isroot() = False)
            object.__setattr__(root_copy, "_HtmlComponent__root", root_copy) # Assign raw root
            object.__setattr__(root_copy, "_HtmlComponent__parent", None) # Reset parent just in case it was mistakenly set.
            
            if not root_copy.is_frozen():
                # Do not reset UID on frozen component as to prevent UID regeneration if uid is not set.
                object.__setattr__(root_copy, "_HtmlComponent__uid", None) # Reset UID to represent new component
            
        if shallow:
            return root_copy
    
        # Initialize stack with root
        stack.append((self, root_copy))
    
        # Iterative traversal
        while stack:
            original, copied = stack.pop()
            
            # Update copied root
            object.__setattr__(copied, "_HtmlComponent__root", root_copy.get_raw_root()) # Assign root
            
            # Continue
            if not hasattr(original, "children"):
                continue
    
            # Create a list for children
            new_children = []
    
            for child in original.children:
                # Copy child node
                child_copy = _copy(child)
                object.__setattr__(child_copy, "_HtmlComponent__root", root_copy.get_raw_root()) # Assign root
                object.__setattr__(child_copy, "_HtmlComponent__parent", copied) # Assign parent
                
                # Prepare children list for child
                if hasattr(child, "children") and child.children:
                    # Push child to stack to process its children later
                    stack.append((child, child_copy))
    
                # Add new child to list.
                new_children.append(child_copy)
                
                # Re-set mutation callbacks
                child_copy.set_mutation_callbacks()
                
            # Assign copied children list to copied parent
            new_children = ChildrenList(parent=copied, initlist=new_children, skip_initlist_events=True)
            
            # Finally assign copied children
            object.__setattr__(copied, "_InnerHtmlComponent__children", new_children)
        
        # Finally return root copied component
        # Re-set mutation callbacks
        root_copy.set_mutation_callbacks()
        return root_copy
    
    def freeze(self):
        """
        Freeze the component.
        """
        self.raise_if_not_loaded("Cannot freeze component which is not loaded yet, use `ensure_freeze()` instead.")
        self.__is_frozen = True
        
    def ensure_freeze(self, *args, **kwargs):
        """
        This works just like `freeze()` but does not raise an exception if component is not yet loaded.  
        
        It ensures that `freeze` is called whenever the component is loaded (if not already loaded) or 
        just freeze the component right away if component is already loaded.
        """
        # TODO: This must be implemented in the future.
        if self.is_frozen():
            return
        
        def ensure_freeze():
            """
            This just freezes the component and provide a reference for debugging 
            when `load()` fails because of this function. 
            """
            self.freeze(*args, **kwargs)
            
        if self.is_loaded():
            self.freeze(*args, **kwargs)
        else:
            # Load is not called yet or already loading.
            self._ensure_freeze_callback = ensure_freeze
             
            if self.is_loaded() and not self.is_frozen():
                # Component already loaded, maybe component was loading already 
                # but it was about to finish that it didn't see the _ensure_freeze_callback attribute.
                self.freeze(*args, **kwargs)
        
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
            sync_targets,
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
               
    def get_event_info(self, event: str) -> Tuple[Callable, Set["HtmlComponent"]]:
        """
        Returns the event info in form: (event_handler, update_targets).
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
        
    def get_css_string(self, style: StyleStore[str, str], add_to_prev_states: bool = True) -> str:
        """
        Returns a CSS style string from a dictionary of style attributes.
    
        Args:
            style (StyleStore[str, str]): The style attributes (e.g., StyleStore({"color": "red", "font-size": "12px"}) ).
            add_to_prev_states (bool): If True, the resulting style string is cached in the component's previous state.
    
        Returns:
            str: The computed CSS string.
        """
        prev_style_version, prev_style, prev_style_string = self._prev_states.get("prev_style", (None, {}, ""))
        
        try:
            current_style_version = style._version
        except AttributeError:
            # Only do isinstance on attribute error to avoid checking excessively always
            if not isinstance(props, StyleStore):
                raise TypeError("The provided style is must be an instance of StyleStore not {type(props).__name__}.")
            raise # Reraise exception
             
        if prev_style_version == current_style_version:
            return prev_style_string
    
        css = ";".join(f"{k}:{v}" for k, v in style.items())
        
        if style:
            css = css.join(['style="', '"'])
        else:
            css = ""
                
        if add_to_prev_states:
            self._prev_states["prev_style"] = (style._version, style.copy(), css)
    
        return css
        
    def get_props_string(self, props: PropertyStore[str, str], add_to_prev_states: bool = True) -> str:
        """
        Returns an HTML property string from a dictionary of attributes.
    
        Args:
            props (PropertyStore[str, str]): HTML attributes (e.g., PropertyStore({"id": "main", "class": "container"}) ).
            add_to_prev_states (bool): If True, the resulting style string is cached in the component's previous state.
            
        Returns:
            str: A string of HTML element properties.
        """
        prev_props_version, prev_props, prev_props_string = self._prev_states.get("prev_props", (None, {}, ""))
        
        try:
            current_props_version = props._version
        except AttributeError:
            # Only do isinstance on attribute error to avoid checking excessively always
            if not isinstance(props, PropertyStore):
                raise TypeError("The provided props is must be an instance of PropertyStore not {type(props).__name__}.")
            raise # Reraise exception
                       
        if prev_props_version == current_props_version:
            return prev_props_string
        
        props_string = " ".join(f'{k}="{v}"' for k, v in props.items())
        
        if not props:
            props_string = ""
            
        if add_to_prev_states:
            self._prev_states["prev_props"] = (props._version, props.copy(), props_string)
        
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
        
        # Check if component is loaded
        self.raise_if_not_loaded(
            f"Component {self} is not yet loaded. "
            f"This may mean that the component is a lazy component."
        )
        
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
            self._prev_states["prev_inner_html"] = (self._mutation_version, self.inner_html)
        
        return self._prev_partial_string 
        
    def has_local_updates(self):
        """
        Checks if the component itself has local updates excluding those of the children.
        
        Notes:
            This doesn't look for any changes to the children but only itself.
        """
        prev_props_version, _, __ = self._prev_states.get('prev_props', (None, {}, ""))
        prev_style_version, _, __ = self._prev_states.get('prev_style', (None, {}, ""))
        prev_inner_html = self._prev_states.get('prev_inner_html', (""))
        
        new_props_version = self.props._version
        new_style_version = self.style._version
        new_inner_html = self.inner_html
        
        return (
            prev_props_version != new_props_version
            or prev_style_version != new_style_version
            or prev_inner_html != new_inner_html
        )
        
    def pre_render(self) -> None:
        """
        Pre-renders this component and optionally its children to optimize future rendering.
        """
        # Start pre-rending from the bottom components upto the top.
        # Root-only initialization
        if self.isroot():
            self.assign_component_uids(self)
    
        # Stack for explicit DFS traversal
        stack = reversed([*getattr(self, "children", [self])])
        
        for child in stack:
            if not child._render_done:
                if child._render_started:
                    child.pre_render()
                else:
                    child.render()
                
    def to_string(self):
        """
        Returns the string representation of the HTML component.
        
        Returns:
            str: The string representation of the HTML component.
        """
        from duck.html.components.core.system import LivelyComponentSystem
        
        # Check if component is loaded
        self.raise_if_not_loaded(
            f"Component {self} is not yet loaded. "
            f"This may mean that the component is a lazy component."
        )
        
        # The following line triggers a mutation if root UID has been altered
        if self.isroot():
            _ = self.props # updates the props with new uid if uid changed.
            
        # Check if there has been any kind of mutation.
        prev_output_version, prev_output = self._prev_states["prev_rendered_output"] 
        
        if prev_output_version == self._mutation_version and prev_output:
            return prev_output
        
        # Continue with render
        self._on_render_start()
        
        if (LivelyComponentSystem.is_active()
            and self.add_to_registry
            and not self.disable_lively
        ):
            
            if self.isroot():
                # Assign component UID's
                self.assign_component_uids(self)
                    
            try:
                _ = self.uid # Check if uid assigned yet.
            except ComponentError:
                # Property uid not assigned yet
                # This component might have been inserted after an event e.g. onclick.
                # Reassign component tree UID's to avoid messing up the structure thereby avoiding
                # unnecessary patches
                root = self.root
                
                if root:
                    # Use force assign component UID's to make sure self.uid is set nomatter what.
                    self.assign_component_uids(root, force=True)
                    
        # Do some staff
        output = [self.get_partial_string()]
        
        if self.accept_inner_html:
            output.append(f"{self.get_children_string(self.children)}</{self.element}>")
        else:
            if not output[0].endswith('>'):
                output.append("/>")
                
        output = "".join(output)
        self._on_render_done()
        
        # Finally return rendered output
        self._prev_states["prev_rendered_output"] = (self._mutation_version, output)
        return output
        
    def _on_render_start(self):
        """
        Internal callback triggered at the beginning of component rendering.
        """
        self._render_done = False
        self._render_started = True
        
    def _on_render_done(self):
        """
        Internal callback triggered at the end of component rendering.
        """
        self._render_done = True
        self._render_started = False
        
    def render(self) -> str:
        """
        Render the component to produce html.
        """
        output = self.to_string()
        return output
        
    async def async_render(self) -> str:
        """
        Asynchronously render component.
        """
        return await convert_to_async_if_needed(self.render)()
        
    def to_vdom(self) -> VDomNode:
        """
        Converts the HtmlComponent into a virtual DOM node.
    
        Returns:
            VDomNode: A virtual DOM representation of the HTML component.
        """
        prev_node_version, prev_node = self._prev_states["prev_vdom_node"]
        
        if (
            prev_node_version == self._mutation_version
            and prev_node 
            and prev_node.key == self.uid
        ):
           # Only return prev_node if uid==key, trying to patch prev_node.key is 
           # causing issues
           return prev_node
            
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
                # Use force assign component UID's to make sure self.uid is set nomatter what.
                self.assign_component_uids(root, force=True)
            
        node = VDomNode(
            tag="%s"%self.element,
            key=self.uid,
            props=self.props.copy(),
            style=self.style.copy(),
            text="%s"%self.inner_html if self.accept_inner_html else None,
            children=[child.to_vdom() for child in getattr(self, "children", [])],
            component=self,
        )
        
        # Record node and return it
        self._prev_states["prev_vdom_node"] = (self._mutation_version, node)
        return node
    
    async def async_to_vdom(self) -> VDomNode:
        """
        Asynchronously convert component to `VDOMNode`.
        """
        return await convert_to_async_if_needed(self.to_vdom)()
        
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
        
    def __copy__(self):
        return self.copy()
        
    def __repr__(self) -> str:
        truncated_inner_html = smart_truncate(str(self.inner_html), cap=8)
        
        # Get component UID
        # UID may be assigned by the following statements
        uid = self.__uid or (self.uid if self.isroot() else None)
        
        # Build component string repr
        first_part = f"<[{self.__class__.__name__}{' copy' if self.is_a_copy() else ''} uid='{uid}', element='{self.element}', inner_html='{truncated_inner_html}'"
        children = getattr(self, "children", None)
                
        if children is not None:
            return first_part + " children=%d]>"%(len(children)) 
        else:
            return first_part + "]>"
            
    __str__ = __repr__ # Assign __str__ as well


class NoInnerHtmlComponent(
    BasicExtension,
    StyleCompatibilityExtension,
    HtmlComponent,
):
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


class InnerHtmlComponent(
    BasicExtension,
    StyleCompatibilityExtension,
    HtmlComponent,
):
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
        inner_html: Optional[Union[str, str, float]] = None,
        children: Optional[List["HtmlComponent"]] = None,
        **kwargs,
    ):
        # Initialize the children list
        # Do not automatically call on_new_child events before super().__init__; this is causing errors somehow.
        self.__children = ChildrenList(parent=self, initlist=children or [], skip_initlist_events=True)
        
        # Super initialization
        super().__init__(
            element,
            accept_inner_html=True,
            inner_html=inner_html,
            properties=properties,
            props=props,
            style=style,
            **kwargs,
        )
        
        # Validate every init child manually
        for child in children or []:
            # Do not check if component is loaded, esp for lazy components like Pages
            self.__children.on_new_child(child, component_loaded_check=False) # Validate child
        
    @property
    def children(self) -> ChildrenList[HtmlComponent]:
        """
        Returns the component children.
        """
        return self.__children
         
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
