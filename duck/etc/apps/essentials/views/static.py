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
from duck.http.response import FileResponse, HttpResponse
from duck.shortcuts import not_found404
from duck.views import cached_view, SkipViewCaching
from duck.contrib.sync import convert_to_async_if_needed
from duck.utils.path import joinpaths
from duck.utils.asyncio import in_async_context


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


def static_mtime(request: HttpRequest, staticfile: str) -> float:
    """
    Return the modification timestamp for a static file.
    """
    # This is a caching function!
    staticfile = resolve_staticfile(request, staticfile)
    
    try:
        stat = os.stat(staticfile)
    
    except FileNotFoundError:
        # Return a specific time for not found response
        return -10
    
    except Exception as e:
        # Unknown exception, caching nolonger possible
        raise ViewCachingError(f"Caching nolonger possible because of exception: {e}")
            
    return stat.st_mtime
            

def on_cache_result(request: HttpRequest, cached: HttpResponse):
    """
    Function that will be called upon retrieving a response from cache.
    """
    
    class CachedStream(io.BytesIO):
        """
        This is a custom Bytes IO representing cached data.
        """
        __slots__ = {"_total_read_bytes"}
        
    class AsyncCachedStream(CachedStream):
        """
        This is a custom asynchronous Bytes IO representing cached data.
        """
        __slots__ = {}
        
        async def read(self, *args, **kw):
             return await convert_to_async_if_needed(super().read)(*args, **kw)
        
        async def write(self, *args, **kw):
             return await convert_to_async_if_needed(super().write)(*args, **kw)
             
        async def close(self, *args, **kw):
             return await convert_to_async_if_needed(super().close)(*args, **kw)
                  
    if isinstance(cached, FileResponse):
        if not in_async_context():
            if not isinstance(cached.stream, CachedStream):
                # We haven't modified cached.stream inplace
                cached_data = cached.stream._total_read_bytes
                cached.stream = CachedStream(cached_data)
                cached.stream._total_read_bytes = cached_data # Update read bytes
                
        else:
            if not isinstance(cached.stream, AsyncCachedStream):
                # We haven't modified cached.stream inplace
                cached_data = cached.stream._total_read_bytes
                cached.stream = AsyncCachedStream(cached_data)
                cached.stream._total_read_bytes = cached_data # Update read bytes


@cached_view(targets={static_mtime: None}, on_cache_result=on_cache_result) # Cache view based on modified time
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


@cached_view(targets={static_mtime: None}, on_cache_result=on_cache_result) # Cache view based on modified time
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
