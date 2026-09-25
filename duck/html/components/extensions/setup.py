"""
Setup of default component extensions (including Native ones if setting NATIVE_ENABLED=True).
"""


def setup():
    """
    Setup all default extensions e.g., HighlightExtension (for buttons).
    """
    # Imports here; avoid circular imports.
    from duck.html.components.extensions import register_default_extension
    from duck.html.components.extensions.clickable import HighlightExtension
    from duck.html.components.button import Clickable
    
    # Start registration
    register_default_extension(Clickable, HighlightExtension)
