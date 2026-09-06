"""
Textarea HTML Component.

This module provides a customizable `TextArea` component for handling multi-line text input in HTML forms.
"""

from duck.html.components.theme import Theme
from duck.html.components import InnerComponent


class TextArea(InnerComponent):
    """
    A reusable HTML `<textarea>` component for multi-line text input.
    
    Args:
        name (str, optional):  
            The name attribute of the textarea, used for form submissions.

        placeholder (str, optional):  
            Placeholder text displayed inside the textarea before user input.

        required (bool, optional):  
            Whether the textarea is a required field in a form.

        maxlength (int, optional):  
            The maximum number of characters allowed in the textarea.
        
        minlength (int, option):
            The minimum number of characters.
        
        disabled (bool, optional):
            Whether input is disabled.
         
    Example:
    
    ```py
    textarea = TextArea(
        name="user_message",
        placeholder="Enter your message...",
        required=True,
        maxlength=500
    )
    component.add_child(textarea)
    ```

    **Generates:**
    ```html
    <textarea name="user_message" placeholder="Enter your message..." required maxlength="500"></textarea>
    ```

    **Default Styling:**
    - Uses padding, borders, and font settings from the `Theme.current` class.
    - Minimum width is set to `50%` and minimum height to `80px`.

    **Returns:**
    - A `<textarea>` HTML element.
    """

    def get_element(self):
        """
        Returns the HTML tag for the component.
        """
        return "textarea"

    def on_create(self):
        """
        Initializes the component with default styles and attributes.
        """
        super().on_create()
        
        # Apply default styling
        textarea_style = {
            "padding": Theme.current.padding,
            "border": f"1px solid {Theme.current.border_color}",
            "border-radius": Theme.current.border_radius,
            "font-size": Theme.current.font_size,
        }
        self.style.setdefaults(textarea_style)

        # Set default properties
        self.props.update({"min-width": "50%", "min-height": "80px"})

        # Assign properties based on arguments
        if "name" in self.kwargs:
            self.props["name"] = self.kwargs.get("name")

        if "placeholder" in self.kwargs:
            self.props["placeholder"] = self.kwargs.get("placeholder")

        if self.kwargs.get("required", False):
            self.props["required"] = "true"

        if "maxlength" in self.kwargs:
            self.props["maxlength"] = str(self.kwargs.get("maxlength"))
        
        if "minlength" in self.kwargs:
           self.props["minlength"] = str(self.kwargs.get('minlength')) or ''  
                
        self.props["disabled"] = bool(self.kwargs.get("disabled"))
