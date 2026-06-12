"""
LatencyPanel component — displays latency percentile tiles and an
inline SVG sparkline chart of recent latency history.
"""

from duck.html.components import InnerComponent
from duck.html.components.container import Container

from ..components.theme import Theme


class LatencyPanel(InnerComponent):
    """
    Renders a panel with p50/p90/p95/p99 latency tiles and a sparkline.

    Props:
        data (dict): Output of services.get_latency_stats().
    """

    def get_element(self) -> str:
        """
        Returns:
            The HTML element tag for this component.
        """
        return "div"

    def on_create(self) -> None:
        """
        Builds the panel header, percentile grid, and sparkline.
        """
        super().on_create()

        data = self.kwargs.get("data", {})
        self.props["class"] = "db-panel"

        # Build the full panel layout
        self.add_children([
            self.build_header(),
            self.build_body(data),
        ])

    def build_header(self) -> Container:
        """
        Returns the panel header with title and avg latency label.

        Returns:
            A Container with the header row markup.
        """
        return Container(
            klass="db-panel-header",
            inner_html=(
                '<span class="db-panel-title">Latency</span>'
                '<span class="db-last-updated">milliseconds</span>'
            ),
        )

    def build_body(self, data: dict) -> Container:
        """
        Returns the panel body containing the percentile grid and sparkline.

        Args:
            data: Latency stats dict from the service layer.

        Returns:
            A Container wrapping both the grid and sparkline.
        """
        percentile_grid = self.build_percentile_grid(data)
        sparkline = self.build_sparkline(data.get("history", []))

        return Container(
            klass="db-panel-body db-sparkline-wrap",
            children=[percentile_grid, sparkline],
        )

    def build_percentile_grid(self, data: dict) -> Container:
        """
        Returns a grid of four latency percentile tiles.

        Args:
            data: Latency stats dict containing p50, p90, p95, p99 keys.

        Returns:
            A Container styled as the latency grid.
        """
        tiles_html = "".join([
            self.render_tile(label, data.get(key, 0))
            for label, key in [("P50", "p50"), ("P90", "p90"), ("P95", "p95"), ("P99", "p99")]
        ])
        return Container(klass="db-latency-grid", inner_html=tiles_html)

    def render_tile(self, label: str, value: int) -> str:
        """
        Returns the raw HTML string for one latency tile.

        Args:
            label: Percentile label, e.g. "P50".
            value: Latency value in milliseconds.

        Returns:
            HTML string for the tile div.
        """
        return (
            f'<div class="db-latency-tile">'
            f'<span class="db-latency-label">{label}</span>'
            f'<span class="db-latency-value">{value}'
            f'<span class="db-latency-unit"> ms</span></span>'
            f'</div>'
        )

    def build_sparkline(self, history: list) -> Container:
        """
        Returns an SVG sparkline chart from the latency history list.

        Args:
            history: List of latency integers representing recent measurements.

        Returns:
            A Container holding the inline SVG sparkline.
        """
        if not history:
            return Container(klass="db-sparkline")

        width = 400
        height = 56
        min_val = min(history)
        max_val = max(history) or 1
        span = max_val - min_val or 1

        # Compute (x, y) for each point
        points = []
        
        for i, val in enumerate(history):
            x = (i / (len(history) - 1)) * width if i > 0 else 0
            y = height - ((val - min_val) / span) * (height - 8) - 4
            points.append((x, y))

        polyline = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)

        # Build gradient fill polygon by closing the path
        fill_pts = polyline + f" {width:.1f},{height} 0,{height}"

        svg = (
            f'<svg class="db-sparkline" viewBox="0 0 {width} {height}" '
            f'preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">'
            f'<defs>'
            f'<linearGradient id="spark-grad" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0%" stop-color="{Theme.orange}" stop-opacity="0.25"/>'
            f'<stop offset="100%" stop-color="{Theme.orange}" stop-opacity="0"/>'
            f'</linearGradient>'
            f'</defs>'
            f'<polygon points="{fill_pts}" fill="url(#spark-grad)"/>'
            f'<polyline points="{polyline}" fill="none" '
            f'stroke="{Theme.orange}" stroke-width="1.5" stroke-linejoin="round" '
            f'stroke-linecap="round"/>'
            f'</svg>'
        )

        return Container(inner_html=svg)
