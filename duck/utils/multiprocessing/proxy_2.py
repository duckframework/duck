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
from typing import List, Dict, Optional, Any


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
        underlying = getattr(callable_obj, "__func__", callable_obj)
        return attr.__func__ is underlying

    # For staticmethod or function attribute on the instance/class, compare directly
    return attr is callable_obj


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
    """

    SET = 1
    """
    Set an attribute on the real object.

    Format: [opcode, [target_object_id, attr, value]]
    """

    EXECUTE = 2
    """
    Execute a callable on the real object.

    Format: [opcode, [target_object_id, attr, args, kwargs]]
    """

    EXECUTION_RESULT = -1
    """
    This represent the result of an execution for the client.

    Format: [opcode, [target_object_id, value, error]]
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
        self.opcode = int(opcode)
        self.payload = payload

    @classmethod
    def parse(self, data: bytes) -> "Frame":
        """
        Parse data and produce a frame object.
        """
        try:
            opcode, payload = msgpack.unpackb(data, raw=False)
            return Frame(int(opcode), payload)
        except Exception as e:
            # Provide clearer context in decoding errors
            raise DataDecodeError(f"Error decoding data from shared memory: {e}.") from e

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

    _proxy_prefix = "<proxy>-"  # Prefix of another proxy object that is usually created for objects that are not serializable
    _callable_prefix = "<callable>-"  # Prefix of callables that cant be send directly using shared memory

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
        "_chain_level",
        "_proxy_chaining_max_level",
    }
    """
    These are attributes that belong solely on this proxy object but not the target object.
    """

    _DATA_SIZE_PREFIX_LEN: int = 4

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
        assert proxy_server is None or isinstance(proxy_server, ProxyServer), (
            f"The proxy_server must be an instance of ProxyServer or None, not {type(proxy_server)}"
        )
        assert target_obj is not None, "Target object must not be None."
        assert isinstance(shared_memory, sm.SharedMemory), f"The shared_memory must be an instance of SharedMemory not {type(shared_memory)}."

        self.idx = idx
        self.target_obj_str = str(target_obj)
        self.shared_memory_name = shared_memory.name
        self._sm: Optional[sm.SharedMemory] = None
        self._bufsize = proxy_server._bufsize if proxy_server is not None else 0
        self._close_on_delete = True

        # chain-level (how many proxies have been created between the original server and this client)
        self._chain_level = 0
        # default max; if a server provided an explicit max it will be applied later in get_response
        self._proxy_chaining_max_level = getattr(proxy_server, "_proxy_chaining_max_level", 7) if proxy_server else 7

        if proxy_server is not None:
            if not proxy_server.running:
                raise ProxyError("The provided proxy_server is not running. Make sure `run` is called on the proxy_server.")
            self._server_running = True
        else:
            # allow creating a client-only proxy "placeholder" (used only when receiving proxy descriptors)
            self._server_running = False

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
        """
        buffer = shared_memory.buf  # memoryview

        if len(buffer) < self._DATA_SIZE_PREFIX_LEN:
            raise DataDecodeError("Shared memory buffer is smaller than the length-prefix size.")

        try:
            prefix_bytes = bytes(buffer[: self._DATA_SIZE_PREFIX_LEN])
            data_length = struct.unpack(">I", prefix_bytes)[0]
        except struct.error as e:
            raise DataDecodeError(f"Failed to unpack data length prefix: {e}")

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
            while True:
                payload = bytes(buffer[start:end])

                if len(payload) == data_length:
                    break

                if timeout is not None and (time.time() - start_time >= timeout):
                    raise TimeoutError(
                        f"Timed out reading full data. Expected {data_length} byte(s) but got {len(payload)} byte(s)."
                    )

                time.sleep(0.001)

            return Frame.parse(payload)

        except DataDecodeError:
            # re-raise known decode errors
            raise
        except Exception as e:
            raise DataDecodeError(f"Error decoding data: {e}") from e

    def write_frame(self, shared_memory: sm.SharedMemory, frame: Frame) -> int:
        """
        Write a frame to the shared memory.

        Returns:
            int: Written payload size in bytes (does not include the 4-byte length prefix).
        """
        assert isinstance(frame, Frame), f"Frame must be an instance of Frame not {type(frame)}."

        try:
            data = msgpack.packb([frame.opcode, frame.payload], use_bin_type=True)
        except Exception as e:
            raise DataEncodeError(f"Failed to encode frame for shared memory: {e}") from e

        size = len(data)
        total_bytes = size + self._DATA_SIZE_PREFIX_LEN

        if total_bytes > self._bufsize:
            raise DataTooBigError(
                f"Data too large to fit into shared memory buffer: {total_bytes} byte(s) is greater than {self._bufsize} byte(s)."
            )

        buffer = shared_memory.buf
        buffer[: self._DATA_SIZE_PREFIX_LEN] = struct.pack(">I", size)
        buffer[self._DATA_SIZE_PREFIX_LEN : total_bytes] = data

        return size

    def get_response(self, frame: Frame, timeout: Optional[float] = None) -> Any:
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

        smm = self.get_shared_memory()

        # Send/write data to shared memory.
        self.write_frame(smm, frame)

        # Read response
        response_frame = None
        start_time = time.time()

        while True:
            if timeout and (time.time() - start_time > timeout):
                raise TimeoutError(f"Request timed out: Got no response in {timeout:.2f} seconds.")

            try:
                response_frame = self.read_frame(smm, timeout=0.001)
                if response_frame.opcode == ProxyOpCode.EXECUTION_RESULT:
                    break

            except (DataDecodeError, EmptyData):
                # Maybe data is not enough yet to be decoded.
                pass

            except TimeoutError:
                pass

            time.sleep(0.0005)

        if response_frame.opcode == ProxyOpCode.EXECUTION_RESULT:
            target_object_id, value, error = response_frame.payload

            if error:
                # Provide the error type and message from server
                raise ProxyError(f"Server-side error when operating on target object id={target_object_id}: {error}")

            # New structured proxy descriptor (preferred). Backwards compat with legacy string prefix.
            if isinstance(value, dict) and value.get("__proxy__") is True:
                proxy_id = value.get("id", target_object_id)
                target_object_str = value.get("obj", "")
                chain_level = int(value.get("level", 0))
                max_level = int(value.get("max_level", getattr(self, "_proxy_chaining_max_level", 7)))

                # Check chaining limit
                if chain_level + 1 > max_level:
                    raise LimitedProxyChaining(max_level, target_obj=target_object_str)

                # Create a lightweight dummy server/placeholder proxy locally.
                dummy_proxy_server = ProxyServer(bufsize=self._bufsize)
                # mark running so Proxy.__init__ won't complain
                dummy_proxy_server._running = True
                dummy_proxy_server._proxy_chaining_max_level = max_level

                dummy_target_object = object()
                proxy = Proxy(
                    proxy_server=dummy_proxy_server,
                    idx=proxy_id,
                    target_obj=dummy_target_object,
                    shared_memory=smm,
                )
                proxy.target_obj_str = target_object_str
                proxy._chain_level = chain_level + 1
                proxy._proxy_chaining_max_level = max_level

                return proxy

            # Backwards compat: string-based proxy
            if isinstance(value, str) and value.startswith(self._proxy_prefix):
                target_object_str = value.split(self._proxy_prefix, 1)[-1]

                # Use default max level stored on this Proxy instance
                max_level = getattr(self, "_proxy_chaining_max_level", 7)
                chain_level = getattr(self, "_chain_level", 0)

                if chain_level + 1 > max_level:
                    raise LimitedProxyChaining(max_level, target_obj=target_object_str)

                dummy_proxy_server = ProxyServer(bufsize=self._bufsize)
                dummy_proxy_server._running = True

                dummy_target_object = object()
                proxy = Proxy(
                    proxy_server=dummy_proxy_server,
                    idx=target_object_id,
                    target_obj=dummy_target_object,
                    shared_memory=smm,
                )
                proxy.target_obj_str = target_object_str
                proxy._chain_level = chain_level + 1
                proxy._proxy_chaining_max_level = max_level

                return proxy

            elif isinstance(value, str) and value.startswith(self._callable_prefix):
                # This is a method descriptor; it's not a proxy object, so reset chain level per requirement
                method = value.split(self._callable_prefix, 1)[-1]

                # Reset chain level on this proxy as we've received a real (callable descriptor) response
                try:
                    self._chain_level = 0
                except Exception:
                    # best-effort; ignore if attribute not present
                    pass

                def execute_on_target(*args, **kwargs):
                    request_frame = Frame(opcode=ProxyOpCode.EXECUTE, payload=[target_object_id, method, args, kwargs])
                    return self.get_response(request_frame)

                return execute_on_target

            # At this point it's a real/serializable value: reset chain level per user's request.
            try:
                self._chain_level = 0
            except Exception:
                # best-effort; ignore if attribute not present
                pass

            return value

        else:
            raise ProxyError(f"Unknown response from server: {response_frame}.")

    def close(self):
        """
        Closes the shared memory for the proxy object.
        """
        try:
            smm = self.get_shared_memory()
            smm.close()
            smm.unlink()
        except FileNotFoundError:
            # Shared memory no longer available
            pass
        except Exception:
            # Be quiet on other cleanup errors
            pass

    def __getattribute__(self, key):
        super_getattr = super().__getattribute__

        if key in type(self)._cls_attrs:
            return super().__getattribute__(key)

        get_response = super_getattr("get_response")
        idx = super_getattr("idx")
        request_frame = Frame(opcode=ProxyOpCode.GET, payload=[idx, key])
        return get_response(request_frame)

    def __setattr__(self, key, value):
        super_getattr = super().__getattribute__

        if key in type(self)._cls_attrs:
            return super().__setattr__(key, value)

        get_response = super_getattr("get_response")
        idx = super_getattr("idx")
        request_frame = Frame(opcode=ProxyOpCode.SET, payload=[idx, key, value])
        return get_response(request_frame)

    def __delattr__(self, key):
        super_getattr = super().__getattribute__

        if key in type(self)._cls_attrs:
            return super().__delattr__(key)

        get_response = super_getattr("get_response")
        idx = super_getattr("idx")
        request_frame = Frame(opcode=ProxyOpCode.EXECUTE, payload=[idx, "__delattr__", (key,), {}])
        return get_response(request_frame)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        try:
            self.close()
        finally:
            return False  # Don't suppress exceptions

    def __del__(self):
        if not self._close_on_delete:
            super_del = getattr(super(), "__del__", None)
            if super_del is not None:
                super_del()
            return

        try:
            # If server is not running, just try local cleanup
            if not getattr(self, "_server_running", False):
                self.close()

            super_getattr = super().__getattribute__
            get_response = super_getattr("get_response")
            idx = super_getattr("idx")
            request_frame = Frame(opcode=ProxyOpCode.EXECUTE, payload=[idx, "__del__", (), {}])

            try:
                return get_response(request_frame)
            except Exception:
                # Failed to do cleanup using the server as a mediator; continue to local cleanup
                pass

            finally:
                self.close()

        finally:
            super_del = getattr(super(), "__del__", None)
            if super_del is not None:
                super_del()
            self.close()

    def __str__(self):
        return f"<[{self.__class__.__name__} {self.target_obj_str}]>"

    __repr__ = __str__


class ProxyServer:
    """
    Server for handling proxy objects.
    """

    _DATA_SIZE_PREFIX_LEN: int = 4

    def __init__(self, bufsize: int):
        self.creator_process = multiprocessing.current_process()
        # map id(target) -> [target_obj, proxy, shared_memory]
        self.proxy_objects: Dict[int, List[Any]] = {}
        self.server_thread: Optional[threading.Thread] = None
        self._running = False
        self._bufsize = bufsize
        self._threaded = False

        # Configuration
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
                        try:
                            _, proxy, shared_memory = data
                            try:
                                request_frame = self.read_frame(shared_memory)
                                if request_frame.opcode in [ProxyOpCode.GET, ProxyOpCode.SET, ProxyOpCode.EXECUTE]:
                                    self.handle_request_frame(shared_memory, request_frame)
                            except EmptyData:
                                # nothing to do
                                pass
                            except DataDecodeError:
                                # Malformed data, surface it
                                raise
                            except Exception:
                                raise
                        except Exception:
                            # If one proxy fails, continue to others rather than killing server
                            raise

                except RuntimeError as e:
                    # Keep compatibility with earlier behavior, but prefer stable iteration
                    if "dictionary changed size" in str(e):
                        continue
                    else:
                        raise

                except Exception:
                    # For now re-raise to surface server errors during development.
                    raise

                time.sleep(0.001)

        if threaded:
            self.server_thread = threading.Thread(target=_run, daemon=True)
            self.server_thread.start()
        else:
            _run()

    def read_frame(self, shared_memory: sm.SharedMemory, timeout: Optional[float] = 0.5) -> Frame:
        """
        Reads a frame from shared memory and returns the parsed Frame.
        """
        # Reuse Proxy implementation for consistent behavior
        dummy = Proxy(proxy_server=None, idx=0, target_obj=object(), shared_memory=shared_memory)
        dummy._bufsize = self._bufsize
        return dummy.read_frame(shared_memory, timeout)

    def write_frame(self, shared_memory: sm.SharedMemory, frame: Frame) -> int:
        """
        Write a frame to the shared memory.
        """
        dummy = Proxy(proxy_server=None, idx=0, target_obj=object(), shared_memory=shared_memory)
        dummy._bufsize = self._bufsize
        return dummy.write_frame(shared_memory, frame)

    def handle_request_frame(self, shared_memory: sm.SharedMemory, frame: Frame):
        """
        Handle a request frame from the client.
        """
        if self._threaded:
            th = threading.Thread(target=self.handle_frame, args=[shared_memory, frame], daemon=True)
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
            with self._lock:
                entry = self.proxy_objects.get(target_object_id, [None, None, None])
            target_object, _, __ = entry

            if not target_object:
                raise ProxyObjectNotFound(f"Proxy target object with ID `{target_object_id}` not found. It may have been deleted or never declared.")

            if frame.opcode == ProxyOpCode.GET:
                _, key = frame.payload
                result = getattr(target_object, key)

            elif frame.opcode == ProxyOpCode.SET:
                _, key, value = frame.payload
                setattr(target_object, key, value)

            elif frame.opcode == ProxyOpCode.EXECUTE:
                # payload: [id, method_name, args, kwargs]
                _, method_name, args, kwargs = frame.payload
                resolved_method = getattr(target_object, method_name)
                result = resolved_method(*args, **kwargs)

        except Exception as e:
            error = e

        def is_serializable(data: Any) -> bool:
            """
            Returns a boolean on whether if the data can be serialized by msgpack.
            Attempt packing to be conservative and robust.
            """
            try:
                # None is serializable by msgpack
                msgpack.packb(data, use_bin_type=True)
                return True
            except Exception:
                return False

        if not error:
            try:
                if callable(result):
                    # This is a method returned as a result
                    if not is_method_of(result, target_object):
                        raise ProxyError(f"Callable returned is not a bound method of the target object (target id={target_object_id}). Independent callables are not allowed for security/stability.")
                    method_name = get_callable_name(result)
                    result = f"{Proxy._callable_prefix}{method_name}"

                if not is_serializable(result) and self._wrap_unserializable_objects:
                    # Create another proxy reference and return a structured proxy descriptor
                    proxy_result = self.create_proxy(result, shared_memory)
                    target_object_id = proxy_result.idx
                    target_object_str = proxy_result.target_obj_str

                    # Prepare structured descriptor so client can validate chain depth & reconstruct proxy
                    result = {
                        "__proxy__": True,
                        "id": target_object_id,
                        "obj": target_object_str,
                        "level": 0,
                        "max_level": self._proxy_chaining_max_level,
                    }

                    # keep the newly created proxy alive long enough to write its descriptor
                    proxy_result._close_on_delete = False
                    # allow Python to cleanup proxy_result after returning descriptor
                    del proxy_result

                # Write response frame
                response_frame = Frame(ProxyOpCode.EXECUTION_RESULT, [target_object_id, result, None])
                self.write_frame(shared_memory, response_frame)
            except Exception as e:
                error = e

        if error:
            # Normalize error for transport
            error_str = f"{error.__class__.__name__}: {error}"
            response_frame = Frame(ProxyOpCode.EXECUTION_RESULT, [target_object_id, None, error_str])
            self.write_frame(shared_memory, response_frame)

    def create_proxy(self, target_object: Any, shared_memory: Optional[sm.SharedMemory] = None) -> Proxy:
        """
        Create a process-safe proxy object.
        """
        super_del = getattr(target_object, "__del__", None)

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
                if super_del is not None:
                    try:
                        super_del()
                    except Exception:
                        pass

        idx = id(target_object)

        with self._lock:
            if idx in self.proxy_objects:
                raise ProxyError("The provided object already exists as a proxy. Please provide a different object or remove the existing proxy first.")

            # Create a shared memory block for the proxy object.
            name = f"shared-memory-{idx}"
            shared_memory = shared_memory or sm.SharedMemory(create=True, size=self._bufsize, name=name)
            proxy = Proxy(self, idx, target_object, shared_memory)
            self.proxy_objects[idx] = [target_object, proxy, shared_memory]

            # Patch the target object's __del__ to perform cleanup, but do so carefully
            try:
                target_object.__del__ = wrapped_del
            except Exception:
                # Some objects may not allow attribute assignment; that's acceptable.
                pass

        return proxy


# Example usage (kept minimal)
class myObject:
    def f(self):
        return "hello from f"

if __name__ == "__main__":
    server = ProxyServer(bufsize=4096)
    server.run()

    obj = myObject()
    obj.a = myObject()

    # Create proxy object
    proxy = server.create_proxy(obj)

    def process_entry(proxy: Proxy):
        with proxy as p:
            # Demonstrates getting nested proxy and invoking a callable
            nested = p.a
            # nested is a Proxy returned by proxy chaining
            print("nested proxy:", nested)
            # call the method
            print("f() ->", nested.f())

            # After invoking a real result, further requests should have chain level reset on the original proxy
            # (the client-side check is internal; this is just a usage example)
            print("p.a (again) ->", p.a)

    p1 = multiprocessing.Process(target=process_entry, args=[proxy])
    p1.start()
    p1.join()