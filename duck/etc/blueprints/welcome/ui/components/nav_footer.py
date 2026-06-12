"""
NavBar and Footer components — top navigation and bottom footer
for the welcome page, both linking to the official Duck Framework
properties.
"""

from duck.html.components import InnerComponent
from duck.html.components.container import Container


class NavBar(InnerComponent):
    """
    Sticky-free top navigation bar with brand mark and external links.

    Links to the official site, docs, and contribute page open in
    a new tab.
    """

    def get_element(self) -> str:
        """
        Returns:
            The HTML element tag for this component.
        """
        return "nav"

    def on_create(self) -> None:
        """
        Builds the brand mark and navigation link row.
        """
        super().on_create()
        self.props["class"] = "wc-nav"

        self.add_children([
            self.build_brand(),
            self.build_links(),
        ])

    def build_brand(self) -> Container:
        """
        Returns the brand mark with animated pulse dot.

        Returns:
            A Container rendered as an anchor to the official site.
        """
        return Container(
            element="a",
            klass="wc-nav-brand",
            props={
                "href": "https://duckframework.com",
                "target": "_blank",
                "rel": "noopener noreferrer",
            },
            inner_html='<span class="wc-nav-dot"></span> Duck Framework',
        )

    def build_links(self) -> Container:
        """
        Returns the row of external navigation links.

        Returns:
            A Container holding three link anchors.
        """
        links = [
            ("Docs", "https://docs.duckframework.com"),
            ("Site", "https://duckframework.com"),
            ("Contribute", "https://duckframework.com/contribute"),
        ]
        links_html = "".join(
            f'<a class="wc-nav-link" href="{url}" target="_blank" '
            f'rel="noopener noreferrer">{label}</a>'
            for label, url in links
        )
        return Container(klass="wc-nav-links", inner_html=links_html)


class Footer(InnerComponent):
    """
    Bottom footer with brand attribution and quick links.

    Mirrors the navbar links so they remain reachable after
    scrolling through the full page.
    """

    def get_element(self) -> str:
        """
        Returns:
            The HTML element tag for this component.
        """
        return "footer"

    def on_create(self) -> None:
        """
        Builds the footer brand label and link row.
        """
        super().on_create()
        self.props["class"] = "wc-footer"

        self.add_children([
            self.build_brand(),
            self.build_links(),
        ])

    def build_brand(self) -> Container:
        """
        Returns the footer brand attribution text.

        Returns:
            A Container with the brand markup.
        """
        return Container(
            klass="wc-footer-brand",
            inner_html=(
                '<span class="wc-nav-dot"></span> '
                'Duck Framework &nbsp;·&nbsp; Built with Python'
            ),
        )

    def build_links(self) -> Container:
        """
        Returns the row of footer links.

        Returns:
            A Container holding three link anchors.
        """
        links = [
            ("Official Site", "https://duckframework.com"),
            ("Documentation", "https://docs.duckframework.com"),
            ("Contribute", "https://duckframework.com/contribute"),
        ]
        links_html = "".join(
            f'<a class="wc-footer-link" href="{url}" target="_blank" '
            f'rel="noopener noreferrer">{label}</a>'
            for label, url in links
        )
        return Container(klass="wc-footer-links", inner_html=links_html)
