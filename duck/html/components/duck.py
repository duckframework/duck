"""
Module containing Duck specific components.
"""

from duck.html.components.container import FlexContainer
from duck.html.components.image import Image
from duck.html.components.label import Label


class MadeWithDuck(FlexContainer):
    """
    This is just a flex container component containing Duck's image alongside
    text named `Proudly made with Duck`
    """
    def on_create(self):
        from duck.etc.templatetags import static
        
        # Call the super creation
        super().on_create()
        
        self.style["gap"] = "10px"
        self.style["align-items"] = "center"
        self.style["justify-content"] = "center"
        
        # Add image.
        self.image = Image(source=static('images/duck-logo.png'))
        self.image.style["object-fit"] = "contain"
        self.image.style["margin"] = "0px"
        self.add_child(self.image)
        
        # Add some text.
        self.add_child(Label(text="Proudly made with Duck", style={"margin": "0px"}))
