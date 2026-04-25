"""
This module provides various utility functions and shortcuts for handling 
common operations in the Duck framework. 

It includes functions for rendering templates, generating responses, 
resolving URLs, managing CSRF tokens, handling static and media resources, 
and manipulating HTTP responses.

The module also defines `URLResolveError`, an exception raised when 
URL resolution fails.
"""
import io

from typing import (
    Optional,
    Any,
    Union,
    Awaitable,
    Callable,
    Dict,
)
from urllib.parse import urljoin
from collections.abc import Iterable
from functools import lru_cache

from duck import template as _template
from duck.http.request import HttpRequest
from duck.http.response import (
    BaseResponse,
    HttpNotFoundResponse,
    HttpRedirectResponse,
    HttpResponse,
    TemplateResponse,
    JsonResponse,
    StreamingHttpResponse,
    ComponentResponse,
)
from duck.utils.path import (
    build_absolute_uri,
    sanitize_path_segment,
    is_good_url_path,
    joinpaths,
)
from duck.utils.urlcrack import URL
from duck.contrib.responses import (
    simple_response,
    template_response,
)
from duck.contrib.responses.errors import get_404_error_response
from duck.contrib.sync import (
  sync_to_async,
  convert_to_sync_if_needed,
)
from duck.contrib.websockets import WebSocketView
from duck.settings import SETTINGS
from duck.exceptions.all import (
    RouteNotFoundError,
    TemplateError,
    SettingsError,
)
from duck.html.components import Component
from duck.meta import Meta
from duck.routes import RouteRegistry, Blueprint


__all__ = [
    "simple_response",
    "template_response",
    "URLResolveError",
    "jinja2_render",
    "django_render",
    "render",
    "async_render",
    "redirect",
    "jsonify",
    "not_found404",
    "merge",
    "content_replace",
    "streaming_content_replace",
    "replace_response",
    "resolve",
    "to_response",
    "static",
    "media",
    "static_filepath",
    "media_filepath",
    "csrf_token",
]


class URLResolveError(Exception):
    """
    Raised if URL resolving fails.
    """


def csrf_token(request) -> str:
    """
    Returns the csrf token, whether for django or duck request.
    """
    from duck.template.csrf import get_csrf_token
    token = get_csrf_token(request)  # csrf_token
    return token


def static(resource_path: str, absolute: bool = True) -> str:
    """
    Returns the static URL for the provided resource path.

    Args:
        resource_path: A URL path or external URL pointing to the resource.
        absolute: Whether to return an absolute URL. Defaults to True.
            Falls back to relative if the absolute server URL cannot be resolved.

    Returns:
        The resolved static URL string.

    Raises:
        TypeError: If resource_path is not a valid URL path.
    """
    if not is_good_url_path(resource_path):
        raise TypeError(f"Please provide valid URL path in form '/some/path' not {resource_path}")
    
    resource_path = sanitize_path_segment(resource_path)
    static_url = URL(SETTINGS["STATIC_URL"])
    
    if static_url.scheme:
        # This is most likely an external CDN
        return static_url.join(resource_path).to_str()
        
    # Serve directly from server
    try:
        root_url = "/" if not absolute else Meta.get_absolute_server_url()
    except Exception:
        root_url = "/"
    
    # Join and return final URL
    static_url_str = urljoin(root_url, static_url.to_str())
    return urljoin(static_url_str, resource_path)


