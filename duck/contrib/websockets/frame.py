"""
WebSocket frame module.

Implements WebSocket frame parsing and serialization per RFC 6455.
"""

import io
import os
import struct

from typing import Optional, Sequence, Callable

from duck.contrib.websockets.exceptions import ProtocolError, PayloadTooBig
from duck.contrib.websockets.opcodes import OpCode, CONTROL_OPCODES
from duck.contrib.websockets.extensions import Extension


def apply_mask(data: bytes, mask: bytes) -> bytes:
    """
    Applies a 4-byte WebSocket mask to the given data.
    """
    return bytes(b ^ mask[i % 4] for i, b in enumerate(data))


class Frame:
    """
    Represents a WebSocket frame according to RFC 6455.
    """

    __slots__ = ("opcode", "fin", "payload", "rsv1", "rsv2", "rsv3")

    def __init__(
        self,
        opcode: int,
        fin: Optional[bool] = True,
        payload: bytes = b"",
        rsv1: bool = False,
        rsv2: bool = False,
        rsv3: bool = False,
    ):
        assert opcode is not None, "Opcode should not be None"
        assert isinstance(payload, bytes), f"Payload should be bytes, not {type(payload)}"

        self.opcode = opcode
        self.fin = fin
        self.payload = payload
        self.rsv1 = rsv1
        self.rsv2 = rsv2
        self.rsv3 = rsv3

    def __repr__(self):
        return f"<[{self.__class__.__name__} opcode={self.opcode}, fin={self.fin}]>"

    def check(self) -> None:
        """
        Check that reserved bits and opcode have acceptable values.

        Raises:
            ProtocolError: If RSV bits are non-zero or control frame rules are violated.
        """
        if self.rsv1 or self.rsv2 or self.rsv3:
            if self.rsv1 and not self.rsv1 and not self.rsv3:
                raise ProtocolError(
                    "Reserved bit 1 (rsv1) must be zero. "
                    "This must have already been resetted by permessage-deflate extension in either `serialize` or `parse`. "
                )
            raise ProtocolError("Reserved bits must be 0")

        if self.opcode in CONTROL_OPCODES:
            if len(self.payload) > 125:
                raise ProtocolError("Control frame too long (greater than 125 bytes)")
            if not self.fin:
                raise ProtocolError("Control frames must not be fragmented")

    @classmethod
    async def parse(
        cls,
        read_exact: Callable[[int], bytes],
        mask_required: bool = True,
        max_size: Optional[int] = None,
        extensions: Optional[Sequence[Extension]] = None,
    ) -> "Frame":
        """
        Parses a WebSocket frame from the connection.

        Args:
            read_exact (Callable): Coroutine to read an exact number of bytes.
            mask_required (bool): Whether to expect and validate masking (clients only).
            max_size (int): Optional maximum size of frame payload.
            extensions (Optional[Sequence[Extension]]): Extensions to apply for decoding.

        Returns:
            Frame: Parsed and decoded WebSocket frame.

        Raises:
            ProtocolError: If the frame format is invalid.
            PayloadTooBig: If the payload exceeds max_size.
        """
        data = await read_exact(2)
        
        if len(data) < 2:
            raise ProtocolError("Expected 2 bytes for frame header, got fewer")
            
        head1, head2 = struct.unpack("!BB", data)

        fin = bool(head1 & 0b10000000)
        rsv1 = bool(head1 & 0b01000000)
        rsv2 = bool(head1 & 0b00100000)
        rsv3 = bool(head1 & 0b00010000)

        try:
            opcode = OpCode(head1 & 0b00001111)
        except ValueError as exc:
            raise ProtocolError("Invalid opcode received") from exc

        mask = bool(head2 & 0b10000000)
        length = head2 & 0b01111111

        if mask_required and not mask:
            raise ProtocolError("Masking required but not received")

        if length == 126:
            data = await read_exact(2)
            (length,) = struct.unpack("!H", data)
        
        elif length == 127:
            data = await read_exact(8)
            (length,) = struct.unpack("!Q", data)

        if max_size is not None and length > max_size:
            raise PayloadTooBig(f"Payload of {length} exceeds limit of {max_size} bytes")

        mask_bytes = await read_exact(4) if mask else b""
        payload = await read_exact(length)

        if mask:
            payload = apply_mask(payload, mask_bytes)

        frame = cls(
            opcode=opcode,
            fin=fin,
            payload=payload,
            rsv1=rsv1,
            rsv2=rsv2,
            rsv3=rsv3,
        )

        if extensions:
            for ext in reversed(extensions):
                frame = ext.decode(frame)

        frame.check()
        return frame

    def serialize(
        self,
        mask: bool = False,
        extensions: Optional[Sequence[Extension]] = None,
    ) -> bytes:
        """
        Serializes the frame into raw bytes ready to send.

        Args:
            mask (bool): Whether to apply masking (typically True for clients).
            extensions (Optional[Sequence[Extension]]): Extensions to apply on the fly.

        Returns:
            bytes: The serialized WebSocket frame.
        """
        self.check()

        if extensions:
            for ext in extensions:
                self = ext.encode(self)

        output = io.BytesIO()

        head1 = (
            (0b10000000 if self.fin else 0)
            | (0b01000000 if self.rsv1 else 0)
            | (0b00100000 if self.rsv2 else 0)
            | (0b00010000 if self.rsv3 else 0)
            | self.opcode
        )

        payload = self.payload
        length = len(payload)

        if length < 126:
            head2 = length
            output.write(struct.pack("!BB", head1, head2 | (0b10000000 if mask else 0)))
        
        elif length < 65536:
            output.write(struct.pack("!BBH", head1, 126 | (0b10000000 if mask else 0), length))
        
        else:
            output.write(struct.pack("!BBQ", head1, 127 | (0b10000000 if mask else 0), length))

        if mask:
            mask_bytes = os.urandom(4)
            output.write(mask_bytes)
            payload = apply_mask(payload, mask_bytes)

        output.write(payload)
        return output.getvalue()
