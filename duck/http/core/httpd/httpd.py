"""
All utilities and tools a server needs to startup.

This module provides the necessary components for initializing and running a server, including 
handling requests, managing timeouts, and logging.
"""
import re
import ssl
import time
import select
import socket
import asyncio
import threading
import platform

from functools import partial
from typing import (
    Optional,
    Tuple,
    Coroutine,
    Union,
    Callable,
    Dict,
)
from duck.contrib.responses import (
    simple_response,
    template_response,
)
from duck.http.core.handler import (
    response_handler,
    log_response,
)
from duck.settings import SETTINGS
from duck.settings.loaded import SettingsLoaded
from duck.exceptions.all import SettingsError
from duck.logging import logger
from duck.meta import Meta
from duck.http.core.processor import (
    AsyncRequestProcessor,
    RequestProcessor,
)
from duck.http.request import HttpRequest
from duck.http.request_data import (
    RawRequestData,
    RequestData,
)
from duck.http.response import (
    HttpRequestTimeoutResponse,
    HttpResponse,
)
from duck.contrib.responses.errors import get_timeout_error_response
from duck.utils.ssl import is_ssl_data
from duck.utils.xsocket import (xsocket, ssl_xsocket, create_xsocket)
from duck.utils.xsocket.io import SocketIO 


KEEP_ALIVE_PATTERN = re.compile(rb"(?i)\bConnection\s*:\s*keep\s*-?\s*alive\b")
KEEP_ALIVE_TIMEOUT = SETTINGS["KEEP_ALIVE_TIMEOUT"]
CONNECTION_MODE = SETTINGS["CONNECTION_MODE"]
SSL_HANDSHAKE_TIMEOUT = 0.3 # in seconds


def call_request_handling_executor(task: Union[threading.Thread, Coroutine]):
    """
    This calls the request handling executor with the provided task (thread or coroutine) and the 
    request handling executor keyword arguments set in settings.py.
    """
    SettingsLoaded.REQUEST_HANDLING_TASK_EXECUTOR.execute(task) # execute thread or coroutine.


