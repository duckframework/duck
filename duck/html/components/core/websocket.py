"""
Lively Component System WebSocket implementation.
"""
import asyncio
import secrets
import msgpack

from typing import (
    List,
    Dict,
    Union,
    Any,
    Tuple,
    Optional,
    Iterable,
)

from duck.settings import SETTINGS
from duck.logging import logger
from duck.http.request import HttpRequest
from duck.http.response import HttpResponse
from duck.http.core.handler import ResponseHandler
from duck.utils.asyncio import create_task
from duck.contrib.sync import convert_to_async_if_needed
from duck.contrib.websockets import (
    WebSocketView,
    OpCode,
    CloseCode,
)
from duck.html.components.core.force_update import (
    ForceUpdate,
    ForceUpdateError,
    check_force_updates,
)
from duck.html.components.core.opcodes import EventOpCode, PatchCode
from duck.html.components.core.exceptions import (
    JavascriptExecutionError,
    JavascriptExecutionTimedOut,
)


def generate_uid(length: int = 6) -> str:
    """
    Generate a short unique ID for tracking JS execution results.
    """
    return secrets.token_urlsafe(length)[:length]


class LivelyWebSocketView(WebSocketView):
    """
    WebSocket view for handling communication between server-side HTML components
    and client-side via virtual DOM patching and JavaScript execution.
    """
    __slots__ = ("request", "execution_futures", "event_handler")
    
    def __init__(self, request, **kwargs):
        super().__init__(request, **kwargs)
        self.execution_futures: Dict[str, asyncio.Future] = {}
        self.event_handler = EventHandler(self)
        
    @staticmethod
    def serialize_data(data: Any) -> bytes:
        """
        Serializes data using MessagePack.
        """
        return msgpack.packb(data, use_bin_type=True)

    @staticmethod
    def unserialize_data(data: bytes) -> Any:
        """
        Deserializes MessagePack-encoded binary data.
        """
        return msgpack.unpackb(data, raw=False)

    async def send_data(self, data: Any):
        """
        Sends serialized data over the WebSocket.
        """
        data = self.serialize_data(data)
        await self.send_binary(data)
        
    async def send_patches(self, patches: List):
        """
        Sends virtual DOM patch instructions to the client.

        Args:
            patches (List): A list of patch operations.
        """
        payload = [EventOpCode.APPLY_PATCH, patches]
        await self.send_data(payload)

    async def execute_js(
        self,
        code: str,
        timeout: Union[int, float] = None,
        wait_for_result: bool = False,
    ) -> Optional[Any]:
        """
        Sends JavaScript code to the client for execution over WebSocket, optionally awaiting the result.
    
        Args:
            code (str): The JavaScript code to execute on the client.
            timeout (Union[int, float], optional): Maximum time (in seconds) to wait for a result.
            wait_for_result (bool): Whether to wait for the feedback that the JS code has been executed.
            
        Returns:
            Optional[Any]: The result returned by the client if `wait_for_result` is True, otherwise None.
    
        Raises:
            JavascriptExecutionError: If the future is cancelled, usually due to WebSocket disconnection or the client raised an exception.
            JavascriptExecutionTimedOut: If the result was not received within the specified timeout.
            ValueError: If user specified a timeout yet wait_for_result is set to False.
        """
        if not wait_for_result and timeout:
            raise ValueError("You specified a timeout yet wait_for_result is False. Set wait_for_result to True to wait for the specified timeout.") 
            
        # Generate random UID
        uid = generate_uid()
        
        payload = [
            EventOpCode.EXECUTE_JS,
            code,
            None,
            timeout,
            wait_for_result,
            uid
        ]
        
        if not wait_for_result:
            await self.send_data(payload)
            return None
    
        future = asyncio.get_event_loop().create_future()
        self.execution_futures[uid] = future
        
        # Send payload to the websocket
        await self.send_data(payload)
    
        try:
            # Wait for JS execution
            return await asyncio.wait_for(future, timeout)
        
        except asyncio.CancelledError:
            raise JavascriptExecutionError("Javascript execution failed because websocket has been disconnected")
        
        except asyncio.TimeoutError:
            raise JavascriptExecutionTimedOut(f"JavaScript execution timed out for uid '{uid}'.")
        
        finally:
            self.execution_futures.pop(uid, None)
            
    async def get_js_result(
        self,
        code: str,
        variable: str,
        timeout: Union[int, float, None] = None,
    ) -> Any:
        """
        Executes JavaScript on the client and retrieves the value of a specific variable.
    
        This is useful when the server needs to fetch a value or result produced by JS code
        after execution.
    
        Args:
            code (str): JavaScript code to execute.
            variable (str): The name of the variable whose value should be returned after execution.
            timeout (Union[int, float], optional): Maximum time (in seconds) to wait for the variable's value.
            
        Returns:
            Any: The value of the specified variable returned from the client.
    
        Raises:
            JavascriptExecutionError: If the future is cancelled, typically due to WebSocket disconnection or the client raised an exception.
            JavascriptExecutionTimedOut: If the result is not received within the specified timeout.
        """
        # Generate random UID
        uid = generate_uid()
        
        payload = [
            EventOpCode.EXECUTE_JS,
            code,
            variable,
            timeout, 
            True,
            uid,
        ]
        
        future = asyncio.get_event_loop().create_future()
        self.execution_futures[uid] = future
        
        # Send payload to the websocket.
        await self.send_data(payload)
    
        try:
            # Wait for JS execution result.
            return await asyncio.wait_for(future, timeout)
        
        except asyncio.CancelledError:
            raise JavascriptExecutionError("Javascript execution failed because websocket has been disconnected")
        
        except asyncio.TimeoutError:
            raise JavascriptExecutionTimedOut(f"Timed out waiting for JS result for uid '{uid}'.")
        
        finally:
            self.execution_futures.pop(uid, None)
            
    async def on_open(self):
        """
        On open event.
        """
        pass
        
    async def on_close(self, frame):
        """
        On close event.
        """
        await super().on_close(frame)
        
        for future in self.execution_futures.values():
            if not future.done():
                future.cancel()
                
    async def on_receive(self, data: bytes, opcode: int):
        """
        Handles incoming WebSocket data.

        Args:
            data (bytes): Message data.
            opcode (int): WebSocket frame opcode.
        """
        if opcode != OpCode.BINARY:
            await self.send_close(CloseCode.INVALID_DATA, reason="Expecting MessagePack binary data.")
            return # Invalid data type.

        try:
            data = self.unserialize_data(data)
        except Exception as e:
            await self.send_close(CloseCode.INVALID_DATA, reason="Failed to decode MessagePack data.")
            return # Invalid data received
            
        if not data or not isinstance(data, list):
            await self.send_close(CloseCode.INVALID_DATA, reason="Invalid message format.")
            return # Unrecognized data received.
        
        try:
            event_opcode = data[0] # Get event opcode
            await self.event_handler.dispatch(event_opcode, data[1:])
        except (IndexError, Exception) as e:
            if not isinstance(e, (asyncio.CancelledError)):
                if SETTINGS['DEBUG']:
                    logger.log("Error whilst handling lively operation for ws client: ", level=logger.WARNING)
                    logger.log_exception(e)

            
