"""
Module, object and variable importation module.
"""
import os
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


@lru_cache
def x_import(object_path, package: str = None):
    """
    Function to import an object or class from a path e.g. `os.path.Path`
    """
    if object_path.count(".") < 1:
        return import_module_once(object_path, package=package)
    module_path, obj_name = object_path.rsplit(".", 1)
    module = import_module_once(module_path, package=package)
    return getattr(module, obj_name)
