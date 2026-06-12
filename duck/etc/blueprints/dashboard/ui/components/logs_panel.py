"""
LogsPanel component — renders a scrollable stream of recent server
log entries with level badges, timestamps, and source labels.
"""

from duck.html.components import InnerComponent
from duck.html.components.container import Container


class LogsPanel(InnerComponent):
    """
    Renders a scrollable log stream panel.

    Each entry shows a timestamp, level badge, source module,
    and the log message text.

    Props:
        data (list[dict]): Output of services.get_recent_logs().
    """

    def get_element(self) -> str:
        """
        Returns:
            The HTML element tag for this component.
        """
        return "div"

    def on_create(self) -> None:
        """
        Builds the logs panel with header and scrollable log list.
        """
        super().on_create()

        data = self.kwargs.get("data", [])
        self.props["class"] = "db-panel"

        self.add_children([
            self.build_header(data),
            self.build_body(data),
        ])

    def build_header(self, data: list) -> Container:
        """
        Returns the panel header with title and entry count.

        Args:
            data: List of log entry dicts.

        Returns:
            A Container with the header row markup.
        """
        count = len(data)
        return Container(
            klass="db-panel-header",
            inner_html=(
                '<span class="db-panel-title">Server Logs</span>'
                f'<span style="font-family:var(--mono);font-size:0.65rem;'
                f'color:var(--muted);">{count} entries</span>'
            ),
        )

    def build_body(self, data: list) -> Container:
        """
        Returns the scrollable log list body.

        Args:
            data: List of log entry dicts.

        Returns:
            A Container with the log entries rendered inside.
        """
        if not data:
            return Container(
                klass="db-panel-body",
                inner_html='<span class="db-loading">No log entries.</span>',
            )

        entries_html = "".join(self.render_entry(e) for e in data)
        return Container(
            klass="db-panel-body",
            inner_html=f'<div class="db-logs-list">{entries_html}</div>',
        )

    def render_entry(self, entry: dict) -> str:
        """
        Returns the HTML string for a single log entry row.

        Args:
            entry: Dict with keys: level, message, ts, source.

        Returns:
            HTML string for the log entry div.
        """
        level = entry.get("level", "INFO")
        message = entry.get("message", "")
        ts = entry.get("ts", "")
        source = entry.get("source", "")
        level_class = f"db-level-{level.lower()}"

        return (
            f'<div class="db-log-entry">'
            f'<span class="db-log-ts">{ts}</span>'
            f'<span class="db-log-level {level_class}">{level}</span>'
            f'<span class="db-log-source">{source}</span>'
            f'<span class="db-log-message">{message}</span>'
            f'</div>'
        )
