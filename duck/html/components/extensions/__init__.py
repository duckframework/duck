"""
Extensions module for components.

Usage example:

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

    def on_create(self):
        super().on_create()
        # Modify something or do something
        self.style["background-color"] = "red"

class MyButton(MyExtension, Button):
    pass

btn = MyButton()
btn.style["background-color"] == "red"  # Outputs: True
```
"""
from typing import Optional, Any, Union

from duck.utils.lazy import Lazy, LiveResult


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
    Override methods like `on_create` or define new ones for extended logic.
    """
    pass


class BasicExtension(Extension):
    """
    Basic extension for HTML components, providing common properties like `text`, `id`, `bg_color`, and `color`.
    """

    def on_create(self):
        """
        Called when the component is created. Applies initial values from `kwargs`
        for basic properties such as `id`, `klass`, `text`, `bg_color`, and `color`.
        """
        super().on_create()
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
    def text(self, text: Union[str, LiveResult, Lazy]):
        """
        Sets the inner body of the component.

        Args:
            text (Union[str, LiveResult, Lazy]): The new inner content.
        
        Notes:
            This escapes HTML if found in text. You can disable this by setting `escape_on_text=False` on component.
           
        Raises:
            ExtensionError: If the component does not support `inner_html` or if input is not a string, LiveResult or Lazy object.
        """
        from duck.html import escape
        from duck.html.components import InnerComponent

        if not isinstance(self, InnerComponent):
            raise ExtensionError(f"Property `text` can only be used on inner components with `inner_html`, not {type(self)}")

        if not isinstance(text, (str, Lazy)):
            raise ExtensionError(f"Text must be a valid string, LiveResult or Lazy object, not {type(text)}")
        
        if not self.escape_on_text:
            self.inner_html = text
            return
            
        def escape_lazy_obj(lazy_obj):
            """
            Escape HTML on a LiveResult or Lazy object.
            """
            getresult = lazy_obj.extra_data["real_getresult"]
            result = getresult()
            if isinstance(result, str):
                result = escape(result)
            return result
            
        if isinstance(text, Lazy):
            if not text.extra_data.get("escape_on_text"):
                text.extra_data['real_getresult'] = text.getresult
                text.getresult = lambda: escape_lazy_obj(text)
                text.extra_data["escape_on_text"] = True
        else:
            text = escape(text)
            
        # Set escaped text.
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
        
    def on_create(self):
        super().on_create()

        def on_style_setitem(key, val):
            """
            Called on setting of style key to apply compatibility keys.
            """
            # Add vendor-prefixed versions if applicable
            for compat_key in self.compatibility_keys.get(key, []):
                self.style.__setitem__(compat_key, val, call_on_set_item_handler=False)

        def on_style_delitem(key):
            """
            Called on deletion of a style key.
            """
            # Optionally delete vendor-prefixed versions
            if self.delete_compatibility_keys_on_delete:
                for compat_key in self.compatibility_keys.get(key, []):
                    if compat_key in self.style:
                        self.style.__delitem__(compat_key, call_on_delete_item_handler=False)

        # Replace the style’s magic methods with our enhanced versions
        self.style.on_set_item = on_style_setitem
        self.style.on_delete_item = on_style_delitem
