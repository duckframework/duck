"""
Module, object and variable importation module.
"""
import sys
import importlib

from functools import lru_cache


def import_module_once(module_name, package: str = None):
    """
    Import a module only once.
    """
    mod = sys.modules.get(module_name, None)
    if not mod:
        mod = importlib.import_module(module_name, package=package)
        sys.modules[module_name] = mod
    return mod


def _is_partial_module(mod) -> bool:
    """
    Best-effort check for a partially initialized module.
    """
    try:
        mod_spec = getattr(mod, "__spec__", None)
        if mod_spec is None:
            return False
        return getattr(mod_spec, "_initializing", False)
    except Exception:
        return False


@lru_cache
def x_import(object_path, package: str = None):
    """
    Function to import an object or class from a path e.g. `os.path.Path`
    """
    if object_path.count(".") < 1:
        return import_module_once(object_path, package=package)
    
    module_path, obj_name = object_path.rsplit(".", 1)
    module = import_module_once(module_path, package=package)
    
    try:
        return getattr(module, obj_name)
    except AttributeError as e:
        # Avoid recursive reload loops while the module is still initializing.
        if _is_partial_module(module):
            raise e

        # On reload, module can be partially initialized; retry after reload once.
        try:
            module = importlib.reload(module)
            return getattr(module, obj_name)
        except Exception:
            raise e

