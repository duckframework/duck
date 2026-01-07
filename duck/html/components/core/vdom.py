"""
Lively Component System Virtual DOM.
"""

from typing import (
    Optional,
    Dict,
    List,
    Union,
    Any,
    Callable,
)
from duck.contrib.sync import iscoroutinefunction
from duck.html.components.core.opcodes import PatchCode


class VDomNode:
    """
    Virtual DOM node optimized for fast diffing and minimal patch generation.

    Attributes:
        tag (str): HTML tag name (e.g., 'div', 'span', 'button').
        key (Optional[Union[str, int]]): Unique identifier for the node (used in keyed diffing).
        props (Dict[str, str]): Dictionary of HTML attributes (e.g., {'class': 'btn'}).
        style (Dict[str, str]): Dictionary of CSS inline styles (e.g., {'color': 'red'}).
        children (List[VDomNode]): List of child VDomNode instances.
        text (Optional[str]): Inner text content of the element.
    """

    __slots__ = ("tag", "key", "props", "style", "children", "text", "component")

    def __init__(
        self,
        tag: str,
        key: Optional[Union[str, int]] = None,
        props: Optional[Dict[str, str]] = None,
        style: Optional[Dict[str, str]] = None,
        children: Optional[List["VDomNode"]] = None,
        text: Optional[str] = None,
        component = None,
    ):
        """
        Initialize a virtual DOM node.

        Args:
            tag (str): The HTML tag of the node (e.g., 'div').
            key (Optional[Union[str, int]]): Optional unique key for diffing.
            props (Optional[Dict[str, str]]): HTML attributes for the node.
            style (Optional[Dict[str, str]]): CSS inline styles for the node.
            children (Optional[List[VDomNode]]): List of child virtual DOM nodes.
            text (Optional[str]): Text content of the node, if any.
            component (Component): The target component.
        """
        self.tag = tag
        self.key = key
        self.props = props or {}
        self.style = style or {}
        self.children = children or []
        self.text = text
        self.component = component
        
        # Check if component is loaded
        component.raise_if_not_loaded(
            f"Component {component} is not loaded. "
            f"This might mean that this is a lazy component."
        )
        
    def to_list(self) -> list:
        """
        Convert the node into a compact list format for efficient serialization.

        Returns:
            list: Serialized representation of the node in the form:
                [tag, key, props, style, text, [children...]]
        """
        return [
            self.tag,
            self.key,
            self.props,
            self.style,
            self.text,
            [child.to_list() for child in self.children],
        ]

    def on_insert(self, node: "VDomNode", parent_node: "VDomNode", index: int):
        """
        Event called when node is to be inserted.
        """
        pass
        
    def on_remove(self, node: "VDomNode"):
        """
        Event called when node is to be removed.
        """
        pass
        
    @staticmethod
    def diff(old: "VDomNode", new: "VDomNode") -> List[list]:
        """
        Compute a minimal set of patches to transform one virtual DOM tree into another.
    
        This method performs key-based diffing on children and emits compact patch lists
        using PatchCode. Each patch is a list optimized for fast encoding with MessagePack.
    
        Args:
            old (VDomNode): The previous virtual DOM node.
            new (VDomNode): The updated virtual DOM node.
    
        Returns:
            List[list]: A list of compact patch operations (lists) in the format:
                [opcode, key, ...data]
        """
        patches = []
        
        # Replace node if tags differ
        if old.tag != new.tag:
            patches.append([PatchCode.REPLACE_NODE, old.key, new.to_list()])
            return patches
    
        # Text/html update
        if old.text != new.text:
            patches.append([PatchCode.ALTER_TEXT, old.key, new.text])
            
        # Props update
        if old.props != new.props:
            patches.append([PatchCode.REPLACE_PROPS, old.key, new.props])
            
        # Style update
        if old.style != new.style:
            patches.append([PatchCode.REPLACE_STYLE, old.key, new.style])
        
        # Map old and new children by key
        old_children_map = {child.key: child for child in old.children if child.key is not None}
        new_children_map = {child.key: child for child in new.children if child.key is not None}
    
        # Remove nodes that no longer exist
        for key in old_children_map:
            if key not in new_children_map:
                patches.append([PatchCode.REMOVE_NODE, key])
                
        # Insert new nodes and diff existing nodes
        for idx, new_child in enumerate(new.children):
            old_child = old_children_map.get(new_child.key)
            if old_child is None:
                # Node is new -> insert
                patches.append([PatchCode.INSERT_NODE, old.key, [idx, new_child.to_list()]])
            else:
                # Node exists -> diff recursively
                patches.extend(VDomNode.diff(old_child, new_child))
        return patches

    @staticmethod
    async def diff_and_act(action: Callable, old: "VDomNode", new: "VDomNode") -> None:
        """
        Compute a minimal set of patches to transform one virtual DOM tree into another.
    
        This method performs key-based diffing on children and emits compact patch lists
        using PatchCode. Each patch is a list optimized for fast encoding with MessagePack.
        
        This method diffs and perform an action on every patch rather than returning a list of all 
        computed patches.
        
        Args:
            action (Callable): A synchronous/asynchronous callable to perform on every patch.
                The first argument to this must be the patch.
            old (VDomNode): The previous virtual DOM node.
            new (VDomNode): The updated virtual DOM node.
    
        Returns:
            None: Nothing to return.
        """
        is_async_action = iscoroutinefunction(action)
        
        # Replace node if tags differ
        if old.tag != new.tag:
            patch = [PatchCode.REPLACE_NODE, old.key, new.to_list()]
            if is_async_action:
                await action(patch)
            else:
                action(patch)
            return
            
        # Text update
        if old.text != new.text:
            patch = [PatchCode.ALTER_TEXT, old.key, new.text]
            if is_async_action:
                await action(patch)
            else:
                action(patch)
                
        # Props update
        if old.props != new.props:
            patch = [PatchCode.REPLACE_PROPS, old.key, new.props]
            if is_async_action:
                await action(patch)
            else:
                action(patch)
                
        # Style update
        if old.style != new.style:
            patch = [PatchCode.REPLACE_STYLE, old.key, new.style]
            if is_async_action:
                await action(patch)
            else:
                action(patch)
                
        # Map old and new children by key
        old_children_map = {child.key: child for child in old.children if child.key is not None}
        new_children_map = {child.key: child for child in new.children if child.key is not None}
    
        # Remove nodes that no longer exist
        for key in old_children_map:
            if key not in new_children_map:
                patch = [PatchCode.REMOVE_NODE, key]
                if is_async_action:
                    await action(patch)
                else:
                    action(patch)
                
        # Insert new nodes and diff existing nodes
        for idx, new_child in enumerate(new.children):
            old_child = old_children_map.get(new_child.key)
            if old_child is None:
                # Node is new -> insert
                patch = [PatchCode.INSERT_NODE, old.key, [idx, new_child.to_list()]]
                if is_async_action:
                    await action(patch)
                else:
                    action(patch)
            else:
                # Node exists -> diff recursively
                await VDomNode.diff_and_act(action, old_child, new_child)
    
    def __repr__(self):
        return f"<{self.__class__.__name__} key='{self.key}', children={len(self.children)}>"
        
    __str__ = __repr__


class LiveVDomNode(VDomNode):
    """
    Custom VDomNode which maintains close relationship with a component.
    """
    __slots__ = ("component")
    
    def __init__(self, component):
        """
        Initialize LiveVDomNode.
        
        Args:
            component: The associated component.
        """
        self.component = component
        
        # Check if component is loaded
        component.raise_if_not_loaded(
            f"Component {component} is not loaded. "
            f"This might mean that this is a lazy component."
        )
     
    @property
    def tag(self):
        return self.component.element or self.component.get_element()
     
    @property
    def key(self):
        return self.component.uid
     
    @property
    def props(self):
        return self.component.props
     
    @property
    def style(self):
        return self.component.style
     
    @property
    def children(self):
        return [LiveVDomNode(child) for child in getattr(self.component, "children", [])]
     
    @property
    def text(self):
        from duck.utils.lazy import Lazy
        return self.component.inner_html if not isinstance(self.component.inner_html, Lazy) else str(self.component.inner_html)
