"""
Socket I/O implementations.
"""
import re
import ssl
import socket

from typing import List, Type, Tuple

from duck.settings import SETTINGS
from duck.utils.xsocket import xsocket


SERVER_BUFFER = SETTINGS["SERVER_BUFFER"]
REQUEST_TIMEOUT = SETTINGS["REQUEST_TIMEOUT"]
STREAM_TIMEOUT = SETTINGS["REQUEST_STREAM_TIMEOUT"]
SEND_TIMEOUT = SETTINGS['SEND_TIMEOUT']
CONTENT_LENGTH_PATTERN = re.compile(rb"(?i)content-length:\s*(\d+)")
TRANSFER_ENCODING_PATTERN = re.compile(rb"(?i)transfer-encoding:\s*([^\r\n]+)")


def check_socket(func):
    """
    Decorator for checking if socket is an instance of xsocket otherwise an error is raised.
    """    
    def wrapper(cls, sock, *args, **kwargs):
        """
        Checks if socket is an instance of xsocket otherwise an error is raised.
        """
        if not isinstance(sock, xsocket):
            raise SocketIOError(f"Expected an instance of xsocket but got {type(sock)}. Please use `duck.utils.xsocket` module for converting to appropriate type.")
        return func(cls, sock, *args, **kwargs)
    return wrapper
    

class SocketIOError(Exception):
    """
    Raised on socket I/O errors.
    """

