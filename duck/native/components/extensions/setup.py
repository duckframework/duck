"""
Setup of default component extensions - enhance native feel.
"""
from duck.html.components.extensions import register_default_extension, unregister_default_extension
from duck.html.components.extensions.clickable import RippleExtension, HighlightExtension
from duck.html.components.button import Clickable


def setup():
    """
    Setup all default extensions e.g., RippleExtension (for buttons).
    """
    # Unregister highlight extension
    unregister_default_extension(Clickable, HighlightExtension, failsafe=True)
    
    # Register native-like ripple extension
    register_default_extension(Clickable, RippleExtension)
