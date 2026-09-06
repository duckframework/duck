"""
Footer component module.
"""
from datetime import datetime
from typing import Any

from duck.html.components import (
    Component,
    InnerComponent,
    to_component,
)
from duck.html.components.theme import Theme
from duck.html.components.duck import MadeWithDuck
from duck.html.components.container import FlexContainer
from duck.html.components.style import Style
from duck.html.components.link import Link
from duck.html.components.span import Span
from duck.html.components.heading import Heading
from duck.meta import Meta


# Duck project links used by the "made with Duck" badge
GITHUB_URL = "https://github.com/duckframework/duck"
DUCK_URL = "https://duckframework.com"

# Default inline svg icons, keyed by platform name, used when a social
# link entry does not supply its own icon
DEFAULT_SOCIAL_ICONS = {
    "twitter": (
        '<svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor">'
        '<path d="M23 3a10.9 10.9 0 0 1-3.14 1.53 4.48 4.48 0 0 0-7.86 3v1'
        'A10.66 10.66 0 0 1 3 4s-4 9 5 13a11.64 11.64 0 0 1-7 2c9 5 20 0 20-11.5'
        'a4.5 4.5 0 0 0-.08-.83A7.72 7.72 0 0 0 23 3z"/></svg>'
    ),
    "instagram": (
        '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" '
        'stroke="currentColor" stroke-width="1.8">'
        '<rect x="2" y="2" width="20" height="20" rx="5"/>'
        '<circle cx="12" cy="12" r="4"/>'
        '<circle cx="17.5" cy="6.5" r="1" fill="currentColor" stroke="none"/>'
        '</svg>'
    ),
    "facebook": (
        '<svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor">'
        '<path d="M13 22v-9h3l.5-4H13V6.5A1.5 1.5 0 0 1 14.5 5H17V1h-3'
        'a5 5 0 0 0-5 5v3H6v4h3v9z"/></svg>'
    ),
    "whatsapp": (
        '<svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor">'
        '<path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5.1-1.3A10 10 0 1 0 12 2z'
        'm0 18.2a8.2 8.2 0 0 1-4.2-1.1l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 1 1 12 20.2z'
        'm4.5-6.1c-.2-.1-1.5-.7-1.7-.8s-.4-.1-.6.1-.6.8-.8 1-.3.2-.6.1'
        'a6.6 6.6 0 0 1-2-1.2 7.4 7.4 0 0 1-1.4-1.7c-.1-.2 0-.4.1-.5s.3-.3.4-.5'
        'a.5.5 0 0 0 .1-.5c-.1-.1-.6-1.4-.8-1.9s-.4-.4-.6-.4h-.5a1 1 0 0 0-.7.3'
        'A3 3 0 0 0 6.5 9c0 1.6 1.2 3.2 1.4 3.4s2.3 3.5 5.6 4.9c.8.3 1.4.5 1.9.7'
        'a4.5 4.5 0 0 0 2 .1c.6-.1 1.5-.6 1.7-1.2s.2-1.1.2-1.2-.2-.2-.4-.3z"/></svg>'
    ),
    "github": (
        '<svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor">'
        '<path d="M12 1.5a10.5 10.5 0 0 0-3.32 20.47c.53.1.72-.23.72-.5v-1.96'
        'c-2.93.64-3.55-1.24-3.55-1.24-.48-1.22-1.17-1.55-1.17-1.55-.96-.66.07-.64'
        '.07-.64 1.06.07 1.62 1.09 1.62 1.09.94 1.61 2.46 1.15 3.06.87.1-.68.37'
        '-1.15.67-1.41-2.34-.27-4.8-1.17-4.8-5.21 0-1.15.41-2.09 1.09-2.83'
        '-.11-.27-.47-1.35.1-2.81 0 0 .89-.29 2.9 1.08a10 10 0 0 1 5.28 0'
        'c2.01-1.37 2.9-1.08 2.9-1.08.57 1.46.21 2.54.1 2.81.68.74 1.09 1.68 1.09'
        ' 2.83 0 4.05-2.47 4.94-4.82 5.2.38.33.71.97.71 1.96v2.9c0 .27.19.61.73.5'
        'A10.5 10.5 0 0 0 12 1.5z"/></svg>'
    ),
    "youtube": (
        '<svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor">'
        '<path d="M22.5 7.2a3 3 0 0 0-2.1-2.1C18.6 4.5 12 4.5 12 4.5s-6.6 0-8.4.6'
        'a3 3 0 0 0-2.1 2.1A31 31 0 0 0 1 12a31 31 0 0 0 .5 4.8 3 3 0 0 0 2.1 2.1'
        'c1.8.6 8.4.6 8.4.6s6.6 0 8.4-.6a3 3 0 0 0 2.1-2.1A31 31 0 0 0 23 12'
        'a31 31 0 0 0-.5-4.8zM9.8 15.3V8.7l6 3.3-6 3.3z"/></svg>'
    ),
    "email": (
        '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" '
        'stroke="currentColor" stroke-width="1.8">'
        '<rect x="2" y="4" width="20" height="16" rx="2"/>'
        '<path d="M2 6l10 7 10-7"/></svg>'
    ),
    "patreon": (
        '<svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor">'
        '<circle cx="15" cy="9.5" r="6.5"/>'
        '<rect x="2" y="2" width="3.5" height="20"/></svg>'
    ),
    "tiktok": (
        '<svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor">'
        '<path d="M16.5 2h-3v13.7a3.2 3.2 0 1 1-2.3-3.07V9.5a6.3 6.3 0 1 0 5.3'
        ' 6.2V8.4a8.2 8.2 0 0 0 4.8 1.5V6.8a5 5 0 0 1-4.8-4.8z"/></svg>'
    ),
    "linkedin": (
        '<svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor">'
        '<path d="M4.98 3.5a2.5 2.5 0 1 1 0 5 2.5 2.5 0 0 1 0-5zM3 9h4v12H3z'
        'M9 9h3.8v1.7h.05c.53-1 1.83-2.06 3.77-2.06 4.03 0 4.78 2.65 4.78 6.1'
        'V21h-4v-5.6c0-1.34-.02-3.06-1.87-3.06-1.87 0-2.16 1.46-2.16 2.96V21H9z"/>'
        '</svg>'
    ),
    "discord": (
        '<svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor">'
        '<path d="M20 4.5A18 18 0 0 0 15.6 3l-.35.7a15 15 0 0 1 3.65 1.4'
        'A16.6 16.6 0 0 0 12 3.6a16.6 16.6 0 0 0-6.9 1.5A15 15 0 0 1 8.75 3.7'
        'L8.4 3A18 18 0 0 0 4 4.5C1.6 8 1 11.4 1.2 14.7a18 18 0 0 0 5.4 2.7'
        'l.75-1.2a11.6 11.6 0 0 1-1.85-.9c.16-.1.3-.23.45-.34a12.8 12.8 0 0 0'
        '10.1 0c.15.11.29.24.45.34a11.6 11.6 0 0 1-1.85.9l.75 1.2a18 18 0 0 0'
        '5.4-2.7c.24-3.9-.7-7.3-2.8-10.2zM8.7 13.1c-.85 0-1.55-.78-1.55-1.75'
        's.68-1.75 1.55-1.75 1.57.79 1.55 1.75c0 .97-.68 1.75-1.55 1.75z'
        'm6.6 0c-.85 0-1.55-.78-1.55-1.75s.68-1.75 1.55-1.75 1.57.79 1.55 1.75'
        'c0 .97-.67 1.75-1.55 1.75z"/></svg>'
    ),
}


