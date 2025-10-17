"""
Icon component module.

Notes:
- This depends on your JS/CSS bundle you are using for icons.
"""
from duck.html.components import InnerComponent
from duck.html.components.link import Link


class IconLink(Link):
    """
    Icon Link component.
    """
    def on_create(self):
        super().on_create()
        self.style["color"] = "#ccc"


class Icon(InnerComponent):
    """
    Icon component.
    
    Notes:
    - This is just a `<span>` component, provide argument `klass` for the icon class.
    """
    def get_element(self):
        return "span"
