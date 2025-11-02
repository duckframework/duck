"""
Module containing template specific classes.
"""

import os
import pathlib
import jinja2

from functools import partial, lru_cache
from typing import (
    Dict,
    List,
    Optional,
    Union,
    Any,
)

from duck.exceptions.all import (
    TemplateError,
    TemplateNotFound,
    SettingsError,
    DisallowedAction,
)
from duck.template.templatetags import (
    TemplateFilter,
    TemplateTag,
)
from duck.utils.path import joinpaths, normalize_url_path
from duck.utils.importer import import_module_once
from duck.settings import SETTINGS


@lru_cache(maxsize=1)
def default_jinja2_engine() -> "Jinja2Engine":
    """
    Returns the default Jinja2 template engine. This caches the result by default.
    """
    return Jinja2Engine.get_default()


@lru_cache(maxsize=1)
def default_django_engine() -> "DjangoEngine":
    """
    Returns the default Django template engine. This caches the result by default.
    """
    return DjangoEngine.get_default()


class Template:
    """
    Template class for all base templates.
    """
    __slots__ = {
        "context",
        "name",
        "origin",
        "engine",
    }
    def __init__(
        self,
        context: Optional[Dict] = None,
        name: Optional[str] = None,
        origin: Optional[str] = None,
        engine: "Engine" = None,
    ):
        """
        Initialize template class.

        Args:
            context (dict, optional): The template context
            name (str, optional): The name of the template. Name will be resolved from origin.
            origin (str, optional): The asolute template path.
            engine (Engine): The template engine.
        """
        self.context = context or {}
        self.origin = origin
        self.name = name or pathlib.Path(origin).basename() if origin else name
        self.engine = engine or Engine.get_default()
        
    def render_template(self) -> str:
        return self.engine.render_template(self)


class Engine:
    """
    Engine class for templates.

    Notes:
        For all engines, Duck internal and custom template tags and filters are enabled by default.
    """
    
    @classmethod
    @lru_cache(maxsize=1)
    def get_default(cls):
        """
        Returns the default template engine, i.e. DjangoEngine.
        """
        return DjangoEngine()
        
    def get_template(self, template_name: str) -> str:
        """
        Custom method for retrieving template data accordingly.
        """
        env = None # The real environment e.g. Jinja2 or Django.
        
        # Normalize template path to make it easy for getting path parts
        template_name = normalize_url_path(template_name)
        
        if isinstance(self, Jinja2Engine):
            env = self.environment
            
        elif isinstance(self, DjangoEngine):
            env = self._django_engine
        
        else:
            raise TemplateError("Unknown engine, expected DjangoEngine or Jinja2Engine for self.")
        
        # First lookup for template in global dirs.
        return env.get_template(template_name)
        
    def render_template(self, template: Template):
        """
        Returns rendered content.
        """
        raise NotImplementedError("Implement method `render_template`.")


class Jinja2Engine(Engine):
    """
    Jinja2 engine class.
    """
    __slots__ = {
        "_duck_templatetags",
        "custom_templatetags",
        "environment",
        "_jinja2__environment",
        "loader",
    }
    def __init__(
        self,
        autoescape: bool = True,
        custom_templatetags: Optional[List[Union[TemplateTag, TemplateFilter]]] = None,
        environment: Optional[jinja2.Environment] = None,
        loader: Any = None,
    ):
        from duck.settings.loaded import SettingsLoaded
        from duck.template.loaders import Jinja2FileSystemLoader, BaseLoader # Best for Duck use-case
        
        self._duck_templatetags = SettingsLoaded.ALL_TEMPLATETAGS
        self.autoescape = autoescape
        self.custom_templatetags = custom_templatetags or []
        self.loader = loader or Jinja2FileSystemLoader()
        self.environment = environment or self.get_default_environment()
        
        if not isinstance(self.loader, BaseLoader):
            raise TypeError(f"Loader must be a subbclass of BaseLoader not {type(loader)}")
            
        # Setup jinja2 environment.
        self.setup_environment()

    def get_default_environment(self) -> jinja2.Environment:
        """
        Returns the appropriate jinja2 environment.
        """
        
        if not hasattr(self, "_jinja2__environment"):
            self._jinja2__environment = jinja2.Environment(loader=self.loader)
        return self._jinja2__environment

    def apply_templatetags(
        self,
        templatetags: Optional[List[Union[TemplateTag, TemplateFilter]]] = None,
     ):
        """
        This applies template tags or filters to the jinja2 environment.
        
        Args:
            templatetags (Optional[List[Union[TemplateTag, TemplateFilter]]],): List of template tags or filters.
        """
        templatetags = templatetags or []
        
        for tag_or_filter in templatetags:
            tag_or_filter.register_in_jinja2(self.environment)
    
    def setup_environment(self):
        """
        Setups the jinja2 environment.
        """
        templatetags = self._duck_templatetags + self.custom_templatetags
        self.environment.autoescape = self.autoescape
        
        # Apply tags and filters available in Duck project.
        self.apply_templatetags(templatetags)
        
    def render_template(self, template: Template) -> str:
        """
        This renders a template into static content.

        Args:
            template (Template): The template object.

        Returns:
            rendered_template (str): Rendered template as string
        """
        if not isinstance(template, Template):
            raise TemplateError(f"The template object must be an instance of Template not {type(template)}")
            
        try:
            jinja2_template = self.get_template(template.name)
            return jinja2_template.render(template.context)
        
        except jinja2.exceptions.TemplateNotFound as e:
            raise TemplateNotFound(f"If using a blueprints, ensure that `blueprint.enable_template_dir=True`: {e}")
            
        except Exception as e:
            raise TemplateError(f"Error rendering template `{template.origin or template.name or template}`: {e}")


