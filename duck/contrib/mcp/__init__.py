"""
Minimal MCP (Model Context Protocol) server support for Duck, mirroring the
WebSocketView pattern. Speaks JSON-RPC 2.0 over a single HTTP endpoint (MCP
"Streamable HTTP" transport): POST for requests, GET for an optional
server-push stream.

By default each request gets one JSON response. SSE is opt-in per view via
`sse = True` and only used when the client also asks for it via
`Accept: text/event-stream` - in that case the response is streamed over the
raw socket as Server-Sent Events, and tools/resources/prompts can push
progress notifications mid-call via `self.notify(...)`.
"""
import uuid
import json
import asyncio

from typing import Optional, Union, Dict, Any, Callable

from duck.exceptions.all import ExpectingNoResponse
from duck.http.response import HttpResponse, JsonResponse
from duck.utils.xsocket.io import SocketIO
from duck.utils.urlcrack import URL
from duck.views import View, csrf_exempt
from duck.shortcuts import jsonify
from duck.settings import SETTINGS
from duck.logging import logger

from duck.contrib.mcp.codes import MCPErrorCode
from duck.contrib.mcp.auth import AuthResult
from duck.contrib.mcp.session import SessionStore
from duck.contrib.mcp.exceptions import (
    MCPError,
    InvalidMCPKindError,
    MCPCapabilityExistsError,
    MCPSseNotInitializedError,
)
from duck.contrib.mcp.capabilities import Capability
from duck.contrib.mcp.capabilities.accessor import CapabilityAccessor
from duck.contrib.mcp.capabilities.defaults import (
    InitializeCapability,
    NotificationsCapability,
    PingCapability,
    ToolsCapability,
    ResourcesCapability,
    PromptsCapability,
    ServerRequestsCapability,
    SamplingCapability,
    RootsCapability,
    ElicitationCapability,
)
from duck.contrib.mcp.decorators import (
    tool as tool,
    prompt as prompt,
    resource as resource,
    resource_template as resource_template,
) # Import all decorators but avoid unused import warning in IDEs


