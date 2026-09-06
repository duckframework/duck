"""
Select HTML Component.

This module provides reusable `Select` and `Option` components for creating dropdown menus in HTML.
"""

from duck.html.components import ComponentError, InnerComponent
from duck.html.components.theme import Theme


class Option(InnerComponent):
    """
    Represents an individual option within a `Select` dropdown.

    This component is used to define selectable items inside a `Select` component.

    Args:
        text (str): The option's display text (or pass `inner_html` directly).
        value (str): Optional. The option's `value` attribute, if it differs from its text.
        selected (bool): Optional. Whether this option is selected by default.

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

    def get_element(self) -> str:
        """
        Returns the HTML tag for the component.
        """
        return "option"

    def on_create(self) -> None:
        super().on_create()

        # Get optional fields, no need for handling text (already handled by default)
        value = self.kwargs.get("value")
        selected = self.kwargs.get("selected")

        if value:
            self.props["value"] = value

        if selected:
            self.props["selected"] = True


class Select(InnerComponent):
    """
    A reusable HTML `<select>` component for creating dropdown menus.

    This component generates a customizable `<select>` dropdown with options.

    Args:
        name (str): Optional. The `name` attribute for the select field.
        options (list): Optional. A list of options, where each item is either
            a string/int/float (used as the option text), a dict of Option
            constructor kwargs, or an `Option` component instance.

    **Styling:**
    - Uses default styling based on the `Theme.current` class, falling back to sensible
      defaults when the active theme doesn't define them.
    - Can be overridden per-instance via the `style` kwarg, or with CSS.
    """

    DEFAULT_STYLE = {
        "padding": "10px",
        "border": "1px solid #ccc",
        "border-radius": getattr(Theme.current, "border_radius", "6px"),
        "font-size": getattr(Theme.current, "font_size", "1rem"),
    }

    def get_element(self) -> str:
        """
        Returns the HTML tag for the component.
        """
        return "select"

    def on_create(self) -> None:
        """
        Initializes the component with default styles and options.
        """
        super().on_create()

        # Fill in theme defaults without clobbering any style already set
        self.style.setdefaults(self.DEFAULT_STYLE)
        
        # Get the name
        name = self.kwargs.get("name")

        if name:
            self.props["name"] = name

        for option in self.kwargs.get("options", []):
            self.add_child(self.to_option(option))

    def to_option(self, option) -> Option:
        """
        Normalizes a raw option value into an `Option` component.

        Args:
            option: A string/int/float, a dict of Option kwargs, or an
                existing `Option` component.

        Returns:
            An `Option` component.

        Raises:
            ComponentError: If `option` isn't one of the supported types.
        """
        if isinstance(option, Option):
            return option

        if isinstance(option, (str, int, float)):
            return Option(text=option)

        if isinstance(option, dict):
            return Option(**option)

        raise ComponentError(
            f"Option must be a string, number, dictionary, or Option component, not {type(option)}"
        )