def media(resource_path: str, absolute: bool = True) -> str:
    """
    Returns the media URL for the provided resource path.

    Args:
        resource_path: A URL path or external URL pointing to the resource.
        absolute: Whether to return an absolute URL. Defaults to True.
            Falls back to relative if the absolute server URL cannot be resolved.

    Returns:
        The resolved media URL string.

    Raises:
        TypeError: If resource_path is not a valid URL path.
    """
    if not is_good_url_path(resource_path):
        raise TypeError(
            f"Please provide valid url path in form '/some/path' not {resource_path}"
        )
    
    resource_path = sanitize_path_segment(resource_path)
    media_url = URL(SETTINGS["MEDIA_URL"])
    
    if media_url.scheme:
        # This is most likely an external media source
        return media_url.join(resource_path).to_str()
        
    # Serve directly from server
    try:
        root_url = "/" if not absolute else Meta.get_absolute_server_url()
    except Exception:
        root_url = "/"
    
    # Join and return final URL
    media_url_str = urljoin(root_url, media_url.to_str())
    return urljoin(media_url_str, resource_path)


def static_filepath(relative_filepath: str, blueprint: Optional[Blueprint] = None, target_static_dir: Optional[str] = None) -> str:
    """
    Returns an absolute file path of the static file.
    
    Args:
        relative_filepath (str): The relative file path within the default static directory.
        blueprint (Optional[Blueprint]): If the static file is within a blueprint static directory (or belongs to a blueprint), a blueprint must be provided.
        target_static_dir (str): This is the selected static directory if you are using more than 1 global static directories.
        
    Example:
    
    ```py
    favicon = static_filepath('images/favicon.ico')
    print(favicon) # May print something like /usr/home/myproject/web/ui/static/images/favicon.ico
    ```
    """
    if target_static_dir and blueprint:
        raise TypeError("Please provide either 'target_static_dir' or 'blueprint', not both.")
    
    if target_static_dir:
        return joinpaths(target_static_dir, relative_filepath)  
    
    if SETTINGS['DEBUG']:
        if blueprint:
            file = joinpaths(blueprint.root_directory, blueprint.static_dir, relative_filepath)
        else:
            global_static_dirs = SETTINGS['GLOBAL_STATIC_DIRS']
            
            if len(global_static_dirs) > 1 and not target_static_dir:
                raise SettingsError("More than 1 global static dirs detected in settings.py. Please provide 'target_static_dir' as an argument.")
            
            # Choose target static directory and return the final filepath
            target_static_dir = global_static_dirs[0]
            return joinpaths(target_static_dir, relative_filepath)  
    else:
        # We are in production.
        target_static_dir = SETTINGS['STATIC_ROOT']
        
        if blueprint:
            # Convert staticdir to relative path
            abs_static_dir = joinpaths(blueprint.root_directory, blueprint.static_dir)
            relative_static_dir = pathlib.Path(abs_static_dir).relative_to(pathlib.Path(blueprint.location).parent)
            
            # The blueprint stripped_staticdir is a dir with removed staticdir name from it
            # so that function static() can resolve files correctly in production.
            parts = pathlib.Path(relative_static_dir).parts
            staticdir_name = ""
            
            if parts:
                staticdir_name = parts[0]
            
            # Set staticdir without staticdir name
            blueprint_stripped_staticdir = str(relative_static_dir).lstrip(staticdir_name)
            target_static_dir = joinpaths(
                static_root,
                blueprint.name,
                blueprint_stripped_staticdir,
            )
            return joinpaths(target_static_dir, relative_filepath)
        else:
            return joinpaths(target_static_dir, relative_filepath)


def media_filepath(relative_filepath: str) -> str:
    """
    Returns an absolute file path of the media file.
    
    Args:
        relative_filepath (str): The relative file path within the default static directory.
        
    Example:
    
    ```py
    profile_img = media_filepath('users/user1/profile.png')
    print(profile_img) # May print something like /usr/home/myproject/assets/media/users/user1/profile1.png
    ```
    """
    return joinpaths(SETTINGS['MEDIA_ROOT'], relative_filepath)


