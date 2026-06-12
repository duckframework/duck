"""
Pre-built error response factories for common HTTP error status codes.

Thin wrappers around make_response that map each HTTP error class to a
named function, providing a convenient one-call API for returning themed
error pages from views and middleware.
"""

from typing import Optional, Union, Dict, Any

from duck.settings import SETTINGS
from duck.http.request import HttpRequest
from duck.http.response import (
    HttpBadGatewayResponse,
    HttpResponse,
    HttpServerErrorResponse,
    HttpMethodNotAllowedResponse,
    HttpNotFoundResponse,
    HttpBadRequestResponse,
    HttpBadRequestSyntaxResponse,
    HttpUnsupportedVersionResponse,
    HttpRequestTimeoutResponse,
)
from duck.contrib.sync import ensure_async
from duck.contrib.responses.base import make_response
from duck.exceptions.all import (
    RequestSyntaxError,
    RequestUnsupportedVersionError,
)
from duck.meta import Meta
from duck.logging import logger


def timeout_error(timeout: Optional[Union[int, float]] = None) -> HttpRequestTimeoutResponse:
    """
    Builds a 408 Request Timeout response.

    In debug mode the response body includes the configured timeout value
    so developers can identify slow or stalled client connections quickly.

    Args:
        timeout: The timeout threshold in seconds that was exceeded. When
            provided, the value is surfaced in the debug body.

    Returns:
        A themed HttpRequestTimeoutResponse.
    """
    body = None

    if SETTINGS["DEBUG"]:
        body = "<p>Client sent nothing within the expected time.</p>"

        if timeout:
            body = (
                "<p>Client sent nothing within the expected time.</p>"
                f"<div>Timeout: ({timeout} seconds)</div>"
            )
            
    return make_response(HttpRequestTimeoutResponse, body=body)


def server_error(exception: Exception, request: Optional[HttpRequest] = None) -> HttpResponse:
    """
    Builds a 500 Internal Server Error response for an unhandled exception.

    In debug mode the full exception traceback and request metadata are
    rendered into the response body. In production the body is suppressed
    to avoid leaking internal details.

    Args:
        exception: The unhandled exception that triggered this error.
        request: The active HTTP request. Used to annotate DEBUG_MESSAGE
            in request metadata and to enrich the debug body.

    Returns:
        A themed HttpServerErrorResponse.
    """
    if request:
        request.META["DEBUG_MESSAGE"] = f"Internal Server Error: {request.path}"

    # Finally, construct and build response.
    return make_response(HttpServerErrorResponse, extra_context={"request": request, "exception": exception})


def bad_gateway(exception: Optional[Exception] = None, request: Optional[HttpRequest] = None) -> HttpResponse:
    """
    Builds a 502 Bad Gateway response.

    Typically raised when an upstream server or proxied service returns
    an invalid or no response. In debug mode the exception detail is
    included in the response body.

    Args:
        exception: The exception that triggered the bad gateway condition, if available.
        
        request: The active HTTP request. Used to annotate DEBUG_MESSAGE
            in request metadata and to enrich the debug body.

    Returns:
        A themed HttpBadGatewayResponse.
    """
    if request:
        request.META["DEBUG_MESSAGE"] = f"Bad Gateway: {request.path}"

    # Build and return response
    context = {}
    
    if SETTINGS['DEBUG']:
        context["exception"] = exception
    
    # Return the final response.
    return make_response(HttpBadGatewayResponse, extra_context=context)


def method_not_allowed(
    request: Optional[HttpRequest] = None,
    route_info: Optional[Dict[str, Any]] = None,
) -> HttpResponse:
    """
    Builds a 405 Method Not Allowed response.

    In debug mode the allowed methods for the matched route are surfaced
    in the response body so developers can identify the correct verb quickly.

    Args:
        request: The active HTTP request. Used to annotate DEBUG_MESSAGE
            with the disallowed method.
        route_info: The matched route's metadata as returned by RouteRegistry.
            When provided, the allowed methods list is extracted and shown.

    Returns:
        A themed HttpMethodNotAllowedResponse.
    """
    if request:
        request.META["DEBUG_MESSAGE"] = f"Method Not Allowed: {request.method}"

    if not SETTINGS["DEBUG"]:
        return make_response(HttpMethodNotAllowedResponse)

    if route_info:
        allowed = [m.upper() for m in route_info["methods"]]
        body = f"<p>Method not allowed.</p><div class='allowed-methods'>Allowed: {allowed}</div>"
    else:
        body = "<p>Method not allowed.</p>"
    
    # Return the final response.
    return make_response(HttpMethodNotAllowedResponse, body=body)


