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
            "width": "100vw",
            "height": "100vh",
            "background": "rgba(0, 0, 0, 0.68)", # Slightly stronger dark overlay for dark modals
            "justify-content": "center",
            "z-index": "1000",
            "flex-direction": "column",
            "display": "none", # Hide by default.
            "overflow": "hidden", # Ensures overlay itself doesn't scroll
        }
        self.style.setdefaults(style)

        # Modal dialog styles (dark, minimal)
        modal_box_style = {
            "background": "#111",
            "color": "#fff",
            "border-radius": "8px",
            "padding": "24px 20px",
            "width": "90%",
            "max-width": "90%",
            "box-shadow": "0 8px 30px rgba(0,0,0,0.18)",
            "position": "fixed",
            "display": "flex",
            "align-items": "center",
            "flex-direction": "column",
            "overflow": "auto",              # Only modal content scrolls
            "scroll-behavior": "smooth",     # Smooth scroll for modal content
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
                    "margin-bottom": "1em",
                    "margin-right": "12px",
                    "margin-top": "3px"
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
                    "position": "absolute",
                    "top": "12px",
                    "right": "14px",
                    "background": "none",
                    "border": "none",
                    "font-size": "1.5rem",
                    "color": "#bbb",
                    "cursor": "pointer",
                    "padding": "2px",
                    "line-height": "1",
                    "display": 'inline-block'
                },
                props={
                    "aria-label": "Close",
                    "onclick": f"closeModal(document.getElementById('{self.id}'));"
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
                  if (modal) modal.style.display = "none";
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
              const height = document.documentElement.scrollHeight;
              const modalOffsetTop = getOffsetTop(modal);
              const heightPx = (height - modalOffsetTop) + "px";
              modal.style["height"] = modal.style["min-height"] = heightPx;
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
        content_children = []

        if self.close_btn:
            content_children.append(self.close_btn)

        if self.modal_script:
            content_children.append(self.modal_script)

        if self.title_heading:
            content_children.append(self.title_heading)

        # Modal content container (FlexContainer for vertical layout)
        self.modal_content = FlexContainer(
            direction="column",
            style=modal_box_style,
            props=modal_box_props,
            id="modal-content",
        )

        # Add modal content.
        super().add_child(self.modal_content)

        for child in content_children:
            self.add_child(child)

    def add_child(self, child):
        if not hasattr(self, 'modal_content'):
            super().add_child(child)
            return

        # Add child to modal content.
        self.modal_content.add_child(child)

    def set_content(self, content: Component):
        """
        Set modal content.
        """
        self.modal_content.clear_children()
        if self.close_btn:
            self.add_child(self.close_btn)
        if self.modal_script:
            self.add_child(self.modal_script)
        if self.title_heading:
            self.add_child(self.title_heading)
        self.add_child(content)
