"""
Duck WebSocket Implementation.

In your urlpatterns, you can use websocket protocol as follows:

```
# urls.py

from duck.urls import path
from duck.contrib.websockets import WebSocketView, OpCode

class MyWebSocket(WebSocketView):
    async def on_open(self):
        print("WebSocket connection established")
        
    async def on_receive(data, opcode: int):
        if opcode == OpCode.TEXT:
            message = "Client sent " + data.decode("utf-8")
            await self.send_text(message)
         else:
             # Handle binary here
             pass

# Now create a urlpattern entry
urlpatterns = [
    path("/ws/myws", MyWebSocket, name="mywebsocket"),
    # other patterns here.
]

```
"""
import ssl
import time
import json
import struct
import copy
import base64
import hashlib
import asyncio
import enum

from typing import (
    Sequence,
    List,
    Optional,
    Union,
)

from duck.views import View
from duck.settings import SETTINGS
from duck.exceptions.all import ExpectingNoResponse 

from duck.http.request import HttpRequest
from duck.http.response import (
    HttpSwitchProtocolResponse,
    HttpBadRequestResponse
)
from duck.contrib.websockets.frame import Frame
from duck.contrib.websockets.logging import log_message, logger
from duck.contrib.websockets.opcodes import (
    OpCode,
    CloseCode,
    DATA_OPCODES,
)
from duck.contrib.websockets.extensions import (
    Extension,
    PerMessageDeflate,
)
from duck.contrib.websockets.exceptions import (
    ProtocolError,
    PayloadTooBig,
)
from duck.utils.xsocket import xsocket
from duck.utils.xsocket.io import SocketIO
from duck.utils.asyncio import create_task


class State(enum.IntEnum):
    """
    Int enum of connection state.
    """
    OPEN = 1
    CLOSED = 0
    INITIATING = -1
    INITIATED = 2