def jinja2_render(
    request: HttpRequest,
    template: str,
    context: Dict[Any, Any] = {},
    status_code: int = 200,
    **kw,
) -> TemplateResponse:
    """
    Render a jinja2 template.

    Args:
        request (HttpRequest): The request object.
        template (str): The Jinja2 template with global or blueprint template dirs.
        context (dict, optional): The context dictionary to pass to the template. Defaults to an empty dictionary.
        status_code (int): The response status code, defaults to 200.
        **kw: Additional keyword arguments to parse to TemplateResponse.

    Returns:
        TemplateResponse: The response object with the rendered content.
    """
    template = sanitize_path_segment(template).lstrip("/") if template else template

    return TemplateResponse(
        request=request,
        template=template,
        context=context,
        engine=_template.environment.default_jinja2_engine(),
        status_code=status_code,
        **kw,
    )


def django_render(
    request: HttpRequest,
    template: str,
    context: Dict[Any, Any] = {},
    status_code: int = 200,
    **kw,
) -> TemplateResponse:
    """
    Render a Django template.

    Args:
        request (HttpRequest): The request object.
        template (str): The Django template within the global or blueprint template dirs.
        context (dict, optional): The context dictionary to pass to the template. Defaults to an empty dictionary.
        status_code (int): The response status code, defaults to 200.
        **kw: Additional keyword arguments to parse to the TemplateResponse.

    Returns:
        TemplateResponse: The response object with the rendered Django template.
    """
    template = sanitize_path_segment(template).lstrip("/") if template else template

    return TemplateResponse(
        request=request,
        template=template,
        context=context,
        engine=_template.environment.default_django_engine(),
        status_code=status_code,
        **kw,
    )


def render(
    request,
    template: str,
    context: Dict[Any, Any] = {},
    status_code: int = 200,
    engine: str = "django",
    **kw,
) -> TemplateResponse:
    """
    Renders a template and returns the response.

    Args:
            request (HttpRequest): Http request object.
            template (str): Template path within the TEMPLATE_DIR.
            context (dict, optional): Dictionary respresenting template context.
            status_code (int): The response status code, defaults to 200.
            engine (str, optional): Template engine to use for rendering template, defaults to 'django'.
            **kw: Additional keywords to parse to the http response for the current template engine.

    Returns:
            TemplateResponse: Http response rendered using Django or Jinja2.
    """
    allowed_engines = {"jinja2", "django"}

    if engine not in allowed_engines:
        raise TemplateError(
            f"Provided engine not recognized, should be one of ['jinja2', 'django'] not '{engine}' "
        )
    try:
        if engine == "jinja2":
            return jinja2_render(request, template, context, status_code, **kw)
        else:
            return django_render(request, template, context, status_code, **kw)
    except Exception as e:
        _e = e
        e = str(e)
        if "Syntax error" in e or "syntax error" in e:
            raise TemplateError(
                f"Error rendering template, make sure you are using right template engine: {e}"
            ) from _e
        else:
            raise _e  # reraise error


async def async_render(
    request,
    template: str,
    context: Dict[Any, Any] = {},
    status_code: int = 200,
    engine: str = "django",
    **kw,
) -> TemplateResponse:
    """
    Asynchronously renders a template and returns the response.

    Args:
            request (HttpRequest): Http request object.
            template (str): Template path within global or blueprint template dirs.
            context (dict, optional): Dictionary respresenting template context.
            status_code (int): The response status code, defaults to 200.
            engine (str, optional): Template engine to use for rendering template, defaults to 'django'.
            **kw: Additional keywords to parse to the http response for the current template engine.

    Returns:
            TemplateResponse: Http response rendered using Django or Jinja2.
    """
    allowed_engines = {"jinja2", "django"}

    if engine not in allowed_engines:
        raise TemplateError(
            f"Provided engine not recognized, should be one of ['jinja2', 'django'] not '{engine}' "
        )
    try:
        if engine == "jinja2":
            return await sync_to_async(jinja2_render)(request, template, context, status_code, **kw)
        else:
            return await sync_to_async(django_render)(request, template, context, status_code, **kw)
    except Exception as e:
        _e = e
        e = str(e)
        if "Syntax error" in e or "syntax error" in e:
            raise TemplateError(
                f"Error rendering template, make sure you are using right template engine: {e}"
            ) from _e
        else:
            raise _e  # reraise error


