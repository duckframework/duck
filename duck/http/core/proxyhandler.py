"""
Module containing proxy handler class.
"""
import ssl
import socket
import importlib

from http.cookies import SimpleCookie
from collections import defaultdict
from typing import (
    Optional,
    Tuple,
    Generator,
    AsyncGenerator,
    Union
)

from duck.settings import SETTINGS
from duck.http.content import Content
from duck.http.headers import Headers
from duck.http.request import HttpRequest
from duck.http.response import StreamingHttpResponse
from duck.http.response_payload import (
    BaseResponsePayload,
    SimpleHttpResponsePayload,
)
from duck.meta import Meta
from duck.utils.net import is_domain
from duck.utils.importer import x_import
from duck.utils.headers import parse_headers_from_bytes
from duck.utils.importer import import_module_once
from duck.utils.xsocket import xsocket, create_xsocket
from duck.utils.xsocket.io import SocketIO


# Buffer size to use when receiving payload from the remote server.
# Ensure that the buffer is large enough to hold most typical payloads
# but not too large to cause inefficient memory usage.
PAYLOAD_BUFFER_SIZE = SETTINGS["SERVER_BUFFER"]

# Timeout to establish a connection with the remote proxy server (e.g., Django).
# A value of 1 second is typically used for fast responses. 
# Consider increasing if connection time to the server is high.
CONNECT_TIMEOUT = SETTINGS["PROXY_CONNECT_TIMEOUT"]  # Timeout in seconds for establishing the connection

# Timeout to wait for data from the remote proxy server.
# This value should balance between waiting for data and not blocking indefinitely.
# Increase if network latency or server load is high.
READ_TIMEOUT = SETTINGS["PROXY_READ_TIMEOUT"]  # Timeout in seconds for reading data

# The amount of data to stream at once from the remote proxy server.
# 4096 bytes (4 KB) is a reasonable default chunk size for streaming,
# but can be adjusted based on specific requirements.
STREAM_CHUNK_SIZE = SETTINGS["PROXY_STREAM_CHUNK_SIZE"]  # Streaming chunk size in bytes

# Import middleware for fixing request before reaching Django server.
DJANGO_REQUEST_FIXER_MIDDLEWARE = x_import("duck.http.middlewares.contrib.DjangoRequestFixerMiddleware")


class ReverseProxyError(Exception):
    """
    Raised on exceptions encountered on reverse-proxy ops.
    """


class BadGatewayError(ReverseProxyError):
    """
    Custom exception for bad gateway errors (HTTP 502).
    
    This exception is used to signal that the request could not be processed
    because of a server-side issue, often related to a gateway or proxy.
    """


