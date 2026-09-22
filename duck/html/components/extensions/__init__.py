"""
Extensions module for components.  

**Usage example:**

```py
from duck.html.components.button import Button
from duck.html.components.extensions import Extension

class MyExtension(Extension):
    def my_new_method(self):
        # This method will now be available on component `MyButton`
        # Do something
        pass

    def existing_method(self):
        super().existing_method()
        # When overriding an existing method, don't forget to call `super()`
        # Do something, e.g. access component keyword arguments through `self.kwargs`

    def apply_extension(self):
        super().apply_extension()
        # Modify something or do something
        self.style.update({"background-color", "red"})

class MyButton(MyExtension, Button):
    pass

btn = MyButton()
btn.style["background-color"] == "red"  # Outputs: True
```
"""
# NOTE: In the future we need to use a max of 2 extensions just to avoid Method Resolution Order (MRO) overhead.
from typing import (
    Optional,
    Any,
    Union,
    Tuple,
    Dict,
    Type,
    Iterable,
    FrozenSet,
)


# Rules for default extensions: (component class, extension) -> rejected classes
DEFAULT_EXTENSIONS: Dict[Tuple[Type, Type], Tuple[Type, ...]] = {}

# Cache of component classes with their default extensions mixed in
RESOLVED_CLASSES: Dict[Tuple[Type, FrozenSet[Type]], Type] = {}


def register_default_extension(
    component_class: type,
    extension: type["Extension"],
    reject: Iterable[Type] = (),
) -> None:
    """
    Attach an extension to every instance of a component class and its subclasses.

    Registering the same component class and extension again replaces the
    previous `reject` classes, so calling this more than once is safe.

    Args:
        component_class (Type): Component class whose instances get the extension.
        extension (Type[Extension]): Extension mixed in ahead of the component.
        reject (Iterable[Type]): Component classes that must not get the extension.
            Subclasses of these classes are rejected as well.

    Raises:
        ExtensionError: If `reject` contains anything other than classes.
    
    Notes:
        You can only reject other extensions apart from `BasicExtension` and `StyleCompatibiliyExtension` because they 
        provide base component operations.
    """
    # Validate the reject classes before storing them
    reject = tuple(reject)
    
    if not all(isinstance(rejected, type) for rejected in reject):
        raise ExtensionError("`reject` must only contain component classes.")

    # Record the rule, replacing any earlier one for the same pair
    DEFAULT_EXTENSIONS[(component_class, extension)] = reject

    # Drop cached classes so the new rule takes effect
    RESOLVED_CLASSES.clear()


def unregister_default_extension(
    component_class: type,
    extension: type["Extension"],
    failsafe: bool = False,
) -> None:
    """
    Remove a previously registered default extension rule.

    Args:
        component_class (Type): Component class the rule was registered under.
        extension (Type[Extension]): Extension to stop attaching by default.
        failsafe (bool): If True, do nothing when the rule was never
            registered, instead of raising.

    Raises:
        ExtensionError: If the rule was never registered and `failsafe` is False.
    
    Notes:
        You can only unregister other extensions apart from `BasicExtension` and `StyleCompatibiliyExtension` because they 
        provide base component operations.
    """
    key = (component_class, extension)

    # Bail out early if there's nothing to remove
    if key not in DEFAULT_EXTENSIONS:
        if failsafe:
            return
        raise ExtensionError(
            f"No default extension rule registered for {component_class.__name__} "
            f"with {extension.__name__}."
        )

    # Remove the rule
    del DEFAULT_EXTENSIONS[key]

    # Drop cached classes so the removal takes effect
    RESOLVED_CLASSES.clear()


