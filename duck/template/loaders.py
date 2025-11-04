"""
Custom template loaders for Duck.
"""
import os

from functools import lru_cache
from typing import (
    List,
    Optional,
    Tuple,
    Generator,
    Callable,
)

from jinja2.loaders import BaseLoader as Jinja2BaseLoader
from django.template.loaders.base import Loader as DjangoBaseLoader

from duck.routes import (
    Blueprint,
    BlueprintJoinPathError,
    BlueprintJoinPathNameNoMatch,
    blueprint_joinpath,
)
from duck.settings import SETTINGS
from duck.utils.path import joinpaths


class BaseLoader:
    """
    Base Loader class.
    """
    
    def blueprint_template_dirs(self) -> Generator[Tuple[Blueprint, str], None, None]:
        """
        Returns a generator for the template directories for all blueprints.
        """
        from duck.settings.loaded import SettingsLoaded
        
        for blueprint in SettingsLoaded.BLUEPRINTS:
            if blueprint.enable_template_dir:
                template_dir = joinpaths(blueprint.root_directory, blueprint.template_dir)
                yield (blueprint, template_dir)
                
    def global_template_dirs(self) -> List[str]:
        """
        Returns the global template directories for entire app scope.
        """
        template_dirs = SETTINGS["TEMPLATE_DIRS"] or []
        return template_dirs


class Jinja2FileSystemLoader(BaseLoader, Jinja2BaseLoader):
    """
    Custom File System Loader for Jinja2.
    """
    
    def get_source(self, environment, template: str) -> Tuple[str, str, Callable]:
        # This is needed by jinja2
        from jinja2 import TemplateNotFound
        
        def template_found(template_path: str) -> Tuple[str, str, Callable]:
            """
            Returns the appropriate data when a template is found.
            """
            mtime = os.path.getmtime(template_path)
            source = None 
            
            try:
                with open(template_path, "r") as fd:
                    source = fd.read()
            except FileNotFoundError:
                # Template not found anymore, maybe deleted
                raise TemplateNotFound(f"Template `{template}` doesn't exist anymore.")
            return (source, template_path, lambda: mtime == os.path.getmtime(template_path))
        
        # First lookup for template in global_template_dirs
        global_template_dirs = self.global_template_dirs()
        
        for template_dir in global_template_dirs:
            template_path = joinpaths(template_dir, template)
            
            if os.path.isfile(template_path):
                # Template found
                return template_found(template_path)
        
        # Template not found, lookup in blueprint template dirs
        original_template_name = template
        
        for blueprint, template_dir in self.blueprint_template_dirs():
            try:
                template_path = blueprint_joinpath(template_dir, original_template_name, blueprint)
            except (BlueprintJoinPathError, BlueprintJoinPathNameNoMatch, ValueError):
                # Raised if maybe template could not be resolved.
                continue
            
            if os.path.isfile(template_path):
                return template_found(template_path)
        
        # Template not found anywhere
        raise TemplateNotFound(f"Template `{template}` not found anywhere in global template dirs or blueprint template dirs.")


class DjangoFileSystemLoader(BaseLoader, DjangoBaseLoader):
    """
    Custom File System Loader for Django.
    """
    def get_contents(self, origin):
        from django.template import TemplateDoesNotExist
        
        if os.path.isfile(origin.name):
            try:
                with open(origin.name, encoding=self.engine.file_charset) as fd:
                    contents = fd.read()
                return contents
            except FileNotFoundError:
                # File not found anymore, may be deleted.
                raise TemplateDoesNotExist(f"Template `{origin.name}` doesn't exist anymore.")
                
        # Source not found
        raise TemplateDoesNotExist(f"Source template `{origin.name}` does not exist.")
         
    def get_template_sources(self, template_name: str) -> Generator["Origin", None, None]:
        # Must be implemented for django
        # Provide all possible sources.
        from django.template import Origin
        
        # First iter in global_template_dirs
        global_template_dirs = self.global_template_dirs()
        
        for template_dir in global_template_dirs:
            template_path = joinpaths(template_dir, template_name)
            # Yield source
            yield Origin(
                name=template_path,
                template_name=template_name,
                loader=self,
            )
            
        # Also yield blueprint template sources
        original_template_name = template_name
        
        for blueprint, template_dir in self.blueprint_template_dirs():
            try:
                template_path = blueprint_joinpath(template_dir, original_template_name, blueprint)
            except (BlueprintJoinPathError, BlueprintJoinPathNameNoMatch, ValueError):
                # Raised if maybe template could not be resolved.
                continue
                
            # Yield source
            yield Origin(
                name=template_path,
                template_name=template_name,
                loader=self,
            )
