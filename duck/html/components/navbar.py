"""
Navigation Bar Component Module.

This module defines reusable components for creating a fully customizable navigation bar.
It includes support for branding, navigation links, and a responsive design.
"""

from duck.html.components import (
    Component,
    InnerComponent,
    Theme,
    to_component,
)
from duck.html.components.container import (
    Container,
    FlexContainer,
)
from duck.html.components.button import (
    Button,
    FlatButton,
)
from duck.html.components.link import Link
from duck.html.components.icon import Icon
from duck.html.components.image import Image
from duck.html.components.script import Script
from duck.html.components.style import Style


class NavbarBrand(Link):
    """
    Navigation Bar Brand Component.

    This component represents the brand section of the navigation bar. It is a clickable
    link that can contain a brand image, text, or both. It is primarily used within
    the `Navbar` component.

    Args:
        brand (dict): A dictionary containing brand details:
            * image_source (str): The URL of the brand image.
            * alt (str): Alternative text for the brand image.
            * url (str): The destination URL when the brand is clicked.
            * text (str): The text displayed next to the brand image.
    """

    def on_create(self):
        """
        Initialize and configure the NavbarBrand component.
        """
        super().on_create()
        self.color = "transaparent"
        self.klass = "navbar-brand me-auto"
        
        if "brand" in self.kwargs:
            self.add_navbar_image()
            
    def add_navbar_image(self):
        """
        Adds a brand image and optional text to the NavbarBrand component.
        """
        brand = self.kwargs.get("brand", {})
        image_source = brand.get("image_source")
        alt = brand.get("alt", "")
        url = brand.get("url")
        text = brand.get("text", "")
        
        if not url:
            raise ValueError("Please provide valid URL in brand dictionary.")
        
        else:
            self.props["href"] = url
        
        if image_source:
            self.brand_image = Image(source=image_source)
            self.brand_image.props["class"] = "nav-brand-image"
            self.brand_image.style["height"] = "40px"
            self.brand_image.style["width"] = "auto"
            self.brand_image.style["margin-right"] = "8px"
            
            if alt:
                self.brand_image.props["alt"] = alt
            
            # Add the brand image.
            self.add_child(self.brand_image)

        if text:
            self.brand_text = FlexContainer(text=text)
            self.brand_text.style["display"] = "inline-flex"
            self.brand_text.style["margin-left"] = "3px"
            self.brand_text.props["class"] = "nav-brand-text"
            self.add_child(self.brand_text)


class NavbarLinks(InnerComponent):
    """
    Navigation Bar Links Component.

    This component contains a list of navigation links displayed in the navbar.

    Args:
        links (list): A list of dictionaries representing navigation links.
            Each dictionary should have:
            * text (str): The display text for the link.
            * url (str): The URL the link navigates to.
    """

    def get_element(self):
        return "ul"

    def on_create(self):
        """
        Initialize and configure the NavbarLinks component.
        """
        super().on_create()
        self.klass = "navbar-nav navbar-links d-flex gap-3"
        self.id = "navbar-links"

        if "links" in self.kwargs:
            self.add_links()

    def add_links(self):
        """
        Adds navigation links to the component.
        """
        links = self.kwargs.get("links", [])

        for link_item in links:
            text = link_item.get("text", "")
            url = link_item.get("url", "#")
            link = Link(url=url, text=text, props={"class": "nav-link active"})
            link.color = "white"
            list_item = to_component(tag="li", props={'class': 'nav-item'})
            list_item.add_child(link)
            self.add_child(list_item)


