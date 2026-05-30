"""
Base application primitives shared by Duck application classes.
"""

from typing import Optional, Dict, Callable

from duck.exceptions.all import ApplicationError
from duck.meta import Meta
from duck.utils.net import is_ipv4, is_ipv6
from duck.utils.path import url_normalize
from duck.utils.urlcrack import URL


APPS_REGISTRY: Dict[str, "BaseApp"] = {}


class BaseApp:
    """
    Provides shared configuration and URL helpers for Duck app classes.

    Subclasses are responsible for creating their own server instance and
    implementing lifecycle methods such as `start_server`, `run`, and `stop`.
    """

    DEFAULT_ADDR = "localhost"
    DEFAULT_PORT = 8000
    
    def __init__(
        self,
        name: Optional[str] = None,
        addr: str = DEFAULT_ADDR,
        port: int = DEFAULT_PORT,
        domain: Optional[str] = None,
        server_url: Optional[str] = None,
        uses_ipv6: bool = False,
        enable_https: bool = False,
        no_checks: bool = False,
        workers: Optional[int] = None,
        force_worker_processes: bool = False,
        events: Optional[Dict[str, Optional[Callable]]] = None,
    ) -> None:
        """
        Initializes shared app configuration.

        Args:
            name: Unique name to your application.
            addr: Address the server binds to.
            port: Port the server binds to.
            domain: Public-facing domain. Defaults to the bind address.
            server_url: Public-facing absolute server URL.
            uses_ipv6: Whether the app should bind using IPv6.
            enable_https: Whether HTTPS is enabled for this app.
            workers: Optional number of server workers.
            force_worker_processes: Determines whether to use worker **processes** instead of the default worker **threads**. 
                    By default, when `workers` is greater than 1, the server will use worker **threads**.  
                    Threads avoid cross-process synchronization issues—such as component registry mismatches 
                    (e.g., issues with Lively components) that occur when state lives in separate processes.  
                    
                    Set this flag to `True` only when process isolation is explicitly desired **and** you do not
                    require shared in-memory synchronization between workers.
            events: Events to handle e.g. {"on_start": some_callable}. Defaults to None.
        
        Raises:
            ApplicationError: If the provided bind address is invalid.
        """
        # Note: Domain and Server URL may be different.
        # Validate bind address before storing it
        self.validate_addr(addr=addr, uses_ipv6=uses_ipv6)
        
        # Store runtime configuration
        self.name = self.resolve_name(name)
        self.enable_https = enable_https
        self.workers = workers
        self.force_worker_processes = force_worker_processes
        
        # Store network configuration
        self.addr = addr
        self.port = port
        self.uses_ipv6 = uses_ipv6
        self.original_domain = domain
        self.domain = self.resolve_domain(addr=addr, domain=domain, uses_ipv6=uses_ipv6)
        self.server_url = self.resolve_server_url(server_url)
        self.no_checks = no_checks
        
        # Event map
        self.event_map = {"on_start": None, "on_pre_stop": None, **(events or {})}
        
        # Server is assigned by subclasses
        self.server = None
        
        # Run extra checks
        if not no_checks:
            self.run_checks()
            
        # Register ports when requested
        self.register_ports()
       
        # Add app to created apps.
        BaseApp.register_app(self.name, self)

    @property
    def running(self) -> bool:
        """
        Returns True if the main server running else False.
        """
        return self.server.running
        
    @property
    def server_up(self) -> bool:
        """
        Checks whether the assigned server is running.

        Returns:
            True if the server exists and is running, otherwise False.
        """
        return bool(self.server and self.server.running)
    
    @property
    def absolute_uri(self) -> str:
        """
        Returns application server absolute `URL`.
        """
        return self.server_url
        
    @property
    def absolute_ws_uri(self) -> str:
        """
        Returns application server absolute WebSockets `URL`.
        """
        url = self.server_url
        url_obj = URL(url)
        url_obj.scheme = "ws" if url_obj.scheme == "http" else 'wss'
        return url_obj.to_str()
    
    @classmethod
    def get_all_apps(self) -> Dict[str, "BaseApp"]:
        """
        Returns all created apps.
        """
        return APPS_REGISTRY
        
    @classmethod
    def get_app_by_name(name: str):
        """
        Returns an app instance by name or else an ApplicationError is raised.
        """
        app = APPS_REGISTRY.get(name, None)
        
        if not app:
            raise ApplicationError(f"Application with name '{name}' not found in registry.")
        
        # Finally, return the app instance.
        return app
        
    @classmethod
    def register_app(cls, name: str, app: "BaseApp"):
        """
        Registers an application.
        """
        app = APPS_REGISTRY.get(name, None)
        
        if app:
            raise ApplicationError(f"An app with the name '{name}' already exists.") 
        
        # Register app in registry
        APPS_REGISTRY[name] = app
        
    @staticmethod
    def validate_addr(addr: str, uses_ipv6: bool = False) -> None:
        """
        Validates the bind address.

        Args:
            addr: Address to validate.
            uses_ipv6: Whether the address should be validated as IPv6.

        Raises:
            ApplicationError: If the address is invalid.
        """
        # Allow named hosts like localhost
        if str(addr).isalnum():
            return

        # Validate IPv6 addresses
        if uses_ipv6 and not is_ipv6(addr):
            raise ApplicationError(
                "Argument uses_ipv6=True but addr is not a valid IPv6 address."
            )

        # Validate IPv4 addresses
        if not uses_ipv6 and not is_ipv4(addr):
            raise ApplicationError("Argument `addr` is not a valid IPv4 address.")
            
    @staticmethod
    def resolve_domain(
        addr: str,
        domain: Optional[str] = None,
        uses_ipv6: bool = False,
    ) -> str:
        """
        Resolves the public domain for the app.

        Args:
            addr: Bind address used as fallback.
            domain: Explicit public-facing domain.
            uses_ipv6: Whether the address is IPv6.

        Returns:
            A browser-safe domain string.
        """
        # Use explicit domain when provided
        resolved_domain = domain or (f"[{addr}]" if uses_ipv6 else addr)

        # Avoid exposing 0.0.0.0 as a browser URL
        if is_ipv4(resolved_domain) and resolved_domain.startswith("0"):
            return "localhost"

        return resolved_domain

    def resolve_name(
        self,
        name: Optional[str] = None,
    ) -> str:
        """
        Resolves a unique identifier for the app.

        Args:
            name: Name to use.
            
        Returns:
            A unique name string.
        """
        if name:
            if name in APPS_REGISTRY:
                raise ApplicationError(f"Another app with the name '{name}' already exists. Please use a different name.")
        else:
            name = f"{self.__class__.__name__}-{len(APPS_REGISTRY)}"
        return name
        
    def resolve_server_url(self, server_url: Optional[str] = None) -> str:
        """
        Resolves the public absolute server URL.

        Args:
            server_url: Explicit public-facing URL.

        Returns:
            Absolute server URL for URL generation.
        """
        # Respect explicit public URL for proxy/CDN deployments
        if server_url:
            return url_normalize(server_url)

        # Build URL from app protocol and domain
        protocol = "https" if self.enable_https else "http"
        return url_normalize(f"{protocol}://{self.domain}:{self.port}")
    
    def run_checks(self):
        """
        Run applications checks, will be implemented by subclass.
        """
        pass
        
    def register_ports(self) -> None:
        """
        Registers a ports as occupied by this app - will be implemented by subclass.
        
        Note: It registers the app port by default.
        """
        from duck.utils.port_registry import PortRegistry
        
        PortRegistry.register_port(self.port, f"{self}")
        
    def build_absolute_uri(self, path: str = "") -> str:
        """
        Builds an absolute HTTP URL from a path.

        Args:
            path: URL path to append to the app URL.

        Returns:
            Normalized absolute URL.
        """
        return url_normalize(f"{self.absolute_uri}/{path.lstrip('/')}")

    def build_absolute_ws_uri(self, path: str = "") -> str:
        """
        Builds an absolute WebSocket URL from a path.

        Args:
            path: URL path to append to the WebSocket URL.

        Returns:
            Normalized absolute WebSocket URL.
        """
        return url_normalize(f"{self.absolute_ws_uri}/{path.lstrip('/')}")
        
    def run(self):
        """
        The method for running the web application.
        """
        raise NotImplementedError("The method 'run' must be implemented.")
     
    def stop(self):
        """
        The method for stopping the web application.
        """
        raise NotImplementedError("The method 'stop' must be implemented.")

    def register_event(self, event: str, handler: Optional[Callable] = None):
        """
        Register an event.
        
        Args:
            event: The event to be handled.
            handler: An optional callable to handle the event. Defaults to None.
        """
        self.event_map[event] = handler
        
    def dispatch_event(self, event: str):
        """
        Dispatch an event and make event handlers handle the event.
        """
        event_handler = self.event_map.get(event, None)
        
        if event_handler is None and event not in self.event_map:
            raise ApplicationError(f"Event '{event}' does not appear to be registered.")
        
        # Execute event handler.
        if event_handler:
            event_handler(event, self)
    
    def _on_app_start(self):
        """
        Internal method called on application start.
        """
        self.dispatch_event("on_start")
