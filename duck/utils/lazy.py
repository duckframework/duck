"""
Lazily evaluates a callable and caches its result with an LRU policy.
"""
import types
import asyncio
import functools

from collections import OrderedDict
from typing import Callable, Tuple, Any


class LazyError(Exception):
    """Custom exception for Lazy evaluation errors."""
    pass


class Lazy:
    """
    Lazily evaluates a callable and caches its result with an LRU policy.
    
    Supports automatic delegation of most magic methods, including:
    - Standard dunders (len, iter, str, etc.)
    - Awaitable (async/await)
    - Context manager
    - Async generator
    
    Notes:
    - You can set `nocache=True` to compute live results.
    """

    _global_cache: OrderedDict[Tuple[Callable, Tuple, Tuple], Any] = OrderedDict()
    _max_size: int = 256

    __slots__ = (
        "_Lazy__callable",
        "_Lazy__args",
        "_Lazy__kwargs",
        "_Lazy__result",
        "_Lazy__nocache",
        "_Lazy__extra_data",
    )

    __all_private_attrs = {}

    def __init__(self, _callable: Callable, nocache: bool = False, *args, **kwargs):
        self.__callable = _callable
        self.__args = args
        self.__kwargs = kwargs
        self.__nocache = nocache
        self.__extra_data = {}
        
        if not type(self).__all_private_attrs:
            type(self).__all_private_attrs = {
                "__getattr__", "__setattr__", "getresult", "__class__",
                "__call__", "__bool__", "extra_data",
            }

    @property
    def extra_data(self) -> dict:
        """
        Returns the dictionary for storing extra data.
        """
        return self.__extra_data
        
    def __getattribute__(self, key):
        if key in type(self).__all_private_attrs or key in type(self).__slots__:
            return super().__getattribute__(key)
        try:
            return getattr(super().__getattribute__('getresult')(), key)
        except AttributeError as e:
            raise LazyError(f"Attribute '{key}' not found in lazy-loaded object: {e}")
        except Exception as e:
            raise LazyError(f"Error accessing attribute '{key}': {e}")

    def __setattr__(self, key, value):
        if key in (*type(self).__slots__, *type(self).__all_private_attrs):
            super().__setattr__(key, value)
        else:
            try:
                setattr(self.getresult(), key, value)
            except Exception as e:
                raise LazyError(f"Error setting attribute '{key}': {e}")

    def __bool__(self):
        return bool(self.getresult())
        
    def __call__(self, *args, **kwargs):
        result = self.getresult()
        try:
            return result(*args, **kwargs) if (args or kwargs) else result
        except Exception as e:
            raise LazyError(f"Error calling lazy object: {e}")

    def getresult(self) -> Any:
        get_attr = super().__getattribute__
        set_attr = super().__setattr__
        nocache = get_attr('_Lazy__nocache')
        
        try:
            if not nocache:
                return get_attr("_Lazy__result")
        except AttributeError:
            pass

        try:
            callable_ = get_attr("_Lazy__callable")
            args = get_attr("_Lazy__args")
            kwargs = get_attr("_Lazy__kwargs")
            maxsize = Lazy._max_size
            key = (callable_, args, tuple(sorted(kwargs.items())))
            cache = Lazy._global_cache
            
            if not nocache and key in cache:
                result = cache.pop(key)
                cache[key] = result
            else:
                result = callable_(*args, **kwargs)
                cache[key] = result
                while len(cache) > maxsize:
                    cache.popitem(last=False)

            set_attr("_Lazy__result", result)
            return result
        except Exception as e:
            raise LazyError(f"Failed to compute or cache the result: {e}")

    def __await__(self):
        return self.getresult().__await__()

    def __aiter__(self):
        return self.getresult().__aiter__()

    async def __anext__(self):
        return await self.getresult().__anext__()

    def __enter__(self):
        return self.getresult().__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self.getresult().__exit__(exc_type, exc_val, exc_tb)

    async def __aenter__(self):
        return await self.getresult().__aenter__()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return await self.getresult().__aexit__(exc_type, exc_val, exc_tb)


class LiveResult(Lazy):
    """
    Computes the latest result of a callable.
    """
    def __init__(self, callable_: Callable, *args, **kwargs):
        super().__init__(callable_, True, *args, **kwargs)


# Auto-forward common dunder methods
_dunder_forward = [
    "__len__", "__str__", "__repr__",
    "__bytes__", "__iter__",
    "__reversed__", "__contains__",
    "__getitem__", "__setitem__", "__delitem__",
    "__eq__", "__ne__", "__lt__", "__le__", "__gt__", "__ge__",
    "__add__", "__sub__", "__mul__", "__matmul__", "__truediv__", "__floordiv__",
    "__mod__", "__divmod__", "__pow__", "__lshift__", "__rshift__", "__and__",
    "__xor__", "__or__", "__radd__", "__rsub__", "__rmul__", "__rmatmul__", 
    "__rtruediv__", "__rfloordiv__", "__rmod__", "__rdivmod__", "__rpow__", 
    "__rlshift__", "__rrshift__", "__rand__", "__rxor__", "__ror__",
    "__index__"
]

skip_dunders = {"__repr__"}

for name in _dunder_forward:
    if name in skip_dunders:
        continue
    def make_dunder(name):
        def method(self, *args, **kwargs):
            try:
                return getattr(self.getresult(), name)(*args, **kwargs)
            except AttributeError as e:
                raise LazyError(f"Attribute '{name}' not found on the lazy result: {e}")
            except Exception as e:
                raise LazyError(f"Error in dunder '{name}': {e}")
        method.__name__ = name
        return method
    setattr(Lazy, name, make_dunder(name))