def bad_request(
    exception: Exception,
    request: Optional[HttpRequest] = None,
) -> HttpResponse:
    """
    Builds the appropriate 4xx Bad Request response for a malformed request.

    Inspects the exception type to select the most specific response class
    and body message. Handles three distinct cases:

    - RequestSyntaxError ➝ 400 Bad Request Syntax
    - RequestUnsupportedVersionError ➝ 505 HTTP Version Not Supported
    - HTTPS-over-HTTP detection ➝ 400 with a protocol mismatch hint
    - All other cases ➝ generic 400 Bad Request

    In debug mode the exception reference is appended to the body. In
    production the body is suppressed entirely.

    Args:
        exception: The exception describing the malformed request.
        request: The active HTTP request. Used to annotate DEBUG_MESSAGE
            with a context-specific message for each error type.

    Returns:
        A themed HttpResponse with the appropriate 4xx status code.
    """
    response_cls = HttpBadRequestResponse
    body = (
        "<p>Bad request — there is an error in the request.</p>"
        "<p>You may need to reconstruct the request in the correct format.</p>"
    )

    if isinstance(exception, RequestSyntaxError):
        response_cls = HttpBadRequestSyntaxResponse
        body = (
            "<p>Bad request syntax.</p>"
            "<p>You may need to reconstruct the request in the correct format.</p>"
        )
        if request:
            request.META["DEBUG_MESSAGE"] = f"Bad Request Syntax: {request.path}"

    elif isinstance(exception, RequestUnsupportedVersionError):
        response_cls = HttpUnsupportedVersionResponse
        body = (
            "<p>Unsupported HTTP version.</p>"
            "<p>You may need to switch to a supported protocol.</p>"
        )
        if request:
            request.META["DEBUG_MESSAGE"] = f"Unsupported HTTP Version: {request.http_version}"

    elif "'utf-8' codec can't decode byte" in str(exception) and not SETTINGS["ENABLE_HTTPS"]:
        # Client is likely sending HTTPS-encrypted traffic to an HTTP server.
        body = (
            "<p>Bad request — there is an error in the request.</p>"
            "<p>The client may be sending HTTPS-encrypted traffic to an HTTP server.</p>"
        )
        if request:
            request.META["DEBUG_MESSAGE"] = (
                "Bad Request: Client may be sending HTTPS traffic to an HTTP server."
            )

    else:
        if request:
            request.META["DEBUG_MESSAGE"] = f"Bad Request: {request.path}"

    if SETTINGS["DEBUG"]:
        ref = f"<p><b>Reference:</b> {exception}</p>"
        return make_response(response_cls, body=body + ref)
    
    # Return final response.
    return make_response(response_cls)


def not_found(request: Optional[HttpRequest] = None) -> HttpNotFoundResponse:
    """
    Builds a 404 Not Found response.

    In debug mode the response renders the full route registry so
    developers can quickly spot mismatched or missing URL patterns.
    A Django-specific hint is included when USE_DJANGO=True to surface
    the DJANGO_SIDE_URLS option.

    Args:
        request: The active HTTP request. Used to annotate DEBUG_MESSAGE
            and to supply the requested path to the template.

    Returns:
        A themed HttpNotFoundResponse rendered from 404.html.
    """
    debug = bool(SETTINGS["DEBUG"])
    
    if request:
        request.META["DEBUG_MESSAGE"] = f"Not Found: {request.path}"
    
    # Non-debug path — render the minimal template with no extra context.
    if not debug:
        return make_response(
            HttpNotFoundResponse,
            template="404.html",
            extra_context={
                "title": "404 · Not Found",
                "status_code": 404,
                "status_label": "Not Found",
                "heading": "Page Not Found",
                "body": (
                    "The page you're looking for doesn't exist "
                    "or has been moved."
                ),
                "request": request,
                "debug": False,
            },
        )

    # Build the structured route list for the debug panel.
    routes = build_route_list()
    context = {
        "title": "404 · Not Found",
        "status_code": 404,
        "status_label": "Not Found",
        "heading": "Page Not Found",
        "body": (
            "The URL you requested doesn't match any registered route. "
            "Check the route registry below."
        ),
        "request": request,
        "debug": True,
        "use_django": bool(SETTINGS.get("USE_DJANGO")),
        "routes": routes,
    }
    
    # Finally, return the response.
    return make_response(HttpNotFoundResponse, template="404.html", extra_context=context)


