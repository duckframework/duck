"""
FeaturesGrid component — a 3-column grid of feature highlight cards.

Each card has an animated floating emoji icon, a title, and a
short description. A colored bottom border animates in on hover.
"""

from duck.html.components import InnerComponent
from duck.html.components.container import Container


class FeaturesGrid(InnerComponent):
    """
    Renders a responsive grid of Duck Framework feature cards.

    Features are defined inline as a class-level constant so they are
    easy to update without touching layout logic.
    """

    # Feature definitions — (icon, title, description, css_color, delay)
    FEATURES = [
        (
            "🐍",
            "Pure Python UI",
            "Build your entire frontend in Python using the component tree. "
            "No templates, no JavaScript files — Lively handles reactivity over WebSocket.",
            "#F5A623",
            "0s",
        ),
        (
            "⚡",
            "Lively WebSocket",
            "Reactive UI updates pushed from server to client over a persistent "
            "WebSocket connection. Patch only what changed — no full page reloads.",
            "#60A5FA",
            "0.08s",
        ),
        (
            "🧩",
            "Component System",
            "Composable, reusable components with props, styles, and lifecycle "
            "hooks. Build once, drop anywhere — the same mental model as React, "
            "but in Python.",
            "#4ADE80",
            "0.16s",
        ),
        (
            "🔌",
            "Django Integration",
            "Use Django's ORM, auth, admin, and apps alongside Duck's async "
            "server. Set USE_DJANGO=True and both frameworks collaborate seamlessly.",
            "#C084FC",
            "0.24s",
        ),
        (
            "📦",
            "Blueprint System",
            "Package features as self-contained blueprints with their own routes, "
            "views, components, static files, and templates. Drop them in and register.",
            "#34D399",
            "0.32s",
        ),
        (
            "🔒",
            "Auth & Sessions",
            "JWT-based authentication with configurable cookie or header transport, "
            "refresh token rotation, and a session middleware that just works.",
            "#F87171",
            "0.4s",
        ),
    ]

    def get_element(self) -> str:
        """
        Returns:
            The HTML element tag for this component.
        """
        return "div"

    def on_create(self) -> None:
        """
        Builds the full features grid with all feature cards.
        """
        super().on_create()
        self.props["class"] = "wc-features"

        self.add_children([
            self.build_card(icon, title, desc, color, delay)
            for icon, title, desc, color, delay in self.FEATURES
        ])

    def build_card(
        self,
        icon: str,
        title: str,
        desc: str,
        color: str,
        delay: str,
    ) -> Container:
        """
        Returns a single feature card container.

        Args:
            icon: Emoji character shown as the card icon.
            title: Short feature title.
            desc: One or two sentence feature description.
            color: CSS color string for the hover bottom border.
            delay: CSS animation-delay string for staggered entrance.

        Returns:
            A Container styled as a feature card.
        """
        return Container(
            klass="wc-feature-card",
            style={"--feature-color": color, "animation-delay": delay},
            inner_html=(
                f'<span class="wc-feature-icon" style="--icon-delay:{delay};">{icon}</span>'
                f'<span class="wc-feature-title">{title}</span>'
                f'<span class="wc-feature-desc">{desc}</span>'
            ),
        )