def redirect(location: str, permanent: bool = False, content_type="text/html", **kw):
    """
    Returns a HttpRedirectResponse object

    Args:
        location (str): URL location
        permanent (bool): Whether this is a permanent redirect, defaults to False
        content_type (str): Content type for response, defaults to 'text/html'
        **kw: Keyword arguments to parse to HttpRedirectResponse

    Returns:
        HttpRedirectResponse: The http redirect response object.
    """
    return HttpRedirectResponse(
        location=location,
        content_type=content_type,
        permanent=permanent,
        **kw,
    )


def jsonify(data: Any, status_code: int = 200, **kw):
    """
    Returns a JsonResponse object

    Args:
        data (Any): Json serializable data
        status_code (int): The response status code. Defaults to 200.
        **kwargs: Extra keywords to parse to JsonResponse
    
    Returns:
        JsonResponse: The http json response object.
    """
    return JsonResponse(data, status_code=status_code, **kw,) 


def not_found404(request: Optional[HttpRequest] = None, body: str = None) -> HttpResponse:
    """
    Returns a 404 error response, either a simple response or a template response given DEBUG mode is on or off.

    Args:
        request (Optional[HttpRequest]): The target http request.
        body (str, optional): Body for the 404 response.
        
    Returns:
        HttpResponse: The http not found response object.
    """
    if body:
        if SETTINGS['DEBUG']:
            response = template_response(
                HttpNotFoundResponse,
                body=body,
            )
        else:
            response = simple_response(
                HttpNotFoundResponse,
                body=body,
            )
        return response
    return get_404_error_response(request)


def merge(
    base_response: HttpResponse,
    take_response: HttpResponse,
    merge_headers: bool = False,
) -> HttpResponse:
    """
    This merges two http response objects into one http response object

    Notes:
    - By default, this only merge content and content headers.
    - This is useful especially when you have a certain type of HttpResponse (for instance HttpNotFoundResponse) 
       but you want that Base response object to have content of a rendered html file.
    """
    assert isinstance(
        base_response, HttpResponse
    ), f"Argument base_response should be an HttpResponse not {type(base_response)}"
    
    assert isinstance(
        take_response, HttpResponse
    ), f"Argument take_response should be an HttpResponse not {type(take_response)}"

    base_response.content_obj = take_response.content_obj
    
    # Add all content headers from take_response to base response
    base_response.set_content_headers(force_set=True)
    
    if merge_headers:
        base_response.header_obj.headers.update(take_response.header_obj.headers)

    return base_response


def content_replace(
    response: HttpResponse,
    new_data: Union[bytes, str],
    new_content_type: str = "auto",
    new_content_filepath: str = "use_existing",
):
    """
    Replaces response content with new content.

    Args:
        response (HttpResponse): Response to replace content for.
        new_data (Union[bytes, str]): String or bytes to set for content.
        new_content_type (str): The new content type, Defaults to `auto` to automatically determine the content type.
        new_content_filepath (str): Filepath to the content, Defaults to "use_existing" to use the already set filepath.

    """
    assert not isinstance(response, StreamingHttpResponse), "Streaming HTTP response not supported, use `streaming_content_replace` instead."
    assert isinstance(new_data, str) or isinstance(
        new_data, bytes
    ), "Only string or bytes allowed for new_data"

    new_data = new_data.encode("utf-8") if isinstance(new_data, str) else new_data
    
    if not new_content_type:
        raise ValueError(
            "Please provide new_content_type or any of these `use_existing` for no change, `auto` to "
            "automatically determine content type or any valid content type."
        )
    
    elif new_content_type == "auto":
        new_content_type = None

    elif new_content_type == "use_existing":
        new_content_type = response.content_obj.content_type

    if new_content_filepath == "use_existing":
        new_content_filepath = response.content_obj.filepath
    response.content_obj.set_content(new_data, new_content_filepath, new_content_type)

    # Update content type header
    response.set_content_type_header()

    return response


