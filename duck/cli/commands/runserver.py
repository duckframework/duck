"""
Module containing runserver command class.
"""
import os
import sys
import subprocess

from typing import Optional
from duck.logging import console


class RunserverCommand:
    # runserver command
    
    @classmethod
    def setup(cls, settings_module: Optional[str] = None):
        # Setup before command execution
        if settings_module:
            os.environ["DUCK_SETTINGS_MODULE"] = settings_module
    
    @classmethod
    def main(
        cls,
        address: str = "0.0.0.0",
        port: int = 8000,
        domain: Optional[str] = None,
        settings_module: Optional[str] = None,
        mainfile: Optional[str] = None,
        uses_ipv6: bool = False,
        is_reload: bool = False,
    ):
        # Runserver
        cls.setup(settings_module)
        cls.runserver(
            address=address,
            port=port,
            domain=domain,
            mainfile=mainfile,
            uses_ipv6=uses_ipv6,
            is_reload=is_reload,
        )
    
    @classmethod
    def runserver(
         cls,
         address: str = "0.0.0.0",
         port: int = 8000,
         domain: Optional[str] = None,
         mainfile: Optional[str] = None,
         uses_ipv6: bool = False,
         is_reload: bool = False,
     ):
        from duck.app import App
        from duck.settings import SETTINGS
        
        if mainfile:
            # file containing app instance provided
            if not mainfile.endswith(".py"):
                raise TypeError(
                    "File provided as the main python file has invalid extension, should be a .py file."
                )
    
            if not os.path.isfile(mainfile):
                raise FileNotFoundError("Main python file which the app resides not found.")
                    
            # Execute sub-command
            command = [sys.executable, mainfile]
            
            if is_reload:
                command.extend(["--is-reload"])
            
            # Execute command and replace current process.
            os.execve(sys.executable, command, os.environ)
        
        else:
            application = App(
                addr=address,
                port=port,
                domain=domain,
                uses_ipv6=uses_ipv6
            )
            application.run()  
