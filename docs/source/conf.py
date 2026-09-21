import os
import ast
import sys
import json
import pathlib
import subprocess
import datetime


# METADATA
DUCK_HOMEPAGE = "https://duckframework.com"
DUCK_DOCS_URL = "https://docs.duckframework.com"
DUCK_DOCS_LATEST_VERSION = "main"
DUCK_PACKAGE_RELATIVE_PATH = "../../duck"

# Metadata for sitemap generation
DOCS_DIR = pathlib.Path(__file__).parent.parent
DOCS_SOURCE_DIRS = ( "source", "source/api")

# Path to the duck package's __init__.py
DUCK_INIT_PATH = (
    pathlib.Path(__file__).resolve().parent / DUCK_PACKAGE_RELATIVE_PATH / "__init__.py"
)

# Sitemap index configuration
SITEMAP_INDEX_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{entries}
</sitemapindex>
"""
SITEMAP_INDEX_ENTRY_TEMPLATE = """  <sitemap>
    <loc>{loc}</loc>
    <lastmod>{lastmod}</lastmod>
  </sitemap>"""


# This must be called before any use of the duck.settings module e.g. through duck.app
os.environ["DUCK_SETTINGS_MODULE"] = "duck.etc.structures.projects.testing.web.settings"
os.environ["DJANGO_SETTINGS_MODULE"] = "duck.etc.structures.projects.testing.web.backend.django.duckapp.duckapp.settings"


# Entry point to sphinx
def setup(app):
    def on_html_page_context(app, template_name, template, context, _):
        context["DUCK_HOMEPAGE"] = DUCK_HOMEPAGE
        context["DUCK_DOCS_URL"] = DUCK_DOCS_URL
    app.connect("html-page-context", on_html_page_context)
    app.connect("build-finished", on_build_finished)
    

def on_build_finished(app, exception):
    """
    Called when Sphinx finishes building the documentation.

    Args:
        app: The Sphinx application object.
        exception: Exception raised during build, if any.
    """
    generate_sitemap(app.outdir)


def read_metadata_from_init(init_path):
    """
    Reads and extracts metadata variables (e.g., __version__, __author__, __email__)
    from the duck/__init__.py file as string values.

    Args:
        init_path (pathlib.Path): The file path of the package's __init__.py file.

    Returns:
        dict: A dictionary containing metadata like __version__, __author__, and __email__.
    """
    metadata = {}
    
    with open(init_path, "r", encoding="utf-8") as f:
        for line in f:
            # Look for __<name>__ = '<value>'
            if line.startswith("__") and "=" in line:
                try:
                    # Parse the line into an abstract syntax tree (AST) for safety
                    node = ast.parse(line).body[0]
                    if isinstance(node, ast.Assign):
                        key = node.targets[0].id
                        value = node.value.s  # Extract the string value
                        metadata[key] = value
                except Exception:
                    pass  # Skip malformed lines
    return metadata


def sitemap_sort_key(url: str, base_url: str) -> tuple[int, str]:
    """
    Sort sitemap URLs so that top-level pages appear before nested pages.

    Args:
        url: Absolute documentation URL.
        base_url: Base URL of the version this sitemap is being built for.

    Returns:
        A tuple used for sorting.
    """
    relative = url.removeprefix(f"{base_url}/")

    # Root page always comes first.
    if relative == base_url or url == base_url:
        return (0, "")

    # Pages without subdirectories come before nested pages.
    depth = relative.count("/")

    return (0 if depth == 0 else 1, relative)
    

def generate_sitemap(outdir: str) -> None:
    """
    Generate a sitemap from the built HTML documentation.

    This function scans the generated HTML output instead of the source files,
    ensuring that only pages actually published by Sphinx are included. It
    automatically supports nested directories and future documentation
    structure changes without requiring updates.

    sphinx-multiversion builds each version into its own subdirectory and
    fires build-finished once per version, with `app.outdir` pointing at that
    version's own output folder -- so the version being built is read from
    `outdir`'s name rather than assumed. Each build writes a sitemap scoped to
    that version, saved inside the version's own output directory (served at
    `/<version>/sitemap.xml`), then rebuilds the root sitemap index from
    every version folder that has one -- see generate_sitemap_index.

    Args:
        outdir: Path to the generated HTML output directory for the version
            currently being built (typically `app.outdir`).
    """
    from duck.contrib.sitemap import SitemapBuilder
    from duck.logging import console
    from duck.utils.path import joinpaths

    # Initialize the output directory, version, and URL collection.
    outdir = pathlib.Path(outdir)
    version_name = outdir.name
    version_base_url = f"{DUCK_DOCS_URL}/{version_name}"
    urls = set()
    
    if str(outdir).endswith("build/html"):
        # We are in build/html
        # No need for sitemap generation
        return
        
    # Scan all generated HTML files.
    for html_file in outdir.rglob("*.html"):
        relative = html_file.relative_to(outdir)

        # Ignore Sphinx-generated support directories.
        if any(part.startswith("_") for part in relative.parts):
            continue

        # Resolve the documentation URL.
        if relative == pathlib.Path("index.html"):
            # Root page for this version.
            url = version_base_url

        elif relative.name == "index.html":
            # Directory index page.
            url = "/".join([
                version_base_url,
                relative.parent.as_posix(),
            ])

        else:
            # Regular documentation page.
            url = "/".join([
                version_base_url,
                relative.with_suffix("").as_posix(),
            ])

        
        # Add URL to list.
        urls.add(url)

    # Sort URLs
    sorted_urls = sorted(
        urls, key=lambda url: sitemap_sort_key(url, version_base_url)
    )

    # Build the version-specific sitemap, served at /<version>/sitemap.xml.
    version_sitemap_path = joinpaths(outdir, "sitemap.xml")
    
    # Build sitemap
    SitemapBuilder(
        server_url=version_base_url,
        save_to_file=True,
        filepath=version_sitemap_path,
        extra_urls=sorted_urls,
    ).build()

    # Show a debug message.
    console.log(
        f"Sitemap has been saved at {version_sitemap_path}",
        level=console.DEBUG,
    )

    # Rebuild the root sitemap index now that this version's sitemap exists.
    generate_sitemap_index(outdir.parent)


def generate_sitemap_index(build_html_dir: pathlib.Path) -> None:
    """
    Rebuild the root sitemap index from every built version's sitemap.xml.

    The index itself carries no page URLs -- each <sitemap> entry just
    points at that version's own sitemap.xml, which is the real source of
    truth for that version's pages. A version's entry disappears on its own
    once its output folder (or sitemap.xml) is gone, so nothing about
    dropped or renamed versions needs separate tracking here.

    Args:
        build_html_dir: Directory containing one subdirectory per built
            version, each already holding its own sitemap.xml.
    """
    from duck.logging import console
    from duck.utils.path import joinpaths

    versions = sorted(
        child.name
        for child in build_html_dir.iterdir()
        if child.is_dir() and (child / "sitemap.xml").exists()
    )
    
    # Latest version listed first, the rest alphabetically.
    versions.sort(key=lambda v: (v != DUCK_DOCS_LATEST_VERSION, v))

    # Build date
    today = datetime.date.today().isoformat()
    
    # Build entries
    entries = "\n".join(
        SITEMAP_INDEX_ENTRY_TEMPLATE.format(
            loc=f"{DUCK_DOCS_URL}/{version}/sitemap.xml",
            lastmod=today,
        )
        for version in versions
    )
    
    # Build index path
    index_path = joinpaths(build_html_dir, "sitemap.xml")
    
    with open(index_path, "w", encoding="utf-8") as fh:
        fh.write(SITEMAP_INDEX_TEMPLATE.format(entries=entries))

    console.log(
        f"Sitemap index rebuilt at {index_path} ({len(versions)} version(s))",
        level=console.DEBUG,
    )


# Project information

# Extract metadata from duck/__init__.py
metadata = read_metadata_from_init(DUCK_INIT_PATH)
project = "Duck"
copyright = f"{datetime.datetime.now().year}, Duck Framework"
author = metadata.get("__author__", "Brian Musakwa")
release = metadata.get("__version__", "")
email = metadata.get("__email__", "digreatbrian@gmail.com")
favicon_url = DUCK_HOMEPAGE + "/favicon.ico"


# General configuration
extensions = [
    "autodocx", # Use sphinx-autodocx for documentation
    "myst_parser", # For parsing MyST markdown
    "sphinx.ext.viewcode",  # Add links to source code
    "sphinx.ext.todo", # Include TODOs in documentation
    "sphinx.ext.mathjax",  # For rendering LaTeX math
    "sphinx.ext.intersphinx", # For linking to other projects
    "sphinx.ext.autosummary", # Automatically generate summary tables
    "sphinx_design", # Useful components for building beautiful docs
    "sphinx_tabs.tabs", # Tab functionality for documentation
    "sphinx_search.extension", # Add search functionality
    "sphinx_autodoc_typehints", # Show type hints in descriptions
    "sphinx_multiversion", # For docs multiversioning
]


# Sphinx multiversion configuration
smv_tag_whitelist = r'^.*$'  # Match all tags
smv_branch_whitelist = r'^(main|stable)$'
smv_remote_whitelist = r'^origin$'


# Napoleon configuration
napoleon_config = {
    "use_google_docstrings": True,  # Enable Google style docstrings
    "use_numpy_docstrings": False,  # Disable Numpy-style docstrings (set to True if needed)
    "napoleon_include_private_with_doc": True,  # Include private members with docstrings
    "napoleon_include_special_with_doc": True,  # Include special methods (e.g., __init__) with docstrings
    "napoleon_use_ivar": True,  # Use 'ivar' for instance variables
    "napoleon_use_param": True,  # Use 'param' for function parameters in Google style
    "napoleon_use_rtype": True,  # Use 'rtype' for return type in Google style
    "napoleon_preprocess_types": True,  # Automatically process type annotations
    "napoleon_attr_annotations": True,  # Enable attribute annotations for class properties
    "napoleon_use_admonition_for_examples": False,  # Use admonitions for 'Examples' sections
    "napoleon_use_admonition_for_notes": True,
    "napoleon_custom_sections": [
        (".*", "notes_style"),  # Treat everything like "Notes:"
    ]
}

# Autodocx Configuration
autodocx_packages = [
    DUCK_PACKAGE_RELATIVE_PATH,  # Path to our source package
]

autodocx_output_dir = "api"  # Where autodocx should store generated docs
autodocx_render_plugin = "myst"  # Render docstrings using MyST Markdown
autodocx_include_private = True  # Include private members (_ prefixed)
autodocx_include_special = True  # Include special methods (__init__, etc.)
autodocx_sort_names = True  # Sort members alphabetically
autodocx_show_if_no_docstring = True
autodocx_docstring_sections = True

# Exclude specific folders from autodocx
autodocx_exclude = [
    "*/projects/*/backend/django/*",  # Exclude Django backend from all projects
    "*/tests/*",  # Exclude test folders
    "*/migrations/*", # Exclude Django migrations
    "*/experimental/*", # Exclude experimental code
]


# -- MyST Configuration --
myst_enable_extensions = [
    "amsmath",
    "attrs_inline",
    "colon_fence",
    "deflist",
    "dollarmath",
    "fieldlist",
    "html_admonition",
    "html_image",
    "linkify",
    "replacements",
    "smartquotes",
    "strikethrough",
    "substitution",
    "tasklist",
]

# Set MyST list indent to 4 to avoid leading whitespace in lists
myst_list_indent = 4

# Make sure TOC tree entries are included
myst_heading_anchors = 3  # Allows anchor links for headings and includes them in the TOC


# -- Autosummary Configuration --
autosummary_generate = True


# -- Templates & Exclusions --
templates_path = ["_templates"]
exclude_patterns = ["*/projects/*/backend/*", "_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------
html_theme = "sphinxawesome_theme"
html_static_path = ["_static"]
html_css_files = ["css/custom.css"]
html_title = "Duck Framework"
html_baseurl = "https://docs.duckframework.com/main/"
html_theme_options = {
    "logo_light": "_static/images/duck-logo.png",
    "logo_dark": "_static/images/duck-logo.png",
    "show_breadcrumbs": True,
    "show_prev_next": True,
    "show_scrolltop": True,
    "main_nav_links": {
        "Explore the Main Site": DUCK_HOMEPAGE,
    }
}

# Add buttons at the bottom (footer) of the page
html_context = {
    "next_previous_buttons": True  # Enable next/prev buttons in the footer
}

html_search = True

# Enabling syntax highlighting in code blocks
highlight_language = 'python'  # or the language you're using (e.g., 'bash', 'cpp', etc.)
pygments_style = 'friendly'  # or 'monokai', 'friendly', 'colorful', etc. for different themes
