# {py:mod}`duck.utils.multiprocessing.proxy`

```{py:module} duck.utils.multiprocessing.proxy
```

```{autodocx-docstring} duck.utils.multiprocessing.proxy
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`Frame <duck.utils.multiprocessing.proxy.Frame>`
  - ```{autodocx-docstring} duck.utils.multiprocessing.proxy.Frame
    :summary:
    ```
* - {py:obj}`Proxy <duck.utils.multiprocessing.proxy.Proxy>`
  - ```{autodocx-docstring} duck.utils.multiprocessing.proxy.Proxy
    :summary:
    ```
* - {py:obj}`ProxyOpCode <duck.utils.multiprocessing.proxy.ProxyOpCode>`
  - ```{autodocx-docstring} duck.utils.multiprocessing.proxy.ProxyOpCode
    :summary:
    ```
* - {py:obj}`ProxyServer <duck.utils.multiprocessing.proxy.ProxyServer>`
  - ```{autodocx-docstring} duck.utils.multiprocessing.proxy.ProxyServer
    :summary:
    ```
````

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`get_callable_name <duck.utils.multiprocessing.proxy.get_callable_name>`
  - ```{autodocx-docstring} duck.utils.multiprocessing.proxy.get_callable_name
    :summary:
    ```
* - {py:obj}`is_method_of <duck.utils.multiprocessing.proxy.is_method_of>`
  - ```{autodocx-docstring} duck.utils.multiprocessing.proxy.is_method_of
    :summary:
    ```
````

### API

````{py:exception} DataDecodeError()
:canonical: duck.utils.multiprocessing.proxy.DataDecodeError

Bases: {py:obj}`duck.utils.multiprocessing.proxy.ProxyError`

```{autodocx-docstring} duck.utils.multiprocessing.proxy.DataDecodeError
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.utils.multiprocessing.proxy.DataDecodeError.__init__
```

````

````{py:exception} DataEncodeError()
:canonical: duck.utils.multiprocessing.proxy.DataEncodeError

Bases: {py:obj}`duck.utils.multiprocessing.proxy.ProxyError`

```{autodocx-docstring} duck.utils.multiprocessing.proxy.DataEncodeError
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.utils.multiprocessing.proxy.DataEncodeError.__init__
```

````

````{py:exception} DataTooBigError()
:canonical: duck.utils.multiprocessing.proxy.DataTooBigError

Bases: {py:obj}`duck.utils.multiprocessing.proxy.ProxyError`

```{autodocx-docstring} duck.utils.multiprocessing.proxy.DataTooBigError
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.utils.multiprocessing.proxy.DataTooBigError.__init__
```

````

````{py:exception} EmptyData()
:canonical: duck.utils.multiprocessing.proxy.EmptyData

Bases: {py:obj}`duck.utils.multiprocessing.proxy.ProxyError`

```{autodocx-docstring} duck.utils.multiprocessing.proxy.EmptyData
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.utils.multiprocessing.proxy.EmptyData.__init__
```

````

`````{py:class} Frame(opcode: int, payload: typing.List[typing.Any])
:canonical: duck.utils.multiprocessing.proxy.Frame

```{autodocx-docstring} duck.utils.multiprocessing.proxy.Frame
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.utils.multiprocessing.proxy.Frame.__init__
```

````{py:method} __repr__()
:canonical: duck.utils.multiprocessing.proxy.Frame.__repr__

````

````{py:attribute} __slots__
:canonical: duck.utils.multiprocessing.proxy.Frame.__slots__
:value: >
   ('opcode', 'payload')

```{autodocx-docstring} duck.utils.multiprocessing.proxy.Frame.__slots__
```

````

````{py:attribute} __str__
:canonical: duck.utils.multiprocessing.proxy.Frame.__str__
:value: >
   None

```{autodocx-docstring} duck.utils.multiprocessing.proxy.Frame.__str__
```

````

````{py:method} parse(data: bytes) -> duck.utils.multiprocessing.proxy.Frame
:canonical: duck.utils.multiprocessing.proxy.Frame.parse
:classmethod:

