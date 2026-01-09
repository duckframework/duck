# 🛠 Settings Configuration

## Understanding `settings.py`

The `settings.py` file serves as the central configuration hub for your **Duck** web application. It defines crucial settings that control the behavior, security, and performance of your project.

Below is a complete configuration example of `settings.py` and an overview of its key components.

``` {note}  
You don’t need to define every setting from the example below. Instead, use it as a reference to understand Duck's configuration options.
```

```py
"""
File containing settings for Duck application.
"""
# yapf: disable
import os
import sys
import json
import pathlib
import socket

from duck.html.components.utils.include import (
    BUILTIN_COMPONENTS,
    components_include,
)
from duck.etc.middlewares import middlewares
from duck.etc.normalizers import normalizers
from duck.secrets import DUCK_SECRET, SECRET_DOMAIN
from duck.storage import duck_storage, BaseDir
from duck.csp import csp_nonce_flag
from duck.utils.path import joinpaths


# Base directory where the Duck application is running from
BASE_DIR: str | pathlib.Path = BaseDir()


# SECURITY WARNING: Keep the secret key used in production secret!
# Modify this for your own secure secret key. Defaults to random secret key on every Duck launch.
SECRET_KEY: str = os.environ.get("DUCK_SECRET_KEY", DUCK_SECRET)


# Debug Mode
# Specifies whether to run the server in debug mode.
# - In debug mode (`DEBUG=True`), the DuckSight Reloader is enabled, and default Duck views are automatically registered.
# - When `DEBUG=False` (recommended for production):
#   - Default Duck views are not registered at any URL, except for `MEDIA_URL` and `STATIC_URL` if applicable.
#   - You must define and register your own URLs by adding `path` or `re_path` entries in the `urlpatterns` list in `urls.py`.
DEBUG: bool = True


# Allowed Hosts, Wildcards Allowed
ALLOWED_HOSTS: list[str] = ["*"]


# Module for urlpatterns definition.
URLPATTERNS_MODULE: str = "web.urls"


# Blueprints
# Blueprints are more Flask's blueprints for organizing routes.
# **Note**: The blueprint name will determine the entire route, e.g.
# For route `/home` and blueprint with name `products`, the final route will be `/products/home`. This behavior can be disabled by setting argument `prepend_name_to_url` to False.
# The best way to maximize usage of blueprints, create subfolders within base directory and create blueprints and their related views in those subfolders for good project organization.
BLUEPRINTS: list[str] = [
    "duck.etc.apps.essentials.blueprint.MediaFiles",
    "duck.etc.apps.essentials.blueprint.StaticFiles",
]


# List of all middlewares as strings in form "middleware.MiddlewareClass"
# WARNING: The middlewares should be arranged in order at this point.
MIDDLEWARES: list[str] = middlewares


# Middleware Failure default behavior.
# This setting determines the action when a Request fails to meet the conditions to pass through the middleware.
# It defaults to 'block' to block all requests that fail to satisfy any middleware conditions thereby returning appropriate error response.
# Available options: "block", "ignore"
MIDDLEWARE_FAILURE_BEHAVIOR: str = "block"


#  Request Normalizers
# These Normalizers accept a Request object as an argument and return the Request object with normalized attributes.
NORMALIZERS: list[str] = normalizers


# Ignore Normalization Errors
# Whether to ignore errors raised from trying to normalize request.
IGNORE_NORMALIZATION_ERRORS: bool = True


# Response Content Compression
# Whether to compress response content
# Note: If a backend server like Django is used, then content compression will depend on that server.
CONTENT_COMPRESSION: dict[str] = {
    "encoding": "gzip",
    "min_size": 1024,  # files more than 1KB
    "max_size": 512 * 1024,  # files not more than 512KB
    "level": 5,
    "compress_streaming_responses": True, # Whether to compress streaming http responses.
    "vary_on": True,  # Whether to include Vary header in response
    "mimetypes": [
        "text/*",
        "application/javascript",
        "application/json",
        "application/xml",
        "application/xhtml+xml",
        "application/rss+xml",
        "application/atom+xml",
    ],  # avoid compressing already compressed files like images
}


# Enable Content Compression
# Specifies whether to enable content compression for responses.
ENABLE_CONTENT_COMPRESSION: bool = True


# AUTOMATION SETTINGS

# Automations you would like to run when the application is running.
# This is a mapping of Automation objects as a string to a dictionary with only one allowed key, ie. `trigger`.
# The key `trigger` can be either a class or an object.
# Do help on duck.automations for more info.
AUTOMATIONS: dict[str, dict[str, str]] = {
    #"duck.automation.SampleAutomation": {
    #   "trigger": "duck.automation.trigger.NoTrigger",
    # }
}


# Automation Dispatcher Configuration
# Specifies the class responsible for dispatching automations.
# - You can use a custom dispatcher by subclassing the `AutomationDispatcher` class and implementing the `listen` method.
AUTOMATION_DISPATCHER: str = "duck.automation.dispatcher.DispatcherV1"


# Run Automations Configuration
# Specifies whether to execute automations when the main application is deployed.
# - When `RUN_AUTOMATIONS=True`, automations will run automatically during deployment.
RUN_AUTOMATIONS: bool = True


# Support HTTP/2 Protocol
SUPPORT_HTTP_2: bool = True


# HTTPS
# Specifies whether to enable HTTPS for the server.
# - When `ENABLE_HTTPS=True`, HTTPS is enabled on the specified port.
# - Ensure you have valid SSL certificates configured for secure communication.
ENABLE_HTTPS: bool = False


# Force HTTPS
# Enforces HTTPS by redirecting unencrypted HTTP traffic to HTTPS.
# - When `FORCE_HTTPS=True`, all HTTP requests will be redirected to HTTPS.
FORCE_HTTPS: bool = False


# Force HTTPS Bind Port
# Specifies the port for the redirection app to handle HTTP to HTTPS redirection.
# - This port will listen for unencrypted traffic and redirect it to the HTTPS-enabled app.
FORCE_HTTPS_BIND_PORT: int = 8080


# Web Server Gateway Interface (WSGI) to use within Duck.
# **Caution**: Changing WSGI may result in unexpected behavior for logging if not handled correctly.
# This wsgi is responsible for processing requests, generating response and sending it to the client unlike other
# WSGI which only generate response but does'nt send it to client.
WSGI: str = "duck.http.core.wsgi.WSGI"


# Asynchronous Server Gateway Interface (ASGI) to use within Duck.
# **Caution**: Changing ASGI may result in unexpected behavior for logging if not handled correctly.
# This asgi is responsible for asynchronously processing requests, generating response and sending it to the client unlike other
# ASGI which only generate response but doesn't send it to client.
ASGI: str = "duck.http.core.asgi.ASGI"


# Asynchronous Request Handling
# Determines whether to use asynchronous request handling.
# If set to False, the framework defaults to multithreaded request handling.
# Example: ASYNC_HANDLING=True enables async handling; False uses threads.
ASYNC_HANDLING: bool = False


# Async Event Loop
# Specifies which asynchronous event loop backend to use.
# Options may include: "asyncio" (default), "uvloop"
ASYNC_LOOP: str = "asyncio"



# Enable Lively Component System
# This enables:
#    1. HTML components usage in templates.
#    2. Real-time component updates for fast & reactive UI.
ENABLE_COMPONENT_SYSTEM: bool = True


# Reload On Unknown Components
# Whether to reload pages when a requested Lively component is not found or expired.
RELOAD_ON_UNKNOWN_COMPONENTS: bool = True


# Template Lively HTML Components
# Components to include in templates.
# Uncomment to enable default builtin components or add yours!
# TEMPLATE_HTML_COMPONENTS: dict[str, str] = {
#    "Button": "duck.html.components.button.Button", # example
#    **components_include(BUILTIN_COMPONENTS),
# }


# Template Dirs
# Global Directories to lookup templates
# Blueprint template dirs will be resolved automatically, no need to be included here.
TEMPLATE_DIRS: list[str | pathlib.Path] = [pathlib.Path("web/ui/templates/").resolve()]


# Module which contains Custom Template Tags or Filters
# Set to '' to disable custom tags or filters
TEMPLATETAGS_MODULE: str = ""


# Custom Templates
# These are custom templates you might want to use for different various status codes
# This maps status codes to callables which are responsible for generating new responses.
# The following are the arguments parsed to custom template callables:
#     current_response: The HTTP response object containing the preprocessed response.
#     request (optional): The corresponding request, can be None if the response was generated at a lower level before the request data was processed.
CUSTOM_TEMPLATES: dict = {
    # Example:
    # 404: lambda current_response, request: "The 404 response was overridden"
}


# Security Headers (loaded from JSON files)
# These headers are added to every response by default.
# The headers are loaded from the JSON file specified in the path.
with open(joinpaths(duck_storage, "etc/headers/default.json")) as fd:
    SECURITY_HEADERS: dict = json.load(fd)


# Security Headers for HTTPS (loaded from JSON file)
with open(joinpaths(duck_storage, "etc/headers/default_ssl.json")) as fd:
    SSL_SECURITY_HEADERS: dict = json.load(fd)


# Extra Headers
EXTRA_HEADERS: dict = {}


# CORS Headers
CORS_HEADERS: dict = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, PUT, PATCH, DELETE, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization",
    "Access-Control-Allow-Credentials": "true",
    "Access-Control-Max-Age": "86400",
}


# Content Security Policy (CSP) trusted sources
#
# When ENABLE_HEADERS_SECURITY_POLICY is True, this dictionary builds the
# 'Content-Security-Policy' HTTP header for your app.
#
# Each key is a CSP directive (e.g., 'script-src', 'img-src').
# Each value is a list of allowed sources (origins, CDNs, etc.).
#
# Add domains like 'https://cdn.example.com' to allow external resources.
#
# Strict CSP:
#   - Add csp_nonce_flag to 'script-src' to allow only scripts with a valid nonce.
#   - Do NOT add csp_nonce_flag to 'style-src' if using Lively components—they require inline styles.
#   - csp_nonce_flag disables all inline events and inline styles.
#
# For details, see: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Security-Policy

CSP_TRUSTED_SOURCES: dict = {
    "default-src": [
        "'self'",
    ],
    "script-src": [
        "'self'",
        "'unsafe-inline'", # Might be needed by Lively components.
        "'unsafe-eval'",  # Needed for JS execution in Lively components.
        # csp_nonce_flag,  # Uncomment for strict CSP (nonce only). Remove for relaxed policy.
        # Add CDN/script sources below, e.g. "https://cdn.jsdelivr.net"
    ],
    "style-src": [
        "'self'",
        "'unsafe-inline'",  # Needed for Lively components' inline styles.
        # Do NOT add csp_nonce_flag here if using Lively components.
        # Add CDN/style sources below, e.g. "https://fonts.googleapis.com"
    ],
    "img-src": [
        "'self'",
        # Add image/CDN sources, e.g. "https://images.example.com"
    ],
    "font-src": [
        "'self'",
        # Add font/CDN sources, e.g. "https://fonts.gstatic.com"
    ],
    "connect-src": [
        "'self'",
        # Add AJAX/websocket endpoints
    ],
    "media-src": [
        "'self'",
        # Add audio/video sources
    ],
    # Add more directives as needed, e.g. "frame-src", "object-src"
}


# Headers Security Policy
# This Policy creates Security Headers for every response, The headers that will be added are either SECURITY_HEADERS or SSL_SECURITY_HEADERS
# SECURITY WARNING: If both SECURITY_HEADERS and SSL_SECURITY_HEADERS are empty, this setting will result in nothing in both HTTP and HTTPS environments.
ENABLE_HEADERS_SECURITY_POLICY: bool = True


# Auto Reload
# Enable or disable autoreload for the server on file changes.
AUTO_RELOAD: bool = True


# Auto Reload Interval
# Time in seconds to delay before listening for file changes.
AUTO_RELOAD_POLL: float = 1


# Files to watch for when autoreload
AUTO_RELOAD_WATCH_FILES = ["*.py"]


# Request Class Configuration
# Specifies the class to be used for parsing incoming requests.
# - The class should be derived from `Duck HttpRequest` to ensure proper request handling.
REQUEST_CLASS: str = "duck.http.request.HttpRequest"


# Request Handling Task Executor
# This is the class for executing request handling threads or coroutines.
# The method 'execute' will be called every time a request has been accepted ready to be handled.
# WARNING: This is very critical in executing all requests handling.
REQUEST_HANDLING_TASK_EXECUTOR: str = "duck.http.core.httpd.task_executor.RequestHandlingExecutor"


# Server Buffer
# Size of the buffer used to receive data chunks per request.
# Defines the maximum size (in bytes) of each chunk of data received by the server.
# Default value is set to 65535 bytes (64KB). Adjust based on expected request sizes.
SERVER_BUFFER: int = 65535


# Server Poll Interval
SERVER_POLL: int | float = 0.5


# Mode for connection
# If keep-alive, the client requests will be handled using keep-alive if Header connection is set to the respective connection mode.
CONNECTION_MODE: str = "close"


# Keep-Alive Timeout
# Specifies the time (in seconds) to wait for the next request from the same client.
# - This setting is only applicable when `CONNECTION_MODE='keep-alive'`.
# - Note: This is distinct from `REQUEST_TIMEOUT`, which defines the wait time for the initial client request.
KEEP_ALIVE_TIMEOUT: int | float = 1


# Request Timeout
# Specifies the time (in seconds) to wait for a client initial request after connecting to the Duck Server.
REQUEST_TIMEOUT: int | float = 10


# Stream Timeout for Incoming Requests
# Timeout (in seconds) when receiving a request body without a Content-Length header,
# or when using "Transfer-Encoding: chunked". 
# Low values minimize blocking on fast networks but may interrupt uploads on slower connections.
REQUEST_STREAM_TIMEOUT: int | float = 0.001  # Ideal for instant streaming on fast networks


# Requests Backlog
# The maximum number of pending requests allowed in the backlog.
REQUESTS_BACKLOG: int = getattr(socket, "SOMAXCONN", 10)


# Specifies the max time (in seconds) for sending something over the net.
SEND_TIMEOUT: int | float = 2


# Reverse Proxy Handler
# This class handles proxying requests between the client and a Django server.
# To create a custom proxy handler, subclass `HttpProxyHandler`.
# Override the following methods for custom behavior:
# - `modify_client_request_headers`: Alter client request headers before forwarding them to the remote server.
# - `modify_client_response_headers`: Modify response headers before sending the response back to the client.
# **Caution**: Overriding these methods can lead to unexpected behavior if not handled properly.
PROXY_HANDLER: str = "duck.http.core.proxyhandler.HttpProxyHandler"


# Asynchronous Proxy Handler
ASYNC_PROXY_HANDLER: str = "duck.http.core.proxyhandler.AsyncHttpProxyHandler"


# Timeout to establish a connection with the remote proxy server (e.g., Django).
# A value of 1 second is typically used for fast responses. 
# Consider increasing if connection time to the server is high.
PROXY_CONNECT_TIMEOUT = 1  # Timeout in seconds for establishing the connection


# Timeout to wait for data from the remote proxy server.
# This value should balance between waiting for data and not blocking indefinitely.
# Increase if network latency or server load is high.
PROXY_READ_TIMEOUT = 15  # Timeout in seconds for reading data


# The amount of data to stream at once from the remote proxy server.
# 4096 bytes (4 KB) is a reasonable default chunk size for streaming,
# but can be adjusted based on specific requirements.
PROXY_STREAM_CHUNK_SIZE = 4096


# DJANGO INTEGRATION
# Whether to use Django for Backend
# This will make Duck server act as Proxy for Django
USE_DJANGO: bool = False


# Path to the Django settings module.
# Required when using Django as the backend in the Duck project.
# Format: "<python_module_path>.settings"
DJANGO_SETTINGS_MODULE: str = "web.backend.django.duckapp.duckapp.settings"


# Django Server Port
# This is the port where django server will be started on
DJANGO_BIND_PORT: int = 9999


# Django Server Wait Time
# Time in seconds to wait before checking if the Django server is up and running.
# This variable is used to periodically verify the server's status during the initial startup or maintenance routines, ensuring that the server is ready to handle incoming requests.
DJANGO_SERVER_WAIT_TIME: float = 2


# These commands will be run before Django server startup if USE_DJANGO is set to True.
# Leave empty if you don't want to run any commands
DJANGO_COMMANDS_ON_STARTUP: list[str] = [
    #"makemigrations",
    #"migrate",
    #"collectstatic --noinput",
]


# Duck Explicit URLs  
# Defines URLs that Duck should handle directly when USE_DJANGO=True.  
# By default, if DUCK_EXPLICIT_URLS is empty, all requests are processed by Django,  
# even if Duck has its own urlpatterns. Duck’s urlpatterns are effectively duplicated  
# on the Django side, meaning Django handles all matching requests first.  

# This setting allows specific URLs to bypass Django and be handled by Duck directly,  
# but only if no matching URL pattern exists in DJANGO_SIDE_URLS. If pattern in DJANGO_SIDE_URLS,  
# Django still takes precedence.  

# Use this to optimize performance by letting Duck handle requests that don’t require Django,  
# such as static/media file serving.  
DUCK_EXPLICIT_URLS: list = [
    ".*"
] # Optimized fast mode, remove ".*" for normal optimum flow'


# URLS to  be parsed straight to django
# This is only useful for urls that were registered with django but not with duck .e.g /admin
# These urls don't pass through the processing middlewares (responsible for detecting errors like Not found.)
# Add a url if the urlpattern was defined only directly in the Django side.
# **Note:** To avoid conflicts, only make sure that the url pattern definition is only in Django (Duck doesnt know of any urlpattern matching this).
# Eg. "/admin.*", Regex urls are allowed

# Note: If a URL is only defined in Django and is not listed in DJANGO_SIDE_URLS,  
# it will still result in a 404 response when accessed through Duck.

DJANGO_SIDE_URLS: list[str] = [
    "/admin.*",
    "/x-static.*"
]


# Whether Django registered urls must skip Duck middleware checks
# These middlewares are those set in settings.py, not processing middlewares (responsible for processing request further).
# This adds an extra layer of security for urlpatterns defined in Django only if set to False.
DJANGO_SIDE_URLS_SKIP_MIDDLEWARES: bool = False


# DuckApp will use this as the ID domain for Django to recognize/accept our requests (if applicable).
# Will be used also to validate private connection between Duck and Django.
DJANGO_SHARED_SECRET_DOMAIN: str = os.environ.get(
    "DJANGO_SHARED_SECRET_DOMAIN", SECRET_DOMAIN)


# SESSION SETTINGS
# This class is used for storing session data. Available cache classes include:
# - duck.utils.caching.InMemoryCache
# - duck.utils.caching.KeyAsFolderCache
# - duck.utils.caching.DynamicFileCache
#
# For detailed information on how these classes work and their benefits, use the help function.
# You can also use a custom cache class, but ensure it implements the following methods: set, get, delete, clear, save.
SESSION_STORAGE: str = "duck.utils.caching.KeyAsFolderCache"


# Session Engine
# The session engine to use for managing user sessions.
# This engine interacts with session storage to perform session operations.
#
# **Note:** 
# - Avoid overriding this directly if you primarily intend to customize session storage. 
# - It's generally preferable to override the session storage mechanism instead.
# - This engine will *not* be automatically synchronized with Django if `USE_DJANGO=True`. 
#   To integrate with Django, you'll need to create a custom Django session backend.
SESSION_ENGINE = "duck.http.session.engine" 


# Session Directory
# Specifies the directory to store session data.
# - If using database session storage, this can be set to `None`.
# - The directory will be automatically created if it does not exist.
SESSION_DIR: str = BASE_DIR / "assets/.cache"


# Session Cookie Name
# The name of the cookie that stores the session ID in the client's request.
SESSION_COOKIE_NAME: str = "session_id"


# Session Duration
# The duration (in seconds) for which a session will remain active.
# Default is set to 7 days (604800 seconds).
SESSION_COOKIE_AGE: int | float = 604800  # 7 days


# Session Cookie Path
SESSION_COOKIE_PATH: str = "/"


# Session Cookie Domain
SESSION_COOKIE_DOMAIN: str = None


# Session Expire At Browser Close
# Whether for sessions to expire at browser close
SESSION_EXPIRE_AT_BROWSER_CLOSE: bool = False


# Session Cookie Secure
# Whether session cookie should be accessed only on https
SESSION_COOKIE_SECURE: bool = False


# Session Cookie HttpOnly
# Whether session cookie should be accessible via http only (javascript not allowed)
SESSION_COOKIE_HTTPONLY: bool = True


# Session Cookie SameSite
SESSION_COOKIE_SAMESITE: str = "Lax"


# Csrf Secret Length
# The length for the csrf secret key.
CSRF_SECRET_LENGTH: int = 32


# Csrf Token Length
CSRF_TOKEN_LENGTH: int = 64


# Csrf Session Key
# The name for the csrf secret in request sessions.
CSRF_SESSION_KEY: str = "_csrftoken"


# CSRF Cookie Name
# The name of the cookie that holds the CSRF token for POST requests.
CSRF_COOKIE_NAME: str = "csrftoken"


# CSRF Header Name
# The header name sent to the client when a new CSRF token is generated for that client.
CSRF_HEADER_NAME: str = "X-CSRF-Token"


# Lifetime of the CSRF cookie in seconds (default is 7 days)
CSRF_COOKIE_AGE: int | float = 604800


# Path for which the CSRF cookie is valid (default is "/")
CSRF_COOKIE_PATH: str = "/"


# Domain for which the CSRF cookie is valid (default is None, meaning the domain of the current request)
CSRF_COOKIE_DOMAIN: str = None


# Whether to send the CSRF cookie only over HTTPS connections (default is False)
CSRF_COOKIE_SECURE: bool = False


# Whether the CSRF cookie should be HttpOnly (default is True, which prevents JavaScript access)
CSRF_COOKIE_HTTPONLY: bool = True


# SameSite attribute for CSRF cookie. Can be 'Strict', 'Lax', or 'None' (default is 'Lax')
CSRF_COOKIE_SAMESITE: str = "Lax"


# Whether to store the CSRF token in the session instead of in a cookie (default is False)
CSRF_USE_SESSIONS: bool = False


# STATIC FILES HANDLING

# These are global static directories to lookup for static files when
# `collectstatic` command is used (in production)
# Blueprint static dirs will be resolved automatically, no need to be included here.
GLOBAL_STATIC_DIRS: list[str] = [BASE_DIR / "web/ui/static"]


# The root directory for storing static files.
# Auto created if it doesn't exist
STATIC_ROOT: str = BASE_DIR / "assets/staticfiles"


# The URL to use for serving static files.
STATIC_URL: str = "static/"


# MEDIA FILES HANDLING

# Media Root
# This is where the media files will reside in.
# Auto created if it does'nt exist
MEDIA_ROOT: str = BASE_DIR / "assets/media"


# Media URL
# This is the url for serving media files
MEDIA_URL: str = "media/"


# File Upload Handler Configuration
# Specifies the handler used to save uploaded files.
# - Default is `PersistentFileUpload`, which saves uploaded files in local storage (but you have to manually call save()).
# Other alternative is TemporaryFileUpload
FILE_UPLOAD_HANDLER: str = "duck.http.fileuploads.handlers.PersistentFileUpload"


# File Upload Directory Configuration
# Specifies the directory where uploaded files will be stored.
# - Required if `PersistentFileUpload` is used as the `FILE_UPLOAD_HANDLER`.
# - The directory will be automatically created if it doesn't already exist.
FILE_UPLOAD_DIR: str = BASE_DIR / "assets/uploads"


# LOGGING SETTINGS

# Silent, No Logs
# Whether to start application with no console logs.
# **Note**: If LOG_TO_FILE is enabled, logs will keep on being logged to file instead.
SILENT: bool = False


# Django Silent, No Logs
# Whether to disable Django console logs also.
DJANGO_SILENT: bool = False


# Logging Directory
# This is the directory to place all logs
LOGGING_DIR: str = BASE_DIR / "assets/logs"


# Log File Format
# Format for log files with date and time, safe for Windows filenames
LOG_FILE_FORMAT: str = "{year}-{month:02d}-{day:02d} [{hours:02d}-{minutes:02d}-{seconds:02d}]"


# Preferred Logging Style
# Specifies the preferred format for logging responses.
# Options: "duck", "django", or None (empty string).
# Defaults to "duck".
# If set to None or not defined, the logging style will be determined by the value of "USE_DJANGO".
PREFERRED_LOG_STYLE: str = "duck"


# Log to File
# Specifies whether to save logs to files or only print them to the console.
# - When `LOG_TO_FILE=True`, logs will be stored in log files. Otherwise, logs will only be printed to the console.
LOG_TO_FILE: bool = True


# Verbose Logging
# Enables detailed logging for exceptions that cause internal server errors.
# - If `DEBUG=True`, verbose logging is enabled by default to capture additional information.
VERBOSE_LOGGING: bool = True


# SSL CERTIFICATE SETTINGS

# SSL Certificate Location
SSL_CERTFILE_LOCATION: str = BASE_DIR / "etc/ssl/server.crt"


# SSL Private Key Location
# SECURITY WARNING: Keep this safe to avoid security bridges
SSL_PRIVATE_KEY_LOCATION: str = BASE_DIR / "etc/ssl/server.key"


# Self-Signed Certificate Generation.
# Settings for generating self-signed certificate using ssl-gen command

# The location of the SSL Certificate Signing Request (CSR).
SSL_CSR_LOCATION: str = BASE_DIR / "etc/ssl/server.csr"


# Domain name for the server. Replace with fully-qualified domain name (FQDN)
SERVER_DOMAIN: str = ""


# Server country as Two-Letter country code as per ISO 3166-1 alpha-2 code eg US or ZW
SERVER_COUNTRY: str = ""  # .e.g ZW


# Server state or province e.g. California
SERVER_STATE: str = ""


# Server locality. Replace with the locality name (city, town, etc.) e.g. Harare
SERVER_LOCALITY: str = ""


# Server Organization. Replace with your legally registered organization name
SERVER_ORGANIZATION: str = ""


# Server Organization Unit. Replace with your legally registered organization unit
SERVER_ORGANIZATION_UNIT: str = ""


# Preconfigured Certbot config
CERTBOT_ROOT: str = BASE_DIR / "etc/certbot"


# SYSTEMD CONFIGURATION
# systemd is a system and service manager used in Linux distributions.
# It controls the starting, stopping, and monitoring of services, making 
# it ideal for managing background processes like web servers.
#
# For the Duck Web Server, using systemd ensures that the server can:
# - Start automatically on boot
# - Be managed easily through standard commands (`start`, `stop`, `restart`)
# - Restart automatically if it crashes or stops unexpectedly
# - Run in the background as a service, freeing up the terminal

# Systemd Execution Command
# Specifies the command that will be executed when the systemd service starts.
# In this case, it runs the Duck web server from web/main.py.
SYSTEMD_EXEC_COMMAND: str = f"{sys.executable} web/main.py"


# Systemd Service Name
# Defines the name of the systemd service unit file. 
# This will be used when managing the service with systemctl (e.g., starting, stopping, enabling).
SYSTEMD_SERVICE_NAME: str = "duck.service"


# Systemd Environment
# Provides the environment variables that should be set for the service.
# The environment is typically populated with the current system environment variables (os.environ).
SYSTEMD_ENVIRONMENT: dict = {
    "DUCK_SETTINGS_MODULE": os.environ.get('DUCK_SETTINGS_MODULE', "settings")
}


# Systemd Restart Policy
# Specifies the restart behavior for the service.
# "always" ensures that the service will be restarted automatically if it fails or stops unexpectedly.
SYSTEMD_RESTART: str = "always"


# Systemd Service Directory
# Indicates the directory where the systemd service unit file will be stored.
# Typically, service unit files are placed in /etc/systemd/system/ for system-wide services.
SYSTEMD_SERVICE_DIR: str = "/etc/systemd/system/"

```
