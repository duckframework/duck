"""
Module for getting or setting Duck environment.
"""
import os


def is_testing_environment():
    """
    Returns `True` if Duck is in testing environment, i.e. `DUCK_SETTINGS_MODULE="duck.etc.settings.structures.projects.testing.settings`.
    """
    return os.getenv("DUCK_SETTINGS_MODULE") == "duck.etc.structures.projects.testing.settings"
    

def set_testing_environment():
    """
    Sets the testing environment for Duck. Useful before Duck setup.
    """
    os.environ["DUCK_SETTINGS_MODULE"] = "duck.etc.structures.projects.testing.settings"
    