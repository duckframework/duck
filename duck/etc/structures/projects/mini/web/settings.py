"""
File containing settings for Duck application.
"""
# yapf: disable
import os
import json
import pathlib

from duck.etc.middlewares import middlewares
from duck.secrets import DUCK_SECRET
from duck.storage import BaseDir


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


# HTTPS
# Specifies whether to enable HTTPS for the server.
# - When `ENABLE_HTTPS=True`, HTTPS is enabled on the specified port.
# - Ensure you have valid SSL certificates configured for secure communication.
ENABLE_HTTPS: bool = False


# Force HTTPS
# Enforces HTTPS by redirecting unencrypted HTTP traffic to HTTPS.
# When `FORCE_HTTPS=True`, all HTTP requests will be redirected to HTTPS.
FORCE_HTTPS: bool = False


# Asynchronous Request Handling
# Determines whether to use asynchronous request handling.
# If set to False, the framework defaults to multithreaded request handling.
# Example: ASYNC_HANDLING=True enables async handling; False uses threads.
ASYNC_HANDLING: bool = False


# DJANGO INTEGRATION
# Whether to use Django for Backend
# This will make Duck server act as Proxy for Django
USE_DJANGO: bool = False


# SSL CERTIFICATE SETTINGS

# SSL Certificate Location
SSL_CERTFILE_LOCATION: str = BASE_DIR / "etc/ssl/server.crt"


# SSL Private Key Location
# SECURITY WARNING: Keep this safe to avoid security bridges
SSL_PRIVATE_KEY_LOCATION: str = BASE_DIR / "etc/ssl/server.key"
