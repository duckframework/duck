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
        self.style["position"] = "fixed"
        self.style["top"] = "0"
        self.style["left"] = "0"
        self.style["right"] = "0"
        self.style["text-align"] = "center"
        self.style["padding"] = "12px 0"
        self.style["z-index"] = "9999"
        self.style["transition"] = "transform 0.3s, opacity 0.3s"
        self.style["transform"] = "translateY(-100%)"
        self.style["opacity"] = "0"
        self.style["backdrop-filter"] = self.style["-webkit-backdrop-filter"] = "blur(20px)"
        self.style["will-change"] = "transform, opacity"
        self.style["flex-direction"] = "column"
        self.style["justify-content"] = "center"
        self.style["align-items"] = "center"
        self.style["margin-bottom"] = "2px"
        
        bg = None
        
        if self.type == "error":
            bg = "#f44336"
        elif self.type == "info":
           bg = "#2196f3"
        else:
            bg = "#43a047"
        self.style["background"] = bg
        
        # Add script to handle show/hide logic.
        self.script = Script(
            inner_html=f"""
            // Track the current auto-hide timer for the snackbar
            if (!window._snackbarTimers) window._snackbarTimers = new WeakMap();
        
            function showSnackbar(snackbar, type, timeout) {{
                let bg = null;
                
                // Set background color based on type
                if (type === "error") bg = "#f44336";
                else if (type === "info") bg = "#2196f3";
                else if (type === "success") bg = "#43a047";
        
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
