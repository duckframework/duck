"""
DashboardPage — the root page for the Duck Framework server dashboard.

Wires all dashboard components together and drives live data refresh
via Lively WebSocket event bindings. Requires a valid JWT session —
unauthenticated requests are routed to LoginPage by the view layer.
"""
import asyncio

from datetime import datetime, timezone

from duck.html.components.page import Page
from duck.html.components.container import Container
from duck.html.components.button import Button
from duck.html.components.style import Style
from duck.shortcuts import static

from ...services import get_full_snapshot
from ...system_metrics import get_system_metrics
from ..components.topbar import DashboardTopbar
from ..components.stats_bar import StatsBar
from ..components.latency_panel import LatencyPanel
from ..components.errors_panel import ErrorsPanel
from ..components.methods_panel import MethodsPanel
from ..components.top_routes_panel import TopRoutesPanel
from ..components.logs_panel import LogsPanel
from ..components.server_info_panel import ServerInfoPanel
from ..components.system_metrics_panel import SystemMetricsPanel


class DashboardPage(Page):
    """
    Full-page server dashboard driven by Lively reactive updates.

    Fetches a complete data snapshot on initial load and on every
    refresh triggered by the topbar button. All panels re-render
    in-place without a full page reload. Requires JWT authentication —
    handled by the view layer before this page is instantiated.
    """
    async def on_dom_ready(self, _, __, ___, ws):
        """
        Event called on when DOM is ready.
        """
        refresh_interval = 3 * 1000
        script = f"setInterval(() => {{ document.getElementById('{self.topbar.refresh_btn.id}').click() }}, {refresh_interval});"
        await ws.execute_js(script)
        
    def on_create(self) -> None:
        """
        Sets up SEO, injects styles, fetches initial data, and builds layout.
        """
        super().on_create()

        self.set_title("Dashboard · Duck Framework")
        self.set_description("Live server state, request metrics, latency, errors, and logs.")
        self.set_accessibility(lang="en")
        self.set_robots("noindex, nofollow")

        # Inject dashboard stylesheet
        self.add_stylesheet(static("dashboard/css/dashboard.css"))

        # Fetch initial data snapshots
        snapshot = get_full_snapshot()
        sys_snapshot = get_system_metrics()

        # Build layout
        self.build_layout(snapshot, sys_snapshot)
        
        # Bind some document level event.
        self.document_bind("DOMContentLoaded", self.on_dom_ready, update_self=False)

    def build_layout(self, snapshot: dict, sys_snapshot: dict) -> None:
        """
        Constructs the full page layout from the provided data snapshots.

        Args:
            snapshot: Dict returned by services.get_full_snapshot().
            sys_snapshot: Dict returned by system_metrics.get_system_metrics().
        """
        # Topbar
        self.topbar = DashboardTopbar(last_updated=self.format_ts())

        # Stats bar
        self.stats_bar = StatsBar(data=snapshot["requests"])

        # Middle panels
        self.latency_panel = LatencyPanel(data=snapshot["latency"])
        self.errors_panel = ErrorsPanel(data=snapshot["errors"])
        self.methods_panel = MethodsPanel(data=snapshot["methods"])
        self.server_panel = ServerInfoPanel(data=snapshot["server"])

        # System metrics panel
        self.sys_panel = SystemMetricsPanel(data=sys_snapshot)

        # Bottom panels
        self.routes_panel = TopRoutesPanel(data=snapshot["routes"])
        self.logs_panel = LogsPanel(data=snapshot["logs"])
        
        self.shell = Container(
            klass="db-shell",
            children=[
                self.topbar,
                self.build_main_content(),
            ],
        )
        
        self.add_to_body(self.shell)
        
        # Bind refresh button — updates all panels
        self.topbar.refresh_btn.bind(
            "click",
            self.handle_refresh,
            update_self=False,
            update_targets=[
                self.shell
            ],
        )

    def build_main_content(self) -> Container:
        """
        Returns the scrollable main content area with all panel rows.

        Returns:
            A Container holding all panel rows inside db-main.
        """
        # Row 1: latency + errors
        row_1 = Container(
            klass="db-row db-row-2",
            children=[self.latency_panel, self.errors_panel],
        )

        # Row 2: methods + server info
        row_2 = Container(
            klass="db-row db-row-2",
            children=[self.methods_panel, self.server_panel],
        )

        # Row 3: system metrics — full width
        row_sys = Container(
            klass="db-row",
            children=[self.sys_panel],
        )

        # Row 4: routes — full width
        row_routes = Container(
            klass="db-row",
            children=[self.routes_panel],
        )

        # Row 5: logs — full width
        row_logs = Container(
            klass="db-row",
            children=[self.logs_panel],
        )

        return Container(
            klass="db-main",
            children=[
                self.stats_bar,
                row_1,
                row_2,
                row_sys,
                row_routes,
                row_logs,
            ],
        )

    async def handle_refresh(self, btn, event: str, value, ws) -> None:
        """
        Re-fetches all dashboard data and updates every panel in-place.

        Args:
            btn: The Button component that fired the event.
            event: The event name string.
            value: Event payload (unused).
            ws: The active LivelyWebSocketView instance.
        """
        await ws.execute_js(
            "document.getElementById('dashboard-refresh-btn')"
            ".classList.add('spinning')"
        )
        
        # Sleep a little for the spinner to be bit visible.
        await asyncio.sleep(.5)
        
        # Get snapshots
        snapshot = get_full_snapshot()
        sys_snapshot = get_system_metrics()
        
        # Update topbar timestamp
        self.topbar.last_updated_label.text = self.format_ts()

        # Rebuild each panel's inner content.
        self.stats_bar.clear_children()
        self.stats_bar.add_children(StatsBar(data=snapshot["requests"]).children, force_reparent=True)
        
        self.latency_panel.clear_children()
        self.latency_panel.add_children(LatencyPanel(data=snapshot["latency"]).children, force_reparent=True)
        
        self.errors_panel.clear_children()
        self.errors_panel.add_children(ErrorsPanel(data=snapshot["errors"]).children, force_reparent=True)

        self.methods_panel.clear_children()
        self.methods_panel.add_children(MethodsPanel(data=snapshot["methods"]).children, force_reparent=True)

        self.server_panel.clear_children()
        self.server_panel.add_children(ServerInfoPanel(data=snapshot["server"]).children, force_reparent=True)

        self.sys_panel.clear_children()
        self.sys_panel.add_children(SystemMetricsPanel(data=sys_snapshot).children, force_reparent=True)

        self.routes_panel.clear_children()
        self.routes_panel.add_children(TopRoutesPanel(data=snapshot["routes"]).children, force_reparent=True)

        self.logs_panel.clear_children()
        self.logs_panel.add_children(LogsPanel(data=snapshot["logs"]).children, force_reparent=True)

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