class FooterHeading(Heading):
    """
    Small-caps section heading used inside a footer block.

    Args:
        heading_color (str): Optional color override for the heading text.
    """

    def on_create(self) -> None:
        super().on_create()

        # Base heading styling
        self.klass = "footer-heading"
        self.style.update({
            "font-size": "0.95rem",
            "letter-spacing": "0.04em",
            "text-transform": "uppercase",
            "margin-bottom": "6px",
            "color": self.kwargs.get("heading_color") or "rgba(255, 255, 255, 0.55)",
        })


class FooterBlock(FlexContainer):
    """
    A single footer column: a heading plus a list of link/text elements.

    Args:
        heading (str):
            The heading for the footer block.
        
        elements (list[str | Component]):
            Block elements, either raw html strings (e.g. produced by a `{% Link %}` template tag) or
            already-built Component instances.
        
        heading_color (str):
            Optional override for the heading color.

    Notes:
        A footer may render several blocks side by side, each with its
        own heading and items.
    """

    def on_create(self) -> None:
        super().on_create()

        # Base column layout
        self.klass = "footer-block"
        self.style.update({
            "flex-direction": "column",
            "gap": "10px",
            "min-width": "100px",
        })

        # Build the heading and items together, in construction order
        self.add_children(self.build_children())

    def build_children(self) -> list[Component]:
        """
        Builds the heading (if any) followed by the block's elements.

        Returns:
            List of Component instances ready to be added as children.
        """
        children = []

        # Optional block heading
        heading = self.kwargs.get("heading")
        
        if heading:
            children.append(
                FooterHeading(
                    type="h3",
                    text=heading,
                    heading_color=self.kwargs.get("heading_color"),
                )
            )

        # Block items, converting raw html where needed
        for element in self.kwargs.get("elements", []):
            if isinstance(element, Component):
                children.append(element)
            else:
                children.append(to_component(element, tag="span"))

        return children


