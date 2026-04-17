"""
Module containing Duck specific components.
"""

from duck.html.components.container import FlexContainer
from duck.html.components.image import Image
from duck.html.components.label import Label
from duck.html.components.link import Link
from duck.html.components.style import Style


class MadeWithDuck(Link, FlexContainer):
    """
    This is just a flex container component containing Duck's image alongside
    text named `Proudly made with Duck`
    """
    def on_create(self):
        from duck.shortcuts import static
        
        self.url = "https://duckframework.com"
        self.color = "white"
        
        # Call the super creation
        super().on_create()
        
        self.style["gap"] = "10px"
        self.style["align-items"] = "center"
        self.style["justify-content"] = "center"
        self.style["text-decoration"] = "underline"
        self.style["font-size"] = ".8rem"
        
        # Set ID
        self.id = "made-with-duck"
        
        # Add image.
        self.image = Image(id="proudly-duck-logo", source=static('images/duck-logo.png'))
        self.image.style["object-fit"] = "contain"
        self.image.style["margin"] = "0px"
        self.add_child(self.image)
        
        # Add some text.
        self.add_child(Label(text="Proudly Made With Duck", style={"margin": "0px"}))
        self.add_child(
            Style(
                inner_html="""
                #proudly-duck-logo {
                    width: 25px;
                    height: 25px;
                    margin-top: 5px;
                    margin-bottom: 5px;
                }"""
            ),
        )
        