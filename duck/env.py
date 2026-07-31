"""
Module for getting or setting Duck environment.
"""
import os
from pathlib import Path
import sys


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


def get_project_name() -> str:
    """
    Returns the current project's name.

    The project name is determined from the directory containing the
    application's entry point.

    Returns:
        str: The current project name.
    """
    cmd = sys.argv[0]
    
    if "duck" in cmd:
        cmd = "web"
        
    entrypoint = Path(cmd).resolve()
    
    # python web/main.py -> project/
    if entrypoint.parent.name == "web":
        return entrypoint.parent.parent.name

    return entrypoint.parent.name
