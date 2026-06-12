"""
Centralized theme tokens for the Duck Framework dashboard blueprint.

All colors, spacing, typography, and radius values live here.
Components import from this module — never hardcode raw values.
"""


class Theme:
    """
    Design tokens for the dashboard UI.

    All values are expressed as CSS variable references where possible
    so they stay in sync with the base stylesheet injected by DashboardPage.
    """

    # Background palette
    bg = "#080808"
    surface = "#101010"
    surface_2 = "#141414"
    surface_3 = "#0c0c0c"

    # Brand accent
    orange = "#F5A623"
    orange_dim = "rgba(245, 166, 35, 0.08)"
    orange_border = "rgba(245, 166, 35, 0.18)"

    # Status colors
    green = "#4ADE80"
    green_dim = "rgba(74, 222, 128, 0.08)"
    green_border = "rgba(74, 222, 128, 0.2)"

    red = "#E05252"
    red_dim = "rgba(224, 82, 82, 0.07)"
    red_border = "rgba(224, 82, 82, 0.18)"

    blue = "#60A5FA"
    blue_dim = "rgba(96, 165, 250, 0.08)"
    blue_border = "rgba(96, 165, 250, 0.18)"

    purple = "#C084FC"
    purple_dim = "rgba(192, 132, 252, 0.08)"
    purple_border = "rgba(192, 132, 252, 0.2)"

    teal = "#34D399"
    teal_dim = "rgba(52, 211, 153, 0.08)"
    teal_border = "rgba(52, 211, 153, 0.2)"

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

    # HTTP method colors — used by method badges
    method_get = "#4ADE80"
    method_post = "#60A5FA"
    method_put = "#F5A623"
    method_patch = "#C084FC"
    method_delete = "#E05252"
    method_ws = "#34D399"
    method_head = "#A0A0A0"
    method_options = "#A0A0A0"