class HttpProxyResponse(StreamingHttpResponse):
    """
    A synchronous subclass of StreamingHttpResponse that handles HTTP responses in a proxy scenario, 
    including cases where the response content is incomplete or partially received.

    This class is specifically designed to handle situations where:
    - Only the HTTP response headers are available, and content is streamed progressively.
    - The response content is incomplete, and the response is processed as it is received.
    
    It is ideal for proxy servers or intermediary systems that need to pass along 
    HTTP responses from a remote server to the client while processing and streaming the data 
    in chunks, minimizing memory usage by not requiring the full response to be loaded at once.

    Key Features:
    - **Streaming**: Supports efficient, memory-friendly streaming of content from the proxy server to the client.
    - **Partial Responses**: Handles scenarios where the response is incomplete or streaming, such as large files or slow connections.
    - **Real-Time Processing**: Allows the server to process parts of the response as they arrive without blocking or waiting for the full content.

    This class can be extended for custom logic related to response manipulation, 
    such as modifying headers, handling chunk sizes, or managing specific proxy behaviors.
        
    Example Usage:
    
    ```py
    response = HttpProxyResponse(
        target_socket,
        payload_obj,
        content_obj,
        chunk_size,
    )
        
    for content in response.iter_content():
        # Content logic here
        pass
    ```
    
    Attributes:
        target_socket: The socket already connected used for communication with the proxy server.
        payload_obj: The response payload associated with the HTTP response.
        content_obj: Content object with the initial or incomplete content.
        chunk_size: The streaming chunk size.
    """

    def __init__(
        self,
        target_socket: xsocket,
        payload_obj: BaseResponsePayload,
        content_obj: Optional[Content] = None,
        chunk_size: int = STREAM_CHUNK_SIZE,
    ):
        """
        Initialize the HttpProxyResponse object.

        Args:
            target_socket (xsocket): The live xsocket connection used to receive content.
            payload_obj (BaseResponsePayload): The response payload object containing headers and metadata.
            content_obj (Optional[Content]): The initial partial content object, if available.
            chunk_size (int): The size (in bytes) of each chunk to stream. Defaults to STREAM_CHUNK_SIZE.
        """
        self.target_socket = target_socket
        self.payload_obj = payload_obj
        self.content_obj = content_obj
        self.chunk_size = chunk_size
        self.more_data: List[bytes] = []  # List Buffer for additional data received during streaming
    
    def iter_content(self) -> Generator[bytes, None, None]:
        """
        A generator to stream the current content followed by additional data as it is received.

        Yields:
            bytes: The next chunk of data to stream.
        """
        if self.content_obj and self.content_obj.data:
            yield self.content_obj.data # Yield current data.
        
        while True:
            data = self.recv_more(self.chunk_size)
            if data:
                yield data
            else:
                break
                
    def recv_more(self, buffer: int = 4096) -> bytes:
        """
        Receive additional data from the target socket.

        Args:
            buffer (int): The buffer size for receiving data. Defaults to 4096 bytes.

        Returns:
            bytes: The received data, or an empty byte string if the content is complete.
        """
        try:
            # Calculate the current content length and the expected total length
            current_content_length = len(self.more_data) + (len(self.content_obj.data) if self.content_obj else 0)
            expected_content_length = self.payload_obj.get_header("content-length")

            # If the content length is known and fully received, stop receiving
            if expected_content_length and expected_content_length.isdigit():
                if current_content_length >= int(expected_content_length):
                    return b""

            # Receive data from the socket
            data = SocketIO.receive(self.target_socket, bufsize=buffer, timeout=READ_TIMEOUT)
            self.more_data.append(data)
            return data

        except (TimeoutError, ConnectionResetError, EOFError):
            # Handle errors silently
            pass

        except (OSError, socket.error) as e:
            raise BadGatewayError(f"Receiving additional data failed: {e}")

        return b""

    def __repr__(self):
        return f"<{self.__class__.__name__} (" f"'{self.status_code}'" f")>"


