"""
Utility functions for the Duck application.
"""

import sys


def get_run_command() -> list[str]:
    """
    Get the command used to run the application.

    Returns:
        list[str]: The command used to run the application.
    """
    cmd = [sys.executable, *sys.argv, "--no-child-process"]

    if "runserver" in sys.argv:
        cmd = [*sys.argv, "--no-child-process",]

    if "--is-reload" in sys.argv:
        cmd.append("--is-reload")

    return cmd
