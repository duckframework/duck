"""
DashboardTopbar component — sticky top navigation bar for the dashboard.

Displays the Duck Framework brand, a live server status pill, a
last-updated timestamp, a refresh button, and a logout link.
The refresh button triggers a Lively data reload over WebSocket.
"""

from duck.html.components import InnerComponent
from duck.html.components.container import Container
from duck.html.components.button import Button
from duck.html.components.link import Link
from duck.shortcuts import resolve


class DashboardTopbar(InnerComponent):
    """
    Renders the dashboard sticky topbar.

    The refresh button fires a "click" event handled by DashboardPage
    which re-fetches all panel data over the Lively WebSocket connection.

    Props:
        last_updated (str): Formatted timestamp string shown in the bar.
    """

    def get_element(self) -> str:
        """
        Returns:
            The HTML element tag for this component.
        """
        return "div"

    def on_create(self) -> None:
        """
        Builds the topbar with brand, status pill, timestamp, refresh, and logout.
        """
        super().on_create()

        self.props["class"] = "db-topbar"

        # Store last_updated label so Lively can sync it after refresh
        self.last_updated_label = Container(
            klass="db-last-updated",
            text=self.kwargs.get("last_updated", "—"),
        )

        # Build refresh button — handler bound in DashboardPage
        self.refresh_btn = Button(
            id="dashboard-refresh-btn",
            klass="db-refresh-btn",
            inner_html=self.refresh_icon() + " Refresh",
        )

        # Assemble left brand and right action area
        self.add_children([
            self.build_brand(),
            self.build_actions(),
        ])

    def build_brand(self) -> Container:
        return Container(
            klass="db-brand",
            inner_html=(
                '<span class="db-brand-dot"></span>'
                'Duck &nbsp;<span style="color:var(--muted);font-weight:400;">/</span>'
                '&nbsp; Dashboard'
            ),
        )

    def build_actions(self) -> Container:
        """
        Returns the right-side action area with status pill, timestamp,
        refresh button, and logout link.

        Returns:
            A Container holding the action widgets.
        """
        status_pill = Container(
            klass="db-status-pill",
            inner_html='<span class="db-status-pill-dot"></span> Running',
        )

        # Resolve the logout URL from the blueprint route name
        logout_url = resolve("dashboard.logout")
        logout_link = Link(
            url=logout_url,
            text="Logout",
            klass="db-logout-link",
        )

        return Container(
            klass="db-topbar-right",
            children=[
                status_pill,
                self.last_updated_label,
                self.refresh_btn,
                logout_link,
            ],
        )

    def refresh_icon(self) -> str:
        """
        Returns the SVG markup for the refresh icon.

        Returns:
            An inline SVG string.
        """
        return (
            '<svg width="12" height="12" viewBox="0 0 12 12" fill="none" '
            'xmlns="http://www.w3.org/2000/svg" style="flex-shrink:0;">'
            '<path d="M10 6A4 4 0 1 1 6 2a4 4 0 0 1 2.83 1.17L10 2v4H6l1.5-1.5" '
            'stroke="currentColor" stroke-width="1.2" stroke-linecap="round" '
            'stroke-linejoin="round"/>'
            '</svg>'
        )
