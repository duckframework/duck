"""
HeroSection component — the opening hero block of the welcome page.

Renders the animated heading with gradient accent text, a typed
tagline, the pip install command card, and the primary CTA buttons.
"""

from duck.html.components import InnerComponent
from duck.html.components.container import Container


class HeroSection(InnerComponent):
    """
    Full hero block shown at the top of the welcome page.

    Contains the version pill, animated heading, tagline with
    typing cursor, install command copy card, and CTA buttons.
    """

    def get_element(self) -> str:
        """
        Returns:
            The HTML element tag for this component.
        """
        return "section"

    def on_create(self) -> None:
        """
        Builds all hero sub-blocks and assembles them into the section.
        """
        super().on_create()
        self.props["class"] = "wc-hero"

        self.add_children([
            self.build_version_pill(),
            self.build_heading(),
            self.build_tagline(),
            self.build_cta_row(),
            self.build_install_card(),
        ])

    def build_version_pill(self) -> Container:
        """
        Returns the animated orange version/status pill above the heading.

        Returns:
            A Container with the pill markup.
        """
        from duck.version import version
        
        return Container(
            klass="wc-version-pill",
            inner_html=(
                '<span class="wc-pill-dot"></span>'
                f'v{version} &nbsp;·&nbsp; Duck Framework'
            ),
        )

    def build_heading(self) -> Container:
        """
        Returns the primary hero heading with a shimmer gradient accent.

        Returns:
            A Container wrapping the h1 heading element.
        """
        return Container(
            element="h1",
            klass="wc-hero-heading",
            inner_html=(
                'Build web apps,<br>'
                '<span class="wc-accent">the Python way.</span>'
            ),
        )

    def build_tagline(self) -> Container:
        """
        Returns the typed tagline paragraph with blinking cursor.

        Returns:
            A Container with the tagline and cursor markup.
        """
        return Container(
            element="p",
            klass="wc-tagline",
            inner_html=(
                'A full-stack Python web framework with a reactive WebSocket-driven'
                ' UI system. Write your entire frontend in Python — no JavaScript'
                ' required.<span class="wc-typed-cursor"></span>'
            ),
        )

    def build_cta_row(self) -> Container:
        """
        Returns the row of primary and secondary CTA buttons.

        Returns:
            A Container with both buttons.
        """
        return Container(
            klass="wc-cta-row",
            inner_html=(
                '<a href="https://docs.duckframework.com" target="_blank" '
                'rel="noopener" class="wc-btn-primary">'
                + self.arrow_right_icon()
                + ' Get Started</a>'
                '<a href="https://duckframework.com" target="_blank" '
                'rel="noopener" class="wc-btn-ghost">'
                + self.globe_icon()
                + ' Official Site</a>'
            ),
        )

    def build_install_card(self) -> Container:
        """
        Returns the pip install command card with clipboard copy on click.

        Returns:
            A Container styled as the install card.
        """
        return Container(
            id="wc-install-card",
            klass="wc-install-card",
            inner_html=(
                '<span class="wc-install-prompt">$</span>'
                '<span class="wc-install-cmd">pip install duckframework</span>'
                '<span class="wc-install-copy" id="wc-copy-label">copy</span>'
            ),
        )

    def arrow_right_icon(self) -> str:
        """
        Returns an inline SVG arrow-right icon.

        Returns:
            SVG string.
        """
        return (
            '<svg width="13" height="13" viewBox="0 0 13 13" fill="none" '
            'xmlns="http://www.w3.org/2000/svg" style="flex-shrink:0;">'
            '<path d="M2.5 6.5h8M7 3l3.5 3.5L7 10" stroke="currentColor" '
            'stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>'
            '</svg>'
        )

    def globe_icon(self) -> str:
        """
        Returns an inline SVG globe icon.

        Returns:
            SVG string.
        """
        return (
            '<svg width="12" height="12" viewBox="0 0 12 12" fill="none" '
            'xmlns="http://www.w3.org/2000/svg" style="flex-shrink:0;">'
            '<circle cx="6" cy="6" r="4.5" stroke="currentColor" stroke-width="1.2"/>'
            '<path d="M6 1.5C6 1.5 4 3.5 4 6s2 4.5 2 4.5M6 1.5C6 1.5 8 3.5 8 6s-2 4.5-2 4.5'
            'M1.5 6h9" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>'
            '</svg>'
        )
