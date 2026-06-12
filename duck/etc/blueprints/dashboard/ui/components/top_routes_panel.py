"""
TopRoutesPanel component — renders a table of the most-hit routes
with their method, hit count, avg latency, and latency status.
"""

from duck.html.components import InnerComponent
from duck.html.components.container import Container


class TopRoutesPanel(InnerComponent):
    """
    Renders a styled table of top routes sorted by hit count.

    Props:
        data (list[dict]): Output of services.get_top_routes().
    """

    def get_element(self) -> str:
        """
        Returns:
            The HTML element tag for this component.
        """
        return "div"

    def on_create(self) -> None:
        """
        Builds the routes panel with header and table body.
        """
        super().on_create()

        data = self.kwargs.get("data", [])
        self.props["class"] = "db-panel"

        self.add_children([
            self.build_header(),
            self.build_body(data),
        ])

    def build_header(self) -> Container:
        """
        Returns the panel header with title.

        Returns:
            A Container with the header markup.
        """
        return Container(
            klass="db-panel-header",
            inner_html='<span class="db-panel-title">Top Routes</span>',
        )

    def build_body(self, data: list) -> Container:
        """
        Returns the panel body containing the routes table.

        Args:
            data: List of route stat dicts.

        Returns:
            A Container wrapping the routes table.
        """
        if not data:
            return Container(
                klass="db-panel-body",
                inner_html='<span class="db-loading">No route data available.</span>',
            )

        table_html = (
            '<table class="db-routes-table">'
            '<thead><tr>'
            '<th>Path</th>'
            '<th>Method</th>'
            '<th>Hits</th>'
            '<th>Avg ms</th>'
            '<th>Status</th>'
            '</tr></thead>'
            '<tbody>'
        )
        table_html += "".join(self.render_row(r) for r in data)
        table_html += "</tbody></table>"

        return Container(klass="db-panel-body", inner_html=table_html)

    def render_row(self, route: dict) -> str:
        """
        Returns the HTML string for one route table row.

        Args:
            route: Dict with keys: path, method, hits, avg_ms, status.

        Returns:
            HTML string for the table row.
        """
        path = route.get("path", "/")
        method = route.get("method", "GET")
        hits = route.get("hits", 0)
        avg_ms = route.get("avg_ms", 0)
        status = route.get("status", "ok")
        css_key = method.lower()
        status_class = f"db-route-status-{status}"
        status_label = "● ok" if status == "ok" else "▲ slow"

        return (
            f'<tr>'
            f'<td class="db-route-path">{path}</td>'
            f'<td><span class="db-method-badge db-m-{css_key}">{method}</span></td>'
            f'<td>{hits:,}</td>'
            f'<td>{avg_ms} ms</td>'
            f'<td class="{status_class}">{status_label}</td>'
            f'</tr>'
        )
