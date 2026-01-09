"""
Module for creating static components.
"""
from typing import (
    Type,
    Optional,
    Union,
    List,
    Any,
    Callable,
)

from duck.html.components.utils.caching import (
    cached_component,
    CachedComponent,
)


def static_component(
    use_caching: bool = True,
    cache_targets: Optional[List[Union[str, Callable]]] = None,
    cache_backend: Optional[Any] = None, 
    cache_expiry: Optional[float] = None,
    cache_namespace: Optional[Union[str, Callable]] = None,
    cache_ignore_args: Optional[List[int]] = None,
    cache_ignore_kwargs: Optional[List[str]] = None,
    skip_cache_attr: str = "skip_cache",
    on_cache_result: Optional[Callable] = None,
    return_copy: bool = True,
):
    """
    Decorator for declaring static components.  
    
    Example:
    ```py
    @static_compoment()
    class MyStaticButton(Button):
        pass
    
    btn = MyStaticButton(text="hello world") # New instance
    btn.is_frozen() # True
    btn.is_from_cache() # False for the first time
    btn.is_a_copy() # True if not isinstance of Page component
    
    btn = MyStaticButton(text="hello world") 
    btn.is_from_cache() # True
    ```
    
    Do help on `cached_component` decorator for more information.
    """
    return cached_component(
        targets=cache_targets,
        cache_backend=cache_backend, 
        expiry=cache_expiry,
        namespace=cache_namespace,
        ignore_args=cache_ignore_args,
        ignore_kwargs=cache_ignore_kwargs,
        skip_cache_attr=skip_cache_attr,
        on_cache_result=on_cache_result,
        return_copy=return_copy,
        freeze=True,
        _no_caching=not use_caching,
    )


def StaticComponent(component_cls: Type, **static_options):
    """
    This is a nested function which you can use directly with component classes 
    without the need of using `static_component` decorator.  
    
    Example:
    ```py
    static_btn_func = StaticComponent(
        Button,
        cache_targets=["id", "text"],
    ) # Returns function for retrieving or creating the button instance.
    
    btn = statc_btn_func(id="my-btn", text="Hello world")
    btn.is_from_cache() # Returns False for the first time and True otherwise
    btn.is_a_copy() # Returns True by default.
    btn.is_a_copy() # True if not isinstance of Page component
    ``` 
    """
    return static_component(**static_options)(component_cls)
