"""
MethodsPanel component — shows request volume broken down by HTTP method
with color-coded badges and proportional fill bars.
"""

from duck.html.components import InnerComponent
from duck.html.components.container import Container


class MethodsPanel(InnerComponent):
    """
    Renders per-method request counts with color-coded badges and bars.

    Props:
        data (list[dict]): Output of services.get_method_breakdown().
    """

    def get_element(self) -> str:
        """
        Returns:
            The HTML element tag for this component.
        """
        return "div"

    def on_create(self) -> None:
        """
        Builds the methods panel with header and method rows.
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
        Returns the panel header row.

        Returns:
            A Container with the panel title.
        """
        return Container(
            klass="db-panel-header",
            inner_html='<span class="db-panel-title">Requests by Method</span>',
        )

    def build_body(self, data: list) -> Container:
        """
        Returns the body containing all method rows.

        Args:
            data: List of method breakdown dicts.

        Returns:
            A Container with rendered method rows.
        """
        if not data:
            return Container(
                klass="db-panel-body",
                inner_html='<span class="db-loading">No method data available.</span>',
            )

        rows_html = "".join(self.render_row(entry) for entry in data)
        return Container(klass="db-panel-body", inner_html=rows_html)

    def render_row(self, entry: dict) -> str:
        """
        Returns the HTML string for one method breakdown row.

        Args:
            entry: Dict with keys: method (str), count (int), percent (float).

        Returns:
            HTML string for the method row div.
        """
        method = entry.get("method", "GET")
        count = entry.get("count", 0)
        pct = entry.get("percent", 0.0)
        css_key = method.lower()

        return (
            f'<div class="db-method-row">'
            f'<span class="db-method-badge db-m-{css_key}">{method}</span>'
            f'<div class="db-method-bar-wrap">'
            f'<div class="db-method-bar db-bar-{css_key}" style="width:{pct}%"></div>'
            f'</div>'
            f'<span class="db-method-pct">{count:,}</span>'
            f'</div>'
        )
