"""
WebSocket Extensions module.

Provides base and concrete implementations for WebSocket frame extensions,
including permessage-deflate compression as defined in RFC 7692.
"""

import zlib

from duck.contrib.websockets.opcodes import OpCode, CONTROL_OPCODES
from duck.contrib.websockets.exceptions import ExtensionError


class Extension:
    """
    Base class for WebSocket extensions.

    Extensions allow for modification of WebSocket frames during encoding
    (sending) or decoding (receiving), such as compression or encryption.
    """

    def __init__(self, name: str):
        """
        Initialize the extension with a valid name.

        Args:
            name (str): The name of the extension as it should appear in
                        the Sec-WebSocket-Extensions header.

        Raises:
            ValueError: If the name is not a non-empty string.
        """
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Extension name must be a non-empty string.")
        self.name = name.strip()
        
    def check_frame(self, frame):
        """
        Validates that the given object is a Frame instance.

        Args:
            frame: The frame object to validate.

        Raises:
            ExtensionError: If the object is not an instance of Frame.
        """
        from duck.contrib.websockets.frame import Frame

        if not isinstance(frame, Frame):
            raise ExtensionError(
                f"The frame should be an instance of Frame, not {type(frame)}."
            )

    def encode(self, frame) -> "Frame":
        """
        Applies the extension to encode (transform) an outgoing frame.

        Args:
            frame: The frame to encode.

        Raises:
            NotImplementedError: If not implemented by a subclass.
        
        Returns:
            Frame: The encoded frame, typically the same frame but encoded.
        """
        raise NotImplementedError("Implement this method to be able to encode frames.")

    def decode(self, frame) -> "Frame":
        """
        Applies the extension to decode (transform) an incoming frame.

        Args:
            frame: The frame to decode.

        Raises:
            NotImplementedError: If not implemented by a subclass.
        
        Returns:
            Frame: The decoded frame, typically the same frame but decoded.
        """
        raise NotImplementedError("Implement this method to be able to decode frames.")


class PerMessageDeflate(Extension):
    """
    Per-message Deflate Extension (RFC 7692).

    Provides compression for non-control WebSocket frames using DEFLATE.
    Supports options for context takeover and window size.

    Args:
        client_no_context_takeover (bool): Whether to disable decompression context reuse.
        server_no_context_takeover (bool): Whether to disable compression context reuse.
        client_max_window_bits (int): Maximum window bits for client decompression (8-15).
                                       Defaults to 15, which means 32K LZ77 history buffer.
    """

    def __init__(
        self,
        name: str,
        client_no_context_takeover: bool = False,
        server_no_context_takeover: bool = False,
        client_max_window_bits: int = 15
    ):
        super().__init__(name)
        
        if not (8 <= client_max_window_bits <= 15):
            raise ValueError("client_max_window_bits must be between 8 and 15.")
        
        self.client_no_context_takeover = client_no_context_takeover
        self.server_no_context_takeover = server_no_context_takeover
        self.client_max_window_bits = client_max_window_bits

        # Create initial compression/decompression contexts with raw DEFLATE.
        self._compressor = zlib.compressobj(wbits=-zlib.MAX_WBITS)
        self._decompressor = zlib.decompressobj(wbits=-client_max_window_bits)

    def encode(self, frame) -> "Frame":
        """
        Compresses the payload of the given frame using DEFLATE.

        Skips control frames. Appends Z_SYNC_FLUSH marker and strips final 4-byte tail
        as required by RFC 7692. Sets RSV1 on first frame of a message.

        Args:
            frame: A Frame instance to encode.

        Raises:
            ExtensionError: If the input is not a valid Frame.
        
        Returns:
            Frame: The encoded frame, typically the same frame but encoded.
        """
        self.check_frame(frame)

        if frame.opcode not in CONTROL_OPCODES:
            # Compress the payload using raw DEFLATE with Z_SYNC_FLUSH.
            compressed = self._compressor.compress(frame.payload)
            compressed += self._compressor.flush(zlib.Z_SYNC_FLUSH)

            # Remove the last 4 bytes (empty DEFLATE block, 0x00 0x00 0xff 0xff)
            frame.payload = compressed[:-4]

            # Set RSV1 on the first frame in a fragmented message
            if frame.opcode != OpCode.CONTINUATION:
                frame.rsv1 = True

            if self.server_no_context_takeover:
                # Reset compressor state for each message if takeover is disabled.
                self._compressor = zlib.compressobj(wbits=-zlib.MAX_WBITS)
        
        # Return the encoded frame (if applicable).
        return frame
        
    def decode(self, frame) -> "Frame":
        """
        Decompresses the payload of the given frame using DEFLATE.

        Skips control frames. Appends the 4-byte tail removed during encoding.
        Unsets RSV1 after decoding.

        Args:
            frame: A Frame instance to decode.

        Raises:
            ExtensionError: If the input is not a valid Frame.
        
        Returns:
            Frame: The decoded frame, typically the same frame but decoded.
        """
        self.check_frame(frame)

        if frame.opcode not in CONTROL_OPCODES:
            # Append DEFLATE tail to allow proper decompression.
            frame.payload += b"\x00\x00\xff\xff"

            # Decompress payload
            frame.payload = self._decompressor.decompress(frame.payload)

            # Clear RSV1 to avoid protocol errors during frame validation
            if frame.opcode != OpCode.CONTINUATION:
                frame.rsv1 = False

            if self.client_no_context_takeover:
                # Reset decompressor state after each message if takeover is disabled.
                self._decompressor = zlib.decompressobj(wbits=-self.client_max_window_bits)
        
        # Return the decoded frame (if applicable)
        return frame
                    
    def __repr__(self):
        """
        Returns a debug-friendly string representation of the extension.
        """
        return (
            f"<PerMessageDeflate "
            f"client_no_context_takeover={self.client_no_context_takeover}, "
            f"server_no_context_takeover={self.server_no_context_takeover}, "
            f"client_max_window_bits={self.client_max_window_bits}>"
        )
