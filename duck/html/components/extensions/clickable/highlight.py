"""
Highlight extension for HTML components.

Gives a container component a native-style press highlight: the whole component
dims to a flat overlay color while pressed and fades back out on release, with
no growth or origin point, unlike `RippleExtension`.

**Usage example:**

```py
from duck.html.components.button import Button
from duck.html.components.extensions.clickable import HighlightExtension

class HighlightButton(HighlightExtension, Button):
    pass

btn = HighlightButton(text="Save", highlight_color="rgba(255, 255, 255, 0.4)")
```

**Keyword arguments:**

- `highlight_color` (str): CSS color of the overlay. Defaults to the text color.
- `highlight_opacity` (float): Overlay opacity while pressed, 0 to 1.
- `highlight_duration` (int): Fade time in milliseconds, in or out.

**Notes:**

- The component must be able to contain children, so void elements are rejected.
- The overlay is pure CSS, driven by `:active`, so it is skipped automatically
  during a scroll or swipe and never touches the DOM on press, unlike the
  ripple's wave. It never interferes with the host's own click handling.
- The host gets `position: relative` unless already set. Rounded corners are
  picked up automatically, since the overlay inherits the host's border radius.
"""

from json import dumps
from string import Template

from duck.html.components.script import Script
from duck.html.components.extensions import Extension, ExtensionError


# Identifiers shared between the Python and browser sides
HOST_CLASS = "duck-highlight"
STYLE_ELEMENT_ID = "duck-highlight-style"
READY_FLAG = "duckHighlightReady"
COLOR_VARIABLE = "--duck-highlight-color"
OPACITY_VARIABLE = "--duck-highlight-opacity"
DURATION_VARIABLE = "--duck-highlight-duration"

# Highlight look and timing
DEFAULT_OPACITY = 0.12
DEFAULT_DURATION_MS = 150

# Inline styles a host needs, applied only when the component has not set them
HOST_STYLE_DEFAULTS = {
    "position": "relative",
    "-webkit-tap-highlight-color": "transparent",
}

# Values substituted into the style and script templates below
TEMPLATE_VALUES = {
    "host_class": HOST_CLASS,
    "style_id": STYLE_ELEMENT_ID,
    "ready_flag": READY_FLAG,
    "color_variable": COLOR_VARIABLE,
    "opacity_variable": OPACITY_VARIABLE,
    "duration_variable": DURATION_VARIABLE,
    "default_opacity": DEFAULT_OPACITY,
    "default_duration": DEFAULT_DURATION_MS,
}

# Styles for the overlay, its fade transition, and the pressed state itself
STYLE_TEMPLATE = """
.$host_class {
  position: relative;
}

.$host_class::after {
  content: "";
  position: absolute;
  inset: 0;
  border-radius: inherit;
  background: var($color_variable, currentColor);
  opacity: 0;
  pointer-events: none;
  transition: opacity var($duration_variable, ${default_duration}ms) ease-out;
}

.$host_class:active::after {
  opacity: var($opacity_variable, $default_opacity);
}

.$host_class:disabled::after,
.$host_class[aria-disabled="true"]::after {
  opacity: 0 !important;
}
"""

# Script that installs the styles and enables :active on iOS Safari
SCRIPT_TEMPLATE = """
(function () {
  if (window.$ready_flag) {
    return;
  }
  window.$ready_flag = true;

  // Inject the shared highlight styles once per page
  var style = document.createElement("style");
  style.id = "$style_id";
  style.textContent = $style;
  document.head.appendChild(style);

  // Enable the CSS :active state on iOS Safari, which otherwise only
  // applies it during a long press unless a touch listener is registered.
  // This never calls preventDefault, so scrolling and clicks are untouched.
  document.addEventListener("touchstart", function () {}, { passive: true });
})();
"""

# Render the templates once, at import time
HIGHLIGHT_STYLE = Template(STYLE_TEMPLATE).substitute(TEMPLATE_VALUES)
HIGHLIGHT_SCRIPT = Template(SCRIPT_TEMPLATE).substitute(
    TEMPLATE_VALUES,
    style=dumps(HIGHLIGHT_STYLE),
)


