"""
Handles the response further after they have been processed.
This includes sending response to client and logging the response.
"""
import ssl
import time
import socket

from typing import (
    Optional,
    Union,
    Callable,
    Dict,
    Type,
    List,
)
from inspect import isasyncgen

from duck.http.request import HttpRequest
from duck.etc.statuscodes import responses
from duck.http.response import (
    BaseResponse,
    HttpResponse,
    StreamingHttpResponse,
)
from duck.contrib.sync import iscoroutinefunction
from duck.settings import SETTINGS
from duck.exceptions.all import AsyncViolationError
from duck.logging import logger
from duck.utils.dateutils import (django_short_local_date, short_local_date,)
from duck.utils.xsocket import xsocket
from duck.utils.xsocket.io import SocketIO
from duck.utils.asyncio.eventloop import SyncFuture


def get_status_code_debug_color(status_code: int) -> str:
    """
    Returns the respective color for the debug message of the status code.
    """
    status = str(status_code)
    
    if status.startswith("1") or status.startswith("2"):
        # informational or success status code respectively
        color = logger.Fore.GREEN
    
    elif status.startswith("3"):
        # Redirectional
        color = logger.Fore.CYAN
    
    elif status.startswith("4"):
        # Client Error
        color = logger.Fore.YELLOW
        
        if status == "403":
            # Forbidden
            color = logger.Fore.RED
    else:
        # Internal Server Error
        color = logger.Fore.RED
        if status == "500":
            color = logger.Fore.MAGENTA
    return color


def get_status_debug_msg(response: HttpResponse, request: HttpRequest) -> Optional[str]:
    """
    Returns a debug message corresponding to an HTTP status code.

    This function is typically used when a request-response lacks an attached
    debug message, but the response carries special meaning that warrants 
    additional debugging information based on the status code.

    Args:
        response (HttpResponse): The HTTP response for which the debug message is required.
        request (HttpRequest): The HTTP request associated with the status code.

    Returns:
        str: A debug message that provides context or explanation for the given status code.
    """
    # exceptional status code that doesnt require debug messages
    final_debug_msg = ""
    
    if response.status_code == 101:
        final_debug_msg += f"Upgrade: {response.get_header('upgrade', 'unknown')}"
        return final_debug_msg
    
    if response.status_code < 300:
        return final_debug_msg
        
    if response.status_code in responses.keys():
        debug_msg, reason = responses[response.status_code]
        
        if request:
            if response.status_code in {301, 302, 307}:
                final_debug_msg += f"{debug_msg}: {request.path} -> {response.get_header('location', 'unknown')}"
            else:
                final_debug_msg += f"{debug_msg}: {request.path}"
        else:
            final_debug_msg += f'{debug_msg}: unknown'
    return final_debug_msg


def get_django_formatted_log(
    response: HttpResponse,
    request: Optional[HttpRequest] = None,
    debug_message: Optional[Union[str, List[str]]] = None,
) -> str:
    """
    Returns a log message formatted similarly to Django logs with color support for various HTTP statuses.

    Args:
        response (HttpResponse): The HTTP response object.
        request (Optional[HttpRequest]): The HTTP request object. Optional, used for adding more detailed log information.
        debug_message (Optional[Union[str, List[str]]] ): A custom debug message or list of messages to append to the log.

    Returns:
        str: The formatted log message with color codes based on the HTTP status.
    
    The log format includes:
     - HTTP status code, with color changes based on success, client errors, redirection, or server errors.
     - Optional request path for 500 errors.
     - Optional debug message if provided.
     - Support for redirections with status codes 301 and 307.
    """
    # Initialize variables
    info = ""
    debug_message = debug_message or ""
    reset = logger.Style.RESET_ALL
    color = get_status_code_debug_color(response.status_code)
    h2_handling = False
    
    if request and request.request_store.get("h2_handling") == True:
        h2_handling = True
    
    # Add optional debug message if available
    if debug_message:
        debug_message = "\n".join(debug_message) if instance(debug_message, list) else debug_message
        info += reset + debug_message.strip() + "\n"
    else:
        debug_message = get_status_debug_msg(response, request)
        if debug_message:
            info += reset + debug_message + "\n"
    
    # Add the main log information with date, status code, content size, and request info
    if request and not request.topheader:
        if not request.http_version:
            request.http_version = "HTTP/1.1"
        request.topheader = f"{request.method or 'UNKNOWN_METHOD'} {request.fullpath} {request.http_version}"
    topheader = request.topheader if request else ""
    
    if topheader and h2_handling:
        meth, path, httpversion = topheader.split(' ', 2)
        topheader = " ".join([meth.strip(), path.strip(), "HTTP/2"])
        
    info += (
        f"[{django_short_local_date()}] {color}"
        f'"{topheader}" {response.status_code} '
        f"{response.content_obj.size}"
    )
    return info + reset  # Restore default color


