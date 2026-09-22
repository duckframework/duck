"""
Icon component module.

Notes:
- This depends on your JS/CSS bundle you are using for icons.
"""
from duck.html.components.link import Link
from duck.html.components.span import Span
from duck.html.components.button import Clickable


class IconLink(Link):
    """
    Icon Link component.
    """


class Icon(Span):
    """
    Icon component.
    
    Notes:
    - This is just a `<span>` component, provide argument `klass` for the icon class.
    """


class IconButton(Clickable, Span):
    """
    An icon button component.
    """
