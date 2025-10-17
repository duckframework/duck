"""
Paragraph component.
"""

from duck.html.components import InnerComponent


class Paragraph(InnerComponent):
    """
    Paragraph component class.
    """
    def get_element(self):
        return "p"
