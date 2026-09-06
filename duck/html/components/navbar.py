"""
Navigation Bar Component Module.

This module defines reusable components for creating a fully customizable navigation bar.
It includes support for branding, navigation links, and a responsive design.

No external CSS/JS dependencies required (no Bootstrap).
"""

from duck.html.components import InnerComponent, to_component
from duck.html.components.theme import Theme
from duck.html.components.container import Container, FlexContainer
from duck.html.components.button import FlatButton
from duck.html.components.link import Link
from duck.html.components.image import Image
from duck.html.components.script import Script
from duck.html.components.style import Style

# Breakpoint below which the navbar collapses behind the toggler.
COLLAPSE_BREAKPOINT = "992px"


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

        self.color = "transparent"
        self.klass = "navbar-brand"

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
            raise ValueError("Please provide a valid URL in the brand dictionary.")

        self.props["href"] = url

        if image_source:
            image_props = {"class": "nav-brand-image"}

            if alt:
                image_props["alt"] = alt

            self.brand_image = Image(
                source=image_source,
                props=image_props,
                style={"height": "40px", "width": "auto", "margin-right": "8px"},
            )
            self.add_child(self.brand_image)

        if text:
            self.brand_text = FlexContainer(
                text=text,
                props={"class": "nav-brand-text"},
                style={"display": "inline-flex", "margin-left": "3px"},
            )
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
            * highlight (bool): Optional. Renders the link as an accented
              button instead of a plain nav link, e.g. for a "Sign Up" call
              to action as the last link. Defaults to False.
    """

    # Base style shared by every link.
    LINK_STYLE = {"color": "white", "text-wrap": "nowrap"}

    # Layered on top of LINK_STYLE for links marked "highlight": True.
    # Falls back to sensible defaults if the active Theme.current doesn't define
    # these attributes.
    HIGHLIGHT_LINK_STYLE = {
        "background": getattr(Theme.current, "accent_color", "#0d6efd"),
        "color": getattr(Theme.current, "text_color", "#ffffff"),
        "padding": "0.4rem 1rem",
        "border-radius": getattr(Theme.current, "border_radius_sm", "999px"),
        "font-weight": "600",
    }

    def get_element(self) -> str:
        return "ul"

    def on_create(self):
        """
        Initialize and configure the NavbarLinks component.
        """
        super().on_create()

        self.klass = "navbar-nav"
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
            highlight = link_item.get("highlight", False)

            link_style = {**self.LINK_STYLE, **(self.HIGHLIGHT_LINK_STYLE if highlight else {})}
            link_classes = "nav-link" + (" nav-link-highlight" if highlight else "")

            link = Link(
                url=url,
                text=text,
                props={"class": link_classes, "role": "link", "aria-label": text},
                style=link_style,
            )
            list_item = to_component(tag="li", props={"class": "nav-item"}, children=[link])
            self.add_child(list_item)


class NavbarToggler(FlatButton):
    """
    Mobile menu toggle button. Pure CSS hamburger icon — no icon library required.
    """

    def on_create(self):
        super().on_create()

        self.klass = "navbar-toggler"
        self.bg_color = "transparent"
        self.style.update({"border": "none", "outline": "none !important"})
        self.props.update({
            "aria-label": "Toggle navigation",
            "aria-expanded": "false",
            "aria-controls": "navbar-links-container",
        })

        # Three bars built purely from a span + CSS ::before/::after (see NavbarContainer css).
        self.icon_bar = to_component(tag="span", props={"class": "navbar-toggler-icon"})
        self.add_child(self.icon_bar)


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

        # Update class
        self.klass = "navbar-container"

        # Update style
        self.style.update({
            "justify-content": "space-between",
            "width": "100%",
            "align-items": "center",
        })

        # Brand
        self.navbar_brand = NavbarBrand(**self.kwargs)
        self.add_child(self.navbar_brand)

        # Toggler (mobile only, opens/closes via the script below)
        self.navbar_toggler = NavbarToggler()

        # Links, collapsed behind the toggler below the COLLAPSE_BREAKPOINT
        self.navbar_links = NavbarLinks(**self.kwargs)

        # Initialize nav bar links container
        self.navbar_links_container = Container(
            id="navbar-links-container",
            klass="navbar-links-container",
            children=[self.navbar_links],
        )

        # Toggle behavior: tap the toggler, tap a link, tap outside, or
        # press Escape all close the mobile menu.
        self.script = Script(
            inner_html="""
                (function () {
                    function boot() {
                        var toggleBtn = document.querySelector('.navbar-toggler');
                        var navLinks = document.querySelector('.navbar-links-container');

                        if (!toggleBtn || !navLinks || toggleBtn._navInit) return;

                        toggleBtn._navInit = true;

                        function isOpen() {
                            return navLinks.classList.contains('is-open');
                        }

                        function isTogglerVisible() {
                            return getComputedStyle(toggleBtn).display !== 'none';
                        }

                        function setOpen(open) {
                            navLinks.classList.toggle('is-open', open);
                            toggleBtn.classList.toggle('is-open', open);
                            toggleBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
                        }

                        toggleBtn.addEventListener('click', function () {
                            setOpen(!isOpen());
                        });

                        navLinks.addEventListener('click', function (event) {
                            // Only close if the click landed on a nav link and the
                            // toggler is visible (i.e. we're on mobile)
                            if (event.target.closest('.nav-link') && isTogglerVisible()) {
                                setOpen(false);
                            }
                        });

                        document.addEventListener('click', function (event) {
                            if (!isOpen() || !isTogglerVisible()) return;
                            if (toggleBtn.contains(event.target) || navLinks.contains(event.target)) return;
                            setOpen(false);
                        });

                        document.addEventListener('keydown', function (event) {
                            if (event.key === 'Escape' && isOpen()) {
                                setOpen(false);
                            }
                        });

                        // Reset mobile "open" state cleanly when crossing back to desktop.
                        window.addEventListener('resize', function () {
                            if (isTogglerVisible()) return;
                            setOpen(false);
                        });
                    }

                    if (document.readyState === 'loading') {
                        document.addEventListener('DOMContentLoaded', boot);
                    } else {
                        boot();
                    }
                })();
            """
        )

        # Full styling — no external CSS framework required.
        self.css = Style(
            inner_html=f"""
                .navbar {{
                    display: flex;
                    align-items: center;
                    padding: 0.5rem 1rem;
                }}

                .navbar-container {{
                    display: flex;
                    flex-wrap: wrap;
                }}

                .navbar-brand {{
                    order: 1;
                    display: inline-flex;
                    align-items: center;
                    text-decoration: none;
                }}

                .navbar-toggler {{
                    order: 2;
                    display: none;
                    align-items: center;
                    justify-content: center;
                    padding: 0.4rem;
                    cursor: pointer;
                }}

                .navbar-toggler-icon {{
                    display: block;
                    position: relative;
                    width: 22px;
                    height: 2px;
                    background: #fff;
                    transition: background-color 0.15s ease;
                }}

                .navbar-toggler-icon::before,
                .navbar-toggler-icon::after {{
                    content: '';
                    position: absolute;
                    left: 0;
                    width: 22px;
                    height: 2px;
                    background: #fff;
                    transition: transform 0.15s ease, top 0.15s ease, opacity 0.15s ease;
                }}

                .navbar-toggler-icon::before {{ top: -7px; }}
                .navbar-toggler-icon::after {{ top: 7px; }}

                .navbar-toggler.is-open .navbar-toggler-icon {{
                    background: transparent;
                }}

                .navbar-toggler.is-open .navbar-toggler-icon::before {{
                    top: 0;
                    transform: rotate(45deg);
                }}

                .navbar-toggler.is-open .navbar-toggler-icon::after {{
                    top: 0;
                    transform: rotate(-45deg);
                }}

                .navbar-links-container {{
                    order: 3;
                    flex-basis: 100%;
                    width: 100%;
                    display: flex;
                    max-height: 0;
                    overflow: hidden;
                    opacity: 0;
                    transition: max-height 0.3s ease, opacity 0.25s ease;
                }}

                .navbar-links-container.is-open {{
                    max-height: 600px;
                    opacity: 1;
                }}

                .navbar-nav {{
                    list-style: none;
                    margin: 0;
                    padding: 0.75rem 0 0.25rem;
                    display: flex;
                    flex-direction: column;
                    gap: 0.5rem;
                    width: 100%;
                }}

                .nav-item {{
                    display: flex;
                }}

                .nav-link {{
                    text-decoration: none;
                    display: inline-block;
                    padding: 0.35rem 0.1rem;
                }}

                .nav-link-highlight {{
                    display: inline-block;
                    text-align: center;
                }}

                .nav-link-highlight:hover,
                .nav-link-highlight:focus-visible {{
                    filter: brightness(0.92);
                }}

                .nav-link-highlight:active {{
                    transform: scale(0.97);
                }}

                .nav-brand-image {{
                    height: 40px;
                }}

                @media (max-width: 768px) {{
                    .nav-brand-image {{
                        height: 30px !important;
                    }}
                }}

                @media (max-width: {COLLAPSE_BREAKPOINT}) {{
                    .navbar-toggler {{
                        display: inline-flex;
                    }}
                }}

                @media (min-width: {COLLAPSE_BREAKPOINT}) {{
                    .navbar-container {{
                        flex-wrap: nowrap;
                    }}

                    .navbar-toggler {{
                        display: none !important;
                    }}

                    .navbar-links-container {{
                        order: 2;
                        flex-basis: auto;
                        width: auto;
                        max-height: none;
                        overflow: visible;
                        opacity: 1;
                        transition: none;
                    }}

                    .navbar-nav {{
                        flex-direction: row;
                        align-items: center;
                        gap: 1rem;
                        padding: 0;
                        width: auto;
                    }}

                    .nav-link {{
                        padding: 0;
                    }}
                }}
            """
        )

        self.add_child(self.navbar_toggler)
        self.add_child(self.navbar_links_container)
        self.add_child(self.css)
        self.add_child(self.script)


class Navbar(InnerComponent):
    """
    Navigation Bar Component.

    This component represents a full navigation bar with a brand logo, navigation links, and
    a responsive toggler button for mobile screens.

    No external dependencies (self-contained CSS + JS, no Bootstrap required).

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
            {"text": "Get Started", "url": "{% resolve 'signup' fallback_url='#' %}", "highlight": True},
        ],
    {% endNavbar %}
    ```
    """

    def get_element(self) -> str:
        return "nav"

    def on_create(self):
        """
        Initialize and configure the Navbar component.
        """
        super().on_create()

        self.klass = "navbar"
        self.bg_color = "rgba(100, 100, 100, .25)"

        self.add_child(NavbarContainer(**self.kwargs))
