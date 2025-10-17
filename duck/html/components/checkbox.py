"""
Checkbox component module.
"""
from duck.html.components.input import Input


class Checkbox(Input):
    """
    Basic Checkbox component.
    
    Args:
     - checked (bool): Whether the checkbox is checked or not.
    """
    def on_create(self):
        super().on_create()
        self.props["type"] = "checkbox"
        
        checkbox_style = {
            "margin": "10px",
            "cursor": "pointer",
        }
        self.style.setdefaults(checkbox_style)
        
        if self.kwargs.get('checked'):
            self.props["checked"] = "true"
