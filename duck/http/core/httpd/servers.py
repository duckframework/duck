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
    create_xsocket,
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
        from duck.app.app import App
        from duck.app.microapp import MicroApp
        from duck.etc.ssl_defaults import SSL_DEFAULTS
        
        assert isinstance(addr, tuple), f"Argument addr should be an instance of 'tuple' not '{type(addr).__name__}'."
        assert len(addr) == 2, f"Argument addr should be a tuple of length 2 not {len(addr)}."
        assert isinstance(addr[0], str), f"Argument addr[0] must be an instance of 'str' not '{type(addr[0]).__name__}'."
        assert isinstance(addr[1], int), f"Argument addr[1] should be an instance of 'int' not '{type(addr[1]).__name__}'."
        assert isinstance(application, (App, MicroApp)), f"Argument application must be an instance of App or MicroApp, not {type(application)}"
        assert ssl_params is None or isinstance(ssl_params, dict), f"Argument `ssl_params` must be an instance of dictionary, not {type(ssl_params)}"
        
        # Create some socket object
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
