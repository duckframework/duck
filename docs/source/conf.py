import os
import ast
import sys
import json
import pathlib
import subprocess
import datetime


# METADATA
DUCK_HOMEPAGE = "https://duckframework.xyz"
DUCK_PACKAGE_RELATIVE_PATH = "../../duck"

# Path to the duck package's __init__.py
DUCK_INIT_PATH = (
    pathlib.Path(__file__).resolve().parent / DUCK_PACKAGE_RELATIVE_PATH / "__init__.py"
)


# Entry point to sphinx
def setup(app):
    pass


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


# -- Project information -----------------------------------------------------

# Extract metadata from duck/__init__.py
metadata = read_metadata_from_init(DUCK_INIT_PATH)
project = "Duck"
copyright = f"{datetime.datetime.now().year}, Duck Framework"
author = metadata.get("__author__", "Brian Musakwa")
release = metadata.get("__version__", "")
email = metadata.get("__email__", "digreatbrian@gmail.com")
favicon_url = DUCK_HOMEPAGE + "/favicon.ico"


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
html_css_files = ["css/custom.css"]
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
