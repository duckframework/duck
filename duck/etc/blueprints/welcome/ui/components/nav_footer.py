"""
NavBar and Footer components — top navigation and bottom footer
for the welcome page, both linking to the official Duck Framework
properties. The navbar also surfaces a link to the project's
dashboard when one is registered.
"""

from duck.html.components import InnerComponent
from duck.html.components.container import Container


def resolve_dashboard_url() -> str | None:
    """
    Attempts to resolve the project's dashboard URL.

    Returns:
        The resolved dashboard URL, or None if no dashboard route
        is registered in the current project.
    """
    from duck.shortcuts import resolve
    return resolve("dashboard.index", fallback_url="") or None


class NavBar(InnerComponent):
    """
    Sticky, glass-effect top navigation bar with brand mark and links.

    Links to the official site and docs open in a new tab. When the
    project registers a dashboard route, a "Dashboard" link is shown
    as the primary call to action.
    """

    def get_element(self) -> str:
        """
        Returns:
            The HTML element tag for this component.
        """
        return "nav"

    def on_create(self) -> None:
        """
        Builds the brand mark, navigation links, hamburger button,
        and the inline toggle script.
        """
        super().on_create()
        self.props["class"] = "wc-nav"

        self.add_children([
            self.build_brand(),
            self.build_links(),
            self.build_burger(),
            self.build_toggle_script(),
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
        Returns the navigation link list — shown inline on desktop and
        as a full-width drawer on mobile.

        Returns:
            A Container holding the navigation link anchors.
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

        # Append a highlighted dashboard link when one is registered
        dashboard_url = resolve_dashboard_url()
        if dashboard_url:
            links_html += (
                f'<a class="wc-nav-link wc-nav-link-cta" href="{dashboard_url}">'
                f'Dashboard {self.arrow_icon()}</a>'
            )

        return Container(
            id="wc-nav-links",
            klass="wc-nav-links",
            inner_html=links_html,
        )

    def build_burger(self) -> Container:
        """
        Returns the hamburger button shown only on mobile.

        Clicking it toggles the ``wc-nav-open`` class on the nav,
        which slides the link drawer into view and animates the
        burger bars into an X.

        Returns:
            A Container rendered as a <button> element.
        """
        return Container(
            element="button",
            klass="wc-nav-burger",
            props={
                "id": "wc-nav-burger",
                "aria-label": "Toggle navigation",
                "aria-expanded": "false",
                "aria-controls": "wc-nav-links",
                "type": "button",
            },
            inner_html=(
                '<span class="wc-burger-bar"></span>'
                '<span class="wc-burger-bar"></span>'
                '<span class="wc-burger-bar"></span>'
            ),
        )

    def build_toggle_script(self) -> Container:
        """
        Returns an inline script that wires the burger button toggle.

        The script is intentionally tiny — it just flips the
        ``wc-nav-open`` class and syncs ``aria-expanded``. All visual
        logic lives in CSS.

        Returns:
            A Container rendered as a <script> element.
        """
        return Container(
            element="script",
            inner_html=(
                "(function(){"
                "var btn=document.getElementById('wc-nav-burger');"
                "var nav=btn&&btn.closest('.wc-nav');"
                "if(!btn||!nav)return;"
                "btn.addEventListener('click',function(){"
                "var open=nav.classList.toggle('wc-nav-open');"
                "btn.setAttribute('aria-expanded',open);"
                "});"
                # Close the drawer when any link inside it is tapped
                "nav.querySelectorAll('.wc-nav-link').forEach(function(a){"
                "a.addEventListener('click',function(){"
                "nav.classList.remove('wc-nav-open');"
                "btn.setAttribute('aria-expanded','false');"
                "});"
                "});"
                "})();"
            ),
        )

    def arrow_icon(self) -> str:
        """
        Returns an inline SVG arrow-right icon for the dashboard link.

        Returns:
            SVG string.
        """
        return (
            '<svg width="11" height="11" viewBox="0 0 13 13" fill="none" '
            'xmlns="http://www.w3.org/2000/svg" style="flex-shrink:0;">'
            '<path d="M2.5 6.5h8M7 3l3.5 3.5L7 10" stroke="currentColor" '
            'stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>'
            '</svg>'
        )


class Footer(InnerComponent):
    """
    Bottom footer with brand attribution and quick links.

    Mirrors the navbar links so they remain reachable after
    scrolling through the full page, and includes the dashboard
    link when one is registered.
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
        Returns the row of footer links, including a dashboard link
        when one is available for this project.

        Returns:
            A Container holding the footer link anchors.
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

        # Append the dashboard link when one is registered
        dashboard_url = resolve_dashboard_url()
        if dashboard_url:
            links_html += f'<a class="wc-footer-link" href="{dashboard_url}">Dashboard</a>'

        return Container(klass="wc-footer-links", inner_html=links_html)
