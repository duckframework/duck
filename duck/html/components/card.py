"""
Card component module
"""

from duck.html.components import Theme
from duck.html.components.container import FlexContainer


class Card(FlexContainer):
    """
    Basic Card component derived from flex container.
    """
    def on_create(self):
        super().on_create()
        self.style["padding"] = Theme.padding
        self.style["min-height"] = "100px"
        self.style['text-align'] = 'center'
        self.style["flex-direction"] = "column"
        self.style["align-items"] = "center"
        self.style["justify-content"] = "center"
        self.style["transition"] = "all 0.3s ease 0s"
        self.style["border-radius"] = Theme.border_radius
        self.style["box-shadow"] = "0 4px 12px rgba(0, 0, 0, 0.1)"
        self.props["class"] = "flex-card"
