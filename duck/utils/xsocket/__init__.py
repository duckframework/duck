"""
Custom Duck socket implementations.
"""
import ssl
import time
import socket
import select
import asyncio

from typing import (
  Any,
  Optional,
  Union,
  Tuple,
)

from duck.contrib.sync import iscoroutinefunction
from duck.settings import SETTINGS
from duck.exceptions.all import AsyncViolationError


DEFAULT_BUFSIZE = SETTINGS["SERVER_BUFFER"] or 1024


def create_xsocket(
    family: int = socket.AF_INET,
    type: int = socket.SOCK_STREAM,
    **kwargs,
) -> "xsocket":
    """
    Create an `xsocket` object from provided arguments.
    
    Args:
        family (int): The socket family. Defaults to socket.AF_INET.
        type (int): Type of socket. Defaults to socket.SOCK_STREAM. 
    """
    sock = socket.socket(family=family, type=type, **kwargs)
    return xsocket(sock)


def ssl_wrap_socket(
    socket_obj: socket.socket,
    keyfile: str = None,
    certfile: str = None,
    version: int = ssl.PROTOCOL_TLS_SERVER,
    server_side: bool = True,
    ca_certs=None,
    ciphers=None,
    alpn_protocols: list[str] = None,
) -> "ssl_xsocket":
    """
    Return an SSL xsocket with the same arguments as `ssl.wrap_socket`.

    Args:
        socket_obj (socket.socket): The underlying socket object to secure.
        keyfile (str, optional): Path to the server's private key file (PEM format).
        certfile (str, optional): Path to the server's certificate file (PEM format).
        version (int): SSL Protocol version.
        server_side (bool): Whether the socket is for the server side.
        ca_certs (str, optional): Path to trusted CA certificates.
        ciphers (str, optional): Cipher suites string.
        alpn_protocols (list, optional): ALPN protocols (e.g., ["h2", "http/1.1"]).

    Returns:
        socket.socket: The secure SSL socket.
    """
    context = ssl.SSLContext(version)

    # Load cert and key
    if certfile and keyfile:
        context.load_cert_chain(certfile=certfile, keyfile=keyfile)

    # Set ciphers if provided
    if ciphers:
        context.set_ciphers(ciphers)

    # Load CA certs if provided
    if ca_certs:
        context.load_verify_locations(cafile=ca_certs)

    # Configure for HTTP/2 if needed
    if alpn_protocols and "h2" in alpn_protocols:
        # Use minimum_version instead of setting context.options
        if hasattr(context, "minimum_version"):
            context.minimum_version = ssl.TLSVersion.TLSv1_2
        else:
            context.options |= (
                ssl.OP_NO_SSLv2 | ssl.OP_NO_SSLv3 |
                ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1
            )
        if hasattr(context, "options") and hasattr(ssl, "OP_NO_COMPRESSION"):
            context.options |= ssl.OP_NO_COMPRESSION

        try:
            context.set_ciphers("ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20")
        except ssl.SSLError:
            pass  # fallback to default if not supported

    # ALPN support
    if alpn_protocols:
        context.set_alpn_protocols(alpn_protocols)
    
    # Return the final socket.
    return ssl_xsocket(socket_obj, context, server_side)


class xsocketError(Exception):
    """
    Raised on `xsocket` related errors.
    """

    
