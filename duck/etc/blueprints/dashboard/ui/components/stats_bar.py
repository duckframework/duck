"""
StatsBar component — top row of KPI tiles showing request totals,
success rate, error count, and requests per minute.
"""

from duck.html.components import InnerComponent
from duck.html.components.container import FlexContainer, Container

from ..components.theme import Theme


class StatsBar(InnerComponent):
    """
    Renders four stat tiles in a horizontal grid row.

    Displays total requests, success rate, error count, and
    requests per minute sourced from the request stats snapshot.

    Props:
        data (dict): Output of services.get_request_stats().
    """

    def get_element(self) -> str:
        """
        Returns:
            The HTML element tag for this component.
        """
        return "div"

    def on_create(self) -> None:
        """
        Builds the four KPI tiles from the provided stats data.
        """
        super().on_create()

        data = self.kwargs.get("data", {})

        # Apply stats bar grid layout
        self.props["class"] = "db-stats-bar"

        # Build each tile and add to the bar
        self.add_children([
            self.build_tile(
                label="Total Requests",
                value=f"{data.get('total', 0):,}",
                sub=f"{data.get('per_minute', 0)} / min",
                accent="db-stat-accent-blue",
            ),
            self.build_tile(
                label="Success Rate",
                value=f"{data.get('success_rate', 0)}%",
                sub=f"{data.get('success', 0):,} successful",
                accent="db-stat-accent-green",
            ),
            self.build_tile(
                label="Errors",
                value=f"{data.get('errors', 0):,}",
                sub="4xx + 5xx responses",
                accent="db-stat-accent-red",
            ),
            self.build_tile(
                label="Req / Min",
                value=str(data.get("per_minute", 0)),
                sub="current throughput",
                accent="db-stat-accent-orange",
            ),
        ])

    def build_tile(self, label: str, value: str, sub: str, accent: str) -> Container:
        """
        Builds a single KPI tile with label, large value, and subtitle.

        Args:
            label: Short uppercase label shown above the value.
            value: The primary metric string displayed prominently.
            sub: Smaller supporting text below the value.
            accent: CSS class name for the value color accent.

        Returns:
            A Container component styled as a stat tile.
        """
        return Container(
            klass="db-stat-tile",
            inner_html=(
                f'<span class="db-stat-label">{label}</span>'
                f'<span class="db-stat-value {accent}">{value}</span>'
                f'<span class="db-stat-sub">{sub}</span>'
            ),
        )
