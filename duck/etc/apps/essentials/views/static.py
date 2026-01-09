"""
Module containing staticfiles view.
"""
import os
import io
import pathlib

from typing import (
    List,
    Optional,
    Generator,
)

from duck.routes import (
    Blueprint,
    BlueprintJoinPathError,
    BlueprintJoinPathNameNoMatch,
    blueprint_joinpath,
)
from duck.settings import SETTINGS
from duck.http.request import HttpRequest
from duck.http.response import FileResponse
from duck.shortcuts import not_found404
from duck.utils.path import joinpaths


STATIC_ROOT = SETTINGS["STATIC_ROOT"]


def dev_find_staticfile(staticfile: str) -> Optional[str]:
    """
    Find staticfile in Development/Debug mode from all static directories in the following order:
    
    1. Global static directories in `GLOBAL_STATIC_DIRS` (settings.py)
    2. All Blueprint static directories
    """
    from duck.cli.commands.collectstatic import CollectStaticCommand
    
    staticfile_root_name = pathlib.Path(staticfile).name
    global_static_dirs = SETTINGS["GLOBAL_STATIC_DIRS"]
    blueprint_static_dirs: Generator = CollectStaticCommand.find_blueprint_static_dirs()
    original_staticfile = staticfile
    
    # Try finding static file in global static dirs
    for static_dir in global_static_dirs:
        staticfile = joinpaths(str(static_dir), original_staticfile)
        if os.path.isfile(staticfile):
            return staticfile
    
    # Try again finding static file in blueprints static dirs.
    for static_dir, blueprint in blueprint_static_dirs:
        try:
            staticfile = blueprint_joinpath(static_dir, original_staticfile, blueprint)
        except (BlueprintJoinPathError, BlueprintJoinPathNameNoMatch, ValueError):
            # Raised if maybe staticfile could not be resolved.
            continue
            
        if os.path.isfile(staticfile):
            return staticfile


def resolve_staticfile(request: HttpRequest, staticfile: str) -> str:
    """
    Resolve the full path of a static file, handling DEBUG and production modes.

    Args:
        request (HttpRequest): The current request (used in dev mode for lookup).
        staticfile (str): Relative path of the static file.

    Returns:
        str: Full path to the static file, or empty string if not found (DEBUG mode).
    """
    if SETTINGS["DEBUG"]:
        # Lookup in all possible dev static dirs
        return dev_find_staticfile(staticfile) or ""
    
    # Production mode: static files collected in STATIC_ROOT
    return joinpaths(STATIC_ROOT, staticfile)


def staticfiles_view(request: HttpRequest, staticfile: str):
    """
    View for serving staticfiles for the app.
    """
    staticfile = resolve_staticfile(request, staticfile)
    
    if not os.path.isfile(staticfile):
        if SETTINGS["DEBUG"]:
            response = not_found404(
                body=(
                    f"<p>Nothing matches the provided URI: {request.path}</p>"
                    "<p>Make sure the static file is available in <strong>global</strong> static dirs or blueprint static dirs.</p>"
                    "<p>Don't forget to execute <strong>collectstatic</strong> in production.</p>"
                ),
            )
        else:
            response = not_found404(
                body=(
                    f"<p>Nothing matches the provided URI: {request.path}</p>"
                ),
            )
        return response
    
    return FileResponse(staticfile)


async def async_staticfiles_view(request: HttpRequest, staticfile: str):
    """
    View for serving staticfiles for the app.
    """
    staticfile = resolve_staticfile(request, staticfile)
    
    if not os.path.isfile(staticfile):
        if SETTINGS["DEBUG"]:
            response = not_found404(
                body=(
                    f"<p>Nothing matches the provided URI: {request.path}</p>"
                    "<p>Make sure the static file is available in <strong>global</strong> static dirs or blueprint static dirs.</p>"
                    "<p>Don't forget to execute <strong>collectstatic</strong> in production.</p>"
                ),
            )
        else:
            response = not_found404(
                body=(
                    f"<p>Nothing matches the provided URI: {request.path}</p>"
                ),
            )
        return response
        
    return FileResponse(staticfile)
