"""
Module for default builtin duck template tags and filters.
"""
import traceback

from duck.template.templatetags import (
    TemplateTag,
    TemplateFilter,
    BlockTemplateTag,
)
from duck.utils.safemarkup import (
    MarkupSafeString,
    mark_safe, 
)
from duck.utils.string import smart_truncate, to_spaced_camel_case


def resolve(*args, **kw):
    """
    Resolves URL associated with a route name.
    """
    from duck.shortcuts import resolve
    return resolve(*args, **kw)


@mark_safe
def csrf_token(context) -> MarkupSafeString:
    """
    Retrieves CSRF HTML input field.
    """
    from duck.shortcuts import csrf_token
    
    # Retrieve request from context
    request = context.get("request")
    
    # Construst and return csrf html input field
    name = "csrfmiddlewaretoken"
    token = csrf_token(request)
    return f'<input id="{name}" name="{name}" type="hidden" value="{token}">'


def static(resource_path: str):
    """
    Returns static url for the provided resource.
    """
    from duck.shortcuts import static
    return static(resource_path)
    

def media(resource_path: str):
    """
    Returns media URL for the provided resource.
    """
    from duck.shortcuts import media
    return media(resource_path)


csrf_tag = TemplateTag(
    tagname="csrf_token",
    tagcallable=csrf_token,
    takes_context=True,
)
static_tag = TemplateTag(
    tagname="static",
    tagcallable=static,
)
media_tag = TemplateTag(
    tagname="media",
    tagcallable=media
)
resolve_tag = TemplateTag(
    tagname="resolve",
    tagcallable=resolve,
)
expand_exception_tag = TemplateTag(
    tagname="expand_exception",
    tagcallable=lambda exc: "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
)
smart_truncate_tag = TemplateTag(
    tagname="smart_truncate",
    tagcallable=smart_truncate,
)
to_spaced_camel_case_tag = TemplateFilter(
    filtername="to_spaced_camel_case",
    filtercallable=to_spaced_camel_case,
)


BUILTIN_TEMPLATETAGS = [
    csrf_tag,
    static_tag,
    media_tag,
    resolve_tag,
    expand_exception_tag,
    smart_truncate_tag,
    to_spaced_camel_case_tag,
    # Builtin template filters following
]