def resolve_component_class(
    cls: type,
    exclude_extensions: Iterable[type["Extension"]] = (),
) -> type:
    """
    Resolve a component class with its applicable default extensions mixed in.

    The derived class is built once per (component class, excluded extensions)
    pair and cached, so repeated instantiations only cost a dictionary lookup.

    Args:
        cls (Type): Component class being instantiated.
        exclude_extensions (Iterable[Type[Extension]]): Default extensions to
            skip for this instance only, even if otherwise applicable.

    Returns:
        Type: `cls` itself when no extension applies, otherwise a generated
            subclass with the extensions ahead of `cls` in the MRO.
    
    Notes:
        Only other extensions apart from `BasicExtension` and `StyleCompatibiliyExtension` can be excluded 
        because these provide base component operations.
    """
    # Build the lookup key for this (class, exclusions) pair
    exclude_extensions = frozenset(exclude_extensions)
    cache_key = (cls, exclude_extensions)

    # Build the class only once per cache key
    if cache_key not in RESOLVED_CLASSES:
        extensions = tuple(
            extension
            for (base, extension), reject in DEFAULT_EXTENSIONS.items()
            if issubclass(cls, base)
            and not issubclass(cls, reject)
            and not issubclass(cls, extension)
            and extension not in exclude_extensions
        )

        # Mix the extensions in ahead of the component, or keep it unchanged
        RESOLVED_CLASSES[cache_key] = (
            type(cls.__name__, (*extensions, cls), {"__module__": cls.__module__})
            if extensions
            else cls
        )

    # Return the cached class
    return RESOLVED_CLASSES[cache_key]


class ExtensionError(Exception):
    """
    Raised when there is an error related to a component extension.
    """


class KwargError(ExtensionError):
    """
    Raised when there is no required keyword argument in component `kwargs`.
    """


class RequestNotFoundError(ExtensionError):
    """
    Raised when there is no required 'request' in component `kwargs` or `kwargs['context']` (if component used in a template).
    """


class Extension:
    """
    Base class for all component extensions.

    Extensions allow reusable behaviors to be added to components via mixins.
    Override methods like `apply_extension` or define new ones for extended logic.
    """
    def load(self):
        self.apply_extension() # This applies all extensions according to MRO
        super().load()
       
        if not getattr(self, "_base_extension_applied", False):
            raise ExtensionError("Seems like extension method `apply_extension` has been overridden but 'super().apply_extension()' has not been called.")
        
    def apply_extension(self):
        """
        Overrride this method to apply the desired extensions.
        
        Notes:
        - Don't forget to call `super().apply_extensions()` inside the method.
        - Methods or property definations are applied to the component automatically.
        """
        self._base_extension_applied = True


