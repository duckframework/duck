"""
This module provides the core application class, `App`, for setting up and running a **Duck-based web application**. It supports various features, including:

- **HTTP/HTTPS Server**: Configures and starts an HTTP or HTTPS server based on application settings.
- **Django Integration**: Can forward requests to a Django server, supporting custom commands on startup.
- **SSL Management**: Checks and manages SSL certificates for secure communication.
- **Force HTTPS**: Redirects all HTTP traffic to HTTPS when enabled.
- **Automations**: Supports running automation scripts during runtime.
- **Ducksight Reloader**: Watches for file changes and enables dynamic reloading in **DEBUG mode**.
- **Port Management**: Ensures that application ports are available.
- **Signal Handling**: Gracefully handles termination signals (e.g., `Ctrl+C`) for clean shutdown.

---

## Attributes

| Attribute                  | Description |
|----------------------------|-------------|
| `DJANGO_ADDR`              | The address and port for the Django server. |
| `DOMAIN`                   | The domain name for the application. |
| `DJANGO_SERVER_WAIT_TIME`  | Time to wait for the Django server to start. |
| `server_up`                | Indicates if the main application server is running. |
| `django_server_up`         | Indicates if the Django server is responsive. |

---

## Methods

### **Application Control**
- `run()`: Starts the application and all services.
- `stop()`: Stops the application.
- `restart()`: Restarts the application.

### **Server Management**
- `start_server()`: Starts the main application server.
- `start_django_server()`: Starts Django and configures Duck as a reverse proxy.
- `start_force_https_server()`: Launches the HTTPS redirection service.

### **Background Services**
- `start_ducksight_reloader()`: Monitors file changes for live reloading.
- `start_automations_dispatcher()`: Handles scheduled automation scripts.

### **Event Handling & Security**
- `register_signals()`: Registers signal handlers for clean exits.
- `on_app_start()`: Event triggered when the application setup is complete.

---

## **Application Instance Management**
The `App` class ensures that only **one instance** of the application is running at a time.  
For **microservices or smaller applications**, use the `MicroApp` class instead.

---

## **Exceptions Handled**
- **`ApplicationError`**: Raised if multiple instances of `App` are created.
- **`SettingsError`**: Raised for misconfigurations in application settings.
- **`SSLError`**: Raised if SSL certificates or private keys are missing/invalid.
"""

import os
import sys
import json
import time
import signal
import socket
import threading
import setproctitle
import multiprocessing

from typing import (
    Optional,
    Dict,
    Any,
    Union,
)
from concurrent.futures import ThreadPoolExecutor, Future

from duck import processes
from duck.settings import SETTINGS
from duck.settings.loaded import SettingsLoaded
from duck.app.microapp import HttpsRedirectMicroApp
from duck.contrib.reloader.ducksight import DuckSightReloader
from duck.exceptions.all import (
    ApplicationError,
    SettingsError,
    SSLError,
)
from duck.http.core.httpd.servers import HTTPServer
from duck.logging import logger
from duck.meta import Meta
from duck.setup import setup
from duck.csp import csp_nonce_flag
from duck.art import display_duck_art
from duck.version import version
from duck.utils import ipc
from duck.utils.net import (is_ipv4, is_ipv6)
from duck.utils.path import url_normalize
from duck.utils.port_recorder import PortRecorder
from duck.utils.lazy import Lazy
from duck.utils.asyncio.eventloop import AsyncioLoopManager
from duck.utils.threading.threadpool import ThreadPoolManager


if SETTINGS['USE_DJANGO']:
    from duck.backend.django import bridge
else:
    # Bridge for starting Django server.
    bridge = None


