"""
Link component module.
"""

from duck.html.components import InnerComponent
from duck.html.components.theme import Theme


class Link(InnerComponent):
    """
    Link component.

    Args:
        url (str): The link's URL.
        text (str): Text for the link.
    """

    def __init__(self, url: str = None, text: str = None, *args, **kwargs) -> None:
        self.url = url or "#"
        super().__init__(text=text, *args, **kwargs)

    def get_element(self) -> str:
        return "a"

    def on_create(self):
        super().on_create()
        
        # Set default class
        self.props.setdefault("class", "link")
        
        # Update props
        self.props.update({"href": self.url, "aria-label": self.text})
        
        # Themeable defaults, callers can still override via style=
        self.style.setdefault("text-decoration", "none")
        self.style.setdefault("color", getattr(Theme.current, "link_color", "inherit"))
