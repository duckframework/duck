"""
Multiprocessing proxy implementation for optimum performance. This module enables 
fast inter-process communication using `msgpack` and shared memory buffers.

Usage:

```py
import multiprocessing

from duck.utils.multiprocessing import ProxyServer, Proxy

class myObject:
    pass
    
server = ProxyServer(bufsize=200)
server.run()

obj = myObject()
obj.a = 100

proxy = server.create_proxy(obj)

def process_entry(proxy: Proxy):
    with proxy as p:
        print(p.a) # Output: 100
        
p1 = multiprocessing.Process(target=process_entry, args=[proxy])
p1.start()
p1.join()

```

TODO:
- Make sure dunder methods like `__iter__`, `__await__` to work seemless the same way original objects act.
- Implement asynchronous protocol
- Enable multiprocessing when starting proxy server, for isolation.
- Make iterables to work with `create_proxy`.  
      Example:
      ```py
      proxy = Proxy([1, 2, 3])
      
      def process_entry(proxy: Proxy):
          with proxy as p:
              print(list(p)) # Must print [1, 2, 3]
              p.append(4)
              print(list(p)) # Must print [1, 2, 3, 4]
      ```
"""
import enum
import time
import struct
import threading
import msgpack
import inspect
import functools
import multiprocessing
import multiprocessing.shared_memory as sm

from types import MethodType
from typing import (
    List,
    Dict,
    Optional,
    Any,
    Callable,
    Union,
    Iterable,
)

from duck.exceptions.all import SettingsError


try:
    from duck.logging import logger
except SettingsError:
    # Not inside a Duck project
    from duck.logging import console as logger


def get_callable_name(fn):
    """
    Return a readable name for fn.
    Works for functions, bound methods, functools.partial, and callable objects.
    """
    # Unwrap partials
    if isinstance(fn, functools.partial):
        return get_callable_name(fn.func)

    # Bound method (has __func__ and __self__)
    if inspect.ismethod(fn):
        return fn.__func__.__name__  # same as fn.__name__ for bound methods

    # Plain function or builtin
    if inspect.isfunction(fn) or inspect.isbuiltin(fn):
        return fn.__name__

    # Callable instance (object with __call__)
    if hasattr(fn, "__call__"):
        # Prefer the __call__ function name, show class for clarity
        call_attr = getattr(fn.__call__, "__name__", None)
        if call_attr and call_attr != "<lambda>":
            return f"{type(fn).__name__}.__call__"
        return type(fn).__name__

    # Fallback
    return getattr(fn, "__name__", type(fn).__name__)


def is_method_of(callable_obj, obj):
    """
    True if callable_obj is a method of obj (bound to that object) or
    if the function underlying callable_obj is the attribute on obj.

    Examples:
    - is_method_of(a.foo, a) -> True
    - is_method_of(A.foo, a) -> True (A.foo is the function, still considered 'a' method)
    - is_method_of(a.bar, a) -> False if bar is not on a
    """
    # If it's a bound method, check its __self__
    if inspect.ismethod(callable_obj):
        return callable_obj.__self__ is obj

    # Unwrap partials
    if isinstance(callable_obj, functools.partial):
        return is_method_of(callable_obj.func, obj)

    # If callable_obj has no name, fall back to False (can't look it up on obj)
    name = getattr(callable_obj, "__name__", None)
    if name is None:
        return False

    # Try to fetch attribute with same name from the object
    try:
        attr = getattr(obj, name)
    except AttributeError:
        return False

    # If attr is a bound method, compare underlying function objects
    if inspect.ismethod(attr):
        # attr.__func__ is the function object stored on the class
        # callable_obj could be either the bound method or the raw function
        underlying = getattr(callable_obj, "__func__", callable_obj)
        return attr.__func__ is underlying

    # For staticmethod or function attribute on the instance/class, compare directly
    meth_str = f"of {obj.__class__.__name__}"
    return attr is callable_obj or meth_str in str(callable_obj)


class ProxyError(Exception):
    """
    Raised on multiprocessing proxy issues.
    """


class ProxyObjectNotFound(ProxyError):
    """
    Raised if target object linked with the proxy is not found.
    """


