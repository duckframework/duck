"""
Minimal test base for Duck webserver using external BASE_URL.
"""
import os
import urllib3
import unittest
import warnings
import random

from typing import Any, Dict


VERBOSE_TESTS = os.getenv("DUCK_TESTS_VERBOSE")


def set_settings(settings: Dict[str, Any]):
    # This must be called before any use of the duck.settings module e.g. through duck.app
    os.environ.setdefault("DUCK_SETTINGS_MODULE", "duck.etc.structures.projects.testing.web.settings")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "duck.etc.structures.projects.testing.web.backend.django.duckapp.duckapp.settings")
    
    # Import settings after setting the settings module
    from duck.settings import SETTINGS
    
    # Edit settings inplace.
    for key, value in settings.items():
        SETTINGS[key.upper()] = value
    
    if VERBOSE_TESTS:
        SETTINGS['SILENT'] = SETTINGS['DJANGO_SILENT'] = False


class TestBaseServer(unittest.TestCase):
    """
    Base class for Duck server tests using a predefined BASE_URL.
    """
    settings: Dict[str, Any] = {
        "silent": True,
        "django_silent": True,
        "log_to_file": False,
        "auto_reload": False,
        "force_https": False,
        "enable_https": False,
        "use_django": False,
    }
    
    _app = None
    
    @property
    def app(self):
        from duck.app import App
        from duck.settings import SETTINGS
        
        app = type(self)._app
        
        if not app:
            type(self)._app = app = App(
                addr="localhost",
                port=random.randint(8000, 9000),
                uses_ipv6=False,
                domain="localhost",
                disable_signal_handler=False,
                disable_ipc_handler=True,
            )
        return app
         
    @property
    def base_url(self) -> str:
        return self.app.absolute_uri
        
    def setUp(self):
        warnings.filterwarnings("ignore", category=ResourceWarning)
        warnings.filterwarnings("ignore", category=urllib3.exceptions.InsecureRequestWarning)
        
        if not self.app.started:
            self.app.run()
    
    @classmethod
    def tearDownClass(cls):
        """Clean up server resources after all tests complete."""
        if cls._app and cls._app.started:
            try:
                cls._app.stop()
            except (AttributeError, RuntimeError) as e:
                # Ignore errors if server is already stopped or app object is invalid
                pass
            

# Set dynamic testing settings
set_settings(TestBaseServer.settings)


if __name__ == "__main__":
    unittest.main()
