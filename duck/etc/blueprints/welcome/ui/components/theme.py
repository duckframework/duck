"""
Centralized design tokens for the Duck Framework welcome blueprint.

All colors, typography, spacing, and animation values live here.
Components import from Theme — never hardcode raw values elsewhere.
"""


class Theme:
    """
    Design tokens for the welcome page UI.

    Token names are descriptive and unambiguous so changing a value
    here propagates consistently across every component.
    """

    # Background palette
    bg = "#080808"
    surface = "#101010"
    surface_2 = "#141414"
    surface_3 = "#0c0c0c"

    # Brand accent — Duck Framework orange
    orange = "#F5A623"
    orange_dim = "rgba(245, 166, 35, 0.08)"
    orange_glow = "rgba(245, 166, 35, 0.15)"
    orange_border = "rgba(245, 166, 35, 0.18)"

    # Status and accent palette
    green = "#4ADE80"
    green_dim = "rgba(74, 222, 128, 0.08)"
    blue = "#60A5FA"
    blue_dim = "rgba(96, 165, 250, 0.08)"
    purple = "#C084FC"
    purple_dim = "rgba(192, 132, 252, 0.08)"
    teal = "#34D399"

    # Text hierarchy
    text = "#E8E8E8"
    text_dim = "#A0A0A0"
    muted = "#555555"

    # Borders
    border = "rgba(255, 255, 255, 0.06)"
    border_subtle = "rgba(255, 255, 255, 0.03)"

    # Typography
    mono = "'JetBrains Mono', monospace"
    font = "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"

    # Shape
    radius_sm = "6px"
    radius = "10px"
    radius_lg = "14px"
    radius_xl = "20px"