def streaming_content_replace(
    response: StreamingHttpResponse,
    stream: Union[Callable, Iterable[bytes]],
    chunk_size: int = 2 * 1024 * 1024,
) -> None:
    """
    Replaces response content with new content.

    Args:
        response (StreamingHttpResponse): Streaming Http Response to replace content for.
        stream (Union[Callable, Iterable[bytes]]): The new stream.
        chunk_size (int): The new chunk size.
        
    Notes:
    - This approach only replace content, it doesn't touch any headers.
    """
    default_chunk_size = 2 * 1024 * 1024
    
    assert isinstance(response, StreamingHttpResponse), "Normal HTTP response not supported, use `content_replace` instead."
    
    def iter_content_original() -> Iterable[bytes]:
        """
        Returns an iterable (like an asynchronous generator) over the response content.
    
        Ensures that the content provider yields chunks of bytes and not raw bytes or strings directly.
        """
        content = response.content_provider()
        
        if isinstance(content, (str, bytes)):
            raise TypeError(
                "Expected iterable or generator yielding bytes, got raw string or bytes. "
                "Wrap your content in a generator or iterable."
            )
            
        if not isinstance(content, Iterable) and not isasyncgen(content):
            raise TypeError(
                f"Expected an iterable, generator or async_generator, got {type(content).__name__}"
            )
        
        # Return the content provider.
        return content
        
    async def async_iter_content_original() -> Awaitable[Iterable[bytes]]:
        """
        Coroutine which returns an iterable (like an asynchronous generator) over the response content.
    
        Ensures that the content provider yields chunks of bytes and not raw bytes or strings directly.
        """
        content = response.content_provider()
        
        if isinstance(content, (str, bytes)):
            raise TypeError(
                "Expected iterable or generator yielding bytes, got raw string or bytes. "
                "Wrap your content in a generator or iterable."
            )
            
        if not isinstance(content, Iterable) and not isasyncgen(content):
            raise TypeError(
                f"Expected an iterable, generator or async_generator, got {type(content).__name__}"
            )
        
        # Return the content provider
        return content
        
    # Now replace content
    if isinstance(stream, io.IOBase):
        content_provider = lambda: (
            response._read_from_file(stream, chunk_size)
            if not SETTINGS['ASYNC_HANDLING']
            else response._async_read_from_file(stream, chunk_size)
        )
           
    elif callable(stream):
        content_provider = stream
        
        if chunk_size and chunk_size != default_chunk_size and not isinstance(stream, io.IOBase):
            raise ValueError(f"Chunk size has been provided yet, the supplied `stream` is not an IO/file-like object. Got {type(stream)} instance.")
                
    elif isinstance(stream, Iterable):
        content_provider = lambda: stream
        
        if chunk_size and chunk_size != default_chunk_size and not isinstance(stream, io.IOBase):
            raise ValueError(f"Chunk size has been provided yet, the supplied `stream` is not an IO/file-like object. Got {type(stream)} instance.")
        
    else:
        raise ValueError("Stream must be either a callable, iterable or a file-like object.")
        
    response.content_provider = content_provider
    response.iter_content = iter_content_original
    response.async_iter_content = async_iter_content_original
            