class SocialLinks(FlexContainer):
    """
    Row of social/contact icon links with a premium hover treatment.

    Args:
        social_links (list[dict]): Each entry supports:
            - platform (str): Key into DEFAULT_SOCIAL_ICONS, e.g. "twitter".
            - url (str): Destination url.
            - icon (str, optional): Raw svg to use instead of the default.
            - label (str, optional): Accessible label, defaults to platform.
    """

    def on_create(self) -> None:
        super().on_create()

        # Base row layout
        self.id = self.kwargs.get("id", "footer-social-links")
        self.klass = "footer-social-links"
        self.style.update({
            "gap": "10px",
            "align-items": "center",
        })

        # Build one icon link per configured social entry
        self.add_children(self.build_icon_links())

    def build_icon_links(self) -> list[Link]:
        """
        Builds one circular icon link per configured social entry.

        Returns:
            List of Link components, each wrapping a social platform icon.
        """
        icon_links = []

        for entry in self.kwargs.get("social_links", []):
            icon_links.append(self.build_icon_link(entry))

        return icon_links

    def build_icon_link(self, entry: dict[str, Any]) -> Link:
        """
        Builds a single circular icon link from a social link entry.

        Args:
            entry: A social link entry, see `social_links` above.

        Returns:
            A Link component wrapping the platform's icon.
        """
        platform = entry.get("platform", "")
        icon = entry.get("icon") or DEFAULT_SOCIAL_ICONS.get(platform, "")
        label = entry.get("label", platform.title())

        return Link(
            id=f"footer-social-{platform}",
            url=entry.get("url", "#"),
            klass="footer-social-icon",
            props={"aria-label": label},
            children=[Span(inner_html=icon, style={"display": "flex", "justify-content": "center", "align-items": "center"})],
        )


class FooterItems(FlexContainer):
    """
    Main container laying out footer blocks in a responsive grid.

    Args:
        footer_items (dict[str, list[str | Component]]): Mapping of footer
            block headings to their list of elements.
    """

    def on_create(self) -> None:
        super().on_create()

        # Base grid layout
        self.id = self.kwargs.get("id", "footer-items")
        self.klass = "footer-items"
        self.style.update({
            "gap": "32px",
            "padding": Theme.current.padding,
            "flex-wrap": "wrap",
        })

        # Build one block per configured heading
        self.add_children(self.build_blocks())

    def build_blocks(self) -> list[FooterBlock]:
        """
        Builds one FooterBlock per configured heading.

        Returns:
            List of FooterBlock components.
        """
        blocks = []

        for heading, elements in self.kwargs.get("footer_items", {}).items():
            block_id = f"footer-block-{heading.lower().replace(' ', '-')}"
            blocks.append(
                FooterBlock(id=block_id, heading=heading, elements=elements)
            )

        return blocks


