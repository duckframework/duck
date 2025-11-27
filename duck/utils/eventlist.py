"""
EventList - A list subclass with event-driven callbacks on item insertion and deletion.
"""

from typing import Any, Callable, Optional


class EventList(list):
    """
    A list subclass that supports event hooks for item insertion and deletion.

    This class allows you to register callback functions that will be triggered
    before any item is inserted or deleted (including through methods like append,
    extend, pop, remove, clear, slice assignment, etc.).
    """
    __slots__ = {"_on_new_item", "_on_delete_item"}
    
    def __init__(
        self,
        initlist=None,
        on_new_item: Optional[Callable[[Any], None]] = None,
        on_delete_item: Optional[Callable[[Any], None]] = None,
    ):
        """
        Initialize the EventList.

        Args:
            initlist (iterable, optional): Initial values to populate the list.
            on_new_item (Callable, optional): Callback triggered before adding an item.
            on_delete_item (Callable, optional): Callback triggered before removing an item.
        """
        super().__init__(initlist or [])
        self._on_new_item = on_new_item
        self._on_delete_item = on_delete_item

    def on_new_item(self, item: Any):
        """
        Triggered before an item is inserted into the list.

        Args:
            item: The item that is about to be added.
        """
        if self._on_new_item:
            self._on_new_item(item)

    def on_delete_item(self, item: Any):
        """
        Triggered before an item is removed or replaced in the list.

        Args:
            item: The item that is about to be deleted.
        """
        if self._on_delete_item:
            self._on_delete_item(item)

    def insert(self, index: int, item: Any):
        """
        Insert an item at a specific index and trigger the on_new_item event.
        """
        self.on_new_item(item)
        super().insert(index, item)

    def append(self, item: Any):
        """
        Append an item to the end of the list and trigger the on_new_item event.
        """
        self.on_new_item(item)
        super().append(item)

    def extend(self, other):
        """
        Extend the list with items from another iterable, triggering events for each item.
        """
        for item in other:
            self.append(item)

    def pop(self, index: int = -1):
        """
        Remove and return item at index, triggering on_delete_item event.
        """
        item = self[index]
        self.on_delete_item(item)
        return super().pop(index)

    def remove(self, item: Any):
        """
        Remove the first occurrence of an item, triggering on_delete_item event.
        """
        self.on_delete_item(item)
        super().remove(item)

    def clear(self):
        """
        Clear the list by removing all items individually (triggering events).
        """
        items = list(self)  # Copy to avoid mutation during iteration
        for item in items:
            self.remove(item)

    def __repr__(self):
        return f"<{self.__class__.__name__} {list(self)}>"

    def __str__(self):
        return f"<{self.__class__.__name__} {list(self)}>"

    def __iadd__(self, other):
        """
        In-place addition (+=), treated as an extend operation.
        """
        self.extend(other)
        return self

    def __delitem__(self, index):
        """
        Handle deletion using `del` keyword.

        Supports both single index and slice deletion.
        """
        if isinstance(index, slice):
            for item in self[index]:
                self.on_delete_item(item)
        else:
            self.on_delete_item(self[index])
        super().__delitem__(index)

    def __setitem__(self, index, value):
        """
        Set the item at the given index or slice, triggering appropriate events.

        For single index assignment, calls on_delete_item (old) and on_new_item (new).
        For slice assignment, replaces old items individually and adds new ones.
        """
        # Single index assignment
        if isinstance(index, int):
            old_item = self[index]
            self.on_delete_item(old_item)
            self.on_new_item(item)
            super().__setitem__(index, item)
            
        # Slice replacement
        elif isinstance(index, slice):
            old_items = self[index]
            
            for index, i in enumerate(old_items):
                self.remove(i)
             
            for index, i in enumerate(item):
                self.insert(index, i)
