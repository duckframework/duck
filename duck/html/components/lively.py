"""
Module containing Scripts component that injects all required scripts to enable the Lively Component System
on the client side via WebSocket.

Includes:
- `msgpack.min.js`: For MessagePack encoding/decoding.
- `lively.js`: Main Lively client-side runtime.
- Inline JS: Instantiates and connects a LivelyWebSocketClient.

Notes:
- `msgpack.min.js` is required and always included.
- Scripts are injected in the order: msgpack, lively, then inline connect.
"""
from duck.exceptions.all import RouteNotFoundError
from duck.html.components import ComponentError
from duck.html.components.container import Container
from duck.html.components.script import Script


class LivelyScripts(Container):
    """
    Component that injects all required scripts to enable the Lively Component System
    on the client side via WebSocket.

    Includes:
    - `msgpack.min.js`: For MessagePack encoding/decoding.
    - `lively.js`: Main Lively client-side runtime.
    - Inline JS: Instantiates and connects a LivelyWebSocketClient.

    Notes:
        - `msgpack.min.js` is required and always included.
        - Scripts are injected in the order: msgpack, lively, then inline connect.
    """
    
    def on_create(self):
        from duck.settings import SETTINGS
        from duck.shortcuts import static, resolve
        
        # Super create
        super().on_create()
        
        try:
            # When resolving urls, the result should be absolute as absolute LIVELY_WS_URL may be needed by
            # the Lively client to resolve server domain.
            ws_url = resolve("lively-component-system")
            static_url = resolve("lively-staticfiles")
        except RouteNotFoundError:
            raise ComponentError(
                "This component can only be initialized after Duck setup. "
                "Make sure the main Duck application has already been initialized"
            ) 
            
        # Include required external scripts
        self.msgpack_script = Script(
            props={"src": static_url.replace("<staticfile>", "msgpack.min.js"), "async": "true"}
        )
        
        self.prepare_script = Script(
            inner_html=(
                f"window.LIVELY_WS_URL = '{ws_url}';"
                f"window.LIVELY_DEBUG = {'true' if SETTINGS['DEBUG'] else 'false'};"
            ),
        )
        
        # Never make the following script async because it will break the app logic.
        self.lively_script = Script(
            props={"src": static_url.replace("<staticfile>", "lively.js")}
        )
        
        # Add all in required order
        self.add_children([self.msgpack_script, self.prepare_script, self.lively_script])