```{autodocx-docstring} duck.utils.multiprocessing.proxy.Frame.parse
```

````

`````

````{py:exception} LimitedProxyChaining(max_level: int, target_obj: typing.Optional[str] = None)
:canonical: duck.utils.multiprocessing.proxy.LimitedProxyChaining

Bases: {py:obj}`duck.utils.multiprocessing.proxy.ProxyError`

```{autodocx-docstring} duck.utils.multiprocessing.proxy.LimitedProxyChaining
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.utils.multiprocessing.proxy.LimitedProxyChaining.__init__
```

````

`````{py:class} Proxy(proxy_server: duck.utils.multiprocessing.proxy.ProxyServer, idx: int, target_obj: typing.Any, shared_memory: multiprocessing.shared_memory.SharedMemory)
:canonical: duck.utils.multiprocessing.proxy.Proxy

```{autodocx-docstring} duck.utils.multiprocessing.proxy.Proxy
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.utils.multiprocessing.proxy.Proxy.__init__
```

````{py:attribute} _DATA_SIZE_PREFIX_LEN
:canonical: duck.utils.multiprocessing.proxy.Proxy._DATA_SIZE_PREFIX_LEN
:type: int
:value: >
   4

```{autodocx-docstring} duck.utils.multiprocessing.proxy.Proxy._DATA_SIZE_PREFIX_LEN
```

````

````{py:method} __del__()
:canonical: duck.utils.multiprocessing.proxy.Proxy.__del__

```{autodocx-docstring} duck.utils.multiprocessing.proxy.Proxy.__del__
```

````

````{py:method} __delattr__(key)
:canonical: duck.utils.multiprocessing.proxy.Proxy.__delattr__

````

````{py:method} __enter__()
:canonical: duck.utils.multiprocessing.proxy.Proxy.__enter__

```{autodocx-docstring} duck.utils.multiprocessing.proxy.Proxy.__enter__
```

````

````{py:method} __exit__(exc_type, exc, exc_tb)
:canonical: duck.utils.multiprocessing.proxy.Proxy.__exit__

```{autodocx-docstring} duck.utils.multiprocessing.proxy.Proxy.__exit__
```

````

````{py:method} __getattribute__(key)
:canonical: duck.utils.multiprocessing.proxy.Proxy.__getattribute__

````

````{py:method} __getitem__(key)
:canonical: duck.utils.multiprocessing.proxy.Proxy.__getitem__

```{autodocx-docstring} duck.utils.multiprocessing.proxy.Proxy.__getitem__
```

````

````{py:method} __repr__()
:canonical: duck.utils.multiprocessing.proxy.Proxy.__repr__

````

````{py:method} __setattr__(key, value)
:canonical: duck.utils.multiprocessing.proxy.Proxy.__setattr__

````

````{py:method} __setitem__(key, value)
:canonical: duck.utils.multiprocessing.proxy.Proxy.__setitem__

```{autodocx-docstring} duck.utils.multiprocessing.proxy.Proxy.__setitem__
```

````

````{py:attribute} __slots__
:canonical: duck.utils.multiprocessing.proxy.Proxy.__slots__
:value: >
   None

```{autodocx-docstring} duck.utils.multiprocessing.proxy.Proxy.__slots__
```

````

````{py:attribute} __str__
:canonical: duck.utils.multiprocessing.proxy.Proxy.__str__
:value: >
   None

```{autodocx-docstring} duck.utils.multiprocessing.proxy.Proxy.__str__
```

````

````{py:attribute} _callable_prefix
:canonical: duck.utils.multiprocessing.proxy.Proxy._callable_prefix
:value: >
   '<callable>-'

```{autodocx-docstring} duck.utils.multiprocessing.proxy.Proxy._callable_prefix
```

````

````{py:attribute} _cls_attrs
:canonical: duck.utils.multiprocessing.proxy.Proxy._cls_attrs
:value: >
   None

