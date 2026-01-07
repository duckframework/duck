"""
Module containing dictionaries for containing HTML props/style.
"""
from typing import (
    Any,
    Optional,
    Tuple,
    Dict,
    Callable,
)


class PropertyStore(dict):
    """
    A dictionary subclass to store properties for HTML components, with certain restrictions.

    Keys and values must both be strings. Certain methods (pop, popitem, update, setdefault, etc.)
    are overridden to ensure they utilize the custom __setitem__ and __delitem__ logic,
    including event hooks for set and delete operations.  
    
    **Args:**
    - `*args`: Arguments to initialize the dictionary.
    - `**kwargs`: Keyword arguments to initialize the dictionary.
    """
    __slots__ = ("__version", "_on_set_item_func", "_on_delete_item_func")
    
    def __init__(
        self,
        initdict: Optional[Dict[Any, Any]] = None,
        on_set_item: Optional[Callable] = None,
        on_delete_item: Optional[Callable] = None,
    ) -> None:
        # Super initialization
        super().__init__(initdict or {})
        
        # Assign event callbacks and other attributes
        self._on_set_item_func = on_set_item
        self._on_delete_item_func = on_delete_item
        self.__version = 0
        
    @property
    def _version(self) -> int:
        return self.__version
        
    def __setitem__(self, key: str, value: str, call_on_set_item_handler: bool = True) -> None:
        """
        Sets the value for the given key if the key is allowed.

        Args:
            key (str): The key to set the value for. Must be a string.
            value (str): The value to set. Must be a string.
            call_on_set_item_handler (bool): Whether to call `on_set_item` after the actual `__setitem__`.

        Raises:
            AssertionError: If the key or value is not a string.
        """
        assert isinstance(key, str), f"Keys for `PropertyStore` must be strings not {type(key)}"
        assert isinstance(value, str), f"Values for `PropertyStore` must be strings not {type(value)}"
        
        k = key.strip().lower()
        
        # Avoid using setitem if value is the same
        try:
            old = self[k]
            if old is value:
                return
        except KeyError:
            pass
            
        # Set key-value pair
        super().__setitem__(k, value)
        
        if call_on_set_item_handler:
            self._on_set_item(k, value)

    def __delitem__(self, key: str, call_on_delete_item_handler: bool = True) -> None:
        """
        Deletes a key from the property store.

        Args:
            key (str): The key to delete. Must be a string.
            call_on_delete_item_handler (bool): Whether to call `on_delete_item` after the actual `__delitem__`.
        """
        k = key.strip().lower()
        super().__delitem__(k)
        
        if call_on_delete_item_handler:
            self._on_delete_item(k)

    def __repr__(self) -> str:
        """
        Returns a string representation of PropertyStore.

        Returns:
            str: String representation of the PropertyStore.
        """
        return f"<{self.__class__.__name__} {dict(self).__repr__()}>"

    def update(self, data: Any = None, call_on_set_item_handler: bool = True, *args, **kwargs) -> None:
        """
        Updates the PropertyStore with the key/value pairs from data, ensuring setitem logic.

        Args:
            data (Any): Mapping or iterable to update from.
            call_on_set_item_handler (bool): Whether to call `on_set_item` for each item.
            *args, **kwargs: Additional data.
        """
        if data is not None:
            if hasattr(data, 'items'):
                items = data.items()
            else:
                items = data
            for key, value in items:
                self.__setitem__(key, value, call_on_set_item_handler)
        for key, value in dict(*args, **kwargs).items():
            self.__setitem__(key, value, call_on_set_item_handler)

    def setdefault(self, key: str, default: Optional[str] = None, call_on_set_item_handler: bool = True) -> str:
        """
        Inserts key with a value of default if key is not in the dictionary.

        Args:
            key (str): The key to check.
            default (str, optional): The default value to set if key is missing.
            call_on_set_item_handler (bool): Whether to call `on_set_item` if setting.

        Returns:
            str: The value for the key.
        """
        k = key.strip().lower()
        if k not in self:
            self.__setitem__(k, default if default is not None else '', call_on_set_item_handler)
            return default if default is not None else ''
        return self[k]

    def pop(self, key: str, default: Any = None) -> Any:
        """
        Removes the specified key and returns its value.
        If key is not found, default is returned if provided, otherwise KeyError is raised.

        Args:
            key (str): The key to remove.
            default (Any, optional): The value to return if key is not found.

        Returns:
            Any: The value associated with the key, or default.

        Raises:
            KeyError: If key is not found and default is not provided.
        """
        k = key.strip().lower()
        if k in self:
            value = self[k]
            self.__delitem__(k)
            return value
        elif default is not None:
            return default
        else:
            raise KeyError(k)

    def popitem(self) -> Tuple[str, str]:
        """
        Removes and returns a (key, value) pair from the dictionary.
        Pairs are returned in LIFO order.

        Returns:
            Tuple[str, str]: The removed (key, value) pair.

        Raises:
            KeyError: If the dictionary is empty.
        """
        try:
            k, v = next(reversed(self.items()))
        except StopIteration:
            raise KeyError(f"{self.__class__.__name__} is empty")
        self.__delitem__(k)
        return k, v

    def setdefaults(self, data: Dict[str, str]) -> None:
        """
        Calls setdefault on multiple items.

        Args:
            data (Dict[str, str]): The key-value pairs to set as defaults.
        """
        for key, value in data.items():
            self.setdefault(key, value)
            
    def on_set_item(self, key: str, value: Any) -> None:
        """
        Called after `__setitem__`.

        Args:
            key (str): The key set.
            value (Any): The value set.
        """
        if self._on_set_item_func:
            self._on_set_item_func(key, value)
        
    def on_delete_item(self, key: str) -> None:
        """
        Called after `__delitem__`.

        Args:
            key (str): The key deleted.
        """
        if self._on_delete_item_func:
            self._on_delete_item_func(key)
        
    def _on_set_item(self, k, v):
        self.__version += 1
        self.on_set_item(k, v)
    
    def _on_delete_item(self, k):
        self.__version += 1
        self.on_delete_item(k)


class StyleStore(PropertyStore):
    """
    PropertyStore dictionary for component styling.
    """
    pass
