"""
Duck view system.

This module defines the base `View` class, which serves as the foundation
for handling HTTP requests in the Duck web framework. Views process incoming
`HttpRequest` objects and return `HttpResponse` objects.

Developers can subclass `View` to define custom request handling logic by
overriding the `run()` method. This abstraction allows separation of business
logic from routing and middleware.
"""
from functools import wraps
from typing import (
    Callable,
    Union,
    Optional,
    List,
    Dict,
    Any,
    Iterable,
)

from duck.http.request import HttpRequest
from duck.http.response import HttpResponse, ComponentResponse
from duck.html.components import Component
from duck.contrib.sync import (
    iscoroutinefunction,
    convert_to_async_if_needed,
    convert_to_sync_if_needed,
)
from duck.logging import logger
from duck.utils.caching import InMemoryCache
from duck.utils.callabletools import get_callable_type


DEFAULT_VIEW_CACHE = InMemoryCache(maxkeys=2048)


class ViewCachingError(Exception):
    """
    Raised when the cached_view decorator fails.
    """
    pass


class SkipViewCaching(Exception):
    """
    This is not an error as such but it's just an interrupt for telling us that caching cannot proceed. This 
    is usually when some data cannot be satisfied or some data is unavailable or broken.  
    
    Example:
    - Lets say user wants to cache views based on `USER ID` but the USER ID is unknown or invalid, user can just raise 
      `SkipViewCaching` exception to tell the system that caching is nolonger possible.
    """


class ViewCachingWarning(UserWarning):
    """
    Warning that will be logged if user tries to cache a view which might cause issues.
    """


