"""
Snackbar component for displaying brief messages at the top of the screen.
"""

from duck.html.components.container import FlexContainer
from duck.html.components.script import Script


class Snackbar(FlexContainer):
    """
    Snackbar component to show notifications.
    """
    allowed_types = {"info", "success", "error"}

    def __init__(self, text: str = None, type: str = "info", timeout: int = None, **kwargs):
        self.type = type
        self.timeout = timeout
        assert self.type in self.allowed_types, f"Snackbar type must be one of {self.allowed_types}."
        super().__init__(text=text or "", **kwargs)
            
    def on_create(self):
        super().on_create()
        self.color = "#222"
        self.klass = f"snackbar snackbar-{self.type}"
        
        # set default colors for different types
        self.error_color = self.kwargs.get("error_color", "#f44336")
        self.info_color = self.kwargs.get("info_color", "#2196f3")
        self.success_color = self.kwargs.get("success_color", "#43a047")
        self.warning_color = self.kwargs.get("warning_color", "#FFB300")

        # Base styles for the snackbar
        self.style.setdefaults({
            "position": "fixed",
            "top": "0",
            "left": "0",
            "right": "0",
            "text-align": "center",
            "padding": "12px 4px",
            "z-index": "9999",
            "transition": "transform 0.3s, opacity 0.3s",
            "transform": "translateY(-100%)",
            "opacity": "0",
            "backdrop-filter": "blur(20px)",
            "-webkit-backdrop-filter": "blur(20px)",
            "will-change": "transform, opacity",
            "flex-direction": "column",
            "justify-content": "center",
            "align-items": "center",
            "margin-bottom": "2px",
        })

        bg = None
        
        if self.type == "error":
            bg = self.error_color
        
        elif self.type == "info":
           bg = self.info_color
        
        elif self.type == "warning":
            bg = self.warning_color

        else:
            bg = self.success_color
        
        # Set background color based on type
        self.style["background"] = bg
        
        # Add script to handle show/hide logic.
        self.script = Script(
            inner_html=f"""
            // Track the current auto-hide timer for the snackbar
            if (!window._snackbarTimers) window._snackbarTimers = new WeakMap();
        
            function showSnackbar(snackbar, type, timeout) {{
                let bg = null;
                
                // Set background color based on type
                if (type === "error") bg = "{self.error_color}";
                else if (type === "info") bg = "{self.info_color}";
                else if (type === "success") bg = "{self.success_color}";
                else if (type === "warning") bg = "{self.warning_color}";
                
                if (bg) {{
                    snackbar.style.background = bg;
                }}
        
                // Clear any previous auto-hide timer for this snackbar
                let prevTimer = window._snackbarTimers.get(snackbar);
                if (prevTimer) {{
                    clearTimeout(prevTimer);
                }}
        
                // Show the snackbar (reset transition if hiding)
                snackbar.style.display = "flex";
                snackbar.style.transform = "translateY(0)";
                snackbar.style.opacity = "1";
        
                if (typeof timeout === "undefined" || timeout === null) timeout = {self.timeout or "null"};
                if (timeout) {{
                    // Autohide: set new timer and track it
                    let timer = setTimeout(function() {{
                        hideSnackbar(snackbar);
                        window._snackbarTimers.delete(snackbar);
                    }}, timeout);
                    window._snackbarTimers.set(snackbar, timer);
                }}
            }}
        
            function hideSnackbar(snackbar) {{
                snackbar.style.transform = "translateY(-100%)";
                snackbar.style.opacity = "0";
        
                function onTransitionEnd(e) {{
                    if (e.propertyName === "opacity") {{
                        snackbar.style.display = "none";
                        snackbar.removeEventListener("transitionend", onTransitionEnd);
                    }}
                }}
                snackbar.addEventListener("transitionend", onTransitionEnd);
        
                // Clear any pending auto-hide timer
                let prevTimer = window._snackbarTimers.get(snackbar);
                if (prevTimer) {{
                    clearTimeout(prevTimer);
                    window._snackbarTimers.delete(snackbar);
                }}
            }}
            """
        )
        self.add_child(self.script)
        
    def show(self):
        """
        Show the snackbar.
        """
        self.style["transform"] = "translateY(0)"
        self.style["opacity"] = "1"
        
    def hide(self):
        """
        Hide the snackbar.
        """
        self.style["transform"] = "translateY(-100%)"
        self.style["opacity"] = "0"
