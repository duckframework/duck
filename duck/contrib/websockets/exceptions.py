"""
WebSocket exceptions module.
"""

class BaseException(Exception):
    """
    Base exception for the websocket-related errors.
    """


class ExtensionError(BaseException):
    """
    Raised on extension errors.
    """


class ProtocolError(BaseException):
    """
    Raised on Protocol-based errors.
    """


class PayloadTooBig(ProtocolError):
    """
    Raised when payload is too big.
    """
