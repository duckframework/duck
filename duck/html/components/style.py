"""
Style HTML Component.

This module defines a reusable `Style` component for embedding CSS styles within an HTML document.
"""

from duck.html.components import InnerComponent
from duck.csp import csp_nonce, csp_nonce_flag


class Style(InnerComponent):
    """
    Style HTML Component.

    The `Style` component allows developers to define and embed custom CSS styles directly within an HTML page.
    It can be used to dynamically style elements without needing an external stylesheet.

    **Features:**
    - Supports inline CSS.
    - Can be dynamically added to any component.
    - Enables styling customization for other components.

    **Example Usage:**
    ```py
    style = Style(
        inner_html='''
            .custom-popup {
                background-color: rgba(0, 0, 0, 0.8);
                color: white;
                padding: 10px;
                border-radius: 5px;
            }
        '''
    )
    component.add_child(style)
    ```

    This will generate the following HTML output:
    ```html
    <style>
        .custom-popup {
            background-color: rgba(0, 0, 0, 0.8);
            color: white;
            padding: 10px;
            border-radius: 5px;
        }
    </style>
    ```

    **Notes:**
    - **Automatic Nonce Addition**: When `ENABLE_HEADERS_SECURITY_POLICY=True` and `csp_nonce_flag` is set in `CSP_TRUSTED_SOURCES`, the `nonce` property is automatically added.
    - **Request Resolution Required**: For the `nonce` to be set automatically, the request must be resolved. This is achieved by calling `get_request_or_raise` on the component root (or the current component if the root is `None`).
    - The `inner_html` parameter must contain valid CSS code.
    - This component is intended for **inline styles** and does not support linking to external CSS files.
    - Styles defined within this component will apply globally unless scoped using class or ID selectors.
    """
    @property
    def properties(self):
        from duck.settings import SETTINGS
        props = super().properties
        # Set CSP configuration.
        if SETTINGS['ENABLE_HEADERS_SECURITY_POLICY']:
            current_nonce = props.get("nonce")
            if not current_nonce:
                self.set_csp_nonce()
        return props
          
    def set_csp_nonce(self):
        """
        This tries to retrieve current request nonce.
        """
        from duck.settings import SETTINGS
        from duck.html.components.extensions import RequestNotFoundError
        
        try:
            root = self.get_raw_root()
            request = root.get_request_or_raise()
        except RequestNotFoundError:
            try:
                request = self.get_request_or_raise()
            except RequestNotFoundError:
                return
                 
        # Set CSP configuration
        csp_directives = SETTINGS['CSP_TRUSTED_SOURCES']
        if csp_directives and request:
            style_src = set(csp_directives.get("style-src"))
            if csp_nonce_flag in style_src:
                nonce = csp_nonce(request)
                # Use _get_raw_props instead to avoid recursion if this method is executed 
                # from properties/props property method.
                self._get_raw_props()["nonce"] = nonce
                
    def get_element(self):
        """
        Returns the HTML tag for the component.
        """
        return "style"
