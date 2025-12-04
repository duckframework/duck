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
from duck.contrib.sync import iscoroutinefunction
from duck.logging import logger
from duck.utils.caching import InMemoryCache
from duck.utils.callabletools import get_callable_type


VIEW_CACHE = InMemoryCache(maxkeys=2048)


class ViewCachingError(Exception):
    """
    Raised when the cached_view decorator fails.
    """
    pass


class ViewCachingWarning(UserWarning):
    """
    Warning that will be logged if user tries to cache a view which might cause issues.
    """


def cached_view(
    targets: Union[Dict[str, Dict[str, Any]], List[str]],
    expiry: Optional[float] = None,
):
    """
    Decorator for caching view outputs based on selected request attributes
    or computed callable results.

    Args:
        targets (Union[Dict[str, Dict[str, Any]], List[str]]):
            List[str]:
                Direct attribute names on the request to include in the cache key.

            Dict[str, Dict[str, Any]]:
                Callable targets with dynamic args/kwargs.
                Example:
                ```py
                    {
                        "some_callable": {"args": (...), "kwargs": {}},
                        "call_with_format": {"args": "{request.user_id}", "kwargs": {}},
                    }
                ```
                
        expiry (Optional[float]):
            Cache expiry in seconds. If None, backend defaults apply.

    Returns:
        Callable: Wrapped view function with caching.

    Raises:
        ViewCachingError: If a target is misconfigured or missing.

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
    ```
    
    Notes:
    - Dynamic args support formatting: "{request.path}" etc.
    - Cache keys use stable, hashable tuples for high performance.
    - This works on both synchronous/asynchronous callables. 
    """
    # TODO: Implement logic for using custom function as a target so a to compute dynamic args/kwargs.
    # E.g.: {<my_function>: {'args': ..., 'kwargs': ...}}
    
    if not isinstance(targets, (list, dict)):
        raise ViewCachingError(
            f"Targets must be list or dict, not {type(targets)}"
        )

    if not targets:
        raise ViewCachingError("Targets cannot be empty.")

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

        return value(*resolved_args, **resolved_kwargs)

    def resolve_targets(request: HttpRequest) -> Dict[str, Any]:
        """
        Resolve all target values from the request.

        Args:
            request (HttpRequest): The request object.

        Returns:
            Dict[str, Any]: Mapping of target name → resolved value.
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
            for name, spec in targets.items():
                try:
                    attr = getattr(request, name)
                except AttributeError:
                    raise ViewCachingError(
                        f"Target '{name}' not found on request."
                    )

                if callable(attr):
                    resolved[name] = compute_callable_value(request, name, spec)
                else:
                    resolved[name] = attr
        return resolved

    def decorator(view_handler: Callable):
        """
        Wrapper responsible for caching.
        """
        
        def maybe_warn_user(result: Union[HttpResponse, Any]):
            """
            Function which decides whether to log a warning depending on result computed from the original view.
            """
            from duck.html.components.core.system import LivelyComponentSystem
            
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
            # New try to wrap exceptions that happen in here because they 
            # are needed by Duck to produce the correct response based on exception.
            view_obj = None
            
            if isinstance(request, View):
                # A method has been wrapped with this decorator
                view_obj = request
                request = view_obj.request
                kwargs = view_obj.kwargs
                
            # Resolve targets and their values.
            resolved = resolve_targets(request)
            cache_key = (
                frozenset(resolved.items()),
                args,
                frozenset(kwargs.items()),
            )
            
            # Return cached if available
            cached = VIEW_CACHE.get(cache_key)
            
            if cached is not None:
                return cached
                
            if not view_obj:
                # This decorator is being used on straight function
                result = view_handler(request, *args, **kwargs)
            else:
                # Decorator is being used on View.run method
                result = view_handler(view_obj) # No args/kwargs are needed on View.run.
            
            # Update cache
            VIEW_CACHE.set(cache_key, result, expiry)
            
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
                
            # Resolve targets and their values.
            resolved = resolve_targets(request)
            cache_key = (
                frozenset(resolved.items()),
                args,
                frozenset(kwargs.items()),
            )
            
            # Return cached if available
            cached = VIEW_CACHE.get(cache_key)
            
            if cached is not None:
                return cached
                
            if not view_obj:
                # This decorator is being used on straight function
                result = await view_handler(request, *args, **kwargs)
            else:
                # Decorator is being used on View.run method
                result = await view_handler(view_obj) # No args/kwargs are needed on View.run.
            
            # Update cache
            VIEW_CACHE.set(cache_key, result, expiry)
            
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
