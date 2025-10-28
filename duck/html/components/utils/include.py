"""
Module containing function for including bulk HTML components in a module.
"""
import inspect

from typing import List, Dict
from functools import lru_cache

from duck.html.components import HtmlComponent
from duck.utils.string import is_pascal_case
from duck.utils.importer import import_module_once


BASE_MODULE = "duck.html.components"
BUILTIN_COMPONENTS = [
    f"{BASE_MODULE}.{module}" for module in [
        "page",
        "paragraph",
        "heading",
        "snackbar",
        "progressbar",
        "section",
        "card",
        "icon",
        "link",
        "form",
        "script",
        "style",
        "input",
        "textarea",
        "select",
        "image",
        "video",
        "hero",
        "container",
        "checkbox",
        "navbar",
        "footer",
        "button",
        "modal",
        "lively",
        "code",
        "label",
        "fileinput",
        "table_of_contents",
    ]
]


@lru_cache
def components_include(modules: List[str]) -> Dict[str, str]:
    """
    This looks up HTML components in the provided modules and returns a dictionary containing the components found.

    Args:
        modules (List[str]): The list of module names containing HTML components in PascalCase.

    Returns:
        Dict[str, str]: A dictionary mapping component names to their full module path.
    """
    from duck.html.components import ComponentError
    
    components = {}
    
    for mod_name in modules:
        try:
            mod = import_module_once(mod_name)  # Ensure module is imported
        except Exception as e:
            raise ComponentError(f"Error importing component library '{mod_name}': {e} ")
            
        if not mod:
            continue  # Skip if import fails

        for attr_name in dir(mod):
            if is_pascal_case(attr_name):  # Ensure it's PascalCase
                cls = getattr(mod, attr_name)
                if inspect.isclass(cls) and issubclass(cls, HtmlComponent):
                    components[attr_name] = f"{mod_name}.{attr_name}"  # Correct dictionary assignment
    return components