class BasicExtension(Extension):
    """
    Basic extension for HTML components, providing common properties like `text`, `id`, `bg_color`, and `color`.
    """

    def apply_extension(self):
        """
        Apply the extension. Applies initial values from `kwargs`
        for basic properties such as `id`, `klass`, `text`, `bg_color`, and `color`.
        """
        super().apply_extension()
        
        # Apply the current extension
        keys = {"id", "klass", "text", "bg_color", "color"}
        
        for key in keys:
            value = self.kwargs.get(key)
            if value is not None:
                setattr(self, key, value)
                
    @property
    def id(self) -> Optional[str]:
        """
        Returns the ID of the component.

        Returns:
            Optional[str]: The ID if set, otherwise None.
        """
        return self.props.get("id")

    @id.setter
    def id(self, id_: str):
        """
        Sets the ID of the component.

        Args:
            id_ (str): The ID to assign to the component.
        """
        from duck.html.components.page import Page
        
        if isinstance(self, Page) and not self.disable_lively and id_ != "page-root":
            raise ExtensionError(
                "The Page component ID is reserved and cannot be changed from 'page-root'. "
                "Lively relies on this ID to locate and manage the root of the component tree — "
                "changing it will break real-time updates and WebSocket communication.\n\n"
                "If you need to identify or target the page element, use a child container instead."
            )
            
        self.props["id"] = id_

    @property
    def klass(self) -> Optional[str]:
        """
        Returns the `class` of the component.

        Returns:
            Optional[str]: The class' if set, otherwise None.
        """
        return self.props.get("class")

    @klass.setter
    def klass(self, class_: str):
        """
        Sets the `class` of the component.

        Args:
            class_ (str): The `class` to assign to the component.
        """
        self.props["class"] = class_

    @property
    def text(self) -> str:
        """
        Returns the inner html of the component.

        Notes:
            This escapes HTML if found in text. You can disable this by setting `escape_on_text=False` on component.
            
        Returns:
            str: The inner content of the component.

        Raises:
            ExtensionError: If the component does not support `inner_html`.
        """
        from duck.html.components import InnerComponent

        if not isinstance(self, InnerComponent):
            raise ExtensionError(f"Property `text` can only be used on inner components with `inner_html`, not {type(self)}")

        return self.inner_html

    @text.setter
    def text(self, text: Union[str, int, float]):
        """
        Sets the text of the component.

        Args:
            text (Union[str, int, float]): The new inner content.
        
        Notes:
            This escapes HTML if found in text. You can disable this by setting `self.escape_on_text=False` on component.
           
        Raises:
            ExtensionError: If the component does not support `inner_html` or if input is not a string, LiveResult or Lazy object.
        """
        from duck.html import escape
        from duck.html.components import InnerComponent
        
        if not isinstance(self, InnerComponent):
            raise ExtensionError(
                f"Property `text` can only be used on inner components with "
                f"`inner_html`, not {type(self)}"
            )
        
        if not isinstance(text, (str, int, float)):
            raise ExtensionError(
                f"Text must be a valid string, integer or float, not {type(text)}"
            )
        
        # Convert to text
        text = str(text)
        
        if self.escape_on_text:
            text = escape(text)
            
        # Tags to ignore for replacing linebreak with <br>
        linebreak_replace_ignore_tags = {"pre", "code", "style", "script", "textarea"}
        
        if self.element not in linebreak_replace_ignore_tags:
            # Convert newlines last so the inserted `<br>` tags are never escaped
            text = text.replace("\n", "<br>")
            
        # Set text
        self.inner_html = text

    @property
    def bg_color(self) -> Optional[str]:
        """
        Returns the background color of the component.

        Returns:
            Optional[str]: The background color if set, otherwise None.
        """
        return self.style.get("background-color")

    @bg_color.setter
    def bg_color(self, color: str):
        """
        Sets the background color of the component.

        Args:
            color (str): A valid CSS color string.
        """
        self.style["background-color"] = color

    @property
    def color(self) -> Optional[str]:
        """
        Returns the foreground (text) color of the component.

        Returns:
            Optional[str]: The text color if set, otherwise None.
        """
        return self.style.get("color")

    @color.setter
    def color(self, color: str):
        """
        Sets the foreground (text) color of the component.

        Args:
            color (str): A valid CSS color string.
        """
        self.style["color"] = color

    def get_kwarg_or_raise(self, kwarg: str) -> Any:
        """
        Retrieves an argument from component `kwargs` or raise an exception.
        
        Raises:
            KwargError:  If a keyword argument is not provided to the component.
        """
        if kwarg not in self.kwargs:
            raise KwargError(f"Keyword argument `{kwarg}` is required, could not be found in `self.kwargs`.")
        return self.kwargs.get(kwarg)
        
    def get_request_or_raise(self) -> "HttpRequest":
        """
        Retrieves a request object from component `kwargs` or raise an exception.
        
        Raises:
            RequestNotFoundError:  If the request is not in kwargs or kwargs['context'] (if used in templates).
        """
        from duck.http.request import HttpRequest
        
        request: HttpRequest = getattr(self, "request", None) or self.kwargs.get('request')
        
        if not request:
            # Μaybe this component is used in a template.
            context = self.kwargs.get("context", {})
            request = context.get("request")
        
        if not request:
            raise RequestNotFoundError("Request not found in `kwargs` or kwargs['context'] (if component used in a template).")
            
        # Finally, return request.
        return request