class WebSocketView(View):
    """
    RFC 7692-compliant WebSocket view with permessage-deflate compression,
    context takeover negotiation, heartbeat, fragmentation handling,
    partial streaming of large frames, and robust error handling.

    Features:
    - Supports WebSocket upgrade handshake with version checks.
    - Negotiates permessage-deflate compression extension with context takeover flags.
    - Sends and receives WebSocket frames with optional compression.
    - Implements ping/pong heartbeat with exponential backoff and failure detection.
    - Handles fragmented message reassembly.
    - Ensures all task exceptions in heartbeat and receive loops are properly re-raised.
    - Cleanly closes connections and releases resources.
    """
    
    MAGIC_STRING = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
    """
    str: Magic string for generating Sec-WebSocket-Accept-Key.
    """
    
    PING_INTERVAL = 20
    """
    int: Seconds between sending ping frames.
    """

    PONG_TIMEOUT = 10
    """
    int: Seconds to wait for a pong response.
    """

    MAX_BACKOFF = 45
    """
    int: Maximum exponential backoff delay in seconds.
    """
    
    RECEIVE_TIMEOUT = 120
    """
    int: Timeout in seconds for receiving WebSocket frames.
    """

    MAX_FRAME_SIZE = 1 * 1024 * 1024
    """
    int: Maximum allowed size of incoming message frame in bytes (1MB).
    """

    def __init__(self, upgrade_request: HttpRequest, **kwargs):
        """
        Initialize the WebSocketView with the initial HTTP upgrade request.

        Args:
            upgrade_request (HttpRequest): The HTTP request that initiated the WebSocket upgrade.
            **kwargs: Additional keyword arguments passed to subclasses.

        Initializes internal state for compression, heartbeat, fragmentation,
        and communication queues.
        """
        from duck.http.core.httpd.httpd import response_handler

        self.request = upgrade_request
        self.kwargs = kwargs
        
        # Private attributes
        self._closing = False
        self._last_pong_time = time.time()
        self._heartbeat_task = None
        self._receiver_task = None
        self._response_handler = response_handler
        self._data_handling_tasks: set[asyncio.Task] = set()
        
        # WebSocket state
        self.client_websocket_version = None
        self.min_websocket_version = 8
        self.initiated_upgrade = False
        self.fragmented_frame: Frame = None
        self.state = State.CLOSED
        
        # Extensions negotiated upon upgrade
        self.extensions: Sequence[Extension] = []
        
    @property
    def server(self):
        return self.request.application.server
        
    @property
    def sock(self):
        """
        Returns the connected socket.
        """
        return self.request.client_socket
        
    def strictly_async(self):
        return True # Set the view to be strictly asynchronous
    
    def get_sec_accept_key(self, sec_websocket_key: str) -> str:
        """
        Generates the Sec-WebSocket-Accept key for the handshake response.
        
        Args:
            sec_websocket_key (str): Sec-WebSocket-Key header value.
            
        Returns:
            str: Base64-encoded SHA-1 hash of the client's Sec-WebSocket-Key and the magic string.
        """
        combined = sec_websocket_key + self.MAGIC_STRING
        sha1 = hashlib.sha1(combined.encode("utf-8")).digest()
        return base64.b64encode(sha1).decode("utf-8")
            
    async def run(self) -> None:
        """
        Entry point for executing the WebSocket view.
    
        This method runs the view's main event loop (`run_forever`). It is expected
        that `run_forever` never returns under normal operation. If it does return
        without raising an exception, an `ExpectingNoResponse` error is raised,
        indicating an unexpected termination.
    
        Raises:
            ExpectingNoResponse: If `run_forever` completes without raising an exception.
            Exception: Any exception raised during the execution of `run_forever`.
        """
        exc = None
        
        # Set client socket blocking to False if set to true.
        self.request.client_socket.setblocking(False)
        
        try:
            await self.run_forever()
        except Exception as e:
            exc = e
        finally:
            if exc is None:
                raise ExpectingNoResponse("WebSocket view must not return a response.")
            if self.state in [State.INITIATED, State.CLOSED]:
                # Don't raise exception, avoid doing so to avoid server responding with Internal Server Error
                # because initial response has already been sent to client.
                logger.log_raw(
                    f'\nError invoking websocket view for URL "{self.request.path}" ',
                    level=logger.ERROR,
                    custom_color=logger.Fore.YELLOW,
                )
                logger.log_exception(exc)
            else:
                raise exc  # Reraise original exception
              
    async def initiate_upgrade_to_ws(self) -> bool:
        """
        Perform the WebSocket handshake and send upgrade response to client.

        Negotiates permessage-deflate compression extension and context takeover
        parameters per RFC 7692 if supported by the client.

        Returns:
            bool: True if handshake and upgrade succeeded, False otherwise.
        """
        from duck.shortcuts import simple_response, template_response
        from duck.http.middlewares.security.csrf import (
            CSRFMiddleware,
            OriginError,
        )
        
        error_msg = None
        sec_key = self.request.get_header('sec-websocket-key', '').strip()
        version = self.request.get_header("sec-websocket-version", "").strip()

        if self.request.get_header("upgrade", "").lower() != "websocket":
            error_msg = "Missing Upgrade: websocket"
        
        elif getattr(self.sock, "h2_handling", False):
            error_msg = "WebSocket not allowed on HTTP/2"
        
        elif not sec_key:
            error_msg = "Missing Sec-WebSocket-Key"
        
        elif not version:
            error_msg = "Missing Sec-WebSocket-Version"
        
        else:
            try:
                self.client_websocket_version = int(version)
                if self.client_websocket_version < self.min_websocket_version:
                    error_msg = f"Minimum version {self.min_websocket_version} required"
            except ValueError:
                error_msg = "Invalid Sec-WebSocket-Version"

        headers = {"Sec-WebSocket-Accept": self.get_sec_accept_key(sec_key)}
        exts = self.request.get_header("sec-websocket-extensions", "").lower()
        negotiated_exts = []
        
        # Check origin validity
        try:
            CSRFMiddleware._check_origin_ok(self.request)
        except OriginError as e:
            response = (template_response if SETTINGS['DEBUG'] else simple_response)(HttpBadRequestResponse)
            self.request.META["DEBUG_MESSAGE"] = str(e)
            await self._response_handler.async_send_response(response, self.sock, request=self.request)
            return
            
        if "permessage-deflate" in exts:
            client_no_context_takeover = "client_no_context_takeover" in exts
            server_no_context_takeover = "server_no_context_takeover" in exts
            
            # Add permessage-deflate extension
            permessage_deflate = PerMessageDeflate(
                name="permessage-deflate",
                client_no_context_takeover=client_no_context_takeover,
                server_no_context_takeover=server_no_context_takeover,
            )
            
            # Add extension in list
            self.extensions.append(permessage_deflate)
            
            # Add negotiated extensions
            negotiated_exts.append(permessage_deflate.name)
            negotiated_exts.append("client_no_context_takeover") if client_no_context_takeover else None
            negotiated_exts.append("server_no_context_takeover") if server_no_context_takeover else None
            
        # Set negotiated extensions in headers
        if negotiated_exts:
            headers["Sec-WebSocket-Extensions"] = "; ".join(negotiated_exts)
            
        response = (
            HttpSwitchProtocolResponse(upgrade_to="websocket", headers=headers)
            if not error_msg
            else (template_response if SETTINGS.get("DEBUG") else simple_response)(
                HttpBadRequestResponse, body=error_msg
            )
        )
        
        # Update state and send response
        self.state = State.INITIATING
        await self._response_handler.async_send_response(response, self.sock, request=self.request)
        
        # Set the state of the upgrade
        self.initiated_upgrade = error_msg is None
        
        # Set and return the state of the upgrade.
        if self.initiated_upgrade:
            self.state = State.INITIATED
        return self.initiated_upgrade

    async def run_forever(self):
        """
        Run the WebSocket connection until closed or error occurs.

        Starts asynchronous tasks for heartbeat ping/pong and receiving frames.
        Waits until one of the tasks completes or raises an exception.

        Exceptions raised inside heartbeat or receive loops are re-raised here.

        Upon exit, calls `safe_close` to clean up resources.
        """
        pending = []
        
        if not await self.initiate_upgrade_to_ws():
            SocketIO.close(self.sock)
            self.state = State.CLOSED
            return
        
        # Log some message to the terminal
        log_message(self.request, f"{self.request.path} [WebSocket] [OPEN]")
        loop_exc = None # exception that may have been raised by a receive_loop or heartbeat_loop
        
        try:
            self._heartbeat_task = create_task(self._heartbeat_loop(), ignore_errors=[BaseException]) # ignore all exceptions.
            self._receiver_task = create_task(self._receive_loop(), ignore_errors=[BaseException])
    
            done, pending = await asyncio.wait(
                [self._receiver_task, self._heartbeat_task], return_when=asyncio.FIRST_COMPLETED
            )
            
            ignore_errors = (
                ConnectionError,
                ConnectionResetError,
                ssl.SSLError,
                ssl.SSLWantReadError,
                ssl.SSLWantWriteError,
                OSError,
                struct.error,
                BrokenPipeError,
                asyncio.CancelledError,
            )
            
            for task in done:
                try:
                    exc = task.exception() # put this in a try block in case it raises an exception
                except Exception as e:
                    exc = e
                    
                if exc:
                    loop_exc = exc
                    
                    if isinstance(exc, TimeoutError):
                        # Did not receive data within specific timeout
                        await self.send_close(CloseCode.GOING_AWAY, reason="WebSocket Timeout Error")
                        return
                        
                    elif not any([isinstance(exc, i) for i in ignore_errors]):
                        if "Connection closed while reading exact bytes" in str(exc):
                            # Avoid logging this exception, it happens almost everytime 
                            # when connection closed unexpectably
                            return
                        
                        if SETTINGS['DEBUG']:
                            # Only log these errors in debug mode.
                            logger.log_raw(f'Error running websocket loop for URL "{self.request.path}" ', level=logger.WARNING)
                            logger.log_exception(task.exception())
                    
                    # Break loop on first exception
                    break
                    
        finally:
            # WebSocket Shutdown
            for task in {*self._data_handling_tasks, *(pending or [])}:
                if not task.done():
                    try:
                        task.cancel()
                    except Exception:
                        pass
                        
            # Clear the data handling tasks
            self._data_handling_tasks.clear()
            
            if loop_exc and isinstance(loop_exc, TimeoutError):
                await self.safe_close(disable_logging=True)
                log_message(self.request, debug_message=[f"{self.request.path} [WebSocket] [CLOSE]", "WebSocket Timeout"])
            else:
                await self.safe_close()
                self.state = State.CLOSED
                
    async def on_new_frame(self, frame: Frame):
        """
        Handles the new frame by parsing it to `on_receive`.
        """
        try:
            await self.on_receive(frame.payload, frame.opcode)
        except Exception as e:
            logger.log_exception(e)
            await self.send_close(CloseCode.INTERNAL_ERROR, reason="Internal Server Error" + f": {e}" if SETTINGS['DEBUG'] else "")
        
    async def on_open(self):
        """
        Called on WebSocket open.
        """
        pass
        
    async def on_receive(self, message: bytes, opcode, **kwargs):
        """
        Called when a full WebSocket message is received.

        Should be overridden by subclasses to implement message handling.

        Args:
            message (bytes): Message payload.
            opcode (int): Message opcode.
        """
        raise NotImplementedError("Implement this method to handle received WebSocket messages.")

    async def on_close(self, frame: Frame = None):
        """
        Called when the WebSocket connection is closed.

        Override to implement cleanup logic but make sure to call `safe_close(call_on_close_handler=False)` to actually close the connection.

        Args:
            frame (int, optional): Close frame if the client sent a close frame.
        """
        if frame:
            try:
                await self.send_close(CloseCode.NORMAL_CLOSURE, reason="Normal closure")
            except Exception:
                pass
        await self.safe_close(call_on_close_handler=False)
          
    async def read_frame(self) -> Frame:
        """
        Read a single WebSocket frame from the client.
        
        Handles masking and permessage-deflate decompression.

        Returns:
            Frame: The parsed frame.
        
        Raises:
            ProtocolError: If the frame format is invalid.
            PayloadTooBig: If the payload exceeds max_size.
        """
        
        async def read_exact(n: int):
            """
            Async function for reading exact number of bytes from the socket.
            """
            timeout = self.RECEIVE_TIMEOUT
            buffer = bytearray()
            
            while len(buffer) < n:
                await asyncio.sleep(0)
                chunk = await SocketIO.async_receive(sock=self.request.client_socket, timeout=timeout, bufsize=(n - len(buffer)))
                if not chunk:
                    # connection closed before reading n bytes
                    raise ProtocolError("Connection closed while reading exact bytes")
                buffer.extend(chunk)
            return bytes(buffer)
            
        # Receive frame from the socket
        frame = await Frame.parse(
            read_exact=read_exact,
            mask_required=True,
            max_size=self.MAX_FRAME_SIZE,
            extensions=self.extensions
        )
        
        # Return the new frame.
        return frame
            
    async def _heartbeat_loop(self):
        """
        Periodically send ping frames and verify pong responses.

        Uses exponential backoff on missed pong frames. Raises TimeoutError after
        three consecutive failures.

        Raises:
            TimeoutError: If pong not received within timeout multiple times.
            Exception: Propagates other exceptions from send_ping or sleep.
        """
        failures = 0
        base = self.PING_INTERVAL
            
        while not self._closing:
            try:
                await self.send_ping()
            except Exception:
                pass
            await asyncio.sleep(self.PONG_TIMEOUT)
            if time.time() - self._last_pong_time > self.PONG_TIMEOUT:
                failures += 1
                if failures >= 3:
                    raise TimeoutError("WebSocket pong timeout")
                delay = min(base * (2 ** failures), self.MAX_BACKOFF)
                await asyncio.sleep(delay)
            else:
                failures = 0
                await asyncio.sleep(base - self.PONG_TIMEOUT)
                
    async def _receive_loop(self):
        """
        Continuously reads frames from the client, handles control frames,
        reassembles fragmented messages, and dispatches complete messages
        to the handler.
    
        Raises:
            Exception: Propagates exceptions from socket read or processing.
        """
        # Execute on_open event.
        await self.on_open()
        
        while not self._closing:
            try:
                frame = await self.read_frame()
            except PayloadTooBig:
                await self.send_close(
                    CloseCode.GOING_AWAY,
                    reason=f"Payload too big. Max payload is {self.MAX_FRAME_SIZE} bytes"
                )
                break
    
            if frame.opcode == OpCode.CLOSE:
                await self.on_close(frame)
    
            elif frame.opcode == OpCode.PING:
                await self.send_pong(frame.payload)
    
            elif frame.opcode == OpCode.PONG:
                self._last_pong_time = time.time()
    
            elif frame.opcode in (OpCode.TEXT, OpCode.BINARY):
                if frame.fin:
                    # Use duck.utils.asyncio.create_task as it automatically raises errors (if any) compared to the
                    # default asyncio.create_task
                    task = create_task(
                        coro=self.on_new_frame(frame),
                        on_complete=lambda task: (
                            self._data_handling_tasks.remove(task)
                            if task in self._data_handling_tasks
                            else None
                        ),
                    )
                    
                    # Add data handling task to task list
                    self._data_handling_tasks.add(task)
                    
                else:
                    # Start buffering fragmented message
                    self.fragmented_frame = frame
    
            elif frame.opcode == OpCode.CONTINUATION:
                if not self.fragmented_frame:
                    raise ProtocolError("Continuation frame without initial fragment")
                
                # Add more payload to fragmented frame.
                self.fragmented_frame.payload += frame.payload
                
                if frame.fin:
                    self.fragmented_frame.fin = True
                    
                    # Make a copy of the frame in case it gets resetted.
                    frame = copy.copy(self.fragmented_frame)
                    
                    try:
                        # Use duck.utils.asyncio.create_task as it automatically raises errors (if any) compared to the
                        # default asyncio.create_task
                        task = create_task(
                            coro=self.on_new_frame(frame),
                            on_complete=lambda task: (
                                self._data_handling_tasks.remove(task)
                                if task in self._data_handling_tasks
                                else None
                            ),
                        )
                        
                        # Add data handling task to task list
                        self._data_handling_tasks.add(task)
                        
                    finally:
                        # Reset the fragmented frame.
                        self.fragmented_frame = None
            else:
                raise ProtocolError(f"Unexpected opcode: {frame.opcode}")
             
            # Yield control to eventloop.
            await asyncio.sleep(0)
             
    async def send_frame(self, frame: Frame):
        """
        Sends a frame to the client, first it applies all negotiated extensions received upon upgrare and
        then it sends the frame to the connected client socket.
        """
        data = frame.serialize(mask=False, extensions=self.extensions)
        await SocketIO.async_send(sock=self.sock, data=data, ignore_error_list=[ssl.SSLError, BrokenPipeError])
        
    async def send(self, data: Union[str, bytes], opcode: int = OpCode.TEXT):
        """
        Alias to send a WebSocket message frame.

        Args:
            data (Union[str, bytes]): Payload data.
            opcode (int): WebSocket frame opcode. Defaults to 0x1 (TEXT).
        """
        data = data.encode() if not isinstance(data, bytes) else data
        max_size = self.MAX_FRAME_SIZE
        data_len = len(data)
        
        if opcode in DATA_OPCODES and data_len > max_size:
            remaining = data_len
            sent_len = 0
            
            # Send fragmented frames.
            while remaining > 0:
                chunk_size = min(max_size, remaining)
                data_to_send = data[sent_len:sent_len + chunk_size]
                
                if remaining == data_len:
                    # First frame
                    frame = Frame(
                        opcode=opcode,
                        fin=False,
                        payload=data_to_send,
                        rsv1=False,
                        rsv2=False,
                        rsv3=False,
                    )
                
                elif remaining > chunk_size:
                    # Continuation frame
                    frame =  Frame(
                        opcode=OpCode.CONTINUATION,
                        fin=False,
                        payload=data_to_send,
                        rsv1=False,
                        rsv2=False,
                        rsv3=False,
                    )
                    
                
                elif remaining == chunk_size:
                    # Last frame
                    frame = Frame(
                        opcode=OpCode.CONTINUATION,
                        fin=True,
                        payload=data_to_send,
                        rsv1=False,
                        rsv2=False,
                        rsv3=False,
                    )
                
                # Send frame
                await self.send_frame(frame)
                
                # Set some values.
                remaining -= chunk_size
                sent_len += chunk_size
        
        else:
            # This is the final frame
            frame = Frame(
                opcode=opcode,
                fin=True,
                payload=data,
                rsv1=False,
                rsv2=False,
                rsv3=False,
            )
            
            # Send frame
            await self.send_frame(frame)
            
    async def send_text(self, data: str):
        """
        Send a text WebSocket message.

        Args:
            data (str): Text message to send.
        """
        await self.send(data, opcode=OpCode.TEXT)

    async def send_json(self, data: Union[dict, list]):
        """
        Serialize a Python object to JSON and send as a text message.

        Args:
            data (Union[dict, list]): Python data to serialize.
        """
        json_str = json.dumps(data)
        await self.send_text(json_str)

    async def send_binary(self, data: bytes):
        """
        Send binary data as a WebSocket message.

        Args:
            data (bytes): Raw bytes to send.
        """
        await self.send(data, opcode=OpCode.BINARY)

    async def send_ping(self, data: bytes = b""):
        """
        Send a ping control frame.

        Args:
            data (bytes): Optional ping payload.
        """
        await self.send(data, opcode=OpCode.PING)

    async def send_pong(self, data: bytes = b""):
        """
        Send a pong control frame.

        Args:
            data (bytes): Optional pong payload.
        """
        await self.send(data, opcode=OpCode.PONG)

    async def send_close(self, code: int = CloseCode.NORMAL_CLOSURE, reason: str = ""):
        """
        Send a close control frame and initiate connection close.
        
        This is failsafe, meaning it just fails silently.
        
        Args:
            code (int): WebSocket close status code. Defaults to 1000 (Normal Closure).
            reason (str): Optional close reason string.
        """
        try:
            payload = struct.pack(">H", code) + reason.encode()
            await self.send(payload, opcode=OpCode.CLOSE)
        except Exception as e:
            logger.log_exception(e)
            
    async def safe_close(self, disable_logging: bool = False, call_on_close_handler: bool = True):
        """
        Safely close the WebSocket connection and invoke `on_close` callback.

        Ensures close logic is only run once.
        
        Args:
            disable_logging (bool): Disables logging even on first attempt.
            call_on_close_handler (bool): Whether to call `on_close` method before closing.
        """
        if not self._closing:
            if self.initiated_upgrade and not disable_logging:
                log_message(self.request, f"{self.request.path} [WebSocket] [CLOSE]")
            self._closing = True
        if call_on_close_handler:
          try:
              await self.on_close(frame=None)
          except Exception as e:
              logger.log_exception(e)
        SocketIO.close(self.sock) # fail-safe method to close socket.'
        self.state = State.CLOSED
