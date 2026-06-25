"""
Snackbar component for displaying brief messages at the top of the screen.
"""

from duck.html.components.container import FlexContainer
from duck.html.components.script import Script


SNACKBAR_SCRIPT = """
if (!window._snackbarTimers) window._snackbarTimers = new WeakMap();

function showSnackbar(snackbar, type, timeout) {
    const colors = {
        error: snackbar.dataset.errorColor,
        info: snackbar.dataset.infoColor,
        success: snackbar.dataset.successColor,
        warning: snackbar.dataset.warningColor,
    };

    const color = colors[type] || colors.info;

    if (color) {
        if (snackbar.dataset.variant === "glacier") {
            snackbar.style.borderColor = color;
            snackbar.style.color = color;
        } else {
            snackbar.style.background = color;
        }
    }

    const prevTimer = window._snackbarTimers.get(snackbar);
    if (prevTimer) {
        clearTimeout(prevTimer);
    }

    snackbar.style.display = "flex";
    snackbar.style.transform = "translateY(0)";
    snackbar.style.opacity = "1";

    if (typeof timeout === "undefined" || timeout === null) {
        timeout = Number(snackbar.dataset.timeout) || null;
    }

    if (timeout) {
        const timer = setTimeout(function() {
            hideSnackbar(snackbar);
            window._snackbarTimers.delete(snackbar);
        }, timeout);

        window._snackbarTimers.set(snackbar, timer);
    }
}

function hideSnackbar(snackbar) {
    snackbar.style.transform = "translateY(-100%)";
    snackbar.style.opacity = "0";

    function onTransitionEnd(event) {
        if (event.propertyName === "opacity") {
            snackbar.style.display = "none";
            snackbar.removeEventListener("transitionend", onTransitionEnd);
        }
    }

    snackbar.addEventListener("transitionend", onTransitionEnd);

    const prevTimer = window._snackbarTimers.get(snackbar);
    if (prevTimer) {
        clearTimeout(prevTimer);
        window._snackbarTimers.delete(snackbar);
    }
}
"""


