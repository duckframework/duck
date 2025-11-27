from duck.html.components import (
    Component,
    InnerComponent,
    ComponentError,
)
from duck.utils.eventlist import EventList


class ChildrenList(EventList):
    """
    A specialized list to manage child components of an InnerComponent.
    
    This class ensures that child components maintain correct parent-child 
    relationships by updating references whenever a child is added or removed.
    
    Inherits from:
        EventList: A custom list that provides hooks for item insertion and deletion.
    """

    def __init__(self, parent: Component):
        """
        Initializes the ChildrenList with a reference to its parent component.

        Args:
            parent (Component): The parent component to which children belong.

        Raises:
            ComponentError: If the parent is not a valid InnerComponent.
        """
        super().__init__(initlist=None)

        if not isinstance(parent, Component):
            raise ComponentError(
                f"Parent should be an instance of HtmlComponent, not {type(parent)}."
            )

        if not isinstance(parent, InnerComponent):
            raise ComponentError(
                "Parent should be an `InnerHtmlComponent` instance. "
                "The provided component does not support children."
            )

        self.parent = parent

        # Set event handlers for when a child is added or removed.
        self._on_new_item = self.on_new_child
        self._on_delete_item = self.on_delete_child

    def on_new_child(self, child: Component):
        """
        Attach a new child to this component, ensuring correct parent/root.
        """
        
        if not isinstance(child, Component):
            raise ComponentError(
                f"Child {child} must be an instance of HtmlComponent, not {type(child)}."
            )
    
        if child.parent or child.root:
            raise ComponentError(
                f"Child component {child} is already added to a parent component. "
                "Please remove it first before adding it to a new parent."
            )
    
        # Reset UID so root can assign it later
        child.uid = None
        
        # Set the current component with this children list
        current = self.parent
        
        # Set parent and compute new root
        child.parent = current
        new_root = current.root if current.root else current
        
        # Update root for child + fix subtree if stale
        if child.root is not new_root:
            child.root = new_root
            if isinstance(child, InnerComponent) and child.children:
                self._update_root_iterative(child, new_root)
                
        # Call on_parent event.
        child.on_parent(current)
        
    def _update_root_iterative(self, node: Component, new_root: Component):
        """
        Iteratively update roots of a subtree.
        Uses a stack (DFS) to avoid recursion overhead.
        """
        stack = [node]
    
        while stack:
            current = stack.pop()
    
            for subchild in getattr(current, "children", []):
                if subchild.root is not new_root:
                    subchild.root = new_root
                    if isinstance(subchild, InnerComponent) and subchild.children:
                        stack.append(subchild)
                
    def on_delete_child(self, child: Component):
        """
        Handler called when a child is removed or replaced from the list.

        Clears the parent and root references of the child component.

        Args:
            child (Component): The child component being removed.

        Raises:
            ComponentError: If the child is not a valid component or not in the list.
        """
        if not isinstance(child, Component):
            raise ComponentError(
                f"Child component {child} must be an instance of HtmlComponent, not {type(child)}."
            )

        if child not in self:
            raise ComponentError(
                f"Child component {repr(child)} not found in children list."
            )

        # Detach the child from its parent and root context.
        child.parent = None
        child.root = None
        child.uid = None # Unset child UID
