"""
Link component module.
"""

from duck.html.components import InnerComponent
from duck.html.components import Theme


class Link(InnerComponent):
    """
    Link component.
    
    Args:
        url (str): The link's URL.
        text (str): Text for the link.
    """
    def __init__(self, url: str = None, *args, **kwargs):  
        self.url = url or "#"
        super().__init__(*args, **kwargs)
        
    def get_element(self):
        return "a"
        
    def on_create(self):
        super().on_create()
        self.style.setdefault("text-decoration", "none")
        self.props.setdefault("class", "link")
        self.props["href"] = self.url
