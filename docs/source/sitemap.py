# Retrieve documentation URLs to the sitemap.
import os

from typing import List
from pathlib import Path


DOCS_URL = "https://docs.duckframework.com"
DOCS_DIR = Path(__file__).parent.parent
DOCS_SOURCE_DIRS = ( "source", "source/api")

# Set a testing directory as Duck settings to avoid SettingsError
os.environ["DUCK_SETTINGS_MODULE"] = "duck.etc.structures.projects.testing.web.settings"


def generate_sitemap():
    """
    This must be called after sphinx build.
    
    The sitemap.xml is placed in `build/html`.
    """
    from duck.logging import console
    from duck.contrib.sitemap import SitemapBuilder
    
    urls = set()
    
    for source_dir in DOCS_SOURCE_DIRS:
        try:
            abs_dir = DOCS_DIR / source_dir
            for entry in os.scandir(abs_dir):
                if entry.is_file():
                    filename = entry.name
                    docname = None
                    
                    if filename == "index.rst":
                        docname = ""
                        
                    elif filename.endswith(".md"):
                        docname = filename.replace(".md", "")
                        
                    elif filename.endswith(".html"):
                        docname = filename.replace(".html", "")
                   
                    elif filename.endswith(".rst"):
                        docname = filename.replace(".rst", "")
                        
                    if source_dir == "source":
                        # This is the root source directory for main docs.
                        # Check if docname is set.
                        if docname is not None:
                            urls.add(f"{DOCS_URL}/{docname}")
                    
                    elif source_dir == "source/api":
                        # This is the source directory for API docs.
                        # This directory contains only html files.
                        # Check if docname is set.
                        if docname is not None:
                            urls.add(f"{DOCS_URL}/api/{docname}")
                    
                    else:
                        raise ValueError(f"Unknown source directory '{source_dir}', expected 'source' or 'source/api'.")
        
        except FileNotFoundError as e:
                console.log(f"Caught an error whilst scanning source dirs: {e}", level=console.WARNING)                
        
    # Build the sitemap.
    sitemap_filepath = DOCS_DIR / "build/html/sitemap.xml"
    builder = SitemapBuilder(
        server_url=DOCS_URL, # Parsing None will automatically resolve server URL
        save_to_file=True,
        filepath=sitemap_filepath,
        extra_urls=urls,
    )
    builder.build()
    console.log(f"Sitemap has been saved at {sitemap_filepath}", level=console.DEBUG)
    
