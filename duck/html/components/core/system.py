"""
Manages the registration and lifecycle of HTML components, and enables communication
with the browser via WebSocket to dispatch events and execute JavaScript in real-time.
"""
import os
import time
import secrets

from typing import (
    List,
    Type,
    Any,
    Optional,
    Tuple,
    Dict,
)

from pathlib import Path

from duck.shortcuts import not_found404
from duck.urls import path, URLPattern
from duck.utils.path import joinpaths
from duck.settings import SETTINGS
from duck.storage import duck_storage
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
    
    registry: InMemoryCache = InMemoryCache(maxkeys=500_000) # cache with LRU eviction lim->500 000 for very busy app.
    """
    Mapping of UIDs to components.
    
    Format: {root_uid: (owner_token, {root_uid: component, child_uid: component, ...}, disconnected_at)}
    """
    
    OWNER_TOKEN_NBYTES: int = 16
    """
    Number of bytes for the Lively owner token registration.
    """
    
    OWNER_TOKEN_REQUEST_KEY: str = "LIVELY_OWNER_TOKEN"
    """
    Key to set in `request.META` when owner token is generated.
    """
    
    OWNER_COOKIE_KEY: str = "_lively_owner"
    """
    The cookie key to set in response when owner token is set.
    """
    
    OWNER_TOKEN_MAX_AGE: float = 3600
    """
    The maximum seconds for the owner token to last.
    """
    
    @classmethod
    def get_urlpatterns(cls) -> List[URLPattern]:
        """
        Returns the appropriate URL patterns for the whole system.
        """
        from duck.html.components.core.browser_state import sync_browser_state
        from duck.html.components.lively_utils.file_request import receive_ws_file
        
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
            path("/lively/sync", sync_browser_state, name="lively-browser-sync"),
            path("/lively/ws-file", receive_ws_file, name="lively-receive-ws-file"),
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
    def get_owner(
        cls,
        root_uid: str,
        entry: Optional[Tuple[str, Dict[str, "Component"], Optional[float]]] = None,
    ) -> Optional[str]:
        """
        Get the owner token bound to a root_uid, lazily expiring it first if needed.
    
        If the root_uid's component tree has been disconnected (via
        `mark_disconnected`) for longer than `OWNER_TOKEN_MAX_AGE`, the entry is
        deleted and treated as gone rather than being returned. This enforces
        a time-bounded expiry without a background sweep task -- the check
        simply runs on whatever access happens to come in next (a reconnect
        attempt, a dispatch call, etc.).
    
        Args:
            root_uid: The root component's UID to look up.
            entry: An already-fetched `(owner_token, root_registry, disconnected_at)`
                tuple for this root_uid, if the caller has one on hand (e.g. from
                a prior `cls.registry.get(root_uid)`). Pass this to avoid a
                redundant registry lookup. If omitted, it's fetched here.
    
        Returns:
            The owner token if the entry exists and hasn't expired, else None.
        """
        if entry is None:
            entry = cls.registry.get(root_uid)
    
        if entry is None:
            return None
    
        # Get data
        owner_token, root_registry, disconnected_at = entry
    
        if disconnected_at is not None and (time.monotonic() - disconnected_at) > cls.OWNER_TOKEN_MAX_AGE:
            # Treat as gone even though LRU hasn't necessarily evicted it yet.
            cls.registry.delete(root_uid)
            return None
    
        return owner_token
    
    @classmethod
    def mark_connected(cls, root_uid: str) -> None:
        """
        Mark a root_uid's component tree as having an active WebSocket connection.
    
        Clears any pending disconnect timestamp, so the entry is treated as
        alive indefinitely for as long as the connection stays open --
        expiry only starts counting again after the next `mark_disconnected`.
    
        Args:
            root_uid: The root component's UID whose WebSocket just connected.
        """
        entry = cls.registry.get(root_uid)
        
        if entry is not None:
            owner_token, root_registry, _ = entry
            cls.registry.set(root_uid, (owner_token, root_registry, None))
    
    @classmethod
    def mark_disconnected(cls, root_uid: str) -> None:
        """
        Mark a root_uid's component tree as having lost its WebSocket connection.
    
        Stamps the current time so that a subsequent `get_owner` call can
        lazily expire this entry once `OWNER_TOKEN_MAX_AGE` has elapsed since
        disconnect, giving the client a grace period to reconnect (e.g. after
        a sleep/wake or brief network drop) before the entry is discarded.
    
        Args:
            root_uid: The root component's UID whose WebSocket just disconnected.
        """
        entry = cls.registry.get(root_uid)
        
        if entry is not None:
            owner_token, root_registry, _ = entry
            cls.registry.set(root_uid, (owner_token, root_registry, time.monotonic()))
        
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
        _, root_uid_dict, _ = cls.registry.get(root_uid) or (None, {}, None)
        return root_uid_dict.get(uid, default)

    @classmethod
    def add_to_registry(cls, uid: str, component: "Component") -> None:
        """
        Add a component to the internal Lively registry.
    
        For the first component registered under a given root_uid (which must
        be the root component itself), this also mints a cryptographically
        random owner token and binds it to the component's request. The
        WebSocket layer later checks incoming `dispatch_component_event` calls
        against this token to confirm the connection actually owns that
        root_uid before touching anything in the registry.
    
        Args:
            uid: The unique identifier for the component within its root tree.
            component: The component instance to register.
    
        Raises:
            ComponentSystemError:
                If `component` isn't a `Component`; if the
                first-ever registration under a fresh root_uid is not the root
                component; or if a root component has no request bound to it.
            
            AlreadyInRegistry:
                If a root component is registered twice under
                the same UID.
        """
        from duck.html.components.extensions import RequestNotFoundError
    
        if not isinstance(component, Component):
            raise ComponentSystemError(
                f"Expected a Component instance, got {type(component).__name__!r}."
            )
    
        root_uid = component.get_raw_root().uid
        
        # Fetch existing entry
        existing_entry = cls.registry.get(root_uid)
        
        if existing_entry is None:
            # First time this root_uid has been seen. Validate before
            # mutating anything, so a failed call leaves no partial state.
            if not component.isroot():
                raise ComponentSystemError(
                    f"First registration under root_uid={root_uid!r} must "
                    f"be the root component, got {component!r}."
                )

            # Initialize request and owner token
            request = None
            owner_token = None
            
            try:
                # Try get the owner from the component
                request = component.get_request_or_raise()
            
            except RequestNotFoundError as e:
                # Registration is skipped for standalone components. Record the
                # error so the Lively WebSocket event handler can report it later
                # if the component attempts to participate in a live event.
                component._skipped_registration_error = ComponentSystemError(
                    f"Couldn't register root component {component!r} with Lively: "
                    "no request is bound to the component. A request is required "
                    "to establish Lively ownership."
                )
                
            if request:
                # Get existing token or generate new owner token
                existing = request.COOKIES.get(cls.OWNER_COOKIE_KEY)
                owner_token = existing or secrets.token_urlsafe(cls.OWNER_TOKEN_NBYTES)
            
                if not existing:
                    # Set the owner token in request's meta
                    request.META[cls.OWNER_TOKEN_REQUEST_KEY] = owner_token
            
            # Typing helpers
            root_registry: Dict[str, Component] = {}
        
        else:
            owner_token, root_registry, _ = existing_entry

            if component.isroot():
                existing_component = root_registry.get(uid)
                
                if existing_component is component:
                    raise AlreadyInRegistry(f"Root component already registered under uid={uid!r}.")

        # Assign component UID in registry
        root_registry[uid] = component
        
        # Register entry
        cls.registry.set(root_uid, (owner_token, root_registry, None))
        
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
        
        # Return final component tags.
        return component_tags
    