class BaseServer:
    """
    Base server class containing core server definitions and behaviors.
    
    Features:
    - HTTP Keep-Alive support for persistent connections.
    - Support for incoming requests using chunked Transfer-Encoding.
    - Synchronous + Asynchronous request handling using `WSGI` or `ASGI`.'
    
    Request Flow:
    1. `start_server` is called.
    2. `accept_and_handle` is called next.
    3. `handle_conn` is called - Full request is received here.
    4. `process_data` is then called - RequestData instance is processed, there is proper socket closure here.
    5. `handle_request_data` is then called last - The RequestData instance is processed further. This func
          is called by `process_data` and no socket closure is done here.
    """
    def __init__(
        self,
        addr: Tuple[str, int],
        application: Union["App", "MicroApp"],
        domain: str = None,
        uses_ipv6: bool = False,
        enable_ssl: bool = False,
        ssl_params: Optional[Dict] = None,
        no_logs: bool = False,
    ):
        """
        Initialise the server instance.

        Args:
            addr (Tuple[str, int]): Tuple of address and port.
            application (Union[App, MicroApp]): The application that is using this server. Can be either duck main app or micro app.
            domain (str): The server domain.
            uses_ipv6 (bool): Whether If the server is on (IPV6)
            enable_ssl (bool): Whether to enable `HTTPS`.
            ssl_params (Optional[Dict]): Dictionary containing ssl parameters to parse to SSLSocket. If None, default ones will be used.
            no_logs (bool): Whether to disable logging.
        """
        from duck.app.app import App
        from duck.app.microapp import MicroApp
        from duck.etc.ssl_defaults import SSL_DEFAULTS
        
        assert isinstance(addr, tuple), "Argument addr should be an instance of tuple"
        assert len(addr) == 2, "Argument addr should be a tuple of length 2"
        assert isinstance(addr[0], str), "Argument addr[0] should be an instance of str"
        assert isinstance(addr[1], int), "Argument addr[1] should be an instance of int"
        assert isinstance(application, (App, MicroApp)), f"Argument application should be an instance of App or MicroApp, not {type(application)}"
        assert ssl_params is None or isinstance(ssl_params, dict), f"Argument ssl_params should be an instance of dictionary, not {type(ssl_params)}"
        
        # Create some socket object
        self.__sock = None
        self.sock: xsocket = create_xsocket(family=socket.AF_INET6 if uses_ipv6 else socket.AF_INET)
        
        # Set some attributes.
        self.addr = addr
        self.application = application
        self.domain = domain
        self.uses_ipv6 = uses_ipv6
        self.enable_ssl = enable_ssl
        self.ssl_params = ssl_params or SSL_DEFAULTS
        self.no_logs = no_logs
        self.running: bool = False
    
    @property
    def sock(self):
        return self.__sock
    
    @sock.setter
    def sock(self, s: xsocket):
         if not isinstance(s, xsocket):
             raise TypeError(f"The provided argument must be an instance of `xsocket` not {type(s)}")
         self.__sock = s
         
    @property
    def running(self):
        return self.__running

    @running.setter
    def running(self, state: bool):
        self.__running = state

    def stop_server(self, log_to_console: bool = True):
        """
        Stops the http(s) server.
        
        Args:
            log_to_console (bool): Log the message that the sever stoped. Defaults to True.
        """
        bold_start = "\033[1m"
        bold_end = "\033[0m"
        
        # Set running to False
        self.running = False
        
        # Close server socket.
        SocketIO.close(self.sock, shutdown=False) # Avoid shutting down server socket, this may raise an error.
        
        if log_to_console: # log message indicating server stopped.
            logger.log(
                f"{bold_start}Duck server stopped!{bold_end}",
                level=logger.INFO,
                custom_color=logger.Fore.MAGENTA,
            )
            
    def start_server(self):
        """
        Starts the `HTTP(S)` server.
        """
        host, port = self.addr
        
        if SETTINGS["DEBUG"]:
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
        self.sock.bind(self.addr)  # bind socket to (address, port)
        self.sock.listen(SETTINGS["REQUESTS_BACKLOG"]) # 200 by default
        
        # Prepare server setup
        duck_host = self.domain or Meta.get_metadata("DUCK_SERVER_HOST")
        duck_host = (list(duck_host)[0] if isinstance(duck_host, tuple) else duck_host or "localhost")
        server_url = "https" if self.enable_ssl else "http"
        server_url += f"://{duck_host}:{port}"
        server_gateway = "WSGI" if not SETTINGS['ASYNC_HANDLING'] else "ASGI"
        
        if not self.no_logs:
            if SETTINGS["DEBUG"]:
                logger.log(f"Started Duck {server_gateway} Server on {server_url}", level=logger.DEBUG)
            else:
                logger.log(
                    f"Started Duck Pro {server_gateway} Server on {server_url}\n "
                    f" └── This is a production server, stay secure! ",
                     level=logger.DEBUG,
                 )
                 
                if SETTINGS['SUPPORT_HTTP_2'] or SETTINGS['ASYNC_HANDLING']:
                     if SETTINGS['ASYNC_LOOP'] != "uvloop" and (platform.system() or "").lower() != "windows":
                         logger.log("Default asyncio loop enabled", level=logger.WARNING)
                         logger.log("Loop: 'uvloop' is recommended for better performance", level=logger.WARNING)
                         
        # Listen and set the server in running state
        self.running = True
        
        # Set server socket to non-blocking mode
        self.sock.setblocking(False)
        
        # Listen and accept incoming connections
        while self.running:
            try:
                # Accept incoming connections
                sock = None
                server = self.sock
                
                # Wait until the server socket is ready (timeout = 1s)
                ready, _, _ = select.select([server], [], [], 1.0)
                
                if server in ready:
                    sock = self.accept_and_handle()
                
            except ConnectionResetError:
                pass
        
            except Exception as e:
                # Close socket immediately.
                if sock:
                    SocketIO.close(sock, ignore_xsocket_error=True)
                    
                # Log the exception if logging allowed.
                if not self.no_logs and SETTINGS['DEBUG']:
                    if self.running:
                        # Explicitly log if server still in running state
                        logger.log_exception(e)
                    
    def accept_and_handle(self) -> socket.socket:
        """
        Accepts and handle IPV4/IPV6 connection.
        
        Returns:
            xsocket: The client socket instance.
        """
        flowinfo, scopeid = None, None
        async_handling = SETTINGS['ASYNC_HANDLING']
        
        if self.uses_ipv6:
            accept_info = self.sock.accept()
            sock, [ip, port, flowinfo, scopeid] = accept_info
            addr = (ip, port)
        else:
            sock, addr = self.sock.accept()
        
        # Set the IP & Port
        ip, port = addr
        
        async def async_task(sock):
            """
            Async way of handling the connection.
            """
            # Set socket blocking to False if set to True.
            sock.setblocking(False)
            
            try:
                if self.enable_ssl:
                    # Wrap & do handshake.
                    sock: ssl_xsocket = self.ssl_wrap_socket(sock)
                    await sock.async_do_handshake(timeout=SSL_HANDSHAKE_TIMEOUT)
                
                else:
                    # Convert sock object to xsocket.
                    sock: xsocket = xsocket(sock)
                
                # Handle connection synchronously.
                await self.async_handle_conn(sock, addr, flowinfo, scopeid)
                 
            except (ConnectionResetError, TimeoutError):
                # Handshake timed out or connection reset
                pass
                
            except ssl.SSLError as e:
                # Wrong protocol used e.g., https on http or vice versa
                if not self.no_logs and SETTINGS["VERBOSE_LOGGING"] and SETTINGS["DEBUG"]:
                    if "HTTP_REQUEST" in str(e):
                        logger.log(f"Client may be trying to connect with HTTPS on HTTP server or vice-versa: {e}\n", level=logger.WARNING)
            
            except Exception as e:
                if not self.no_logs:
                    # Log exception if allowed.
                    logger.log_exception(e)
            
            finally:
                # Close client socket if not closed
                SocketIO.close(sock, ignore_xsocket_error=True)
                
        def thread_task(sock):
            """
            Sync way of handling the connection.
            """
            sock.setblocking(True)
            
            try:
                if self.enable_ssl:
                    # Wrap & do handshake.
                    sock: ssl_xsocket = self.ssl_wrap_socket(sock)
                    sock.do_handshake(timeout=SSL_HANDSHAKE_TIMEOUT)
                else:
                    # Convert sock object to xsocket.
                    sock: xsocket = xsocket(sock)
                    
                # Handle connection synchronously.
                self.handle_conn(sock, addr, flowinfo, scopeid)
                 
            except (ConnectionResetError, TimeoutError):
                # Handshake timed out or connection reset
                pass
                
            except ssl.SSLError as e:
                # Wrong protocol used e.g., https on http or vice versa
                if not self.no_logs and SETTINGS["VERBOSE_LOGGING"] and SETTINGS["DEBUG"]:
                    if "HTTP_REQUEST" in str(e):
                        logger.log(f"Client may be trying to connect with HTTPS on HTTP server or vice-versa: {e}\n", level=logger.WARNING)
            
            except Exception as e:
                if not self.no_logs:
                    # Log exception if allowed.
                    logger.log_exception(e)
            
            finally:
                # Close client socket if not closed
                SocketIO.close(sock, ignore_xsocket_error=True)  
        
        # Decide how to handle the connection.
        if async_handling:
            async_task = async_task(sock)
            call_request_handling_executor(async_task)
        else:
            thread_task = partial(thread_task, sock)
            thread_task.name = f"client-{ip}@{port}"
            call_request_handling_executor(thread_task)
        
        # Finally return the client socket
        return sock
        
    def handle_conn(
        self,
        sock: xsocket,
        addr: Tuple[str, int],
        flowinfo: Optional = None,
        scopeid: Optional = None,
    ) -> None:
        """
        Main entry point to handle new connection (supports both ipv6 and ipv4).

        Args:
            sock (xsocket): The client socket object.
            addr (Tuple[str, int]): Client ip address and port.
            flowinfo (Optional): Flow info if IPv6.
            scopeid (Optional): Scope id if IPv6.
        """
        sock.addr = addr
        sock.flowinfo = flowinfo
        sock.scopeid = scopeid
        
        try:
            # Receive the full request (in bytes)
            data = SocketIO.receive_full_request(sock)
        except TimeoutError:
            # For the first request, client took too long to respond.
            self.do_request_timeout(sock, addr)
            return
        
        if not data:
            # Client sent an empty request, terminate the connection immediately
            SocketIO.close(sock)
            return
        
        # Process data/request
        self.process_data(sock, addr, RawRequestData(data))
        
        # Close client socket just in case it is not closed
        SocketIO.close(sock)
    
    def process_data(
        self,
        sock: xsocket,
        addr: Tuple[str, int],
        request_data: RequestData,
    ) -> None:
        """
        Process and handle the request dynamically.
        """
        # Continue with data processing.
        data = request_data.data if isinstance(request_data, RawRequestData) else request_data.content
        
        if is_ssl_data(data):
            if SETTINGS['DEBUG']:
                logger.log(
                    "Data should be decoded at this point but it seems like it's ssl data",
                    level=logger.WARNING,
                )
                logger.log(f"Client may be trying to connect with https on http server or vice-versa\n", level=logger.WARNING)
            return None
            
        try:
            self.handle_request_data(sock, addr, request_data)
        except Exception as e:
            # Log the error message
            logger.log_exception(e)
        
        finally:
            # Check if client wants a keep alive connection
            # Only handle keep alive connection if the server supports it.
            try:
                if KEEP_ALIVE_PATTERN.search(request_data.data.split(b"\r\n\r\n")[0]):  # target headers only
                    if CONNECTION_MODE == "keep-alive":
                        # Server supports keep alive
                        self.handle_keep_alive_conn(sock, addr)
            finally:
                # Finally close the socket if everything is finished
                SocketIO.close(sock)
                    
    def handle_keep_alive_conn(
        self,
        sock: xsocket,
        addr: Tuple[str, int],
    ) -> None:
        """
        Processes and handles keep alive connection.
        """
        data: bytes = b""
        
        # Assume the client wants keep alive to run forever until explicitly stated to end it.
        while True:
            try:
                # Receive client request with a timeout.
                data = SocketIO.receive_full_request(sock=sock, timeout=KEEP_ALIVE_TIMEOUT)
                
                if not data:
                    # Client sent nothing or closed connection
                    # End the keep alive data exchange immediately
                    break
                
                # Process and handle the complete request using appropriate WSGI
                self.handle_request_data(sock, addr, RawRequestData(data))
            
            except TimeoutError:
                # Client sent nothing in expected time it was suppose to
                # Close connection immediately
                break
            
            except Exception as e:
                # Encountered an unknown exception, log that exception right away
                logger.log_exception(e)
            
            finally:
                # After every keep alive cycle, check if client still wants to continue with
                # the connection or terminate immediately
                
                if KEEP_ALIVE_PATTERN.search(data.split(b"\r\n\r\n")[0]):
                    # client seem to like to continue with keep alive connection
                    if CONNECTION_MODE == "keep-alive":
                        # keep connection alive
                        continue
                    else:
                        break
                else:
                    # Client would like to terminate keep alive connection.
                    break
                    
    def do_request_timeout(
        self,
        sock: xsocket,
        addr: Tuple[str, int],
    ):
        """
        Sends request timeout response to client and close connection.

        Args:
            sock (xsocket): Client socket object
            addr (Tuple[str, int]): Client ip address and port.
        """
        # Send timeout error message to client.
        timeout_response = get_timeout_error_response(timeout=SETTINGS["REQUEST_TIMEOUT"])
        
        SettingsLoaded.WSGI.finalize_response(timeout_response, request=None)
        
        # Send timeout response
        response_handler.send_response(
            timeout_response,
            sock=sock,
            disable_logging=self.no_logs,
         )
        
        # Close client socket immediately
        SocketIO.close(sock)
        
    def handle_request_data(
        self,
        sock: xsocket,
        addr: Tuple[str, int],
        request_data: RequestData,
    ) -> None:
        """
        This processes the request using WSGI application callable.

        Args:
            sock (xsocket): Client Socket object
            addr (Tuple[str, int]): Tuple for ip and port from where this request is coming from, ie Client addr
            request_data (RequestData): The request data object
        """
        handle_wsgi_request = SettingsLoaded.WSGI
        
        handle_wsgi_request(
            self.application,
            sock,
            addr,
            request_data,
        )
    
    # ASYNCHRONOUS IMPLEMENTATIONS
    
    async def async_handle_conn(
        self,
        sock: xsocket,
        addr: Tuple[str, int],
        flowinfo: Optional = None,
        scopeid: Optional = None,
    ) -> None:
        """
        Main entry point to handle new connection asynchronously (supports both ipv6 and ipv4).

        Args:
            sock (xsocket): The client socket object.
            addr (Tuple[str, int]): Client ip address and port.
            flowinfo (Optional): Flow info if IPv6.
            scopeid (Optional): Scope id if IPv6.
        """
        sock.addr = addr
        sock.flowinfo = flowinfo
        sock.scopeid = scopeid
        
        try:
            # Receive the full request (in bytes)
            data = await SocketIO.async_receive_full_request(sock=sock)
        
        except TimeoutError:
            # For the first request, client took too long to respond.
            await self.async_do_request_timeout(sock, addr)
            return
        
        if not data:
            # Client sent an empty request, terminate the connection immediately
            await SocketIO.close(sock)
            return
        
        # Process data/request 
        await self.async_process_data(sock, addr, RawRequestData(data))
        
        # Close client socket just in case it is not closed
        SocketIO.close(sock)
        
    async def async_process_data(
        self,
        sock: xsocket,
        addr: Tuple[str, int],
        request_data: RequestData,
    ) -> None:
        """
        Process and handle the request dynamically and asynchronously.
        """
        # Continue with data processing.
        data = request_data.data if isinstance(request_data, RawRequestData) else request_data.content
        
        if is_ssl_data(data):
            if SETTINGS['DEBUG']:
                logger.log(
                    "Data should be decoded at this point but it seems like it's ssl data",
                    level=logger.WARNING,
                )
                logger.log(f"Client may be trying to connect with https on http server or vice-versa\n", level=logger.WARNING)
            return None
            
        try:
            await self.async_handle_request_data(sock, addr, request_data)
        except Exception as e:
            # Log the error message
            logger.log_exception(e)
        
        finally:
            # Check if client wants a keep alive connection
            # Only handle keep alive connection if the server supports it.
            try:
                if KEEP_ALIVE_PATTERN.search(data.split(b"\r\n\r\n")[0]):  # target headers only
                    if CONNECTION_MODE == "keep-alive":
                        # Server supports keep alive
                        await self.async_handle_keep_alive_conn(sock, addr)
            finally:
                # Finally close the socket if everything is finished
                SocketIO.close(sock)
            
    async def async_handle_keep_alive_conn(
        self,
        sock: xsocket,
        addr: Tuple[str, int],
    ) -> None:
        """
        Processes and handles keep alive connection asynchronously.
        """
        data: bytes = b""
        
        # Assume the client wants keep alive to run forever until explicitly stated to end it.
        while True:
            try:
                # Receive client request with a timeout.
                data = await SocketIO.async_receive_full_request(sock=sock, timeout=KEEP_ALIVE_TIMEOUT)
                
                if not data:
                    # Client sent nothing or closed connection
                    # End the keep alive data exchange immediately
                    break
                
                # Process and handle the complete request using appropriate WSGI
                await self.async_handle_request_data(sock, addr, RawRequestData(data))
            
            except TimeoutError:
                # Client sent nothing in expected time it was suppose to
                # Close connection immediately
                break
            
            except Exception as e:
                # Encountered an unknown exception, log that exception right away
                logger.log_exception(e)
            
            finally:
                # After every keep alive cycle, check if client still wants to continue with
                # the connection or terminate immediately
                if KEEP_ALIVE_PATTERN.search(data.split(b"\r\n\r\n")[0]):
                    # client seem to like to continue with keep alive connection
                    if CONNECTION_MODE == "keep-alive":
                        # keep connection alive
                        continue
                    else:
                        break
                else:
                    # Client would like to terminate keep alive connection.
                    break
                    
    async def async_do_request_timeout(
        self,
        sock: xsocket,
        addr: Tuple[str, int]
    ):
        """
        Sends request timeout response to client and close connection asynchronously.

        Args:
            sock (xsocket): Client socket object
            addr (Tuple[str, int]): Client ip address and port.
        """
        from duck.settings.loaded import SettingsLoaded
        
        # Send timeout error message to client.
        timeout_response = get_timeout_error_response(timeout=SETTINGS["REQUEST_TIMEOUT"])
        
        await SettingsLoaded.ASGI.finalize_response(timeout_response, request=None)
        
        # Send timeout response
        await response_handler.async_send_response(
            timeout_response,
            sock,
            disable_logging=self.no_logs,
         )
        
        # Close client socket immediately
        SocketIO.close(sock)
        
    async def async_handle_request_data(
        self,
        sock: xsocket,
        addr: Tuple[str, int],
        request_data: RequestData,
    ) -> None:
        """
        Asynchronously processes the request using WSGI application callable.

        Args:
            sock (xsocket): Client Socket object
            addr (Tuple[str, int]): Tuple for ip and port from where this request is coming from, ie Client addr
            request_data (RequestData): The request data object
        """
        handle_asgi_request = SettingsLoaded.ASGI
        
        await handle_asgi_request(
            self.application,
            sock,
            addr,
            request_data,
        )


