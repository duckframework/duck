"""
Base server implementation for HTTP/2
"""
import re
import os
import h2
import ssl
import time
import socket
import queue
import asyncio
import base64

from typing import (
    Tuple,
    Dict,
    Optional,
    List,
    Callable,
)

from h2.config import H2Configuration
from h2.connection import H2Connection

from duck.settings import SETTINGS
from duck.http.response import (
    HttpResponse,
    HttpSwitchProtocolResponse,
)
from duck.http.request_data import RequestData, RawRequestData
from duck.http.core.httpd.httpd import (
    BaseServer,
    response_handler,
)
from duck.logging import logger
from duck.utils.xsocket import xsocket
from duck.utils.xsocket.io import SocketIO
from duck.utils.asyncio.eventloop import AsyncioLoopManager


# Regex to match "Upgrade: h2" or "Upgrade: h2c" in headers only
H2_UPGRADE_REGEX = re.compile(
    rb'^(?:[^\r\n]*\r\n)*Upgrade:\s*h2c?\s*(?:\r\n[^\r\n]*)*\r\n\r\n',
    re.IGNORECASE | re.MULTILINE
)             
# Regex to extract HTTP2-Settings header value
H2_SETTINGS_REGEX = re.compile(
    rb"HTTP2-Settings:\s*([A-Za-z0-9+\/=]+)",
    re.IGNORECASE | re.MULTILINE,
)


class SyncH2ProtocolStartWarning(UserWarning):
    """
    Flagged when `H2` protocol failed to start within specific timeframe in a synchronous environment.
    """
    

