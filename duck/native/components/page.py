"""
Proxy module to `duck.html.components.Page` with additionals.
"""

from duck.html.components.page import * 
from duck.html.components.page import Page
from duck.html.components.snackbar import Snackbar
from duck.html.components.style import Style


BASE_CSS = """
/* Native-feel patching indicator (Arc/Vercel-style blur) */
[data-patching="true"] {
  filter: blur(1px);
  opacity: 0.85;
  transition: filter 0.15s ease-out, transform 0.15s ease-out, opacity 0.15s ease-out;
  pointer-events: none;
}
"""


class AppPage(Page):
    """
    Application specific page - this is just a better alternative to the default duck's `Page`
    component.
    """
    
    def on_create(self):
        super().on_create()
        
        # Add base.css
        self.add_to_head(Style(inner_html=BASE_CSS))
    
    def add_default_body_components(self):
        """
        Add default body components.
        """
        # Add body components
        # Initialize bottom page snackbar
        self.page_snackbar = Snackbar(
            id="page-snackbar",
            type="info",
            variant="filled",
            style={
              "bottom": "0px",
            },
            children=[
                Label(
                    klass="snackbar-label",
                    style={
                        "text-align": "center",
                        "margin": "auto",
                    }
                ),
            ]
        )
        
        # Add all body components.
        self.add_to_body([self.page_snackbar])