class StyleCompatibilityExtension(Extension):
    """
    Extension for improving CSS style compatibility between browsers.
    Automatically adds and (optionally) deletes vendor-prefixed versions
    of certain CSS properties when setting or deleting styles.
    """
    def __init__(self, *args, **kw) -> None:
        # Controls whether prefixed properties are deleted along with the main key
        self.delete_compatibility_keys_on_delete = True

        # Mapping of base CSS properties to their vendor-prefixed equivalents
        self.compatibility_keys = {
            # Layout and visual effects
            "backdrop-filter": [
                "-webkit-backdrop-filter",
                "-ms-backdrop-filter",
            ],
            "box-shadow": [
                "-webkit-box-shadow",
                "-moz-box-shadow",
            ],
            "box-sizing": [
                "-webkit-box-sizing",
                "-moz-box-sizing",
            ],
            "appearance": [
                "-webkit-appearance",
                "-moz-appearance",
            ],
            "filter": [
                "-webkit-filter",
            ],
            "opacity": [
                "-webkit-opacity",
                "-moz-opacity",
            ],

            # Transformations and animations
            "transform": [
                "-webkit-transform",
                "-moz-transform",
                "-ms-transform",
                "-o-transform",
            ],
            "transform-origin": [
                "-webkit-transform-origin",
                "-moz-transform-origin",
                "-ms-transform-origin",
                "-o-transform-origin",
            ],
            "transition": [
                "-webkit-transition",
                "-moz-transition",
                "-o-transition",
            ],
            "animation": [
                "-webkit-animation",
                "-moz-animation",
                "-o-animation",
            ],
            "animation-delay": [
                "-webkit-animation-delay",
                "-moz-animation-delay",
                "-o-animation-delay",
            ],
            "animation-duration": [
                "-webkit-animation-duration",
                "-moz-animation-duration",
                "-o-animation-duration",
            ],

            # User interaction
            "user-select": [
                "-webkit-user-select",
                "-moz-user-select",
                "-ms-user-select",
            ],
            "touch-action": [
                "-ms-touch-action",
            ],
            "cursor": [
                "-webkit-cursor",
            ],

            # Gradients and backgrounds
            "background-clip": [
                "-webkit-background-clip",
                "-moz-background-clip",
            ],
            "background-origin": [
                "-webkit-background-origin",
                "-moz-background-origin",
            ],
            "background-size": [
                "-webkit-background-size",
                "-moz-background-size",
                "-o-background-size",
            ],

            # Flexbox
            "display": [
                "-webkit-box",       # old flexbox syntax
                "-moz-box",
                "-ms-flexbox",
                "-webkit-flex",
            ],
            "align-items": [
                "-webkit-align-items",
                "-ms-flex-align",
            ],
            "justify-content": [
                "-webkit-justify-content",
                "-ms-flex-pack",
            ],
            "flex": [
                "-webkit-flex",
                "-ms-flex",
            ],
            "flex-direction": [
                "-webkit-flex-direction",
                "-ms-flex-direction",
            ],

            # Sticky and clipping
            "clip-path": [
                "-webkit-clip-path",
            ],
            "position": [
                "-webkit-sticky",  # sticky support
            ],
        }

        # Super init
        super().__init__(*args, **kw)
        
    def apply_extension(self):
        super().apply_extension()
        
        def on_style_setitem(key, val):
            """
            Called on setting of style key to apply compatibility keys.
            """
            # Add vendor-prefixed versions if applicable
            for compat_key in self.compatibility_keys.get(key, []):
                self.style.__setitem__(compat_key, val, call_on_set_item_handler=False)
            super_on_set_item(key, val)
            
        def on_style_delitem(key):
            """
            Called on deletion of a style key.
            """
            # Optionally delete vendor-prefixed versions
            if self.delete_compatibility_keys_on_delete:
                for compat_key in self.compatibility_keys.get(key, []):
                    if compat_key in self.style:
                        self.style.__delitem__(compat_key, call_on_delete_item_handler=False)
            super_on_delete_item(key)
                        
        # Replace the style’s magic methods with our enhanced versions
        super_on_set_item = self.style._on_set_item
        super_on_delete_item = self.style._on_delete_item
        
        self.style._on_set_item = on_style_setitem
        self.style._on_delete_item = on_style_delitem
