"""
Extra components apart from `duck.html.components` for native feel.

This is a proxy package to `duck.html.components`: modules pass through unchanged unless a native-feel module of the same name is defined here.
"""
from duck.settings import SETTINGS
from duck.html.components import *


# Rebind overridden modules so they win over the pass-through originals
from . import page


if SETTINGS["NATIVE_ENABLED"]:
    from duck.native.components.extensions.setup import setup as setup_native_extensions
    
    # Setup native extensions
    setup_native_extensions()
