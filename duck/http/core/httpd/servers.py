"""
Module containing server classes.
"""
import ssl
import socket

from typing import (
    Dict,
    Optional,
    Tuple,
    Union,
)

from duck.settings import SETTINGS
from duck.http.core.httpd.httpd import (
    BaseMicroServer,
    BaseServer,
)
from duck.http.core.httpd.http2 import BaseHTTP2Server
from duck.exceptions.all import SettingsError
from duck.utils.xsocket import (
    xsocket,
    ssl_xsocket,
    ssl_wrap_socket,
)
       
BaseServer = (
    BaseHTTP2Server if SETTINGS["SUPPORT_HTTP_2"]
    else BaseServer
)


class HTTPServer(BaseServer):
    """
    HTTPServer class for handling requests.
    """
    
    __instances: int = 0

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
        super().__init__(
            addr=addr,
            application=application,
            domain=domain,
            uses_ipv6=uses_ipv6,
            enable_ssl=enable_ssl,
            ssl_params=ssl_params,
            no_logs=no_logs,
        )
        
        # Increment instances
        type(self).__instances += 1
        
    def ssl_wrap_socket(self, client_socket: socket.socket) -> ssl_xsocket:
        """
        Wraps client socket with SSL context.
        """
        alpn_protocols = ["http/1.1", "http/1.0"]
             
        if SETTINGS['SUPPORT_HTTP_2']:
            alpn_protocols.insert(0, "h2")
                  
        return ssl_wrap_socket(
            socket_obj=client_socket,
            server_side=True,
            alpn_protocols=alpn_protocols,
            **self.ssl_params,
        )


class MicroHTTPServer(BaseMicroServer, HTTPServer):
    """
    MicroHTTPServer class.
    """
    def __init__(
        self,
        addr: Tuple[str, int],
        microapp: "MicroApp",
        domain: str = None,
        uses_ipv6: bool = False,
        enable_ssl: bool = False,
        ssl_params: bool = None,
        no_logs: bool = True,
    ):
        self.set_microapp(microapp)
        
        super().__init__(
            addr,
            microapp,
            domain=domain,
            uses_ipv6=uses_ipv6,
            enable_ssl=enable_ssl,
            ssl_params=ssl_params,
            no_logs=no_logs,
        )
