"""
Base capability system for MCP views. Lets related JSON-RPC methods be
grouped under one namespace and registered as a single pluggable unit
instead of being wired into `self.handlers` one by one.
"""

from typing import Any, Callable, Dict, Optional


class Capability:
    """
    Base class for a pluggable MCP capability.

    A capability owns one namespace of the method space. Registering it
    with `view.register_capability("tools", ToolsCapability(view))` routes
    every `tools/*` method here automatically - `action` is the part of
    the method after the slash (e.g. "call" for `tools/call`).

    Args:
        view: The MCPView this capability is attached to.

    Example:
        ```python
        class ToolsCapability(Capability):
            def setup(self):
                self.handlers = {
                    "list": self.list,
                    "call": self.call,
                }

            async def list(self, params):
                return {"tools": []}

            async def call(self, params):
                return {"content": [], "isError": False}

        view.register_capability("tools", ToolsCapability(view))
        ```
    """

    def __init__(self, view: "MCPView"):
        self.view = view
        self.namespace = None
        self.handlers: Dict[str, Callable] = {}
        self.setup()

    def setup(self) -> None:
        """
        Called once on registration. Populate `self.handlers` here.
        """
        pass

    def cleanup(self) -> None:
        """
        Called when the capability is removed or the view is torn down.
        """
        pass

    def describe(self) -> dict:
        """
        Build this namespace's entry in the 'initialize' capabilities object.

        Returns:
            dict: An empty object by default. Override to advertise
                anything beyond bare namespace presence (e.g.
                {"listChanged": True}).
        """
        return {}

    async def before_request(self, action: str, params: dict) -> Optional[Any]:
        """
        Optional hook run before an action's handler.

        Args:
            action: The part of the method after the slash (e.g. "call").
            params: The method parameters.

        Returns:
            Any non-None value short-circuits the handler entirely and is
                returned as the result instead - useful for things like
                per-capability rate limiting or caching.
        """
        return None

    async def after_request(self, action: str, result: Any) -> Any:
        """
        Optional hook run after an action's handler.

        Args:
            action: The part of the method after the slash (e.g. "call").
            result: The value returned by the handler.

        Returns:
            The (possibly modified) result.
        """
        return result

    async def dispatch(self, action: str, params: dict) -> Any:
        """
        Route a namespace-local action to its registered handler, running the before/after hooks around it.

        Args:
            action: The part of the method after the slash (e.g. "call").
            params: The method parameters.

        Raises:
            ValueError: If no handler is registered for this action.
        """
        handler = self.handlers.get(action)

        if handler is None:
            raise ValueError(f"Unknown action: {self.namespace}/{action}")

        # Let the hook short-circuit before the real handler runs.
        early_result = await self.before_request(action, params)

        if early_result is not None:
            return early_result

        result = await handler(params)
        return await self.after_request(action, result)