def get_duck_formatted_log(
    response: HttpResponse,
    request: Optional[HttpRequest] = None,
    debug_message: Optional[Union[str, List[str]]]  = None,
) -> str:
    """
    This returns default duck formatted log with color support.

    Args:
        response (HttpResponse): The http response object.
        request (Optional[HttpRequest]): The http request object.
        debug_message (Optional[Union[str, List[str]]]): Custom debug message or list of messages to add to log.
    """
    info = ""
    debug_message = debug_message or ""
    reset = logger.Style.RESET_ALL
    color = get_status_code_debug_color(response.status_code)
    addr = ("unknown", "unknown")
    h2_handling = False
    
    if request and request.request_store.get("h2_handling") == True:
        h2_handling = True
    
    if request and request.client_address:
        addr = request.client_address
    
    if request and not request.topheader:
        if not request.http_version:
            request.http_version = "HTTP/1.1"
        request.topheader = f"{request.method or 'UNKNOWN_METHOD'} {request.fullpath} {request.http_version}"
    topheader = request.topheader if request else ""
    
    if topheader and h2_handling:
        meth, path, httpversion = topheader.split(' ', 2)
        topheader = " ".join([meth.strip(), path.strip(), "HTTP/2"])
        
    info = (
        f'[{short_local_date()}] {color}"{topheader}" '
        f"{response.content_obj.size}"
    )
    
    info += f"\n  {reset}├── ADDR {list(addr)} "
    
    if not debug_message:
        # Obtain debug message if not present.
        debug_message = get_status_debug_msg(response, request)
        
    if debug_message:
        info += f"\n  ├── {response.payload_obj.status_message} [{response.payload_obj.status_code}] "
        if isinstance(debug_message, list):
            for index, msg in enumerate(debug_message):
                if not index == len(debug_message) - 1:
                    info += f"\n  ├── {msg}"
                else:
                    # last debug_message in list
                    info += f"\n  {reset}└── {msg}"
        else:
                info += f"\n  {reset}└── {debug_message} "
    else:
        info += f"\n  {reset}└── {response.payload_obj.status_message} [{response.payload_obj.status_code}] "
    
    return info + reset  # Restore default color (default)


def log_response(
    response: Union[BaseResponse, HttpResponse],
    request: Optional[HttpRequest] = None,
    debug_message: Optional[Union[str, List[str]]]  = None,
) -> None:
    """
    Logs a response to the console.

    Args:
        response (Union[BaseResponse, HttpResponse]): The http response object.
        request (Optional[Request]): The http request object.
        debug_message (Optional[Union[str, List[str]]]): Message or list of messages to display along the response, usually middleware error debug message.
    """
    logdata = ""
    
    if SETTINGS["USE_DJANGO"]:
        if SETTINGS['PREFERRED_LOG_STYLE'] == "duck":
            logdata = get_duck_formatted_log(response, request, debug_message)
            # Add newline to separate requests for duck formatted logs
            logdata += "\n"  
        else:
            logdata = get_django_formatted_log(response, request, debug_message)
    else:
        if SETTINGS['PREFERRED_LOG_STYLE'] == "django":
            logdata = get_django_formatted_log(response, request, debug_message)
        else:
            logdata = get_duck_formatted_log(response, request, debug_message)
            # Add newline to separate requests for duck formatted logs
            logdata += "\n"  
    
    # Log response, use_colors=False to because logdata already has colors
    logger.log_raw(logdata, use_colors=False)


