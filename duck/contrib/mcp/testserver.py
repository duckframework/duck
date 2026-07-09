"""
MCP protocol feature test server.

This module provides a complete test MCP server implementation for validating
Duck's MCP support, including:

- Tool registration and execution
- Tool authorization using scopes
- Server-to-client notifications
- Progress notifications
- Client sampling requests
- Client root discovery
- User elicitation requests
- Resource listing and reading
- Resource templates
- Prompt generation
- MCP session handling
- SSE streaming transport

The server is intended for development and protocol verification only.
It exposes `/mcp` as an MCP endpoint and can be connected to MCP clients
such as MCP Inspector for testing supported features.

Example:
    Connect an MCP client to:

        http://localhost:<port>/mcp

    Authentication testing:
        Authorization: Bearer admin-token

    The `admin_test` tool requires the `admin` scope.

"""

import asyncio

from duck.urls import path
from duck.contrib.mcp import MCPView, tool, resource, prompt, resource_template


class TestMCPServer(MCPView):
    """
    MCP test server covering the main protocol features.
    """

    name = "duck-mcp-test-server"
    version = "1.0.0"
    sse = True
    
    async def authenticate(self):
        """
        Test authentication provider.
    
        In a real server this would validate a token/session.
        """
        from duck.contrib.mcp.auth import AuthResult
    
        token = self.request.get_header("authorization")
        
        if token == "Bearer admin-token":
            return AuthResult(scopes={"admin"})
            
        return AuthResult(scopes=[])  # Authenticated but with no granted scopes. Use AuthResult.deny() to reject authentication entirely.
        
    @tool(description="Send a custom MCP notification")
    async def test_notification(self, message: str) -> str:
        """
        Test sending custom notifications to the client.
    
        This verifies that the active SSE stream receives server push messages.
        """
        await self.notify(
            "notifications/test",
            {
                "message": message,
                "timestamp": asyncio.get_event_loop().time(),
            },
        )
    
        return "Notification sent"
    
    @tool(description="Admin-only test tool", scopes=["admin"])
    async def admin_test(self, message: str) -> dict:
        """
        Test scoped authorization.
    
        Requires the client/user to have the `admin` scope.
        """
        return {
            "message": message,
            "authorized": True,
            "scope": "admin",
        }
    
    @tool(description="Add two numbers")
    async def add(self, a: int, b: int) -> int:
        """
        Test addition tool.
        """
        return a + b

    @tool(description="Ask client for sampling generation")
    async def test_sampling(self, prompt: str):
        """
        Test sampling/createMessage.
        """
        response = await self.capabilities.sampling.create_message(
            messages=[
                {
                    "role": "user",
                    "content": {
                        "type": "text",
                        "text": prompt,
                    },
                }
            ],
            max_tokens=100,
        )

        return response

    @tool(description="Test client root discovery")
    async def test_roots(self):
        """
        Test roots/list.
        """
        roots = await self.capabilities.roots.list_roots()
        return {
            "roots": roots,
        }

    @tool(description="Ask the user a question")
    async def test_elicitation(self):
        """
        Test elicitation/create.
        """
        result = await self.capabilities.elicitation.create(
            message="What is your favorite programming language?",
            requested_schema={
                "type": "object",
                "properties": {
                    "language": {
                        "type": "string",
                    }
                },
                "required": [
                    "language",
                ],
            },
        )

        return result

    @resource(
        uri="test://hello",
        name="hello",
        description="Simple test resource",
        mime_type="text/plain",
    )
    async def hello_resource(self):
        """
        Test resource.
        """
        return "Hello from MCP resource"

    @resource_template(
        uri_template="users:///{user_id}",
        name="User Profile",
        description="Returns a user profile by ID",
        mime_type="application/json",
    )
    async def user_profile(self, user_id: str):
        return {
            "id": user_id,
            "name": "Test User",
        }
    
    @prompt(
        name="test_prompt",
        description="Generate a test prompt",
    )
    async def test_prompt(self, name: str):
        """
        Test prompt generation.
        """
        return [
            {
                "role": "user",
                "content": {
                    "type": "text",
                    "text": f"Hello {name}",
                },
            }
        ]
