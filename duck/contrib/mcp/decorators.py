"""
Decorators for MCPView.
"""
import inspect


PY_TO_JSON_TYPE = {
    str: "string", int: "integer", float: "number",
    bool: "boolean", dict: "object", list: "array",
}


def schema_from_signature(func) -> dict:
    """
    Build a JSON Schema "object" definition from a function's signature,
    using its type hints for property types and the presence/absence of a
    default value to determine which parameters are required. `self` is
    skipped. Unannotated parameters default to "string".
    """
    sig = inspect.signature(func)
    props, required = {}, []
    
    for pname, param in sig.parameters.items():
        if pname == "self":
            continue
        
        ann = param.annotation if param.annotation is not inspect.Parameter.empty else str
        props[pname] = {"type": PY_TO_JSON_TYPE.get(ann, "string")}
        
        if param.default is inspect.Parameter.empty:
            required.append(pname)
    
    # Return schema.
    return {"type": "object", "properties": props, "required": required}


def get_summary_from_docstring(func) -> str:
    """
    Extract a short description from a function's docstring.

    The function uses the docstring summary section, stopping before common
    Google-style docstring sections such as Args, Returns, Raises, Examples,
    and Notes.

    Args:
        func:
            Function whose docstring should be inspected.

    Returns:
        A cleaned description string, or an empty string when no docstring
        exists.
    """
    doc = inspect.getdoc(func)

    # No documentation available.
    if not doc:
        return ""

    lines = []

    # Sections that should not be included in the description.
    stop_sections = {
        "Args:",
        "Arguments:",
        "Parameters:",
        "Returns:",
        "Yields:",
        "Raises:",
        "Examples:",
        "Example:",
        "Notes:",
        "Attributes:",
        "Warnings:",
    }

    for line in doc.splitlines():
        stripped = line.strip()

        # Stop at the first structured section.
        if stripped in stop_sections:
            break

        # Keep non-empty summary lines.
        if stripped:
            lines.append(stripped)

    return "\n".join(lines)
    

def resolve_description(func, description: str = "") -> str:
    """
    Resolve MCP metadata description.

    Explicit decorator descriptions take priority. If no description is
    provided, the function docstring summary is used.

    Args:
        func:
            Function being decorated.

        description:
            Explicit MCP description.

    Returns:
        Resolved description string.
    """
    return description or get_summary_from_docstring(func)
    

def tool(description: str = "", name: str = None, scopes: list = None):
    """
    Mark a method as an MCP tool. The method's signature is introspected to
    build its JSON Schema `inputSchema`, and it becomes callable via the
    `tools/call` RPC method using the given (or inferred) name.

    `scopes`, if given, are required scopes checked against
    `self.granted_scopes` (set in `authenticate()`) before the tool runs.
    """
    def deco(func):
        if not inspect.iscoroutinefunction(func):
            raise TypeError(f"@tool methods must be async: {func.__name__}")
        
        # Set some data on func
        func.mcp_kind = "tool"
        func.mcp_name = name or func.__name__
        func.mcp_description = resolve_description(func, description)
        func.mcp_schema = schema_from_signature(func)
        func.mcp_scopes = scopes or []
        
        # Return the func
        return func
    
    # Return the decorator.
    return deco


def resource(
    uri: str,
    name: str,
    description: str = "",
    mime_type: str = "text/plain",
    scopes: list = None,
):
    """
    Mark a method as an MCP resource, addressable at `uri` and readable via
    the `resources/read` RPC method.

    The method should take no arguments (beyond `self`) and return the
    resource's content.

    Args:
        uri:
            Unique URI identifying the resource.

        name:
            Human-readable resource name displayed by MCP clients.

        description:
            Optional description of the resource.

        mime_type:
            MIME type of the returned resource content.

        scopes:
            Optional authorization scopes required to read the resource.
            Checked against `self.granted_scopes` (set in `authenticate()`).

    Raises:
        TypeError:
            If the decorated method is not asynchronous.
    """
    def deco(func):
        if not inspect.iscoroutinefunction(func):
            raise TypeError(f"@resource methods must be async: {func.__name__}")

        # Set MCP metadata on function.
        func.mcp_kind = "resource"
        func.mcp_uri = uri
        func.mcp_name = name
        func.mcp_description = resolve_description(func, description)
        func.mcp_mime_type = mime_type
        func.mcp_scopes = scopes or []
        
        # Return the func
        return func

    # Return the decorator.
    return deco


def resource_template(
    uri_template: str,
    name: str,
    description: str = "",
    mime_type: str = "text/plain",
    scopes: list = None,
):
    """
    Mark a method as an MCP resource template.

    Resource templates describe dynamic resources that can be resolved from
    URI templates. The method should accept the extracted URI template
    arguments and return the resource content.

    Args:
        uri_template:
            URI template used to match dynamic resources.

        name:
            Human-readable resource template name.

        description:
            Optional description of the resource template.

        mime_type:
            MIME type of the returned resource content.

        scopes:
            Optional authorization scopes required to access the resource.

    Raises:
        TypeError:
            If the decorated method is not asynchronous.
    """
    def deco(func):
        if not inspect.iscoroutinefunction(func):
            raise TypeError(
                f"@resource_template methods must be async: {func.__name__}"
            )

        # Set MCP metadata on function.
        func.mcp_kind = "resource_template"
        func.mcp_uri_template = uri_template
        func.mcp_name = name
        func.mcp_description = resolve_description(func, description)
        func.mcp_mime_type = mime_type
        func.mcp_scopes = scopes or []
        
        # Return the func
        return func

    # Return the decorator.
    return deco
    

def prompt(description: str = "", name: str = None, scopes: list = None):
    """
    Mark a method as an MCP prompt template, listed via `prompts/list` and
    rendered via `prompts/get` using the given (or inferred) name. The
    method's signature is introspected the same way as for tools.

    `scopes`, if given, are required scopes checked against
    `self.granted_scopes` (set in `authenticate()`) before it's rendered.
    """
    def deco(func):
        if not inspect.iscoroutinefunction(func):
            raise TypeError(f"@prompt methods must be async: {func.__name__}")
        
        # Set some data on func
        func.mcp_kind = "prompt"
        func.mcp_name = name or func.__name__
        func.mcp_description = resolve_description(func, description)
        func.mcp_schema = schema_from_signature(func)
        func.mcp_scopes = scopes or []
        
        # Return func
        return func
    
    # Return decorator
    return deco
