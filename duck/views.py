"""
Duck view system.

This module defines the base `View` class, which serves as the foundation
for handling HTTP requests in the Duck web framework. Views process incoming
`HttpRequest` objects and return `HttpResponse` objects.

Developers can subclass `View` to define custom request handling logic by
overriding the `run()` method. This abstraction allows separation of business
logic from routing and middleware.
"""
import inspect

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
    ensure_async,
    ensure_sync,
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


def csrf_exempt(view_func):
    """
    Decorator that marks a view as exempt from CSRF middleware checks.

    Usage:
        @csrf_exempt
        def my_view(request):
            ...

        @csrf_exempt
        async def my_async_view(request):
            ...
    """
    if iscoroutinefunction(view_func):
        @wraps(view_func)
        async def wrapped_view(request, *args, **kwargs):
            return await view_func(request, *args, **kwargs)
    else:
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            return view_func(request, *args, **kwargs)
            
    # Set csrf exempt flag
    wrapped_view.csrf_exempt = True
    return wrapped_view

def cached_view(
    targets: Union[Dict[Union[str, Callable], Dict[str, Any]], List[str]],
    expiry: Optional[float] = None,
    cache_backend: Optional = None,
    namespace: Optional[Union[str, Callable]] = None,
    skip_cache_attr: str = "skip_cache",
    on_cache_result: Optional[Callable] = None,
    returns_static_response: bool = False,
    freeze_if_component_response: bool = True,
):
    """
    Decorator for caching view outputs based on selected request attributes
    or computed callable results.

    This decorator supports:
     - Direct request attribute extraction.
     - Callable attributes on the request (with dynamic args/kwargs).
     - External Python callables used as cache-key producers.
     - Sync and async view handlers, including View.run methods.
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
                    "{request.path}" ➝ replaced at runtime.

        expiry (Optional[float]):
            TTL/expiry in seconds. If None, backend default TTL is used.

        cache_backend (Optional[Any]):
            A cache backend implementing:
                get(key)
                set(key, value, ttl)
            Async backends or sync backends are both supported.

        namespace (Optional[Union[str, Callable]]): Optional string or callable returning a namespace prefix for keys.
            Use `namespace` for grouping and easy bulk cache invalidation.

            Example:
            ```py
            @cached_view(targets=['path'], namespace=lambda request: request.COOKIES.get('user_id'))
            def handler(request):
                # Caches based on USER ID instead of global caching.
                return HttpResponse("OK")
            ```

        skip_cache_attr (str): Optional request attribute to skip caching (for debugging). Defaults to
            `skip_cache`, meaning if `request.skip_cache=True` then caching is skipped for that request.

        on_cache_result (Optional[Callable]): Callable executed upon receiving a result from cache. Use this
            if some data needs to be reinitialized.

        returns_static_response (bool): By default, caching a view that returns a component or component
            response while `LivelyComponentSystem` is active and not disabled on the target component may
            raise `ViewCachingWarning`. Setting this to True tells the system the component is static and
            safe from direct user-specific alteration, avoiding the warning.

        freeze_if_component_response (bool): Whether to freeze the target component if the result is a
            component/component response. Boosts performance by >=50%, and only applies if
            `returns_static_response=True`.

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
        # View that will be cached based on request's path only.
        return HttpResponse("OK")

    class MyView(View):
        @cached_view(targets=["fullpath", "method"])
        async def run(self, request, **kwargs):
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
    - Works transparently on both synchronous and asynchronous views, and on View.run methods.
    - Sync cache backends are auto-wrapped for async views; async backends are auto-wrapped for sync views.
    - Callable targets may raise errors at runtime; these are wrapped into ViewCachingError.
    - When Lively Component System is active, caching Component or ComponentResponse
      will issue a safety warning to avoid state leakage across users.
    - targets=[] is not allowed ➝ caching requires at least one dimension of variation.
    - Namespace allows per-user, per-tenant, or per-feature cache isolation.
    - Setting `request.skip_cache = True` will bypass caching.
    - For callable targets, if caching can no longer proceed, e.g. some data is unavailable, raise
      `SkipViewCaching` to tell the caching system that caching is not possible for this request.
    """
    # Fall back to the shared default cache if none was provided
    cache_backend = cache_backend or DEFAULT_VIEW_CACHE

    # Validate the cache backend implements the required interface
    try:
        if not callable(cache_backend.get):
            raise ViewCachingError(f"The provided cache backend {cache_backend} attribute `get` must be a callable or method.")
    except AttributeError:
        raise ViewCachingError(f"The provided cache backend {cache_backend} must implement method `get`.")

    try:
        if not callable(cache_backend.set):
            raise ViewCachingError(f"The provided cache backend {cache_backend} attribute `set` must be a callable or method.")
    except AttributeError:
        raise ViewCachingError(f"The provided cache backend {cache_backend} must implement method `set`.")

    # Validate targets shape upfront
    if not isinstance(targets, (list, dict)):
        raise ViewCachingError(f"Targets must be list or dict, not {type(targets)}")

    if not targets:
        raise ViewCachingError("Targets cannot be empty.")

    def compute_custom_callable(fn: Callable, request: HttpRequest, spec: Dict[str, Any], *view_args, **view_kwargs) -> Any:
        """
        Executes a user-supplied callable target.

        Args:
            fn: Custom function (not an attribute on the request).
            request: The request.
            spec: args/kwargs spec, with dynamic formatting supported.
            *view_args: Positional arguments belonging to the view/handler.
            **view_kwargs: Keyword arguments belonging to the view/handler.

        Returns:
            Any: The callable's return value.

        Notes:
        - Request is always passed as the first argument.
        - View arguments are always passed before resolved arguments.
        """
        args = spec.get("args") or ()
        kwargs = spec.get("kwargs") or {}

        if not isinstance(args, Iterable):
            raise ViewCachingError(f"Args for target '{fn}' must be iterable, not {type(args)}")
        
        if not isinstance(kwargs, dict):
            raise ViewCachingError(f"Kwargs for target '{fn}' must be a dict, not {type(kwargs)}")

        # Resolve dynamic args
        resolved_args = []
        
        for arg in args:
            try:
                resolved_args.append(arg.format(request=request) if isinstance(arg, str) else arg)
            except Exception as exc:
                raise ViewCachingError(f"Failed formatting arg '{arg}' for custom callable target: {fn}.") from exc

        # Resolve dynamic kwargs
        resolved_kwargs = {}
        
        for key, val in kwargs.items():
            try:
                resolved_kwargs[key] = val.format(request=request) if isinstance(val, str) else val
            except Exception as exc:
                raise ViewCachingError(f"Failed formatting kwarg '{key}={val}' for custom callable target: {fn}.") from exc

        # Call the custom callable with request, view args, then resolved args
        try:
            return fn(request, *view_args, *resolved_args, **view_kwargs, **resolved_kwargs)
        except SkipViewCaching:
            raise
        except Exception as e:
            raise ViewCachingError(f"Error computing result for the callable target '{fn}': {e}.") from e

    def compute_callable_value(request: HttpRequest, name: str, spec: Dict[str, Any]) -> Any:
        """
        Executes a callable attribute on the request with optional dynamic args.

        Args:
            request: Request object.
            name: Attribute name.
            spec: Arguments/kwargs specification.

        Returns:
            Any: The callable's return value.

        Raises:
            ViewCachingError: On formatting errors or type violations.
        """
        value = getattr(request, name)

        if not callable(value):
            raise ViewCachingError(f"Target '{name}' expected to be callable but isn't.")

        # Avoid spec.get('args', ()) since args can explicitly be None
        args = spec.get("args") or ()
        kwargs = spec.get("kwargs") or ()

        if not isinstance(args, Iterable):
            raise ViewCachingError(f"Args for target '{name}' must be iterable, not {type(args)}")
        
        if not isinstance(kwargs, dict):
            raise ViewCachingError(f"Kwargs for target '{name}' must be a dict, not {type(kwargs)}")

        # Resolve dynamic args
        resolved_args = []
        
        for arg in args:
            try:
                resolved_args.append(arg.format(request=request) if isinstance(arg, str) else arg)
            except Exception as exc:
                raise ViewCachingError(f"Failed formatting arg '{arg}' for '{name}'.") from exc

        # Resolve dynamic kwargs
        resolved_kwargs = {}
        
        for key, val in kwargs.items():
            try:
                resolved_kwargs[key] = val.format(request=request) if isinstance(val, str) else val
            except Exception as exc:
                raise ViewCachingError(f"Failed formatting kwarg '{key}={val}' for '{name}'.") from exc

        # Call the resolved attribute with the resolved args/kwargs
        try:
            return value(*resolved_args, **resolved_kwargs)
        except SkipViewCaching:
            raise
        except Exception as e:
            raise ViewCachingError(f"Error computing result for the resolved callable target '{value}': {e}.") from e

    def resolve_targets(request: HttpRequest, *view_args, **view_kwargs) -> Dict[str, Any]:
        """
        Resolves all target values from the request.

        Args:
            request: The request object.
            *view_args: Positional arguments for the view.
            **view_kwargs: Keyword arguments for the view.

        Returns:
            Dict[str, Any]: Mapping of target name to resolved value.

        Notes:
        - view_args and view_kwargs are only passed to custom callable targets.
        """
        resolved = {}

        if isinstance(targets, list):
            # Simple attribute lookup
            for name in targets:
                try:
                    resolved[name] = getattr(request, name)
                except AttributeError:
                    raise ViewCachingError(f"Target '{name}' not found on request object: {request}.")
        else:
            # Callable or complex targets
            for target, spec in targets.items():
                spec = spec or {}

                if callable(target):
                    # Custom external function, keyed by qualname for stable hashing
                    key = getattr(target, "__qualname__", repr(target))
                    resolved[key] = compute_custom_callable(target, request, spec, *view_args, **view_kwargs)
                    continue

                # Standard request attribute, possibly callable
                try:
                    attr = getattr(request, target)
                except AttributeError:
                    raise ViewCachingError(f"Target '{target}' not found on request.")

                if callable(attr):
                    resolved[target] = compute_callable_value(request, target, spec)
                else:
                    resolved[target] = attr
        return resolved

    def make_cache_key(request, resolved: dict, args, kwargs):
        """
        Builds the cache key from namespace, resolved targets, args and kwargs.
        """
        # Resolve namespace, static or dynamic
        namespace_value = ""
        
        if namespace:
            namespace_value = namespace(request) if callable(namespace) else namespace
        return (namespace_value, frozenset(resolved.items()), args, frozenset(kwargs.items()))

    def decorator(view_handler: Callable):
        """
        Wraps view_handler with caching behavior, sync or async.
        """

        def maybe_warn_user(result: Union[HttpResponse, Any]):
            """
            Logs a ViewCachingWarning if caching result may cause issues.
            """
            from duck.html.components.core.system import LivelyComponentSystem

            if returns_static_response:
                # Static components are safe from direct user-specific alteration
                return

            # Warn if caching a live component while Lively is active
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
        def wrapper(first_arg, *args, **kwargs):
            """
            Wraps a view function or View.run method with caching.

            Distinguishes a bound View.run call from a plain function call
            by checking whether the first argument is a View instance, which
            Python's descriptor binding supplies automatically for methods.
            """
            # Detect calling convention: View.run method vs plain function
            if isinstance(first_arg, View):
                view_obj = first_arg
                request = args[0]
                view_args = ()
                view_kwargs = kwargs

                def call_handler():
                    return view_handler(view_obj, request, **view_kwargs)
            else:
                request = first_arg
                view_args = args
                view_kwargs = kwargs

                def call_handler():
                    return view_handler(request, *view_args, **view_kwargs)

            # Bypass caching entirely when the request opts out
            if getattr(request, skip_cache_attr, False):
                return call_handler()

            # Resolve cache-key targets, allowing user opt-out via SkipViewCaching
            try:
                resolved = resolve_targets(request, *view_args, **view_kwargs)
            except SkipViewCaching:
                return call_handler()

            # Look up an existing cached result
            cache_key = make_cache_key(request, resolved, view_args, view_kwargs)
            cached = ensure_sync(cache_backend.get)(cache_key)

            if cached is not None:
                if on_cache_result:
                    on_cache_result(request, cached)
                return cached

            # Compute and store a fresh result
            result = call_handler()
            ensure_sync(cache_backend.set)(cache_key, result, expiry)
            maybe_warn_user(result)

            # Freeze static component results for faster repeated reads
            if returns_static_response and freeze_if_component_response:
                if isinstance(result, Component):
                    result.ensure_freeze()
                elif isinstance(result, ComponentResponse):
                    result.component.ensure_freeze()

            return result

        @wraps(view_handler)
        async def async_wrapper(first_arg, *args, **kwargs):
            """
            Async counterpart to wrapper, using the same calling-convention detection.
            """
            # Detect calling convention: View.run method vs plain function
            if isinstance(first_arg, View):
                view_obj = first_arg
                request = args[0]
                view_args = ()
                view_kwargs = kwargs
                
                async def call_handler():
                    return await view_handler(view_obj, request, **view_kwargs)
            
            else:
                request = first_arg
                view_args = args
                view_kwargs = kwargs

                async def call_handler():
                    return await view_handler(request, *view_args, **view_kwargs)

            # Bypass caching entirely when the request opts out
            if getattr(request, skip_cache_attr, False):
                return await call_handler()

            # Resolve cache-key targets, allowing user opt-out via SkipViewCaching
            try:
                resolved = resolve_targets(request, *view_args, **view_kwargs)
            except SkipViewCaching:
                return await call_handler()

            # Look up an existing cached result
            cache_key = make_cache_key(request, resolved, view_args, view_kwargs)
            cached = await ensure_async(cache_backend.get)(cache_key)

            if cached is not None:
                if on_cache_result:
                    on_cache_result(request, cached)
                return cached

            # Compute and store a fresh result
            result = await call_handler()
            
            # Convert to async
            await ensure_async(cache_backend.set)(cache_key, result, expiry)
            
            # Decide whether to warn user
            maybe_warn_user(result)

            # Freeze static component results for faster repeated reads
            if returns_static_response and freeze_if_component_response:
                if isinstance(result, Component):
                    result.ensure_freeze()
                elif isinstance(result, ComponentResponse):
                    result.component.ensure_freeze()

            return result

        # Return the wrapper matching the handler's sync/async nature
        return async_wrapper if iscoroutinefunction(view_handler) else wrapper

    return decorator