class LimitedProxyChaining(ProxyError):
    """
    Raised when proxy chaining reaches configured maximum depth.
    Provides a clear message and suggests mitigations.
    """

    def __init__(self, max_level: int, target_obj: Optional[str] = None):
        self.max_level = max_level
        msg = (
            f"Proxy chaining reached the maximum allowed level ({max_level}). "
            "This usually means your code repeatedly returns non-serializable objects "
            "which get wrapped as proxy references. Consider increasing the server "
            "proxy chaining limit, refactoring to return serializable data, or "
            "exposing a higher-level API on the server side to avoid deep chaining."
        )
        if target_obj:
            msg = f"{msg} Offending object description: {target_obj!r}."
        super().__init__(msg)


class DataDecodeError(ProxyError):
    """
    Raised when there are issues decoding data written to the shared memory.
    """


class DataEncodeError(ProxyError):
    """
    Raised when there are issues encoding data to be written to the shared memory.
    """


class DataTooBigError(ProxyError):
    """
    Raised when trying to write data that is too big to the shared memory.
    """


class EmptyData(ProxyError):
    """
    Raised if data to be read is empty or zero.
    """


class ProxyOpCode(enum.IntEnum):
    """
    Opcodes for proxy operations.
    """
    
    GET = 0
    """
    Get an attribute from the real object.  
     
    Format: [opcode, [target_object_id, attr]]  
    
    Where:
    - opcode (int): The operation code.
    - target_object_id (int): The original object ID.
    - attr (str): The attribute to retrieve.
    """
    
    SET = 1
    """
    Set an attribute on the real object.  
    
    Format: [opcode, [target_object_id, attr, value]]  
    
    Where:
    - opcode (int): The operation code.
    - target_object_id (int): The original object ID.
    - attr (str): The attribute to alter.
    - value (Any): The value to set.
    """
    
    EXECUTE = 2
    """
    Execute a callable on the real object.
    
    Format: [opcode, [target_object_id, attr, args, kwargs]]  
    
    Where:
    - opcode (int): The operation code for the request i.e. 2 in this case.
    - target_object_id (int): The target ID for the real object.
    - attr (str): The method name to execute.
    - args (tuple): The arguments to parse when executing (as a tuple).
    - kwargs (dict): Dictionary of positional keyword arguments.
    """
    
    EXECUTION_RESULT = -1
    """
    This represent the result of an execution for the client.  
    
    Format: [opcode, [target_object_id, value, error]]  
    
    Where:
    - opcode (int): The operation code, i.e., -1 in this case.
    - target_object_id (int): The ID to the target object.
    - value (Any): Any serializable data (using msgpack).
    - error (str): Error if any has been encountered.
    """
    
    RESPONSE_PENDING = -2
    """
    Represents that the server is still processing request and the 
    response is not ready yet. 
    
    Format: [opcode, []]
    """
    

class Frame:
    """
    Frame that will be written to the shared memory.
    """
    
    __slots__ = ("opcode", "payload")
    
    def __init__(self, opcode: int, payload: List[Any]):
        """
        Initialize the frame.
        
        Args:
            opcode (int): The operation code for this frame.
            payload (List[Any]): The payload for the frame as a list.
        """
        self.opcode = opcode
        self.payload = payload
        
    @classmethod
    def parse(self, data: bytes) -> "Frame":
        """
        Parse data and produce a frame object.
        """
        try:
            opcode, payload = msgpack.unpackb(data, raw=False)
            return Frame(opcode, payload)
        except Exception as e:
            raise DataDecodeError(f"Error decoding data: {e}.") 
            
    def __repr__(self):
        return f"<[{self.__class__.__name__} opcode={self.opcode}]>"
    
    __str__ = __repr__
    

