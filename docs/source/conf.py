import os
import sys
import json
import pathlib


# METADATA
DUCK_HOMEPAGE = "https://duckframework.xyz"
DUCK_PACKAGE_RELATIVE_PATH = "../../duck"


# Ensure sphinx finds our package
sys.path.insert(0, os.path.abspath("../../"))


# The following imports should succeed if source directory for duck is included in sys.path
from duck import (
    __version__,
    __author__,
    __email__,
)


# Function to prepare the versions list
def prepare_versions(versions):
    """
    Processes the versions dictionary into a list for template consumption.

    Args:
        versions (dict): The raw versions dictionary from sphinx-multiversion.

    Returns:
        list[dict]: A list of dictionaries containing version details.
    """
    version_list = []

    if versions:  # Check if 'versions' is defined and not empty
        for version in versions:
            version_list.append({
                'name': version.name,
                'url': version.url,
                'version': version.version,
                'release': version.release,
            })
    
    return version_list


def on_context(app, pagename, templatename, context, doctree):
    """
    Hook called when page has context.
    """
    # Get the versions provided by Sphinx Multiversion
    raw_versions = context.get('versions')  # Retrieve raw `versions` dictionary
    
    # Prepare the versions list
    context['version_list'] = prepare_versions(raw_versions)
   

# Entry point to sphinx
def setup(app):
    app.connect("html-page-context", on_context)
    app.add_css_file("_static/css/custom.css")


# -- Project information -----------------------------------------------------
project = "Duck"
copyright = f"2026, Duck Framework"
author = __author__
release = __version__
email = __email__


# -- General configuration ---------------------------------------------------
extensions = [
    "autodocx",                     # Use sphinx-autodocx for documentation
    "myst_parser",                  # For parsing MyST markdown
    "sphinx.ext.viewcode",          # Add links to source code
    "sphinx.ext.todo",              # Include TODOs in documentation
    "sphinx.ext.mathjax",           # For rendering LaTeX math
    "sphinx.ext.intersphinx",       # For linking to other projects
    "sphinx.ext.autosummary",       # Automatically generate summary tables
    "sphinx_design",                # Useful components for building beautiful docs
    "sphinx_tabs.tabs",             # Tab functionality for documentation
    "sphinx_search.extension",      # Add search functionality
    "sphinx_autodoc_typehints",     # Show type hints in descriptions
    "sphinx_multiversion", # For docs multiversioning
]


# Sphinx multiversion configuration
smv_tag_whitelist = r'^v\d+\.\d+(\.\d+)?$'
smv_branch_whitelist = r'^(main|stable)$'
smv_remote_whitelist = r'^origin$'

# Where versions are mounted
#smv_released_pattern = r'^tags/v\d+\.\d+(\.\d+)?$'
smv_rewrite_config = {
    "main": "latest",  # Rewrite 'main' branch to 'latest'
}


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
    "*/tests/*",                      # Exclude test folders
    "*/migrations/*",                  # Exclude Django migrations
    "*/experimental/*",                # Exclude experimental code
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
html_theme_options = {
    "logo_light": "_static/images/duck-logo.png",
    "logo_dark": "_static/images/duck-logo.png",
    "show_breadcrumbs": True,
    "show_prev_next": True,
    "show_scrolltop": True,
    "main_nav_links": {
        "Go Home": DUCK_HOMEPAGE,
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
