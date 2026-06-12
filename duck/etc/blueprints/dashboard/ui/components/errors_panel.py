"""
ErrorsPanel component — displays a breakdown of HTTP error responses
by status code with proportional bar indicators.
"""

from duck.html.components import InnerComponent
from duck.html.components.container import Container


class ErrorsPanel(InnerComponent):
    """
    Renders error counts broken down by HTTP status code.

    Shows each status code as a row with a label, proportional
    fill bar, and numeric count.

    Props:
        data (list[dict]): Output of services.get_error_breakdown().
    """

    def get_element(self) -> str:
        """
        Returns:
            The HTML element tag for this component.
        """
        return "div"

    def on_create(self) -> None:
        """
        Builds the panel header and error rows.
        """
        super().on_create()

        data = self.kwargs.get("data", [])
        self.props["class"] = "db-panel"

        # Build full panel
        self.add_children([
            self.build_header(data),
            self.build_body(data),
        ])

    def build_header(self, data: list) -> Container:
        """
        Returns the panel header with title and total error count.

        Args:
            data: List of error breakdown dicts.

        Returns:
            A Container with header markup.
        """
        total = sum(e.get("count", 0) for e in data)
        return Container(
            klass="db-panel-header",
            inner_html=(
                '<span class="db-panel-title">Errors by Status</span>'
                f'<span class="db-stat-accent-red" style="font-family:var(--mono);'
                f'font-size:0.75rem;font-weight:700;">{total} total</span>'
            ),
        )

    def build_body(self, data: list) -> Container:
        """
        Returns the scrollable body containing all error rows.

        Args:
            data: List of error breakdown dicts.

        Returns:
            A Container with the rendered error rows.
        """
        if not data:
            return Container(
                klass="db-panel-body",
                inner_html='<span class="db-loading">No error data available.</span>',
            )

        max_count = max((e.get("count", 0) for e in data), default=1) or 1
        rows_html = "".join(
            self.render_row(entry, max_count) for entry in data
        )
        return Container(klass="db-panel-body", inner_html=rows_html)

    def render_row(self, entry: dict, max_count: int) -> str:
        """
        Returns the HTML string for a single error status row.

        Args:
            entry: Dict with keys: code, label, count.
            max_count: The highest count in the dataset for bar scaling.

        Returns:
            HTML string for the error row div.
        """
        code = entry.get("code", "???")
        label = entry.get("label", "Unknown")
        count = entry.get("count", 0)
        bar_pct = round((count / max_count) * 100) if max_count else 0

        return (
            f'<div class="db-error-row">'
            f'<span class="db-error-code">{code}</span>'
            f'<span class="db-error-label">{label}</span>'
            f'<div class="db-error-bar-wrap">'
            f'<div class="db-error-bar" style="width:{bar_pct}%"></div>'
            f'</div>'
            f'<span class="db-error-count">{count}</span>'
            f'</div>'
        )
