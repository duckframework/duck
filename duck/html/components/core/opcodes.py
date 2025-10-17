"""
WebSocket Operation Codes for Virtual DOM Patch and Component Event System.

This module defines compact integer codes for efficiently encoding and decoding
DOM patch operations and component-related events transmitted over WebSockets.
It supports a virtual DOM update protocol using binary encoding (e.g., MessagePack)
for minimal overhead and high performance.
"""

import enum


class PatchCode(enum.IntEnum):
    """
    Patch operation codes used for virtual DOM updates.

    These codes define how the DOM should be modified on the client. Each opcode
    corresponds to a specific structural or content change in the DOM, and is designed
    for use with efficient binary serialization protocols.

    Format of each patch instruction:
        [opcode, node_key, payload...]
    """

    # --- Structural Operations ---

    REPLACE_NODE = 0
    """
    int: Replace the entire node. Format: [0, key, new_node_list]
    """

    REMOVE_NODE = 1
    """
    int: Remove the node. Format: [1, key]
    """

    INSERT_NODE = 2
    """
    int: Insert a new node. Format: [2, key, new_node_list]
    """

    # --- Content Update Operations ---

    ALTER_TEXT = 3
    """
    int: Change text content of a node. Format: [3, key, new_text]
    """

    # --- Attributes and Style Updates ---

    REPLACE_PROPS = 4
    """
    int: Replace all HTML attributes (props). Format: [4, key, new_props_dict]
    """

    REPLACE_STYLE = 5
    """
    int: Replace all inline styles. Format: [5, key, new_style_dict]
    """


class EventOpCode(enum.IntEnum):
    """
    Event operation codes used to coordinate DOM updates, component interactions,
    and JavaScript execution between the client and the server.

    These codes are used in higher-level instructions that may bundle patches,
    dispatch component-bound events, or evaluate JavaScript on the client.
    """

    APPLY_PATCH = 1
    """
    int: Apply one or more virtual DOM patches. Format: [1, patches_list]
    
    Each item in patches_list should be:
        [patch_opcode, component_uid, payload]
    """

    DISPATCH_COMPONENT_EVENT = 100
    """
    int: Dispatch a component-bound event from client to server.
    
    Format: [100, [root_component_uid, component_uid, event_name, event_value, is_document_event]]
    
    Where:
        root_component_uid: The unique ID for the root component.
        component_uid: Stable ID of the component (may depend on component position in children list.)
        event_name: Event name bound with `component.bind()` (e.g., "onclick").
        event_value: Associated value (e.g., input.value or button state).
        is_document_event: Whether the event is specifically tied to the `document` rather than the element.
    """

    EXECUTE_JS = 101
    """
    int: Execute a JavaScript code snippet on the client.
    
    Format: [101, [code, variable, timeout, wait_for_result, uid]]
    
    Where:
        code: JavaScript code string to execute.
        variable: Variable to retrieve post-execution.
        timeout: Max duration (in ms) to wait for completion.
        wait_for_result: Boolean indicating if client should return the result.
        uid: Unique ID for the execution.
    """

    JS_EXECUTION_RESULT = 111
    """
    int: Response from previously executed JS code.
    
    Format: [111, [result, exception, uid]]
    
    Where:
        result: Output value of the variable (if successful).
        exception: Any exception raised during client execution.
        uid: Unique ID for the execution.
    """
    
    NAVIGATE_TO = 120
    """
    int: Navigation request from client to server.
    
    Format: [120, [prev_component_uid, path, headers]]
    
    Where:
        prev_component_uid: This is the previous root component UID. The component last rendered as full webpage on client side.
        path: Full URL path matching a registered urlpattern.
        headers: The headers for the request, usually default browser headers. Referer header is needed for diffing.
    """
    
    NAVIGATION_RESULT = 121
    """
    int: Send a navigation patch from server to client.
    
    Format: [121, path, fullreload, component_uid, patches_list, is_final]
    
    Where:
        path: The requested URL path.
        fullreload: Boolean on whether to make the client do a fresh reload as it may be impossible to produce patches.
        component_uid: The UID of the next root component which represents a new page.
        patches_list: List of patches to apply. 
        is_final: Whether this is a final navigation result. Useful in when sending partial patches to the client.
    """
