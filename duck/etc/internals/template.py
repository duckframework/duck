"""
Module containing Duck's internal template engine.
"""
from functools import lru_cache
from typing import (
    List,
    Dict,
    Any,
)

from duck.http.request import HttpRequest
from duck.http.response import TemplateResponse
from duck.storage import duck_storage
from duck.utils.path import joinpaths, sanitize_path_segment
from duck.template.environment import Jinja2Engine
from duck.template.loaders import Jinja2FileSystemLoader


def internal_render(
    request: HttpRequest,
    template: str,
    context: Dict[Any, Any] = {},
    **kwargs,
) -> TemplateResponse:
    """
    Function to render internal templates.
    
    Args:
        request (HttpRequest): The request object.
        template (str): The Jinja2 template.
        context (dict, optional): The context dictionary to pass to the template. Defaults to an empty dictionary.
        **kwargs: Additional keyword arguments to parse to TemplateResponse.

    Returns:
        TemplateResponse: The response object with the rendered content.
    """
    template = sanitize_path_segment(template).lstrip("/") if template else template
    engine = InternalJinja2Engine.get_default()
    
    return TemplateResponse(
        request=request,
        template=template,
        context=context,
        engine=engine,
        **kwargs,
    )


class InternalJinja2FileSystemLoader(Jinja2FileSystemLoader):
    def global_template_dirs(self) -> List[str]:
        # Expose the base template dir.
        # Templates inside here doesn't need appname prefix for template resolving.
        return [joinpaths(duck_storage, "etc/templates")]
    
    def blueprint_template_dirs(self):
        # Only expose global template dirs no blueprints
        return []


class InternalJinja2Engine(Jinja2Engine):
    """
    InternalJinja2TemplateEngine class representing duck's internal template engine,
    meaning this engine is focused only on retreiving templates that are within the internal
    `Duck` storage.
    """
    @classmethod
    @lru_cache(maxsize=1)
    def get_default(self):
        """
        Returns the default internal duck engine.
        """
        # in short, this returns InternalDuckEngine instance with default settings
        return InternalJinja2Engine(loader=InternalJinja2FileSystemLoader())