class View:
    """
    Base class for Duck views.

    Subclasses override run(self, request, **kwargs) to handle the
    request. The signature is fixed so views compose cleanly with
    decorators like `login_required`.
    """
    def __init__(self, request: HttpRequest, **kwargs):
        """
        Initialize the view.

        Args:
            request: The incoming HTTP request.
            **kwargs: Parameters extracted from the matched route.
        """
        self.request = request
        self.kwargs = kwargs

    def run(self, request: HttpRequest, **kwargs) -> Optional[HttpResponse]:
        """
        Handle the request.

        Subclasses must override this method.

        Args:
            request: The incoming HTTP request.
            **kwargs: Parameters extracted from the matched route.

        Returns:
            Optional[HttpResponse]: The response generated by the view.
        """
        raise NotImplementedError(
            "Subclasses must implement the run() method and return "
            "the appropriate response."
        )
        
    def dispatch(self) -> Any:
        """
        Dispatch the view using its current request and route parameters.

        Returns:
            Any: The value returned by run().
        """
        return ensure_sync(self.run)(self.request, **self.kwargs)

    async def async_dispatch(self) -> Any:
        """
        Asynchronously dispatch the view using its current request and route parameters.

        Returns:
            Any: The value returned by run().
        """
        return await ensure_async(self.run)(self.request, **self.kwargs)
