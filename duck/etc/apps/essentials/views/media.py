"""
Module containing mediafiles view.
"""

import os

from duck.settings import SETTINGS
from duck.http.request import HttpRequest
from duck.http.response import FileResponse
from duck.utils.path import joinpaths
from duck.shortcuts import not_found404


MEDIA_ROOT = str(SETTINGS["MEDIA_ROOT"])


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
