## Upcoming Features

### Duck AI Agent Framework

A native AI agent system built into Duck Framework.

The goal is to provide developers with a simple way to build intelligent applications using Duck's existing MCP infrastructure.

Planned features:

- Native `Agent` API for building AI-powered applications
- Built-in MCP client integration for discovering and using tools
- LLM provider abstraction
- Async-first agent execution
- Tool calling and function execution
- Conversation memory and persistent sessions
- Streaming AI responses
- Agent lifecycle events and hooks
- Agent workflows and task orchestration
- Multi-agent collaboration support
- Built-in evaluation and tracing tools

Example:

```python
from duck.ai import Agent

agent = Agent(
    model="gpt-5",
    tools="auto",
)

response = await agent.run(
    "Build a user dashboard component"
)

print(response.text)

