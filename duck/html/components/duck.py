"""
Module containing Duck specific components.
"""
from duck.shortcuts import static

from duck.html.components import to_component
from duck.html.components.theme import Theme
from duck.html.components.container import FlexContainer
from duck.html.components.image import Image
from duck.html.components.label import Label
from duck.html.components.link import Link
from duck.html.components.style import Style


# Default badge content, overridable via kwargs
DEFAULT_URL = "https://duckframework.com"
DEFAULT_TEXT = "Made with Duck \U0001F986"
DEFAULT_LOGO_SRC = "images/duck-logo.png"
DEFAULT_ACCENT_COLOR = "#F5C842"


class MadeWithDuck(Link, FlexContainer):
    """
    A small clickable badge reading "Made with Duck".

    Renders as a pill-shaped chip with the Duck logo, label text, and a
    trailing arrow. On hover the badge lifts, its border picks up an
    accent color, the logo gives a small wiggle, and the arrow slides —
    inviting a click rather than sitting there as a static credit line.

    Args:
        url (str, optional):
            Link target. Defaults to duckframework.com.
        
        text (str, optional):
            Label text. Defaults to "Made with Duck".
        
        logo_src (str, optional):
            Static path to the logo image.
        
        accent_color (str, optional):
            Hover border/glow color. Defaults to `Theme.current.accent_color` when 
            the project defines one, otherwise falls back to Duck's own accent yellow.
        
        id (str, optional):
            Element id, used to scope the hover styling.
    """

    def on_create(self) -> None:
        # Resolve link target and text color before Link builds itself
        self.url = self.kwargs.get("url", DEFAULT_URL)
        self.color = self.kwargs.get("color", "rgba(255, 255, 255, 0.85)")
        
        # Super create
        super().on_create()

        # Base pill badge layout
        self.id = self.kwargs.get("id", "made-with-duck")
        self.klass = "made-with-duck"
        
        # Update style
        self.style.update({
            "display": "inline-flex",
            "gap": "8px",
            "align-items": "center",
            "justify-content": "center",
            "padding": "6px 14px 6px 8px",
            "border-radius": "999px",
            "background": "rgba(255, 255, 255, 0.06)",
            "border": "1px solid rgba(255, 255, 255, 0.14)",
            "font-size": "0.8rem",
            "font-weight": "500",
            "text-decoration": "none",
            "transition": (
                "transform 0.25s ease, border-color 0.25s ease, "
                "background 0.25s ease, box-shadow 0.25s ease"
            ),
        })

        # Badge content and scoped hover behaviour
        self.add_children(self.build_children())
        self.add_child(self.build_style())

    def build_children(self) -> list:
        """
        Builds the badge's logo, label, and trailing arrow.

        Returns:
            List of components making up the badge content.
        """
        return [
            self.build_logo(),
            self.build_label(),
            self.build_arrow(),
        ]

    def build_logo(self) -> Image:
        """
        Builds the small circular Duck logo shown at the start of the badge.

        Returns:
            A configured Image component.
        """
        return Image(
            id="made-with-duck-logo",
            klass="made-with-duck-logo",
            source=static(self.kwargs.get("logo_src", DEFAULT_LOGO_SRC)),
            style={
                "width": "20px",
                "height": "20px",
                "object-fit": "contain",
                "margin": "0px",
                "transition": "transform 0.35s ease",
            },
        )

    def build_label(self) -> Label:
        """
        Builds the badge's label text.

        Returns:
            A configured Label component.
        """
        return Label(
            text=self.kwargs.get("text", DEFAULT_TEXT),
            style={"margin": "0px", "white-space": "nowrap"},
        )

    def build_arrow(self):
        """
        Builds the trailing arrow that slides on hover.

        Returns:
            A Component rendering the arrow glyph.
        """
        return to_component(
            "&#8599;",
            tag="span",
            klass="made-with-duck-arrow",
            style={
                "display": "inline-block",
                "transition": "transform 0.25s ease",
            },
        )

    def build_style(self) -> Style:
        """
        Builds the badge's hover styling, scoped to this instance's id.

        Returns:
            A Style component containing the badge's css rules.
        """
        # Explicit kwarg wins, then a project-defined Theme.current.accent_color,
        # falling back to Duck's own accent yellow
        accent = self.kwargs.get(
            "accent_color", getattr(Theme.current, "accent_color", DEFAULT_ACCENT_COLOR)
        )

        return Style(
            inner_html=f"""
                #{self.id} {{
                    box-shadow: 0 0 0 rgba(0, 0, 0, 0);
                }}

                #{self.id}:hover {{
                    background: rgba(255, 255, 255, 0.1);
                    border-color: {accent};
                    transform: translateY(-2px);
                    box-shadow: 0 6px 18px color-mix(in srgb, {accent} 35%, transparent);
                }}

                #{self.id}:hover .made-with-duck-logo {{
                    transform: rotate(-10deg) scale(1.12);
                }}

                #{self.id}:hover .made-with-duck-arrow {{
                    transform: translateX(4px);
                }}
            """
        )
