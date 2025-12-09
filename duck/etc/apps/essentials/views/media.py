"""
Module containing mediafiles view.
"""
import io
import os

from duck.settings import SETTINGS
from duck.http.request import HttpRequest
from duck.http.response import FileResponse, HttpResponse
from duck.shortcuts import not_found404
from duck.views import cached_view, SkipViewCaching
from duck.contrib.sync import convert_to_async_if_needed
from duck.utils.path import joinpaths
from duck.utils.asyncio import in_async_context


MEDIA_ROOT = str(SETTINGS["MEDIA_ROOT"])


def media_mtime(request: HttpRequest, mediafile: str) -> float:
    """
    Return the modification timestamp for a media file.
    """
    # This is a caching function!
    mediafile = joinpaths(MEDIA_ROOT, mediafile)
    
    try:
        stat = os.stat(mediafile)
    
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


@cached_view(targets={"path": None, media_mtime: None}, on_cache_result=on_cache_result) # Cache view based on modified time
def mediafiles_view(request: HttpRequest, mediafile: str):
    """
    View for serving media files for the app.
    """
    mediafile = joinpaths(MEDIA_ROOT, mediafile)
    
    if not os.path.isfile(mediafile):
        if SETTINGS["DEBUG"]:
            response = not_found404(
                body=(
                    f"<p>Nothing matches the provided URI: {request.path}</p>"
                    "<p>Make sure the media file is available in <strong>MEDIA_ROOT.</strong>"
                ),
            )
        else:
            response = not_found404(
                body=(
                    f"<p>Nothing matches the provided URI: {request.path}</p>"
                ),
            )
        return response
    
    return FileResponse(mediafile)


@cached_view(targets={"path": None, media_mtime: None}, on_cache_result=on_cache_result) # Cache view based on modified time
async def async_mediafiles_view(request: HttpRequest, mediafile: str):
    """
    Asynchronous iew for serving media files for the app.
    """
    mediafile = joinpaths(MEDIA_ROOT, mediafile)

    if not os.path.isfile(mediafile):
        if SETTINGS["DEBUG"]:
            response = not_found404(
                body=(
                    f"<p>Nothing matches the provided URI: {request.path}</p>"
                    "<p>Make sure the media file is available in <strong>MEDIA_ROOT.</strong>"
                ),
            )
        else:
            response = not_found404(
                body=(
                    f"<p>Nothing matches the provided URI: {request.path}</p>"
                ),
            )
        return response
    
    return FileResponse(mediafile)