class xsocket:
    """
    Wrapper for raw sockets providing async support and
    transparent delegation of socket methods/attributes.
    """

    def __init__(self, raw_socket: Union[socket.socket, "xsocket"]):
        
        if isinstance(raw_socket, xsocket):
            raw_socket = raw_socket.raw_socket
            
        elif not isinstance(raw_socket, socket.socket):
            raise xsocketError(f"Raw socket should be an instance of socket.socket or xsocket not {type(raw_socket)}")
        
        elif isinstance(raw_socket, ssl.SSLSocket):
            raise xsocketError("Only raw socket is allowed not SSLSocket.")
            
        self.raw_socket = raw_socket
        
        # Attributes/methods we want to avoid being used on the raw_socket through this instance
        # but we haven't implemented them yet.
        self._unimplemented_attrs = set({
            "sendall", # The default send uses sendall by default.
            "recvfrom", # Not implemented.
            "recv_into",
        })
        
        # Attributes/methods that belong explicitly within this class,
        # will not be resolved on raw_sovket.
        self._cls_attrs = {
            "loop",
            "raise_if_blocking",
            "raise_if_in_async_context",
            "raw_socket",
            "_unimplemented_attrs",
            "_cls_attrs",
            "connect",
            "close",
            "send",
            "recv",
            "async_connect",
            "async_send",
            "async_recv",
            "__repr__",
            "__str__",
            "__getattribute__",
            "__class__",
            "__dir__",
            "__dict__",
        }
        
        # Update left out class attrs
        for i in dir(self):
            if i not in self._cls_attrs:
                self._cls_attrs.add(i)

    @property
    def loop(self) -> asyncio.AbstractEventLoop:
        """
        Returns the currently running event loop.
        """
        return asyncio.get_event_loop()
        
    def raise_if_blocking(self):
        """
        Checks whether socket is in or not in blocking mode, useful in async.
        
        Raises:
            AsyncViolationError: If socket is in blocking mode.
        """
        blocking = self.raw_socket.getblocking()
        
        if blocking:
            raise AsyncViolationError("Socket is in blocking mode.")
        
    def raise_if_in_async_context(self, message: str):
        """
        Checks whether we are not in async context else an error is raised.
        
        Args:
            message (str): Error message to display if in async context.
            
        Raises:
            AsyncViolationError: If we are in async context. Useful in cases a user is trying to use blocking
                methods like `send`, `recv` instead of `async_send` & `async_recv`.
        """
        loop = None
        
        try:
            loop = self.loop # fetch the current event loop.    
        except Exception:
            pass
        finally:
            if loop:
                raise AsyncViolationError(message) # we are in async context.
                
    def connect(self, target = Tuple[str, int], timeout: float = None) -> None:
        """
        Connect socket to a target.
        """
        self.raise_if_in_async_context("This method is synchronous yet you are in async context, consider using `async_connect` instead.")
        
        sock = self.raw_socket
        
        original_timeout = sock.gettimeout()
        sock.settimeout(timeout)
        
        try:
            sock.connect(target)
        except socket.timeout:
            raise TimeoutError(f"Connect operation timed out after {timeout} seconds")
        finally:
            sock.settimeout(original_timeout)
        
    def close(self, shutdown: bool = True, shutdown_reason: int = socket.SHUT_RDWR):
        """
        Closes the underlying socket.
        
        Args:
            sock (xsocket): The underlying xsocket object.
            shutdown (bool): Whether to shutdown the socket using `sock.shutdown`.
            shutdown_reason (int): Reason for shutdown.
        """
        try:
            if shutdown:
                self.shutdown(socket.SHUT_RDWR)
        except Exception:
            # Ignore every exception
            pass
        
        # Now proceed to closing socket.
        try:
            self.raw_socket.close()
        except Exception:
            # Ignore every exception
            pass
            
    def send(self, data: bytes, timeout: float = None) -> int:
        """
        Custom `send` method with optional timeout. This defaults to using `sendall`.
    
        Args:
            data (bytes): Data to send.
            timeout (float, optional): Timeout in seconds. If None, blocking behavior depends on socket settings.
    
        Returns:
            int: Number of bytes sent.
    
        Raises:
            TimeoutError: If the send operation times out.
            OSError: For other socket errors.
        """
        self.raise_if_in_async_context("This method must not be used in an async context, use `async_send` instead.")
        
        sock = self.raw_socket
        
        original_timeout = sock.gettimeout()
        sock.settimeout(timeout)
        
        try:
            sent = sock.sendall(data)
            return len(data) if sent is None else None
        except socket.timeout:
            raise TimeoutError(f"Send operation timed out after {timeout} seconds")
        finally:
            sock.settimeout(original_timeout)
            
    def recv(self, n: int = DEFAULT_BUFSIZE, timeout: float = None):
        """
        Custom `recv` method using `recv_into` with a reusable buffer and optional timeout.
    
        Args:
            n (int): Number of bytes to read.
            timeout (float, optional): Timeout in seconds. If None, blocking behavior depends on socket settings.
    
        Returns:
            bytes: Data received.
    
        Raises:
            TimeoutError: If no data is received within the specified timeout.
        """
        self.raise_if_in_async_context("This method must not be used in an async context, use `async_recv` instead.")
        
        sock = self.raw_socket
        buf = bytearray(n)
        mv = memoryview(buf)
        
        # Save original timeout to restore later
        original_timeout = sock.gettimeout()
        sock.settimeout(timeout)
        
        try:
            count = sock.recv_into(mv, 0)
            if count == 0:
                # Connection closed gracefully
                return b""
            return bytes(buf[:count])
        except socket.timeout:
            raise TimeoutError(f"No data received within {timeout} seconds")
        finally:
            sock.settimeout(original_timeout)
    
    async def async_accept(self, timeout: float = None) -> None:
        """
        Accept client connection.
        """
        self.raise_if_blocking()
        await asyncio.wait_for(self.loop.sock_accept(self.raw_socket, target), timeout=timeout)
        
    async def async_connect(self, target = Tuple[str, int], timeout: float = None) -> None:
        """
        Connect socket to a target.
        """
        self.raise_if_blocking()
        await asyncio.wait_for(self.loop.sock_connect(self.raw_socket, target), timeout=timeout)
        
    async def async_send(self, data: bytes, timeout: Optional[float] = None) -> int:
        """
        Asynchronously sends data through the socket with optional timeout.

        Args:
            data (bytes): The data to send.
            timeout (float, optional): Max seconds to wait before timing out.

        Returns:
            int: Number of bytes sent.

        Raises:
            xsocketError: If socket in blocking mode, this may block the event loop.
            TimeoutError: If sending takes too long.
            OSError: If a socket error occurs.
        """
        self.raise_if_blocking() # Raise error if socket is in blocking mode.
        try:
            none = await asyncio.wait_for(self.loop.sock_sendall(self.raw_socket, data), timeout)
            return len(data) if none is None else None
        except asyncio.TimeoutError:
            raise TimeoutError(f"Send timed out after {timeout} seconds")

    async def async_recv(self, n: int = DEFAULT_BUFSIZE, timeout: Optional[float] = None) -> bytes:
        """
        Asynchronously receives data from the socket with optional timeout.

        Args:
            n (int): Maximum number of bytes to read.
            timeout (float, optional): Max seconds to wait before timing out.

        Returns:
            bytes: The received data.

        Raises:
            xsocketError: If socket in blocking mode, this may block the event loop.
            TimeoutError: If receiving takes too long.
            OSError: If a socket error occurs.
        """
        self.raise_if_blocking() # Raise error if socket is in blocking mode.
        try:
            return await asyncio.wait_for(self.loop.sock_recv(self.raw_socket, n), timeout)
        except asyncio.TimeoutError:
            raise TimeoutError(f"Receive timed out after {timeout} seconds")
            
    def __setattr__(self, key: str, value: Any) -> None:
        """
        Custom setattr to track attributes defined on this wrapper.
        """
        # Using _cls_attrs set to avoid adding duplicate keys
        if not hasattr(self, "_cls_attrs"):
            super().__setattr__(key, value)
            return
        
        # Super setattribute
        super().__setattr__(key, value)
        
        if key not in self._cls_attrs:
            self._cls_attrs.add(key)

    def __getattribute__(self, attr: str) -> Any:
        """
        Returns attributes from the wrapper if present,
        else falls back to the wrapped raw_socket attributes.
        
        Raises AttributeError if not found.
        """
        _cls_attrs = super().__getattribute__("_cls_attrs")
        _unimplemented_attrs = super().__getattribute__("_unimplemented_attrs")
        
        if attr in _cls_attrs:
            return super().__getattribute__(attr)
        
        if attr in _unimplemented_attrs:
            raise xsocketError(
                f"Attribute `{attr}` is not implemented. "
                f"Consider using the available methods, which may offer equivalent functionality."
            )
        
        raw_socket = super().__getattribute__("raw_socket")
        
        try:
            return getattr(raw_socket, attr)
        except AttributeError as e:
            raise AttributeError(f"Attribute '{attr}' not found on xsocket or underlying raw socket.") from e

    def __repr__(self):
        return (
            f"<{self.__class__.__name__} fd={self.fileno()}, "
            f"family={self.family}, type={self.type}, proto={self.proto}, "
            f"laddr={self.getsockname()}>"
        )