class EventHandler:
    """
    Event handler for incoming WebSocket messages.
    """
    __slots__ = ("ws_view", "event_map")
    
    def __init__(self, ws_view: LivelyWebSocketView):
       self.ws_view = ws_view
       self.event_map = {
           EventOpCode.DISPATCH_COMPONENT_EVENT: self.dispatch_component_event,
           EventOpCode.JS_EXECUTION_RESULT: self.handle_js_execution_result,
           EventOpCode.NAVIGATE_TO: self.handle_navigation,
       }
    
    async def dispatch(self, opcode: EventOpCode, data: List[Any]):
        """
        Handle incoming WebSocket events.
        """
        try:
            handler = self.event_map.get(opcode, None)
            if not handler:
                await self.send_close(CloseCode.INVALID_DATA, reason="Unknown event opcode.")
            else:
                await handler(data)
        except Exception as e:
            logger.log_exception(e)
            if not isinstance(e, asyncio.CancelledError):
                if SETTINGS['DEBUG']:
                    logger.log("Error whilst handling lively operation for ws client: ", level=logger.WARNING)
                    logger.log_exception(e)
                 
    async def dispatch_component_event(self, data: List[Any]):
        """
        Dispatch a component event e.g. Button click, then send patches to client on changes the button click event made
        on the component tree.
        """
        from duck.html.components.core.system import LivelyComponentSystem
        from duck.html.components.page import Page
        
        root_uid, uid, event_name, value, is_document_event = data
            
        # Retrieve the component and then dispatch the event.
        component = resolved_component = LivelyComponentSystem.get_from_registry(root_uid, uid)
        
        if not component and SETTINGS['DEBUG']:
            msg = (
                f"Component with UID `{uid}` at root UID `{root_uid}` requested by WS client not found."
            )
            if is_document_event:
                msg += (
                    " This appears to be a document-level event. "
                    "Ensure you have bound document events only on Page components."
                )
            else:
                msg += (
                    " This may indicate an unbound or missing component."
                )
            
            # Log some blank line.
            logger.log(msg + "\n", level=logger.WARNING)
            
            # Send a response that this component is not found
            must_reload = bool(SETTINGS['RELOAD_ON_UNKNOWN_COMPONENTS'])
            await self.ws_view.send_data([EventOpCode.COMPONENT_UNKNOWN, [uid, must_reload]])
            return
        
        if is_document_event and not isinstance(component, Page):
            if SETTINGS['DEBUG']:
                logger.log(
                    f"Component of type `{type(component).__name__}` with UID `{uid}` "
                    "received a document-specific event, but it is not an instance of Page.\n"
                    "Document events should only be bound on Page components to avoid unexpected behavior.",
                    level=logger.WARNING
                )
                return
        
        # Don't repeat calling DOMContentLoaded if called, must only be called once
        # Useful on back navigation where a previous component can be revisited, so if DOMContentLoaded is already executed,
        # then there is no need to call it again
        if is_document_event and event_name == "DOMContentLoaded" and getattr(component, "_domcontentloaded_event_called", False):
            return

        # Execute event and send patches/updates
        event_handler, update_targets, update_self = component.get_event_info(event_name) if not is_document_event else component.get_document_event_info(event_name)
        update_targets = set(update_targets or [])
            
        if update_self:
            update_targets.add(component)
            
        old_vdoms = {c: c.to_vdom() for c in update_targets} # Create targets current VDOM's
        event_handler_return_value = None # Return value for the event handler
        force_updates_patchlist = [] # List of force updates patches already sent to client.
        
        # Execute event handler
        # Convert handler to async (if handler is synchronous) in case it is doing long tasks to avoid blocking event loop
        event_handler_coro = convert_to_async_if_needed(event_handler)(component, event_name, value, self.ws_view)
        event_handler_return_value = await event_handler_coro
        
        async def on_force_update_patch(patch):
            """
            Action called when new patch found as a result of a force update.
            """
            # Initialize force updates patchlist
            nonlocal force_updates_patchlist
            
            if patch:
                if patch in force_updates_patchlist:
                    # Patch was already sent as a force update before.
                    return
                
                # Finally send patches
                patches = [patch]
                await self.ws_view.send_patches(patches)
                
                # Add force update patch to the list
                force_updates_patchlist.append(patch)
                
                # Flag that a 'prop' update on the component itself happened
                if patch[0] == PatchCode.REPLACE_PROPS and patch[1] == resolved_component.uid:
                    nonlocal resolved_component_props_patch_sent
                    resolved_component_props_patch_sent = True
                    
        async def on_patch(patch):
            """
            Action called when new patch is found.
            """
            # Initialize force updates patch list
            nonlocal force_updates_patchlist
            
            if patch:
                if patch in force_updates_patchlist:
                    # Patch was already sent as a force update.
                    return
                
                # Send patches
                patches = [patch]
                await self.ws_view.send_patches(patches)
                
                # Flag that a 'prop' update on the component itself happened
                if patch[0] == PatchCode.REPLACE_PROPS and patch[1] == resolved_component.uid:
                    nonlocal resolved_component_props_patch_sent
                    resolved_component_props_patch_sent = True
                    
        # Update force updates
        if event_handler_return_value:
            if not isinstance(event_handler_return_value, Iterable):
                if not isinstance(event_handler_return_value, ForceUpdate):
                    raise ForceUpdateError(f"Return value for the event handler {event_handler} must be an instance of `ForceUpdate` or a list of ForceUpdate instances not {type(event_handler_return_value)}")
                # Send force update patch
                force_update = event_handler_return_value
                await force_update.generate_patch_and_act(action=on_force_update_patch)
            else:
                # Check if the list of updates only include `ForceUpdate` instances else raise an error.
                check_force_updates(event_handler_return_value)
                
                # Send force updates first but avoid resending same patches on DOM patch if an identical patch already sent.
                for force_update in event_handler_return_value:
                    await force_update.generate_patch_and_act(action=on_force_update_patch)
                     
        # This is the flag on whether the resolved component was be diffed somehow.
        # This value will be used to track event bindings.
        # The trick of this is that there will be no need for parsing the resolved component itself
        # to update_targets for changes to event bindings so that they will be updated on client side.
        resolved_component_props_patch_sent = False # will be set in on_patch or on_force_update_patch
        
        for comp in update_targets:
            old_vdom = old_vdoms[comp]
            new_vdom = comp.to_vdom()
            await comp.vdom_diff_and_act(on_patch, old_vdom, new_vdom)

        # Flag that DOMContentLoaded was executed so as to avoid repeated loads if page is revisited esp in backward navigation
        if is_document_event and event_name == "DOMContentLoaded":
            component._domcontentloaded_event_called = True

        # If REPLACE_PROPS patch was sent for the current component, reset _event_bindings_changed
        if resolved_component_props_patch_sent:
            # Props patches are definately sent by this time if there were changes to event bindings.
            resolved_component._event_bindings_changed = False
            return
            
        if resolved_component._event_bindings_changed:
            # Manually create patch to avoid creating patches other than props patches.
            patch = [
                PatchCode.REPLACE_PROPS,
                resolved_component.uid,
                resolved_component.props,
            ]
            
            # Send patches.
            await self.ws_view.send_patches([patch])
                       
            # Props/events now synced with client, reset the event bindings changed flag.
            resolved_component._event_bindings_changed = False
            
    async def handle_js_execution_result(self, data: List[Any]):
        """
        Process a JavaScript execution result.
        """
        # Send Format: [101, [script_type, code, variable, timeout, wait_for_result, uid]]
        # Recv Format: [111, [result, exception, uid]]
        result, exception, uid = data
        future = self.ws_view.execution_futures.pop(uid, None)
        
        if future and not future.done():
            if exception:
                future.set_exception(JavascriptExecutionError(str(exception)))
            else:
                future.set_result(result)
                  
    async def handle_navigation(self, data: List[Any]):
        """
        Handle a navigation request from the client.
        """
        from duck.settings.loaded import ASGI
        from duck.http.response import ComponentResponse
        from duck.html.components.core.system import LivelyComponentSystem
        
        # Recv Format [120, [prev_root_component_uid, next_component_uid, path, headers]]
        # Send Format: [121, path, fullreload, component_uid, patches_list]
        fullpath = None
        total_patches = 0
        
        async def on_new_patch(patch):
            """
            Action called when new patch is generated/found.
            """
            nonlocal fullpath
            nonlocal next_component
            nonlocal total_patches
            
            if patch:
                patches = [patch]
                is_final = False # Whether this is the final patch.
                payload = [
                    EventOpCode.NAVIGATION_RESULT,
                    fullpath,
                    False, # fullreload
                    next_component.uid, # component uid
                    patches, # patches list.
                    is_final, # patches are not final yet, this must be False.
                ]
                await self.ws_view.send_data(payload)
                total_patches += 1
                
        # Try producing minimal patches for the new page.
        try:
            prev_component_uid, next_component_uid, fullpath, headers = data
            root_component_uid = prev_component_uid # Same as prev_component uid
            
            if prev_component_uid and fullpath and headers:
                # Fetch previous root component.
                prev_component = LivelyComponentSystem.get_from_registry(
                    root_component_uid,
                    prev_component_uid,
                )
                
                # Try getting the next component if available
                next_component = None
                if next_component_uid:
                    next_component = LivelyComponentSystem.get_from_registry(
                        next_component_uid,
                        next_component_uid,
                    )
                    
                if prev_component:
                    if not next_component:
                        # This is the last rendered component which was used to fill up the client whole page., usually the Page component.
                        topheader = f"GET {fullpath} HTTP/1.1"
                        request = HttpRequest(
                            client_socket=self.ws_view.request.client_socket,
                            client_address=self.ws_view.request.client_address
                        )
                        request.parse_request(topheader, headers, content=b'')
                        
                        # Reuse CSP nonce from last session to avoid unmatching nonces on patching
                        first_request = self.ws_view.request
                        first_nonce = first_request.META.get("DUCK_CSP_NONCE")
                        
                        if first_nonce:
                            # Set the nonce from the first request.
                            # The below code will make function `csp_nonce` return the first_csp_nonce
                            request.META["DUCK_CSP_NONCE"] = first_csp_nonce
                            
                        # Get the new response
                        response = await ASGI.get_response(request)
                    
                        if isinstance(response, ComponentResponse):
                            # This is easy to diff
                            next_component = response.component
                    
                    # Check if next component has been set somehow e.g. from ComponentResponse
                    if next_component:
                        # Set dummy response and request
                        request = HttpRequest(
                            client_address=self.ws_view.request.client_address, 
                            client_socket=self.ws_view.request.client_socket, 
                        )
                        request.fullpath = fullpath
                        request.method = "GET"
                        response = HttpResponse()
                        
                        if hasattr(next_component, "fullpage_reload") and next_component.fullpage_reload:
                            # Server prefers fullpage_reload
                            await self.ws_view.send_data([
                                EventOpCode.NAVIGATION_RESULT,
                                fullpath,
                                True, # fullreload
                                None, # component uid
                                [], # patches
                                True, # List of patches are final.
                            ])
                            return
                        
                        # Try partial page reload
                        prev_vdom = prev_component.to_vdom()
                        next_vdom = next_component.to_vdom()
                        
                        # Send patches as we are generating every patch
                        await next_component.vdom_diff_and_act(on_new_patch, old=prev_vdom, new=next_vdom)
                        
                        # Send final empty patches - Flag as patches finished.
                        await self.ws_view.send_data([
                            EventOpCode.NAVIGATION_RESULT,
                            fullpath,
                            False, # fullreload
                            next_component.uid, # component uid
                            [], # patches
                            True, # List of patches are final.
                        ])
                        
                        # Log response after sending patches
                        response.content_obj.set_fake_size(f"[{total_patches} patches]")
                        ResponseHandler.auto_log_response(response, request)
                        return
             
            # Just send full reload response
            await self.ws_view.send_data([
                EventOpCode.NAVIGATION_RESULT,
                fullpath,
                True, # fullreload
                None, # component uid
                [], # patches
                True, # List of patches are final.
            ])
        
        except Exception as e:
             if isinstance(e, asyncio.CancelledError):
                 return
                 
             if SETTINGS['DEBUG']:
                 logger.log("Error whilst handling navigation for ws client: ", level=logger.WARNING)
                 logger.log_exception(e)
                 
             # Fallback to full page reload on every exception
             if fullpath:
                 await self.ws_view.send_data([
                     EventOpCode.NAVIGATION_RESULT,
                     fullpath,
                     True, # fullreload
                     None, # component uid
                     [], # patches
                     True, # These patches are final.
                 ])