class DjangoEngine(Engine):
    """
    Django engine class.
    """
    
    __slots__ = {
        "_duck_templatetags",
        "autoescape",
        "libraries",
        "_django_engine",
        "_imported_django_settings_module",
        "_django__engine",
        "loaders",
    }
    
    def __init__(
        self,
        autoescape: bool = True,
        libraries: Optional[List[str]] = None,
        _django_engine: Optional[Any] = None,
        loaders: List[str] = None,
    ):
        self._duck_templatetags: List[str] = ["duck.backend.django.templatetags.ducktags"]  # all internal and custom template tags and filters
        self.autoescape = autoescape
        self.libraries = libraries
        self._django_engine = _django_engine or self.get_default_django_engine()
        self.loaders = loaders or ["duck.template.loaders.DjangoFileSystemLoader"] 
        self.setup_django_engine()

    @classmethod
    @lru_cache(maxsize=1)
    def get_default(cls):
        """
        Returns the default Django engine.
        """
        return DjangoEngine()

    def get_default_django_engine(self):
        """
        Returns the django default template engine.
        """
        from django.template import Engine as _Engine
        from django.core.exceptions import ImproperlyConfigured
        
        # Attempt to import the local Django project settings
        try:
            if not hasattr(self, '_imported_django_settings_module'):
                import_module_once(SETTINGS['DJANGO_SETTINGS_MODULE'])
                self._imported_django_settings_module = True
        except (ImportError, KeyError, ModuleNotFoundError):
            raise SettingsError("Please make sure that the Django project structure for Duck is correct for you to use Django template engine.")
        
        if not hasattr(self, "_django__engine"):
            try:
                self._django__engine = _Engine.get_default()
            except ImproperlyConfigured:
                raise SettingsError(
                    "Please make sure that the Django project structure for Duck is correct for you to use Django template engine. "
                    "Also ensure that DJANGO_SETTINGS_MODULE is set correctly in Duck settings.py."
                )
        return self._django__engine

    def apply_templatetags(
        self,
        builtin_libraries: Optional[List[str]] = None,
        custom_libraries: Optional[Dict[str, str]] = None
     ):
        """
        This applies template tags or filters to the engine.
        """
        if builtin_libraries:
            # register builtin libraries to engine.
            builtins = self._django_engine.get_template_builtins(builtin_libraries)
            self._django_engine.builtins.extend(builtin_libraries)
            self._django_engine.template_builtins.extend(builtins)

        if custom_libraries:
            # add custom libraries
            libraries = self._django_engine.get_template_libraries(custom_libraries)
            self._django_engine.libraries.update(custom_libraries)
            self._django_engine.template_builtins.extend(libraries)
    
    def setup_django_engine(self):
        """
        Setups the inner django engine.
        """
        self._django_engine.autoescape = self.autoescape
        self._django_engine.loaders.extend(self.loaders)
        
        # Apply template tags and filters.
        self.apply_templatetags(
            builtin_libraries=self._duck_templatetags,
            custom_libraries=self.libraries,
        )
        
    def render_template(self, template: Template) -> str:
        """
        Returns rendered content.
        """
        from django.template import Context, TemplateDoesNotExist
        
        if not isinstance(template, Template):
            raise TemplateError(f"The template object must be an instance of Template not {type(template)}")
            
        try:
            django_template = self.get_template(template.name)
            return django_template.render(Context(template.context))
        
        except TemplateDoesNotExist as e:
            raise TemplateNotFound(f"Template not found. If using a blueprints, ensure that `blueprint.enable_template_dir=True`: {e}")
            
        except Exception as e:
            raise TemplateError(f"Error rendering template `{template.origin or template.name or template}`: {e}")
