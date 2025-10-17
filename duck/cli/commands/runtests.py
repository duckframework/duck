"""
Module containing runtests command class.
"""
import os
import sys
import subprocess

from duck.logging import console
from duck.storage import duck_storage
from duck.utils.path import joinpaths


class RuntestsCommand:
    # runtests command
    
    @classmethod
    def setup(cls):
        # Setup before command execution
        os.environ["DUCK_SETTINGS_MODULE"] = "duck.etc.structures.projects.testing.web.settings"
        
    @classmethod
    def main(cls, verbose: bool = False):
        cls.setup()
        cls.runtests(verbose)
     
    @classmethod
    def runtests(cls, verbose: bool = False):
        # Execute command after setup.
        from duck.settings import SETTINGS
        
        tests_dir = joinpaths(duck_storage, "tests")
        
        if verbose:
            os.environ["DUCK_TESTS_VERBOSE"] = "true"
            
        subprocess.call([
            sys.executable, "-m", "unittest", "discover", "-s",
            tests_dir, "-p", "test_*.py", "-t", tests_dir,
        ])
