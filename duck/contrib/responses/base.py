"""
Duck Framework built-in response factory.

Transforms bare HttpResponse subclasses into fully rendered,
themed HTML responses using Duck's internal template engine.
"""

import os

from typing import Type, Optional, Dict, Any

from duck.etc.internals.template import internal_render, async_internal_render
from duck.http.response import HttpResponse, TemplateResponse
from duck.utils.path import joinpaths
from duck.utils.safemarkup import mark_safe
from duck.settings import SETTINGS


# Resolved once at import time; overridable via environment variable.
DEFAULT_FAVICON = (
    os.getenv("MAKE_RESPONSE_DEFAULT_ICON")
    or joinpaths("/" + str(SETTINGS["STATIC_URL"]), "/welcome/duck-favicon.png")
)


def make_response(
    response_class: Type[HttpResponse],
    title: str = None,
    heading: str = None,
    body: str = None,
    status_code: int = None,
    status_label: str = None,
    icon_link: str = DEFAULT_FAVICON,
    icon_type: str = "image/png",
    debug: bool = None,
    extra_context: Optional[Dict[Any, Any]] = None,
    template: Optional[str] = None,
) -> TemplateResponse:
    """
    Transforms an HttpResponse subclass into a themed HTML response.

    Uses Duck's internal base template to produce a styled error or
    informational page. Falls back to the response class's own status
    message and explanation when title, heading, or body are omitted.

    Args:
        response_class: A subclass of HttpResponse to render.
        title: Browser tab title. Defaults to the response status message.
        heading: Primary heading shown on the page. Defaults to the response status message.
        body: Body text or HTML. Defaults to the response status explanation.
        status_code: HTTP status code passed to the template watermark. Inferred from
            the response class when omitted.
        status_label: Human-readable status label e.g. "Not Found". Inferred when omitted.
        icon_link: URL to the favicon. Defaults to Duck's built-in favicon.
        icon_type: MIME type of the favicon. Required when icon_link is provided.
        debug: Renders the debug notice when True. Defaults to the DEBUG setting.
        extra_context: The extra context to pass to the base template.
        template: The internal template to use, defaults to `base.html`.
        
    Returns:
        A TemplateResponse with the rendered HTML body and correct status code.

    Raises:
        TypeError: If response_class is not a subclass of HttpResponse.
        TypeError: If icon_link is provided without icon_type.
    """

    # Validate response class before doing any work.
    if not issubclass(response_class, HttpResponse):
        raise TypeError(
            f"{response_class.__name__} must be a subclass of HttpResponse."
        )

    # icon_type is required whenever a custom icon is supplied.
    if icon_link and not icon_type:
        raise TypeError("icon_type must be provided when icon_link is set.")

    # Instantiate to read status metadata off the class.
    response = response_class()

    # Resolve body first so we can stash it for later retrieval.
    resolved_body = mark_safe(body or response.status_explanation)
    response._body = resolved_body

    # Build the template context, inferring any omitted values.
    context = {
        "title": title or response.status_message,
        "heading": heading or response.status_message,
        "body": resolved_body,
        "status_code":  status_code or response.status_code,
        "status_label": status_label or response.status_message,
        "icon_link": icon_link,
        "icon_type": icon_type,
        "debug": debug if debug is not None else SETTINGS["DEBUG"],
        **(extra_context or {}),
    }
    
    # Render the base template into a new TemplateResponse.
    rendered = internal_render(
        request=context.get("request", None),
        template=template or "base.html",
        context=context,
        content_type="text/html",
        status_code=response.status_code,
    )

    # Preserve the resolved body on the rendered response for downstream use.
    rendered._body = resolved_body
    
    # Return the final template response.
    return rendered


async def async_make_response(
    response_class: Type[HttpResponse],
    title: str = None,
    heading: str = None,
    body: str = None,
    status_code: int = None,
    status_label: str = None,
    icon_link: str = DEFAULT_FAVICON,
    icon_type: str = "image/png",
    debug: bool = None,
    extra_context: Optional[Dict[Any, Any]] = None,
    template: Optional[str] = None,
) -> TemplateResponse:
    """
    Async variant of `make_response` for use inside async views and handlers.

    Transforms an HttpResponse subclass into a themed HTML response using
    Duck's async internal template renderer. Behaviour is identical to
    make_response except the render step is awaited.

    Args:
        response_class: A subclass of HttpResponse to render.
        title: Browser tab title. Defaults to the response status message.
        heading: Primary heading shown on the page. Defaults to the response status message.
        body: Body text or HTML. Defaults to the response status explanation.
        status_code: HTTP status code passed to the template watermark. Inferred from
            the response class when omitted.
        status_label: Human-readable status label e.g. "Not Found". Inferred when omitted.
        icon_link: URL to the favicon. Defaults to Duck's built-in favicon.
        icon_type: MIME type of the favicon. Required when icon_link is provided.
        debug: Renders the debug notice when True. Defaults to the DEBUG setting.
        context: The extra context to pass to the base template.
        template: The internal template to use, defaults to `base.html`.
        
    Returns:
        A TemplateResponse with the rendered HTML body and correct status code.

    Raises:
        TypeError: If response_class is not a subclass of HttpResponse.
        TypeError: If icon_link is provided without icon_type.
    """

    # Validate before any work is done.
    if not issubclass(response_class, HttpResponse):
        raise TypeError(
            f"{response_class.__name__} must be a subclass of HttpResponse."
        )

    if icon_link and not icon_type:
        raise TypeError("icon_type must be provided when icon_link is set.")

    # Instantiate to read status metadata.
    response = response_class()

    # Resolve and stash body for downstream retrieval.
    resolved_body = mark_safe(body or response.status_explanation)
    response._body = resolved_body

    # Build template context.
    context = {
        "title": title or response.status_message,
        "heading": heading or response.status_message,
        "body": resolved_body,
        "status_code": status_code or response.status_code,
        "status_label": status_label or response.status_message,
        "icon_link": icon_link,
        "icon_type": icon_type,
        "debug": debug if debug is not None else SETTINGS["DEBUG"],
        **(extra_context or {}),
    }

    # Await the async render step.
    rendered = await async_internal_render(
        request=context.get("request", None),
        template=template or "base.html",
        context=context,
        content_type="text/html",
        status_code=response.status_code,
    )

    # Preserve resolved body on the rendered response.
    rendered._body = resolved_body
    
    # Return the final response.
    return rendered
    