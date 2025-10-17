"""
WebSocket Opcodes.
"""
import enum


class OpCode(enum.IntEnum):
    """
    Static class for storing WebSocket opcodes.
    """
    CONTINUATION = 0x0
    TEXT = 0x1
    BINARY = 0x2
    PING = 0x9
    PONG = 0xA
    CLOSE = 0x8


class CloseCode(enum.IntEnum):
    """
    Close code values for WebSocket close frames.
    """
    NORMAL_CLOSURE = 1000
    GOING_AWAY = 1001
    PROTOCOL_ERROR = 1002
    UNSUPPORTED_DATA = 1003
    # 1004 is reserved
    NO_STATUS_RCVD = 1005
    ABNORMAL_CLOSURE = 1006
    INVALID_DATA = 1007
    POLICY_VIOLATION = 1008
    MESSAGE_TOO_BIG = 1009
    MANDATORY_EXTENSION = 1010
    INTERNAL_ERROR = 1011
    SERVICE_RESTART = 1012
    TRY_AGAIN_LATER = 1013
    BAD_GATEWAY = 1014
    TLS_HANDSHAKE = 1015


# Set control opcodes.
CONTROL_OPCODES = (
    OpCode.PING,
    OpCode.PONG,
    OpCode.CLOSE,
)

# Set data opcodes
DATA_OPCODES = (
    OpCode.CONTINUATION,
    OpCode.TEXT,
    OpCode.BINARY,
)
