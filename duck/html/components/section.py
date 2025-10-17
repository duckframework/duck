"""
Section component.
"""

from duck.html.components import InnerComponent


class Section(InnerComponent):
    """
    Section component class.
    """
    def get_element(self):
        return "section"