class BaseMicroServer(BaseServer):
    """
    BaseMicroServer class containing definitions for micro application server.
    
    This class is the base definition of a micro application server.
    """

    def set_microapp(self, microapp):
        """
        Sets the target micro application for this server instance.
        """
        from duck.app.microapp import MicroApp

        if not isinstance(microapp, MicroApp):
            raise ValueError(f"MicroApp instance expected, received {type(micropp)} instead.")
        
        self.microapp = microapp # set the micro application instance
    
    def handle_request_data(
        self,
        sock: xsocket,
        addr: Tuple[str, int],
        request_data: RequestData,
    ) -> None:
        """
        Processes and handles the request.

        Args:
            sock (xsocket): The target client socket.
            addr (Tuple): The client address and port.
            request_data (RequestData): The full request data object.
        """
        from duck.shortcuts import to_response
        
        request_class = SettingsLoaded.REQUEST_CLASS

        if not issubclass(request_class, HttpRequest):
            raise SettingsError(
                f"REQUEST_CLASS set in settings.py should be an instance of Duck HttpRequest not {request_class}"
            )
        
        try:
            request = request_class(
                client_socket=sock,
                client_address=addr,
            ) # create an http request instance.
            
            # Parse request data to create a request object.
            request.parse(request_data)
            
            # Process the request and obtain the http response by
            # parsing the request and the predefined request processor.
            # This method also finalizes response by default.
            response = self.microapp._view(
                request,
                RequestProcessor(request),
            )
            
            # Validate the response type.
            response = to_response(response)
            
            # Send the http response back to client
            response_handler.send_response(
                response,
                sock=request.client_socket,
                request=request,
                disable_logging=self.microapp.no_logs,
            )

        except Exception as e:
            # Encountered an unknown error.
            from duck.http.core.wsgi import get_server_error_response
            
            # Send an http server error response to client.
            response = get_server_error_response(e, request)
           
            # Finalize server error response
            SettingsLoaded.WSGI.finalize_response(response, request)
            
            response_handler.send_response(
                response,
                sock=request.client_socket,
                request=request,
                disable_logging=self.microapp.no_logs,
            )
            
            if not self.microapp.no_logs:
                # If logs are not disabled for the micro application, log error immediately
                logger.log_exception(e)
        
    async def async_handle_request_data(
        self,
        sock: xsocket,
        addr: Tuple[str, int],
        request_data: RequestData,
    ) -> None:
        """
        Processes and handles the request asynchronously.

        Args:
            sock (xsocket): The target client socket.
            addr (Tuple): The client address and port.
            request_data (RequestData): The full request data object.
        """
        from duck.shortcuts import to_response
        
        request_class = SettingsLoaded.REQUEST_CLASS

        if not issubclass(request_class, HttpRequest):
            raise SettingsError(
                f"REQUEST_CLASS set in settings.py should be an instance of Duck HttpRequest not {request_class}"
            )
        
        try:
            request = request_class(
                client_socket=sock,
                client_address=addr,
            ) # create an http request instance.
            
            # Parse request data to create a request object.
            request.parse(request_data)
            
            # Process the request and obtain the http response by
            # parsing the request and the predefined request processor.
            # This method also finalizes response by default.
            response = await self.microapp._async_view(
                request,
                AsyncRequestProcessor(request),
            )
            
            # Validate the response type.
            response = to_response(response)
            
            # Send the http response back to client
            await response_handler.async_send_response(
                response,
                sock=request.client_socket,
                request=request,
                disable_logging=self.microapp.no_logs,
            )

        except Exception as e:
            # Encountered an unknown error.
            from duck.http.core.asgi import get_server_error_response
            
            # Send an http server error response to client.
            response = get_server_error_response(e, request)
           
            # Finalize server error response
            await SettingsLoaded.ASGI.finalize_response(response, request)
            
            await response_handler.async_send_response(
                response,
                sock=request.client_socket,
                request=request,
                disable_logging=self.microapp.no_logs,
            )
            
            if not self.microapp.no_logs:
                # If logs are not disabled for the micro application, log error immediately
                logger.log_exception(e)