class Footer(InnerComponent):
    """
    Premium, flexible site footer.

    Args:
        footer_items (dict[str, list[str]]):
            Mapping of footer block headings to their list of html components.
        
        social_links (list[dict], optional):
            See `SocialLinks` for shape.
        
        tagline (str, optional):
            Short line shown above the footer blocks.
        
        copyright (str, optional):
            Copyright text. Defaults to a generated "&copy; <year> <site name>.
            All rights reserved." string built from central site metadata.
        
        show_made_with_duck (bool):
            Whether to show the "made with Duck" badge. Defaults to True.
        
        accent (str):
            Accent color for the top divider glow. Defaults to Theme.current.accent_color.

    Template Usage:

    ```django
    {% Footer %}
        tagline = "Discover what's happening tonight, across Zimbabwe.",
        footer_items = {
            "Company": [
                '{% Link %}text="About Us", url="{% resolve "about" fallback_url="#" %}"{% endLink %}',
                '{% Link %}text="Contact Us", url="{% resolve "contact" fallback_url="#" %}"{% endLink %}',
            ],
            "Legal": [
                '{% Link %}text="Privacy Policy", url="{% resolve "privacy" fallback_url="#" %}"{% endLink %}',
                '{% Link %}text="Terms & Conditions", url="{% resolve "tos" fallback_url="#" %}"{% endLink %}',
            ],
        },
        social_links = [
            {"platform": "instagram", "url": "https://instagram.com/duckframework"},
            {"platform": "twitter", "url": "https://twitter.com/duckframework"},
        ],
    {% endFooter %}
    ```
    """

    def get_element(self) -> str:
        return "footer"

    def on_create(self) -> None:
        super().on_create()

        # Base footer styling
        self.id = self.kwargs.get("id", "site-footer")
        self.klass = "site-footer"
        self.style.update({
            "width": "100%",
            "font-size": "0.85rem",
            "position": "relative",
            "padding-top": Theme.current.padding,
            "background": self.kwargs.get(
                "background",
                "linear-gradient(180deg, rgba(10, 10, 16, 0.0) 0%, "
                "rgba(10, 10, 16, 0.97) 18%, #0a0a10 100%)",
            ),
        })

        # Optional tagline above the footer columns
        if self.kwargs.get("tagline"):
            self.add_child(self.build_tagline())

        # Footer columns
        self.add_child(
            FooterItems(footer_items=self.kwargs.get("footer_items", {}))
        )

        # Bottom bar: badge, social links, copyright
        self.add_child(self.build_bottom_bar())

        # Scoped stylesheet
        self.add_child(self.build_style())

    def build_tagline(self) -> Component:
        """
        Builds the short tagline paragraph shown above the footer columns.

        Returns:
            A Component rendering the tagline text.
        """
        return to_component(
            self.kwargs.get("tagline"),
            tag="p",
            klass="footer-tagline",
            style={
                "padding": f"{Theme.current.padding} {Theme.current.padding} 0",
                "color": "rgba(255, 255, 255, 0.5)",
                "max-width": "480px",
            },
        )

    def build_bottom_bar(self) -> FlexContainer:
        """
        Assembles the badge, social links, and copyright row.

        Returns:
            A FlexContainer holding the footer's bottom bar content.
        """
        children = []

        # Made-with-Duck badge
        if self.kwargs.get("show_made_with_duck", True):
            children.append(self.build_duck_link())

        # Social icon row
        if self.kwargs.get("social_links"):
            children.append(SocialLinks(social_links=self.kwargs["social_links"]))

        # Copyright text
        children.append(self.build_copyright())

        return FlexContainer(
            id="footer-bottom-bar",
            klass="footer-bottom-bar",
            style={
                "flex-direction": "column",
                "justify-content": "space-between",
                "align-items": "center",
                "flex-wrap": "wrap",
                "gap": "12px",
                "padding": Theme.current.padding,
                "border-top": "1px solid rgba(255, 255, 255, 0.08)",
                "margin-top": "8px",
            },
            children=children,
        )

    def build_duck_link(self) -> Link:
        """
        Builds the "made with Duck" badge, pointing to the right domain.

        Returns:
            A Link component wrapping the MadeWithDuck badge.
        """
        is_duck_site = Meta.get_metadata("DUCK_SERVER_DOMAIN") == "duckframework.com"

        return Link(
            id="footer-duck-link",
            url=GITHUB_URL if is_duck_site else DUCK_URL,
            children=[MadeWithDuck()],
        )

    def build_copyright(self) -> Component:
        """
        Builds the copyright line, defaulting to generated site metadata.

        Returns:
            A Component rendering the copyright text.
        """
        # Fall back to a generic label when no site name is configured
        site_name = Meta.get_metadata("SITE_NAME")
        
        if not site_name:
            site_name = "This site"

        default_text = f"&copy; {datetime.now().year} {site_name}. All rights reserved."
        copyright_text = self.kwargs.get("copyright") or default_text

        return to_component(
            copyright_text,
            tag="p",
            klass="footer-copyright",
            style={
                "color": "rgba(255, 255, 255, 0.45)",
                "margin": "0",
                "text-align": "center",
            },
        )

    def build_style(self) -> Style:
        """
        Builds the footer's scoped and responsive css.

        Returns:
            A Style component containing the footer's stylesheet.
        """
        accent = self.kwargs.get("accent", Theme.current.accent_color)

        return Style(
            inner_html=f"""
                footer.site-footer::before {{
                    content: "";
                    position: absolute;
                    top: 0;
                    left: 50%;
                    transform: translateX(-50%);
                    width: 60%;
                    height: 1px;
                    background: radial-gradient(
                        ellipse at center, {accent} 0%, transparent 75%
                    );
                    opacity: 0.5;
                }}

                footer .footer-social-icon {{
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    width: 36px;
                    height: 36px;
                    border-radius: 50%;
                    background: rgba(255, 255, 255, 0.06);
                    color: rgba(255, 255, 255, 0.7);
                    transition: background 0.2s ease, color 0.2s ease, transform 0.2s ease;
                }}

                footer .footer-social-icon:hover {{
                    background: {accent};
                    color: #0a0a10;
                    transform: translateY(-2px);
                }}

                footer .footer-heading {{
                    font-weight: 600;
                }}

                @media (max-width: 768px) {{
                    footer.site-footer {{
                        font-size: 0.8rem;
                    }}

                    footer .footer-items {{
                        gap: 24px;
                    }}
                    
                    footer .footer-bottom-bar {{
                        flex-direction: column;
                        align-items: flex-start;
                        text-align: left;
                    }}

                    footer #proudly-duck-logo {{
                        width: 25px;
                        height: 25px;
                        margin-top: 5px;
                        margin-bottom: 5px;
                    }}
                }}
            """
        )


class PlainFooter(InnerComponent):
    """
    Just plain simple footer without anything.
    """
    
    def get_element(self):
        return "footer"