class ssl_xsocket(xsocket):
    """
    SSL Wrapper for raw sockets providing async support and
    transparent delegation of socket methods/attributes.
    """

    def __init__(
        self,
        raw_socket: socket.socket,
        ssl_context: ssl.SSLContext,
        server_side: bool = True,
    ):
        super().__init__(raw_socket)
        self._handshake_done = False
        self.server_side = server_side
        self.ssl_inbio = ssl.MemoryBIO() # write to this
        self.ssl_outbio = ssl.MemoryBIO() # read from this
            
        self.ssl_obj = ssl_context.wrap_bio(
            self.ssl_inbio,
            self.ssl_outbio,
            server_side=server_side,
        )
          
        # Record some attributes, they belong to this class explicitly rather than raw_socket.
        self._cls_attrs.update({
            "_handshake_done",
            "_set_ssl_attributes",
            "server_side",
            "ssl_obj",
            "ssl_inbio",
            "ssl_outbio",
            "data_to_send",
            "send_pending_data",
            "recv_pending_data",
            "do_handshake",
            # async implementations
            "async_send_pending_data",
            "async_recv_pending_data",
            "async_do_handshake",
        })
              
        # Set SSL attributes that might belong to the ssl object
        self._set_ssl_attributes()
        
        # Update left out class attrs
        for i in dir(self):
            if i not in self._cls_attrs:
                self._cls_attrs.add(i)
                
    def _set_ssl_attributes(self):
        """
        Dynamically exposes non-callable public attributes from `self.ssl_obj` onto `self`.
        Creates properties with both getter and setter to reflect changes in real-time.
        """
        self_attrs = dir(self)
        
        # Dynamic getter and setter for the property ---
        def make_property(attr_name):
            def getter(instance):
                return getattr(instance.ssl_obj, attr_name)
                 
            def setter(instance, val):
                setattr(instance.ssl_obj, attr_name, val)
                    
            return property(getter, setter)
                
        for attr in dir(self.ssl_obj):
            if attr.startswith('_') or attr in self_attrs:
                continue  # Skip private or already existing attributes
    
            value = getattr(self.ssl_obj, attr)
            
            # Create live attributes which fetches live results.
            if callable(value):
                setattr(self, attr, value)
            else:
                # Set the property on the class, not the instance
                value = make_property(attr)
                setattr(type(self), attr, value)
            
    def close(self, shutdown: bool = True, shutdown_reason: int = socket.SHUT_RDWR):
        # Calling ssl_obj.unwrap is causing segmentation errors sometimes
        # so lets just ignore the ssl_obj.unwrap call.
        self.ssl_obj = None
        self.ssl_inbio = None
        self.ssl_outbio = None
        super().close(shutdown, shutdown_reason)
    
    def handle_sock_close(func):
        """
        Decorator to handle socket close by raising ConnectionError if `ssl_obj` is set to None.
        
        Notes:
        - The `ssl_obj` is set to None if `close` is called so this prevents operations on NoneType,
               by raising ConnectionError.
        """
        def wrapper(self, *args, **kwargs):
            if self.ssl_obj is None:
                raise ConnectionError("The `ssl_obj` is set to None. This means, `close` has already been called.")
            return func(self, *args, **kwargs)
        
        async def async_wrapper(self, *args, **kwargs):
            if self.ssl_obj is None:
                raise ConnectionError("The `ssl_obj` is set to None. This means, `close` has already been called.")
            return await func(self, *args, **kwargs)
        
        if iscoroutinefunction(func):
            return async_wrapper
        return wrapper
        
    @handle_sock_close
    def data_to_send(self) -> bytes:
        """
        Return all currently buffered encrypted bytes from the outbio.
        """
        # MemoryBIO.read() consumes and returns available data
        return self.ssl_outbio.read()
    
    @handle_sock_close
    def send_pending_data(self, timeout: Optional[float] = None) -> int:
        """
        Blocking send to flush outbio. Will loop until outbio is drained or socket stops accepting.
        Returns total bytes written to the transport socket (not the application bytes).
        """
        self.raise_if_in_async_context("This method is blocking, use `async_send_pending_data` instead.")
        total = 0
        while True:
            data = self.ssl_outbio.read()
            if not data:
                break
            sent = super().send(data, timeout=timeout) or 0
            if sent == 0:
                # transport closed or would block: re-write the unsent bytes back to outbio
                # MemoryBIO does not support push-back; simplest approach: if partial send, push rest back by
                # writing it back into ssl_outbio (be careful: ssl_outbio.write expects bytes to be read later).
                # But super().send should ideally be blocking and send all (document assumption).
                raise ConnectionError("Transport unable to send pending encrypted data")
            total += sent
            # loop until outbio drained
        return total
    
    @handle_sock_close
    def recv_more_encrypted_data(self, n: int = DEFAULT_BUFSIZE, timeout: Optional[float] = None) -> int:
        """
        Read encrypted bytes from the transport and feed them into ssl_inbio.
        Returns number of bytes written into ssl_inbio.
        Raises ConnectionResetError on EOF.
        """
        self.raise_if_in_async_context("This method is blocking, use `async_recv_pending_data` instead.")
        data = super().recv(n, timeout)
        if not data:
            # peer closed connection — signal EOF
            # MemoryBIO has no explicit write_eof; writing empty bytes won't help.
            # Best to raise so the caller can handle.
            raise ConnectionResetError("Underlying transport closed (EOF) while expecting encrypted data")
        self.ssl_inbio.write(data)
        return len(data)
    
    @handle_sock_close
    def do_handshake(self, timeout: Optional[float] = None):
        """
        Blocking handshake loop with flush/recv handling and EOF detection.
        """
        self.raise_if_in_async_context("This method is blocking, use `async_do_handshake` instead.")
        
        while not self._handshake_done:
            try:
                self.ssl_obj.do_handshake()
                
                # Flush any data remaining in outbio
                self.send_pending_data(timeout=timeout)
                self._handshake_done = True
                return
                
            except ssl.SSLWantReadError:
                # Flush any sendable data, then attempt to read more encrypted bytes
                self.send_pending_data(timeout=timeout)
                
                # if recv returns EOF -> will raise ConnectionResetError
                self.recv_more_encrypted_data(timeout=timeout)
            
            except ssl.SSLWantWriteError:
                # We need to flush outbio — then retry
                self.send_pending_data(timeout=timeout)
    
    @handle_sock_close
    def send(self, data: bytes, timeout: float = None) -> int:
        """
        Encrypts and sends application data over the network.
        
        Returns:
            int: Total bytes sent.
        """
        self.raise_if_in_async_context("This method is blocking, use `async_send` instead.")
        
        total_written = 0
        view = memoryview(data)
        
        while total_written < len(data):
            try:
                written = self.ssl_obj.write(view[total_written:])
                
                # Written is number of application bytes accepted by SSLObject
                total_written += written
                
                # Flush out any encrypted output produced
                self.send_pending_data(timeout=timeout)
            
            except ssl.SSLWantWriteError:
                # Need to flush outbio and retry
                self.send_pending_data(timeout=timeout)
            
            except ssl.SSLWantReadError:
                # SSL needs more encrypted input (e.g. renegotiation)
                # read and feed more encrypted data
                self.recv_more_encrypted_data(timeout=timeout)
        
        # Final flush attempt to ensure no bytes stuck in outbio
        self.send_pending_data(timeout=timeout)
        return total_written
    
    @handle_sock_close
    def recv(self, n: int = DEFAULT_BUFSIZE, timeout: float = None) -> bytes:
        """
        Receives encrypted data from the socket, decrypts and returns it.
        """
        self.raise_if_in_async_context("This method is blocking, use `async_recv` instead.")
        
        while True:
            try:
                data = self.ssl_obj.read(n)
                # After reading decrypted data, there might be pending bytes to send (handshakes/renegotiation) —
                # flush them to the wire.
                try:
                    self.send_pending_data(timeout=timeout)
                except Exception:
                    # non-fatal flushing failure — propagate only if necessary
                    pass
                return data
            
            except ssl.SSLWantReadError:
                # Need more encrypted data from transport
                self.recv_more_encrypted_data(timeout=timeout)
            
            except ssl.SSLWantWriteError:
                # Flush out pending encrypted data to allow underlying SSL to proceed
                self.send_pending_data(timeout=timeout)
            
            except ssl.SSLEOFError:
                # peer closed cleanly
                return b''
            
            except ssl.SSLError as e:
                raise # Reraise SSLError
                
    # ASYNCHRONOUS IMPLEMENTATIONS
    
    @handle_sock_close
    async def async_send_pending_data(self, timeout: Optional[float] = None) -> int:
        """
        Asynchronous send to flush outbio. Will loop until outbio is drained or socket stops accepting.
        Returns total bytes written to the transport socket (not the application bytes).
        """
        self.raise_if_blocking()
        
        total = 0
        while True:
            data = self.ssl_outbio.read()
            if not data:
                break
            sent = await super().async_send(data, timeout=timeout) or 0
            if sent == 0:
                # transport closed or would block: re-write the unsent bytes back to outbio
                # MemoryBIO does not support push-back; simplest approach: if partial send, push rest back by
                # writing it back into ssl_outbio (be careful: ssl_outbio.write expects bytes to be read later).
                # But super().send should ideally be blocking and send all (document assumption).
                raise ConnectionError("Transport unable to send pending encrypted data")
            total += sent
            # loop until outbio drained
        return total
    
    @handle_sock_close
    async def async_recv_more_encrypted_data(self, n: int = DEFAULT_BUFSIZE, timeout: Optional[float] = None) -> int:
        """
        Asynchronously read encrypted bytes from the transport and feed them into ssl_inbio.
        Returns number of bytes written into ssl_inbio.
        Raises ConnectionResetError on EOF.
        """
        self.raise_if_blocking()
        data = await super().async_recv(n, timeout)
        if not data:
            # peer closed connection — signal EOF
            # MemoryBIO has no explicit write_eof; writing empty bytes won't help.
            # Best to raise so the caller can handle.
            raise ConnectionResetError("Underlying transport closed (EOF) while expecting encrypted data")
        self.ssl_inbio.write(data)
        return len(data)
        
    @handle_sock_close
    async def async_do_handshake(self, timeout: Optional[float] = None):
        """
        Asynchronous handshake loop with flush/recv handling and EOF detection.
        """
        self.raise_if_blocking()
        
        while not self._handshake_done:
            try:
                self.ssl_obj.do_handshake()
                
                # Flush any data remaining in outbio
                await self.async_send_pending_data(timeout=timeout)
                self._handshake_done = True
                return
            
            except ssl.SSLWantReadError:
                # Flush any sendable data, then attempt to read more encrypted bytes
                await self.async_send_pending_data(timeout=timeout)
                
                # if recv returns EOF -> will raise ConnectionResetError
                await self.async_recv_more_encrypted_data(timeout=timeout)
            
            except ssl.SSLWantWriteError:
                # We need to flush outbio — then retry
                await self.async_send_pending_data(timeout=timeout)
                
    @handle_sock_close
    async def async_send(self, data: bytes, timeout: float = None) -> int:
        """
        Encrypts and asynchronously sends application data over the network.
        
        Returns:
            int: Total bytes sent.
        """
        self.raise_if_blocking()
        
        total_written = 0
        view = memoryview(data)
        
        while total_written < len(data):
            try:
                written = self.ssl_obj.write(view[total_written:])
                
                # Written is number of application bytes accepted by SSLObject
                total_written += written
                
                # Flush out any encrypted output produced
                await self.async_send_pending_data(timeout=timeout)
            
            except ssl.SSLWantWriteError:
                # Need to flush outbio and retry
                await self.async_send_pending_data(timeout=timeout)
            
            except ssl.SSLWantReadError:
                # SSL needs more encrypted input (e.g. renegotiation)
                # read and feed more encrypted data
                await self.async_recv_more_encrypted_data(timeout=timeout)
            
        # Final flush attempt to ensure no bytes stuck in outbio
        await self.async_send_pending_data(timeout=timeout)
        return total_written
        
    @handle_sock_close
    async def async_recv(self, n: int = DEFAULT_BUFSIZE, timeout: float = None) -> bytes:
        """
        Asynchronously receives encrypted data from the socket, decrypts and returns it.
        """
        self.raise_if_blocking()
        
        while True:
            try:
                data = self.ssl_obj.read(n)
                # After reading decrypted data, there might be pending bytes to send (handshakes/renegotiation) —
                # flush them to the wire.
                try:
                    await self.async_send_pending_data(timeout=timeout)
                except Exception:
                    # non-fatal flushing failure — propagate only if necessary
                    pass
                return data
            
            except ssl.SSLWantReadError:
                # Need more encrypted data from transport
                await self.async_recv_more_encrypted_data(timeout=timeout)
            
            except ssl.SSLWantWriteError:
                # Flush out pending encrypted data to allow underlying SSL to proceed
                await self.async_send_pending_data(timeout=timeout)
            
            except ssl.SSLEOFError:
                # peer closed cleanly
                return b''
            
            except ssl.SSLError as e:
                raise # Reraise SSLError
