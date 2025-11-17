"""
H2 Event handler module.
"""
import ssl
import time
import asyncio
import threading

from typing import (
    Dict,
    Optional,
    List,
    Tuple,
    Callable,
)
from functools import partial
from h2.events import (
    ConnectionTerminated,
    DataReceived,
    RemoteSettingsChanged,
    RequestReceived,
    StreamEnded,
    StreamReset,
    WindowUpdated,
    SettingsAcknowledged,
    PriorityUpdated,
    PingReceived,
)
from h2.exceptions import ProtocolError
from h2.errors import ErrorCodes
from h2.settings import SettingCodes

from duck.settings import SETTINGS
from duck.http.request_data import RequestData
from duck.http.response import HttpResponse
from duck.contrib.sync import iscoroutinefunction, convert_to_async_if_needed
from duck.utils.threading import SyncFuture
from duck.utils.asyncio import create_task
from duck.logging import logger


class EventHandler:
    """
    HTTP/2 Event handler.
    
    This handles `h2` events asynchrously.
    """
    def __init__(self, protocol, server):
        self.protocol = protocol
        self.conn = protocol.conn
        self.server = server
        self.stream_data = {} # {stream_id: RequestData}
        self.stream_event_queue = {} # {stream_id: asyncio.Queue[H2Event]}
        self.flow_control_futures = {} # {stream_id: asyncio.Future}
        self.stream_tasks = {} # {stream_id: asyncio.Task}
        
        # Stream specific event handlers
        self.stream_event_map = {
            RequestReceived: self.on_new_request,
            DataReceived: self.on_request_body,
            StreamEnded: self.on_request_complete,
            StreamReset: lambda e: self.on_stream_reset(e.stream_id),
        }
        
        # Global event handlers
        self.event_map = {
            PingReceived: lambda e: 0,
            PriorityUpdated: lambda e: 0,
            SettingsAcknowledged: lambda e: 0,
            WindowUpdated: lambda e: self.on_window_updated(e.stream_id, e.delta),
            ConnectionTerminated: self.on_connection_terminated,
            RemoteSettingsChanged: self.on_remote_settings_changed,
        }

    async def entry(self, data: bytes):
        """
        Entry method for processing incoming data.
        """
        events = self.conn.receive_data(data)
        await self.dispatch_events(events)
        
    async def start_stream_loop(self, stream_id: int):
        """
        Starts a loop for handling stream events.
        
        Notes:
        - This handles events by stream ID.
        """
        # This must be started in an asyncio task
        while True:
            # Yield control to the event loop
            await asyncio.sleep(0)
            
            # Retrieve stream queue
            event_queue = self.stream_event_queue[stream_id]
            
            try:
                event = await event_queue.get()
                handler = self.stream_event_map.get(type(event))
                
                if handler:
                    if iscoroutinefunction(handler):
                        await handler(event)
                    else:
                        handler(event)
                else:
                    raise TypeError(f"Received an unknown event: {event}. No event handler for this event in stream_event_map.")
                    
            except asyncio.QueueEmpty:
                # No event to handle
                continue
                
            except Exception as e:
                # For every event failure, just log the exception and
                # continue with other events as not doing so may stall the connection
                logger.log_exception(e)
            
            finally:
                # Send any pending data.
                await self.protocol.async_send_pending_data()
            
    def on_new_request(self, event):
        """
        Received headers for a new request.
        """
        stream_id = event.stream_id
        
        headers = {
            header.decode("utf-8"): value.decode("utf-8")
            for header, value in event.headers
        }
        
        # Update stream_data
        request_data = RequestData(headers)
        self.stream_data[stream_id] = request_data
        
    async def on_request_body(self, event):
        """
        Called when we received a request body.
        """
        stream_id = event.stream_id
        data = event.data
        stream_data = self.stream_data.get(stream_id)
        
        if not stream_data:
            self.conn.reset_stream(
                stream_id, error_code=ErrorCodes.PROTOCOL_ERROR
            )
        else:
            stream_data.content = stream_data.content.join([b"", data])
            self.conn.increment_flow_control_window(5 * 1024 * 1024, stream_id)
            self.conn.acknowledge_received_data(len(data), stream_id)
            await self.protocol.async_send_pending_data()
            
    async def on_request_complete(self, event):
        """
        Full request received.
        """
        stream_id = event.stream_id
        request_data = self.stream_data.pop(stream_id, None)
        
        if not request_data:
            return
        
        # Create headers
        headers = request_data.headers
        topheader = "{method} {path} {http_version}".format(
            method=headers.pop(':method'),
            path=headers.pop(':path'),
            http_version='HTTP/1.1'
        )
        
        if ":authority" in headers:
            authority = headers.pop(':authority')
            headers["host"] = authority
        
        if ":scheme" in headers:
            headers.pop(":scheme")
            
        #: Important
        # Set the request data topheader in headers
        request_data.headers["topheader"] = topheader
        
        # Set request data stream ID and h2_handling
        request_data.request_store["stream_id"] = stream_id
        request_data.request_store["h2_handling"] = True
        
        if SETTINGS['ASYNC_HANDLING']:
            # We are in async context
            coro = self.server.async_handle_request_data(
                self.protocol.sock,
                self.protocol.addr,
                request_data,
            )
            await coro
        else:
            # The server is using threads to manage the connection, so we need to dispose the processing of request
            # back to the current thread so that it will be handled synchronously rather than in async context.
            await self.execute_synchronously_in_current_thread(
                partial(
                    self.server.handle_request_data,
                    self.protocol.sock,
                    self.protocol.addr,
                    request_data,
                )
            )
            
    async def execute_synchronously_in_current_thread(self, func: Callable):
        """
        Adds a callable to `sync_queue` so that it will be executed outside async context,
        useful in multithreaded environment where threads are created for each connection
        and `ASYNC_HANDLING=False`
        
        Args:
            func (Callable): Callable function or method which doesn't accept any arguments.
        """
        if not self.protocol.sync_queue:
            raise TypeError("Sync queue is not set, it is required for adding tasks to queue.")
        
        if SETTINGS['ASYNC_HANDLING']:
            raise SettingsError(
                "ASYNC_HANDLING is set to True so no thread will be available to handle this task."
                "This method must be called in a multithreaded environment."
            )
            
        # Add task to queue so that will be executed synchronously.
        future = SyncFuture()
        self.protocol.sync_queue.put((func, future))
        await convert_to_async_if_needed(future.result)()
        
    def on_stream_reset(self, stream_id: int):
        """
        Called when the client resets a stream.
        
        This can occur when:
        - The client cancels an in-progress request.
        - The client connection is aborted or timed out.
        - An internal protocol error is detected.
        
        Cleans up any cached request data, pending flow control futures,
        or in-progress tasks associated with the given stream.
        
        Args:
            stream_id (int): The HTTP/2 stream ID that was reset.
        """
        # Remove stream request data if exists
        self.stream_data.pop(stream_id, None)
        
        # Remove stream queue
        self.stream_event_queue.pop(stream_id, None)
            
        # Cancel flow control future if one exists
        future = self.flow_control_futures.pop(stream_id, None)
        if future and not future.done():
            future.cancel()
        
        # Cancel any tasks if any
        task = self.stream_tasks.pop(stream_id, None)
        task.cancel()

    def on_window_updated(self, stream_id, delta):
        """
        A window update frame was received.
        """
        if stream_id and stream_id in self.flow_control_futures:
            # Update flow control future.
            f = self.flow_control_futures.pop(stream_id)
            f.set_result(delta)
        
        elif not stream_id:
            # Update all flow control futures.
            for f in self.flow_control_futures.values():
                f.set_result(delta)
            self.flow_control_futures = {}
        
    def on_remote_settings_changed(self, event):
        """
        On RemoteSettingsChanged event handler method.
        """
        if SettingCodes.INITIAL_WINDOW_SIZE in event.changed_settings:
            self.on_window_updated(None, 0)
            
    def on_connection_terminated(self, event):
        """
        Connection terminated.
        """
        for future in self.flow_control_futures.values():
            future.cancel()
        
        # Cancel any tasks if any
        for task in self.stream_tasks.values():
            task.cancel()
        
        # Reset some data.        
        self.stream_event_queues = {}
        self.flow_control_futures = {}
        self.stream_tasks = {}
        self.protocol.connection_lost()
        
    async def wait_for_flow_control(self, stream_id: int):
        """
        Waits for a Future that fires when the flow control window is opened.
        
        Args:
            stream_id (int): The HTTP/2 stream ID.
        """
        f = asyncio.Future()
        self.flow_control_futures[stream_id] = f
        await f
        
    async def dispatch_events(self, events: List):
        """
        Dispatch all received events.
        """
        await self.protocol.async_send_pending_data()
        
        async def handle_stream_event(event):
            """
            Handle stream specific event.
            """
            stream_id = event.stream_id
            
            if isinstance(event, RequestReceived):
                # Cancel any existing task (if any)
                existing_task = self.stream_tasks.pop(stream_id, None)
                if existing_task:
                    if not existing_task.done():
                        existing_task.cancel()
                
                # Cancel any existing flow control future (if any)
                existing_flow_control_future = self.flow_control_futures.pop(stream_id, None)
                if existing_flow_control_future:
                    if not existing_flow_control_future.done():
                        existing_flow_control_future.cancel()
                
                # Set stream info
                self.stream_event_queue[stream_id] = asyncio.Queue()
                self.stream_tasks[stream_id] = create_task(self.start_stream_loop(event.stream_id))
            
            # Now handle the event, even the RequestReceived must be rehandled here.
            queue = self.stream_event_queue[stream_id]
            await queue.put(event) # Submit event to the queue
            
        # Handle events.
        for event in events:
            try:
                handler = self.event_map.get(type(event))
                
                if handler:
                    if iscoroutinefunction(handler):
                        await handler(event)
                    else:
                        handler(event)
                
                elif self.stream_event_map.get(type(event)):
                    # Handle stream specific event
                    await handle_stream_event(event)
                
                else:
                    raise TypeError(f"Received an unknown event: {event}. No event handler for this event in event_map.")
                    
            except Exception as e:
                # For every event failure, just log the exception and
                # continue with other events as not doing so may stall the connection
                logger.log_exception(e)
            
            # Send any pending data.
            await self.protocol.async_send_pending_data()
