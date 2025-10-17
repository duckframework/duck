"""
Heading component.
"""

from duck.html.components import InnerComponent


class Heading(InnerComponent):
    """
    Heading component class.
    
    Args:
        type (str): The html tag e.g. h1, h2.
    """
    def __init__(self, type: str, text: str=None, *args, **kwargs):
        # The following approach allows inner_html to be setable if no text supplied. 
        if text:
            super().__init__(element=type, text=text, *args, **kwargs)
        else:
            super().__init__(element=type, *args, **kwargs)