```{autodocx-docstring} duck.utils.multiprocessing.proxy.Proxy._cls_attrs
```

````

````{py:attribute} _proxy_prefix
:canonical: duck.utils.multiprocessing.proxy.Proxy._proxy_prefix
:value: >
   '<proxy>-'

```{autodocx-docstring} duck.utils.multiprocessing.proxy.Proxy._proxy_prefix
```

````

````{py:method} close()
:canonical: duck.utils.multiprocessing.proxy.Proxy.close

```{autodocx-docstring} duck.utils.multiprocessing.proxy.Proxy.close
```

````

````{py:method} get_response(frame: duck.utils.multiprocessing.proxy.Frame, timeout: typing.Optional[float] = None) -> typing.Union[typing.Any, duck.utils.multiprocessing.proxy.Proxy, typing.Callable]
:canonical: duck.utils.multiprocessing.proxy.Proxy.get_response

```{autodocx-docstring} duck.utils.multiprocessing.proxy.Proxy.get_response
```

````

````{py:method} get_shared_memory() -> multiprocessing.shared_memory.SharedMemory
:canonical: duck.utils.multiprocessing.proxy.Proxy.get_shared_memory

```{autodocx-docstring} duck.utils.multiprocessing.proxy.Proxy.get_shared_memory
```

````

````{py:method} read_frame(shared_memory: multiprocessing.shared_memory.SharedMemory, timeout: typing.Optional[float] = 0.5) -> duck.utils.multiprocessing.proxy.Frame
:canonical: duck.utils.multiprocessing.proxy.Proxy.read_frame

```{autodocx-docstring} duck.utils.multiprocessing.proxy.Proxy.read_frame
```

````

````{py:method} write_frame(shared_memory: multiprocessing.shared_memory.SharedMemory, frame: duck.utils.multiprocessing.proxy.Frame) -> int
:canonical: duck.utils.multiprocessing.proxy.Proxy.write_frame

```{autodocx-docstring} duck.utils.multiprocessing.proxy.Proxy.write_frame
```

````

`````

````{py:exception} ProxyError()
:canonical: duck.utils.multiprocessing.proxy.ProxyError

Bases: {py:obj}`Exception`

```{autodocx-docstring} duck.utils.multiprocessing.proxy.ProxyError
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.utils.multiprocessing.proxy.ProxyError.__init__
```

````

````{py:exception} ProxyObjectNotFound()
:canonical: duck.utils.multiprocessing.proxy.ProxyObjectNotFound

Bases: {py:obj}`duck.utils.multiprocessing.proxy.ProxyError`

```{autodocx-docstring} duck.utils.multiprocessing.proxy.ProxyObjectNotFound
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.utils.multiprocessing.proxy.ProxyObjectNotFound.__init__
```

````

`````{py:class} ProxyOpCode()
:canonical: duck.utils.multiprocessing.proxy.ProxyOpCode

Bases: {py:obj}`enum.IntEnum`

```{autodocx-docstring} duck.utils.multiprocessing.proxy.ProxyOpCode
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.utils.multiprocessing.proxy.ProxyOpCode.__init__
```

````{py:attribute} EXECUTE
:canonical: duck.utils.multiprocessing.proxy.ProxyOpCode.EXECUTE
:value: >
   2

```{autodocx-docstring} duck.utils.multiprocessing.proxy.ProxyOpCode.EXECUTE
```

````

````{py:attribute} EXECUTION_RESULT
:canonical: duck.utils.multiprocessing.proxy.ProxyOpCode.EXECUTION_RESULT
:value: >
   None

```{autodocx-docstring} duck.utils.multiprocessing.proxy.ProxyOpCode.EXECUTION_RESULT
```

````

````{py:attribute} GET
:canonical: duck.utils.multiprocessing.proxy.ProxyOpCode.GET
:value: >
   0

```{autodocx-docstring} duck.utils.multiprocessing.proxy.ProxyOpCode.GET
```

````

