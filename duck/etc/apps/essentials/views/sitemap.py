"""
Module containing sitemap view.
"""

from duck.settings import SETTINGS
from duck.http.request import HttpRequest
from duck.http.response import HttpResponse
from duck.contrib.sitemap import SitemapBuilder
from duck.contrib.sync import convert_to_async_if_needed
from duck.views import cached_view


SITEMAP_EXTRA_URLS = SETTINGS.get("SITEMAP_EXTRA_URLS", [])
SITEMAP_EXCLUDE_PATTERNS = SETTINGS.get("SITEMAP_EXCLUDE_PATTERNS", [])
SITEMAP_DEFAULT_PRIORITY = SETTINGS.get("SITEMAP_DEFAULT_PRIORITY", 0.5)
SITEMAP_CHANGE_FREQUENCY = SETTINGS.get("SITEMAP_CHANGE_FREQUENCY", "monthly")
SITEMAP_SAVE_TO_FILE = SETTINGS.get("SITEMAP_SAVE_TO_FILE", False)
SITEMAP_FILEPATH = SETTINGS.get("SITEMAP_FILEPATH", None)
SITEMAP_APPLY_DEFAULT_EXCLUDES = SETTINGS.get("SITEMAP_APPLY_DEFAULT_EXCLUDES", True)


@cached_view(targets=["path"]) # Cache view based on path.
def sitemap_view(request: HttpRequest):
    """
    View for serving sitemap for the app.
    """
    builder = SitemapBuilder(
        server_url=None, # Parsing None will automatically resolve server URL
        save_to_file=SITEMAP_SAVE_TO_FILE,
        filepath=SITEMAP_FILEPATH,
        extra_urls=SITEMAP_EXTRA_URLS,
        exclude_patterns=SITEMAP_EXCLUDE_PATTERNS,
        default_priority=SITEMAP_DEFAULT_PRIORITY,
        default_changefreq=SITEMAP_CHANGE_FREQUENCY,
        apply_default_excludes=SITEMAP_APPLY_DEFAULT_EXCLUDES,
    )
    xml = builder.build()
    return HttpResponse(xml, content_type="text/xml")


@cached_view(targets=["path"]) # Cache view based on path.
async def async_sitemap_view(request: HttpRequest):
    """
    Asynchronous view for serving sitemap for the app.
    """
    builder = SitemapBuilder(
        server_url=None, # Parsing None will automatically resolve server URL
        save_to_file=SITEMAP_SAVE_TO_FILE,
        filepath=SITEMAP_FILEPATH,
        extra_urls=SITEMAP_EXTRA_URLS,
        exclude_patterns=SITEMAP_EXCLUDE_PATTERNS,
        default_priority=SITEMAP_DEFAULT_PRIORITY,
        default_changefreq=SITEMAP_CHANGE_FREQUENCY,
        apply_default_excludes=SITEMAP_APPLY_DEFAULT_EXCLUDES,
    )
    xml = await convert_to_async_if_needed(builder.build)()
    return HttpResponse(xml, content_type="text/xml")
