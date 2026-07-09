"""
Module containing codes for the Model Context Protocol.
"""
from enum import IntEnum


class MCPErrorCode(IntEnum):
    """
    JSON-RPC 2.0 error codes used by this server. The standard codes
    (PARSE_ERROR, INVALID_REQUEST, METHOD_NOT_FOUND, INTERNAL_ERROR) are
    fixed by the JSON-RPC 2.0 spec. The remaining codes fall in the
    -32000 to -32099 range the spec reserves for implementation-defined
    server errors.
    """
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INTERNAL_ERROR = -32603
    UNAUTHORIZED = -32001
    NOT_AUTHORIZED = -32002
    ORIGIN_NOT_ALLOWED = -32003
