"""
Image components module.

Available Images:
- `Image`: Base image component.
- `CircularImage`: Rounded circular image component.
"""

from duck.html.components import NoInnerComponent


class Image(NoInnerComponent):
    """
    Basic Image component.

    Args:
        source (str): Image source URL.
        alt (str): Image alternative text.
        width (str): Image width.
        height (str): Image height.
    """

    def get_element(self) -> str:
        return "img"

    def on_create(self):
        super().on_create()

        if self.kwargs.get("source"):
            self.props["src"] = self.kwargs.get("source")

        if self.kwargs.get("alt"):
            self.props["alt"] = self.kwargs.get("alt")

        # Initialize style
        style = {}

        if self.kwargs.get("width"):
            style["width"] = self.kwargs.get("width")

        if self.kwargs.get("height"):
            style["height"] = self.kwargs.get("height")

        self.style.update(style)


class CircularImage(Image):
    """
    Circular Image component.

    Args:
        source (str): Image source URL.
        alt (str): Image alternative text.
        width (str): Image width.
        height (str): Image height.
    """

    def on_create(self):
        super().on_create()
        
        # Update style
        self.style.update({"border-radius": "50%"})
