"""
Module for setting up Duck space and configure all necessary components to ensure the application is ready for operation.
"""

import os
import sys
import asyncio
import platform
import threading

from duck.env import is_testing_environment
from duck.exceptions.all import SettingsError
from duck.routes import register_blueprints, register_urlpatterns
from duck.logging import logger
from duck.settings import SETTINGS
from duck.settings.loaded import SettingsLoaded
from duck.utils.asyncio import validate_event_loop, ASYNCIO_LOOP_CREATORS


def validate_asyncio_loop():
    """
    Validate the ASYNC_LOOP setting and configure the event loop accordingly.

    Raises:
        SettingsError: If the specified ASYNC_LOOP value is unsupported or if uvloop is selected on Windows.
    """
    configured_loop = SETTINGS.get("ASYNC_LOOP", "asyncio")
    supported_loops = sorted(set(ASYNCIO_LOOP_CREATORS.keys()))

    try:
        current_platform = platform.system() or ""

        if configured_loop == "uvloop" and current_platform.lower() == "windows":
            raise SettingsError(
                "uvloop is generally not supported on Windows in official releases. "
                "Set ASYNC_LOOP to 'asyncio' or run on a Unix-like OS (Linux, macOS)."
            )

        # Validate the loop type and ensure it can be created
        validate_event_loop(configured_loop, return_loop_creator=False)

    except ValueError as e:
        raise SettingsError(
            f"Invalid ASYNC_LOOP setting: '{configured_loop}'. "
            f"Supported options are: {supported_loops}."
        ) from e

    except ImportError as e:
        raise SettingsError(
            f"Failed to import the required module for ASYNC_LOOP '{configured_loop}'. "
            "Ensure the necessary package is installed."
        ) from e
    

def setup():
    """
    Setup the Duck application.

    Initialize and configure all necessary components to ensure the application is ready for operation.

    Notes:
        This configures and registers all routes either simple or ones created
    """
    # Improve the setup it's taking approx >= 2s
    from duck.backend.django.setup import prepare_django, DjangoSetupWarning
    
    base_dir = str(SETTINGS['BASE_DIR'])
    
    # Validate the ASYNC_LOOP setting and configure the event loop accordingly
    if SETTINGS.get("ASYNC_HANDLING") or SETTINGS.get("SUPPORT_HTTP_2"):
        validate_asyncio_loop()

    # Try preparing Django backend
    try:
        prepare_django(True)
        
    except Exception as e:
        logger.warn(f"Django setup failed: {e}", DjangoSetupWarning)
        
        if SETTINGS['DEBUG']:
            logger.log_exception(e)
            
    # Register some urlpatterns
    register_urlpatterns(SettingsLoaded.URLPATTERNS)
    register_blueprints(SettingsLoaded.BLUEPRINTS)
    
    if base_dir not in sys.path:
        # Add project directory to path
        sys.path.insert(-1, base_dir)
