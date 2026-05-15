"""
Provides access to application settings.
"""
import os
import sys
import warnings

from functools import lru_cache
from typing import List, Tuple

from duck.exceptions.all import SettingsError
from duck.utils.importer import import_module_once


# Set default settings if not provided
os.environ.setdefault("DUCK_SETTINGS_MODULE", "web.settings")

# Retrieve settings module from the environment
SETTINGS_MODULE = os.environ.get("DUCK_SETTINGS_MODULE")

# Deprecated settings
DEPRECATED_SETTINGS: List[Tuple[str, str]] = [
    (
        "FORCE_HTTPS",
        "Setting 'FORCE_HTTPS' is deprecated, please use "
        "'HTTPS_REDIRECT' instead.",
    ),
    (
        "FORCE_HTTPS_BIND_PORT",
        "Setting 'FORCE_HTTPS_BIND_PORT' is deprecated, please use "
        "'HTTPS_REDIRECT_BIND_PORT' instead.",
    ),
]


def warn_deprecated_settings(settings: "Settings"):
    """
    Warn about deprecated settings currently in use.

    Args:
        settings:
            Loaded settings object to inspect.
    """
    for setting_name, message in DEPRECATED_SETTINGS:
        if setting_name in settings:
            warnings.warn(message, DeprecationWarning)


class Settings(dict):
    """
    A class for managing **Duck** settings.
    """
    
    source = None
    
    def reload(self):
        """
        Re-execute the settings module and update this dict in-place.
        """
        import importlib
        
        mod_str = os.environ.get("DUCK_SETTINGS_MODULE")
        mod = sys.modules.get(mod_str, None)
        mods = []
        
        if mod:
            importlib.reload_module(mod)
            mods.append(mod)
        else:
            mod = import_module_once(mod_str)
            mods.append(import_module_once("duck.etc.settings"))
            mods.append(mod)
            
        # Apply settings inplace
        self.source = mod
        
        for mod in mods:
            for var in dir(mod):
                if var.isupper():
                    self[var] = getattr(mod, var)
                    
        # Warn deprecated settings
        warn_deprecated_settings(self)
                
    def __repr__(self):
        return (
           "<" + f"{self.__class__.__name__} "
            f"source={repr(self.source)}".replace('<', "[").replace('>', "]") + ">"
        )


@lru_cache
def settings_to_dict(settings_module: str) -> Settings:
    """
    Convert a settings module into a Settings object.
    """
    settings_mod = import_module_once(settings_module)
    
    # Initialize and update settings
    settings = Settings({})
    settings.source = settings_mod
    
    for var in dir(settings_mod):
        if var.isupper():
            settings[var] = getattr(settings_mod, var)
            
    # Finally, return settings.
    return settings


def get_combined_settings() -> Settings:
    """
    Combine default and user settings into a single settings object.

    Returns:
        Settings:
            Combined settings object.

    Raises:
        SettingsError:
            Raised if the user settings module cannot be loaded.
    """
    default_settings = settings_to_dict("duck.etc.settings")
    
    try:
        user_settings = settings_to_dict(SETTINGS_MODULE)
    except Exception as e:
        raise SettingsError(
            "Error loading Duck settings module, ensure "
            "environment variable DUCK_SETTINGS_MODULE "
            f"is set correctly: {e}."
        ) from e
    
    # Override defaults with user settings
    default_settings.update(user_settings)
    
    # Create and update Settings object.
    settings = Settings(default_settings)
    settings.source = user_settings.source
    
    # Warn deprecated settings
    warn_deprecated_settings(settings)
    
    # Return final settings.
    return settings


# Set and load important settings, objects, etc.
SETTINGS: Settings = get_combined_settings()


# Set Django specific configurations
if not SETTINGS_MODULE.startswith("web") and SETTINGS['DJANGO_SETTINGS_MODULE'].startswith('web.backend.django.duckapp.duckapp.settings'):
    # Duck settings module is external yet the Django settings module is default.
    try:
        # Try to resolve the settings
        import_module_once(SETTINGS['DJANGO_SETTINGS_MODULE'])
    except ImportError:
        # We need to fix the Django settings module
        SETTINGS['DJANGO_SETTINGS_MODULE'] = SETTINGS_MODULE.rsplit('.', 1)[0] + ".backend.django.duckapp.duckapp.settings"
        

# Set django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', SETTINGS['DJANGO_SETTINGS_MODULE'])


if (
    os.getenv("DUCK_USE_DJANGO", None) == "true"
    or "-dj" in sys.argv 
    or "--use-django" in sys.argv
):
    SETTINGS["USE_DJANGO"] = True
