"""
Hero component module.
"""
from duck.html.components.container import FlexContainer


class Hero(FlexContainer):
    """
    Basic Hero component.
    """

    def on_create(self):
        super().on_create()
        
        # Update class
        self.klass = "hero"
        
        # Update style
        self.style.update({
            "flex-direction": "column",
            "width": "100%",
            "min-height": "100vh",
            "justify-content": "center",
            "overflow": "hidden",
        })