class Snackbar(FlexContainer):
    """
    Snackbar component for showing brief notifications.
    """

    allowed_types = {"info", "success", "error", "warning"}
    allowed_variants = {"filled", "glacier"}

    def __init__(
        self,
        text: str | None = None,
        type: str = "info",
        variant: str = "filled",
        timeout: int | None = None,
        **kwargs,
    ):
        """
        Initialize the snackbar.

        Args:
            text: Snackbar message text.
            type: Snackbar type. Must be ``info``, ``success``, ``error``,
                or ``warning``.
            variant: Visual style. Must be ``filled`` (solid background) or
                ``glacier`` (frosted, outlined glass look).
            timeout: Auto-hide timeout in milliseconds.
            **kwargs: Additional component keyword arguments.

        Raises:
            ValueError: If the snackbar type or variant is invalid.
        """
        if type not in self.allowed_types:
            raise ValueError(
                f"Snackbar type must be one of {sorted(self.allowed_types)}."
            )

        if variant not in self.allowed_variants:
            raise ValueError(
                f"Snackbar variant must be one of {sorted(self.allowed_variants)}."
            )

        self.type = type
        self.variant = variant
        self.timeout = timeout
        super().__init__(text=text or "", **kwargs)

    def on_create(self) -> None:
        """
        Initialize and compose the snackbar.
        """
        super().on_create()

        # Snackbar state
        self.error_color = self.kwargs.get("error_color", "#ef4444")    # Tailwind red-500
        self.info_color = self.kwargs.get("info_color", "#3b82f6")      # Tailwind blue-500
        self.success_color = self.kwargs.get("success_color", "#22c55e") # Tailwind green-500
        self.warning_color = self.kwargs.get("warning_color", "#f59e0b") # Tailwind amber-500

        # Component setup
        self.color = "#222"
        self.klass = f"snackbar snackbar-{self.type} snackbar-{self.variant}"

        # Update props
        self.props.setdefault("id", "snackbar")
        self.props.update({
            "data-error-color": self.error_color,
            "data-info-color": self.info_color,
            "data-success-color": self.success_color,
            "data-warning-color": self.warning_color,
            "data-timeout": str(self.timeout or ""),
            "data-variant": self.variant,
        })

        # Update style
        self.style.setdefaults({
            "position": "fixed",
            "top": "0",
            "left": "0",
            "right": "0",
            "text-align": "center",
            "padding": "12px 4px",
            "z-index": "9999",
            "transition": "transform 0.3s, opacity 0.3s, background 0.3s, border-color 0.3s, color 0.3s",
            "transform": "translateY(-100%)",
            "opacity": "0",
            "display": "none",
            "backdrop-filter": "blur(20px)",
            "-webkit-backdrop-filter": "blur(20px)",
            "will-change": "transform, opacity",
            "flex-direction": "column",
            "justify-content": "center",
            "align-items": "center",
            "margin-bottom": "2px",
        })

        self._apply_variant_style()

        # Component children
        self.add_child(Script(inner_html=SNACKBAR_SCRIPT))

    # Public API

    def show(self) -> None:
        """
        Show the snackbar from Python.
        """
        self.style.update({
            "display": "flex",
            "transform": "translateY(0)",
            "opacity": "1",
        })

    def hide(self) -> None:
        """
        Hide the snackbar from Python.
        """
        self.style.update({
            "transform": "translateY(-100%)",
            "opacity": "0",
        })

    def set_type(self, type: str) -> None:
        """
        Set snackbar type and background color.

        Args:
            type: Snackbar type. Must be ``info``, ``success``, ``error``,
                or ``warning``.

        Raises:
            ValueError: If the snackbar type is invalid.
        """
        if type not in self.allowed_types:
            raise ValueError(
                f"Snackbar type must be one of {sorted(self.allowed_types)}."
            )

        self.type = type
        self.klass = f"snackbar snackbar-{self.type} snackbar-{self.variant}"
        self._apply_variant_style()

    def set_variant(self, variant: str) -> None:
        """
        Set the snackbar's visual variant.

        Args:
            variant: Visual style. Must be ``filled`` or ``glacier``.

        Raises:
            ValueError: If the variant is invalid.
        """
        if variant not in self.allowed_variants:
            raise ValueError(
                f"Snackbar variant must be one of {sorted(self.allowed_variants)}."
            )

        self.variant = variant
        self.klass = f"snackbar snackbar-{self.type} snackbar-{self.variant}"
        self.props["data-variant"] = variant
        self._apply_variant_style()

    def set_timeout(self, timeout: int | None) -> None:
        """
        Set the default JavaScript auto-hide timeout.

        Args:
            timeout: Auto-hide timeout in milliseconds, or ``None`` to disable.
        """
        self.timeout = timeout
        self.props["data-timeout"] = str(timeout or "")

    # Helpers

    def get_type_color(self, type: str) -> str:
        """
        Return the accent color for a snackbar type.

        Args:
            type: Snackbar type.

        Returns:
            The configured CSS color for the snackbar type.
        """
        return {
            "error": self.error_color,
            "info": self.info_color,
            "success": self.success_color,
            "warning": self.warning_color,
        }[type]

    def set_type_color(self, type: str, color: str) -> None:
        """
        Set the color for a snackbar type.

        Args:
            type: Snackbar type.
            color: CSS color value.

        Raises:
            ValueError: If the snackbar type is invalid.
        """
        if type not in self.allowed_types:
            raise ValueError(
                f"Snackbar type must be one of {sorted(self.allowed_types)}."
            )

        # Update the component color attribute
        attr_name = f"{type}_color"
        setattr(self, attr_name, color)

        # Update color in props
        self.props[f"data-{type}-color"] = color

        if self.type == type:
            self._apply_variant_style()

    def _apply_variant_style(self) -> None:
        """
        Apply the background/border/text styling for the current
        type + variant combination.
        """
        accent = self.get_type_color(self.type)

        if self.variant == "glacier":
            self.style.update({
                "background":  "rgba(255, 255, 255, 0.12)",
                "border": f"1px solid {accent}",
                "color": accent,
                "box-shadow": f"0 1px 12px 0 {accent}33",
            })
        else:
            self.style.update({
                "background": accent,
                "border": "none",
                "color": "#222",
                "box-shadow": "none",
            })
