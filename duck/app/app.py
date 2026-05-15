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
"""

import os
import sys
import json
import time
import signal
import threading
import setproctitle
import multiprocessing

from typing import (
    Optional,
    Dict,
    Any,
    Union,
)
from concurrent.futures import Future

from duck.settings import SETTINGS
from duck.settings.loaded import SettingsLoaded
from duck.exceptions.all import (
    SSLError,
    ApplicationError,
    SettingsError,
)
from duck.http.core.httpd.servers import HTTPServer
from duck.logging import logger
from duck.meta import Meta
from duck.csp import csp_nonce_flag
from duck.art import display_duck_art
from duck.version import version
from duck.utils.lazy import Lazy
from duck.utils.asyncio.eventloop import get_or_create_loop_manager
from duck.utils.threading.threadpool import get_or_create_thread_manager
from duck.app.base import BaseApp


class App(BaseApp):
    """
    Initializes and configures the **Duck** application.
    """
    DEFAULT_ADDR = "localhost"
    DEFAULT_PORT = 8000
    
    __instances__ = 0
    __mainapp__ = None
    
    def __init__(
        self,
        name: Optional[str] = None,
        
        # Network configuration
        addr: str = DEFAULT_ADDR,
        port: int = DEFAULT_PORT,
        domain: Optional[str] = None,
        server_url: Optional[str] = None,
        uses_ipv6: bool = False,
    
        # Process configuration
        process_name: Optional[str] = None,
        workers: Optional[int] = None,
        force_worker_processes: bool = False,
    
        # HTTPS redirect server
        https_redirect_logs: bool = False,
        https_redirect_workers: Optional[int] = None,
        https_redirect_force_worker_processes: bool = False,
    
        # Runtime behavior
        start_bg_eventloop_if_wsgi: bool = True,
        disable_signal_handler: bool = False,
        disable_ipc_handler: bool = False,
    
        # Development / internal flags
        no_checks: bool = False,
        skip_setup: bool = False,
    ) -> None:
        """
        Initialize the main Duck application instance.
        
        Sets up the application runtime, networking configuration, worker handling,
        HTTPS redirect support, and internal runtime services.
        
        Args:
            name:
                Optional application name.
                
            addr:
                Address or hostname to bind the server to.
        
            port:
                Port to bind the server to.
        
            domain:
                Public-facing domain name for the application. If not provided,
                the bound address is used.
            
            server_url:
                Optional public-facing absolute server URL.
            
            uses_ipv6:
                Whether to use IPv6 networking.
        
            process_name:
                Optional process name used for runtime identification.
        
            no_checks:
                Whether to skip startup and environment checks.
        
            skip_setup:
                Whether to skip automatic framework setup such as URL and
                blueprint registration.
        
            disable_signal_handler:
                Whether to disable OS signal handlers.
        
            disable_ipc_handler:
                Whether to disable the internal IPC handler.
        
            start_bg_eventloop_if_wsgi:
                Whether to start a background asyncio event loop when running
                in a WSGI environment. This allows async protocols such as
                WebSockets and HTTP/2 to run under WSGI.
        
            workers:
                Number of workers to use for the main application server.
                `None` disables workers.
        
            force_worker_processes:
                Whether to use worker processes instead of threads for the
                main application server.
        
                By default, Duck uses threads because they avoid cross-process
                synchronization issues involving shared in-memory state such as
                component registries.
        
                Enable this only when process isolation is explicitly required.
        
            https_redirect_logs:
                Whether to enable console logs for the HTTPS redirect server.
        
            https_redirect_workers:
                Number of workers to use for the HTTPS redirect server.
                `None` disables workers.
        
            https_redirect_force_worker_processes:
                Whether to use worker processes instead of threads for the
                HTTPS redirect server.
        
        Raises:
            ApplicationError:
                Raised if the provided address is invalid or if multiple
                main application instances are created.
        
        Notes:
            - Only one main `App` instance should exist per process.
              Use `MicroApp` for additional services or sub-applications.
        
            - Disabling the IPC handler is intended mainly for testing.
              In normal environments, the IPC handler keeps the runtime
              alive and coordinated correctly.
        """
        from duck.utils.threading.threadpool import get_or_create_thread_manager
        from duck.app.microapp import HttpsRedirectMicroApp
        
        # Runtime behavior
        self.skip_setup = skip_setup
        self.disable_signal_handler = disable_signal_handler
        self.disable_ipc_handler = disable_ipc_handler
        self.start_bg_eventloop_if_wsgi = start_bg_eventloop_if_wsgi
        
        # Process configuration
        self.process_name = process_name or "duck-server"
        
        # Django configuration
        self.use_django = SETTINGS["USE_DJANGO"]
        self.django_server_wait_time = SETTINGS["DJANGO_SERVER_WAIT_TIME"]
        self.django_addr = addr
        self.django_bind_port = SETTINGS["DJANGO_BIND_PORT"]
        
        # HTTPS redirect configuration
        self.https_redirect = SETTINGS["HTTPS_REDIRECT"]
        self.https_redirect_addr = addr
        self.https_redirect_port = SETTINGS["HTTPS_REDIRECT_BIND_PORT"]
        self.https_redirect_logs = https_redirect_logs
        self.https_redirect_workers = https_redirect_workers
        self.https_redirect_force_worker_processes = https_redirect_force_worker_processes
        
        # Automation configuration
        self.run_automations = SETTINGS["RUN_AUTOMATIONS"]

        # Runtime objects
        self.automations_dispatcher = None
        self.ducksight_reloader = None
        self.https_redirect_app = None
        
        # Concurrent futures / threads
        self.server_future = None
        self.django_server_future = None
        self.automations_dispatcher_future = None
        self.ducksight_reloader_thread = None
        
        # Child processes
        self.https_redirect_process = None
        
        # Runtime executor
        self.runtime_executor = get_or_create_thread_manager(id="app-runtime-executor")
        
        # Super initialize
        super().__init__(
            name=name,
            addr=addr,
            port=port,
            domain=domain,
            server_url=server_url,
            uses_ipv6=uses_ipv6,
            enable_https=SETTINGS['ENABLE_HTTPS'],
            no_checks=no_checks,
            workers=workers,
            force_worker_processes=force_worker_processes,
        )
        
        # HTTPS redirect app
        if self.https_redirect:
            self.https_redirect_app = Lazy(
                HttpsRedirectMicroApp,
                server_url=self.server_url,
                addr=self.https_redirect_addr,
                port=self.https_redirect_port,
                domain=self.domain,
                uses_ipv6=self.uses_ipv6,
                enable_https=False,
                no_logs=not self.https_redirect_logs,
                workers=self.https_redirect_workers,
                force_worker_processes=self.https_redirect_force_worker_processes,
            )
            
            # Set HTTPS redirect state.
            self.https_redirect_process_running_state = multiprocessing.Value("i", 0)
        
        # Main HTTP server
        self.server = HTTPServer(
            (addr, port),
            application=self,
            domain=self.domain,
            uses_ipv6=self.uses_ipv6,
            enable_ssl=self.enable_https,
            no_logs=False,
            workers=self.workers,
            force_worker_processes=self.force_worker_processes,
        )
        
        # Process setup
        self.set_process_name()
        
        # Main app singleton guard
        if type(self).__instances__ > 0:
            raise ApplicationError(
                "Application limit reached: only one main application is permitted. "
                "Use MicroApp for additional services or sub-applications."
            )
        
        type(self).__instances__ += 1
        type(self).__mainapp__ = self

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
    def start_background_workers(
        application: BaseApp,
        start_request_handling_threadpool_manager,
        start_request_handling_eventloop_manager,
        start_component_threadpool_manager: bool = True,
        start_automations_eventloop_manager: bool = False,
        recreate_managers: bool = False,
    ):
        """
        Starts or restarts background workers, e.g. `AsyncioLoopManager` & `ThreadPoolManager`.
        
        Args:
            application (BaseApp): The target application.
            start_request_handling_threadpool_manager (bool): Whether to start request handling threadpool in `WSGI` environment. This is only valid in WSGI environment only.
            start_request_handling_eventloop_manager (bool): Whether to start asyncio event loop either in `WSGI` or `ASGI` environment.
            start_component_threadpool_manager (bool): Whether to start the background threadpool manager for HTML components rendering, assistance, etc. Defaults to True.
            start_automations_eventloop_manager (bool): Whether to start a dedicated event loop for running automations. Defaults to False.
            recreate_managers (bool): Whether to recreate managers for the current thread and all it's descendents. Defaults to False.
                This argument doesn't affect argument `start_automations_eventloop_manager`. Argument `recreate_managers` only applies to 
                every other manager except the automations eventloop manager.
            
        Notes:
        - This is usually useful when starting new worker processes/threads.
        - Use methods `get_or_create_loop_manager` and `get_or_create_thread_manager` to create new managers before this function if 
          new managers are needed.
        - This only focus on default `AsyncioLoopManager` & `ThreadPoolManager`.
        - The thread manager is only run in `WSGI` mode but loop manager can be run in any environment (ASGI or WSGI).
         """
        from duck.utils.threading import get_max_workers
        from duck.setup import set_asyncio_loop
        
        _async = SETTINGS['ASYNC_HANDLING']
        start_bg_eventloop_if_wsgi = getattr(application, "start_bg_eventloop_if_wsgi", True)
        max_threadpool_workers = get_max_workers()
        
        if _async and start_request_handling_threadpool_manager:
            raise ApplicationError("Argument 'start_request_handling_threadpool_manager' can only be True in a WSGI environment.")
        
        if not _async and start_request_handling_eventloop_manager and not start_bg_eventloop_if_wsgi:
            raise ApplicationError("Argument 'start_request_handling_threadpool_manager' can only be True if app's `start_bg_eventloop_if_wsgi` is set to True.")
            
        if multiprocessing.parent_process() is not None:
            # Not in main process; this is a child process.
            # Reset asyncio event loop
            set_asyncio_loop()
        
        # This block is not affected by recreate managers.
        if start_automations_eventloop_manager:
            loop_manager = get_or_create_loop_manager(id="automations-eventloop-manager")
            loop_manager.start() # Do not restrict task types for automations
        
        # Start component threadpool manager    
        if start_component_threadpool_manager:
            component_threadpool_manager = get_or_create_thread_manager(id="component-threadpool-manager", force_create=recreate_managers)
            component_threadpool_manager.start(
                task_type="component-task", # Restrict task to only `component-task` type.
                max_workers=int(max_threadpool_workers / 2),
                daemon=True,
                thread_name_prefix="component-task",
            )
            
        # In WSGI environment
        if not _async:
            if start_request_handling_threadpool_manager:
                # Start request handling threadpool
                request_handling_threadpool_manager = get_or_create_thread_manager(id="request-handling-threadpool-manager", force_create=recreate_managers)
                request_handling_threadpool_manager.start(
                    task_type="request-handling-task", # Restrict task to only `request-handling-task` type.
                    max_workers=max_threadpool_workers,
                    daemon=True,
                    thread_name_prefix="request-handling-task",
                )
            
        # In any environment WSGI/ASGI
        if start_request_handling_eventloop_manager:
            request_handling_loop_manager = get_or_create_loop_manager(id="request-handling-eventloop-manager", force_create=recreate_managers)
            request_handling_loop_manager.start(task_type="request-handling-task") # Restrict to only request handling tasks
                
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
    def meta(self) -> Dict[str, Any]:
        """
        Get global application metadata.
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
        Returns application server absolute `URL` - this is fetched using `duck.meta.Meta`.
        """
        return Meta.get_absolute_server_url()
        
    @property
    def absolute_ws_uri(self) -> str:
        """
        Returns application server absolute WebSockets `URL` - this is fetched using `duck.meta.Meta`.
        """
        return Meta.get_absolute_ws_server_url()

    @property
    def django_server_up(self) -> bool:
        """
        Checks whether django server to forward requests to has started

        Returns:
            started (bool): True if up else False
        """
        import requests

        try:
            host_addr, port = self.django_addr
            
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
            
            _ = requests.get(
                url=url,
                headers={"Host": SETTINGS["DJANGO_SHARED_SECRET_DOMAIN"]},
                timeout=1,
            )

            # If we reached here, a response has been received
            return True
        except Exception:
            pass
        return False

    @property
    def https_redirect_server_up(self) -> bool:
        """
        Checks whether HTTPS redirect micro application is running.

        Returns:
            bool: True if up else False
        """
        if self.https_redirect_process:
            if self.https_redirect_process.is_alive():
                return bool(self.https_redirect_process_running_state.value)
            else:
                return False
        else:
            return self.https_redirect_app.server.running
               
    def register_ports(self):
        """
        Register occupied ports.
        """
        from duck.utils.port_registry import PortRegistry
        
        super().register_ports()
        
        if self.use_django:
            PortRegistry.register_port(self.django_bind_port, "DJANGO_BIND_PORT")
        
    def run_checks(self):
        """
        Runs application checks.
        """
        if self.enable_https:
            self.check_ssl_credentials()
            
    def set_process_name(self):
        """
        Set the whole process name.
        """
        setproctitle.setproctitle(self.process_name)
    
    def register_signals(self):
        """
        Register and bind signals to appropriate signal handler.
        """
        signal.signal(signal.SIGINT, self.handle_signal)
        signal.signal(signal.SIGTERM, self.handle_signal)
        
    def handle_signal(self, sig, frame):
        """
        Method for handling process signals.

        Signals:
        - `SIGINT` (Ctrl-C), `SIGTERM` (Terminate): Quits the server/application.
        """
        if sig in [signal.SIGINT, signal.SIGTERM]:
            self.stop(wait_for_runtime_executor_shutdown=False)
            
    def handle_ipc_messages(self):
        """
        Handles incoming IPC messages from the shared file.
        
        Notes:
        - This usually holds the main process from exiting because of the blocking behavior.
        """
        from duck.utils import ipc
        
        with ipc.get_reader() as reader:
            with ipc.get_writer() as writer:
                # Clear IPC writer file
                writer.write_message("")  # Clear ipc shared file
            
            while True:
                # Handle any incoming message.
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
            "DUCK_SERVER_URL": self.server_url,
            "DUCK_SERVER_NAME": "webserver",
            "DUCK_SERVER_PORT": self.port,
            "DUCK_SERVER_DOMAIN": self.domain,
            "DUCK_SERVER_PROTOCOL": ("https" if self.enable_https else "http"),
            "DUCK_DJANGO_ADDR": self.django_addr,
            "DUCK_USES_IPV6": self.uses_ipv6,
            "DUCK_SERVER_BUFFER": SETTINGS["SERVER_BUFFER"],
            "DUCK_WORKERS": int(self.workers or 0), # Meta.update doesnt support NoneType
        }
        
        # Update global metadata.
        Meta.update_meta(data)
    
    def start_server(self) -> None:
        """
        Starts the app server in new thread.
        """  
        if not self.server_future or not self.server_future.running():
            self.server_future = self.runtime_executor.submit_task(self.server.start_server)
                
    def start_django_server(self) -> None:
        """
        Starts Django server and use Duck as reverse proxy server for Django.
        """
        from duck.backend.django import bridge
        
        # We were starting Django in new process but we shouldn't because it isolates 
        # memory spaces which may make using Lively component system at Django side difficult.
        # If we used a new process, synchronization between django process and main process Lively Component System registry 
        # is almost impossible now. This can lead to components not found all the time.
        
        def start_django_server():
            """
            Starts Django application server
            """
            # Set the host to start Django on.
            host = self.django_addr
            
            # Start django server
            bridge.start_django_server(*host, uses_ipv6=self.uses_ipv6)
            
        if self.use_django:
            if not self.django_server_future or not self.django_server_future.is_running():
                self.django_server_future = self.runtime_executor.submit_task(start_django_server)
                
    def start_https_redirect_server(self, log_message: bool = True):
        """
        Starts HTTPS redirect micro application in a new process.  
        
        Args:
            log_message (bool): Whether to log something before starting the micro app.
        """
        def start_https_redirect(process_safe_running_state: multiprocessing.Value):
            """
            Starts app for redirecting non encrypted traffic to main app using https.
            """
            p = multiprocessing.current_process()
            
            # Set process name.
            setproctitle.setproctitle(p.name)
            
            # Register signal handler
            signal.signal(signal.SIGINT, lambda *a: self.https_redirect_app.stop())
            
            # Restart background workers
            # Recreate managers recreates and attaches new managers fot the current 
            # thread and all its descendents.
            
            # Restart only request handling threadpool/eventloop manager
            _async = SETTINGS['ASYNC_HANDLING']
            start_bg_eventloop_if_wsgi = getattr(self, "start_bg_eventloop_if_wsgi", True)
            start_eventloop = _async or (not _async and start_bg_eventloop_if_wsgi)
            
            App.start_background_workers(
                self,
                start_request_handling_threadpool_manager=not _async,
                start_request_handling_eventloop_manager=start_eventloop,
                start_component_threadpool_manager=False,
                start_automations_eventloop_manager=False,    
                recreate_managers=True,
            )
            
            # Start the microapp
            self.https_redirect_app.on_app_start = lambda: setattr(process_safe_running_state, 'value', int(self.https_redirect_app.server.running))
            self.https_redirect_app.run(run_forever=True) # This is blocking; run_forever=True is blocking.
            
        if self.https_redirect:
            # Log something if applicable.
            if log_message:
                logger.log(
                    f"Redirecting incoming HTTP traffic [{self.https_redirect_port} -> {self.port}]",
                    level=logger.DEBUG,
                )
                
            # Start HTTP redirect process
            if not self.https_redirect_process or not self.https_redirect_process.is_alive():
                self.https_redirect_process = multiprocessing.Process(
                    target=start_https_redirect,
                    name="duck-https-redirect-server",
                    args=(self.https_redirect_process_running_state, ),
                )
                
                # Start the HTTPS redirect process
                self.https_redirect_process.start()
    
    def start_automations_dispatcher(self, log_message: bool = True):
        """
        Starts automations dispatcher for executing automations during runtime.
        
        Args:
            log_message (bool): Whether to log something before starting the micro app.
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
            
            # Start automations dispatcher
            self.automations_dispatcher.start()
                
        if self.run_automations:
            # Submit task to the pool
            if not self.automations_dispatcher_future or not self.automations_dispatcher_future.running():
                self.automations_dispatcher_future = self.runtime_executor.submit_task(start_automations_dispatcher)
                        
    def start_ducksight_reloader(self):
        """
        Starts the DuckSight Reloader for reloading app on file modifications, deletions, etc.
        
        Notes:
        - Unlike other tasks like starting Duck server, HTTPS redirect server, etc which will be run by the app's `runtime_executor`,
          this runs in an independant background thread with `daemon=True`.
        """
        from duck.contrib.reloader.ducksight import DuckSightReloader
        
        # Note: Production server should not be restarted at any point only start duck sight reloader on DEBUG
        def start_reloader():
            """
            Start the app's reloader.'
            """
            if not self.ducksight_reloader:
                self.ducksight_reloader = DuckSightReloader(SETTINGS['BASE_DIR'])
            self.ducksight_reloader.run()
            
        if SETTINGS["DEBUG"] and SETTINGS['AUTO_RELOAD']:
            if not self.ducksight_reloader_thread or not self.ducksight_reloader_thread.is_alive():
                if not self.ducksight_reloader_thread:
                    self.ducksight_reloader_thread = threading.Thread(target=start_reloader)
                self.ducksight_reloader_thread.start()
                            
    def get_runtime_futures(self) -> Dict[str, Optional[Future]]:
        """
        Returns a dictionary of all application runtime concurrent futures.
        
        Notes:
        - The `DuckSightReloader` task is run on an independent thread, so no future for it will be included.
        """
        return {
            "duck_server": self.server_future,
            "automations_dispatcher": self.automations_dispatcher_future,
            "django_server": self.django_server_future,
        }
        
    def on_app_start(self):
        """
        Event called when application has successfully been started.
        """
        from duck import processes
        
        # Record main process data
        log_file = None
            
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
            pass  # Ignore for now, maybe writting is still in progress
        
        if not self.disable_signal_handler:
            self.register_signals()  # bind signals to appropriate signal handlers
            logger.log(
                f"Use Ctrl-C to quit [APP PID: {self.process_id}]",
                level=logger.DEBUG,
                custom_color=logger.Fore.GREEN,
            ) 
        
        if SETTINGS["AUTO_RELOAD"] and SETTINGS["DEBUG"]:
            # Start duck sight reloader (if not running)
            self.start_ducksight_reloader()
            logger.log(
                "Duck Sight Reloader watching file changes",
                level=logger.DEBUG,
                custom_color=logger.Fore.GREEN,
            )
        
        # Log a success message
        logger.log(
            "Waiting for incoming requests :-) \n",
            level=logger.DEBUG,
            custom_color=logger.Fore.GREEN,
        )
        
        if not self.disable_ipc_handler:
            # Handle any incoming IPC messages.
            # This is a blocking operation, it prevents app from exiting.
            self.handle_ipc_messages()
            
    def on_pre_stop(self):
        """
        Event called before final application termination.
        """
        pass
        
    def run(self, print_ansi_art: bool = True):
        """
        Runs the Duck application.
        """
        from duck.setup import setup
        
        if not self.skip_setup:
            # Setup Duck environment and the entire application.
            setup()
            
        # Record application metadata and run the server
        self.record_metadata()
        
        # Start runtime executor
        self.runtime_executor.start(max_workers=5)
        
        # Run the main application
        return self._run(print_ansi_art=print_ansi_art)
        
    def stop_servers(
        self,
        stop_https_redirect_server: bool = True,
        log_to_console: bool = True,
        wait: bool = True,
    ):
        """
        Stop all running servers i.e., Duck main server, HTTPS redirect server & Django server.

        Args:
            stop_https_redirect_server (bool): Whether to stop HTTPS redirect microapp server.
            log_to_console (bool): Whether to an exit message log to console.
            wait (bool): Whether to wait for termination. Defaults to True but with a timeout.
        """
        self.server.stop_server(log_to_console=log_to_console, wait=wait)
        
        if (
            stop_https_redirect_server
            and self.https_redirect_process
            and self.https_redirect_process.is_alive()
        ):
            self.https_redirect_process.terminate()
            
            if wait:
                # Wait for termination
                self.https_redirect_process.join(1)
    
    def stop(
        self,
        log_to_console: bool = True,
        no_exit: bool = False,
        call_on_pre_stop_handler: bool = True,
        kill_ducksight_reloader: bool = True,
        wait_for_runtime_executor_shutdown: bool = True,
        close_log_file: bool = True,
    ):
        """
        Stops the application and terminates the whole program.

        Args:
            no_exit (bool): Whether to terminate everything but keep the program running.
            log_to_console (bool): Whether to log an exit message.
            call_on_pre_stop_handler (bool): Whether to call method `on_pre_stop`. Defaults to True.
            kill_ducksight_reloader (bool): This attempts to kill the `DuckSightReloader`. Useful if `no_exit=True`,
            wait_for_runtime_executor_shutdown (bool): Whether to wait for the runtime executor to complete shutdown. 
                                                                                            This mean waiting for current tasks to finish/cancel.
                                                                                            This is only used if argument `no_exit=True` else it is automatically `False`.
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
                    
        # Call on_pre_stop event
        if call_on_pre_stop_handler:
            self.on_pre_stop()
        
        try:
            # Close the session storage connector in new thread
            SettingsLoaded.SESSION_STORAGE_CONNECTOR.close()
        except Exception as e:
            logger.log_raw('\n')
            logger.log(f"Error closing session storage: {e}", level=logger.WARNING)

        try:
            # Stop all started servers
            self.stop_servers(log_to_console=log_to_console, wait=wait_for_runtime_executor_shutdown if no_exit else False)
        except Exception as e:
            logger.log_raw('\n')
            logger.log(f"Error stopping servers: {e}", level=logger.ERROR)
            
            if SETTINGS['DEBUG']:
                logger.log_exception(e)
                
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
        concurrent_futures = self.get_runtime_futures()
        
        for name, future in concurrent_futures.items():
            stop_future(future)
        
        # Shutdown runtime executor if not stopped.            
        if self.runtime_executor:
            try:
                self.runtime_executor.stop(wait=wait_for_runtime_executor_shutdown if no_exit else False)
            except Exception as e:
                logger.log_exception(e)
        
        if (
            no_exit
            and kill_ducksight_reloader
            and wait_for_runtime_executor_shutdown
        ):
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
    
    def _run(self, print_ansi_art: bool = True):
        """
        Runs the Duck application.
        """
        from duck.contrib.sync.smart_async import _TRANSACTION_THREAD_POOL
        from duck.art import display_duck_art
        
        # Fine tune threadpool for executing sync_to_async calls
        default_sync_to_async_workers = _TRANSACTION_THREAD_POOL.max_threads
        
        # Update max_threads according to app workers
        _TRANSACTION_THREAD_POOL.max_threads = (default_sync_to_async_workers * self.workers) if self.workers else default_sync_to_async_workers
                
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
            # Display duck art
            display_duck_art()
            
            # Print some app start header
            settings_mod = "DUCK_SETTINGS_MODULE"
            settings_mod = os.environ.get(settings_mod, 'settings')
            (f"{bold_start}VERSION {version}{bold_end}")

        if SETTINGS["LOG_TO_FILE"]:
            # Redirect all console output to log file
            logger.Logger.redirect_console_output()
        
        # Log the current settings module in use
        settings_mod = "DUCK_SETTINGS_MODULE"
        settings_mod = os.environ.get(settings_mod, 'settings')
        logger.log_raw(f'{bold_start}USING SETTINGS{bold_end} "{settings_mod}" \n')
        
        if not SETTINGS['DEBUG'] and "*" in SETTINGS['ALLOWED_HOSTS']:
            logger.log("WARNING: ALLOWED_HOSTS seem to have global host (*)", level=logger.WARNING)
            
        if not self.original_domain:
            logger.log(
                f'WARNING: Domain not set, using "{self.domain}" ',
                level=logger.WARNING,
            )
        
        # Start background event loop or threadpool if needed
        if self.workers:
            # We are using workers, so eventloops or threadpools will be
            # started by httpd.httpd.start_server.start_server_loop_in_worker.
            
            # Only start automations asyncio loop (if applicable) that will be run in background outside worker
            App.start_background_workers(
                self,
                start_request_handling_threadpool_manager=False,
                start_request_handling_eventloop_manager=False,
                start_component_threadpool_manager=False,
                start_automations_eventloop_manager=True,    
            )
        else:
            # No worker processes/threads will be responsible for starting the threads/asyncio loop manager for us
            # Start everything that needs to be started
            _async = SETTINGS['ASYNC_HANDLING']
            start_bg_eventloop_if_wsgi = getattr(self, "start_bg_eventloop_if_wsgi", True)
            start_eventloop = _async or (not _async and start_bg_eventloop_if_wsgi)
            
            App.start_background_workers(
                self,
                start_request_handling_threadpool_manager=not _async,
                start_request_handling_eventloop_manager=start_eventloop,
                start_component_threadpool_manager=True,
                start_automations_eventloop_manager=True,    
            )
            
        if not SETTINGS['ASYNC_HANDLING']:
            if self.start_bg_eventloop_if_wsgi:
                # Started asyncio loop in background
                logger.log(
                    "Background event loop scheduled",
                    level=logger.DEBUG,
                )
            else:
                logger.log(
                    "App argument `start_bg_eventloop_if_wsgi` is set to False. "
                    "This may prevent protocols like `HTTP/2` or `WebSockets` from working correctly\n",
                    level=logger.WARNING,
                )
        
        if SETTINGS['ENABLE_COMPONENT_SYSTEM']:
            # Components are enabled
            logger.log("Lively Component System active", level=logger.DEBUG)
            
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
                            "Component system active but `csp_nonce_flag` is in style-src. "
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
        logger.log("Waiting 1s to read server state...", level=logger.DEBUG)
        time.sleep(1)

        # Check server start attempt
        if not self.server_up:
            logger.log(duck_start_failure_msg, level=logger.ERROR)
            self.stop()
            return
            
        if self.https_redirect:
            # Start HTTPS redirect server & wait 1 second
            self.start_https_redirect_server()
            time.sleep(1)

            # Check HTTPS redirect server start attempt
            if not self.https_redirect_server_up:
                logger.log("HTTPS redirect app failed to start", level=logger.ERROR)
                self.stop()
                return

        if self.use_django:
            logger.log(
                "Requests will be forwarded to Django server",
                level=logger.DEBUG,
            )
            logger.log(
                f"Starting Django server on port [self.django_port]",
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
            wait_t = self.django_server_wait_time
            logger.log(f"Waiting for Django server to start ({wait_t} secs)\n", level=logger.DEBUG)
            self.start_django_server()
            
            # Wait a little bit.
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