class MCPView(View):
    """
    Base class for an MCP server endpoint.

    Subclass it, decorate methods with @tool / @resource / @prompt, and wire
    the class up with `path()` like any other view:
        
    ```python
    class SomeMCPServer(MCPView):
        name = "duck-mcp-server"
        version = "1.0.0"

        @tool(description="Add two numbers")
        async def add(self, a: int, b: int) -> int:
            return a + b

    urlpatterns = [
        path('/mcp', SomeMCPServer, name="mcp_endpoint"),
    ]
    ```
    
    For anything beyond the built-in methods, register a `Capability`
    instead of adding one-off handlers by hand. Every method whose prefix
    matches the registered name is routed there automatically:

    ```python
    class UsageCapability(Capability):
        def setup(self):
            self.handlers = {"report": self.report}

        async def report(self, params):
            return {"calls": 42}

    class SomeMCPServer(MCPView):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.register_capability("usage", UsageCapability(self))
    ```

    A request for `usage/report` now dispatches to `UsageCapability.report`.
    """
    name = "duck-mcp-server"
    version = "0.1.0"
    protocol_version = "2024-11-05"

    sse = False
    """
    bool: Set True to allow this server to stream responses as Server-Sent
    Events. Only takes effect on requests that also send
    `Accept: text/event-stream` - plain requests still get a single JSON
    response either way.
    """
    
    allowed_origins = None
    """
    list[str] | None: hostnames to validate the Origin header against
    (DNS-rebinding protection, as recommended by the MCP spec for locally-
    bound servers). None (default) falls back to `settings.ALLOWED_HOSTS`,
    so there's nothing to configure twice - pass an explicit list on a
    subclass to override. `"*"` in the list disables the check entirely,
    matching Django-style ALLOWED_HOSTS semantics.
    """

    SSE_CHUNK_SIZE = 64 * 1024
    """
    int: max bytes written to the socket per send call while streaming an SSE event, so large payloads don't block the event loop in one write.
    """
    
    SSE_PING_INTERVAL = 15
    """
    int: seconds between keep-alive pings on a standalone GET SSE stream, so
    intermediaries don't time out an otherwise idle connection.
    """
    
    _session_queues = {}
    """
    dict[str, asyncio.Queue]: process-wide registry mapping MCP session IDs to
    the queue backing that session's standalone GET SSE stream, so `notify()`
    calls from any request - even one running in a completely different
    instance, e.g. a background job kicked off by a tool call - can reach a
    stream opened elsewhere. Class-level so it's shared across all instances of
    this view.
    """
    
    _session_id_header = "Mcp-Session-Id"
    """
    The MCP session ID header. Defaults to 'mcp-session-id'.
    """
    
    def __init__(self, *args, **kwargs):
        """
        Collect all @tool / @resource / @prompt decorated methods on this instance into lookup dicts.
        """
        from duck.http.core.httpd.httpd import response_handler
        
        # Super init
        super().__init__(*args, **kwargs)
        
        # Attribute setup
        self.granted_scopes = None # scopes granted by the last `authenticate()` call - None means unrestricted. Set automatically from the `AuthResult` it returns; don't set this directly."""
        self._response_handler = response_handler
        self._sse_initiated = False
        self._attrs = None
        self._mcp_registry = {}
        self._initialized = False
        
        # Hook system for extensions
        self._hooks = {
            "before_dispatch": [],   # (body, rpc_id, method, params) -> (handled, response)
            "after_dispatch": [],    # (rpc_id, method, result) -> modified_result
            "before_sse_send": [],   # (message) -> modified_message
            "after_sse_send": [],    # (message) -> None
            "on_session_create": [], # (session_id) -> None
            "on_session_delete": [], # (session_id) -> None
        }
        
        # Session for the client/view
        self.session = SessionStore(None)
        
        # Capability system - namespace (e.g. "tools") to Capability instance.
        self.capabilities = CapabilityAccessor(self) # Used for accessing capabilities easily.
        
        # Flag that initialization has finished - before register_default_capabilities.
        self._initialized= True
        
        # Register default hooks
        self.register_default_hooks()
        
        # Register default capabilities.
        self.register_default_capabilities()
        
    @property
    def attrs(self) -> Dict[str, Any]:
        """
        Method for getting MCP view attributes, with stripped `__` private attributes.
        This must be called after full object initiazation.
        """
        if not self._initialized:
            raise MCPError("Collection of attributes must only done when view is fully initialized.")
            
        if not self._attrs:
            self._attrs = [attr for attr in dir(self) if not attr.startswith('__')]
        return self._attrs
        
    @property
    def mcp_registry(self) -> Dict[str, Callable]:
        """
        Registry of MCP-decorated methods.
        
        Maps method names to callables with an `mcp_kind` attribute. Any additional
        MCP metadata is stored directly on the callables by their decorators.
        """
        if not self._mcp_registry:
            for attr_name in self.attrs:
                try:
                    member = getattr(self, attr_name, None)
                except MCPError:
                    # Attribute not fetchable - maybe we got this error: To use the persistent_state, session_id must be assigned.
                    continue
                    
                kind = getattr(member, "mcp_kind", None)
                
                if kind is not None:
                    self._mcp_registry.setdefault(kind, {})
                    
                    # Required identifier attribute for each supported MCP kind.
                    key_attrs = {
                        "tool": "mcp_name",
                        "prompt": "mcp_name",
                        "resource": "mcp_uri",
                        "resource_template": "mcp_uri_template",
                    }
                    
                    try:
                        key = getattr(member, key_attrs[kind])
                    except KeyError:
                        raise InvalidMCPKindError(
                            f"Unsupported MCP kind {kind!r} on method '{attr_name}'. "
                            f"Expected one of: {', '.join(repr(k) for k in key_attrs)}."
                        ) from None
                     
                    self._mcp_registry[kind][key] = member
                    
        return self._mcp_registry
        
    @property
    def session_id(self) -> Optional[None]:
        """
        Return the session ID for the client.
        """
        return self.session.session_id
        
    @session_id.setter
    def session_id(self, key: str):
        """
        Set the session ID for the client.
        """
        self.session.session_id = key
        
    @property
    def persistent_state(self) -> object:
        """
        Return an object whose attributes persist for the lifetime of the session.
    
        You can attach custom attributes to this object to store session-specific
        state without modifying the session itself.
        """
        class PersistentState:
            pass
            
        if not self.session_id:
            raise MCPError("To use the persistent_state, session_id must be assigned.")
        
        # Set the default state if not set.
        self.session.setdefault("persistent_state", PersistentState())
        
        # Return the persistent state from session.
        return self.session.get("persistent_state")
        
    @property
    def message_queue(self):
        """
        Returns the message Queue for sending messages to client.
        """
        lifetime_state = self.persistent_state
        queue = getattr(lifetime_state, "message_queue", None)
        
        if queue is None:
            queue = asyncio.Queue()
            lifetime_state.message_queue = queue
        
        # Finally return the queue
        return queue
        
    @property
    def sock(self):
        """
        Returns the connected socket.
        """
        return self.request.client_socket
        
    @property
    def session_id_header(self) -> str:
        """
        Returns the formatted session ID header.
        """
        return self._session_id_header.title()
        
    @property
    def has_session_id_header(self) -> bool:
        """
        Checks whether the current request has session id header.
        """
        return self.request.get_header(self._session_id_header, None) is not None
        
    def strictly_async(self):
        return True # Set the view to be strictly asynchronous
    
    async def assign_session_if_new(self, method: str) -> dict:
        """
        Mint a session id on a successful 'initialize' call that didn't
        already have one, firing on_session_create. Must run before any
        after_dispatch hook — the default save hook needs the id to exist
        first, or the session's initial state is silently dropped.
    
        Returns response headers carrying the new id (empty dict otherwise).
        """
        if method != "initialize" or self.session_id:
            return {}
        
        # Assign new session id
        session_id = self.session.assign_new_session_id()
        
        # Run session create hook.
        await self.run_hooks("on_session_create", self.session_id)
        
        # Return session headers
        return {self.session_id_header: session_id}
    
    def register_default_hooks(self):
        """
        Registers the default hooks.
        """
        async def ensure_session_saved(*args, **kwargs):
            """
            Ensure the session is saved.
            """
            if self.session_id and self.session.needs_update():
                self.session.save()
        
        defaults = {
            "after_dispatch": ensure_session_saved,
            "after_sse_send": ensure_session_saved,
        }
        
        for hook, handler in defaults.items():
            self.register_hook(hook, handler)
        
    def register_hook(self, hook_name: str, callback: callable) -> None:
        """
        Register a hook callback for extension points.
        
        Args:
            hook_name: Name of the hook point (e.g., "before_dispatch")
            callback: Async function to call at the hook point
        
        Hook Points:
            - before_dispatch: (body, rpc_id, method, params) -> (handled, response)
                Called before dispatching a JSON-RPC method. If handled is True,
                returns response immediately.
            
            - after_dispatch: (rpc_id, method, result) -> modified_result
                Called after a successful dispatch. Can modify the result.
            
            - before_sse_send: (message) -> modified_message
                Called before sending an SSE event. Can modify the message.
            
            - after_sse_send: (message) -> None
                Called after sending an SSE event.
            
            - on_session_create: (session_id) -> None
                Called when a new session is created.
            
            - on_session_delete: (session_id) -> None
                Called when a session is deleted.
        """
        if hook_name not in self._hooks:
            raise ValueError(f"Unknown hook point: {hook_name}")
        self._hooks[hook_name].append(callback)
    
    def unregister_hook(self, hook_name: str, callback: callable) -> None:
        """
        Remove a previously registered hook callback.
        """
        if hook_name in self._hooks and callback in self._hooks[hook_name]:
            self._hooks[hook_name].remove(callback)
    
    async def run_hooks(self, hook_name: str, *args, **kwargs):
        """
        Run all registered hooks for a given hook point.
        
        Returns:
            For before_dispatch: (handled, response) - first hook that handles
                the request stops further hooks.
            For other hooks: the last returned value, or None.
        """
        if hook_name not in self._hooks:
            return None
        
        if hook_name == "before_dispatch":
            # Special handling: first hook that handles stops processing
            for hook in self._hooks[hook_name]:
                handled, response = await hook(*args, **kwargs)
                if handled:
                    return (handled, response)
            return (False, None)
        
        # Other hooks: run all and return the last non-None result
        result = None
        
        for hook in self._hooks[hook_name]:
            hook_result = await hook(*args, **kwargs)
            if hook_result is not None:
                result = hook_result
        return result
        
    def register_default_capabilities(self):
        """
        Registers the default capabilities e.g. InitializeCapability, ToolsCapability, etc.
        """
        defaults = {
            "initialize": (InitializeCapability(self), None),
            "notifications": (NotificationsCapability(self), None),
            "ping": (PingCapability(self), None),
            "tools": (ToolsCapability(self), None),
            "resources": (ResourcesCapability(self), None),
            "prompts": (PromptsCapability(self), None),
            "_server_requests": (ServerRequestsCapability(self), "server"),
            "sampling": (SamplingCapability(self), None),
            "roots": (RootsCapability(self), None),
            "elicitation": (ElicitationCapability(self), None),
        }
        
        for namespace, (capability, alias) in defaults.items():
            self.register_capability(namespace, capability, alias=alias)
        
    def register_capability(self, name: str, capability: Capability, alias: Optional[str] = None) -> Capability:
        """
        Register a capability under a namespace, routing every '{name}/*' method to it.

        Args:
            name: The namespace to claim, e.g. "tools" claims "tools/list", "tools/call", etc.
            capability: The Capability instance to route matching methods to.
            alias: Optional short name for direct access via `self.capabilities.{alias}`. If not provided, you can still access
                   via `self.capabilities.{name}`.
                   
        Returns:
            Capability: The same instance, for chaining.

        Example:
            ```python
            self.register_capability("tools", ToolsCapability(self))
            ```
        """
        try:
            # Register capability.
            capability = self.capabilities.register(name, capability, alias=alias)
        
        except MCPCapabilityExistsError as exc:
            # Capability not registered
            raise MCPCapabilityExistsError(
                f"A capability with the namespace '{name}' is already registered. "
                "Call `unregister_capability()` before registering it again."
            ) from exc
            
        # Return the final capabilities.
        return capability
    
    def unregister_capability(self, name: str) -> Capability:
        """
        Remove a previously registered capability, running its cleanup() hook first.
        """
        # Remove from accessor
        capability = self.capabilities.unregister(name)
            
        # Do cleanup on capability.
        capability.cleanup()
        
        # Return removed capability
        return capability
             
    def get_handler(self, method: str):
        """
        Resolve a JSON-RPC method to a callable.

        Notes:
            Checks any capability registered for the method's namespace - the
            part before the '/'. e.g. "tools/call" falls back to whatever
            was registered under the "tools" namespace, dispatching "call".

        Returns:
            A callable of shape `handler(params)`, or None if nothing matches.
        """
        namespace, _, action = method.partition("/")
        capability = self.capabilities.registry.get(namespace)
        
        if capability is None:
            return None
        
        # Bind the resolved action so this reads like any other handler(params).
        async def capability_handler(params):
            return await capability.dispatch(action, params)
        
        return capability_handler
        
    @csrf_exempt
    async def run(self) -> Optional[JsonResponse]:
        """
        Entry point, required by the routing dispatch convention. Delegates to `handle_rpc()`.
        """
        try:
            return await self.handle_rpc()
        finally:
            # Only cleanup non-session requests.
            if not self.session_id:
                self.cleanup_resources()
        
    async def authenticate(self) -> AuthResult:
        """
        Override to gate access to this MCP server. Must return an
        `AuthResult` - default is `AuthResult()`, i.e. allowed with no scope
        restriction. Pass `scopes=` to grant specific scopes, which
        `authorize()` then checks automatically against any `scopes=`
        declared on a @tool/@resource/@prompt:
        
        ```python
        async def authenticate(self):
            token = self.request.headers.get("Authorization", "").removeprefix("Bearer ")
            claims = verify_jwt(token)
            if claims is None:
                return AuthResult.deny()
            return AuthResult(scopes=claims["scopes"])
        ```
        """
        return AuthResult()
        
    async def authorize(self, scopes: list) -> bool:
        """
        Check whether the authenticated client has required scopes.
        
        Called before a tool/resource/prompt with declared `scopes=` runs.
        Default checks those scopes against `self.granted_scopes` (set from
        the `AuthResult` returned by `authenticate()`); `None` there means
        unrestricted.
        
        In the common case you never need to override this -
        just return the right scopes from `authenticate()`. Override only
        for non-scope-based logic (e.g. per-name rules).
        """
        if not scopes:
            return True
    
        if self.granted_scopes is None:
            return False
    
        return set(scopes).issubset(self.granted_scopes)
    
    def validate_origin(self) -> bool:
        """
        Check the request's Origin header against `allowed_origins`. 
        Missing Origin always passes - most
        non-browser MCP clients don't send one - this only catches a
        present-but-mismatched Origin, which is the DNS-rebinding/malicious-
        webpage case it's meant for.
        """
        from duck.http.middlewares.security.csrf import CSRFMiddleware, OriginError
        
        allowed = self.allowed_origins or []
        
        if "*" in allowed:
            return True
        
        # Get origin header
        origin = self.request.get_header("origin")
        
        if origin is None or not allowed:
            return True
            
        # Origin header present - check if request host matches origin.
        try:
            CSRFMiddleware.check_origin_ok(self.request)
        except OriginError:
            return False
            
        # Checks if origin is allowed
        return URL(origin).host in allowed
        
    async def handle_rpc(self) -> Optional[JsonResponse]:
        """
        Validate origin, authenticate the request, parse it as JSON-RPC 2.0, and dispatch it to the matching MCP method handler.
        """
        # CORS preflight - answer directly, before auth/origin checks, since
        # preflights carry no credentials and browsers expect a fast, bodyless
        # reply regardless of what this server ends up requiring.
        if self.request.method == "OPTIONS":
            return self.handle_preflight()
            
        if self.request.method == "DELETE":
            return await self.handle_session_delete()
            
        if not self.validate_origin():
            return self.error_response(None, MCPErrorCode.ORIGIN_NOT_ALLOWED, "Origin not allowed", status=403)
            
        # Session id travels via header on every request after 'initialize' issues one.
        self.session_id = self.request.get_header(self.session_id_header)
        
        # Do some auth - after attaching session
        auth = await self.authenticate()
        
        if not isinstance(auth, AuthResult):
            raise TypeError(
                f"authenticate() must return an AuthResult, got {type(auth).__name__}"
            )
        
        # Get auth scopes.
        self.granted_scopes = auth.scopes
        
        if not auth.allowed:
            return jsonify(
                {"jsonrpc": "2.0", "id": None, "error": {"code": MCPErrorCode.UNAUTHORIZED, "message": "Unauthorized"}},
                status_code=401,
                headers={"WWW-Authenticate": 'Bearer realm="mcp"'},
            )
            
        # A bare GET is the standalone server-push stream, not a JSON-RPC call - no body to parse.
        if self.request.method == "GET":
            if self.sse and self.wants_sse():
                # Server and client wants SSE
                if not self.session_id:
                    # Client didn't provide the session ID
                    return self.error_response(
                        None, MCPErrorCode.INVALID_REQUEST,
                        "No MCP Session ID header found. If you're using legacy "
                        "HTTP+SSE, this server doesn't support it - use Streamable HTTP.",
                        status=400,
                    )
                
                # Handle SSE streaming.
                return await self.handle_sse_stream()
            
            # SSE not applicable here because either server or client doesn't support SSE
            return self.error_response(
                None, MCPErrorCode.METHOD_NOT_FOUND,
                "This server uses the Streamable HTTP transport, not legacy SSE. "
                "POST JSON-RPC requests to this same endpoint instead of GET.",
                status=405,
            )
        
        # Use alternative streamable HTTP
        return await self.handle_streamable_http(self.request.content)
        
    def handle_preflight(self) -> HttpResponse:
        """
        Answer a CORS preflight OPTIONS request with a 204 and no body -
        just the Access-Control-* headers the browser needs before it will
        send the actual POST/GET.
        """
        origin = self.request.get_header("origin") or "*"
    
        response = HttpResponse(
            status_code=204,
            headers={
                "Access-Control-Allow-Origin": origin,
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS, DELETE",
                "Access-Control-Allow-Headers": f"Content-Type, Authorization, {self.session_id_header}, Accept, Mcp-Protocol-Version",
                "Access-Control-Max-Age": "86400",
            },
        )
    
        if origin != "*":
            response.set_header("Vary", "Origin")
        
        return response
    
    async def handle_session_delete(self):
        """
        Terminate an MCP session and clean up associated resources.
        """
        if self.session_id:
            # Detach session
            self.session.delete()
            
            # Cleanup session-scoped resources.
            self.cleanup_resources()
            
            # Run on_session_delete hooks
            await self.run_hooks("on_session_delete", self.session_id)
            
        # Return the final response.
        return HttpResponse(status_code=200)
    
    async def handle_streamable_http(self, raw_body: str) -> JsonResponse:
        """
        Parse a POST body as JSON-RPC 2.0 and dispatch it to the matching
        handler. 
        
        Notes:
            Replies with a single JSON body, unless the client asked for SSE and `self.sse` is on - then `handle_single_sse()` streams the response instead.
        """
        try:
            body = json.loads(raw_body)
        except (ValueError, TypeError):
            return self.error_response(None, MCPErrorCode.PARSE_ERROR, "Parse error")
        
        # Get data from body
        rpc_id = body.get("id")
        method = body.get("method")
        params = body.get("params") or {}
        
        # Run before_dispatch hooks - they can intercept client responses
        handled, hook_response = await self.run_hooks(
            "before_dispatch", body, rpc_id, method, params
        )
        
        if handled:
            # Run after_dispatch hooks
            _ = await self.run_hooks("after_dispatch", rpc_id, method, result=None)
            
            # Return the hook response.
            return hook_response
        
        # Not handled, handle here.
        handler = self.get_handler(method)
        
        if handler is None:
            return self.error_response(rpc_id, MCPErrorCode.METHOD_NOT_FOUND, f"Method not found: {method}")
    
        # Stream this call's response as SSE instead of one JSON body, if asked.
        if self.sse and self.wants_sse():
            # The below method might return a response immediately if an error happened.
            return await self.handle_single_sse(rpc_id, method, handler, params)
            
        # Headers to be sent alongside response.
        response_headers = {}
        
        try:
            # Get handler result.
            result = await handler(params)
            
            # Assign session if new.
            response_headers = await self.assign_session_if_new(method)
            
            # Run after_dispatch hooks
            result = await self.run_hooks("after_dispatch", rpc_id, method, result) or result
            
        except ExpectingNoResponse as exc:
            raise exc
            
        except PermissionError as exc:
            if SETTINGS['DEBUG']:
                logger.log_exception(exc)
            return self.error_response(rpc_id, MCPErrorCode.NOT_AUTHORIZED, str(exc))
        
        except Exception as exc:
            if SETTINGS['DEBUG']:
                logger.log_exception(exc)
            return self.error_response(rpc_id, MCPErrorCode.INTERNAL_ERROR, str(exc))
            
        # Return success response
        return jsonify({"jsonrpc": "2.0", "id": rpc_id, "result": result}, headers=response_headers)
    
    def wants_sse(self) -> bool:
        """
        Whether the client's Accept header asks for an SSE stream rather than a plain JSON response.
        """
        return "text/event-stream" in self.request.get_header("accept", "")
        
    async def finalize_initial_sse_response(self, response: HttpResponse):
        """
        Finalizes the first/initial response that gets sent to client when initiating SSE.
    
        Notes:
            Sets the CORS headers needed for browser-based clients (e.g. MCP
            Inspector's "direct" mode) to read this response and its Mcp-Session-Id header.
        """
        # Echo the request Origin rather than a literal "*" - the CORS spec
        # forbids combining "*" with Allow-Credentials, and echoing costs
        # nothing if credentials are never turned on.
        origin = self.request.get_header("origin") or "*"
        
        response.set_header("Access-Control-Allow-Origin", origin)
        response.set_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS, DELETE")
        response.set_header("Access-Control-Allow-Headers", f"Content-Type, Authorization, {self.session_id_header}, Accept")
    
        # Without this the client can't read Mcp-Session-Id from the
        # response headers even though the body itself is visible.
        response.set_header("Access-Control-Expose-Headers", self.session_id_header)
    
        if origin != "*":
            response.set_header("Vary", "Origin")
        
    async def handle_single_sse(self, rpc_id, method, handler, params) -> Optional[JsonResponse]:
        """
        Handle a single JSON-RPC call by streaming its response back as
        Server-Sent Events on this same connection, instead of one JSON body.
        
        Notes:
            Opens the SSE response immediately, then runs `handler(params)` with
                `self._sse_initiated = True` so any `self.notify(...)` made during the
                call - e.g. tool progress - writes straight to this socket as it happens.
            
            The call's own result (or error) is sent last as a single
                `message` event, then the stream closes. Scoped to this one
                request/response, unlike the persistent channel `handle_sse_stream()` opens.
        
        Raises:
            ExpectingNoResponse: Since the response has already been written directly to the socket.
        """
        response_headers = await self.assign_session_if_new(method) or {}
        
        if not self.session_id:
            error = (
                f"No {self.session_id_header} header found. If you're using legacy "
                "HTTP+SSE, this server doesn't support it - use Streamable HTTP.",
            )
            
            if not self.has_session_id_header:
                error = (
                    f"{self.session_id_header} header found but it's empty.",
                )
                
            # Generate error response
            response = self.error_response(
                rpc_id, MCPErrorCode.INVALID_REQUEST, error, 
                status=400,
            )
            
            # Return the response so Duck will send it - this will cancel further processing.
            return response
            
        else:
            response = HttpResponse(
                headers={
                    "Content-Type": "text/event-stream",
                    "Cache-Control": "no-cache",
                    **response_headers,
                }
            )
            
            # Finalize the initial sse response - adding CORS etc.
            await self.finalize_initial_sse_response(response)
            
        # Set client socket blocking to False if set to true.
        self.sock.setblocking(False)
    
        # Send the SSE response headers immediately.
        await self._response_handler.async_send_response(response, self.sock, request=self.request)
        
        # Notifications from here on go straight to this socket.
        self._sse_initiated = True
    
        try:
            result = await handler(params)
            
            # Run after_dispatch hooks
            result = await self.run_hooks("after_dispatch", rpc_id, method, result) or result
            
            # Create message
            message = {"jsonrpc": "2.0", "id": rpc_id, "result": result}
    
        except ExpectingNoResponse as exc:
            raise exc
            
        except PermissionError as exc:
            message = {"jsonrpc": "2.0", "id": rpc_id, "error": {"code": MCPErrorCode.NOT_AUTHORIZED, "message": str(exc)}}
            
            if SETTINGS['DEBUG']:
                logger.log_exception(exc)
                
        except Exception as exc:
            message = {"jsonrpc": "2.0", "id": rpc_id, "error": {"code": MCPErrorCode.INTERNAL_ERROR, "message": str(exc)}}
            
            if SETTINGS['DEBUG']:
                logger.log_exception(exc)
                
        try:
            # Final event: the call's own result or error.
            await self.send_sse_event(message)
        finally:
            self._sse_initiated = False
            
        # Close socket if not closed properly.
        SocketIO.close(self.sock)
        
        # Tell Duck not to close the socket - it's already been handled here.
        raise ExpectingNoResponse("SSE response sent.")
    
    async def handle_sse_stream(self) -> None:
        """
        Open a standalone SSE stream for a bare GET request - the MCP spec's
        optional server-push channel, separate from the per-call stream a POST
        gets via `handle_single_sse()`. 
        
        Notes:
            Requires an `Mcp-Session-Id` header (issued on `initialize`) so `notify()` calls from other requests in the same
            session - e.g. a background job kicked off by a tool call - can be
            routed here via the shared `_session_queues` registry. Held open with
            periodic pings so intermediaries don't close it as idle.
        
        Raises:
            ExpectingNoResponse: Since the response has already been written directly to the socket.
        """
        response = HttpResponse(
            headers={
                "Content-Type": "text/event-stream",
                "Cache-Control": "no-cache",
            }
        )
        
        # Finalize the initial sse response - adding CORS etc.
        await self.finalize_initial_sse_response(response)
            
        # Set client socket blocking to False if set to true.
        self.sock.setblocking(False)
        
        # Send the success response immediately.
        await self._response_handler.async_send_response(response, self.sock, request=self.request)
        
        # Mark that sse has been initiated.
        self._sse_initiated = True
        
        try:
            while True:
                try:
                    message = await asyncio.wait_for(self.message_queue.get(), timeout=self.SSE_PING_INTERVAL)
                    await self.send_sse_event(message)
                    
                except asyncio.TimeoutError:
                    await self.send_sse_event({}, event="ping")
        
        except (ConnectionResetError, BrokenPipeError):
            pass
        
        finally:
            # Close socket if not closed properly.
            SocketIO.close(self.sock)
            
        # Raise this error - tell Duck that we already handled sending response manually.
        raise ExpectingNoResponse("SSE stream closed.")
        
    async def send_sse_event(self, message: dict, event: str = "message"):
        """
        Write a single Server-Sent Event (`event:` + `data:` lines, blank
        line terminated) to the socket, in SSE_CHUNK_SIZE-byte pieces so a
        large payload doesn't block the event loop with one giant write.
        """
        if not self._sse_initiated:
            raise MCPSseNotInitializedError('MCP SSE not initiated.')
            
        # Run before_sse_send hooks
        message = await self.run_hooks("before_sse_send", message) or message
        
        # Create a payload to send directly to socket.
        payload = f"event: {event}\ndata: {json.dumps(message)}\n\n".encode()
        
        for i in range(0, len(payload), self.SSE_CHUNK_SIZE):
            chunk = payload[i:i + self.SSE_CHUNK_SIZE]
            await SocketIO.async_send(sock=self.sock, data=chunk)
            await asyncio.sleep(0)
        
        # Run after_sse_send hooks
        await self.run_hooks("after_sse_send", message)
    
    async def ensure_sse_event_sent(self, message: dict, event: str = "message"):
        """
        Tries writting single Server-Sent Event to the socket only if SSE has been initialized
        else the message is added to session queue.
        """
        if self._sse_initiated:
            await self.send_sse_event(message)
        
        # Get queue
        try:
            queue = self.message_queue
        except MCPError:
            return
            
        if queue is not None:
            await queue.put(message)
        
    async def notify(self, method: str, params: dict = None):
        """
        Push a JSON-RPC notification (e.g. progress) to the client. If this
        request is itself streaming a response (inside `handle_sse()`), it's
        sent directly on this socket. Otherwise, if this request's session has
        a standalone GET stream open elsewhere (via `handle_sse_stream()`), it's
        queued for delivery there. If neither applies, this is a no-op, so
        tools can call it unconditionally:
        
        ```python
        @tool(description="Process a big job")
        async def process(self, job_id: str) -> str:
            await self.notify("notifications/progress", {"progress": 50})
            ...
            return "done"
        ```
        """
        message = {"jsonrpc": "2.0", "method": method, "params": params or {}}
        
        if self._sse_initiated:
            await self.send_sse_event(message)
        
        # Get queue
        queue = self.message_queue
        
        if queue is not None:
            await queue.put(message)
        
    def error_response(self, rpc_id, code: Union[int, MCPErrorCode], message, status=200):
        """
        Build a JSON-RPC 2.0 error response envelope.
        """
         # Set debug message.
        self.request.META["DEBUG_MESSAGE"] = f"MCP Error: '{self.name}' : {message}"
        
        return jsonify(
            {"jsonrpc": "2.0", "id": rpc_id, "error": {"code": int(code), "message": message}},
            status_code=status,
        )
        
    def empty_response(self) -> JsonResponse:
        """
        Return an empty 200 OK JSON response.
        """
        return JsonResponse({}, status_code=200)

    def cleanup_resources(self):
        """
        Ensure all capabilities are removed - ensuring cleanup on every capability.
        
        Safe to delete session-scoped resources here.
        """
        for name in self.capabilities.registry.copy().keys():
            self.unregister_capability(name)