class App:
    """
    Initializes and configures the **Duck** application.
    """
    
    DJANGO_ADDR: tuple[str, int] = None
    """
	Specifies the host address and port for the Django server. 
	For enhanced security, ensure that uncommon ports are used.
	"""

    DOMAIN: str = None
    """
    Domain for the application used in building the application absolute URI.
    """

    DJANGO_SERVER_WAIT_TIME: int = SETTINGS["DJANGO_SERVER_WAIT_TIME"]
    """
    Time in seconds to wait before checking if the Django server is up and running. 
    This variable is used to periodically verify the server's status during the initial startup or 
    maintenance routines, ensuring that the server is ready to handle incoming requests.
    """
    
    __instances__: int = 0
    """
    The number of App instances, must be <= 1.
    """
    
    __mainapp__ = None
    """
    This is the main application instance.
    """
    
    def __init__(
        self,
        addr: str = "localhost",
        port: int = 8000,
        domain: str = None,
        uses_ipv6: bool = False,
        no_checks: bool = False,
        disable_signal_handler: bool = False,
        disable_ipc_handler: bool = False,
        skip_setup: bool = False,
        enable_force_https_logs: bool = False,
        start_bg_event_loop_if_wsgi: bool = True,
        process_name: str = "duck-server",
        workers: Optional[int] = None,
        force_https_workers: Optional[int] = None, 
    ):
        """
        Initializes the main Duck application instance.
    
        This constructor sets up the application server, including optional Django integration,
        HTTPS redirection, and automation dispatching. It validates IP configuration, initializes
        environment settings, performs startup checks, and prepares runtime threads for the
        core services.
    
        Args:
            addr (str): The IP address or hostname the server will bind to. Defaults to "localhost".
            port (int): The port number to run the application on. Defaults to 8000.
            domain (str, optional): The public-facing domain for the app. If not provided, defaults to `addr`.
            uses_ipv6 (bool): Whether to use IPv6 for networking. Defaults to False.
            no_checks (bool): If True, skips initial environment checks. Defaults to False.
            disable_signal_handler (bool): If True, disables setup of OS-level signal handlers. Defaults to False.
            disable_ipc_handler (bool): If True, disables setup of inter-process communication handlers. Defaults to False.
            skip_setup (bool): If True, skips setting up Duck environment, e.g. setting up urlpatterns and blueprints.
            enable_force_https_logs (bool): If True, force https microapp logs will be outputed to console. Defaults to False.
            start_bg_event_loop_if_wsgi (bool): If True, it starts an event loop in background thread for offloading coroutines in `WSGI` environment.
                This is useful for running asynchronous protocols like `HTTP/2` and `WebSockets` even in `WSGI` environment.
            process_name (str): The name of the process for this application. Defaults to "duck-server".
            workers (Optional[int]): Number of workers to use. None will disable workers.
            force_https_workers (Optional[int]): Number of workers to use for HTTPS redirects. None will disable workers.
            
        Raises:
            ApplicationError: If the provided address is invalid or if multiple main application
            instances are created (only one is allowed).
    
        Side Effects:
        - Validates IP address format (IPv4 or IPv6).
        - Initializes HTTPS redirect server if `FORCE_HTTPS` is enabled.
        - Starts Django server if `USE_DJANGO` is set.
        - Starts the main application server.
        - Registers automation triggers if `RUN_AUTOMATIONS` is enabled.
        - Adds the application port to a port registry to prevent conflicts.
        
        Notes:
        - Only a single instance of the main `App` should be created. For additional services or sub-applications, use `MicroApp`.
            
        - Set `disable_ipc_handler=False` **only** in a test environment.
              The IPC handler introduces a blocking mechanism that keeps the main interpreter running.
              Disabling it in production may lead to unhandled or improperly managed requests, as the blocking behavior is essential for proper execution.
              The app will be run in background and `app.run` won't be blocking anymore.
        """
        if uses_ipv6 and not is_ipv6(addr) and not str(addr).isalnum():
            raise ApplicationError("Argument uses_ipv6=True yet addr provided is not a valid IPV6 address.")

        if not uses_ipv6 and not is_ipv4(addr) and not str(addr).isalnum():
            raise ApplicationError("Argument `addr` is not a valid IPV4 address.")
        
        self.addr = addr
        self.port = port
        self.uses_ipv6 = uses_ipv6
        self.no_checks = no_checks
        self.is_domain_set = True if domain else False
        self.started = False
        self._restart_success = False  # state on whether last restart operation has been successfull
        
        # Set appropriate domain
        self.domain = domain or (addr if not uses_ipv6 else f"[{addr}]")
        
        if is_ipv4(self.domain) and self.domain.startswith("0"):
            # IP "0.x.x.x" not allowed as domain because most browsers cannot resolve this.
            self.domain = "localhost"
            
        self.enable_https: bool = SETTINGS["ENABLE_HTTPS"]
        self.DOMAIN = self.domain
        self.SETTINGS = SETTINGS
        self.DJANGO_ADDR = addr, SETTINGS["DJANGO_BIND_PORT"]
        self.force_https = SETTINGS["FORCE_HTTPS"]
        self.force_https_port = SETTINGS["FORCE_HTTPS_BIND_PORT"]
        self.enable_force_https_logs = enable_force_https_logs
        self.use_django = SETTINGS["USE_DJANGO"]
        self.run_automations = SETTINGS["RUN_AUTOMATIONS"]
        self.disable_signal_handler = disable_signal_handler
        self.disable_ipc_handler = disable_ipc_handler
        self.skip_setup = skip_setup
        self.start_bg_event_loop_if_wsgi = start_bg_event_loop_if_wsgi
        self.process_name = process_name or "duck-server"
        self.workers = workers
        self.force_https_workers = force_https_workers
        
        # Initialize some attributes
        self.automations_dispatcher = None
        self.ducksight_reloader = None
        self.force_https_app = None
        self.last_request = None # Will be updated everytime by either ASGI/WSGI
        
        # Set the app thread pool executor
        def thread_pool_submit(task) -> Future:
            # Custom submit callable to always handle exceptions gracefully.
            @logger.handle_exception
            def on_task_done(task):
                err = task.exception() # May sometimes raise exception
                if err:
                    raise err # Reraise exception
            future = self.thread_pool_executor._super_submit(task)
            future.add_done_callback(on_task_done)
            return future
            
        # Modify default thread pool executor submit method
        self.thread_pool_executor = ThreadPoolExecutor()
        self.thread_pool_executor._super_submit = self.thread_pool_executor.submit
        self.thread_pool_executor.submit = thread_pool_submit
        
        # Initialize some concurrent futures
        self.duck_server_future = None
        self.automations_dispatcher_future = None
        self.ducksight_reloader_thread = None
        
        # Create some child processes (will be set later when necessary)
        self.force_https_app_process = None
        self.django_server_process = None
        
        # Add application port to used ports
        PortRecorder.add_new_occupied_port(port, f"{self}")
        PortRecorder.add_new_occupied_port(
            SETTINGS["DJANGO_BIND_PORT"],
            "DJANGO_BIND_PORT",
        ) if self.use_django else None
        
        if not no_checks:
            # Run some checks
            self.run_checks()
            
        # Vital objects creation
        if self.force_https:
            self.force_https_addr = addr
            self.force_https_app = Lazy(
                HttpsRedirectMicroApp,
                location_root_url=self.absolute_uri,
                addr=self.force_https_addr,
                port=self.force_https_port,
                parent_app=self,
                domain=self.domain,
                uses_ipv6=uses_ipv6,
                enable_https=False,
                no_logs=not enable_force_https_logs,
                workers=force_https_workers,
            )  # Create https redirect mivro application.
            
            # Set the process safe state for the force https app. 
            self.force_https_process_safe_running_state = multiprocessing.Value('i', 0)
            
        # Create a server object.
        self.server = HTTPServer(
            (addr, port),
            application=self,
            domain=self.domain,
            uses_ipv6=uses_ipv6,
            enable_ssl=self.enable_https,
            no_logs=False,
            workers=workers,
        )
        
        # Set process title
        self.set_process_name()
        
        # Set app instances count
        if type(self).__instances__ == 0:
            type(self).__instances__ += 1
            type(self).__mainapp__ = self
        else:
            raise ApplicationError(
                "Application limit reached: Only one main application is permitted. "
                "To create additional functionalities, consider using a MicroApp."
            )

    @classmethod
    def instances(cls) -> int:
        """
        Returns number of Application instances.
        """
        return cls.__instances__

    @classmethod
    def get_main_app(cls) -> "App":
        """
        Returns the main application instance if set.
        """
        if not cls.__mainapp__:
            raise ApplicationError("Main application not set, there is no running application.")
        return cls.__mainapp__
        
    @staticmethod
    def restart_background_workers(
        application: Union['App', 'MicroApp'],
        start_threadpool: bool = True,
        start_asyncio_event_loop: bool = True,
    ):
        """
        Restart background workers, e.g. `AsyncioLoopManager` thread & `ThreadPoolManager` pool.
        
        Args:
            application (Union['App', 'MicroApp']): The target application.
            start_threadpool (bool): Whether to start request handling threadpool in `WSGI` environment.
            start_asyncio_event_loop (bool): Whether to start asyncio event loop either in `WSGI` or `ASGI` environment.
            
        Notes:
        - This is usually useful when starting new process. Background workers like the request handling threadpool and asyncio loop's 
           thread.
        - This only focus on default `AsyncioLoopManager` & `ThreadPoolManager`.
        """
        from duck.utils.asyncio.eventloop import AsyncioLoopManager
        from duck.utils.threading.threadpool import ThreadPoolManager
        from duck.setup import set_asyncio_loop
        
        # Set asyncio event loop
        set_asyncio_loop()
        
        # Reinitialize asyncio/threadpool manager
        if SETTINGS['ASYNC_HANDLING'] and start_asyncio_event_loop:
            AsyncioLoopManager._thread = None
            AsyncioLoopManager._loop = None
            AsyncioLoopManager.start()
        else:
            bg_event_loop = getattr(application, "start_bg_event_loop_if_wsgi", True)
                
            # Reinitialize threadpool manager
            if start_threadpool:
                ThreadPoolManager._pool = None # Reset pool avoid RuntimeError if _pool is forked.
                ThreadPoolManager.start(
                    daemon=True,
                    thread_name_prefix="request-handler",
                    task_type="request-handling",
                 )
                    
            if bg_event_loop and start_asyncio_event_loop:
                AsyncioLoopManager._thread = None
                AsyncioLoopManager._loop = None
                AsyncioLoopManager.start()   
    
    @staticmethod
    def check_ssl_credentials():
        """
        This checks for ssl certfile and private key file existence.

        Raises:
            SSLError: Either certfile or private key file is not found.
        """
        certfile_path = SETTINGS["SSL_CERTFILE_LOCATION"]
        private_key_path = SETTINGS["SSL_PRIVATE_KEY_LOCATION"]
        
        if not os.path.isfile(certfile_path):
            raise SSLError(
                "SSL certfile provided in settings.py not found. You may use command `python3 -m duck ssl-gen` to "
                "generate a new self signed certificate and key pair."
            )

        if not os.path.isfile(private_key_path):
            raise SSLError(
                "SSL private key provided in settings.py not found. You may use command `python3 -m duck ssl-gen` to "
                "generate a new self signed certificate and key pair."
            )
    
    @property
    def running(self) -> bool:
        """
        Returns True if the main server running else False.
        """
        return self.server.running
        
    @property
    def meta(self) -> Dict[str, Any]:
        """
        Get application metadata.
        """
        return Meta.compile()

    @property
    def process_id(self) -> int:
        """
        Returns the application main process ID.
        """
        if not hasattr(self, "_main_process_id"):
            self._main_process_id = os.getpid()
        return self._main_process_id    
    
    @property
    def absolute_uri(self) -> str:
        """
        Returns application server absolute `URL`.
        """
        scheme = "http"
        
        if self.enable_https:
            scheme = "https"
        
        uri = f"{scheme}://{self.domain}"
        uri = uri.strip("/").strip("\\")
        
        if not (self.port == 80 or self.port == 443):
            uri += f":{self.port}"
        
        return uri
        
    @property
    def absolute_ws_uri(self) -> str:
        """
        Returns application server absolute WebSockets `URL`.
        """
        scheme = "ws"
        
        if self.enable_https:
            scheme = "wss"
        
        uri = f"{scheme}://{self.domain}"
        uri = uri.strip("/").strip("\\")
        
        if not (self.port == 80 or self.port == 443):
            uri += f":{self.port}"
        
        return uri
        
    @property
    def server_up(self) -> bool:
        """
        Checks whether the main application server is up and running.

        Returns:
            bool: True if up else False
        """
        return self.server.running

    @property
    def django_server_up(self) -> bool:
        """
        Checks whether django server to forward requests to has started

        Returns:
            started (bool): True if up else False
        """
        import requests

        try:
            host_addr, port = self.DJANGO_ADDR
            
            if host_addr.startswith("0") and not self.uses_ipv6:
                # Host 0.0.0.0 not allowed on windows
                host_addr = "127.0.0.1"
            
            # Note: Use /admin path as this is not usually altered like path /. Path /
            # may be accessing real Duck path from Django side, which might be slower than
            # /admin path, leading to ReadTimeoutError.
            if not self.uses_ipv6:
                url = f"http://{host_addr}:{port}/admin"
                
            else:
                url = f"http://[{host_addr}]:{port}/admin"
            
            response = requests.get(
                url=url,
                headers={"Host": SETTINGS["DJANGO_SHARED_SECRET_DOMAIN"]},
                timeout=1,
            )
            
            if not response:
                # Response status is not expected here.
                return False
            return True
        except Exception:
            pass
        return False

    @property
    def force_https_server_up(self) -> bool:
        """
        Checks whether force HTTPS redirect micro application is running.

        Returns:
            bool: True if up else False
        """
        if self.force_https_app_process:
            if self.force_https_app_process.is_alive():
                return bool(self.force_https_process_safe_running_state.value)
            else:
                return False
        else:
            return self.force_https_app.server.running
               
    def set_process_name(self):
        """
        Set the whole process name.
        """
        setproctitle.setproctitle(self.process_name)
        
    def run_checks(self):
        """
        Runs application checks.
        """
        if self.enable_https:
            self.check_ssl_credentials()

        # HTTPS checks
        if self.force_https:
            if not self.enable_https:
                raise SettingsError("FORCE_HTTPS has been set in settings.py, also ensure ENABLE_HTTPS=True.")
    
    def build_absolute_uri(self, path: str) -> str:
        """
        Builds and returns absolute URL from provided path.
        """
        return url_normalize(self.absolute_uri + "/" + path)
        
    def build_absolute_ws_uri(self, path: str) -> str:
        """
        Builds and returns absolute WebsSockets URL from provided path.
        """
        return url_normalize(self.absolute_ws_uri + "/" + path)
        
    def start_server(self):
        """
        Starts the app server in new thread.
        """  
        def start_server():
            """
            Starts Duck application main server.
            """
            self.server.start_server()
            
        if not self.duck_server_future or not self.duck_server_future.running():
            self.duck_server_future = self.thread_pool_executor.submit(start_server)
                
    def start_django_server(self):
        """
        Starts Django server and use Duck as reverse proxy server for django.
        """
        def start_django_server():
            """
            Starts Django application server
            """
            p = multiprocessing.current_process()
            setproctitle.setproctitle(p.name)
            host = self.DJANGO_ADDR
            
            # Restart background workers
            App.restart_background_workers(self, start_threadpool=False)
            
            # Start django server
            bridge.start_django_server(*host, uses_ipv6=self.uses_ipv6)
            
        if self.use_django:
            if not self.django_server_process or not self.django_server_process.is_alive():
                self.django_server_process = multiprocessing.Process(
                    target=start_django_server,
                    name="duck-django-server",
                )
                
                # Start the Django process
                self.django_server_process.start()

    def start_force_https_server(self, log_message: bool = True):
        """
        Starts force HTTPS redirect micro application.  
        
        Args:
            log_message (bool): Whether to log something before starting the micro app.
        
        Conditions:
         - `ENABLE_HTTPS = True`
         - `FORCE_HTTPS = True`
        """
        def start_force_https(process_safe_running_state: multiprocessing.Value):
            """
            Starts app for redirecting non encrypted traffic to main app using https.
            """
            from duck.utils.asyncio.eventloop import AsyncioLoopManager
            from duck.utils.threading.threadpool import ThreadPoolManager
            
            p = multiprocessing.current_process()
            setproctitle.setproctitle(p.name)
            signal.signal(signal.SIGINT, lambda *a: self.force_https_app.stop())
            
            # Restart background workers
            App.restart_background_workers(self)
            
            # Start the microapp
            self.force_https_app.on_app_start = lambda: setattr(process_safe_running_state, 'value', int(self.force_https_app.server.running))
            self.force_https_app.run(run_forever=True) # This is blocking
            
        if self.enable_https and self.force_https:
            # Log something if applicable.
            if log_message:
                logger.log(
                    f"Forcing HTTPS to all incoming traffic [{SETTINGS['FORCE_HTTPS_BIND_PORT']} -> {self.port}]",
                    level=logger.DEBUG,
                )
                
            # Start https redirect process
            if not self.force_https_app_process or not self.force_https_app_process.is_alive():
                self.force_https_app_process = multiprocessing.Process(
                    target=start_force_https,
                    name="duck-force-https-server",
                    args=(self.force_https_process_safe_running_state, ),
                )
                
                # Start the force https process
                self.force_https_app_process.start()
    
    def start_automations_dispatcher(self, log_message: bool = True):
        """
        Starts automations dispatcher for executing automations during runtime.
        
        Args:
            log_message (bool): Whether to log something before starting the micro app.
            
        Conditions:
        - `RUN_AUTOMATIONS = True`
        """
        def start_automations_dispatcher():
            """
            Starts automations dispatcher for running and managing automations on runtime.
            """
            if not self.automations_dispatcher:
                self.automations_dispatcher = SettingsLoaded.AUTOMATION_DISPATCHER(self)
            
            if log_message:
                automations_dispatcher_name = self.automations_dispatcher.__class__.__name__
                logger.log(
                    f"Running all automations with {automations_dispatcher_name}",
                    level=logger.DEBUG,
                )
                
            for trigger, automation in SettingsLoaded.AUTOMATIONS:
                # Register trigger and automation
                self.automations_dispatcher.register(trigger, automation)
            self.automations_dispatcher.start()
                
        if self.run_automations:
            # Submit task to the pool
            if not self.automations_dispatcher_future or not self.automations_dispatcher_future.running():
                self.automations_dispatcher_future = self.thread_pool_executor.submit(start_automations_dispatcher)
                        
    def start_ducksight_reloader(self):
        """
        Starts the DuckSight Reloader for reloading app on file modifications, deletions, etc.
        
        Notes:
        - Unlike other tasks like starting Duck server, HTTPS redirect server, etc which will be run by the app 
              `thread_pool_executor`, this runs in an independant background thread with `daemon=True`.
              
        Conditions:
        - `DEBUG = True`
        """
        # Note: Production server should not be restarted at any point only start duck sight reloader on DEBUG
        def start_reloader():
            if not self.ducksight_reloader:
                self.ducksight_reloader = DuckSightReloader(SETTINGS['BASE_DIR'])
            self.ducksight_reloader.run()
            
        if SETTINGS["DEBUG"] and SETTINGS['AUTO_RELOAD']:
            # Start ducksight reloader
            if not self.ducksight_reloader_thread or not self.ducksight_reloader_thread.is_alive():
                if not self.ducksight_reloader_thread:
                    self.ducksight_reloader_thread = threading.Thread(target=start_reloader)
                self.ducksight_reloader_thread.start()
                            
    def get_threadpool_futures(self) -> Dict[str, Optional[Future]]:
        """
        Returns a dictionary of all application concurrent futures as a result of submitting tasks 
        to the `ThreadPoolExector`.
        
        Notes:
        - The `DuckSightReloader` task is run on an independent thread, so no future for it will 
               be included in the dictionary.
        """
        return {
            "duck_server": self.duck_server_future,
            "automations_dispatcher": self.automations_dispatcher_future,
        }
        
    def register_signals(self):
        """
        Register and bind signals to appropriate signal handler.
        """
        signal.signal(signal.SIGINT, self.handle_signal)
        signal.signal(signal.SIGTERM, self.handle_signal)
        
    def handle_ipc_messages(self):
        """
        Handles incoming IPC messages from the shared file.
        
        Notes:
        - This usually holds the main process from exiting because of the blocking behavior.
        """
        with ipc.get_reader() as reader:
            # Clear ipc writer file
            with ipc.get_writer() as writer:
                writer.write_message("")  # clear ipc shared file
            
            # Handle any incoming message.    
            while True:
                message = reader.read_message().strip()
                if message:
                    if any({message.lower() == i for i in ["bye", "quit", "exit"]}):
                        self.stop()
                        break
                                
                # Simulate some delay
                time.sleep(1)
                
    def record_metadata(self):
        """
        Sets or updates the metadata for the app, these changes will
        be globally available in `duck.meta.Meta` class.
        """
        # Security reasons not mentioning real servername but 'webserver' is safer.
        data = {
            "DUCK_SERVER_NAME": "webserver",
            "DUCK_SERVER_PORT": self.port,
            "DUCK_SERVER_DOMAIN": self.domain,
            "DUCK_SERVER_PROTOCOL": ("https" if self.enable_https else "http"),
            "DUCK_DJANGO_ADDR": self.DJANGO_ADDR,
            "DUCK_USES_IPV6": self.uses_ipv6,
            "DUCK_SERVER_BUFFER": SETTINGS["SERVER_BUFFER"],
            "DUCK_WORKERS": int(self.workers or 0), # Meta.update doesnt support NoneType
        }
        Meta.update_meta(data)
        
    def handle_signal(self, sig, frame):
        """
        Method for handling process signals.

        Signals:
        - `SIGINT` (Ctrl-C), `SIGTERM` (Terminate): Quits the server/application.
        """
        if sig in [signal.SIGINT, signal.SIGTERM]:
            logger.log_raw("") # print a blank line to separate ^C and Stop message.
            self.stop()
    
    def stop_servers(
        self,
        stop_force_https_server: bool = True,
        log_to_console: bool = True,
    ):
        """
        Stop all running servers i.e., Duck main server, Force HTTPS server & Django server.

        Args:
            stop_force_https_server (bool): Whether to stop Force HTTPS redirect microapp.
            log_to_console (bool): Whether to an exit message log to console.
        """
        self.server.stop_server(log_to_console=log_to_console)
        
        if (stop_force_https_server
            and self.force_https_app_process
            and self.force_https_app_process.is_alive()
        ):
            self.force_https_app_process.terminate()
            self.force_https_app_process.join(1)
    
        if (self.django_server_process
            and self.django_server_process.is_alive()
        ):
            self.django_server_process.terminate()
            self.django_server_process.join(1)                
    
    def on_pre_stop(self):
        """
        Event called before final application termination.
        """
        if self.run_automations:
            self.automations_dispatcher.stop()

    def stop(
        self,
        log_to_console: bool = True,
        no_exit: bool = False,
        call_on_pre_stop_handler: bool = True,
        kill_ducksight_reloader: bool = True,
        wait_for_thread_pool_executor_shutdown: bool = True,
        close_log_file: bool = True,
    ):
        """
        Stops the application and terminates the whole program.

        Args:
            no_exit (bool): Whether to terminate everything but keep the program running.
            log_to_console (bool): Whether to log an exit message.
            call_on_pre_stop_handler (bool): Whether to call method `on_pre_stop`. Defaults to True.
            kill_ducksight_reloader (bool): This attempts to kill the `DuckSightReloader`. Useful if `no_exit=True`,
            wait_for_thread_pool_executor_shutdown (bool): Whether to wait for the thread pool executor to complete shutdown, 
                meaning waiting for current tasks to finish/cancel. This is only used if argument `no_exit=True` else it is automatically `False`.
            close_log_file (bool): Whether to close the log file. Defaults to True.
        """
        if "--is-reload" in sys.argv:
            log_to_console = False
            
        def stop_future(future):
            """
            Stops a running running future safely.
            """
            if future and future.running():
                try:
                    future.cancel()
                except Exception:
                    # Ignore as the thread_pool_executor is going to be shut down anyway if it's still running.
                    pass
                    
        # Cleanup session cache
        try:
            if (
                hasattr(self, "last_request")
                and self.last_request
                and hasattr(self.last_request.SESSION, "session_storage_connector") 
                 and self.last_request.SESSION.session_storage_connector
                ):
                    # Close the session storage connector
                    self.last_request.SESSION.session_storage_connector.close()
        
        except Exception as e:
            logger.log_raw('\n')
            logger.log(
                f"Error while closing session storage: {e}",
                level=logger.WARNING,
            )

        try:
            # Stop all servers
            self.stop_servers(log_to_console=log_to_console)
        except Exception as e:
            logger.log_raw('\n')
            logger.log(f"Error stopping servers: {e}", level=logger.ERROR)
            if SETTINGS['DEBUG']:
                logger.log_exception(e)
                
        if call_on_pre_stop_handler:
            try:
                # Execute a pre stop method before final termination.
                self.on_pre_stop()
            except Exception as e:
                logger.log_exception(e) # Log the exception.
        
        # Try cancel other cancelable components.
        if self.run_automations:
            try:
                self.automations_dispatcher.stop()
            except Exception as e:
                logger.log_exception(e)
        
        # Try cancel other cancelable components.
        if SETTINGS['DEBUG'] and SETTINGS['AUTO_RELOAD'] and kill_ducksight_reloader:
            try:
                self.ducksight_reloader.stop() if self.ducksight_reloader else None
            except Exception as e:
                logger.log_exception(e)
                
        # Cancel all running futures
        concurrent_futures = self.get_threadpool_futures()
        for name, future in concurrent_futures.items():
            stop_future(future)
        
        # Shutdown threadpool executor if not stopped.            
        if self.thread_pool_executor:
            try:
                self.thread_pool_executor.shutdown(wait=wait_for_thread_pool_executor_shutdown if no_exit else False)
            except Exception as e:
                logger.log_exception(e)
        
        if no_exit and kill_ducksight_reloader and wait_for_thread_pool_executor_shutdown:
            try:
                if self.ducksight_reloader_thread.is_alive():
                    self.ducksight_reloader_thread.join()
            except Exception as e:
                logger.log_exception(e)
                
        if close_log_file:
            # Close logging file
            if SETTINGS['LOG_TO_FILE']:
                try:
                    logger.Logger.close_logfile()
                except Exception as e:
                    logger.log(f"Error closing log file: {e}", level=logger.WARNING)
            
        # Perform forceful termination if needed
        if not no_exit:
            # Force exit (avoids lingering threads/processes)
            os._exit(0)
    
    def on_app_start(self):
        """
        Event called when application has successfully been started.
        """
        # Record main process data
        log_file = None
        is_reload = False
        
        if "--is-reload" in sys.argv:
            # App is being restarted somehow
            is_reload = True
            
        if SETTINGS["LOG_TO_FILE"]:
            log_file = logger.Logger.get_current_logfile()
        
        try:
            # Set process metadata in a file.
            processes.set_process_data(
                name="main",
                data={
                    "pid": self.process_id,
                    "start_time": time.time(),
                    "sys_argv": sys.argv,
                    "log_file": log_file,
                },
                clear_existing_data=True,
            )
        except json.JSONDecodeError:
            # The file used by duck.processes is corrupted
            pass  # ignore for now, maybe writting is still in progress
        
        if not self.disable_signal_handler:
            self.register_signals()  # bind signals to appropriate signal handlers
            logger.log(
                f"Use Ctrl-C to quit [APP PID: {self.process_id}]",
                level=logger.DEBUG,
                custom_color=logger.Fore.GREEN,
            ) 
        
        if SETTINGS["AUTO_RELOAD"] and SETTINGS["DEBUG"]:
            # Start ducksight reloader (if not running)
            self.start_ducksight_reloader()
            logger.log(
                f"Duck Sight Reloader watching file changes",
                level=logger.DEBUG,
                custom_color=logger.Fore.GREEN,
            )
        
        # Continue logging
        logger.log(
            "Waiting for incoming requests :-) \n",
            level=logger.DEBUG,
            custom_color=logger.Fore.GREEN,
        )
        
        # Update application state
        self.started = True
        
        # Handle any incoming IPC messages.
        if not self.disable_ipc_handler:
            self.handle_ipc_messages() # this is a blocking operation
            
    def run(self, print_ansi_art: bool = True):
        """
        Runs the Duck application.
        """
        # Setup Duck environment and the entire application.
        if not self.skip_setup:
            setup()
            
        # Record application metadata and run the server
        self.record_metadata()
        return self._run(print_ansi_art=print_ansi_art)
        
    def _run(self, print_ansi_art: bool = True):
        """
        Runs the Duck application.
        """
        # App is not in reload state, continue
        bold_start = "\033[1m"
        bold_end = "\033[0m"
        duck_start_failure_msg = f"{bold_start}Failed to start Duck server{bold_end}"
        is_reload = False
        
        if "--is-reload" in sys.argv:
            # App is being restarted somehow
            is_reload = True
            logger.log_raw("")
            
        if not is_reload and print_ansi_art and not SETTINGS["SILENT"]:
            display_duck_art()  # print duck art
            settings_mod = "DUCK_SETTINGS_MODULE"
            settings_mod = os.environ.get(settings_mod, 'settings')
            print(f"{bold_start}VERSION {version}{bold_end}")

        # Redirect all console output to log file
        if SETTINGS["LOG_TO_FILE"]:
            logger.Logger.redirect_console_output()
        
        # Log the current settings module in use
        settings_mod = "DUCK_SETTINGS_MODULE"
        settings_mod = os.environ.get(settings_mod, 'settings')
        logger.log_raw(f'{bold_start}USING SETTINGS{bold_end} "{settings_mod}" \n')
        
        if not SETTINGS['DEBUG'] and "*" in SETTINGS['ALLOWED_HOSTS']:
            logger.log("WARNING: ALLOWED_HOSTS seem to have global host (*)", level=logger.WARNING)
            
        if not self.is_domain_set:
            logger.log(
                f'WARNING: Domain not set, using "{self.domain}" ',
                level=logger.WARNING,
            )
        
        # Start WSGI background event loop if needed
        if not SETTINGS['ASYNC_HANDLING']:
            # Start threadpool for handling requests.
            ThreadPoolManager.start(
                daemon=True,
                thread_name_prefix="request-handler",
                task_type="request-handling",
            )
            
            if self.start_bg_event_loop_if_wsgi:
                # Start asyncio loop in background
                AsyncioLoopManager.start()
                logger.log(
                    "Background event loop started",
                    level=logger.DEBUG,
                )
            else:
                logger.log(
                    "App argument `start_bg_event_loop_if_wsgi` is set to False. "
                    "This may prevent protocols like `HTTP/2` or `WebSockets` from working correctly\n",
                    level=logger.WARNING,
                )
        else:
            # Start asyncio loop in background
            AsyncioLoopManager.start()
                        
        if SETTINGS['ENABLE_COMPONENT_SYSTEM']:
            # Components are enabled
            logger.log(
                "Lively Component System active"
                f"\n  └── Some components require JQuery & Bootstrap +icons ",
                level=logger.DEBUG,
            )
            
            # Check if CSP headers are set correctly for component system to run nicely.
            csp_directives = SETTINGS['CSP_TRUSTED_SOURCES']
            if SETTINGS['ENABLE_HEADERS_SECURITY_POLICY'] and csp_directives:
                script_src = set(csp_directives.get("script-src", []))
                style_src = set(csp_directives.get("style-src", []))
                
                # For components, we often need 'unsafe-eval' in script-src or default-src
                required_script_flags = {"'unsafe-eval'"}
                missing_script_flags = [
                    flag for flag in required_script_flags
                    if flag not in script_src
                ]
                
                # For styles, we often need 'unsafe-inline' in style-src
                required_style_flag = "'unsafe-inline'"
                
                if "'unsafe-eval'" not in script_src:
                    logger.log(
                        (
                            f"Component system active but script flag {'unsafe-eval'} is missing from script-src. "
                            "This may prevent JS execution from lively components."
                        ),
                        level=logger.WARNING,
                    )
                elif missing_script_flags:
                    logger.log(
                        (
                            f"Component system active but script flag(s) {', '.join(missing_script_flags)} are missing from script-src. "
                            "This may prevent dynamic components from loading correctly."
                        ),
                        level=logger.WARNING,
                    )
                elif csp_nonce_flag in style_src:
                    logger.log(
                        (
                            f"Component system active but `csp_nonce_flag` is in style-src. "
                            "This may block inline styles from components."
                        ),
                        level=logger.WARNING,
                    )
                elif required_style_flag not in style_src:
                    logger.log(
                        (
                            f"Component system active but flag {required_style_flag} is missing from style-src. "
                            "This may block inline styles from components."
                        ),
                        level=logger.WARNING,
                    )
                    
        if self.run_automations:
            # Start the automations dispatcher
            self.start_automations_dispatcher()
        
        # Start the main application server.    
        self.start_server()
        
        # Log some info message and sleep for 2 minutes.
        logger.log("Waiting 2s to read server state...", level=logger.DEBUG)
        time.sleep(2)

        # Check server start attempt
        if not self.server_up:
            logger.log(duck_start_failure_msg, level=logger.ERROR)
            self.stop()
            return
            
        if self.force_https:
            # Start force HTTPS redirect server & wait 2 seconds
            self.start_force_https_server()
            time.sleep(2)

            # Check force HTTPS server start attempt
            if not self.force_https_server_up:
                logger.log("HTTPS redirect app failed to start", level=logger.ERROR)
                self.stop()
                return

        if self.use_django:
            logger.log(
                "Requests will be forwarded to Django server",
                level=logger.DEBUG,
            )
            logger.log(
                f"Starting Django server on port [{SETTINGS['DJANGO_BIND_PORT']}]",
                level=logger.DEBUG,
            )

            if SETTINGS["DJANGO_COMMANDS_ON_STARTUP"]:
                try:
                    logger.log_raw("\n")
                    bridge.run_django_app_commands()
                except Exception as e:
                    logger.log(
                        f"Failed to run django commands: {e}\n",
                        level=logger.ERROR,
                    )
                    logger.log_exception(e)
                    self.stop()
                    return
            
            # Wait for Django server to start
            wait_t = self.DJANGO_SERVER_WAIT_TIME
            logger.log(
                f"Waiting for Django server to start ({wait_t} secs)\n",
                level=logger.DEBUG,
            )
            self.start_django_server()
            time.sleep(wait_t)

            # Check if django is running
            if not self.django_server_up:
                logger.log(f"Failed to get response from Django server [{wait_t} secs]", level=logger.ERROR)
                self.stop()
                return
                
            else:
                host_url = "http://" if not self.server.enable_ssl else "https://"
                host, port = self.server.addr
                
                if host.startswith("0") and not self.uses_ipv6:
                    # Convert host to browser's recognizeable
                    host = "127.0.0.1"
                else:
                    if self.uses_ipv6:
                        host = f"[{host}]"
                
                # Log some info
                host_url += f"{host}:{port}"
                #logger.log_raw("")
                logger.log(
                    "Django started yey, that's good!",
                    level=logger.DEBUG,
                    custom_color=logger.Fore.GREEN,
                )
                logger.log(
                    f"Duck Server listening on {host_url}",
                    level=logger.DEBUG,
                    custom_color=logger.Fore.GREEN,
                )
                
        # Call on_app_start handler
        self.on_app_start()


if __name__ == "__main__":
    multiprocessing.freeze_support()
