"""
Script HTML Component.

This module defines a reusable `Script` component for embedding JavaScript code within an HTML document.
"""

from duck.html.components import InnerComponent
from duck.csp import csp_nonce, csp_nonce_flag


class Script(InnerComponent):
    """
    Script HTML Component.

    The `Script` component allows developers to embed JavaScript code within an HTML page dynamically.
    It can be used to define inline scripts that interact with other components.

    **Features:**
    - Supports inline JavaScript execution.
    - Can be dynamically added to any component.
    - Provides flexibility for defining custom client-side logic.

    **Example Usage:**
    ```py
    script = Script(
        inner_html='''
            function showAlert() {
                alert("Hello, world!");
            }
        '''
    )
    component.add_child(script)
    ```

    This will generate the following HTML output:
    ```html
    <script>
        function showAlert() {
            alert("Hello, world!");
        }
    </script>
    ```

    **Notes:**
    - **Automatic Nonce Addition**: When `ENABLE_HEADERS_SECURITY_POLICY=True` and `csp_nonce_flag` is set in `CSP_TRUSTED_SOURCES`, the `nonce` property is automatically added.
    - **Request Resolution Required**: For the `nonce` to be set automatically, the request must be resolved. This is achieved by calling `get_request_or_raise` on the component root (or the current component if the root is `None`).
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
            script_src = set(csp_directives.get("script-src"))
            if csp_nonce_flag in script_src:
                nonce = csp_nonce(request)
                # Use _get_raw_props instead to avoid recursion if this method is executed 
                # from properties/props property method.
                self._get_raw_props()["nonce"] = nonce
                
    def get_element(self):
        """
        Returns the HTML tag for the component.
        """
        return "script"
