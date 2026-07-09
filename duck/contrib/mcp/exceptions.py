"""
Exceptions module for the MCP module.
"""


class MCPError(Exception):
    """
    Base exception for MCP-related errors.
    """


class InvalidMCPKindError(MCPError):
    """
    Raised when an unsupported MCP kind is encountered.
    """


class MCPCapabilityExistsError(MCPError):
    """
    Raised when attempting to register an MCP capability that is already registered.
    """


class MCPCapabilityNotRegistered(MCPError):
    """
    Raised when attempting to unregister an MCP capability that is not registered.
    """


class MCPSseNotInitializedError(MCPError):
    """
    Raised when attempting to do an operation before SSE is initiated.
    """


class SessionError(MCPError):
    """
    Raised on session related exceptions.
    """

class MCPCapabilityDependencyError(MCPError):
    """
    Raised when a capability requires another capability that is not registered.

    Example:
        SamplingCapability requires ServerRequestsCapability.
    """

    def __init__(
        self,
        capability: str,
        required_capability: str,
    ):
        """
        Initialize the capability dependency error.

        Args:
            capability:
                The capability that has the missing dependency.

            required_capability:
                The capability that is required but unavailable.
        """
        super().__init__(
            f"Capability '{capability}' requires capability "
            f"'{required_capability}', but it is not registered."
        )
        
        self.capability = capability
        self.required_capability = required_capability
