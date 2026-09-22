"""
Proxy module to `duck.html.components.Page` with additionals.
"""

from duck.html.components.page import * 
from duck.html.components.page import Page
from duck.html.components.snackbar import Snackbar
from duck.html.components.progressbar import ProgressBar
from duck.html.components.unsupported_browser import UnsupportedBrowserBanner


class AppPage(Page):
    """
    Application specific page - this is just a better alternative to the default duck's `Page`
    component.
    """
    
    def add_default_body_components(self):
        """
        Add default body components.
        """
        
        # Add body components
        # Initialize top page snackbar
        # Initialize top page snackbar
        self.page_snackbar = Snackbar(
            id="page-snackbar",
            type="info",
            variant="solid",
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
        
        # Initialize top page progress
        self.page_progress_bar = ProgressBar(
            id="page-progress-bar",
            style={
                "position": "fixed",
                "z-index": "50000",
            }
        )
        
        # Initialize unsupported browser banner
        self.unsupported_browser_banner = UnsupportedBrowserBanner()
    
        # Add all body components.
        self.add_to_body([self.page_snackbar, self.page_progress_bar, self.unsupported_browser_banner])
