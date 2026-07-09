"""
Default capabilities for the MCPView.
"""
import re
import asyncio

from typing import Dict, Optional, Callable, Any

from duck.exceptions.all import ExpectingNoResponse

from duck.contrib.mcp.codes import MCPErrorCode
from duck.contrib.mcp.capabilities import Capability
from duck.contrib.mcp.exceptions import MCPError


class InitializeCapability(Capability):
    """
    The initialize capability for the MCP view.
    """
     
    def setup(self):
        """
        Setup the capability.
        """
        self.handlers = {
            "": self.initialize,
        }

    async def initialize(self, params):
        """
        Handle the `initialize` handshake: report server identity, protocol version, and capabilities.
        """
        capabilities = {}
        
        # Let every registered capability advertise itself too.
        for name, capability in self.view.capabilities.registry.items():
            if name not in ("initialize", "notifications", "ping"):
                capabilities[name] = capability.describe()
        
        return {
            "protocolVersion": self.view.protocol_version,
            "serverInfo": {"name": self.view.name, "version": self.view.version},
            "capabilities": capabilities,
        }


class NotificationsCapability(Capability):
    """
    Utility capability for sending MCP notifications.

    This is not advertised in the MCP initialize capabilities object because
    notifications are part of the protocol layer, not a negotiated capability.
    """

    def setup(self):
        """
        Setup the capability.
        """
        self.handlers = {"initialized": self.handle_initialized}

    def suppress_response(self):
        """
        Drop the current request without sending a response.
    
        Used for JSON-RPC notifications and other requests where the protocol
        requires no response body.
        """
        raise ExpectingNoResponse("Response intentionally dropped.")
    
    async def handle_initialized(self, params: dict):
        """
        Handle the MCP `notifications/initialized` notification.
    
        This notification is sent by the client after it has successfully
        completed the initialize handshake. It does not return a response.
        """
        self.suppress_response()
        
    async def notify(
        self,
        method: str,
        params: Optional[dict] = None,
    ) -> None:
        """
        Send a notification to the connected client.

        Args:
            method:
                Notification method name.

            params:
                Optional notification parameters.
        """
        await self.view.notify(method, params)
        

class PingCapability(Capability):
    """
    The ping capability for the MCP view.
    """
     
    def setup(self):
        """
        Setup the capability.
        """
        self.handlers = {
            "": self.ping,
        }

    async def ping(self, params):
        """
        Handle the MCP ping request.
    
        MCP uses ping as a lightweight liveness check. No state changes are
        required and the response body is an empty result object.
        """
        return {}
        

class ToolsCapability(Capability):
    """
    The tools capability for the MCP view.
    """
    
    @property
    def tools(self) -> Dict[str, Callable]:
        """
        Get all tools from decorated MCPView methods.
        """
        return self.view.mcp_registry.get("tool", {})
        
    def setup(self):
        """
        Setup the capability.
        """
        self.handlers = {
            "list": self.tools_list,
            "call": self.tools_call,
        }

    async def tools_list(self, params):
        """
        Handle `tools/list`: return name, description, and input schema for every registered tool.
        """
        return {"tools": [
            {"name": fn.mcp_name, "description": fn.mcp_description, "inputSchema": fn.mcp_schema}
            for fn in self.tools.values()
        ]}

    async def tools_call(self, params):
        """
        Handle `tools/call`: invoke the named tool with the given arguments and wrap its result as MCP content.
        """
        name, args = params.get("name"), params.get("arguments") or {}
        fn = self.tools.get(name)
        
        if fn is None:
            raise ValueError(f"Unknown tool: {name}")
        
        if fn.mcp_scopes and not await self.view.authorize(fn.mcp_scopes):
            raise PermissionError(f"Not authorized to call tool: {name}")
        
        # Get result
        result = await fn(**args)
        content = result if isinstance(result, list) else [{"type": "text", "text": str(result)}]
        
        # Return content.
        return {"content": content, "isError": False}


