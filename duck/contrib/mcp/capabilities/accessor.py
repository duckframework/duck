"""
Explicit, traceable accessor for MCP capabilities.

Provides attribute-style access to registered capabilities with clear
error messages and discovery methods.
"""
from typing import Dict

from duck.contrib.mcp.capabilities import Capability
from duck.contrib.mcp.exceptions import (
    MCPError,
    MCPCapabilityExistsError,
    MCPCapabilityNotRegistered,
)


class CapabilityAccessor:
    """
    Explicit, traceable accessor for MCP capabilities.
    
    Provides attribute-style access to registered capabilities with clear
    error messages and discovery methods.
    
    Example:
    
    ```python
    capabilities = CapabilityAccessor(view)
    
    capabilities.tools                # Returns ToolsCapability
    capabilities.server              # Returns aliased capability
    capabilities.get('tools')      # Safe get with default
    capabilities.has('server')   # Check existence
    capabilities.list()                 # List all capabilities
    ```
    """
    def __init__(self, view: "MCPView"):
        self._view = view
        self._registry = {} # name -> capability
        self._aliases = {}  # alias -> capability
    
    @property
    def registry(self) -> Dict[str, "Capability"]:
        """
        Public property for the capabilities registry.
        """
        return self._registry
        
    def register(self, name: str, capability: Capability, alias: str = None) -> "Capability":
        """
        Internal: Register a capability.
        """
        if name in self.registry.keys():
            raise MCPCapabilityExistsError(
                f"A capability with the namespace '{name}' is already registered. "
                "Call `unregister()` before registering it again."
            )
        
        if alias and alias in self._aliases.keys():
            raise MCPCapabilityExistsError(
                f"A capability with the alias '{alias}' is already registered. "
                "Call `unregister()` before registering it again."
            )
        
        # Register capability
        self._registry[name] = capability
        
        if alias:
            self._aliases[alias] = capability
        
        # Set capability namespace.
        capability.namespace = name
        
        # Return registered capability
        return capability
    
    def unregister(self, name: str) -> "Capability":
        """
        Internal: Unregister a capability.
        """
        target = self.registry.pop(name, None)
        
        if target is None:
            # Capability does not exist.
            raise MCPCapabilityNotRegistered("Capability with name `{name}` is not registered.")
    
        # Remove any aliases pointing to this capability
        for alias, cap in list(self._aliases.items()):
            if cap is target:
                del self._aliases[alias]
        
        # Return the removed capability
        return target
    
    def set_alias(self, alias: str, capability_name: str):
        """
        Create an alias for a capability.
        
        Args:
            alias: Short name to use (e.g., 'server', 'tools')
            capability_name: The registered capability name (e.g., '_server_requests')
        
        Example:
        
        ```python
        capabilities.set_alias('server', '_server_requests')
        # Now capabilities.server works
        ```
        """
        cap = self.registry.get(capability_name)
        
        if cap is None:
            raise MCPCapabilityNotRegistered(f"Capability '{capability_name}' not found. Available: {', '.join(self.registry.keys())}")
        
        if alias in self._aliases.keys():
            raise MCPCapabilityExistsError(
                f"A capability with the alias '{alias}' is already registered. "
                "Call `unregister()` before registering it again."
            )
        
        # Create an alias
        self._aliases[alias] = cap
        return self
    
    def get(self, name: str, default=None):
        """
        Get a capability by name or alias.
        
        Args:
            name: Capability name or alias
            default: Value to return if capability doesn't exist
        
        Example:
        
        ```python
        server_cap = self.capabilities.get('_server_requests')
        if server_cap:
            await server_cap.send_request(...)
        ```
        """
        # Check aliases first
        if name in self._aliases:
            return self._aliases[name]
        return self.registry.get(name, default)
    
    def has(self, name: str) -> bool:
        """
        Check if a capability exists (by name or alias).
        """
        return name in self.registry or name in self._aliases
    
    def list(self) -> Dict[str, str]:
        """
        List all registered capabilities and their aliases.
        
        Returns:
            Dict mapping capability names to their aliases (or None)
        """
        result = {}
        
        for name in self.registry:
            # Find if this capability has an alias
            alias = None
            
            for a, cap in self._aliases.items():
                if cap is self.registry[name]:
                    alias = a
                    break
            result[name] = alias
        return result
    
    def __getattr__(self, name: str):
        """
        Attribute-style access to capabilities.
    
        Example:
            self.capabilities.tools
            self.capabilities.server
        """
        getattribute = object.__getattribute__
    
        aliases = getattribute(self, "_aliases")
        registry = getattribute(self, "registry")
    
        # Check aliases first
        if name in aliases:
            return aliases[name]
    
        # Then check capability names
        if name in registry:
            return registry[name]
    
        available = sorted(set(registry) | set(aliases))
    
        raise AttributeError(
            f"No capability named '{name}'. "
            f"Available: {', '.join(available) if available else 'none'}"
        )
    
    def __dir__(self):
        """
        Help with autocomplete in IDEs.
        """
        return (
            list(self.registry.keys())
            + list(self._aliases.keys())
            + ['get', 'has', 'list', 'alias']
        )
