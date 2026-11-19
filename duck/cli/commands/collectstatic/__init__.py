"""
Module containing sync and async collectstatic command classes.
"""

from duck.cli.commands.collectstatic._async import AsyncCollectStaticCommand
from duck.cli.commands.collectstatic.sync import CollectStaticCommand


__all__ = [
    "AsyncCollectStaticCommand",
    "CollectStaticCommand",
]
