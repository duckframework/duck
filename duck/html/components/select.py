"""
Select HTML Component.

This module provides reusable `Select` and `Option` components for creating dropdown menus in HTML.
"""

from duck.html.components import (
    InnerComponent,
    ComponentError,
    Theme,
)


class Option(InnerComponent):
    """
    Represents an individual option within a `Select` dropdown.

    This component is used to define selectable items inside a `Select` component.

    **Example Usage:**
    ```py
    option = Option(inner_html="Option 1")
    select.add_child(option)
    ```

    This generates:
    ```html
    <option>Option 1</option>
    ```

    **Returns:**
        - An `<option>` HTML element.
    """

    def get_element(self):
        """
        Returns the HTML tag for the component.
        """
        return "option"
    
    def on_create(self):
        super().on_create()
        
        # Get optional fields, no need for handling text (already handled by default)
        value = self.kwargs.get("value")
        selected = self.kwargs.get("selected")
        
        if value:
            self.props["value"] = value
        
        if selected:
            self.props["selected"] = "true"
        

class Select(InnerComponent):
    """
    A reusable HTML `<select>` component for creating dropdown menus.

    This component generates a customizable `<select>` dropdown with options.
    
    **Styling:**
    - Uses default styling based on the `Theme` class.
    - Can be customized using CSS styles.
    """
    def get_element(self):
        """
        Returns the HTML tag for the component.
        """
        return "select"

    def on_create(self):
        """
        Initializes the component with default styles and options.
        """
        super().on_create()
        select_style = {
            "padding": "10px",
            "border": "1px solid #ccc",
            "border-radius": Theme.border_radius,
            "font-size": Theme.normal_font_size,
        }
        self.style.setdefaults(select_style)
        
        # Retrieve optional options
        options = self.kwargs.get("options", [])
        
        for option in options:
            if isinstance(option, (str, int, float)):
                option = Option(text=option)
            
            elif isinstance(option, dict):
                option = Option(**option)
            
            elif not isinstance(option, Option):
                raise ComponentError(f"Option must be a string, dictionary, list or Option component not {type(option)}")
            
            # Finally add option
            self.add_child(option if isinstance(option, Option) else Option(inner_html=option))