class HttpProxyHandler:
    """
    HttpProxyHandler class to handle forwarding TCP requests to target hosts.
    
    This class supports both IPv4 and IPv6 and allows modification of headers
    before forwarding the data to the client.
    """
    __slots__ = ("uses_ipv6", "target_host", "target_port", "uses_ssl")
    
    def __init__(
        self,
        target_host: str,
        target_port: int,
        uses_ipv6: bool = False,
        uses_ssl: bool = False,
    ):
        """
        Initializes the ProxyHandler.

        Args:
            uses_ipv6 (bool): Boolean indicating whether to use IPv6. Defaults to False.
        """
        assert isinstance(target_host, str), (
            "Target host should be a string representing hostname or host ip address."
        )
        
        assert isinstance(target_port, int), (
            "Target port should be an integer for host port."
        )
        
        self.uses_ipv6 = uses_ipv6
        self.target_host = socket.gethostbyname(target_host) if is_domain(target_host) else target_host
        self.target_host = "127.0.0.1" if self.target_host.startswith("0.") else self.target_host # Windows compatibility
        self.target_port = target_port
        self.uses_ssl = uses_ssl
        
        if self.uses_ssl:
            raise ReverseProxyError("Reverse proxying to SSL servers not supported yet.")
        
    def get_response(
        self,
        request: HttpRequest,
        client_socket: socket.socket,
     ) -> HttpProxyResponse:
        """
        Handles the client connection and forwards the request to the target server and returns partial response.
        To receive more response, use method HttpPartialResponse.recvmore, this method may raise

        Args:
            request (HttpRequest): Client Http request object.
            client_socket (socket.socket): The socket object connected to the client.

        Returns:
                HttpProxyResponse: The partial unfinished response ready for processing but lacking full content.
        """
        # Connect to the target server
        target_socket = self.connect_to_target()
        
        try:
            # Forward the client's request to the target server
            self.forward_request_to_target(request, client_socket, target_socket)
            
            # Receive partial response
            payload, partial_content = self.fetch_response_payload(target_socket)
            
            content_length_header = payload.get_header("content-length")
            chunk_size = None
            
            try:
                content_length_header = int(content_length_header)
                chunk_size = min(content_length_header, STREAM_CHUNK_SIZE)
            except (ValueError, TypeError):
                pass
            
            streaming_response = HttpProxyResponse(
                target_socket,
                payload_obj=payload,
                content_obj=Content(partial_content),
                chunk_size=chunk_size or STREAM_CHUNK_SIZE,
            )
            return streaming_response
        except (OSError, ConnectionRefusedError, socket.error) as e:
            raise BadGatewayError(f"Connection was successful, but subsequent actions failed: {e}.")
    
    def connect_to_target(self) -> xsocket:
        """
        Connects to the target server.

        Returns:
            xsocket: The xsocket object connected to the target server.
        """
        target_socket = create_xsocket(
            socket.AF_INET6 if self.uses_ipv6 else socket.AF_INET,
            socket.SOCK_STREAM,
        )
        
        try:
            SocketIO.connect(target_socket, (self.target_host, self.target_port), timeout=CONNECT_TIMEOUT)
            return target_socket
        except (OSError, ConnectionRefusedError, socket.error) as e:
            raise BadGatewayError(f"Connection to remote server failed: {e}")

    def forward_request_to_target(
        self,
        request: HttpRequest,
        client_socket: xsocket,
        target_socket: xsocket,
    ):
        """
        Forwards the client's request to the target server.

        Args:
            request (HttpRequest): Client Http request object to forward to target server.
            client_socket (xsocket): The socket object connected to the client.
            target_socket (xsocket): The socket object connected to the target server.
        """
        # Modify headers if needed
        self.modify_client_request(request)
        SocketIO.send(target_socket, request.raw)

    def fetch_response_payload(
        self,
        target_socket: xsocket,
     ) -> Tuple[SimpleHttpResponsePayload, bytes]:
        """
        Returns received Response Payload and leftover data from target server.

        Returns:
            SimpleHttpResponsePayload, bytes: This is SimpleHttpResponsePayload object and leftover_data (partial data sent from target server after headers).
        """
        data = b""
        leftover_data = b""
        
        while True:
            part = SocketIO.receive(target_socket, bufsize=PAYLOAD_BUFFER_SIZE, timeout=READ_TIMEOUT)
            data = data.join([b"", part])
            
            if b"\r\n\r\n" in data or not data:
                # content separator
                break
        try:
            topheader, data = data.split(b"\r\n", 1)
            data = data.split(b"\r\n\r\n", 1)
        except ValueError:
            raise BadGatewayError("Response payload is malformed.")
        
        if len(data) > 1:
            data, _leftover = data
            leftover_data = leftover_data.join([b"", _leftover])
        else:
            data = data[0]
        
        # Parse headers from bytes - assuming it returns a dictionary with lists of values for each header
        headers: Dict[str, List[str]] = parse_headers_from_bytes(data)
        
        # Prepare containers for cleaned headers and set-cookie headers
        cleaned_headers = {}  # Will hold only the latest value for each header (no duplicates)
        set_cookies = []  # List to hold all Set-Cookie headers
        
        # Iterate through each header to process them
        for header, values in headers.items():
            # Special handling for 'Set-Cookie' headers as they can appear multiple times
            if header.lower() == "set-cookie":
                set_cookies.extend(values)  # Add all 'Set-Cookie' values to the set_cookies list
            else:
                # For all other headers, keep only the last value (no duplicates)
                cleaned_headers[header] = values[-1]
        
        # At this point, `cleaned_headers` will contain headers with a single value each,
        # and `set_cookies` will contain all Set-Cookie values.
        # set topheader, headers in response payload
        payload = SimpleHttpResponsePayload(topheader.decode("utf-8"), cleaned_headers)
        
        for set_cookie in set_cookies:
            try:
                payload.cookies.load(set_cookie)
            except (CookieError, TypeError):
                pass
        return payload, leftover_data

    def modify_client_request(self, request: HttpRequest):
        """
        Modifies the Http request if needed.

        Args:
            request (HttpRequest): Client Http request object.
        """
        # Implement your header modification logic here
        if SETTINGS["USE_DJANGO"]:
            DJANGO_REQUEST_FIXER_MIDDLEWARE.process_request(request)