class ResponseHandler:
    """
    Handles sending processed responses to clients via socket communication.
    This class contains methods for sending raw data and HTTP responses, 
    along with optional error handling and logging.
    """
    
    @classmethod
    def auto_log_response(cls, response, request):
        """
        Logs a response to the console, considering middleware errors and any other issues. This
        automatically creates debug messages (if applicable).
        
        Notes:
        - Nothing will be logged if response is `None`.
        """
        if response:
            debug_message = ""
            if request and hasattr(request, "META"):
                failed_middleware = request.META.get("FAILED_MIDDLEWARE")
                if failed_middleware and response.status_code != 500:
                    # Do not log debug message for internal server errors (status code 500).
                    debug_message = failed_middleware.debug_message
                else:
                    debug_message = request.META.get("DEBUG_MESSAGE", "")
            
            # Log the response, including debug messages if available
            log_response(
                response,
                request=request,
                debug_message=debug_message,
            )
    
    @classmethod
    def close_streaming_response(cls, response):
        """
        Synchronously closes streaming response `stream` usually 
        after response sending.
        """
        if isinstance(response, StreamingHttpResponse):
            if hasattr(response, "stream") and hasattr(response.stream, "close"):
                # Close stream if we are done.
                response.stream.close()
    
    @classmethod
    async def async_close_streaming_response(cls, response):
        """
        Asynchronously closes streaming response `stream` usually 
        after response sending.
        """
        if isinstance(response, StreamingHttpResponse):
            if hasattr(response, "stream") and hasattr(response.stream, "close"):
                # Close stream if we are done.
                if not iscoroutinefunction(response.stream.close):
                    raise AsyncViolationError(
                        f"Method `{response.stream}.close` must be an asynchronous function."
                    )
                await response.stream.close()
                
    def send_response(
        self,
        response: Union[BaseResponse, HttpResponse],
        sock: xsocket,
        request: Optional[HttpRequest] = None,
        disable_logging: bool = False,
        suppress_errors: bool = False,
        strictly_http1: bool = False,
    ) -> None:
        """
        Sends an HTTP response to the client socket, optionally logging the response.

        Args:
            response (Union[BaseResponse, HttpResponse]): The HTTP response object containing the response data.
            sock (xsocket): The client socket object to which the response will be sent.
            request (Optional[HttpRequest]): The request object associated with the response. Used for logging and debugging purposes.
            disable_logging (bool): If True, disables logging of the response. Defaults to False.
            suppress_errors (bool): If True, suppresses any errors that occur during the sending process (only sending data). Defaults to False.
            strictly_http1 (bool): Strictly send response using `HTTP/2`, even if `HTTP/2` is enabled.
            
        Raises:
            Exception: If there is an error during the data sending process (e.g., socket errors), unless suppressed.
        
        This method calls `SocketIO.send` to transmit the raw response data to the client and 
        performs logging if `disable_logging` is False. If the request object contains 
        debug information or failed middleware details, they are included in the logs.
        """
        h2_handling = False
        
        if not strictly_http1 and hasattr(sock, 'h2_protocol'):
            if request and request.request_store.get('h2_handling') == False:
                pass
            else:
                # Set H2 handling to True
                h2_handling = True
        
        if h2_handling:
            stream_id = request.request_store.get("stream_id") if request else None
        
            if not stream_id:
                raise TypeError(
                    "HTTP/2 appears to be enabled on the provided socket, "
                    "but no 'stream_id' was found in `request.request_store`. "
                    "Use the `send_http2_response` method directly if you're managing the stream manually."
                )
            
            # H2 Protocol already handles close_streaming_response
            sync_future = self.send_http2_response(
                response=response,
                stream_id=stream_id,
                sock=sock,
                request=request,
                disable_logging=disable_logging,
                suppress_errors=suppress_errors,
                return_future=True,
            )
            
            # Wait for this action to complete.
            _ = sync_future.result()
            return # No further processing
        
        # Explicitly send response
        try:
            self._send_response(response, sock, suppress_errors=suppress_errors)
        
        except (BrokenPipeError, ConnectionResetError):
             # Client disconnected
             return
        
        finally:
            # Close streaming response if it is one
            type(self).close_streaming_response(response)
            
        if not disable_logging:
            # Log response (if applicable)
            type(self).auto_log_response(response, request)
            
    def send_http2_response(
        self,
        response: Union[BaseResponse, HttpResponse],
        stream_id: int,
        sock: xsocket,
        request: Optional[HttpRequest] = None,
        disable_logging: bool = False,
        suppress_errors: bool = False,
        return_future: bool = False,
    ) -> Optional[SyncFuture]:
        """
        This sends an HTTP/2 response to the H2Connection.
        
        Notes:
        - This sends data asynchronously but the difference between this method and
          `async_send_response` is that it submits the coroutine for sending response to `AsyncioLoopManager`
          and returns a `SyncFuture` you can wait for.
        
        Args:
            response (Union[BaseResponse, HttpResponse]): The HTTP response object containing the response data.
            stream_id (int): The target H2 stream ID.
            request (Optional[HttpRequest]): The request object associated with the response. Used for logging and debugging purposes.
            disable_logging (bool): If True, disables logging of the response. Defaults to False.
            suppress_errors (bool): If True, suppresses any errors that occur during the sending process (only sending data). Defaults to False.
            return_future (bool): Whether to return sync future.
            
        Returns:
            Optional[SyncFuture]: A synchronous future you can wait for upon response send completion.
            
        Raises:
            AttributeError: If the xsocket doesn't have the attribute `h2_protocol`.
            ValueError: If request is not set to be be handled with HTTP/2.
            DisallowedAction: If ASYNC_HANDLING is True in settings.
            Exception: If there is an error during the data sending process (e.g., socket errors), unless suppressed.
        """
        if not hasattr(sock, 'h2_protocol'):
            raise AttributeError("The provided socket seem to have no associated HTTP/2 connection, socket should have attribute `h2_protocol` set.")
        
        if request and request.request_store.get("h2_handling") == False:
            raise ValueError("The provided socket seem to have HTTP/2 connection, but the key `h2_handling` in `request.request_store` is False.")
        
        protocol = sock.h2_protocol
        
        # Send response according to H2 Protocol
        return protocol.send_response(
            response,
            stream_id,
            request,
            disable_logging,
            suppress_errors,
            return_future,
        )
    
    def _send_response(
        self,
        response: Union[BaseResponse, HttpResponse],
        sock: xsocket,
        suppress_errors: bool = False,
    ):
       """
        Sends an HTTP response to the client socket.
        
        Args:
            response (Union[BaseResponse, HttpResponse]): The HTTP response object containing the response data.
            sock (xsocket): The client socket object to which the response will be sent.
            suppress_errors (bool): If True, suppresses any errors that occur during the sending process. Defaults to False.

        Raises:
            Exception: If there is an error during the data sending process (e.g., socket errors), unless suppressed.
       """
       try:
           if not isinstance(response, StreamingHttpResponse):
                SocketIO.send(
                    sock=sock,
                    data=response.raw,
                    suppress_errors=False,
                )  # Send the whole response to the client
           else:
                SocketIO.send(
                    sock=sock,
                    data=response.payload_obj.raw + b'\r\n\r\n',
                    suppress_errors=False,
                )  # Send the response payload
                
                content_length = 0
                
                for chunk in response.iter_content():
                     content_length += len(chunk)
                     
                     if isinstance(chunk, str):
                         chunk = bytes(chunk, "utf-8")
                     
                     SocketIO.send(
                         sock=sock,
                         data=chunk,
                         suppress_errors=False,
                      )  # Send the whole response to the client.
                      
                # Set a custom content size for streaming responses, which may not match the actual size 
                # of the current content. This size represents the correct total size of the content 
                # after being fully sent to the client. Setting this enables accurate logging of 
                # the content size.
                response.content_obj.set_fake_size(content_length)   
       except Exception as e:
            if not suppress_errors:
                raise e  # Re-raises the error if suppression is not enabled.
    
    # ASYNCHRONOUS IMPLEMENTATIONS
    
    async def async_send_response(
        self,
        response: Union[BaseResponse, HttpResponse],
        sock: xsocket,
        request: Optional[HttpRequest] = None,
        disable_logging: bool = False,
        suppress_errors: bool = False,
        strictly_http1: bool = False,
    ) -> None:
        """
        Asynchronously sends an HTTP response to the client socket, optionally logging the response.

        Args:
            response (Union[BaseResponse, HttpResponse]): The HTTP response object containing the response data.
            sock (xsocket): The client socket object to which the response will be sent.
            request (Optional[HttpRequest]): The request object associated with the response. Used for logging and debugging purposes.
            disable_logging (bool): If True, disables logging of the response. Defaults to False.
            suppress_errors (bool): If True, suppresses any errors that occur during the sending process (only sending data). Defaults to False.
            strictly_http1 (bool): Strictly send response using `HTTP/2`, even if `HTTP/2` is enabled.
            
        Raises:
            Exception: If there is an error during the data sending process (e.g., socket errors), unless suppressed.
        
        This method calls `SocketIO.send` to transmit the raw response data to the client and 
        performs logging if `disable_logging` is False. If the request object contains 
        debug information or failed middleware details, they are included in the logs.
        """
        h2_handling = False
        
        if not strictly_http1 and hasattr(sock, 'h2_protocol'):
            if request and request.request_store.get('h2_handling') == False:
                pass
            else:
                # Set H2 handling to True
                h2_handling = True
        
        if h2_handling:
            stream_id = request.request_store.get("stream_id") if request else None
        
            if not stream_id:
                raise TypeError(
                    "HTTP/2 appears to be enabled on the provided socket, "
                    "but no 'stream_id' was found in `request.request_store`. "
                    "Use the `send_http2_response` method directly if you're managing the stream manually."
                )
            
            # H2 Protocol already handles close_streaming_response
            try:
                await self.async_send_http2_response(
                    response=response,
                    stream_id=stream_id,
                    sock=sock,
                    request=request,
                    disable_logging=disable_logging,
                    suppress_errors=suppress_errors,
                )
            except TimeoutError:
                # Timeout whilst sending
                pass
                
            return # No further processing
        
        # Explicitly send response
        try:
            await self._async_send_response(response, sock, suppress_errors=suppress_errors)
        
        except (BrokenPipeError, ConnectionResetError):
             # Client disconnected
             return
        
        finally:
            # Close streaming response if it is one
            await type(self).async_close_streaming_response(response)
        
        if not disable_logging:
            # Log response (if applicable)
            type(self).auto_log_response(response, request)
              
    async def async_send_http2_response(
        self,
        response: Union[BaseResponse, HttpResponse],
        stream_id: int,
        sock: xsocket,
        request: Optional[HttpRequest] = None,
        disable_logging: bool = False,
        suppress_errors: bool = False,
    ) -> None:
        """
        Asynchronously sends an HTTP/2 response to the H2Connection.
        
        Args:
            response (Union[BaseResponse, HttpResponse]): The HTTP response object containing the response data.
            stream_id (int): The target H2 stream ID.
            sock (xsocket): The client socket object to which the response will be sent.
            request (Optional[HttpRequest]): The request object associated with the response. Used for logging and debugging purposes.
            disable_logging (bool): If True, disables logging of the response. Defaults to False.
            suppress_errors (bool): If True, suppresses any errors that occur during the sending process (only sending data). Defaults to False.

        Raises:
            Exception: If there is an error during the data sending process (e.g., socket errors), unless suppressed.
        
        This method calls `SocketIO.send` to transmit the raw response data to the client and 
        performs logging if `disable_logging` is False. If the request object contains 
        debug information or failed middleware details, they are included in the logs.
        """
        if not hasattr(sock, 'h2_protocol'):
            raise AttributeError("The provided socket seem to have no associated HTTP/2 connection, socket should have attribute `h2_protocol` set.")
        
        if request and request.request_store.get("h2_handling") == False:
            raise ValueError("The provided socket seem to have HTTP/2 connection, but the key `h2_handling` in `request.request_store` is False.")
        
        protocol = sock.h2_protocol
        
        # Send response according to H2 Protocol
        await protocol.async_send_response(
            response,
            stream_id,
            request,
            disable_logging,
            suppress_errors,
        )
        
    async def _async_send_response(
        self,
        response: Union[BaseResponse, HttpResponse],
        sock: xsocket,
        suppress_errors: bool = False,
    ):
       """
       Asynchronously sends an HTTP response to the client socket.
        
        Args:
            response (Union[BaseResponse, HttpResponse]): The HTTP response object containing the response data.
            sock (xsocket): The client socket object to which the response will be sent.
            suppress_errors (bool): If True, suppresses any errors that occur during the sending process. Defaults to False.

        Raises:
            Exception: If there is an error during the data sending process (e.g., socket errors), unless suppressed.
       """
       try:
           if not isinstance(response, StreamingHttpResponse):
                await SocketIO.async_send(
                    sock=sock,
                    data=response.raw,
                    suppress_errors=False,
                )  # Send the whole response to the client
           else:
                await SocketIO.async_send(
                    sock=sock,
                    data=response.payload_obj.raw + b'\r\n\r\n',
                    suppress_errors=False,
                )  # Send the response payload
                
                content_length = 0
                content = response.async_iter_content()
                
                if not isasyncgen(content):
                    # The content is not an async generator so lets await the result.
                    content = await content
            
                if not isasyncgen(content):
                    for chunk in content:
                         content_length += len(chunk)
                         
                         if isinstance(chunk, str):
                             chunk = bytes(chunk, "utf-8")
                         
                         await SocketIO.async_send(
                             sock=sock,
                             data=chunk,
                             suppress_errors=False,
                          )  # Send the whole response to the client.
                else:
                    async for chunk in content:
                         content_length += len(chunk)
                         
                         if isinstance(chunk, str):
                             chunk = bytes(chunk, "utf-8")
                         
                         await SocketIO.async_send(
                             sock=sock,
                             data=chunk,
                             suppress_errors=False,
                          )  # Send the whole response to the client.
                          
                # Set a custom content size for streaming responses, which may not match the actual size 
                # of the current content. This size represents the correct total size of the content 
                # after being fully sent to the client. Setting this enables accurate logging of 
                # the content size.
                response.content_obj.set_fake_size(content_length)   
       except Exception as e:
            if not suppress_errors:
                raise e  # Re-raises the error if suppression is not enabled.


# Create an instance for use.
response_handler = ResponseHandler()
