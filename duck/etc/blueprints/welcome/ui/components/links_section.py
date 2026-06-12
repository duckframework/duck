"""
LinksSection component — three large link cards pointing to the
official Duck Framework site, documentation, and contribution page.
"""

from duck.html.components import InnerComponent
from duck.html.components.container import Container


class LinksSection(InnerComponent):
    """
    Renders the three primary outbound links as interactive cards.

    Each card has a colored ambient glow on hover and an arrow that
    shifts on hover to suggest navigation.
    """

    # Link definitions — (icon, title, desc, url, accent_color, glow_color)
    LINKS = [
        (
            "🌐",
            "Official Site",
            "Explore the Duck Framework homepage — overview, showcase, "
            "and the latest framework news and releases.",
            "https://duckframework.com",
            "#F5A623",
            "rgba(245,166,35,0.08)",
        ),
        (
            "📚",
            "Documentation",
            "Full guides covering routing, components, Lively, "
            "authentication, caching, blueprints, and Django integration.",
            "https://docs.duckframework.com",
            "#60A5FA",
            "rgba(96,165,250,0.08)",
        ),
        (
            "💛",
            "Contribute & Sponsor",
            "Help shape Duck Framework — open an issue, submit a PR, "
            "or support development directly through sponsorship.",
            "https://duckframework.com/contribute",
            "#4ADE80",
            "rgba(74,222,128,0.08)",
        ),
    ]

    def get_element(self) -> str:
        """
        Returns:
            The HTML element tag for this component.
        """
        return "div"

    def on_create(self) -> None:
        """
        Builds the section label and the three link cards.
        """
        super().on_create()
        self.props["class"] = "wc-links-section"

        self.add_children([
            self.build_link_card(icon, title, desc, url, accent, glow)
            for icon, title, desc, url, accent, glow in self.LINKS
        ])

    def build_link_card(
        self,
        icon: str,
        title: str,
        desc: str,
        url: str,
        accent: str,
        glow: str,
    ) -> Container:
        """
        Returns a single outbound link card.

        Args:
            icon: Emoji icon shown at the top of the card.
            title: Card heading text.
            desc: Short description of the destination.
            url: The external URL the card links to.
            accent: CSS color for the arrow and hover accent.
            glow: CSS rgba color for the radial hover glow.

        Returns:
            A Container rendered as an anchor element.
        """
        return Container(
            element="a",
            klass="wc-link-card",
            style={"--link-accent": accent, "--link-glow": glow},
            props={
                "href": url,
                "target": "_blank",
                "rel": "noopener noreferrer",
            },
            inner_html=(
                f'<span class="wc-link-icon">{icon}</span>'
                f'<span class="wc-link-title">{title}</span>'
                f'<span class="wc-link-desc">{desc}</span>'
                f'<span class="wc-link-arrow">Visit {self.arrow_icon()}</span>'
            ),
        )

    def arrow_icon(self) -> str:
        """
        Returns an inline SVG arrow icon for link cards.

        Returns:
            SVG string.
        """
        return (
            '<svg width="11" height="11" viewBox="0 0 11 11" fill="none" '
            'xmlns="http://www.w3.org/2000/svg" style="flex-shrink:0;">'
            '<path d="M2 9L9 2M9 2H4M9 2V7" stroke="currentColor" '
            'stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>'
            '</svg>'
        )
