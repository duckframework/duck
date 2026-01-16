"""
Module for caching components.
"""
import copy

from functools import wraps
from typing import (
    Optional,
    Dict,
    Any,
    List,
    Union,
    Type,
    Callable,
    Tuple,
    Iterable,
)

from duck.utils.caching import InMemoryCache
from duck.utils.threading.threadpool import get_or_create_thread_manager


DEFAULT_CACHE_BACKEND = InMemoryCache(maxkeys=2048)


# NOTE: Whilst we are rendering component in background, computing vdom or
# rendering different component whilst tasks are being executed in background results 
# in increased latency because of background tasks being executed by another thread.

# In general, computing becomes slower if busy background threads exist (not doing I/O)


class ComponentCachingError(Exception):
    """
    Raised upon component caching error.
    """


def make_cache_key(component_cls, args: Any, kwargs: Dict[str, Any], namespace: Optional[str] = None) -> Tuple:
    """
    Returns a cache key.
    """
    ns = ""
    kwargs_items = kwargs.items()
    if namespace:
        ns = namespace(component_cls) if callable(namespace) else namespace
    return (ns, component_cls, frozenset(args), frozenset(kwargs_items))


def cached_component(
    targets: Optional[List[Union[str, Callable]]] = None,
    cache_backend: Optional[Any] = None, 
    expiry: Optional[float] = None,
    namespace: Optional[Union[str, Callable]] = None,
    ignore_args: Optional[List[int]] = None,
    ignore_kwargs: Optional[List[str]] = None,
    skip_cache_attr: str = "skip_cache",
    on_cache_result: Optional[Callable] = None,
    freeze: bool = False,
    return_copy: bool = True,
    _no_caching: bool = False,
):
    """
    Decorator for returning cached components.
    
    Create a new instance or return a cached instance.
        
    Args:
        targets (Optional[List[Union[str, Callable]]]): These are component keyword arguments to focus on when caching or a custom caching callable which returns cache value.
            Example
            ```py
            targets = ["some_keyword_arg", <custom_callable>]
            ```
        cache_backend (Optional[Any]): A custom cache backend which implements methods `get` and `set`. If None, default cache backend is used.
        expiry (Optional[float]): The expiry for cache keys. Defaults to None.
        namespace (Optional[Union[str, Callable]]): Optional string or callable returning a namespace prefix for keys. 
            Use `namespace` for grouping and easy bulky cache invalidation.  
        ignore_args (Optional[List[int]]): Indices to ignore in arguments. For example to ignore first argument when caching, `[0]` may be parsed as `ignore_args`.
        ignore_kwargs (Optional[List[str]]): Keyword arguments keys to ignore when caching.
        skip_cache_attr (str): Optional component attribute to skip caching (for debugging). This defaults to `skip_cache`, meaning,
            if `component.skip_cache=True` then, cache is skipped for that component.
        on_cache_result (Optional[Callable]): This is a callable that can be executed upon receiving a result from cache. If some 
            data needs to be reinitialized, you can do this here.
       freeze (bool): Whether to freeze cached components. Defaults to True. This enables fast re-rendering.
       returns_copy (bool): Whether to return a copy of the original cached component. This enables separation of concerns and avoids ComponentError 
            when the component wants to be added to a new component tree. Defaults to True. This is only looked at if `freeze=False` and the component class 
            is not a subclass of `Page` component. All static pages (frozen) will not be returned as copies.
    """
    from duck.html.components import Component, ComponentCopyError
    from duck.html.components.page import Page
    
    if targets and ignore_args:
        raise ComponentCachingError("When 'targets' argument is supplied, only keys in the targets list are used. Argument 'ignore_args' is not applicable.")
        
    if targets and ignore_kwargs:
        raise ComponentCachingError("When 'targets' argument is supplied, only keys in the targets list are used. Argument 'ignore_kwargs' is not applicable.")
        
    cache_backend = cache_backend or DEFAULT_CACHE_BACKEND
    
    def resolve_cache_key_args_kwargs(component_args: Iterable, component_kwargs: Dict):
        """
        Resolve args & kwargs to use for producing cache_key.
        """
        resolved_args = list(component_args)
        resolved_kwargs = {}
        
        if targets:
            # Targets explicitly provided, use those.
            # Build resolved_kwargs only, args not supported if targets provided.
            # Reset resolved args and focus only on kwargs
            resolved_args = ()
            
            for target in targets:
                if callable(target):
                    # This is a custom callable
                    fn = target
                    try:
                       # This is a custom external function
                       # use __qualname__ to ensure stable hashable representation
                        key = getattr(target, "__qualname__", repr(target))
                        resolved_kwargs[key] = fn(*component_args, **component_kwargs)
                        continue
                    except Exception as e:
                        raise ComponentCachingError(f"Error computing result for the callable target '{fn}': {e}.") from e
                
                # This is an ordinary key
                key = target
                
                try:
                    value = component_kwargs[key]
                    resolved_kwargs[key] = value
                except KeyError:
                    raise ComponentCachingError(f"Key '{key}' provided in targets is not found in component keyword arguments.")
        
        else:
            # Build resolved_args first.
            if ignore_args:
                for idx in ignore_args:
                    try:
                        resolved_args.pop(idx)
                    except IndexError:
                        raise ComponentCachingError(f"Index '{idx}' provided in ignore_args does not match any index in component positonal arguments.")
            
            # Build resolved_kwargs
            resolved_kwargs = component_kwargs.copy()
            
            if ignore_kwargs:
                for key in ignore_kwargs:
                    try:
                        resolved_kwargs.pop(key)
                    except KeyError:
                        raise ComponentCachingError(f"Key '{key}' provided in ignore_kwargs is not found in component keyword arguments.")
        
        # Return final args & kwargs
        return (resolved_args, resolved_kwargs)
        
    def decorator(component_cls: Type):
        assert issubclass(component_cls, Component), f"Component class must be a subclass of HtmlComponent. Got {component_cls}."
        
        @wraps(decorator)
        def wrapper(*component_args, **component_kwargs):
            # Generate cache args and kwargs.
            cache_key_args, cache_key_kwargs = resolve_cache_key_args_kwargs(component_args, component_kwargs)
            
            # Try creating cache key
            try:
                cache_key = make_cache_key(component_cls, cache_key_args, cache_key_kwargs, namespace)
            except KeyError as e:
                raise KeyError("Error making cache key: {e}. Try using argument `targets` with simpler keys like 'id' or just utilize the 'namespace' argument.")
             
            
            # Retrieve existing component from cache.
            resolved = cached = cache_backend.get(cache_key)
             
            if resolved is None:
                # Compute live result
                resolved = component_cls(*component_args, **component_kwargs)
                do_caching = not _no_caching and not getattr(resolved, skip_cache_attr, False)
                
                # Decide whether to cache this component
                if do_caching:
                    # Component is cacheable, cache it
                    cache_backend.set(cache_key, resolved, expiry=expiry)
                    
                # Freeze component if needed
                if freeze:
                    # Ensure component is frozen
                    resolved.ensure_freeze()
            
            else:
                # This is from cache
                if not resolved._is_from_cache:
                    resolved._is_from_cache = True
                
            # Continue
            if return_copy: # Return a copy to avoid altering the original component
                original_component = resolved
                
                if original_component.is_frozen() and issubclass(component_cls, Page):
                    # For all static page components, never return a copy
                    return original_component
                
                if original_component.is_loading():
                    original_component.wait_for_load()
                
                try:
                    if resolved.is_frozen():
                        # Only do shallow copy if component is frozen, meaning component is 
                        # purely static and there is no dynamic content.
                        resolved = resolved.copy(shallow=True)
                except ComponentCopyError:
                    pass
               
                if not resolved.is_a_copy():
                    # Shallow copy might have failed
                    resolved = resolved.copy()
                
                if not cached:
                    # The original component is not cached yet.
                    # If we are returning a copy, make sure we do component load, pre_render & more to the original component
                    # so that the next time the component is retrieved, it's faster, no need to load the component again.
                    is_loaded = original_component.is_loaded()
                    is_frozen = original_component.is_frozen()
                    pre_render = original_component.pre_render
                    render = original_component.render
                    
                    # For loaded components, submit tasks independantly (more granular for keeping threads mostly free)
                    # but for components not yet loaded, bulk tasks load() followed by other tasks (more busy threads because of many bulk tasks)
                    tasks = [render if freeze or is_frozen else pre_render, lambda: original_component.to_vdom]
                    component_threadpool_manager = get_or_create_thread_manager(id="component-threadpool-manager", strictly_get=True)
                    
                    if not is_loaded:
                        tasks.insert(0, original_component.load) # If freeze=True, component will be freezed on load()
                        
                    # Submit tasks
                    if is_loaded:
                        # Submit tasks independently
                        for task in tasks:
                            component_threadpool_manager.submit_task(task, task_type="component-task")
                    else:
                        def execute_batched_tasks():
                            # Execute tasks as a batch
                            for task in tasks:
                                task()
                        
                        # Submit one bulked task
                        component_threadpool_manager.submit_task(execute_batched_tasks, task_type="component-task")
                        
            # Finally return component
            if cached and on_cache_result:
                # Call on_cache_result hook
                on_cache_result(resolved)
            
            # Finally return resolved component
            if freeze:
                resolved.ensure_freeze()  
            return resolved             
        return wrapper
    return decorator


def CachedComponent(component_cls: Type, **cache_options):
    """
    This is a nested function which you can use directly with component classes 
    without the need of using `cached_component` decorator.  
    
    Example:
    ```py
    cached_btn_func = CachedComponent(
        Button,
        namespace="welcome-btn",
        targets=["id", "text"],
    ) # Returns function for retrieving or creating the button instance.
    
    btn = cached_btn_func(id="my-btn", text="Hello world")
    btn.is_from_cache() # Returns False for the first time and True otherwise
    btn.is_a_copy() # Returns True by default.
    ``` 
    """
    return cached_component(**cache_options)(component_cls)