class NavbarContainer(FlexContainer):
    """
    Navbar Container Component.

    This component wraps and organizes all elements inside the navigation bar, including
    branding, toggler buttons for mobile, and navigation links.
    """

    def on_create(self):
        """
        Initialize and configure the NavbarContainer component.
        """
        super().on_create()
        self.klass = "container-fluid d-flex justify-content-between align-items-center"
        self.style["justify-content"] = "space-between"
        self.style["width"] = "100%"
        
        # Add Navbar Brand
        self.navbar_brand = NavbarBrand(**self.kwargs)
        self.add_child(self.navbar_brand)
        
        # Add Navbar Toggler (for mobile)
        self.navbar_toggler = FlatButton()
        self.navbar_toggler.style["outline"] = "none !important"
        self.navbar_toggler.bg_color = "transparent"
        self.navbar_toggler.klass = "navbar-toggler"
        self.navbar_toggler.props["onclick"] = "toggleCollapse($('.navbar-links-container'));"

        self.navbar_toggler_icon = Icon(klass="navbar-toggler-icon bi bi-list")
        self.navbar_toggler_icon.style["width"] = "16px"
        self.navbar_toggler_icon.style["height"] = "16px"
        self.navbar_toggler_icon.props["alt"] = "menu"

        self.navbar_toggler.add_child(self.navbar_toggler_icon)
        self.add_child(self.navbar_toggler)

        # Add Navbar Links Container
        self.navbar_links_container = Container()
        self.navbar_links_container.props["class"] = "navbar-links-container collapse navbar-collapse d-lg-flex align-items-center"
        self.add_child(self.navbar_links_container)
        
        # Add Navbar Links to their container
        self.navbar_links_container.add_child(NavbarLinks(**self.kwargs))
        
        # Add script for toggling navbar visibility
        self.script = Script(
            inner_html="""
                function toggleCollapse(elem) {
                    elem = $(elem);
                    if (elem.is(':hidden')) {
                        elem.css('display', 'flex');
                    } else {
                        elem.css('display', 'none');
                    }
                }
                
                function closeNavbar() {
                  const toggleBtn = $('.navbar-toggler');
                  const navlinks = $('.navbar-links-container');
                  
                  // Only hide if navbar toggle button is visible
                  if (!toggleBtn.is(':hidden')) {
                    navlinks.css('display', 'none');
                  }
                }
                
                $(document).ready(() => {
                  const navlinks = $('.nav-link');
                  navlinks.on('click', closeNavbar);
                });
            """
        )
        
        # Add responsive styles
        self.css = Style(
            inner_html="""
                @media (max-width: 768px){
                    .navbar-links-container {
                        justify-content: flex-start !important;
                    }
                    .nav-brand-image {
                        height: 30px !important;
                    }
                }

                @media (min-width: 992px){
                    .navbar-links-container {
                        justify-content: flex-end !important;
                    }
                }
            """
        )
        
        self.add_child(self.css)
        self.add_child(self.script)


class Navbar(InnerComponent):
    """
    Navigation Bar Component.

    This component represents a full navigation bar with a brand logo, navigation links, and
    a responsive toggler button for mobile screens.
    
    Notes:
    - This requires Bootsrap & Bootstrap icons library.
    
    Example Template Usage:
    
    ```django
    {% Navbar %}
        brand = {
            "image_source": "{% static 'images/logo.png' %}",
            "alt": "Duck Logo",
            "url": '{% resolve "home" fallback_url="#" %}',
            "text": "Duck logo"
        },
        links = [
            {"text": "Home", "url": "{% resolve 'home' fallback_url='#' %}"},
            {"text": "About", "url": "{% resolve 'about' fallback_url='#' %}"},
            {"text": "Services", "url": "{% resolve 'services' fallback_url='#' %}"},
            {"text": "Contact", "url": "{% resolve 'contact' fallback_url='#' %}"},
            {"text": "Consultation", "url": "{% resolve 'consultation' fallback_url='#' %}"},
            {"text": "Jobs", "url": "{% resolve 'jobs' fallback_url='#' %}"},
        ],
    {% endNavbar %}
    ```
    """

    def get_element(self):
        return "nav"

    def on_create(self):
        """
        Initialize and configure the Navbar component.
        """
        super().on_create()
        self.klass = "navbar navbar-expand-lg navbar-dark px-3"
        self.bg_color = "rgba(100, 100, 100, .25)"

        # Add Navbar Container
        self.add_child(NavbarContainer(**self.kwargs))
       