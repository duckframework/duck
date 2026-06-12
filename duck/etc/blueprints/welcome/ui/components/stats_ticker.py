"""
StatsTicker component — a horizontal row of animated count-up stats
displayed between the hero and features sections.
"""

from duck.html.components import InnerComponent
from duck.html.components.container import Container


class StatsTicker(InnerComponent):
    """
    Displays key framework stats with count-up animation on scroll.

    Stats are hardcoded marketing figures. They animate from zero
    on first viewport entry via IntersectionObserver in JS.
    """

    # Stats data — label, final value, suffix
    STATS = [
        ("Pure Python", "100", "%"),
        ("Built-in Components", "40", "+"),
        ("Lines to Hello World", "5", ""),
        ("Lively WebSocket UI", "1", "x"),
    ]

    def get_element(self) -> str:
        """
        Returns:
            The HTML element tag for this component.
        """
        return "div"

    def on_create(self) -> None:
        """
        Builds the stats ticker row with dividers between items.
        """
        super().on_create()
        self.props["class"] = "wc-stats-ticker"
        self.props["id"] = "wc-stats-ticker"

        items = []
        for i, (label, value, suffix) in enumerate(self.STATS):
            items.append(self.build_stat(label, value, suffix))
            if i < len(self.STATS) - 1:
                items.append(Container(klass="wc-stat-divider"))

        self.add_children(items)

    def build_stat(self, label: str, value: str, suffix: str) -> Container:
        """
        Returns a single stat column with number and label.

        Args:
            label: Descriptive label shown below the number.
            value: The numeric target for the count-up animation.
            suffix: Optional character appended after the number (%, +, etc.).

        Returns:
            A Container styled as a stat item.
        """
        return Container(
            klass="wc-stat-item",
            inner_html=(
                f'<span class="wc-stat-num" data-target="{value}" data-suffix="{suffix}">'
                f'0{suffix}</span>'
                f'<span class="wc-stat-label">{label}</span>'
            ),
        )