def replace_response(
  old_response: HttpResponse,
  new_response: HttpResponse,
  full_replacement: bool = True,
) -> HttpResponse:
    """
    Replaces/transforms the old response into a new response object (inplace).
    
    Args:
        old_response (HttpResponse): The response you want to apply modifications to.
        new_response (HttpResponse): The base response you want to get values or reference data from.
        full_replacement (bool): Whether to completely alter the old response into identical response with the new response (defaults to True).
          As the name suggests, this replaces all attributes of old with new ones and even the response type will become the same as the new one's.
          If set to False, the old response will keep its attributes but status, headers & content will change.
          This might not work if responses includes unmatching `__slots__` attributes.
          
    Returns:
        HttpResponse: The old response but transformed or combined with new response
    """
    
    if isinstance(old_response, StreamingHttpResponse):
        # Stream might need to be closed first.
        if hasattr(old_response, "stream") and hasattr(old_response.stream, "close"):
          convert_to_sync_if_needed(old_response.stream.close)() # close stream before replacing response
          
    if full_replacement:
      # A little hack to alter response inplace.
      old_response.__class__ = new_response.__class__
      old_response.__dict__ = new_response.__dict__
      return old_response
   
    # Else, use a different approach for replacement.
    old_response.payload_obj = new_response.payload_obj
    
    if isinstance(old_response, StreamingHttpResponse):
        if isinstance(new_response, StreamingHttpResponse):
            # New and old response are both streaming http responses
            streaming_content_replace(old_response, stream=new_response.stream)
            
        else:
            # New response is not a streaming http response
            streaming_content_replace(old_response, stream=[new_response.content])
            
    else:
        if isinstance(new_response, StreamingHttpResponse):
            raise ValueError("Old response is not compatible with new response, i.e. StreamingHttpResponse")
        old_response.content_obj = new_response.content_obj
    return old_response


@lru_cache(maxsize=1024)
def resolve(name: str, absolute: bool = True, fallback_url: Optional[str] = None) -> str:
    """
    This resolves a URL based on name.

    Args:
        name (str): The name of the URL to resolve.
        absolute (bool): This will return the absolute url instead of registered path only but it requires the app to be in running state
        fallback_url (Optional[str]): The fallback url to use if the URL is not found.
        
    ``` {important}
    This function is primarily designed for resolving URLs registered as plain, static paths. 
     
     It is strongly recommended to use this function only with URLs registered in the form:
     `
     pattern = '/url/path'
     `

     Using this function with dynamic URLs (e.g., those containing path parameters or regular expression patterns) will return the raw, unregistered pattern, which is typically not useful for direct use. 
     
     For example, using it with:
     `
     pattern = '/url/<some_input>/path'  
     pattern = '/url/hello*'
     `
         
    will return those patterns as is, and not a resolved URL.
    ```
    
    Raises:
        (URLResolveError): Raised if there is no url associated with the name, url associated with the name is not a plain url
    """
    try:
        info = RouteRegistry.fetch_route_info_by_name(name)
        url = info["url"]
        handler = info["handler"]
        
        if absolute:
            # build absolute url
            if type(handler) == type and issubclass(handler, WebSocketView):
                root_url = Meta.get_absolute_ws_server_url()
            else:
                root_url = Meta.get_absolute_server_url()

            # return absolute url
            abs_url = build_absolute_uri(root_url, url, normalization_ignore_chars=["*", "<", ">"])
            return abs_url
        return "/" + url if not url.startswith("/") else url

    except RouteNotFoundError:
        if fallback_url:
            return fallback_url
        raise URLResolveError(f"No URL in registry is associated with name '{name}' ")


def to_response(value: Any, **kwargs) -> Union[BaseResponse, HttpResponse]:
    """
    Converts any value to http response (including html components).
    
    Args:
        value (Any): The target object to convert/transform.
        **kwargs: The keyword arguments to parse to the HTTP response instance.
        
    Raises:
        TypeError: If the value is not convertable to http response.
    
    Notes:
    - If value is already a response object, nothing will be done.

    """
    allowed_types = (int, str, bytes, float, dict, list, set, Component)

    if not isinstance(value, BaseResponse):
        if not any([isinstance(value, t) for t in allowed_types]):
            raise TypeError(f"Value '{value}' cannot be converted to http response. Consider these types: {allowed_types}")
        if isinstance(value, Component):
            value = ComponentResponse(value, **kwargs)
        else:
            value = HttpResponse("%s" % value if not isinstance(value, bytes) else value, **kwargs)
    return value
