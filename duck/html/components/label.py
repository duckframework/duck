"""
Label component module.
"""
from duck.html.components import Theme, InnerHtmlComponent


class Label(InnerHtmlComponent):
    """
    Basic Label component.
    """
    def get_element(self):
        return "label"