class Proxy:
    """
    Multiprocessing proxy object. This performs actions like `get` or `set` of anything 
    indirectly on a real object.
    
    Use Case:
    - Indirectly performing actions on objects that are heavy or complex (not serializable) 
          between processes.
    
    Notes:
    - This must be created in process where the real object resides and then be used as proxy in another process.
    - Make sure to delete the proxy object after use, this frees the shared memory also. 
    """
    _proxy_prefix = "<proxy>-" # Prefix of another proxy object that is usually created for objects that are not serializable
    _callable_prefix = "<callable>-" # Prefix of callables that cant be send directly using shared memory    
    
    _cls_attrs = {
        "get_shared_memory",
        "get_response",
        "read_frame",
        "write_frame",
        "idx",
        "close",
        "target_obj_str",
        "shared_memory_name",
        "_sm",
        "_bufsize",
        "_server_running",
        "_callable_prefix",
        "_proxy_prefix",
        "_close_on_delete",
        "_DATA_SIZE_PREFIX_LEN",
        "__str__",
        "__repr__",
        "__del__",
        "__enter__",
        "__exit__",
        "__class__",
        "__dir__",
        "__setitem__",
        "__getitem__",
        "_chain_level",
        "_proxy_chaining_max_level",
        "_last_error",
    }
    """
    These are attributes that belong soley on this proxy object but not the target object.
    """
    
    _DATA_SIZE_PREFIX_LEN: int = 4
    """
    This is the 4-byte length of the `data size prefix` when placing data in shared memory.  
    
    Example:
        20 [0, ...]  
    
    Where:
    - `20`: Is the data size prefix.
    - `0`: This is the OpCode for `GET`.
    - `...`: This is extra payload for the data.
    
    """
    
    __slots__ = {
        "idx",
        "target_obj_str",
        "shared_memory_name",
        "_sm",
        "_bufsize",
        "_server_running",
        "_close_on_delete",
        "_chain_level",
        "_proxy_chaining_max_level",
        "_last_error",
    }
    
    def __init__(
        self,
        proxy_server: "ProxyServer",
        idx: int,
        target_obj: Any,
        shared_memory: sm.SharedMemory,
    ):
        """
        Initialize the proxy object.
        
        Args:
            proxy_server (ProxyServer): The proxy server which wants to create this proxy object.
            idx (int): Unique ID for the proxy object.
            target_obj (Any): This is the real/target object you want to proxy to.
            shared_memory (sm.SharedMemory): The target shared memory for this proxy object.
        """
        assert isinstance(proxy_server, ProxyServer), f"The proxy_server must be an instance of ProxyServer not {type(proxy_server)}"
        assert target_obj is not None, f"Target object must not be None."
        assert isinstance(shared_memory, sm.SharedMemory), f"The shared_memory must be an instance of SharedMemory not {type(shared_memory)}."
        
        self.idx = idx
        self.target_obj_str = str(target_obj)
        self.shared_memory_name = shared_memory.name
        self._sm: Optional[sm.SharedMemory] = None
        self._bufsize = proxy_server._bufsize
        self._close_on_delete = True
        self._last_error = None
        
        if isinstance(target_obj, Iterable):
            # Don't use the default string representation of iterables because this may reflect wrong data 
            # as the str representation may not include current available items
            self.target_obj_str = str(type(target_obj))
        
        # Chain-level (how many proxies have been created between the original server and this client)
        self._chain_level = 0
        
        # Default max; if a server provided an explicit max it will be applied later in get_response
        self._proxy_chaining_max_level = getattr(proxy_server, "_proxy_chaining_max_level", 7) if proxy_server else 7
        
        if not proxy_server.running:
            raise ProxyError("The provided proxy_server is not running. Make sure `run` is called on the proxy_server for running the server.")
        self._server_running = True
        
    def get_shared_memory(self) -> sm.SharedMemory:
        """
        Gets the target shared memory for this proxy object.
        """
        if not self._sm:
            # Open existing shared memory block by name (created by server)
            self._sm = sm.SharedMemory(name=self.shared_memory_name)
        return self._sm
        
    def read_frame(self, shared_memory: sm.SharedMemory, timeout: Optional[float] = 0.5) -> Frame:
        """
        Reads a frame from shared memory and returns the parsed Frame (or result of Frame.parse).

        This waits until the full payload (as indicated by the 4-byte big-endian length prefix)
        is available in the shared memory or until the optional timeout expires.

        Raises:
            TimeoutError: if the full payload isn't available within `timeout`.
            DataTooBigError: if the indicated payload would exceed the configured buffer size.
            DataDecodeError: for other decoding/parsing errors.
            EmptyData: If data is empty or size is less than 1 byte.
        """
        buffer = shared_memory.buf  # memoryview

        # Ensure prefix bytes exist
        if len(buffer) < self._DATA_SIZE_PREFIX_LEN:
            raise DataDecodeError("Shared memory buffer is smaller than the length-prefix size.")

        try:
            # Read the 4-byte big-endian length prefix
            prefix_bytes = bytes(buffer[: self._DATA_SIZE_PREFIX_LEN])
            data_length = struct.unpack(">I", prefix_bytes)[0]
        except struct.error as e:
            raise DataDecodeError(f"Failed to unpack data length prefix: {e}")
            
        # Check if total_bytes is not greater than bufsize
        total_bytes = data_length + self._DATA_SIZE_PREFIX_LEN
        if total_bytes > self._bufsize:
            raise DataTooBigError(
                f"The data to be read is too big. Max is {self._bufsize} byte(s) but data to be read is {total_bytes} bytes."
            )

        start = self._DATA_SIZE_PREFIX_LEN
        end = start + data_length
        start_time = time.time()
        
        if data_length == 0:
            raise EmptyData("Data to be read is empty or zero.")
            
        try:
            # Try to read until we get the expected number of payload bytes or timeout.
            while True:
                payload = bytes(buffer[start:end])
                
                if len(payload) == data_length:
                    break
                
                if timeout is not None and (time.time() - start_time >= timeout):
                    raise TimeoutError(
                        f"Timed out reading full data. Expected {data_length} byte(s) but got {len(payload)} byte(s)."
                    )
                
                # Small sleep to avoid tight busy loop; adjust as needed for your use-case.
                time.sleep(0.001)
    
            # Parse the frame payload
            return Frame.parse(payload)
        
        except Exception as e:
            raise DataDecodeError(f"Error decoding data: {e}") from e
            
    def write_frame(self, shared_memory: sm.SharedMemory, frame: Frame) -> int:
        """
        Write a frame to the shared memory.

        The written layout is:
        [4-byte big-endian uint32 payload-length][payload bytes]

        Returns:
            int: Written payload size in bytes (does not include the 4-byte length prefix).

        Raises:
            DataTooBigError: if the payload+prefix would not fit into the configured buffer.
        """
        assert isinstance(frame, Frame), f"Frame must be an instance of Frame not {type(frame)}."
        
        # Pack payload using msgpack
        data = msgpack.packb([frame.opcode, frame.payload], use_bin_type=True)
        size = len(data)
        total_bytes = size + self._DATA_SIZE_PREFIX_LEN

        if total_bytes > self._bufsize:
            raise DataTooBigError(
                f"Data too large to fit into shared memory buffer: {total_bytes} byte(s) is greater than {self._bufsize} byte(s)."
            )

        # Write 4-byte length prefix then payload
        buffer = shared_memory.buf  # memoryview supports slice assignment with bytes
        buffer[: self._DATA_SIZE_PREFIX_LEN] = struct.pack(">I", size)
        buffer[self._DATA_SIZE_PREFIX_LEN : total_bytes] = data
        
        # Return written bytes
        return size
        
    def get_response(self, frame: Frame, timeout: Optional[float] = None) -> Union[Any, "Proxy", Callable]:
        """
        This makes a request to the proxy server and returns the correct response/result.

        Important behaviour:
        - If the response is a Proxy descriptor (structured dict or legacy string), a new Proxy object
          is returned and its chain level is incremented.
        - If the response is a normal (real/serializable) value or a callable descriptor,
          this proxy's chain level is reset to 0 (per user's requirement).
        """
        valid_opcodes = [
            ProxyOpCode.GET,
            ProxyOpCode.SET,
            ProxyOpCode.EXECUTE,
        ]
        
        assert frame.opcode in valid_opcodes, f"OpCode not recognized, available opcodes: {valid_opcodes}."
        
        # Retrieve the shared memory.
        sm = self.get_shared_memory()
        
        # Send/write data to shared memory.
        self.write_frame(sm, frame)
        
        # Read response
        response_frame = None
        start_time = time.time()
        
        while True:
            if timeout and (time.time() - start_time >= timeout):
                raise TimeoutError(f"Request timed out: Got no response in {timeout: .2f} seconds.")
                
            try:
                response_frame = self.read_frame(sm, timeout=0.001)
                if response_frame.opcode == ProxyOpCode.EXECUTION_RESULT:
                    break
                     
            except DataDecodeError:
                # Maybe data is not enough yet to be decoded.
                pass
                
            except TimeoutError:
                pass
                
            # Sleep to avoid busy loop
            time.sleep(0.0005)
            
        if response_frame.opcode == ProxyOpCode.EXECUTION_RESULT:
            target_object_id, value, error = response_frame.payload
            
            if error:
                # Provide the error type and message from server
                raise ProxyError(f"Server-side error when operating on target object id={target_object_id}: {error}")
                
            if isinstance(value, str) and value.startswith(self._proxy_prefix):
                # Server is trying to tell us that this is another proxy object, usually sent if data cannot be serialized.
                target_object_str = value.split(self._proxy_prefix, 1)[-1]
                
                # Use default max level stored on this Proxy instance
                max_level = getattr(self, "_proxy_chaining_max_level", 7)
                chain_level = getattr(self, "_chain_level", 0)
                
                # Implement proxy chaining check logic
                if chain_level + 1 > max_level:
                    raise LimitedProxyChaining(max_level, target_obj=target_object_str)

                dummy_proxy_server = ProxyServer(bufsize=self._bufsize)
                dummy_proxy_server._running = 1
                dummy_target_object = object()
                
                # Create new proxy object
                proxy = Proxy(
                    proxy_server=dummy_proxy_server,
                    idx=target_object_id,
                    target_obj=dummy_target_object,
                    shared_memory=sm,
                )
                
                # Update vital attributes
                proxy.target_obj_str = target_object_str
                proxy._chain_level = chain_level + 1
                proxy._proxy_chaining_max_level = max_level

                # Return the proxy object.
                return proxy
                
            elif isinstance(value, str) and value.startswith(self._callable_prefix):
                # This is a method
                method = value.split(self._callable_prefix, 1)[-1]
                
                # Reset chain level on this proxy as we've received a real (callable descriptor) response
                try:
                    self._chain_level = 0
                except Exception:
                    # best-effort; ignore if attribute not present
                    pass
                    
                # Create custom method that makes a request for execution upon callback
                def execute_on_target(*args, **kwargs):
                    request_frame = Frame(opcode=ProxyOpCode.EXECUTE, payload=[target_object_id, method, args, kwargs])
                    return self.get_response(request_frame)
                
                # Return proxy callable
                return execute_on_target
                
            # At this point it's a real/serializable value: reset chain level per user's request.
            try:
                self._chain_level = 0
            except Exception:
                # best-effort; ignore if attribute not present
                pass
                
            # Return the value
            return value
            
        else:
            raise ProxyError(f"Unknown response from server: {response_frame}.")
            
    def close(self):
        """
        Closes the shared memory for the proxy object.
        """
        try:
            sm = self.get_shared_memory()
            sm.close()
            sm.unlink()
        
        except FileNotFoundError:
            # Shared memory nolonger available
            pass
        
        except Exception:
            # Be quiet on other cleanup errors
            pass
                 
    def __getattribute__(self, key):
        super_getattr = super().__getattribute__
        super_setattr = super().__setattr__
        last_error = super_getattr('_last_error')
        
        if last_error:
            # We manually return immediately inside this method because if we don't, 
            # any exception encountered inside context manager will be suppressed
            super_setattr('_last_error', None)
            return
            
        if key in type(self)._cls_attrs:
            return super().__getattribute__(key)
        
        # Get response from the server.
        get_response = super_getattr("get_response")
        idx = super_getattr('idx')
        request_frame = Frame(opcode=ProxyOpCode.GET, payload=[idx, key])
        result = get_response(request_frame)
        return result
        
    def __setattr__(self, key, value):
        super_getattr = super().__getattribute__
        
        if key in type(self)._cls_attrs:
            return super().__setattr__(key, value)
        
        # Send a request for setting attribute and get response.
        get_response = super_getattr("get_response")
        idx = super_getattr('idx')
        request_frame = Frame(opcode=ProxyOpCode.SET, payload=[idx, key, value])
        return get_response(request_frame)
        
    def __delattr__(self, key):
        super_getattr = super().__getattribute__
        
        if key in type(self)._cls_attrs:
            return super().__delattr__(key)
        
        # Send a request for deleting the attribute to the server.
        get_response = super_getattr("get_response")
        idx = super_getattr('idx')
        request_frame = Frame(opcode.ProxyOpCode.EXECUTE, [idx, "__delattr__", (), {}])
        return get_response(request_frame)
        
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc, exc_tb):
        try:
            self.close()
        finally:
            if exc:
                super().__setattr__("_last_error", exc)
            return False
            
    def __getitem__(self, key):
        super_getattr = super().__getattribute__
        get_response = super_getattr("get_response")
        idx = super_getattr('idx')
        args = [key]
        kwargs = {}
        request_frame = Frame(opcode=ProxyOpCode.EXECUTE, payload=[idx, "__getitem__", args, kwargs])
        result = get_response(request_frame)
        return result
        
    def __setitem__(self, key, value):
        super_getattr = super().__getattribute__
        get_response = super_getattr("get_response")
        idx = super_getattr('idx')
        args = [key, value]
        kwargs = {}
        request_frame = Frame(opcode=ProxyOpCode.EXECUTE, payload=[idx, "__setitem__", args, kwargs])
        result = get_response(request_frame)
        return result
        
    def __del__(self):
        if not self._close_on_delete:
            super_del = getattr(super(), '__del__', None)
            if super_del is not None:
                super_del()
            return
            
        try:
            if not getattr(self, "_server_running", False):
                # Server is not running
                self.close()
            
            # Try sending a request for cleanup
            super_getattr = super().__getattribute__
            get_response = super_getattr("get_response")
            idx = super_getattr('idx')
            request_frame = Frame(opcode=ProxyOpCode.EXECUTE, payload=[idx, "__del__"])
            
            try:
                return get_response(request_frame)
            except Exception:
                # Failed to do cleanup using the server as a mediator
                pass
            
            finally:
                self.close()
                
        finally:    
            super_del = getattr(super(), '__del__', None)
            if super_del is not None:
                super_del()
            
            # Close on our end just in case
            self.close()
            
    def __repr__(self):
        # Only define __repr__, __str__ must be resolved on real object
        return f"<[{self.__class__.__name__} {self.target_obj_str}]>"
    
    __str__ = __repr__


