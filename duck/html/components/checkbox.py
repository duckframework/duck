"""
Checkbox component module.
"""
from duck.html.components.input import Input


class Checkbox(Input):
    """
    Basic Checkbox component.
    
    Args:
        checked (bool): Whether the checkbox is checked or not.
    """
    def on_create(self):
        super().on_create()
        
        # Update props
        self.props.update({"type": "checkbox"})
        
        # Update style
        self.style.setdefaults({
            "margin": "10px",
            "cursor": "pointer",
        })
        
        self.props.update("checked", self.kwargs.get('checked'))
