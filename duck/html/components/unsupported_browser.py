"""
Unsupported Browser Banner.
"""
from duck.html.components.modal import Modal
from duck.html.components.paragraph import Paragraph
from duck.html.components.script import Script


BANNER_SCRIPT = """
document.addEventListener("DOMContentLoaded", () => {{
  const unsupportedBrowserBanner = document.getElementById(`{banner_id}`);
  setTimeout(() => {{
    if (!window.LIVELY_SCRIPT_COMPATIBLE && window.receivedFullLivelyJs) {{
      openModal(unsupportedBrowserBanner);
    }}
  }}, 10); // Delay a little bit
}});
"""

class UnsupportedBrowserBanner(Modal):
    """
    Banner for unsupported browser.
    """
    
    def on_create(self):
        """
        Build the component.
        """
        # Alter title before super on_create
        self.kwargs["title"] = "🌐 Unsupported Browser Detected"
        super().on_create()
        
        # Some modifications
        self.props.setdefault("id", "unsupported-browser-banner")
        self.style.update({
            "align-items": "flex-start",
            "padding": "20px",
        })
        
        # Minimalist dark modal content styling
        self.modal_content.style.update({
            "padding": "24px 20px",
            "text-align": "center",
        })
        
        # Initialize info to display in banner
        self.info = Paragraph(
            inner_html=(
                "<div style='font-size:2em;margin-bottom:0.3em;'>🚫</div>"
                "<b>Unsupported Browser</b><br>"
                "Your browser isn't supported.<br>"
                "Please update or switch to a modern browser.<br><br>"
                "<a href='https://www.google.com/chrome/' target='_blank' style='color:#4fd1c5;text-decoration:underline;'>Chrome</a> &nbsp;|&nbsp; "
                "<a href='https://www.mozilla.org/firefox/new/' target='_blank' style='color:#fbbf24;text-decoration:underline;'>Firefox</a> &nbsp;|&nbsp; "
                "<a href='https://www.microsoft.com/edge' target='_blank' style='color:#60a5fa;text-decoration:underline;'>Edge</a>"
            ),
            style={
                "text-align": "center",
                "color": "#ccc",
            }
        )
        
        # Set banner content.
        self.set_content(self.info)
        
        # Add some script for the banner.
        self.add_child(Script(inner_html=BANNER_SCRIPT.format(banner_id=self.id)))
