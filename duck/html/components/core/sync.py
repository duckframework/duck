"""
Sync-now module for Lively.

Provides sync_now(), a way for an event handler to push an immediate,
diffed update for a single descendant component mid-handler — without
waiting for the dispatch loop's final diff, and without re-rendering or
re-diffing the ancestor (e.g. page) that component lives under.

This matters when a handler needs the client to reflect an intermediate
state change before later restoring that state for the final VDOM diff
(which would otherwise see old == new and skip sending a patch). Rather
than force-pushing an update unconditionally, sync_now() diffs the
component against its own last checkpoint and sends only real changes,
scoped to that component's subtree.
"""

from typing import Optional
from dataclasses import dataclass, field
from contextvars import ContextVar
from contextlib import contextmanager

from duck.utils.lazy import Lazy
from duck.html.components.core.vdom import VDomNode
from duck.html.components.core.exceptions import SyncNowError


@dataclass
class Entry:
    """
    Registry entry for a single indexed VDomNode.

    Attributes:
        node (VDomNode): The indexed node's last known snapshot.
        parent (Optional[VDomNode]): The node's parent in the vdom tree,
            or None if this node is itself a root (an update_target).
        index (Optional[int]): The node's position in parent.children,
            or None if this node is a root.
    """
    node: VDomNode
    parent: Optional[VDomNode]
    index: Optional[int]


@dataclass
class SyncNowState:
    """
    Lazily-built sync_now state for a single event dispatch.

    Attributes:
        old_vdoms (dict):
            Root checkpoint vdoms keyed by update_target
            component, as built by the dispatch loop before the handler ran.
        
        registry (Lazy):
            Flattened uid -> Entry index. The flatten walk
            only runs the first time this is accessed, so handlers that
            never call sync_now() pay zero indexing cost.
    """
    old_vdoms: dict
    registry: Lazy = field(init=False)

    def __post_init__(self):
        self.registry = Lazy(lambda: self._build_registry())

    def _build_registry(self) -> dict:
        """
        Flatten every update_target's checkpoint vdom into one registry.
        """
        registry: dict = {}
        
        for old_vdom in self.old_vdoms.values():
            flatten_vdom(old_vdom, registry=registry)
        
        # Return the final registry
        return registry


_sync_now_state: ContextVar[Optional[SyncNowState]] = ContextVar("sync_now_state", default=None)


@contextmanager
def track_sync_now_checkpoints(old_vdoms: dict):
    """
    Expose the dispatch loop's pre-handler vdom snapshots to sync_now()
    calls made from inside the event handler.

    The registry itself is a Lazy — flattening only happens on first
    access from within sync_now(), not here.
    """
    state = SyncNowState(old_vdoms=old_vdoms)
    token = _sync_now_state.set(state)

    try:
        yield state
    finally:
        _sync_now_state.reset(token)


def flatten_vdom(
    vdom: VDomNode,
    parent: Optional[VDomNode] = None,
    index: Optional[int] = None,
    registry: Optional[dict] = None,
) -> dict:
    """
    Recursively index a VDomNode tree by key (component uid).

    Records each node's parent VDomNode and its position in the parent's
    children list, so a descendant can be diffed and swapped back in
    without rebuilding the tree it belongs to.

    Args:
        vdom (VDomNode): The vdom node to index, along with its subtree.
        parent (Optional[VDomNode]): The node's parent, or None if root.
        index (Optional[int]): The node's position in parent.children.
        registry (Optional[dict]): Registry to populate; created if None.

    Returns:
        dict: Mapping of component uid to Entry.
    """
    if registry is None:
        registry = {}

    # Update entry in registry
    registry[vdom.key] = Entry(node=vdom, parent=parent, index=index)

    for i, child in enumerate(vdom.children):
        flatten_vdom(child, parent=vdom, index=i, registry=registry)

    return registry


async def sync_now(ws, component: "HtmlComponent") -> None:
    """
    Diff a component against its last checkpoint and push the difference
    immediately. Scoped to component's own subtree only.

    Args:
        ws: The active lively websocket connection.
        component (HtmlComponent): The descendant component to sync.

    Raises:
        ForceUpdateError: If component isn't a descendant of any
            update_target for this event, or if called outside an
            active event handler.
    """
    state = _sync_now_state.get()

    if state is None:
        raise SyncNowError(
            "sync_now() must be called from within an active event handler."
        )

    # Initialize registry and entry
    registry: Lazy = state.registry
    entry: Optional[Entry] = registry.get(component.uid)

    if entry is None:
        raise SyncNowError(
            "sync_now() requires the component to be a descendant of one "
            "of the event's update_targets."
        )

    # Initialize old vdom plus new vdom.
    old_vdom = entry.node
    new_vdom = component.to_vdom()

    async def on_patch(patch):
        """
        Send a patch immediately to the client.
        """
        if patch:
            await ws.send_patches([patch])

    # Do diffing right away
    await component.vdom_diff_and_act(on_patch, old_vdom, new_vdom)
    
    # Update the new vdom for component parent.
    if entry.parent is not None:
        entry.parent.children[entry.index] = new_vdom
    else:
        state.old_vdoms[component] = new_vdom

    # Flatten the new vdom
    flatten_vdom(new_vdom, parent=entry.parent, index=entry.index, registry=registry)