class HighlightExtension(Extension):
    """
    Extension adding a native-style press highlight to container components.

    The component only carries a class, a few style variables and one small
    script. The script installs the overlay styles and the iOS `:active` fix
    the first time it runs, so highlights also work on components added later.
    """

    def apply_extension(self) -> None:
        """
        Apply the highlight effect to the component.

        Marks the component as a highlight host, applies the highlight options
        from `kwargs` and attaches the script that installs the shared styles.

        Raises:
            ExtensionError: If the component cannot contain children.
        """
        super().apply_extension()

        # Import lazily to avoid circular imports, like the other extensions
        from duck.html.components import InnerComponent
        from duck.html.components.script import Script

        # Reject void components because the shared script is a child element
        if not isinstance(self, InnerComponent):
            raise ExtensionError(
                f"Highlight can only be used on inner components that can "
                f"hold children, not {type(self)}"
            )

        # Prepare the host box and the highlight options
        self.apply_highlight_extension_host_style()
        self.apply_highlight_extension_options()
        
    def load(self):
        """
        Load component, modified by HighlightExtension.
        """
        # Only add script after component has been loaded - by default, apply_extension is called before load()
        super().load()
        
        # Add script to component tree
        self.add_highlight_extension_script()
        
    def add_highlight_extension_script(self):
        """
        Adds highlight extension script to component or component's parent.
        """
        # Import lazily to avoid circular imports, like the other extensions
        from duck.html.components import InnerComponent
        from duck.html.components.script import Script
        
        if not getattr(self, "_highlight_extension_script_added", False):
            target_container = self

            # Highlights are rendered as child elements, so the target must be an
            # InnerComponent capable of containing children.
            if not isinstance(target_container, InnerComponent):
                if target_container.parent is not None:
                    target_container = target_container.parent
            
                if not isinstance(target_container, InnerComponent):
                    raise ExtensionError(
                        f"Highlight requires an InnerComponent, but {type(self).__name__} "
                        "cannot contain children. Use an InnerComponent or exclude the "
                        "Highlight extension with exclude_extensions=[HighlightExtension]."
                    )
        
            script = Script(inner_html=HIGHLIGHT_SCRIPT)
            
            # Attach the shared script that installs the styles and pointer handler.
            # This avoids the component error raised when children and inner_html
            # are both populated.
            if target_container.inner_html:
                target_container.inner_html += script.render()
            else:
                target_container.add_child(script)
                
            # Update flag
            self._highlight_extension_script_added = True
            
    def apply_highlight_extension_host_style(self) -> None:
        """
        Mark the component as a highlight host.

        The overlay is an absolutely positioned pseudo-element on the host, so
        the host needs a positioned box. Values the component has already set
        are kept.
        """
        # Add the host class without dropping existing classes
        existing_classes = self.props.get("class", "")
        self.klass = f"{existing_classes} {HOST_CLASS}".strip()

        # Apply the box styles unless the component already defines them
        for property_name, value in HOST_STYLE_DEFAULTS.items():
            if property_name not in self.style:
                self.style[property_name] = value

    def apply_highlight_extension_options(self) -> None:
        """
        Apply the highlight options from `kwargs`.

        Color, opacity, and duration all go through CSS variables read by the
        shared stylesheet, so no per-instance stylesheet rules are needed.
        """
        # Apply the highlight color when one is provided
        color = self.kwargs.get("highlight_color")

        if color is not None:
            self.style[COLOR_VARIABLE] = color

        # Apply the pressed opacity when one is provided
        opacity = self.kwargs.get("highlight_opacity")

        if opacity is not None:
            self.style[OPACITY_VARIABLE] = str(opacity)

        # Apply the fade duration when one is provided
        duration = self.kwargs.get("highlight_duration")

        if duration is not None:
            self.style[DURATION_VARIABLE] = f"{duration}ms"
