"""
Manages the registration and lifecycle of HTML components, and enables communication
with the browser via WebSocket to dispatch events and execute JavaScript in real-time.
"""
import os

from typing import (
    List,
    Type,
    Any,
    Optional,
)

from pathlib import Path

from duck.shortcuts import not_found404
from duck.urls import path, URLPattern
from duck.utils.path import joinpaths
from duck.settings import SETTINGS
from duck.utils.storage import duck_storage
from duck.utils.importer import x_import
from duck.utils.caching import InMemoryCache
from duck.html.components import Component
from duck.html.components.templatetags import ComponentTag
from duck.html.components.core.exceptions import (
    AlreadyInRegistry,
    ComponentSystemError,
)
from duck.http.response import (
    HttpResponse,
    FileResponse,
)
from duck.template.templatetags import TemplateTagError


class LivelyComponentSystem:
    """
    LivelyComponentSystem class.
    """
    
    registry: InMemoryCache = InMemoryCache(maxkeys=100_000) # cache with LRU eviction lim->100 000 for very busy app.
    """
    Mapping of UIDs to components.
    
    Format: {root_uid: {root_uid: component, child_uid: component, ...}}
    """
    
    @classmethod
    def get_urlpatterns(cls) -> List[URLPattern]:
        """
        Returns the appropriate URL patterns for the whole system.
        """
        ws_view_cls = cls.get_websocket_view_cls()
        
        def serve_staticfiles(request, staticfile: str) -> HttpResponse:
            """
            Function to serve static files for the component system e.g. serving msgpack.js & lively.js.
            """
            staticfile = joinpaths(duck_storage, "html/components/core/staticfiles", staticfile)
            if not os.path.isfile(staticfile):
                return not_found404(request)
            return FileResponse(staticfile)
                
        return ([
            path("/ws/lively/", ws_view_cls, name="lively-component-system"),
            path("/lively/static/<staticfile>", serve_staticfiles, name="lively-staticfiles"),
        ])
        
    @classmethod
    def get_websocket_view_cls(cls) -> Type:
        """
        Returns the WebSocket view class responsible for handling communication
        between the server and the client, including event dispatching.
        
        Returns:
            Type: The WebSocket view class used for client communication.
        """
        from duck.html.components.core.websocket import LivelyWebSocketView
        
        # Return the view class responsible.
        return LivelyWebSocketView
        
    @classmethod
    def is_active(cls) -> bool:
        """
        Returns boolean on whether the component system is active.
        """
        return bool(SETTINGS['ENABLE_COMPONENT_SYSTEM'])
        
    @classmethod
    def get_from_registry(cls, root_uid: str, uid: str, default: Optional[Any] = None) -> Optional[Component]:
        """
        Retrieve a component from the registry using its UID.

        Args:
            root_uid (str): The UID of the root component group.
            uid (str): The unique identifier of the component.
            default (Any, optional): The value to return if the component is not found.

        Returns:
            Component | Any: The component if found, otherwise the default value.
        """
        root_uid_dict = cls.registry.get(root_uid) or {}
        return root_uid_dict.get(uid)

    @classmethod
    def add_to_registry(cls, uid: str, component: Component) -> None:
        """
        Add a component to the internal registry.

        Args:
            uid (str): The unique identifier for the component.
            component (Component): The component instance to register.

        Raises:
            AlreadyInRegistry: If the component is already registered with the same UID.
            ComponentSystemError: If the provided component is not a valid Component instance.
        """
        if not isinstance(component, Component):
            raise ComponentSystemError(
                f"Expected instance of Component, got {type(component).__name__}."
            )
        
        root_uid = component.get_raw_root().uid
        root_registry = cls.registry.get(root_uid, None)
        
        if root_registry is None:
            cls.registry.set(root_uid, {})
            root_registry = cls.registry.get(root_uid)
            
        if component.isroot():
            existing = root_registry.get(uid)
            if existing is component:
                raise AlreadyInRegistry("Component is already registered with this UID.")
                
        root_registry[uid] = component
        
    @classmethod
    def get_html_tags(cls) -> List[ComponentTag]:
        """
        Returns loaded HTML component template tags defined in `settings.py`.
    
        Raises:
            ComponentSystemError: If any component cannot be imported or instantiated.
        """
        component_tags = []
        
        try:
            for name, cls_path in SETTINGS.get("TEMPLATE_HTML_COMPONENTS", {}).items():
                cls = x_import(cls_path)
                try:
                    component_tags.append(ComponentTag(name, cls))
                except (TemplateTagError):
                    # template tag already in existence
                    component_tags.append(ComponentTag.get_tag(name))
        except Exception as e:
            raise ComponentSystemError(f"Error loading HTML components: {e}") from e
        return component_tags
    