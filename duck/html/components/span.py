"""
Span component.
"""
from duck.html.components import InnerComponent


class Span(InnerComponent):
    """
    Span component class.
    """

    def get_element(self):
        return "span"
