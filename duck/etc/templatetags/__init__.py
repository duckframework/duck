"""
Module for default builtin duck template tags and filters.
"""
from duck.template.templatetags import (
    TemplateTag,
    TemplateFilter,
    BlockTemplateTag,
)
from duck.utils.safemarkup import (
    MarkupSafeString,
    mark_safe, 
)


def resolve(*args, **kw):
    """
    Resolves URL associated with a route name.
    """
    from duck.shortcuts import resolve
    return resolve(*args, **kw)


@mark_safe
def csrf_token(context) -> MarkupSafeString:
    """
    Retrieves CSRF html input field.
    """
    from duck.shortcuts import csrf_token
    
    request = context.get("request")
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
BUILTIN_TEMPLATETAGS = [
    csrf_tag,
    static_tag,
    media_tag,
    resolve_tag,
    # builtin template filters following
]