def cached_view(
    targets: Union[Dict[Union[str, Callable], Dict[str, Any]], List[str]],
    expiry: Optional[float] = None,
    cache_backend: Optional = None,
    namespace: Optional[Union[str, Callable]] = None,
    skip_cache_attr: str = "skip_cache",
    on_cache_result: Optional[Callable] = None,
    returns_static_response: bool = False,
):
    """
    Decorator for caching view outputs based on selected request attributes
    or computed callable results.
    
    This decorator supports:
     - Direct request attribute extraction.
     - Callable attributes on the request (with dynamic args/kwargs).
     - External Python callables used as cache-key producers.
     - Sync and async view handlers.
     - Sync/async cache backends with automatic compatibility conversion.
    
    The caching system guarantees stable, deterministic cache keys by
    converting all target values into a normalized (and hashable) structure.
    
    Args:
        targets (Union[Dict[Union[str, Callable], Dict[str, Any]], List[str]]):
            Defines which request attributes or computed callable results should
            contribute to the cache key.
    
            - List[str]:
                Direct request attribute lookups.
                Example:
                    ["path", "method"]
    
            - Dict[str or Callable, Dict[str, Any]]:
                Complex targets supporting:
                    { "<request_attr_or_callable>": {"args": (...), "kwargs": {...}} }
                    { my_function: {"args": (...), "kwargs": {...}} }
    
                Dynamic formatting is supported:
                    "{request.path}" → replaced at runtime.
    
        expiry (Optional[float]):
            TTL/expiry in seconds. If None, backend default TTL is used.
    
        cache_backend (Optional[Any]):
            A cache backend implementing:
                get(key)
                set(key, value, ttl)
            Async backends or sync backends are both supported.
        
        namespace (Optional[Union[str, Callable]]: Optional string or callable returning a namespace prefix for keys. 
            Use `namespace` for grouping and easy bulky cache invalidation.  
            
            Example:
            ```py
            
            @cached_view(targets=['path'], namespace=lambda request: request.COOKIES.get('user_id'))
            def handler(request):
                # Caches based on USER ID instead of global caching.
                return HttpResponse("OK")
            ```    
            
        skip_cache_attr (str): Optional request attribute to skip caching (for debugging). This defaults to `skip_cache`, meaning,
            if `request.skip_cache=True` then, cache is skipped for that request.
        
        on_cache_result (Optional[Callable]): This is a callable that can be executed upon receiving a result from cache. If some 
            data needs to be reinitialized, you can do this here.
            
        returns_static_response (bool): By default, If user tries to cache a view which returns either a component or component response whilst 
            `LivelyComponentSystem` is active and is not disabled on the target component. This may lead to `ViewCachingWarning` being raised. This 
            tells the system that the component is a static component and cannot be altered directly by users. So setting this to True avoids `ViewCachingWarning` being 
            logged on safe static components. In the future, this will apply to any dynamic responses.
        
    Returns:
        Callable: Wrapped view function with caching behavior.
    
    Raises:
        ViewCachingError:
            Malformed target configuration, formatting errors,
            missing attributes, or errors inside computed callables.

    Example:
    ```py
    from duck.views import View
    from duck.utils.performance import exec_time
    
    @cached_view(targets=["path"])
    def handler(request):
        # View that will be cached based on request's path only.'
        return HttpResponse("OK")
        
    class myView(View):
        @cached_view(targets=["fullpath", "method"])
        async def run(self):
            # View that will be cached based on request's path plus method.
            return HttpResponse("OK")
            
    exec(handler)() # Slow for the first time, prints more time 
    exec_time(handler)() # Fast, prints less time.
    
    # Complex caching
    @cached_view(targets={"callable_request_attribute": {'args': "{request.path}"})
    def handler_2(request):
        # View is cached based on request callable attribute.
        return HttpResponse("OK")
    
    @cached_view(targets={my_custom_function: {'args': "{request.path}"})
    def handler_3(request):
        # View cached based on custom external function.
        return HttpResponse("OK")
    ```
    
    Notes:
    - Dynamic formatting ("{request.path}") is supported everywhere.
    - Cache keys use stable frozenset+tuple structures for high hashing performance.
    - Custom callables receive: (request, *view_args, *resolved_args, **view_kwargs, **resolved_kwargs)
    - Works transparently on both synchronous and asynchronous views.
    - Sync cache backends are auto-wrapped for async views; async backends are auto-wrapped for sync views.
    - Callable targets may raise errors at runtime; these are wrapped into ViewCachingError.
    - When Lively Component System is active, caching Component or ComponentResponse
      will issue a safety warning to avoid state leakage across users.
    - targets=[] is not allowed — caching requires at least one dimension of variation.
    - Namespace allows per-user, per-tenant, or per-feature cache isolation.
    - Setting `request.skip_cache = True` will bypass caching.
    - For callable targets, if caching can nolonger be possible e.g. some data you might wanna use is unavailable, exception `SkipViewCaching` 
          can be raised to tell the caching system that caching is not possible because of some data invalidity.
    """
    # Now supports logic for using custom function as a target so a to compute dynamic args/kwargs.
    # E.g.: {<my_function>: {'args': ..., 'kwargs': ...}}
    
    cache_backend = cache_backend or DEFAULT_VIEW_CACHE
    
    try:
        if not callable(cache_backend.get):
            raise ViewCachingError(f"The provided cache backend {cache_backend} attribute `get` must be a callable or method.")
    except AttributeError as e:
        raise ViewCachingError(f"The provided cache backend {cache_backend} must implement method `get`.")
        
    try:
        if not callable(cache_backend.set):
            raise ViewCachingError(f"The provided cache backend {cache_backend} attribute `set` must be a callable or method.")
    except AttributeError as e:
        raise ViewCachingError(f"The provided cache backend {cache_backend} must implement method `set`.")
       
    if not isinstance(targets, (list, dict)):
        raise ViewCachingError(
            f"Targets must be list or dict, not {type(targets)}"
        )

    if not targets:
        raise ViewCachingError("Targets cannot be empty.")

    # NEW: Execute an external/custom function target
    def compute_custom_callable(fn: Callable, request: HttpRequest, spec: Dict[str, Any], *view_args, **view_kwargs) -> Any:
        """
        Execute a user-supplied callable target.

        Args:
            fn (Callable): Custom function (not an attribute on the request)
            request (HttpRequest): The request
            spec (dict): args, kwargs — dynamic formatting supported.
            *view_args: These are positional arguments that belong to the view/handler.
            **view_kwargs: These are keyword arguments that belong to the view/handler.
            
        Returns:
            Any
        
        Notes:
        - We always parse request as the first argument.
        - View arguments are always parsed first before resolved arguments.
        """
        args = spec.get("args") or ()
        kwargs = spec.get("kwargs") or {}

        if not isinstance(args, Iterable):
            raise ViewCachingError(
                f"Args for target '{fn}' must be iterable, not {type(args)}"
            )
        if not isinstance(kwargs, dict):
            raise ViewCachingError(
                f"Kwargs for target '{fn}' must be a dict, not {type(kwargs)}"
            )

        # Resolve arguments 
        resolved_args = []
        for arg in args:
            try:
                resolved_args.append(
                    arg.format(request=request) if isinstance(arg, str) else arg
                )
            except Exception as exc:
                raise ViewCachingError(f"Failed formatting arg '{arg}' for custom callable target: {fn}.") from exc

        resolved_kwargs = {}
        for key, val in kwargs.items():
            try:
                resolved_kwargs[key] = (
                    val.format(request=request) if isinstance(val, str) else val
                )
            except Exception as exc:
                raise ViewCachingError(
                    f"Failed formatting kwarg '{key}={val}' for custom callable target: {fn}."
                ) from exc

        # Return computed value
        try:
            return fn(request, *view_args, *resolved_args, **view_kwargs, **resolved_kwargs)
        
        except SkipViewCaching as e:
            raise e # Reraise exception
            
        except Exception as e:
             raise ViewCachingError(f"Error computing result for the callable target '{fn}': {e}.") from e
             
    def compute_callable_value(request: HttpRequest, name: str, spec: Dict[str, Any]) -> Any:
        """
        Execute a callable attribute on the request with optional dynamic args.

        Args:
            request (HttpRequest): Request object.
            name (str): Attribute name.
            spec (Dict[str, Any]): Arguments/kwargs specification.

        Returns:
            Any: The callable's return value.

        Raises:
            ViewCachingError: On formatting errors or type violations.
        """
        value = getattr(request, name)

        if not callable(value):
            raise ViewCachingError(
                f"Target '{name}' expected to be callable but isn't."
            )

        # Don't use spec.get('args', ()) because args can be None
        args = spec.get("args") or ()
        kwargs = spec.get("kwargs") or ()

        if not isinstance(args, Iterable):
            raise ViewCachingError(
                f"Args for target '{name}' must be iterable, not {type(args)}"
            )
        if not isinstance(kwargs, dict):
            raise ViewCachingError(
                f"Kwargs for target '{name}' must be a dict, not {type(kwargs)}"
            )

        # Dynamic args
        resolved_args = []
        for arg in args:
            try:
                resolved_args.append(
                    arg.format(request=request) if isinstance(arg, str) else arg
                )
            except Exception as exc:
                raise ViewCachingError(
                    f"Failed formatting arg '{arg}' for '{name}'."
                ) from exc

        # Dynamic kwargs
        resolved_kwargs = {}
        for key, val in kwargs.items():
            try:
                resolved_kwargs[key] = (
                    val.format(request=request) if isinstance(val, str) else val
                )
            except Exception as exc:
                raise ViewCachingError(
                    f"Failed formatting kwarg '{key}={val}' for '{name}'."
                ) from exc

        # Return computed value
        try:
            return value(*resolved_args, **resolved_kwargs)
        
        except SkipViewCaching as e:
            raise e # Reraise exception
            
        except Exception as e:
             raise ViewCachingError(f"Error computing result for the resolved callable target '{value}': {e}.") from e
        
    def resolve_targets(request: HttpRequest, *view_args, **view_kwargs) -> Dict[str, Any]:
        """
        Resolve all target values from the request.

        Args:
            request (HttpRequest): The request object.
            *view_args: These are arguments for the view.
            **view_kwargs: These are keyword arguments for the view.
            
        Returns:
            Dict[str, Any]: Mapping of target name → resolved value.
        
        Notes:
        - `view_args` and `view_kwargs` are only parsed to custom callable targets.
        """
        resolved = {}

        if isinstance(targets, list):
            # Simple attribute lookup
            for name in targets:
                try:
                    resolved[name] = getattr(request, name)
                except AttributeError:
                    raise ViewCachingError(
                        f"Target '{name}' not found on request object: {request}."
                    )
        else:
            # Callable/complex targets
            for target, spec in targets.items():
                # Normalize spec
                spec = spec or {}
                
                if callable(target):
                    # This is a custom external function
                    # use __qualname__ to ensure stable hashable representation
                    key = getattr(target, "__qualname__", repr(target))
                    resolved[key] = compute_custom_callable(target, request, spec, *view_args, **view_kwargs)
                    continue
    
                # Standard request attribute / callable
                try:
                    attr = getattr(request, target)
                except AttributeError:
                    raise ViewCachingError(
                        f"Target '{target}' not found on request."
                    )

                # Update resolved
                if callable(attr):
                    resolved[target] = compute_callable_value(request, target, spec)
                else:
                    resolved[target] = attr
        return resolved

    def make_cache_key(request, resolved: dict, args, kwargs):
        """
        Returns the cache key for request, resolved data, args and kwargs.
        """
        # resolve namespace
        ns = ""
        if namespace:
            ns = namespace(request) if callable(namespace) else namespace
        return (ns, frozenset(resolved.items()), args, frozenset(kwargs.items()))

    def decorator(view_handler: Callable):
        """
        Wrapper responsible for caching.
        """
        
        def maybe_warn_user(result: Union[HttpResponse, Any]):
            """
            Function which decides whether to log a warning depending on result computed from the original view.
            """
            from duck.html.components.core.system import LivelyComponentSystem
            
            if returns_static_response:
                # The component being returned is a static component and its safe from 
                # direct user-specific alteration.
                return
                
            # Log a warning if components are cached while Lively component system is active
            if LivelyComponentSystem.is_active():
                if isinstance(result, (ComponentResponse, Component)):
                    component = result.component if isinstance(result, ComponentResponse) else result
                    if not getattr(component, "disable_lively", False):
                        logger.warn(
                            (
                                "Caching components or ComponentResponses while the Lively component system is active "
                                "may lead to inconsistent state across users. Changes to the cached component could "
                                "propagate globally, potentially causing unexpected behavior or security issues."
                            ),
                            ViewCachingWarning,
                        )

        
        @wraps(view_handler)
        def wrapper(request: Union[HttpRequest, View], *args, **kwargs):
            # Never try to wrap exceptions that happen in here because they 
            # are needed by Duck to produce the correct response based on exception.
            view_obj = None
            
            if isinstance(request, View):
                # A method has been wrapped with this decorator
                view_obj = request
                request = view_obj.request
                kwargs = view_obj.kwargs
                
            if getattr(request, skip_cache_attr, False):
                if not view_obj:
                    # This decorator is being used on straight function
                    result = view_handler(request, *args, **kwargs)
                else:
                    # Decorator is being used on View.run method
                    result = view_handler(view_obj) # No args/kwargs are needed on View.run.
                
                # Skip caching and return response immediately
                return result
                
            # Resolve targets and their values.
            try:
                resolved = resolve_targets(request, *args, **kwargs)
            except SkipViewCaching:
                # This exception is raised by user if cache cannot proceed, e.g. some data is missing or cannot 
                # be satisfied.
                if not view_obj:
                    # This decorator is being used on straight function
                    result = view_handler(request, *args, **kwargs)
                else:
                    # Decorator is being used on View.run method
                    result = view_handler(view_obj) # No args/kwargs are needed on View.run.
                
                # Skip caching and return response immediately
                return result
            
            # Continue with caching.    
            cache_key = make_cache_key(request, resolved, args, kwargs)
            
            # Return cached if available
            cached = convert_to_sync_if_needed(cache_backend.get)(cache_key)
            
            if cached is not None:
                if on_cache_result:
                    on_cache_result(request, cached)
                return cached
                
            if not view_obj:
                # This decorator is being used on straight function
                result = view_handler(request, *args, **kwargs)
            else:
                # Decorator is being used on View.run method
                result = view_handler(view_obj) # No args/kwargs are needed on View.run.
            
            # Update cache
            convert_to_sync_if_needed(cache_backend.set)(cache_key, result, expiry)
            
            # May log a warning if caching the result may cause issues.
            maybe_warn_user(result)
            
            # Return live computed result
            return result
        
        @wraps(view_handler)
        def method_wrapper(view: View):
            """
            Decorator is being used on a method.
            """
            if not isinstance(view, View):
                raise ViewCachingError(
                    f"Expected a view object, an instance of View but got {type(view)}. "
                    "Please ensure you are using this decorator on correct View object."
                )
            
            # The request and kwargs are stored on the view object.
            request = view.request
            return wrapper(view) # Parse the view object, wrapper knows what to do with that.
            
        # ASYNCHRONOUS IMPLEMENTATIONS
        
        @wraps(view_handler)
        async def async_wrapper(request: Union[HttpRequest, View], *args, **kwargs):
            # New try to wrap exceptions that happen in here because they 
            # are needed by Duck to produce the correct response based on exception.
            view_obj = None
            
            if isinstance(request, View):
                # A method has been wrapped with this decorator
                view_obj = request
                request = view_obj.request
                kwargs = view_obj.kwargs
                
            if getattr(request, skip_cache_attr, False):
                if not view_obj:
                    # This decorator is being used on straight function
                    result = await view_handler(request, *args, **kwargs)
                else:
                    # Decorator is being used on View.run method
                    result = await view_handler(view_obj) # No args/kwargs are needed on View.run.
                
                # Skip caching and return response immediately
                return result
                
            # Resolve targets and their values.
            try:
                resolved = resolve_targets(request, *args, **kwargs)
            except SkipViewCaching:
                # This exception is raised by user if cache cannot proceed, e.g. some data is missing or cannot 
                # be satisfied.
                if not view_obj:
                    # This decorator is being used on straight function
                    result = await view_handler(request, *args, **kwargs)
                else:
                    # Decorator is being used on View.run method
                    result = await view_handler(view_obj) # No args/kwargs are needed on View.run.
                
                # Skip caching and return response immediately
                return result
                
            # Continue with caching
            cache_key = make_cache_key(request, resolved, args, kwargs)
            
            # Return cached if available
            cached = await convert_to_async_if_needed(cache_backend.get)(cache_key)
            
            if cached is not None:
                if on_cache_result:
                    on_cache_result(request, cached)
                return cached
                
            if not view_obj:
                # This decorator is being used on straight function
                result = await view_handler(request, *args, **kwargs)
            else:
                # Decorator is being used on View.run method
                result = await view_handler(view_obj) # No args/kwargs are needed on View.run.
            
            # Update cache
            await convert_to_async_if_needed(cache_backend.set)(cache_key, result, expiry)
            
            # May log a warning if caching the result may cause issues.
            maybe_warn_user(result)
            
            # Return live computed result
            return result
        
        @wraps(view_handler)
        async def async_method_wrapper(view: View):
            """
            Decorator is being used on a method.
            """
            if not isinstance(view, View):
                raise ViewCachingError(
                    f"Expected a view object, an instance of View but got {type(view)}. "
                    "Please ensure you are using this decorator on correct View object."
                )
            
            # The request and kwargs are stored on the view object.
            request = view.request
            return await async_wrapper(view) # Parse the view object, wrapper knows what to do with that.
            
        # Return correct wrapper
        async_ = iscoroutinefunction(view_handler)
        
        if "method" in get_callable_type(view_handler, View):
            return method_wrapper if not async_ else async_method_wrapper
        return wrapper if not async_ else async_wrapper
    return decorator


