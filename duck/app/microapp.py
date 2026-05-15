"""
Mini application of Duck app which may be used for many simple tasks.

Notes:
- `Mini applications` run independently on their own individual ports.
- An example of a mini app is Duck's internal `HttpsRedirectApp` which is used to redirect HTTP traffic to a more secure HTTPS server.
"""
import time
import threading

from typing import Union, Optional

from duck.http.core.httpd.servers import MicroHTTPServer
from duck.http.core.processor import (
    AsyncRequestProcessor,
    RequestProcessor,
)
from duck.http.request import HttpRequest
from duck.http.response import HttpResponse
from duck.contrib.sync import ensure_async, ensure_sync
from duck.utils.urlcrack import URL
from duck.shortcuts import redirect
from duck.app.base import BaseApp


class MicroApp(BaseApp):
    """
    **Duck** micro application class to create a new lightweight sub-application/server.  

    This micro app can be used to create a new sub-application with its own server, meaning,
    you can create multiple micro apps in a single Duck application.  
    
    **Notes:**
    - MicroApp should be used when you want to create a new server with its own address and port.
    - Every request to the micro app will be handled by the `view` or `async_view` method, no request will be passed to WSGI/ASGI.
    - Everything is to be handled manually in the view/async_view method and none of all available middlewares will be applied.
    """
    
    DEFAULT_ADDR = "localhost"
    DEFAULT_PORT = 8000
    
    def __init__(
        self,
        name: Optional[str] = None,
        addr: str = DEFAULT_ADDR,
        port: int = DEFAULT_PORT,
        domain: Optional[str] = None,
        server_url: Optional[str] = None,
        uses_ipv6: bool = False,
        enable_https: bool = False,
        no_checks: bool = False,
        no_logs: bool = True,
        workers: Optional[int] = None,
        force_worker_processes: bool = False,
    ):
        """
        Args:
            name: Unique name to your application.
            addr: Address the server binds to.
            port: Port the server binds to.
            domain: Public-facing domain. Defaults to the bind address.
            server_url: Public-facing absolute server URL.
            uses_ipv6: Whether the app should bind using IPv6.
            enable_https: Whether HTTPS is enabled for this app.
            no_checks: Whether to skip app checks. Defaults to Fa
            no_logs: Whether to disable app logging. Defaults to False.
            workers: Optional number of server workers.
            force_worker_processes: Determines whether to use worker **processes** instead of the default worker **threads**. 
                    By default, when `workers` is greater than 1, the server will use worker **threads**.  
                    Threads avoid cross-process synchronization issues—such as component registry mismatches 
                    (e.g., issues with Lively components) that occur when state lives in separate processes.  
                    
                    Set this flag to `True` only when process isolation is explicitly desired **and** you do not
                    require shared in-memory synchronization between workers.
        
        Raises:
            ApplicationError: If the provided bind address is invalid.
        """
        super().__init__(
            name=name,
            addr=addr,
            port=port,
            domain=domain,
            server_url=server_url,
            uses_ipv6=uses_ipv6,
            enable_https=enable_https,
            no_checks=no_checks,
            workers=workers,
            force_worker_processes=force_worker_processes,
        )
        
        # Store some application attributes
        self.no_logs = no_logs
        
        # Create server with processed data.
        self.server = MicroHTTPServer(
            addr=(self.addr, self.port),
            microapp=self,
            domain=self.domain,
            uses_ipv6=self.uses_ipv6,
            enable_ssl=self.enable_https,
            no_logs=self.no_logs,
            workers=self.workers,
            force_worker_processes=self.force_worker_processes,
        )
        
        # Assign server thread to None
        self.server_thread = None
        
    def start_server(self):
        """
        Starts the server in a new thread.
        """
        def start_server_wrapper(*args, **kw):
            """
            Wrapper for server start.
            """
            try:
                self.server.start_server(*args, **kw)
            except KeyboardInterrupt:
                pass
                
        if not self.server_thread or not self.server_thread.is_alive():
            # Set the server thread
            self.server_thread = threading.Thread(
                target=start_server_wrapper,
                kwargs={'on_server_start_fn': self.on_app_start},
            )
            
            # Start the server thread
            self.server_thread.start()
        
    def run(self, run_forever: bool = True):
        """
        Runs the duck sub-application.
        
        Args:
            run_forever (bool): Whether to run a while loop to avoid app from exiting.
                                              Server is always run in background and setting `run_forever=False` will make this method return 
                                              immediately after starting the background thread.
        """
        # Start the server in a new thread - only if not running.
        self.start_server()
        
        while run_forever:
            # Just sleep for 5 seconds
            time.sleep(5)
            
    def stop(self):
        """
        Stops the current running micro-application.
        """
        self.server.stop_server(log_to_console=not self.no_logs)
    
    def view(self, request: HttpRequest, processor: Union[AsyncRequestProcessor, RequestProcessor]) -> HttpResponse:
        """
        Entry method to response generation.

        Args:
            request (HttpRequest): The http request object.
            processor (RequestProcessor]): Default request processor which you may use to process request.
        
        Notes:
        - Middlewares will not be applied on microapps, you are responsible for applying and handling middlewares.
        - On microapps, you are almost responsible for everything including managing database connections before and
          after request if needed.
        - But, the view response will be finalized automatically, meaning necessary headers will be set and response will be
          compressed if necessary.
        """
        raise NotImplementedError("Implement this method to return HttpResponse or any data as response.")
    
    async def async_view(self, request: HttpRequest, processor: AsyncRequestProcessor) -> HttpResponse:
        """
        Asynchronous entry method to response generation.

        Args:
            request (HttpRequest): The http request object.
            processor (AsyncRequestProcessor): Default request processor which you may use to process request.
        
        Notes:
        - Middlewares will not be applied on microapps, you are responsible for applying and handling middlewares.
        - On microapps, you are almost responsible for everything including managing database connections before and
          after request if needed.
        - But, the view response will be finalized automatically, meaning necessary headers will be set and response will be
          compressed if necessary.
        """
        raise NotImplementedError("Implement this method to return HttpResponse or any data as response.")
        
    def _view(self, request: HttpRequest, processor: RequestProcessor) -> HttpResponse:
        """
        Internal entry method to response generation.

        Args:
            request (HttpRequest): The http request object.
            processor (RequestProcessor): Default request processor which may be used to process request.
        """
        from duck.settings.loaded import SettingsLoaded
        
        # Get response from view method
        response = ensure_sync(self.view)(request, processor)
        
        # Finalize response using WSGI
        SettingsLoaded.WSGI.finalize_response(response, request)  # finalize response
        
        # Return the final response
        return response

    async def _async_view(self, request: HttpRequest, processor: AsyncRequestProcessor) -> HttpResponse:
        """
        Internal entry method to asynchronous response generation.

        Args:
            request (HttpRequest): The http request object.
            processor (AsyncRequestProcessor): Default asynchronous request processor which may be used to process request.
        """
        from duck.settings.loaded import SettingsLoaded
        
        # Get response from view method
        response = await ensure_async(self.async_view)(request, processor)
        
        # Finalize response using ASGI
        await SettingsLoaded.ASGI.finalize_response(response, request)  # finalize response
        
        # Return final response.
        return response


class HttpsRedirectMicroApp(MicroApp):
    """
    Micro application class capable of redirecting HTTP traffic to HTTPS.
    """
    def view(self, request: HttpRequest, request_processor: RequestProcessor) -> HttpResponse:
        """
        Returns an HTTP redirect response.
        """
        # Create destination URL
        dest_url_obj = URL(self.absolute_uri)
        
        # Edit the destination URL object inplace
        dest_url_obj.innerjoin(request.fullpath)
        
        # Return response
        return redirect(dest_url_obj.to_str(), permanent=False)

    async def async_view(self, request: HttpRequest, request_processor: AsyncRequestProcessor) -> HttpResponse:
        """
        Returns an HTTP redirect response.
        """
        # Just return whatever view() is returning because no async API is needed here
        return self.view(request, request_processor)
