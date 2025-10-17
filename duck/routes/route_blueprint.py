"""
Module for route arrangements using Blueprint. This acts as a set of routes, much like how Flask's blueprints organize routes in a module.

Example:

```py
app = Blueprint(location=__file__, name="products", urlpatterns=...)
```

``` {note}
To resolve a url for a blueprint, the name should be `{blueprint_name}.{path_name}` .e.g.,
  `"api.followers"` for blueprint named `api` and a path registered with name `followers`
```
"""

import pathlib

from typing import List, Optional

from duck.urls import (
    URLPattern,
    path,
    re_path,
)
from duck.exceptions.all import BlueprintError
from duck.utils.path import joinpaths


class Blueprint:
    """
    Mini application for storing route information.
    """

    __names = []
    """
	Names of all created blueprints.
	"""

    def __init__(
        self,
        location: str,
        name: str,
        urlpatterns: Optional[List[URLPattern]] = None,
        prepend_name_to_urls: bool = True,
        static_dir: str = "static",
        template_dir: str = "templates",
        enable_static_dir: bool = True,
        enable_template_dir: bool = True,
        is_builtin: bool = False,
    ):
        """
        Initialize the Blueprint.
        
        Args:
            location (str): The absolute path to where the blueprint is located.
            name (str): A valid string representing the blueprint's name.
            urlpatterns (Optional[List[URLPattern]]): List of urlpatterns created using duck.urls.path or re_path.
            prepend_name_to_urls (bool): Whether to prepend name to urlpatterns. Defaults to True.
            static_dir (str): The location of static files within the blueprint base directory.
            template_dir (str): The template directory for the blueprint.
            enable_static_dir (bool): Boolean on whether to enable commands like `duck collectstatic` to access the blueprint staticfiles.
            enable_template_dir (bool): Expose the template dir for template resolving.
            is_builtin (bool): Flag the route blueprint as an internal builtin blueprint, Defaults to False (optional).
        """

        if not (name and isinstance(name, str)):
            raise BlueprintError(
                "Name for the Blueprint must be a valid string"
            )

        elif name in self.__names:
            raise BlueprintError(
                f'Blueprint with the same name already exists. Conflicting name: "{name}".'
            )
        else:
            type(self).__names.append(name)
        
        self.location = location
        self.name = name
        self.urlpatterns = []
        self.prepend_name_to_urls = prepend_name_to_urls
        self.static_dir = static_dir
        self.template_dir = template_dir
        self.enable_static_dir = enable_static_dir
        self.enable_template_dir = enable_template_dir
        self.is_builtin = is_builtin
        
        urlpatterns = urlpatterns or []

        try:
            for urlpattern in urlpatterns:
                self.add_urlpattern(urlpattern)
        except Exception as e:
            raise BlueprintError(
                "Error while trying to add urlpatterns provided, ensure all urlpatterns are in correct format."
            ) from e

    def __repr__(self):
        return f'<{self.__class__.__name__} name="{self.name}", location=...>'

    @property
    def root_directory(self) -> str:
        """
        Returns the absolute blueprint root path.
        """
        root = str(pathlib.Path(self.location).parent)
        return root
    
    @property
    def root_directory_name(self) -> str:
        """
        Returns the blueprint root path name.
        """
        location = pathlib.Path(self.location)
        relative_root = location.relative_to(location.parent)
        return relative_root.name
        
    def add_urlpattern(
        self,
        urlpattern: URLPattern,
    ):
        """
        Adds a url pattern to the blueprint urlpatterns collection.
        
        Notes:
            - This reconfigures the urlpattern to belong to the blueprint before adding
              the url pattern.
        """
        name = urlpattern["name"]
        route = urlpattern["url"]
        
        if self.prepend_name_to_urls:
            route = joinpaths(self.name, route)
            
        if name:
            name = f"{self.name}.{name}"
        else:
            name = f"{self.name}.route_{len(self.urlpatterns) + 1}"  # Auto-generate names
         
        urlpattern["url"] = route
        urlpattern["name"] = name
        self.urlpatterns.append(urlpattern)
