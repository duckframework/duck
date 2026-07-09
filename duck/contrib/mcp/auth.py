"""
Authentication module for MCP.
"""

class AuthResult:
    """
    Return value expected from `MCPView.authenticate()`. `allowed` controls
    whether the connection is accepted at all; `scopes` controls what scope-
    gated tools/resources/prompts the caller can use - `None` means
    unrestricted (the default, i.e. no scope checking), an empty set/list
    means no scopes granted, anything else is checked as a subset by
    `authorize()`.
    """
    def __init__(self, allowed: bool = True, scopes=None):
        self.allowed = allowed
        self.scopes = set(scopes) if scopes is not None else None

    @classmethod
    def deny(cls):
        """
        Shorthand for rejecting the connection outright.
        """
        return cls(allowed=False)