class BaseHTTP2Server(BaseServer):
    """
    Base HTTP/2 server with HTTP/1.1 backward compatibility.
    
    Notes:
    - Supports both HTTP/2 and HTTP/1.1 protocols.
    - The `H2Protocol` is implemented using asynchronous I/O, even in WSGI environments.
    - In WSGI mode, request handling may be offloaded to a synchronous thread 
          for execution outside the async context.
    """
    def set_h2_settings(self, h2_conn):
        """
        Sets the H2 settings on the unitiated h2 connection.
        """
        h2_conn.update_settings({
            h2.settings.SettingCodes.INITIAL_WINDOW_SIZE: 2**24,  # e.g., 16MB window
            h2.settings.SettingCodes.MAX_CONCURRENT_STREAMS: 100
        })
        
    def handle_conn(
        self,
        sock: xsocket,
        addr: Tuple[str, int],
        flowinfo: Optional = None,
        scopeid: Optional = None,
        strictly_http2: bool = True,
    ) -> None:
        """
        Main entry point to handle new connection (supports both ipv6 and ipv4).

        Args:
            sock (xsocket): The client socket object.
            addr (Tuple[str, int]): Client ip and port.
            flowinfo (Optional): Flow info if IPv6.
            scopeid (Optional): Scope id if IPv6.
            strictly_http2 (bool): Whether to srtrictly use `HTTP/2` without checking if user selected it.
        """
        has_h2_alpn = hasattr(sock, 'selected_alpn_protocol') and sock.selected_alpn_protocol() == 'h2'
        
        if not has_h2_alpn or not strictly_http2:
            # Fallback to HTTP/1
            # The user selected alpn protocol is not h2, switch to default HTTP/1 only if Upgrade to h2c is not set
             try:
                # Receive the full request (in bytes)
                data = SocketIO.receive_full_request(sock=sock)
            
             except TimeoutError:
                # For the first request, client took too long to respond.
                self.do_request_timeout(sock, addr)
                return
            
             if not data:
                # Client sent an empty request, terminate the connection immediately
                SocketIO.close(sock)
                return
             
             if H2_UPGRADE_REGEX.match(data):
                 try:
                    # Lets upgrade to HTTP/2
                    settings_header = None
                    settings_match = H2_SETTINGS_REGEX.search(data)
                    
                    if settings_match:
                        settings_header = settings_match.group(1)
                        settings_header = base64.urlsafe_base64decode(settings_header + "==")
                        
                    config = H2Configuration(client_side=False)
                    h2_connection = H2Connection(config=config)
                    
                    # Set base server settings
                    self.set_h2_settings(h2_connection)
                    
                    if settings_header:
                        h2_connection.initiate_upgrade_connection(settings_header=settings_header)
                    else:
                        h2_connection.initiate_connection()
                    
                    # Send switching protocols response
                    switching_proto_response = HttpSwitchProtocolResponse(upgrade_to="h2c")
                    
                    response_handler.send_response(
                        switching_proto_response,
                        sock=sock,
                        request=None,
                        strictly_http1=True,
                     )
                    
                    # Send pending HTTP/2 data.
                    try:
                        SocketIO.send(
                            sock=sock,
                            data=h2_connection.data_to_send(),
                            suppress_errors=False,
                        )
                    except (BrokenPipeError, ConnectionResetError):
                        # Client disconnected 
                        return
                 except Exception:
                     return
                     
             else:
                # No HTTP/2 Upgrade, strictly HTTP/1.1
                request_data = RawRequestData(data)
                request_data.request_store["h2_handling"] = False
                self.process_data(sock, addr, request_data)
             
             # Hang here...
             return
         
        # Initiate and send HTTP/2 preamble
        config = H2Configuration(client_side=False)
        h2_connection = H2Connection(config=config)
        
        # Set HTTP/2 settings and initiate connection
        self.set_h2_settings(h2_connection)
        h2_connection.initiate_connection()
        
        # Send pending HTTP/2 preamble data.
        try:
            SocketIO.send(
                sock=sock,
                data=h2_connection.data_to_send(),
                suppress_errors=False,
            )
        except (BrokenPipeError, ConnectionResetError):
            # Client disconnected 
            return
        
        # Start handling H2 frames
        self.start_http2_loop(sock, addr, h2_connection)
    
    @logger.handle_exception
    def handle_request_data(
        self,
        sock: xsocket,
        addr: Tuple[str, int],
        request_data: RequestData,
    ) -> None:
        """
        Processes and handles a request but logs any encountered error (but doesn't raise exception).
        """
        super().handle_request_data(sock, addr, request_data)
        
    def start_http2_loop(
        self,
        sock: xsocket,
        addr: Tuple[str, int],
        h2_connection: H2Connection,
    ) -> None:
        """
        Starts the loop for handling HTTP/2 connection.
        """
        from duck.http.core.httpd.http2.protocol import H2Protocol
        from duck.http.core.httpd.http2.event_handler import EventHandler
        
        # Assume client supports HTTP/2
        event_loop = AsyncioLoopManager.get_event_loop()
        
        protocol = H2Protocol(
            sock=sock,
            addr=addr,
            conn=h2_connection,
            event_handler=None,
            event_loop=event_loop, # Required in sync mode.
            sync_queue=queue.Queue(),
        )
        
        # Send H2 pending data
        protocol.send_pending_data()
        
        # Set some values.
        protocol.event_handler = EventHandler(protocol=protocol, server=self)
        sock.h2_protocol = protocol
        coro = protocol.run_forever()
        
        # Submit coroutine for sending/receiving data asynchronously
        # but we create a loop for executing synchronous tasks out of async context, in the current thread.
        AsyncioLoopManager.submit_task(coro)
        
        # Wait for protocol to start but for limited time
        wait_time_interval = .1
        total_wait_time = 0
        max_wait_time = 0
        
        while protocol.closing:
            if total_wait_time >= max_wait_time:
                # The protocol did not start within expected time
                if SETTINGS['DEBUG']:
                    logger.warn(f"H2 protocol failed to start within {max_wait_time} seconds for addr {addr}", SyncH2ProtocolStartWarning)
                break
            time.sleep(wait_time_interval)
            total_wait_time += wait_time_interval
         
        # As h2 is asynchrous, some tasks may require to be executed directly in current thread, thats the
        # use of the following loop.
        while not protocol.closing:
            # Listen for synchronous tasks to handle only when h2 connection is valid
            try:
                func, future = protocol.sync_queue.get(timeout=0.000000001)
                
                # Execute function synchronously in current thread
                result = func()
                future.set_result(result)
                
            except queue.Empty:
                continue
            
            except Exception as e:
                future.set_exception(e)
                logger.log_exception(e)
        
    # ASYNCHRONOUS IMPLEMENTATIONS
     
    async def async_handle_conn(
        self,
        sock: xsocket,
        addr: Tuple[str, int],
        flowinfo: Optional = None,
        scopeid: Optional = None,
        strictly_http2: bool = True,
    ) -> None:
        """
        Main entry point to handle new connection asynchronously (supports both ipv6 and ipv4).

        Args:
            sock (xsocket): The client socket object.
            addr (Tuple[str, int]): Client ip and port.
            flowinfo (Optional): Flow info if IPv6.
            scopeid (Optional): Scope id if IPv6.
            strictly_http2 (bool): Whether to srtrictly use `HTTP/2` without checking if user selected it.
        """
        has_h2_alpn = hasattr(sock, 'selected_alpn_protocol') and sock.selected_alpn_protocol() == 'h2'
        
        if not has_h2_alpn or not strictly_http2:
            # Fallback to HTTP/1
            # The user selected alpn protocol is not h2, switch to default HTTP/1 only if Upgrade to h2c is not set
             
             try:
                # Receive the full request (in bytes)
                data = await SocketIO.async_receive_full_request(sock=sock)
            
             except TimeoutError:
                # For the first request, client took too long to respond.
                await self.async_do_request_timeout(sock, addr)
                return
            
             if not data:
                # Client sent an empty request, terminate the connection immediately
                SocketIO.close(sock)
                return
             
             if H2_UPGRADE_REGEX.match(data):
                 try:
                    # Lets upgrade to HTTP/2
                    settings_header = None
                    settings_match = H2_SETTINGS_REGEX.search(data)
                    
                    if settings_match:
                        settings_header = settings_match.group(1)
                        settings_header = base64.urlsafe_base64decode(settings_header + "==")
                        
                    config = H2Configuration(client_side=False)
                    h2_connection = H2Connection(config=config)
                    
                    # Set base server settings
                    self.set_h2_settings(h2_connection)
                    
                    if settings_header:
                        h2_connection.initiate_upgrade_connection(settings_header=settings_header)
                    else:
                        h2_connection.initiate_connection()
                    
                    # Send switching protocols response
                    switching_proto_response = HttpSwitchProtocolResponse(upgrade_to="h2c")
                    
                    await response_handler.async_send_response(
                        switching_proto_response,
                        sock=sock,
                        request=None,
                        strictly_http1=True,
                     )
                    
                    # Send pending HTTP/2 data.
                    try:
                        await SocketIO.async_send(
                            sock=sock,
                            data=h2_connection.data_to_send(),
                            suppress_errors=False,
                        )
                    except (BrokenPipeError, ConnectionResetError):
                        # Client disconnected 
                        return
                 except Exception:
                     return
                     
             else:
                 # No HTTP/2 Upgrade, strictly HTTP/1.1
                request_data = RawRequestData(data)
                request_data.request_store["h2_handling"] = False
                await self.async_process_data(sock, addr, request_data)
              
             # Hang here...
             return
        
        # Initiate and send HTTP/2 preamble
        config = H2Configuration(client_side=False)
        h2_connection = H2Connection(config=config)
        
        # Set H2 settings and initiate connection
        self.set_h2_settings(h2_connection)
        h2_connection.initiate_connection()
        
        # Send pending HTTP/2 preamble data.
        try:
            await SocketIO.async_send(
                sock=sock,
                data=h2_connection.data_to_send(),
                suppress_errors=False,
            )
        except (BrokenPipeError, ConnectionResetError):
            # Client disconnected
            return
        
        # Start handling H2 frames
        await self.async_start_http2_loop(sock, addr, h2_connection)
    
    @logger.handle_exception
    async def async_handle_request_data(
        self,
        sock: xsocket,
        addr: Tuple[str, int],
        request_data: RequestData
    ) -> None:
        """
        Processes and handles a request asynchronously but logs any encountered error (but doesn't raise exception).
        """
        await super().async_handle_request_data(sock, addr, request_data)
        
    async def async_start_http2_loop(
        self,
        sock: xsocket,
        addr: Tuple[str, int],
        h2_connection: H2Connection
    ) -> None:
        """
        This starts the asynchronous loop for handling HTTP/2 connection.
        """
        from duck.http.core.httpd.http2.protocol import H2Protocol
        from duck.http.core.httpd.http2.event_handler import EventHandler
        
        protocol = H2Protocol(
            sock=sock,
            addr=addr,
            conn=h2_connection,
            event_handler=None,
            event_loop=None, # optional in async mode.
        )
        
        # Send pending H2 data.
        await protocol.async_send_pending_data()
        
        # Set some values.
        protocol.event_handler = EventHandler(protocol=protocol, server=self)
        sock.h2_protocol = protocol
        coro = protocol.run_forever()
        
        # Wait for coroutine to finish
        await coro
        