class ResourcesCapability(Capability):
    """
    The resources capability for the MCP view.
    """
    
    @property
    def resources(self) -> Dict[str, Callable]:
        """
        Get all resources from decorated MCPView methods.
        """
        return self.view.mcp_registry.get("resource", {})
        
    @property
    def templates(self) -> Dict[str, Callable]:
        """
        Get all resource templates from decorated MCPView methods.
        """
        return self.view.mcp_registry.get("resource_template", {})
        
    def match_resource_template(self, uri: str):
        """
        Match a URI against registered resource templates.
    
        Returns:
            tuple:
                (handler, extracted_arguments)
    
            Returns:
                (None, {}) if no template matches.
        """
        for template, fn in self.templates.items():
            pattern = re.escape(template)
    
            # Convert {variable} placeholders into named regex groups.
            variables = re.findall(r"\{([^}]+)\}", template)
    
            for variable in variables:
                pattern = pattern.replace(
                    r"\{" + variable + r"\}",
                    rf"(?P<{variable}>[^/]+)",
                )
    
            match = re.fullmatch(pattern, uri)
    
            if match:
                return fn, match.groupdict()
    
        return None, {}
        
    def setup(self):
        """
        Setup the capability.
        """
        self.handlers = {
            "list": self.resources_list,
            "read": self.resources_read,
            "templates/list": self.templates_list,
        }

    async def resources_list(self, params):
        """
        Handle `resources/list`: return uri, description, and mime type for every registered resource.
        """
        return {"resources": [
            {"uri": uri, "name": fn.mcp_name, "description": fn.mcp_description, "mimeType": fn.mcp_mime_type}
            for uri, fn in self.resources.items()
        ]}

    async def resources_read(self, params):
        """
        Handle `resources/read`: fetch static or templated resources.
        """
        uri = params.get("uri")
    
        fn = self.resources.get(uri)
        kwargs = {}
    
        if fn is None:
            fn, kwargs = self.match_resource_template(uri)
    
        if fn is None:
            raise ValueError(f"Unknown resource: {uri}")
    
        if fn.mcp_scopes and not await self.view.authorize(fn.mcp_scopes):
            raise PermissionError(f"Not authorized to read resource: {uri}")
    
        # Resolve resource content.
        result = await fn(**kwargs)
    
        return {
            "contents": [
                {
                    "uri": uri,
                    "mimeType": fn.mcp_mime_type,
                    "text": str(result),
                }
            ]
        }
    
    async def templates_list(self, params):
        """
        Handle `resources/templates/list`.
        """
        return {
            "resourceTemplates": [
                {
                    "uriTemplate": fn.mcp_uri_template,
                    "name": fn.mcp_name,
                    "description": fn.mcp_description,
                    "mimeType": fn.mcp_mime_type,
                }
                for fn in self.templates.values()
            ]
        }


class PromptsCapability(Capability):
    """
    The prompts capability for the MCP view.
    """
    
    @property
    def prompts(self) -> Dict[str, Callable]:
        """
        Get all prompts from decorated MCPView methods.
        """
        return self.view.mcp_registry.get("prompt", {})
     
    def setup(self):
        """
        Setup the capability.
        """
        self.handlers = {
            "list": self.prompts_list,
            "get": self.prompts_get,
        }

    async def prompts_list(self, params):
        """
        Handle `prompts/list`: return name and description for every registered prompt.
        """
        return {"prompts": [
            {"name": fn.mcp_name, "description": fn.mcp_description}
            for fn in self.prompts.values()
        ]}

    async def prompts_get(self, params):
        """
        Handle `prompts/get`: render the named prompt with the given arguments into MCP message format.
        """
        name, args = params.get("name"), params.get("arguments") or {}
        fn = self.prompts.get(name)
        
        if fn is None:
            raise ValueError(f"Unknown prompt: {name}")
        
        if fn.mcp_scopes and not await self.view.authorize(fn.mcp_scopes):
            raise PermissionError(f"Not authorized to use prompt: {name}")
        
        # Get result and construct messages.
        result = await fn(name, **args)
        messages = result if isinstance(result, list) else [
            {"role": "user", "content": {"type": "text", "text": str(result)}}
        ]
        
        # Return final messages.
        return {"messages": messages}


