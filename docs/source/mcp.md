# 🤖 Duck MCP (Model Context Protocol) Support

![MCP](https://img.shields.io/badge/MCP-Protocol-blue)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Duck Framework](https://img.shields.io/badge/Duck%20Framework-MCP-orange)
![Transport](https://img.shields.io/badge/Transport-Streamable%20HTTP-green)

Duck Framework provides built-in support for the **Model Context Protocol (MCP)**, allowing Python applications to expose tools, resources, prompts, and advanced AI integrations through a standardized protocol.

MCP enables AI clients such as MCP Inspector, AI assistants, and other compatible clients to communicate with your Duck application.

With Duck MCP you can build servers that expose:

- Tools that AI clients can execute
- Resources that clients can read
- Prompts for reusable AI workflows
- Sampling requests to ask clients for AI generation
- Root discovery
- User elicitation
- Real-time notifications
- Scope-based authorization
- Server-Sent Events (SSE) streaming

---

## Table of Contents

1. [What is MCP?](#what-is-mcp)
2. [Quick Start](#quick-start)
3. [Testing with MCP Inspector](#testing-with-mcp-inspector)
4. [Core Concepts](#core-concepts)
5. [Capabilities](#capabilities)
6. [Hooks](#hooks)
7. [Transport & Connection Lifecycle](#transport--connection-lifecycle)
8. [Server-Sent Events (SSE)](#server-sent-events-sse)
9. [Transport Summary](#transport-summary)

---

## What is MCP?

Model Context Protocol (MCP) is a protocol that standardizes communication between AI applications and external services.

Instead of every AI client implementing custom integrations, MCP defines a common interface.

**Simplified view:**

```text
AI Client
    |
    | MCP (JSON-RPC)
    |
Duck MCP Server
    |
    |
Your Application Logic
```

**Without MCP** — every application needs a different integration:

```text
AI Client
   |
   | Custom API
   |
Your Server
```

**With MCP** — one standardized interface:

```text
AI Client
   |
   | MCP
   |
Duck MCP Server
   |
   | Tool call
   |
Your Application Logic
```

---

## Quick Start

Create an MCP server by extending `MCPView`.

```python
from duck.contrib.mcp import MCPView, tool


class MyMCPServer(MCPView):
    name = "my-server"
    version = "1.0.0"

    @tool(description="Add two numbers")
    async def add(self, a: int, b: int):
        return a + b
```

Register it:

```python
# urls.py
from duck.urls import path

urlpatterns = [
    path("/mcp", MyMCPServer, "mcp"),
]
```

Your MCP endpoint is now available:

```text
POST /mcp
```

---

## Testing with MCP Inspector

Duck MCP can be tested quickly using the official MCP Inspector without creating a separate client application.

The MCP Inspector provides a visual interface for connecting to an MCP server, exploring available capabilities, calling tools, reading resources, testing prompts, and inspecting protocol messages.

### Running the Test MCP Server

Duck provides a ready-to-use test MCP server:

```text
duck.contrib.mcp.testserver.TestMCPServer
```

It demonstrates the main MCP features:

- Tools
- Resources
- Resource templates
- Prompts
- Sampling
- Roots
- Elicitation
- Authentication
- Notifications
- Progress updates

### Registering the MCP Endpoint

Before testing your MCP server, make sure the MCP view is registered in your Duck application's `urls.py`. Your MCP server will not be available until it has been added to `urlpatterns`.

```python
from duck.urls import path
from duck.contrib.mcp.testserver import TestMCPServer


urlpatterns = [
    path("/mcp", TestMCPServer, "mcp"),
]
```

The path you choose becomes your MCP endpoint. In this example:

```text
http://localhost:8000/mcp
```

is the URL that MCP clients connect to.

### Starting the Duck Server

Start your Duck application normally:

```text
python web/main.py
```

The MCP endpoint will be available at `http://localhost:8000/mcp` (the exact port depends on your Duck server configuration).

### Connecting MCP Inspector

No MCP Inspector installation is required. Run it directly using `npx`:

```text
npx @modelcontextprotocol/inspector
```

This opens the MCP Inspector interface in your browser.

**Configure the connection:**

1. Select the transport: `Streamable HTTP`
2. Enter your MCP endpoint: `http://localhost:8000/mcp`
3. Click `Connect`

The Inspector will perform the MCP initialization handshake automatically.

### Testing Tools

After connecting, open the **Tools** section. You should see tools from `@TestMCPServer`, for example:

```text
add
admin_test
test_sampling
test_roots
test_elicitation
test_notification
```

**Calling a tool** — call `add` with:

```json
{
    "a": 10,
    "b": 20
}
```

The server responds:

```json
{
    "result": 30
}
```

### Testing Notifications

The test server includes notification examples. Call `test_notification` with:

```json
{
    "message": "Hello MCP"
}
```

The server sends a `notifications/test` event, which the Inspector displays.

### Testing Resources

Open the **Resources** section. Example resource: `test://hello`. Reading it returns:

```text
Hello from MCP resource
```

### Testing Resource Templates

Resource templates allow dynamic resources. Example template:

```text
users:///{user_id}
```

Requesting `users:///123` returns:

```json
{
    "id": "123",
    "name": "Test User"
}
```

### Testing Authentication

The test server includes a protected tool, `admin_test`, which requires the `admin` scope.

- Without authentication: `Unauthorized`
- With `Authorization: Bearer admin-token`: the tool succeeds

### Testing Sampling

Sampling tests server-to-client model generation. Call `test_sampling`; the server sends `sampling/createMessage` to the MCP client, and the client decides how to generate the response.

```text
Duck MCP Server
        |
        ↓
sampling/createMessage
        |
        ↓
MCP Client Model
        |
        ↓
Generated response
        |
        ↓
Duck MCP Server
```

### Testing Elicitation

Elicitation allows the server to request additional user input. Call `test_elicitation`; the client displays a form/question, for example:

```text
What is your favorite programming language?
```

The user's answer is returned to the server.

### Debugging MCP Messages

MCP Inspector is also useful for understanding the protocol. You can inspect:

- Initialization handshake
- Capability discovery
- JSON-RPC requests
- JSON-RPC responses
- Notifications
- Server-to-client requests

This makes it easier to debug custom capabilities and integrations.

### Recommended Development Workflow

```text
1. Create MCPView
        ↓
2. Add tools/resources/prompts
        ↓
3. Start Duck server
        ↓
4. Open MCP Inspector
        ↓
5. Test protocol interactions
        ↓
6. Build your real MCP client integration
```

MCP Inspector removes the need to build a client while developing, allowing you to focus on your MCP server implementation.

---

## Core Concepts

### MCP Request Flow

A typical MCP connection follows this lifecycle:

```text
Client
 |
 | 1. initialize
 |
 v
Duck MCP Server
 |
 | Creates session
 | Advertises capabilities
 |
 v
Client
 |
 | 2. tools/list
 |
 v
Server
 |
 | Returns available tools
 |
 v
Client
 |
 | 3. tools/call
 |
 v
Tool execution
 |
 | Optional:
 | - notifications
 | - sampling
 | - elicitation
 |
 v
Tool result
```

### Initialization Flow

Before using an MCP server, the client sends `initialize`:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {}
}
```

Duck responds with:

```json
{
  "protocolVersion": "2024-11-05",
  "serverInfo": {
    "name": "my-server",
    "version": "1.0.0"
  },
  "capabilities": {
    "tools": {},
    "resources": {},
    "prompts": {}
  }
}
```

After initialization:

- A session ID is created
- Capabilities are stored
- The client can start using the server

### Tools

Tools are functions that MCP clients can execute.

```python
from duck.contrib.mcp import tool


@tool(description="Search users")
async def search_users(self, query: str):
    return [
        {
            "name": "John"
        }
    ]
```

The client discovers tools via `tools/list`, then executes via `tools/call`:

```text
Client
 |
 | tools/call
 |
 v
Duck
 |
 | Execute Python function
 |
 v
Return result
```

### Resources

Resources provide readable data that MCP clients can access. They are useful for exposing:

- Configuration data
- Documents
- Database records
- Files
- Application state

```python
from duck.contrib.mcp import resource


@resource(
    uri="config://app",
    name="Application Config",
    mime_type="application/json",
)
async def config(self):
    return {
        "debug": True
    }
```

Clients discover resources via `resources/list`, then read via `resources/read`:

```text
Client
 |
 | resources/read
 |
 v
Duck MCP Server
 |
 | Execute resource method
 |
 v
Return contents
```

### Resource Templates

Resource templates allow dynamic resources with parameters. Instead of registering every resource individually (`users:///1`, `users:///2`, `users:///3`, ...), you can define a template:

```python
from duck.contrib.mcp import resource_template


@resource_template(
    uri_template="users:///{user_id}",
    name="User Profile",
    description="Returns user information",
    mime_type="application/json",
)
async def user_profile(self, user_id: str):
    return {
        "id": user_id,
        "name": "Test User",
    }
```

A request to `users:///123` is resolved internally as `user_profile(user_id="123")`.

### Prompts

Prompts expose reusable AI instructions, allowing clients to request predefined prompt templates.

```python
from duck.contrib.mcp import prompt


@prompt(
    name="welcome",
    description="Generate a welcome message",
)
async def welcome(self, name: str):
    return [
        {
            "role": "user",
            "content": {
                "type": "text",
                "text": f"Hello {name}",
            },
        }
    ]
```

Clients discover prompts via `prompts/list`, then request via `prompts/get`.

### Sampling

Sampling allows the MCP server to request AI generation from the client. The server does not need its own AI provider.

```text
Duck MCP Server
 |
 | sampling/createMessage
 |
 v
AI Client
 |
 | Generate response
 |
 v
Duck MCP Server
```

```python
response = await self.capabilities.sampling.create_message(
    messages=[
        {
            "role": "user",
            "content": {
                "type": "text",
                "text": "Explain MCP",
            },
        }
    ],
    max_tokens=100,
)
```

This allows tools to use the client's AI capabilities.

### Notifications

Notifications are server-to-client messages that do not expect a response. Common uses:

- Progress updates
- Status changes
- Background events
- Long-running operations

```python
await self.notify(
    "notifications/progress",
    {
        "progressToken": "job-1",
        "progress": 50,
        "total": 100,
    },
)
```

```text
Tool execution
      |
      v
notify()
      |
      v
Client receives update
```

### Roots

Roots allow the MCP server to ask the client which filesystem roots, projects, or working directories are available. This is useful when a client application controls local resources and wants to expose them safely to an MCP server without directly giving the server unrestricted filesystem access.

**How it works:**

```text
Server -> roots/list request -> Client
Client -> returns available roots -> Server
```

The server does not decide what roots exist — the client provides the information.

**Example use cases:**

- Reading files from a user's project directory
- Understanding the current workspace
- Building tools that operate on the user's local environment
- Allowing an AI assistant to work inside an IDE workspace

**Server usage:**

```python
@tool(description="List available client roots")
async def list_workspace(self):
    roots = await self.capabilities.roots.list_roots()

    return {
        "roots": roots,
    }
```

The client responds with roots such as:

```json
{
    "roots": [
        {
            "uri": "file:///home/user/project",
            "name": "My Project"
        }
    ]
}
```

**Important notes:**

- Roots are controlled by the client
- The server should not assume filesystem access
- Roots provide discovery, not direct file permissions
- Clients may return no roots

### Elicitation

Elicitation allows the MCP server to request additional information from the user while a tool or operation is running. It is useful when the server needs information that was not provided initially.

**How it works:**

```text
Server starts tool execution
        ↓
Server sends elicitation/create request
        ↓
Client shows a form/question to the user
        ↓
User provides information
        ↓
Client sends response
        ↓
Server continues execution
```

**Example use cases:**

- Asking for missing configuration values
- Confirming an important action
- Requesting user preferences
- Collecting structured input

**Server usage:**

```python
@tool(description="Ask user for preferences")
async def setup_preferences(self):

    result = await self.capabilities.elicitation.create(
        message="What programming language do you prefer?",
        requested_schema={
            "type": "object",
            "properties": {
                "language": {
                    "type": "string"
                }
            },
            "required": [
                "language"
            ]
        },
    )

    return result
```

The client may display a form like:

```text
What programming language do you prefer?

[ Python ]
[ Submit ]
```

And return:

```json
{
    "language": "Python"
}
```

**Important notes:**

- Elicitation is initiated by the server
- The user always controls the final answer
- The client may reject or cancel the request
- Servers should handle incomplete responses gracefully

**Roots vs. Elicitation**

| Capability | Direction | Purpose |
|---|---|---|
| Roots | Server asks client | Discover available client resources |
| Elicitation | Server asks user through client | Collect additional information |

Both capabilities allow MCP servers to interact with their environment without taking direct control away from the client.

### Authentication and Scopes

MCP methods can require authorization scopes.

```python
@tool(
    description="Admin action",
    scopes=["admin"],
)
async def admin_action(self):
    return "allowed"
```

Implement authentication:

```python
from duck.contrib.mcp.auth import AuthResult


async def authenticate(self):
    token = self.request.get_header("authorization")

    if token == "Bearer admin-token":
        return AuthResult(
            scopes={"admin"}
        )

    return AuthResult(scopes=[])  # Authenticated but with no granted scopes. Use AuthResult.deny() to reject authentication entirely.
```

**Authentication flow:**

```text
Incoming request
 |
 v
authenticate()
 |
 v
Scopes checked
 |
 +------------+
 |            |
Allowed     Denied
 |
 v
Execute method
```

---

## Capabilities

Capabilities are the main extension system in Duck MCP.

A capability owns a namespace and handles all MCP methods under that namespace. Instead of adding protocol handlers directly into `MCPView`, functionality is isolated into reusable capability classes.

For example, `tools/list` and `tools/call` are handled by `ToolsCapability`, while `resources/list` and `resources/read` are handled by `ResourcesCapability`.

**The flow:**

```text
Incoming MCP Request
        ↓
Method namespace extracted
        ↓
Capability lookup
        ↓
Capability handler execution
        ↓
JSON-RPC response
```

### Built-in Capabilities

| Capability | Namespace | Purpose |
|---|---|---|
| Initialize | `initialize` | MCP handshake and capability discovery |
| Ping | `ping` | Client/server liveness checks |
| Tools | `tools` | Expose callable server functions |
| Resources | `resources` | Expose readable data sources |
| Prompts | `prompts` | Provide reusable prompt templates |
| Sampling | `sampling` | Request model generation from the client |
| Roots | `roots` | Discover client-provided filesystem roots |
| Elicitation | `elicitation` | Request additional user input |
| Server Requests | `_server_requests` | Internal server-to-client request handling |
| Notifications | `notifications` | Handle MCP notifications |

### Creating Custom Capabilities

Custom capabilities extend the MCP protocol with application-specific features.

```python
from duck.contrib.mcp.capabilities import Capability


class StatisticsCapability(Capability):

    def setup(self):
        self.handlers = {
            "report": self.report,
        }

    async def report(self, params):
        return {
            "users": 100,
            "requests": 5000,
        }
```

Register the capability:

```python
self.register_capability(
    "statistics",
    StatisticsCapability(self),
)
```

The client can now call `statistics/report`.

### Capability Aliases

Capabilities can have aliases for easier server-side access.

```python
self.register_capability(
    "_server_requests",
    ServerRequestsCapability(self),
    alias="server",
)
```

Now instead of `self.capabilities._server_requests`, you can use `self.capabilities.server`.

Aliases are only for internal access — the MCP namespace remains unchanged.

---

## Hooks

Hooks provide lifecycle extension points around MCP execution. Unlike capabilities, hooks do not expose new MCP methods — they observe or modify the server lifecycle.

They are useful for:

- Logging
- Authentication middleware
- Request inspection
- Response modification
- SSE message processing
- Session lifecycle handling

### Available Hooks

| Hook | Trigger |
|---|---|
| `before_dispatch` | Before routing an MCP request |
| `after_dispatch` | After a handler completes |
| `before_sse_send` | Before sending an SSE message |
| `after_sse_send` | After sending an SSE message |
| `on_session_create` | When a new session starts |
| `on_session_delete` | When a session ends |

### Registering Hooks

```python
class MyMCPServer(MCPView):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.register_hook(
            "before_dispatch",
            self.log_request,
        )

    async def log_request(
        self,
        body,
        rpc_id,
        method,
        params,
    ):
        print("MCP method:", method)

        return False, None
```

Returning `(False, None)` continues normal processing. Returning `(True, response)` stops dispatch and returns the provided response.

### Capabilities vs. Hooks

| Feature | Capabilities | Hooks |
|---|---|---|
| Purpose | Add MCP functionality | Modify lifecycle behavior |
| Exposes MCP methods | Yes | No |
| Has namespace | Yes | No |
| Example | `tools/call` | Logging requests |
| Used by clients | Directly | Indirectly |

**A good rule of thumb:**

- Use **Capabilities** when you are adding a new MCP feature.
- Use **Hooks** when you are modifying how the server behaves.

### Example Architecture

A typical Duck MCP server looks like:

```text
                MCP Client
                    |
                    ↓
             MCPView Endpoint
                    |
        +-----------+-----------+
        |           |           |
        ↓           ↓           ↓
   Capabilities   Hooks    Sessions
        |
        ↓
 tools/resources/prompts/custom features
```

Capabilities define what your MCP server can do. Hooks define how your MCP server behaves while doing it.

---

## Transport & Connection Lifecycle

Duck MCP uses the **Streamable HTTP transport** defined by the MCP specification. Unlike the older HTTP+SSE transport, Streamable HTTP uses a single endpoint for JSON-RPC communication.

A typical MCP endpoint:

```python
path("/mcp", MyMCPServer, "mcp")
```

The client communicates with this endpoint using:

- `POST` — Send JSON-RPC requests
- `GET` — Open an optional SSE stream for server notifications
- `DELETE` — Terminate an MCP session

### Request Flow

A normal MCP interaction follows this lifecycle:

```text
Client                              Duck MCP Server
------------------------------------------------------------

POST initialize
        |
        | ------------------------>
        |
        | authenticate()
        | create session
        | discover capabilities
        |
        | <------------------------
        | protocolVersion
        | serverInfo
        | capabilities
        | Mcp-Session-Id


POST tools/list
        |
        | ------------------------>
        |
        | ToolsCapability
        | discovers @tool methods
        |
        | <------------------------
        | available tools


POST tools/call
        |
        | ------------------------>
        |
        | execute Python method
        |
        | optional notifications
        |
        | <------------------------
        | tool result
```

### Session Lifecycle

MCP sessions allow state to persist between requests. A session begins after a successful `initialize` request. The server returns:

```text
Mcp-Session-Id: abc123
```

The client must include this header on future requests:

```http
POST /mcp

Mcp-Session-Id: abc123
```

### Creating Sessions

Sessions are automatically created by Duck after initialization:

```text
initialize request
        |
        v
authenticate()
        |
        v
initialize capabilities
        |
        v
assign session id
        |
        v
save session state
```

Session creation triggers `on_session_create` hooks:

```python
self.register_hook(
    "on_session_create",
    my_callback,
)
```

### Persistent Session State

Duck provides `persistent_state` for storing session-specific data.

```python
state = self.persistent_state

state.username = "Brian"
state.counter = 10
```

The data survives across requests using the same MCP session.

### Closing Sessions

Clients can terminate sessions:

```http
DELETE /mcp

Mcp-Session-Id: abc123
```

Duck will:

1. Delete session data
2. Clean up session resources
3. Run cleanup hooks
4. Remove session-scoped capabilities

```text
Session created
      |
      v
Active requests
      |
      v
DELETE request
      |
      v
Cleanup
      |
      v
Session removed
```

---

## Server-Sent Events (SSE)

SSE allows the server to push messages to the client without waiting for a request.

Enable SSE:

```python
class MyServer(MCPView):

    sse = True
```

SSE is useful for:

- Progress updates
- Notifications
- Long-running operations
- Background events

### SSE Modes

Duck supports two SSE scenarios.

**1. Response Streaming**

A client sends:

```http
POST /mcp
Accept: text/event-stream
```

The response stays open while the request executes.

```python
@tool(description="Long task")
async def process(self):

    await self.notify(
        "notifications/progress",
        {
            "progress": 50,
        }
    )

    return "done"
```

The client receives:

```text
event: message
data: {"method":"notifications/progress"}

event: message
data: {"result":"done"}
```

**2. Persistent Notification Stream**

The client opens:

```http
GET /mcp
Accept: text/event-stream
Mcp-Session-Id: abc123
```

Duck keeps this connection open. Notifications from tools or background tasks are delivered through this stream.

```python
await self.notify(
    "notifications/message",
    {
        "message": "Background job finished",
    }
)
```

### Notifications Flow

Notifications are JSON-RPC messages without an `id`.

```json
{
    "jsonrpc": "2.0",
    "method": "notifications/progress",
    "params": {
        "progress": 50
    }
}
```

Unlike requests, notifications:

- Do not expect responses
- Are fire-and-forget
- Are pushed through SSE

### Disconnect Handling

If a client disconnects:

- The SSE socket closes
- Pending streams are cleaned up
- Future notifications are ignored
- Session data remains until the session expires or a `DELETE` request is received

---

## Transport Summary

| Method | Purpose |
|---|---|
| POST | JSON-RPC requests |
| GET | SSE notification stream |
| DELETE | Close session |
| SSE | Server push communication |
| Session ID | Persistent client state |
