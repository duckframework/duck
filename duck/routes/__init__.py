"""
Module for route-specific actions.
"""
import os
import pathlib

from typing import List

from duck.routes.route_blueprint import Blueprint
from duck.routes.route_registry import RouteRegistry
from duck.exceptions.all import (
    RouteError,
    BlueprintError,
)
from duck.urls import URLPattern
from duck.utils.path import joinpaths, sanitize_path_segment


class BlueprintJoinPathError(BlueprintError):
    """
    Raised on function `blueprint_joinpath` if blueprint_subdir is not not really a subpath or doesn't belong to blueprint root directory.  
    """


class BlueprintJoinPathNameNoMatch(BlueprintJoinPathError):
    """
    Raised on function `blueprint_joinpath` If path's root name is not equal to blueprint name. Handle this to avoid unnecessary lookup for unresolvable paths.
    """


def register_urlpatterns(urlpatterns: List[URLPattern]):
    """
    Register some application urlpatterns.
    """
    
    # register route urlpatterns
    for urlpattern in urlpatterns:
        try:
            if urlpattern.regex:
                # this is a regex urlpattern
                url, handler, name, methods = (
                        urlpattern['url'], 
                        urlpattern['handler'],
                        urlpattern['name'],
                        urlpattern['methods']
                  )
                RouteRegistry.regex_register(
                       url, handler, name, methods,
                )
            else:
                # this is a normal urlpattern
                url, handler, name, methods = (
                        urlpattern['url'], 
                        urlpattern['handler'],
                        urlpattern['name'],
                        urlpattern['methods']
                )
                RouteRegistry.register(
                        url, handler, name, methods,
                )
        except Exception as e:
            raise RouteError(f"Error registering URL pattern '{urlpattern}': {e}")


def register_blueprints(blueprints: List[Blueprint]):
    """
    Register some application blueprints.
    """
    
    # Register route blueprint.urlpatterns
    for blueprint in blueprints:
        try:
            register_urlpatterns(blueprint.urlpatterns)
        except Exception as e:
            raise BlueprintError(f"Error registering urlpatterns for blueprint '{blueprint}' ") from e


def blueprint_joinpath(blueprint_subdir: str, path: str, blueprint: Blueprint) -> str:
    """
    Joins directory to form a final blueprint resolvable path.
    
    This makes it easy to resolve sub blueprint paths/files.
    
    Args:
        blueprint_subdir (str): This is the absolute subdirectory to the blueprint root directory.
        path (str): The path to join with, will be joined correctly without the path rootname if blueprint name == path rootname.
        blueprint (Blueprint): The blueprint with the blueprint_subdir.
    
    Raises:
        ValueError: If path is not relative path. 
        BlueprintJoinPathError: If blueprint_subdir is not not really a subpath or doesn't belong to blueprint root directory. 
        BlueprintJoinPathNameNoMatch: If path's root name is not equal to blueprint name. Handle this to avoid unnecessary lookup for unresolvable paths.
        
    Example:
    
    ```py
    # The blueprint_subdir can be any absolute blueprint subpath e.g. template_dir/static_dir
    blueprint_subdir = "/some/absolute/blueprint/subpath"
    
    # This is the target blueprint with the base_dir e.g. template dir
    blueprint = SomeBlueprint(...)
    
    # This is a path of a file you wanna resolve inside the blueprint_subdir
    # For this to be resolvable in blueprint subdir, Blueprint name must be the first path part. 
    path = "blueprint_name/some/file"
    
    # This works if the blueprint name == path root name even if the blueprint path is different.
    print(blueprint_joinpath(base_dir, path, blueprint)) # Outputs: /some/absolute/blueprint/subpath/some/file
    ```
    """
    
    # Normalize path and remove the first backslash so that pathlib can interpret
    # `parts` correctly.
    path = sanitize_path_segment(path).lstrip('/') 
    
    # Now continue.
    path = pathlib.Path(path)
    blueprint_subdir = pathlib.Path(blueprint_subdir.replace("\\", "/"))
    path_root_name = path.parts[0].strip('/')
    
    if path.is_absolute():
        raise ValueError("The `path` argument must be a relative path.")
    
    try:
        # Find if the blueprint_subdir belongs to the blueprint root directory.
        _ = blueprint_subdir.relative_to(str(blueprint.root_directory).replace("\\", "/"))
    except ValueError as e:
        raise BlueprintJoinPathError(str(e))
    
    if path_root_name != blueprint.name:
        raise BlueprintJoinPathNameNoMatch(
            "The path's name doesn't match with blueprint name, "
            "this may mean this path is not meant to be resolved at this blueprint subpath."
        )
    
    # Remove the path's root name and join with blueprint subpath.
    path = str(path).lstrip('/').lstrip(path_root_name)
    return joinpaths(blueprint_subdir, path)
