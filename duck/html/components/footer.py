"""
Footer component module.
"""
from duck.html.components import (
  Component,
  InnerComponent,
  Theme,
  to_component,
)
from duck.html.components.duck import MadeWithDuck
from duck.html.components.container import FlexContainer
from duck.html.components.style import Style
from duck.html.components.link import Link
from duck.html.components.heading import Heading


class FooterBlock(FlexContainer):
    """
    Footer Block component which will contain a list of footer items.
    
    Args:
        heading (str): The heading for the footer block
        elements (list[str]): List containing block elements as html e.g ['<b>Value</b>', ...]
    
    Notes:
    - This component may have different footer blocks with different headings and items.
    """
    def on_create(self):
        super().on_create()
        self.style["flex-direction"] = "column"
        
        if "heading" in self.kwargs:
            heading = self.kwargs.get('heading')
            self.heading = Heading("h2", text=heading, klass="footer-heading", color="white")
            self.heading.style["font-size"] = "1.2rem"
            self.add_child(self.heading)
            
        if 'elements' in self.kwargs:
           for element in self.kwargs.get('elements', []):
               # This is an html element
               if isinstance(element, Component):
                   self.add_child(element)
               else:
                   self.add_child(to_component(element))


class FooterItems(FlexContainer):
    """
    Main container component for storing footer items.
    
    Args:
        footer_items (dict[str, list[str]]): A dictionary containing a mapping of footer block headings to a
                                                                list of different html elements as strings. 
    """
    def on_create(self):
        super().on_create()
        self.style["gap"] = "10px"
        self.style["padding"] = Theme.padding
        self.style["justify-content"] = "space-between"
        self.style["flex-wrap"] = "wrap"
        
        if "footer_items" in self.kwargs:
             for heading, elements in self.kwargs.get('footer_items', {}).items():
                 footer_block = FooterBlock(heading=heading, elements=elements)
                 self.add_child(footer_block)


class Footer(InnerComponent):
    """
    Footer component.
    
    Args:
        footer_items (dict[str, list[str]]): A dictionary containing a mapping of footer block headings to a
            list of different html elements as strings. 
        copyright (str): Copyright information.
        
    Template Usage:
     
     ```django
     {% Footer %}
         footer_items = {
             "Company": [
                 '{% Link %}text="About Us", url="{% resolve 'about' fallback_url='#' %}"{% endLink %}',
                 '{% Link %}text="Contact Us", url="{% resolve 'contact' fallback_url='#' %}"{% endLink %}',
                 '{% Link %}text="Our Services", url="{% resolve 'services' fallback_url='#' %}"{% endLink %}',
             ], # Quick links
             "Legal": [
                 '{% Link %}text="Privacy Policy", url="{% resolve 'privacy' fallback_url='#' %}"{% endLink %}',
                 '{% Link %}text="Terms & Conditions", url="{% resolve 'tos' fallback_url='#' %}"{% endLink %}',
             ],
           },
           copyright="&copy; 2025 Duck. All rights reserved.",
   {% endFooter %}
    ```
    """
    def get_element(self):
        return "footer"
    
    def on_create(self):
        super().on_create()
        self.style["padding"] = Theme.padding
        self.style["width"] = "100%"
        self.style["font-size"] = ".8rem"
        self.footer_items = FooterItems(**self.kwargs)
        
        # Add footer items
        self.add_child(self.footer_items)
        
        # Add made with Duck
        self.duck_link = Link(url="https://github.com/duckframework/duck")
        self.duck_link.add_child(MadeWithDuck())
        self.add_child(self.duck_link)
        
        # Add copyright info
        if self.kwargs.get('copyright'):
            copyright = self.kwargs.get('copyright') or ''
            self.copyright = to_component(copyright, "p", style={"text-align": "center"})
            self.add_child(self.copyright)
        
        # Add style
        self.css= Style(
            inner_html="""
                @media (max-width: 768px){
                    footer {
                          font-size: .8rem;
                      }
                      
                      footer p {
                          font-size: .8rem !important;
                      }
                      
                      footer img {
                          width: 25px;
                          height: 25px;
                          margin-top: 5px;
                          margin-bottom: 5px;
                      }
                  }
            """
        )
        self.add_child(self.css)
