"""
DashboardPage — the root page for the Duck Framework server dashboard.

Wires all dashboard components together and drives live data refresh
via Lively WebSocket event bindings. All panel data is re-fetched from
the service layer on each refresh without a full page reload.
"""

from datetime import datetime, timezone

from duck.html.components.page import Page
from duck.html.components.container import Container, FlexContainer
from duck.html.components.script import Script
from duck.html.components.style import Style
from duck.shortcuts import static

from ...services import get_full_snapshot
from ..components.topbar import DashboardTopbar
from ..components.stats_bar import StatsBar
from ..components.latency_panel import LatencyPanel
from ..components.errors_panel import ErrorsPanel
from ..components.methods_panel import MethodsPanel
from ..components.top_routes_panel import TopRoutesPanel
from ..components.logs_panel import LogsPanel
from ..components.server_info_panel import ServerInfoPanel


class DashboardPage(Page):
    """
    Full-page server dashboard driven by Lively reactive updates.

    Fetches a complete data snapshot on initial load and on every
    refresh triggered by the topbar button. All panels re-render
    their inner content in-place without a full page reload.
    """

    def on_create(self) -> None:
        """
        Sets up SEO, injects styles, fetches initial data, and builds layout.
        """
        super().on_create()

        # SEO and page metadata
        self.set_title("Dashboard · Duck Framework")
        self.set_description("Live server state, request metrics, latency, errors, and logs.")
        self.set_favicon("/static/favicon.ico")
        self.set_accessibility(lang="en")

        # Inject dashboard stylesheet
        self.add_stylesheet(static("dashboard/css/dashboard.css"))

        # Fetch the initial full data snapshot
        snapshot = get_full_snapshot()

        # Build and store all panels so handlers can replace their content
        self.build_layout(snapshot)

    def build_layout(self, snapshot: dict) -> None:
        """
        Constructs the full page layout from the provided data snapshot.

        Args:
            snapshot: Dict returned by services.get_full_snapshot().
        """
        # Build topbar with current timestamp
        self.topbar = DashboardTopbar(
            last_updated=self.format_ts(),
        )

        # Build stats bar at the top
        self.stats_bar = StatsBar(data=snapshot["requests"])

        # Build middle-row panels
        self.latency_panel = LatencyPanel(data=snapshot["latency"])
        self.errors_panel = ErrorsPanel(data=snapshot["errors"])
        self.methods_panel = MethodsPanel(data=snapshot["methods"])
        self.server_panel = ServerInfoPanel(data=snapshot["server"])

        # Build bottom-row panels
        self.routes_panel = TopRoutesPanel(data=snapshot["routes"])
        self.logs_panel = LogsPanel(data=snapshot["logs"])

        # Bind the refresh button to the async data reload handler
        self.topbar.refresh_btn.bind(
            "click",
            self.handle_refresh,
            update_self=False,
            update_targets=[
                self.topbar,
                self.stats_bar,
                self.latency_panel,
                self.errors_panel,
                self.methods_panel,
                self.server_panel,
                self.routes_panel,
                self.logs_panel,
            ],
        )

        # Assemble the full page shell
        shell = Container(
            klass="db-shell",
            children=[
                self.topbar,
                self.build_main_content(),
            ],
        )

        self.add_to_body(shell)

    def build_main_content(self) -> Container:
        """
        Returns the scrollable main content area with all panel rows.

        Returns:
            A Container holding all panel rows inside db-main.
        """
        # Row 1 — latency + errors side by side
        row_latency_errors = Container(
            klass="db-row db-row-2",
            children=[self.latency_panel, self.errors_panel],
        )

        # Row 2 — methods + server info side by side
        row_methods_server = Container(
            klass="db-row db-row-2",
            children=[self.methods_panel, self.server_panel],
        )

        # Row 3 — routes table spanning full width
        row_routes = Container(
            klass="db-row",
            children=[self.routes_panel],
        )

        # Row 4 — logs spanning full width
        row_logs = Container(
            klass="db-row",
            children=[self.logs_panel],
        )

        return Container(
            klass="db-main",
            children=[
                self.stats_bar,
                row_latency_errors,
                row_methods_server,
                row_routes,
                row_logs,
            ],
        )

    async def handle_refresh(self, btn, event: str, value, ws) -> None:
        """
        Re-fetches all dashboard data and updates every panel in-place.

        Called when the topbar refresh button is clicked. Fetches a fresh
        snapshot from the service layer and pushes updated inner HTML to
        each panel over the Lively WebSocket connection.

        Args:
            btn: The Button component that fired the event.
            event: The event name string.
            value: Event payload (unused here).
            ws: The active LivelyWebSocketView instance.
        """
        # Add spinning class to the button while loading
        await ws.execute_js(
            "document.getElementById('dashboard-refresh-btn')"
            ".classList.add('spinning')"
        )

        # Fetch fresh data from the service layer
        snapshot = get_full_snapshot()

        # Update topbar timestamp
        self.topbar.last_updated_label.text = self.format_ts()

        # Rebuild each panel's inner content with fresh data
        self.stats_bar.clear_children()
        self.stats_bar.add_children(
            StatsBar(data=snapshot["requests"]).children
        )

        self.latency_panel.clear_children()
        self.latency_panel.add_children(
            LatencyPanel(data=snapshot["latency"]).children
        )

        self.errors_panel.clear_children()
        self.errors_panel.add_children(
            ErrorsPanel(data=snapshot["errors"]).children
        )

        self.methods_panel.clear_children()
        self.methods_panel.add_children(
            MethodsPanel(data=snapshot["methods"]).children
        )

        self.server_panel.clear_children()
        self.server_panel.add_children(
            ServerInfoPanel(data=snapshot["server"]).children
        )

        self.routes_panel.clear_children()
        self.routes_panel.add_children(
            TopRoutesPanel(data=snapshot["routes"]).children
        )

        self.logs_panel.clear_children()
        self.logs_panel.add_children(
            LogsPanel(data=snapshot["logs"]).children
        )

        # Remove spinning class once done
        await ws.execute_js(
            "document.getElementById('dashboard-refresh-btn')"
            ".classList.remove('spinning')"
        )

    def format_ts(self) -> str:
        """
        Returns the current UTC time formatted as a display string.

        Returns:
            A string like "Updated 14:32:07 UTC".
        """
        now = datetime.now(timezone.utc)
        return f"Updated {now.strftime('%H:%M:%S')} UTC"
