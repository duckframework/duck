"""
Refresh claims for the client using the following APIs.

Flow:

1. User calls `queue_browser_state`, this adds the Page/component request ID to a registry.
2. User calls `sync_browser_state` and it makes a fetch to the appropriate URL and set sensitive data directly from headers which maybe safer e.g. HttpOnly, Secure cookie
"""
from duck.http.request import HttpRequest
from duck.http.response import HttpResponse
from duck.settings.loaded import SettingsLoaded
from duck.utils.caching import InMemoryCache


BROWSER_STATE_REGISTRY = InMemoryCache(maxkeys=1024*2)


def needs_browser_state_update(component_request: HttpRequest) -> bool:
    """
    Returns a boolean on whether the request passed to the component is dirty or needs 
    Lively to do a `fetch()` on the `sync_browser_state` view.
    
    Args:
        component_request: The request passed to the component.
    """
    session_needs_update = component_request.SESSION.needs_update()
    jwt_needs_update = component_request.JWT.needs_update()
    csrf_needs_update = component_request.META.get('CSRF_COOKIE_NEEDS_UPDATE', False)
    return any([session_needs_update, jwt_needs_update, csrf_needs_update])
    

def queue_browser_state_response(component_request: HttpRequest, response: HttpResponse):
    """
    This adds component request and response that needs to be sent when user visits sync browser state view to the registry.
     
     Args:
        component_request: The request passed to the component.
    """
    rid = component_request.ID
    
    BROWSER_STATE_REGISTRY.set(rid, response)
    

def sync_browser_state(request):
    """
    This syncs the browser state like updating sensitive HTTPONLY cookies.
    
    Notes:
        This will be called within Lively on client side using `fetch()`.
    
    Returns:
        HttpResponse: Http response added to queue else 404 HttpResponse.
    """
    rid = request.GET.get("rid")
    response = BROWSER_STATE_REGISTRY.pop(rid, None)
    
    # Finally, return response
    return response or HttpResponse(status_code=404)
