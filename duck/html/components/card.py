"""
Card component module.
"""
from duck.html.components.theme import Theme
from duck.html.components.container import FlexContainer
from duck.html.components.style import Style


class Card(FlexContainer):
    """
    Basic card component derived from flex container.

    Renders a centered, vertically-stacked card with a soft shadow and a
    subtle hover lift, suited for feature tiles, stat blocks, and similar
    content that needs equal visual weight.

    Args:
        bg_color (str): Optional card background override.
        border_color (str): Optional card border color override.
    """

    def on_create(self) -> None:
        super().on_create()

        # Base layout
        self.id = self.kwargs.get("id", "card")
        self.klass = "flex-card"
        
        # Update style
        self.style.update({
            "min-height": "100px",
            "flex-direction": "column",
            "align-items": "center",
            "justify-content": "center",
            "text-align": "center",
        })

        # Surface styling
        border_color = self.kwargs.get("border_color", "rgba(255, 255, 255, 0.08)")
        
        self.style.update({
            "padding": Theme.current.padding,
            "border-radius": Theme.current.border_radius,
            "background": self.kwargs.get("bg_color", "rgba(255, 255, 255, 0.03)"),
            "border": f"1px solid {border_color}",
            "box-shadow": "0 4px 12px rgba(0, 0, 0, 0.1)",
            "--card-border-color": border_color,
        })

        # Hover transition
        self.style.update({
            "transition": "transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease",
        })

        # Scoped hover behaviour
        self.add_child(self.build_style())

    def build_style(self) -> Style:
        """
        Builds the card's scoped hover styling.

        Reads the per-instance border color from the `--card-border-color`
        custom property set alongside the base styling, so multiple cards
        with different border colors don't stomp on each other's hover rule.

        Returns:
            A Style component containing the card's hover rule.
        """
        return Style(
            inner_html="""
                .flex-card:hover {
                    transform: translateY(-4px);
                    box-shadow: 0 10px 24px rgba(0, 0, 0, 0.18);
                    border-color: var(--card-border-color, rgba(255, 255, 255, 0.08));
                }
            """
        )