# ASYNCHRONOUS IMPLEMENTATIONS

class AsyncHttpProxyResponse(HttpProxyResponse):
    """
    An asynchronous subclass of HttpProxyResponse that handles HTTP responses in a proxy scenario, 
    including cases where the response content is incomplete or partially received.

    This class is specifically designed to handle situations where:
    - Only the HTTP response headers are available, and content is streamed progressively.
    - The response content is incomplete, and the response is processed as it is received.
    
    It is ideal for proxy servers or intermediary systems that need to pass along 
    HTTP responses from a remote server to the client while processing and streaming the data 
    in chunks, minimizing memory usage by not requiring the full response to be loaded at once.

    Key Features:
    - **Streaming**: Supports efficient, memory-friendly streaming of content from the proxy server to the client.
    - **Partial Responses**: Handles scenarios where the response is incomplete or streaming, such as large files or slow connections.
    - **Real-Time Processing**: Allows the server to process parts of the response as they arrive without blocking or waiting for the full content.

    This class can be extended for custom logic related to response manipulation, 
    such as modifying headers, handling chunk sizes, or managing specific proxy behaviors.
    
    Example Usage:
    
    ```py
    response = AsyncHttpProxyResponse(
        target_socket,
        payload_obj,
        content_obj,
        chunk_size,
    )
        
    async for content in response.async_iter_content():
        # Content logic here
        pass
    ```
    
    Attributes:
        target_socket: The socket already connected used for communication with the proxy server.
        payload_obj: The response payload associated with the HTTP response.
        content_obj: Content object with the initial or incomplete content.
        chunk_size: The streaming chunk size.
    """
    async def async_iter_content(self) -> AsyncGenerator[bytes]:
        """
        An asynchronous generator to stream the current content followed by additional data as it is received.

        Yields:
            bytes: The next chunk of data to stream.
        """
        if self.content_obj and self.content_obj.data:
            yield self.content_obj.data # Yield current data.
            
        while True:
            data = await self.recv_more(self.chunk_size)
            if data:
                yield data
            else:
                break
                
    async def recv_more(self, buffer: int = 4096) -> bytes:
        """
        Asynchronously receive additional data from the target socket.

        Args:
            buffer (int): The buffer size for receiving data. Defaults to 4096 bytes.

        Returns:
            bytes: The received data, or an empty byte string if the content is complete.
        """
        try:
            # Calculate the current content length and the expected total length
            current_content_length = len(self.more_data) + (len(self.content_obj.data) if self.content_obj else 0)
            expected_content_length = self.payload_obj.get_header("content-length")

            # If the content length is known and fully received, stop receiving
            if expected_content_length and expected_content_length.isdigit():
                if current_content_length >= int(expected_content_length):
                    return b""

            # Receive data from the socket
            data = await SocketIO.async_receive(self.target_socket, bufsize=buffer, timeout=READ_TIMEOUT)
            self.more_data.append(data)
            return data

        except (TimeoutError, ConnectionResetError, EOFError):
            # Handle errors silently
            pass

        except (OSError, socket.error) as e:
            raise BadGatewayError(f"Receiving additional data failed: {e}")

        return b""

    def __repr__(self):
        return f"<{self.__class__.__name__} (" f"'{self.status_code}'" f")>"