````{py:attribute} RESPONSE_PENDING
:canonical: duck.utils.multiprocessing.proxy.ProxyOpCode.RESPONSE_PENDING
:value: >
   None

```{autodocx-docstring} duck.utils.multiprocessing.proxy.ProxyOpCode.RESPONSE_PENDING
```

````

````{py:attribute} SET
:canonical: duck.utils.multiprocessing.proxy.ProxyOpCode.SET
:value: >
   1

```{autodocx-docstring} duck.utils.multiprocessing.proxy.ProxyOpCode.SET
```

````

`````

`````{py:class} ProxyServer(bufsize: int)
:canonical: duck.utils.multiprocessing.proxy.ProxyServer

```{autodocx-docstring} duck.utils.multiprocessing.proxy.ProxyServer
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.utils.multiprocessing.proxy.ProxyServer.__init__
```

````{py:attribute} _DATA_SIZE_PREFIX_LEN
:canonical: duck.utils.multiprocessing.proxy.ProxyServer._DATA_SIZE_PREFIX_LEN
:type: int
:value: >
   4

```{autodocx-docstring} duck.utils.multiprocessing.proxy.ProxyServer._DATA_SIZE_PREFIX_LEN
```

````

````{py:method} create_proxy(target_object: typing.Any, shared_memory: typing.Optional[multiprocessing.shared_memory.SharedMemory] = None) -> duck.utils.multiprocessing.proxy.Proxy
:canonical: duck.utils.multiprocessing.proxy.ProxyServer.create_proxy

```{autodocx-docstring} duck.utils.multiprocessing.proxy.ProxyServer.create_proxy
```

````

````{py:method} handle_frame(shared_memory: multiprocessing.shared_memory.SharedMemory, frame: duck.utils.multiprocessing.proxy.Frame)
:canonical: duck.utils.multiprocessing.proxy.ProxyServer.handle_frame

```{autodocx-docstring} duck.utils.multiprocessing.proxy.ProxyServer.handle_frame
```

````

````{py:method} handle_request_frame(shared_memory: multiprocessing.shared_memory.SharedMemory, frame: duck.utils.multiprocessing.proxy.Frame)
:canonical: duck.utils.multiprocessing.proxy.ProxyServer.handle_request_frame

```{autodocx-docstring} duck.utils.multiprocessing.proxy.ProxyServer.handle_request_frame
```

````

````{py:method} read_frame(shared_memory: multiprocessing.shared_memory.SharedMemory, timeout: typing.Optional[float] = 0.5) -> duck.utils.multiprocessing.proxy.Frame
:canonical: duck.utils.multiprocessing.proxy.ProxyServer.read_frame

```{autodocx-docstring} duck.utils.multiprocessing.proxy.ProxyServer.read_frame
```

````

````{py:method} run(threaded: bool = True)
:canonical: duck.utils.multiprocessing.proxy.ProxyServer.run

```{autodocx-docstring} duck.utils.multiprocessing.proxy.ProxyServer.run
```

````

````{py:property} running
:canonical: duck.utils.multiprocessing.proxy.ProxyServer.running
:type: bool

```{autodocx-docstring} duck.utils.multiprocessing.proxy.ProxyServer.running
```

````

````{py:method} write_frame(shared_memory: multiprocessing.shared_memory.SharedMemory, frame: duck.utils.multiprocessing.proxy.Frame) -> int
:canonical: duck.utils.multiprocessing.proxy.ProxyServer.write_frame

```{autodocx-docstring} duck.utils.multiprocessing.proxy.ProxyServer.write_frame
```

````

`````

````{py:function} get_callable_name(fn)
:canonical: duck.utils.multiprocessing.proxy.get_callable_name

```{autodocx-docstring} duck.utils.multiprocessing.proxy.get_callable_name
```
````

````{py:function} is_method_of(callable_obj, obj)
:canonical: duck.utils.multiprocessing.proxy.is_method_of

```{autodocx-docstring} duck.utils.multiprocessing.proxy.is_method_of
```
````
