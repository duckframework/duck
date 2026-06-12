"""
ServerInfoPanel component — displays server health metadata including
uptime, Python version, OS platform, and worker count.
"""

from duck.html.components import InnerComponent
from duck.html.components.container import Container


class ServerInfoPanel(InnerComponent):
    """
    Renders a grid of server state key-value pairs.

    Props:
        data (dict): Output of services.get_server_state().
    """

    def get_element(self) -> str:
        """
        Returns:
            The HTML element tag for this component.
        """
        return "div"

    def on_create(self) -> None:
        """
        Builds the server info panel with header and metadata grid.
        """
        super().on_create()

        data = self.kwargs.get("data", {})
        self.props["class"] = "db-panel"

        self.add_children([
            self.build_header(data),
            self.build_body(data),
        ])

    def build_header(self, data: dict) -> Container:
        """
        Returns the panel header with status pill.

        Args:
            data: Server state dict.

        Returns:
            A Container with the header row markup.
        """
        status = data.get("status", "unknown")
        pill_class = "db-status-pill" if status == "running" else "db-status-pill-error"
        return Container(
            klass="db-panel-header",
            inner_html=(
                '<span class="db-panel-title">Server State</span>'
                f'<span class="{pill_class}">'
                f'<span class="db-status-pill-dot"></span>{status}'
                f'</span>'
            ),
        )

    def build_body(self, data: dict) -> Container:
        """
        Returns the panel body with a two-column metadata grid.

        Args:
            data: Server state dict.

        Returns:
            A Container with the server info grid.
        """
        items = [
            ("Uptime", f'<span class="db-uptime">{data.get("uptime", "—")}</span>'),
            ("Python", data.get("python_version", "—")),
            ("Platform", data.get("platform", "—")),
            ("Workers", str(data.get("worker_count", "—"))),
            ("Started", data.get("start_time", "—")),
            ("Status", data.get("status", "—").capitalize()),
        ]

        grid_html = "".join(
            f'<div class="db-server-item">'
            f'<span class="db-server-key">{key}</span>'
            f'<span class="db-server-val">{value}</span>'
            f'</div>'
            for key, value in items
        )

        return Container(
            klass="db-panel-body",
            inner_html=f'<div class="db-server-grid">{grid_html}</div>',
        )
