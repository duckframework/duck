"""
Modal components module.
"""
import random

from duck.html.components import Theme, Component
from duck.html.components.container import FlexContainer
from duck.html.components.button import Button
from duck.html.components.heading import Heading
from duck.html.components.script import Script


class Modal(FlexContainer):
    """
    Modal component with overlay and centered content.

    Args:
        title (str): Optional title for the modal dialog.
        show_close (bool): Whether to show a close ('×') button (default: True).
        open_on_ready (bool): Whether to open modal instantly after page load. Defaults to False.
        modal_props (dict): Props for the modal content container (optional).
        modal_style (dict): Style for the content container (optional).
        children (list): List of child components (modal body).
        **kwargs: Extra arguments passed to the overlay.
    
    Example:
    
    ```py
    from duck.html.components.label import Label
    
    modal = Modal(title="Test modal", open_on_ready=True) # `open_on_ready` will open modal instantly on page load
    modal.set_content(Label(color="blue", text="Some Content"))
    ```
    """

    def on_create(self):
        super().on_create()
        self.style["display"] = "none" # invisible by default.
        
        if not self.id:
            self.id = f"modal-{random.randint(0, 2000)}"

        # Overlay style (full-screen dark background)
        style = {
            "position": "fixed",
            "top": "0",
            "left": "0",
            "width": "100%",
            "height": "100vh",
            "background": "rgba(0, 0, 0, 0.68)", # Slightly stronger dark overlay for dark modals
            "z-index": "1000",
            "align-items": "center",
            "flex-direction": "column",
            "display": "none", # Hide by default.
            "overflow": "hidden", # Ensures overlay itself doesn't scroll
        }
        self.style.update(style)
           
        # Modal dialog styles (dark, minimal)
        modal_box_style = {
            "min-height": "100px",
            "background": "#111",
            "color": "#fff",
            "border-radius": "8px",
            "width": "100%",
            "box-shadow": "0 8px 30px rgba(0,0,0,0.18)",
            "display": "flex",
            "padding": "0",           # Padding moved to inner sections so header sits flush
            "align-items": "stretch",
            "flex-direction": "column",
            "overflow": "auto",
            "scroll-behavior": "smooth",
            "position": "relative",   # Required so the header row stays inside the box
        }
        modal_box_props = self.kwargs.get("modal_props") or {}

        # Update modal box style
        modal_style = self.kwargs.get("modal_style") or {}
        modal_box_style.update(modal_style)

        # Title bar (optional)
        title = self.kwargs.get("title")
        self.title_heading = None

        if title:
            self.title_heading = Heading(
                "h3",
                text=title,
                style={
                    "margin": "0",
                    "font-size": "1rem",
                    "color": "#fff",
                    "flex": "1",
                }
            )

        # Close button (optional)
        show_close = self.kwargs.get("show_close", True)
        open_on_ready = bool(self.kwargs.get("open_on_ready", False))
        self.close_btn = None
        self.close_modal_script = None

        if show_close:
            self.close_btn = Button(
                klass="close-btn",
                text="×",
                style={
                    "background": "none",
                    "border": "none",
                    "font-size": "1.4rem",
                    "color": "#888",
                    "cursor": "pointer",
                    "padding": "0 0 0 12px",
                    "line-height": "1",
                    "flex-shrink": "0",
                    "display": "inline-block",
                    "transition": "color 0.15s",
                },
                props={
                    "aria-label": "Close modal",
                    "onclick": f"closeModal(document.getElementById('{self.id}'));",
                    "onmouseenter": "this.style.color='#fff'",
                    "onmouseleave": "this.style.color='#888'",
                    "type": "button",
                },
            )

        # Create script for opening/closing modal AND locking background scroll
        # Added: scrollToTop argument. If true (default), will scroll modal content and window to top when opened.
        self.modal_script = Script(
            inner_html=f"""
                /**
                  * Gets the offsetTop for an element.
                  */
                function getOffsetTop(elem) {{
                  const rect = elem.getBoundingClientRect();
                  const win = elem.ownerDocument.defaultView;
        		  return rect.top + win.pageYOffset;
                }}
                
                /**
                  * Closes a modal by setting display to "none"
                  */
                function closeModal(modal) {{
                  if (modal) {{
                    modal.style.display = "none";
                    
                    // Restore modal height
                    modal.style["height"] = modal._originalHeight || "";
                    modal.style["min-height"] = modal._originalMinHeight || "";
                  }}
                }}
                
                /**
                 * Open modal with optional scroll to top.
                 * @param {{HTMLElement}} modal 
                 * @param {{boolean}} [scrollToTop=true] - If true, scroll modal content and window to top
                 */
                function openModal(modal, scrollToTop=true) {{
                  if (!modal) {{
                    console.warn("Modal could not be resolved.");
                  }}
                  if (modal) {{
                    modal.style.display = "flex";
                    
                    // Set modal height after the modal is visible to avoid returning zero when getting offset.                   
                    setModalHeight(modal);
                    
                    // Try to find first child with overflow:auto (the modal content)
                    const modalContent = modal.querySelector('#modal-content');
                    if (modalContent) {{
                      const modalContentTop = getOffsetTop(modalContent);
                      window.scrollTo({{top: modalContentTop, behavior: "smooth"}});
                    }}
                  }}
                }}
            
            function setModalHeight(modal) {{
              modal._originalHeight = modal.style["height"];
              modal._originalMinHeight = modal.style["min-height"];
              
              const height = document.documentElement.scrollHeight;
              const modalOffsetTop = getOffsetTop(modal);
              const heightPx = (height - modalOffsetTop) + "px";
              
              // Set modal height
              modal.style["height"] = heightPx;
              modal.style['min-height'] = heightPx;
            }}
            
            if (document.readyState !== "complete") {{
              const modal = document.getElementById('{self.id}');
              document.addEventListener('DOMContentLoaded', () => {{
                   if ({str(open_on_ready).lower()})  openModal(document.getElementById('{self.id}'), true);
              }});
            }}
            else {{
              const modal = document.getElementById('{self.id}');
              if ({str(open_on_ready).lower()})  openModal(document.getElementById('{self.id}'), true);
            }}
            """
        )
        
        # Modal content (title, close button, children)
        # Build a header row that always sits at the top of the modal box.
        # This keeps the close button anchored to the modal content regardless
        # of how tall or short the content inside is.
        self.modal_header = None

        has_header = bool(title or show_close)
        if has_header:
            self.modal_header = FlexContainer(
                style={
                    "flex-direction": "row",
                    "align-items": "center",
                    "justify-content": "space-between",
                    "padding": "16px 20px",
                    "border-bottom": "1px solid rgba(255,255,255,0.06)" if title else "none",
                    "flex-shrink": "0",
                }
            )
            
            if self.title_heading:
                self.modal_header.add_child(self.title_heading)
            
            if self.close_btn:
                # Push close button to the right when there's no title
                if not self.title_heading:
                    spacer = FlexContainer()
                    spacer.style["flex"] = "1"
                    self.modal_header.add_child(spacer)
                self.modal_header.add_child(self.close_btn)

        # Modal content container (modal content parent)
        self.modal_content_container = FlexContainer(
            style={
                "flex-direction": "column",
                "position": "fixed",
                "height": "100vh",
                "width": "100%",
            },
            id="modal-content-container",
        )

        # Modal content (FlexContainer for vertical layout)
        self.modal_content = FlexContainer(
            direction="column",
            style=modal_box_style,
            props=modal_box_props,
            id="modal-content",
        )

        # Add header row first, then script, then body content
        if self.modal_header:
            self.modal_content.add_child(self.modal_header)

        if self.modal_script:
            self.modal_content.add_child(self.modal_script)

        # Add modal content.
        super().add_child(self.modal_content_container)
        self.modal_content_container.add_child(self.modal_content)

    def add_child(self, child):
        if not hasattr(self, 'modal_content'):
            super().add_child(child)
            return

        # Script and header are added directly — everything else goes into
        # a padded body wrapper so content has breathing room below the header
        if child is self.modal_header or child is self.modal_script:
            self.modal_content.add_child(child)
            return

        # Wrap body content in a padded container
        body_wrap = FlexContainer()
        body_wrap.style.update({
            "flex-direction": "column",
            "padding": "20px",
            "gap": "12px",
            "flex": "1",
        })
        body_wrap.add_child(child)
        self.modal_content.add_child(body_wrap)

    def open_modal(self):
        """
        Opens the modal; This simply makes the component visible.
        """
        self.style["display"] = "flex"

    def set_content(self, content: Component):
        """
        Replaces the modal body content while keeping the header row
        (title + close button) intact at the top.
        """
        # Remove everything except the header row and script
        preserved = []
        
        for child in list(self.modal_content.children):
            if child is self.modal_header or child is self.modal_script:
                preserved.append(child)

        self.modal_content.clear_children()

        for child in preserved:
            self.modal_content.add_child(child)

        # Add the new body content below the header
        self.modal_content.add_child(content)