class View:
    """
    Base class for Duck views (request handlers).

    A view encapsulates logic to handle an HTTP request and produce a response.
    Views are instantiated per request and can carry state during request processing.

    Subclasses should override the `run()` method to implement custom behavior.

    Attributes:
        request (HttpRequest): The incoming HTTP request object.
        kwargs (dict): Additional parameters extracted from the route (e.g., path variables).
    """

    def __init__(self, request: HttpRequest, **kwargs):
        """
        Initializes the view with the incoming request and any route parameters.

        Args:
            request (HttpRequest): The HTTP request to be handled.
            **kwargs: Arbitrary keyword arguments passed from the URL routing, such as path variables.
        """
        self.request = request
        self.kwargs = kwargs

    def strictly_async(self) -> bool:
        """
        Indicates whether the view requires asynchronous execution.

        This is useful in environments like WSGI, where strictly asynchronous
        views should be deferred to an async execution queue instead of being
        executed synchronously.

        Override this method if your view contains non-blocking I/O or requires
        an event loop context.

        Returns:
            bool: True if the view should be treated as strictly async, False otherwise.
        """
        return False

    def run(self) -> Optional[HttpResponse]:
        """
        Handles the request and returns an HTTP response.

        This method should be overridden by subclasses to implement
        custom request handling logic. It must return an `HttpResponse`
        object to be sent to the client.

        If no response is expected (e.g., in cases of low-level socket handling),
        raise `duck.exceptions.all.ExpectingNoResponse` and handle the response
        manually using `request.client_socket` and `request.client_address`.

        Returns:
            Optional[HttpResponse]: The HTTP response or data that can be converted to HTTP response to be returned to the client.

        Raises:
            NotImplementedError: If the method is not overridden in a subclass.
        """
        raise NotImplementedError("Subclasses must implement the run() method and return the appropriate response.")