class AsyncHttpProxyHandler(HttpProxyHandler):
    """
    An asynchronous HttpProxyHandler class to handle forwarding TCP requests to target hosts.
    
    This class supports both IPv4 and IPv6 and allows modification of headers
    before forwarding the data to the client.
    """
    
    async def get_response(
        self,
        request: HttpRequest,
        client_socket: socket.socket,
     ) -> AsyncHttpProxyResponse:
        """
        Asynchronously handles the client connection and forwards the request to the target server and returns partial response.
        To receive more response, use method HttpPartialResponse.recvmore, this method may raise

        Args:
            request (HttpRequest): Client Http request object.
            client_socket (socket.socket): The socket object connected to the client.

        Returns:
                AsyncHttpProxyResponse: The partial unfinished response ready for processing but lacking full content.
        """
        # Connect to the target server
        target_socket = await self.connect_to_target()
        
        try:
            # Forward the client's request to the target server
            await self.forward_request_to_target(request, client_socket, target_socket)
            
            # Receive partial response
            payload, partial_content = await self.fetch_response_payload(target_socket)
            
            content_length_header = payload.get_header("content-length")
            chunk_size = None
            
            try:
                content_length_header = int(content_length_header)
                chunk_size = min(content_length_header, STREAM_CHUNK_SIZE)
            except (ValueError, TypeError):
                pass
            
            streaming_response = AsyncHttpProxyResponse(
                target_socket,
                payload_obj=payload,
                content_obj=Content(partial_content),
                chunk_size=chunk_size or STREAM_CHUNK_SIZE,
            )
            
            return streaming_response
        except (OSError, ConnectionRefusedError, socket.error) as e:
            raise BadGatewayError(f"Connection was successful, but subsequent actions failed: {e}.")
    
    async def connect_to_target(self) -> xsocket:
        """
        Asynchronously connects to the target server.

        Returns:
            xsocket: The xsocket object connected to the target server.
        """
        target_socket = create_xsocket(
            socket.AF_INET6 if self.uses_ipv6 else socket.AF_INET,
            socket.SOCK_STREAM,
        )
        
        # Set socket blocking to False 
        target_socket.setblocking(False)
        
        try:
            await SocketIO.async_connect(target_socket, (self.target_host, self.target_port), timeout=CONNECT_TIMEOUT)
            return target_socket
        except (OSError, ConnectionRefusedError, socket.error) as e:
            raise BadGatewayError(f"Connection to remote server failed: {e}")

    async def forward_request_to_target(
        self,
        request: HttpRequest,
        client_socket: xsocket,
        target_socket: xsocket,
    ):
        """
        Asynchronously forwards the client's request to the target server.

        Args:
            request (HttpRequest): Client Http request object to forward to target server.
            client_socket (xsocket): The socket object connected to the client.
            target_socket (xsocket): The socket object connected to the target server.
        """
        # Modify headers if needed
        self.modify_client_request(request)
        raw_request = request.raw.join([b"", b"\r\n\r\n"])
        await SocketIO.async_send(target_socket, raw_request)

    async def fetch_response_payload(
        self,
        target_socket: xsocket,
     ) -> Tuple[SimpleHttpResponsePayload, bytes]:
        """
        Returns received Response Payload and leftover data from target server.

        Returns:
            SimpleHttpResponsePayload, bytes: This is SimpleHttpResponsePayload object and leftover_data (partial data sent from target server after headers).
        """
        data = b""
        leftover_data = b""
        
        while True:
            part = await SocketIO.async_receive(target_socket, bufsize=PAYLOAD_BUFFER_SIZE, timeout=READ_TIMEOUT)
            data = data.join([b"", part])
            
            if b"\r\n\r\n" in data or not data:
                # content separator
                break
        try:
            topheader, data = data.split(b"\r\n", 1)
            data = data.split(b"\r\n\r\n", 1)
        except ValueError:
            raise BadGatewayError("Response payload is malformed.")
        
        if len(data) > 1:
            data, _leftover = data
            leftover_data = leftover_data.join([b"", _leftover])
        else:
            data = data[0]
        
        # Parse headers from bytes - assuming it returns a dictionary with lists of values for each header
        headers: Dict[str, List[str]] = parse_headers_from_bytes(data)
        
        # Prepare containers for cleaned headers and set-cookie headers
        cleaned_headers = {}  # Will hold only the latest value for each header (no duplicates)
        set_cookies = []  # List to hold all Set-Cookie headers
        
        # Iterate through each header to process them
        for header, values in headers.items():
            # Special handling for 'Set-Cookie' headers as they can appear multiple times
            if header.lower() == "set-cookie":
                set_cookies.extend(values)  # Add all 'Set-Cookie' values to the set_cookies list
            else:
                # For all other headers, keep only the last value (no duplicates)
                cleaned_headers[header] = values[-1]
        
        # At this point, `cleaned_headers` will contain headers with a single value each,
        # and `set_cookies` will contain all Set-Cookie values.
        # set topheader, headers in response payload
        payload = SimpleHttpResponsePayload(topheader.decode("utf-8"), cleaned_headers)
        
        for set_cookie in set_cookies:
            try:
                payload.cookies.load(set_cookie)
            except (CookieError, TypeError):
                pass
        return payload, leftover_data