def build_route_list() -> list[dict]:
    """
    Converts the RouteRegistry url_map into a list of template-friendly dicts.

    Each entry exposes the URL pattern, its registered name, and any HTTP
    methods declared on the route handler. The pattern is HTML-escaped so
    the template can render angle-bracket parameters safely.

    Returns:
        A list of dicts with keys: pattern (str), name (str), methods (list[str]).
    """
    from duck.routes import RouteRegistry
    
    routes = []

    for pattern, info in RouteRegistry.url_map.items():
        # url_map stores {pattern: {name: handler}} — grab the first entry.
        name, other = next(iter(info.items()))

        # Escape < > so Jinja2 outputs them as visible characters.
        safe_pattern = pattern.replace("<", "&lt;").replace(">", "&gt;")

        # Pull declared HTTP methods off the handler if present.
        methods = other[1]
        
        # Add route info.
        routes.append({
            "pattern": safe_pattern,
            "name": name,
            "methods": methods,
        })

    # Return the final routes.
    return routes


# ASYNC API

async def async_timeout_error(timeout: Optional[Union[int, float]] = None) -> HttpRequestTimeoutResponse:
    """
    Asynchronously builds a 408 Request Timeout response.

    In debug mode the response body includes the configured timeout value
    so developers can identify slow or stalled client connections quickly.

    Args:
        timeout: The timeout threshold in seconds that was exceeded. When
            provided, the value is surfaced in the debug body.

    Returns:
        A themed HttpRequestTimeoutResponse.
    """
    return await ensure_async(timeout_error)(timeout)


async def async_server_error(exception: Exception, request: Optional[HttpRequest] = None) -> HttpResponse:
    """
    Asynchronously builds a 500 Internal Server Error response for an unhandled exception.

    In debug mode the full exception traceback and request metadata are
    rendered into the response body. In production the body is suppressed
    to avoid leaking internal details.

    Args:
        exception: The unhandled exception that triggered this error.
        request: The active HTTP request. Used to annotate DEBUG_MESSAGE
            in request metadata and to enrich the debug body.

    Returns:
        A themed HttpServerErrorResponse.
    """
    return await ensure_async(server_error)(exception, request)


async def async_bad_gateway(exception: Optional[Exception] = None, request: Optional[HttpRequest] = None) -> HttpResponse:
    """
    Asynchronously builds a 502 Bad Gateway response.

    Typically raised when an upstream server or proxied service returns
    an invalid or no response. In debug mode the exception detail is
    included in the response body.

    Args:
        exception: The exception that triggered the bad gateway condition, if available.
        
        request: The active HTTP request. Used to annotate DEBUG_MESSAGE
            in request metadata and to enrich the debug body.

    Returns:
        A themed HttpBadGatewayResponse.
    """
    await ensure_async(bad_gateway)(exception)


async def async_not_found(request: Optional[HttpRequest] = None) -> HttpResponse:
    """
    Asynchronously builds a 404 Not Found response.

    In debug mode the response lists all routes currently registered in
    the RouteRegistry so developers can diagnose mismatched or missing
    URL patterns. A Django-specific hint is appended when USE_DJANGO=True
    to surface the DJANGO_SIDE_URLS option.

    Args:
        request: The active HTTP request. Used to annotate DEBUG_MESSAGE
            and to include the requested path in the debug body.

    Returns:
        A themed HttpNotFoundResponse.
    """
    return await ensure_async(not_found)(request)


async def async_method_not_allowed(
    request: Optional[HttpRequest] = None,
    route_info: Optional[Dict[str, Any]] = None,
) -> HttpResponse:
    """
    Asynchronously builds a 405 Method Not Allowed response.

    In debug mode the allowed methods for the matched route are surfaced
    in the response body so developers can identify the correct verb quickly.

    Args:
        request: The active HTTP request. Used to annotate DEBUG_MESSAGE
            with the disallowed method.
        
        route_info: The matched route's metadata as returned by RouteRegistry.
            When provided, the allowed methods list is extracted and shown.

    Returns:
        A themed HttpMethodNotAllowedResponse.
    """
    return await ensure_async(method_not_allowed)(request, route_info)


async def async_bad_request(
    exception: Exception,
    request: Optional[HttpRequest] = None,
) -> HttpResponse:
    """
    Asynchronously builds the appropriate 4xx Bad Request response for a malformed request.

    Inspects the exception type to select the most specific response class
    and body message. Handles three distinct cases:

    - RequestSyntaxError ➝ 400 Bad Request Syntax
    - RequestUnsupportedVersionError ➝ 505 HTTP Version Not Supported
    - HTTPS-over-HTTP detection ➝ 400 with a protocol mismatch hint
    - All other cases ➝ generic 400 Bad Request

    In debug mode the exception reference is appended to the body. In
    production the body is suppressed entirely.

    Args:
        exception: The exception describing the malformed request.
        request: The active HTTP request. Used to annotate DEBUG_MESSAGE
            with a context-specific message for each error type.

    Returns:
        A themed HttpResponse with the appropriate 4xx status code.
    """
    return await ensure_async(bad_request)(exception, request)