class ProxyServer:
    """
    Server for handling proxy objects.
    """
    
    _DATA_SIZE_PREFIX_LEN: int = 4
    """
    This is the 4-byte length of the `data size prefix` when placing data in shared memory.  
    
    Example:
    ```py
        20 [0, ...]  
    ```
    
    Where:
    - `20`: Is the data size prefix.
    - `0`: This is the OpCode for `GET`.
    - `...`: This is extra payload for the data.
    """
    
    def __init__(self, bufsize: int):
        # map id(target) -> [target_obj, proxy, shared_memory]
        self.proxy_objects: Dict[int, List[Any, Proxy, sm.SharedMemory]] = {}
        
        # Define more attributes
        self.creator_process = multiprocessing.current_process()
        self.server_thread: Optional[threading.Thread] = None
        self._running = False
        self._bufsize = bufsize
        self._threaded = False
        
        # Whether to enable proxy chaining. Condition on whether to wrap 
        # all objects that are not serializable as Proxy objects.
        self._wrap_unserializable_objects = True
        self._proxy_chaining_max_level = 7
        
        # Lock to avoid race conditions when manipulating proxy_objects
        self._lock = threading.RLock()
        
    @property
    def running(self) -> bool:
        """
        Returns boolean on whether if or if not the server is running.
        """
        return self._running
        
    def run(self, threaded: bool = True):
        """
        Runs the current proxy server on current thread.
        
        Args:
            threaded (bool): Whether to run the server in a thread. Defaults to True.
        """
        assert not self._running, "Proxy server already running."
        self._running = True
        self._threaded = threaded
        
        def _run():
            while self._running:
                try:
                    # Copy items to avoid "dictionary changed size during iteration"
                    with self._lock:
                        items = list(self.proxy_objects.items())
                        
                    for _, data in items:
                        # data is [target_object, proxy, shared_memory]
                        data: List[Any, Proxy, sm.SharedMemory]
                        _, proxy, shared_memory = data
                        try:
                            request_frame = self.read_frame(shared_memory)
                            
                            if request_frame.opcode in [ProxyOpCode.GET, ProxyOpCode.SET, ProxyOpCode.EXECUTE]:
                                # Only handle request if the data in shared memory is written by the client not us.
                                self.handle_request_frame(shared_memory, request_frame)
                        
                        except EmptyData:
                            # Nothing to do.
                            pass
                            
                        except DataDecodeError as e:
                            # Malformed data, surface it.
                            raise e # Reraise exception
                            
                        except Exception:
                            raise
                    
                except RuntimeError as e:
                    if "dictionary changed size" in str(e):
                        continue
                    else:
                        raise e
                            
                except Exception as e:
                    logger.log_exception(e) # Log exception
                        
                # Sleep a little bit.
                time.sleep(0.001)
                               
        if threaded:
            self.server_thread = threading.Thread(target=_run)
            self.server_thread.start()
        else:
            _run() # Run directly
            
    def read_frame(self, shared_memory: sm.SharedMemory, timeout: Optional[float] = 0.5) -> Frame:
        """
        Reads a frame from shared memory and returns the parsed Frame (or result of Frame.parse).

        This waits until the full payload (as indicated by the 4-byte big-endian length prefix)
        is available in the shared memory or until the optional timeout expires.

        Raises:
            TimeoutError: if the full payload isn't available within `timeout`.
            DataTooBigError: if the indicated payload would exceed the configured buffer size.
            DataDecodeError: for other decoding/parsing errors.
            EmptyData: If data is empty or size is less than 1 byte.
        """
        return Proxy.read_frame(self, shared_memory, timeout)
        
    def write_frame(self, shared_memory: sm.SharedMemory, frame: Frame) -> int:
        """
        Write a frame to the shared memory.

        The written layout is:
        [4-byte big-endian uint32 payload-length][payload bytes]

        Returns:
            int: Written payload size in bytes (does not include the 4-byte length prefix).

        Raises:
            DataTooBigError: if the payload+prefix would not fit into the configured buffer.
        """
        return Proxy.write_frame(self, shared_memory, frame)
        
    def handle_request_frame(self, shared_memory: sm.SharedMemory, frame: Frame):
        """
        Handle a request frame from the client.
        """
        if self._threaded:
            th = threading.Thread(target=self.handle_frame, args=[shared_memory, frame])
            th.start()
        else:
            self.handle_frame(shared_memory, frame)
            
    def handle_frame(self, shared_memory: sm.SharedMemory, frame: Frame):
        """
        Handles a frame from the shared memory.
        """
        error = None
        result = None
        target_object_id = None
        target_object = None
        
        # Write a frame that we are now handling the request
        self.write_frame(shared_memory, Frame(ProxyOpCode.RESPONSE_PENDING, []))
        
        try:
            target_object_id = frame.payload[0]
            
            # Get object but with a lock
            with self._lock:
                entry = self.proxy_objects.get(target_object_id, [None, None, None])
            
            # Assign target object.
            target_object, _, __ = entry
            
            if target_object is None: # Doing not target_object can cause issues for empty iterables like lists/dicts
                raise ProxyObjectNotFound(f"Proxy target object with ID `{target_object_id}` not found. It may have been deleted or never declared.") 
            
            if frame.opcode == ProxyOpCode.GET:
                _, key = frame.payload
                result = getattr(target_object, key)
                
            elif frame.opcode == ProxyOpCode.SET:
                _, key, value = frame.payload 
                setattr(target_object, key, value)
             
            elif frame.opcode == ProxyOpCode.EXECUTE:
                _, method_name, args, kwargs = frame.payload
                resolved_method = getattr(target_object, method_name)
                result = resolved_method(*args, **kwargs)
                
        except Exception as e:
            error = e
            
        def is_serializable(data: Any) -> bool:
            """
            Returns a boolean on whether if the data can be serialized by msgpack.
            """
            return isinstance(data, (tuple, int, str, dict, set, list, bool)) if data is not None else True 
        
        if not error:
            if callable(result):
                # This is a method returned as a result
                if not is_method_of(result, target_object):
                    raise ProxyError(f"Callable must be a method of {self}. Independant callables are not allowed. Got {result}.")
                method_name = get_callable_name(result)
                result = f"{Proxy._callable_prefix}{method_name}"
            
            if not is_serializable(result) and self._wrap_unserializable_objects:
                # Create another proxy reference
                proxy_result = self.create_proxy(result, shared_memory)
                target_object_id = proxy_result.idx
                target_object_str = proxy_result.target_obj_str
                result = f"{Proxy._proxy_prefix}{target_object_str}"
                
                # Tweak the proxy result and delete it
                proxy_result._close_on_delete = False
                del proxy_result
                
            # Write response frame
            response_frame = Frame(ProxyOpCode.EXECUTION_RESULT, [target_object_id, result, None])
            
            try:
                self.write_frame(shared_memory, response_frame) 
            except TypeError as e:
                # Error serializing object.
                if self._wrap_unserializable_objects:
                    # Create another proxy reference
                    proxy_result = self.create_proxy(result, shared_memory)
                    target_object_id = proxy_result.idx
                    target_object_str = proxy_result.target_obj_str
                    result = f"{Proxy._proxy_prefix}{target_object_str}"
                    
                    # Tweak the proxy result and delete it
                    proxy_result._close_on_delete = False
                    del proxy_result
                
                    # Alter response frame inplace and retry writting.
                    response_frame.payload = [target_object_id, result, None]
                    self.write_frame(shared_memory, response_frame)
                else:
                    raise e # Reraise exception
                        
        else: 
            error = f"{error.__class__.__name__}: {error}"
            response_frame = Frame(ProxyOpCode.EXECUTION_RESULT, [target_object_id, None, error])
            self.write_frame(shared_memory, response_frame)
    
    def create_proxy(self, target_object: Any, shared_memory: Optional[sm.SharedMemory] = None) -> Proxy:
        """
        Create a process-safe proxy object.
        
        Args:
            target_object (Any): The target object to create the proxy for.
            shared_memory (Optional[sm.SharedMemory]): The shared memory to use for communication. None will create a new shared memory.
        """
        super_del = getattr(target_object, '__del__', None)
        
        def wrapped_del():
            """
            Custom version of delete which closes the shared memory upon delete.
            """
            try:
                data = self.proxy_objects.get(idx)
                
                if data:
                    _, __, shared_mem = data
                    try:
                        shared_mem.close()
                        shared_mem.unlink()
                    except Exception:
                        # best-effort cleanup
                        pass
                    
                    with self._lock:
                        self.proxy_objects.pop(idx, None)
            
            finally:
                # Finally call original __del__ (if available)
                if super_del is not None:
                    super_del()
            
        idx = id(target_object)
        
        with self._lock:
            if idx in self.proxy_objects:
                raise ProxyError("The provided object already exists as a proxy. Please provide a different object or remove the existing proxy first.")

            # Create a shared memory block for the proxy object.
            shared_memory = shared_memory or sm.SharedMemory(create=True, size=self._bufsize, name=f"shared-memory-{idx}")
            proxy = Proxy(self, idx, target_object, shared_memory)
            self.proxy_objects[idx] = [target_object, proxy, shared_memory]
        
        # Patch the target object's __del__ to perform cleanup, but do so carefully
        try:
            target_object.__del__ = wrapped_del
        except Exception:
            # Some objects may not allow attribute assignment; that's acceptable.
            pass
        
        # Finally, return the proxy object    
        return proxy