class ServerRequestsCapability(Capability):
    """
    Capability that enables server-to-client request/response via hooks.

    This capability registers itself with the view's hook system to intercept
    incoming client responses. It provides the `send_request()` method that
    tools can use to send JSON-RPC requests to the client and await responses.

    The capability automatically:
    - Registers a pre-request hook to detect client responses
    - Manages pending request futures with timeouts
    - Cleans up on capability removal

    Example:
    
    ```python
    class MyServer(MCPView):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.register_capability("_server_requests", ServerRequestsCapability(self), alias="server")

        @tool(description="Ask client for input")
        async def ask_client(self, question: str) -> str:
            result = await self._server_requests.send_request(
                "custom/ask",
                {"question": question}
            )
            return result.get("answer", "No answer")
    ```
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request_counter = 0

    @property
    def pending_requests(self) -> Dict[int, asyncio.Future]:
        """
        Return the pending requests in queue.
        """
        persistent_state = self.view.persistent_state
        pending_requests = getattr(persistent_state, "_pending_requests", None)
        if pending_requests is None:
            persistent_state._pending_requests = {}
        return persistent_state._pending_requests
    
    def setup(self):
        """
        Register hooks and initialize state.
        """
        self.handlers = {}  # No handlers - this is purely for utility
        
        # Register hook to intercept client responses
        self.view.register_hook("before_dispatch", self.handle_client_response)
        
    def cleanup(self):
        """
        Cancel all pending requests and release any associated resources.
        """
        if not self.view.session_id:
            # Accessing pending_requests with SSE initialized/Session ID set will raise an error
            return
        for future in list(self.pending_requests.values()):
            future.cancel()
        # Clear all pending requests
        self.pending_requests.clear()

    async def handle_client_response(self, body: dict, rpc_id, method, params):
        """
        Hook that intercepts incoming messages to detect client responses.
        
        If the message is a response (has 'id' and either 'result' or 'error',
        but no 'method'), it resolves the pending future and returns a special
        sentinel to short-circuit further processing.
        
        Returns:
            tuple (handled, result_or_response)
            - (True, response): Message was a client response, return this to client
            - (False, None): Not a response, continue normal processing
        """
        # A response has an id, no method, and either result or error
        if method is None and rpc_id is not None and ("result" in body or "error" in body):
            future = self.pending_requests.pop(rpc_id, None)
            
            if future is not None and not future.done():
                future.set_result(body)
                
                # Return a 200 OK empty response to the client
                return (True, self.view.empty_response())
            
            else:
                # Unknown or expired ID - return error
                response = self.view.error_response(
                    rpc_id,
                    MCPErrorCode.INVALID_REQUEST,
                    f"Unknown or expired request id: {rpc_id}",
                    status=400,
                )
                
                # Return that we handled this alongside error response
                return (True, response)
        
        # Return that we didn't intercept this.
        return (False, None)

    async def send_request(
        self,
        method: str,
        params: Optional[dict] = None,
        timeout: float = 10.0,
    ) -> Any:
        """
        Send a JSON-RPC request to the client and wait for its response.

        Args:
            method: The method name to call on the client.
            params: Optional parameters for the method.
            timeout: Maximum seconds to wait for a response.

        Returns:
            The `result` field from the client's response.

        Raises:
            RuntimeError: If no active SSE stream exists.
            TimeoutError: If the client does not respond within the timeout.
            Exception: If the client returns an error object.
        """
        view = self.view

        # Generate a unique request ID
        self.request_counter += 1
        request_id = self.request_counter

        # Create a future that will be resolved when the client replies
        loop = asyncio.get_event_loop()
        future = loop.create_future()
        
        # Set request future.
        self.pending_requests[request_id] = future
        
        # Build the JSON-RPC request envelope
        message = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method,
            "params": params or {},
        }
        
        # Send the request via the active SSE stream
        try:
            # Direct send on the active SSE response
            await view.ensure_sse_event_sent(message)
            
        except Exception as exc:
            self.pending_requests.pop(request_id, None)
            raise RuntimeError(f"Failed to send request: {exc}") from exc

        # Wait for the response with a timeout
        try:
            response = await asyncio.wait_for(future, timeout=timeout)
        except asyncio.TimeoutError:
            self.pending_requests.pop(request_id, None)
            raise TimeoutError(f"Client did not respond to '{method}' within {timeout}s") from None
        
        except Exception:
            self.pending_requests.pop(request_id, None)
            raise

        # Check for an error response
        if "error" in response:
            error = response["error"]
            raise MCPError(
                f"Client error: {error.get('message', 'Unknown error')} "
                f"(code {error.get('code', 'N/A')})"
            )

        return response.get("result")


class SamplingCapability(Capability):
    """
    MCP sampling capability.

    Provides helpers for requesting the client to generate model completions
    through the MCP `sampling/createMessage` request.

    This capability does not expose any MCP handlers because sampling is a
    server-to-client request initiated by the server.
    """

    def setup(self):
        """
        Setup the capability.
        """
        self.handlers = {}
        
    @property
    def server_requests(self) -> Capability:
        """
        Access the internal server request capability.
        """
        try:
            # Access the server requests capability.
            return self.view.capabilities._server_requests
            
        except AttributeError as exc:
            # Reraise exception
            raise MCPCapabilityDependencyError(
                capability=self.__class__.__name__,
                required_capability="ServerRequestsCapability",
            ) from exc
        
    async def create_message(
        self,
        messages: list,
        max_tokens: int,
        *,
        model_preferences: Optional[dict] = None,
        system_prompt: Optional[str] = None,
        include_context: Optional[str] = None,
        temperature: Optional[float] = None,
        stop_sequences: Optional[list[str]] = None,
        timeout: float = 60.0,
    ) -> dict:
        """
        Request the client to sample a model response.

        Args:
            messages:
                Conversation messages in MCP format.

            max_tokens:
                Maximum number of tokens the client may generate.

            model_preferences:
                Optional model selection hints.

            system_prompt:
                Optional system instruction.

            include_context:
                Optional context inclusion preference.

            temperature:
                Optional sampling temperature.

            stop_sequences:
                Optional generation stop sequences.

            timeout:
                Maximum time to wait for the client response.

        Returns:
            The client's sampling response.

        Raises:
            TimeoutError:
                If the client does not respond in time.
            MCPError:
                If the client returns an error.
        """
        params = {
            "messages": messages,
            "maxTokens": max_tokens,
        }

        if model_preferences is not None:
            params["modelPreferences"] = model_preferences

        if system_prompt is not None:
            params["systemPrompt"] = system_prompt

        if include_context is not None:
            params["includeContext"] = include_context

        if temperature is not None:
            params["temperature"] = temperature

        if stop_sequences is not None:
            params["stopSequences"] = stop_sequences

        return await self.server_requests.send_request(
            "sampling/createMessage",
            params,
            timeout=timeout,
        )


class RootsCapability(Capability):
    """
    MCP roots capability.

    Provides helpers for requesting the client to list available filesystem
    roots through the MCP `roots/list` request.

    This capability does not expose any MCP handlers because roots are fetched
    by the server from the client.
    """

    def setup(self):
        """
        Setup the capability.
        """
        self.handlers = {}

    @property
    def server_requests(self) -> Capability:
        """
        Access the internal server request capability.
        """
        try:
            return self.view.capabilities._server_requests
        except AttributeError as exc:
            raise MCPCapabilityDependencyError(
                capability=self.__class__.__name__,
                required_capability="ServerRequestsCapability",
            ) from exc

    async def list_roots(
        self,
        timeout: float = 10.0,
    ) -> list:
        """
        Request available roots from the client.

        Args:
            timeout:
                Maximum time to wait for the client response.

        Returns:
            A list of root objects.

        Raises:
            TimeoutError:
                If the client does not respond within the timeout.
            MCPError:
                If the client returns an error.
        """
        response = await self.server_requests.send_request(
            "roots/list",
            timeout=timeout,
        )
        
        # Return roots.
        return response.get("roots", [])


class ElicitationCapability(Capability):
    """
    MCP elicitation capability.

    Provides helpers for requesting user input from the client through the MCP
    `elicitation/create` request.

    This capability does not expose any handlers because elicitation is a
    server-to-client request initiated by the server.
    """

    def setup(self):
        """
        Setup the capability.
        """
        self.handlers = {}

    @property
    def server_requests(self) -> Capability:
        """
        Access the internal server request capability.
        """
        try:
            return self.view.capabilities._server_requests
        except AttributeError as exc:
            raise MCPCapabilityDependencyError(
                capability=self.__class__.__name__,
                required_capability="ServerRequestsCapability",
            ) from exc

    async def create(
        self,
        message: str,
        requested_schema: dict,
        *,
        timeout: float = 60.0,
    ) -> dict:
        """
        Request information from the user through the client.

        Args:
            message:
                Message displayed to the user.

            requested_schema:
                JSON schema describing the information being requested.

            timeout:
                Maximum time to wait for the client response.

        Returns:
            Client elicitation response.

        Raises:
            TimeoutError:
                If the client does not respond within the timeout.
            MCPError:
                If the client returns an error.
        """
        return await self.server_requests.send_request(
            "elicitation/create",
            {
                "message": message,
                "requestedSchema": requested_schema,
            },
            timeout=timeout,
        )