class SocketIO:
    """
    Class for doing socket I/O operations like connect, send and receive data through the network.
    """
    @classmethod
    @check_socket
    def connect(cls, sock: xsocket, target: Tuple[str, int], timeout: float = None):
        """
        Connect to a target.
        """
        sock.connect(target, timeout=timeout)
        
    @classmethod
    def close(cls, sock: xsocket, shutdown: bool = True, shutdown_reason: int = socket.SHUT_RDWR, ignore_xsocket_error: bool = False):
        """
        Closes a socket.
        
        Args:
            sock (xsocket): The underlying xsocket object.
            shutdown (bool): Whether to shutdown the socket using `sock.shutdown`.
            shutdown_reason (int): Reason for shutdown.
            ignore_xsocket_error (bool): Whether to ignore xsocket error when closing socket.
        """
        if not ignore_xsocket_error:
            check_socket(sock.close)(shutdown, shutdown_reason)
        else:
            sock.close() # Ommit args because this may be a raw socket.
        
    @classmethod
    @check_socket
    def send(
        cls,
        sock: xsocket,
        data: bytes,
        timeout: float = SEND_TIMEOUT,
        suppress_errors: bool = False,
        ignore_error_list: List[Type[Exception]] = [
            ssl.SSLError,
            BrokenPipeError,
            OSError,
            ConnectionError,
        ],
    ) -> int:
        """
        Sends raw data directly to a client socket.

        Args:
            sock (xsocket): The client xsocket object that will receive the data.
            data (bytes): The data to be sent in bytes.
            timeout (float): Timeout for sending data.
            suppress_errors (bool): If True, suppresses any errors (errors not in `ignore_error_list`) that occur during the sending process. Defaults to False.
            ignore_error_list (List[Type[Exception]]): List of error classes to ignore when raised during data transfer.
        
        Returns:
            int: The number of bytes that has been sent (useful if suppress_errors=True)
            
        Raises:
            BrokenPipeError: If the connection is broken during data transmission.
            Exception: Any other exceptions that occur during the sending process.
        """
        try:
            return sock.send(data, timeout=timeout)
            
        except Exception as e:
            if any([isinstance(e, exc) for exc in ignore_error_list]):
                return
                    
            if not suppress_errors:
                raise e  # Re-raises the error if suppression is not enabled.
            
    @classmethod
    @check_socket
    def receive(cls, sock: xsocket,  timeout: float = REQUEST_TIMEOUT, bufsize: int = SERVER_BUFFER) -> bytes:
        """
        Receive data from the socket.
        
        Args:
            sock (xsocket): The xsocket object to receive data from.
            timeout (float): The timeout in seconds to receive data. Defaults to REQUEST_TIMEOUT set in settings.py.
            bufsize (int): Max number of bytes to read.
                
        Raises:
            TimeoutError: If no data is received within the specified time.
            
        Returns:
            bytes: The received data in bytes.
        """
        return sock.recv(n=bufsize, timeout=timeout)
    
    @classmethod
    @check_socket
    def receive_full_request(cls,
        sock: xsocket,
        timeout: float = REQUEST_TIMEOUT,
        stream_timeout: float = STREAM_TIMEOUT,
     ) -> bytes:
        """
        Receives the complete request data from the socket.
        
        Args:
            sock (xsocket): The underlying xsocket object
            timeout (float): Timeout in seconds to receive the first part of the data. Defaults to REQUEST_TIMEOUT set in settings.py.
            stream_timeout (float): The timeout in seconds to receive the next stream of bytes after the first part has been received.
                This is only used if request is using `chunked` Transfer-Encoding or request doesn't have `Content-Length` header set.
                
        Raises:
            TimeoutError: If no data is received within the first timeout (not stream timeout).
            Exception: Any other exception, e.g. connection errors.
            
        Returns:
            bytes: The received data in bytes.
        """
        # Suppress all other exceptions when receiving all data after headers.
        suppress_errors_after_headers = True
        
        try:
            # Receive the first part of data
            data = cls.receive(sock, timeout=timeout)
        except Exception as e:
            if isinstance(e, TimeoutError):
                # Reraise timeout error.
                raise e # reraise timeout error.
                
            elif isinstance(e, (ConnectionResetError, EOFError, OSError, BlockingIOError)):
                # Return empty bytes
                return b""
            
            else:
                raise e # reraise error.
                
        def receive_data_upto_headers_end(data: bytearray):
            """
            Receives data until all headers have been received.
            
            Raises:
                ConnectionResetError: On connection close.
                TimeoutError: If we receive nothing in certain timeframe.
                Exception: Any unknown exception.
            """
            # Receive data until there is enough \r\n\r\n
            while not b"\r\n\r\n" in data:
                data.extend(cls.receive(sock, timeout=timeout))
        
        def receive_content_using_content_length(data: bytearray, content_length: int):
            """
            Receive more data using the content-length header.
            """
            _, received_content = data.split(b"\r\n\r\n", 1)        
            received_length = len(received_content)
            
            while received_length < content_length:
                try:
                    # Receive data with a request timeout
                    more_data = cls.receive(sock, timeout=timeout)
                    data.extend(more_data)
                    received_length += len(more_data)
                    
                    if not more_data:
                        # Data received is empty, this may mean the client is done sending.
                        break
                    
                except Exception as e:
                    # Suppress all other exceptions when receiving all data after headers.
                    if not suppress_errors_after_headers:
                        raise e # reraise error on content data receive.
                    return # exit loop & function immediately
                    
        def receive_content_using_transfer_encoding(data: bytearray, encoding: bytes):
            """
            Efficiently receive and process data using the 'chunked' transfer-encoding.
            Only 'chunked' is supported.
        
            Args:
                data (bytearray): Mutable bytearray holding already received request data.
                encoding (bytes): Value of the Transfer-Encoding header.
        
            Raises:
                Exception: On invalid chunk sizes or unexpected stream errors.
            """
            if encoding.strip().lower() != b"chunked":
                receive_content_using_streaming_method(data)
                return
        
            _, body = data.split(b"\r\n\r\n", 1)
            body_offset = len(data) - len(body)
        
            while True:
                # Read chunk size line
                while b"\r\n" not in data[body_offset:]:
                    try:
                        more = cls.receive(sock, timeout=stream_timeout)
                        data.extend(more)
                    except Exception as e:
                        # Suppress all other exceptions when receiving all data after headers.
                        if not suppress_errors_after_headers:
                            raise e # reraise error on content data receive.
                        return # exit loop & function immediately
                        
                # Parse chunk size
                try:
                    newline_index = data.index(b"\r\n", body_offset)
                    chunk_size_line = data[body_offset:newline_index]
                    chunk_size = int(chunk_size_line.split(b";")[0].strip(), 16)
                
                except Exception as e:
                    # Invalid chunk size line
                    # Suppress all other exceptions when receiving all data after headers.
                    if not suppress_errors_after_headers:
                        raise e # reraise error on content data receive.
                    return # exit loop & function immediately.
                    
                body_offset = newline_index + 2  # Move past \r\n
        
                if chunk_size == 0:
                    # Final chunk
                    # Receive the trailing \r\n after the final chunk
                    while len(data) < body_offset + 2:
                        try:
                            more = cls.receive(sock, timeout=stream_timeout)
                            data += more
                        except Exception as e:
                            # Suppress all other exceptions when receiving all data after headers.
                            if not suppress_errors_after_headers:
                                raise e # reraise error on content data receive.
                    
                    # Break the loop & exit the function immediately.
                    return
        
                # Receive chunk data + \r\n
                remaining = chunk_size + 2  # chunk data + trailing \r\n
                
                while len(data) - body_offset < remaining:
                    try:
                        more = cls.receive(sock, timeout=stream_timeout)
                        data += more
                    except Exception as e:
                        # Suppress all other exceptions when receiving all data after headers.
                        if not suppress_errors_after_headers:
                            raise e # reraise error on content data receive.
                        return # exit loop & function immediately.
        
                body_offset += remaining  # Move offset past the full chunk
            
        def receive_content_using_streaming_method(data: bytearray):
            """
            Receive data through streaming interval method where if we 
            don't receive data within specific timeout, that means the data is complete.
            """
            while True:
                try:
                    # Receive data with a stream timeout
                    more_data = cls.receive(sock, timeout=stream_timeout)
                    data.extend(more_data)
                    if not more_data:
                        # Data received is empty, this may mean the client is done sending.
                        break
                except Exception as e:
                    # Suppress all other exceptions when receiving all data after headers.
                    if not suppress_errors_after_headers:
                        raise e # reraise error on content data receive.
                    return # exit loop & function immediately
        
        if data:
            # First part of data is not empty
            # Prefer receive_content_using_content_length over receive_content_using_streaming_method, these
            # approaches modify data inplace.
            
            # Modify data to be mutable in nested functions
            data = bytearray(data)
            
            try:
                # Receive until headers are complete.
                receive_data_upto_headers_end(data)
            except Exception as e:
                if not suppress_errors_after_headers:
                    # Errors after headers shouldn't be ignored, what about errors before headers are complete,
                    # obviously we don't ignore such errors.
                    raise e
                return bytes(data) # Just return the received data.    
            
            # From this point, we are receiving request content from here onwards.
            encoding_match = TRANSFER_ENCODING_PATTERN.search(data)
            
            if encoding_match:
                # Receive more content
                receive_content_using_transfer_encoding(data, encoding_match.group(1))
                return bytes(data)
            
            # Try to extract Content-Length using a regex (fast, direct)
            length_match = CONTENT_LENGTH_PATTERN.search(data)
            
            if length_match:
                try:
                    content_length = int(length_match.group(1))
                    receive_content_using_content_length(data, content_length)
                except ValueError:               
                    receive_content_using_streaming_method(data)
            else:
                receive_content_using_streaming_method(data)
            
        # Return the total received data
        return bytes(data)
    
    # Asynchronous implementations
    
    @classmethod
    @check_socket
    async def async_connect(cls, sock: xsocket, target: Tuple[str, int], timeout: float = None):
        """
        Asynchronously connect to a target.
        """
        await sock.async_connect(target, timeout=timeout)
        
    @classmethod
    @check_socket
    async def async_send(
        cls,
        sock: xsocket,
        data: bytes,
        timeout: float = SEND_TIMEOUT,
        suppress_errors: bool = False,
        ignore_error_list: List[Type[Exception]] =  [
            ssl.SSLError,
            BrokenPipeError,
            OSError,
        ],
    ) -> int:
        """
        Asynchronously sends raw data directly to a client socket.

        Args:
            sock (xsocket): The client xsocket object that will receive the data.
            data (bytes): The data to be sent in bytes.
            timeout (float): Timeout for sending data.
            suppress_errors (bool): If True, suppresses any errors (errors not in `ignore_error_list`) that occur during the sending process. Defaults to False.
            ignore_error_list (List[Type[Exception]]): List of error classes to ignore when raised during data transfer.
        
        Returns:
            int: The number of bytes that has been sent (useful if suppress_errors=True)
            
        Raises:
            BrokenPipeError: If the connection is broken during data transmission.
            Exception: Any other exceptions that occur during the sending process.
        """
        try:
            return await sock.async_send(data, timeout=timeout) # sendall is not available in asynchronous mode.
            
        except Exception as e:
            if any([isinstance(e, exc) for exc in ignore_error_list]):
                return
                    
            if not suppress_errors:
                raise e  # Re-raises the error if suppression is not enabled.
            
    @classmethod
    @check_socket
    async def async_receive(cls, sock: xsocket,  timeout: float = REQUEST_TIMEOUT, bufsize: int = SERVER_BUFFER) -> bytes:
        """
        Asynchronously receive data from the socket.
        
        Args:
            sock (xsocket): The xsocket object to receive data from.
            timeout (float): The timeout in seconds to receive data. Defaults to REQUEST_TIMEOUT set in settings.py.
            bufsize (int): Max number of bytes to read.
                
        Raises:
            TimeoutError: If no data is received within the specified time.

        Returns:
            bytes: The received data in bytes.
        """
        return await sock.async_recv(n=bufsize, timeout=timeout)
    
    @classmethod
    @check_socket
    async def async_receive_full_request(cls,
        sock: xsocket,
        timeout: float = REQUEST_TIMEOUT,
        stream_timeout: float = STREAM_TIMEOUT,
     ) -> bytes:
        """
        Asynchronously receives the complete request data from the socket.
        
        Args:
            sock (xsocket): The underlying xsocket object
            timeout (float): Timeout in seconds to receive the first part of the data. Defaults to REQUEST_TIMEOUT set in settings.py.
            stream_timeout (float): The timeout in seconds to receive the next stream of bytes after the first part has been received.
                This is only used if request is using `chunked` Transfer-Encoding or request doesn't have `Content-Length` header set.
                
        Raises:
            TimeoutError: If no data is received within the first timeout (not stream timeout).
            Exception: Any other exception, e.g. connection errors.
            
        Returns:
            bytes: The received data in bytes.
        """
        # Suppress all other exceptions when receiving all data after headers.
        suppress_errors_after_headers = True
        
        try:
            # Receive the first part of data
            data = await cls.async_receive(sock, timeout=timeout)
            
        except Exception as e:
            if isinstance(e, TimeoutError):
                # Reraise timeout error.
                raise e # reraise timeout error.
                
            elif isinstance(e, (ConnectionResetError, EOFError, OSError, BlockingIOError)):
                # Return empty bytes
                return b""
            
            else:
                raise e # reraise error.
                
        async def receive_data_upto_headers_end(data: bytearray):
            """
            Asynchronously receives data until all headers have been received.
            
            Raises:
                ConnectionResetError: On connection close.
                TimeoutError: If we receive nothing in certain timeframe.
                Exception: Any unknown exception.
            """
            # Receive data until there is enough \r\n\r\n
            while not b"\r\n\r\n" in data:
                data.extend(await cls.async_receive(sock, timeout=timeout))
        
        async def receive_content_using_content_length(data: bytearray, content_length: int):
            """
            Asynchronously receives more data using the content-length header.
            """
            _, received_content = data.split(b"\r\n\r\n", 1)        
            received_length = len(received_content)
            
            while received_length < content_length:
                try:
                    # Receive data with a request timeout
                    more_data = await cls.async_receive(sock, timeout=timeout)
                    data.extend(more_data)
                    received_length += len(more_data)
                    
                    if not more_data:
                        # Data received is empty, this may mean the client is done sending.
                        break
                    
                except Exception as e:
                    # Suppress all other exceptions when receiving all data after headers.
                    if not suppress_errors_after_headers:
                        raise e # reraise error on content data receive.
                    return # exit loop & function immediately
                    
        async def receive_content_using_transfer_encoding(data: bytearray, encoding: bytes):
            """
            Asynchronously & efficiently receive and process data using the 'chunked' transfer-encoding.
            Only 'chunked' is supported.
        
            Args:
                data (bytearray): Mutable bytearray holding already received request data.
                encoding (bytes): Value of the Transfer-Encoding header.
        
            Raises:
                Exception: On invalid chunk sizes or unexpected stream errors.
            """
            if encoding.strip().lower() != b"chunked":
                await receive_content_using_streaming_method(data)
                return
        
            _, body = data.split(b"\r\n\r\n", 1)
            body_offset = len(data) - len(body)
        
            while True:
                # Read chunk size line
                while b"\r\n" not in data[body_offset:]:
                    try:
                        more = await cls.async_receive(sock, timeout=stream_timeout)
                        data.extend(more)
                    except Exception as e:
                        # Suppress all other exceptions when receiving all data after headers.
                        if not suppress_errors_after_headers:
                            raise e # reraise error on content data receive.
                        return # exit loop & function immediately
                        
                # Parse chunk size
                try:
                    newline_index = data.index(b"\r\n", body_offset)
                    chunk_size_line = data[body_offset:newline_index]
                    chunk_size = int(chunk_size_line.split(b";")[0].strip(), 16)
                
                except Exception as e:
                    # Invalid chunk size line
                    # Suppress all other exceptions when receiving all data after headers.
                    if not suppress_errors_after_headers:
                        raise e # reraise error on content data receive.
                    return # exit loop & function immediately.
                    
                body_offset = newline_index + 2  # Move past \r\n
        
                if chunk_size == 0:
                    # Final chunk
                    # Receive the trailing \r\n after the final chunk
                    while len(data) < body_offset + 2:
                        try:
                            more = await cls.async_receive(sock, timeout=stream_timeout)
                            data += more
                        except Exception as e:
                            # Suppress all other exceptions when receiving all data after headers.
                            if not suppress_errors_after_headers:
                                raise e # reraise error on content data receive.
                    
                    # Break the loop & exit the function immediately.
                    return
        
                # Receive chunk data + \r\n
                remaining = chunk_size + 2  # chunk data + trailing \r\n
                
                while len(data) - body_offset < remaining:
                    try:
                        more = await cls.async_receive(sock, timeout=stream_timeout)
                        data += more
                    except Exception as e:
                        # Suppress all other exceptions when receiving all data after headers.
                        if not suppress_errors_after_headers:
                            raise e # reraise error on content data receive.
                        return # exit loop & function immediately.
        
                body_offset += remaining  # Move offset past the full chunk
            
        async def receive_content_using_streaming_method(data: bytearray):
            """
            Receive data through streaming interval method where if we 
            don't receive data within specific timeout, that means the data is complete.
            """
            while True:
                try:
                    # Receive data with a stream timeout
                    more_data = await cls.async_receive(sock, timeout=stream_timeout)
                    data.extend(more_data)
                    if not more_data:
                        # Data received is empty, this may mean the client is done sending.
                        break
                except Exception as e:
                    # Suppress all other exceptions when receiving all data after headers.
                    if not suppress_errors_after_headers:
                        raise e # reraise error on content data receive.
                    return # exit loop & function immediately
        
        if data:
            # First part of data is not empty
            # Prefer receive_content_using_content_length over receive_content_using_streaming_method, these
            # approaches modify data inplace.
            
            # Modify data to be mutable in nested functions
            data = bytearray(data)
            
            try:
                # Receive until headers are complete.
                await receive_data_upto_headers_end(data)
            except Exception as e:
                if not suppress_errors_after_headers:
                    # Errors after headers shouldn't be ignored, what about errors before headers are complete,
                    # obviously we don't ignore such errors.
                    raise e
                return bytes(data) # Just return the received data.    
            
            # From this point, we are receiving request content from here onwards.
            encoding_match = TRANSFER_ENCODING_PATTERN.search(data)
            
            if encoding_match:
                # Receive more content
                await receive_content_using_transfer_encoding(data, encoding_match.group(1))
                return bytes(data)
            
            # Try to extract Content-Length using a regex (fast, direct)
            length_match = CONTENT_LENGTH_PATTERN.search(data)
            
            if length_match:
                try:
                    content_length = int(length_match.group(1))
                    await receive_content_using_content_length(data, content_length)
                except ValueError:               
                    await receive_content_using_streaming_method(data)
            else:
                await receive_content_using_streaming_method(data)
            
        # Return the total received data
        return bytes(data)
