# {py:mod}`duck.utils.asyncio.eventloop`

```{py:module} duck.utils.asyncio.eventloop
```

```{autodocx-docstring} duck.utils.asyncio.eventloop
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`AsyncioLoopManager <duck.utils.asyncio.eventloop.AsyncioLoopManager>`
  - ```{autodocx-docstring} duck.utils.asyncio.eventloop.AsyncioLoopManager
    :summary:
    ```
````

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`get_or_create_loop_manager <duck.utils.asyncio.eventloop.get_or_create_loop_manager>`
  - ```{autodocx-docstring} duck.utils.asyncio.eventloop.get_or_create_loop_manager
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`REGISTRY <duck.utils.asyncio.eventloop.REGISTRY>`
  - ```{autodocx-docstring} duck.utils.asyncio.eventloop.REGISTRY
    :summary:
    ```
````

### API

`````{py:class} AsyncioLoopManager(creator_thread: typing.Optional[threading.Thread] = None)
:canonical: duck.utils.asyncio.eventloop.AsyncioLoopManager

```{autodocx-docstring} duck.utils.asyncio.eventloop.AsyncioLoopManager
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.utils.asyncio.eventloop.AsyncioLoopManager.__init__
```

````{py:attribute} __instances
:canonical: duck.utils.asyncio.eventloop.AsyncioLoopManager.__instances
:value: >
   []

```{autodocx-docstring} duck.utils.asyncio.eventloop.AsyncioLoopManager.__instances
```

````

````{py:method} __repr__()
:canonical: duck.utils.asyncio.eventloop.AsyncioLoopManager.__repr__

````

````{py:method} __str__()
:canonical: duck.utils.asyncio.eventloop.AsyncioLoopManager.__str__

````

````{py:method} all_instances() -> typing.List[duck.utils.asyncio.eventloop.AsyncioLoopManager]
:canonical: duck.utils.asyncio.eventloop.AsyncioLoopManager.all_instances
:classmethod:

```{autodocx-docstring} duck.utils.asyncio.eventloop.AsyncioLoopManager.all_instances
```

````

````{py:method} get_event_loop() -> asyncio.AbstractEventLoop
:canonical: duck.utils.asyncio.eventloop.AsyncioLoopManager.get_event_loop

```{autodocx-docstring} duck.utils.asyncio.eventloop.AsyncioLoopManager.get_event_loop
```

````

````{py:method} registry() -> typing.Dict[int, typing.Dict[typing.Any, duck.utils.asyncio.eventloop.AsyncioLoopManager]]
:canonical: duck.utils.asyncio.eventloop.AsyncioLoopManager.registry
:classmethod:

```{autodocx-docstring} duck.utils.asyncio.eventloop.AsyncioLoopManager.registry
```

````

````{py:method} start(task_type: typing.Optional[str] = None)
:canonical: duck.utils.asyncio.eventloop.AsyncioLoopManager.start

```{autodocx-docstring} duck.utils.asyncio.eventloop.AsyncioLoopManager.start
```

````

````{py:method} stop()
:canonical: duck.utils.asyncio.eventloop.AsyncioLoopManager.stop

```{autodocx-docstring} duck.utils.asyncio.eventloop.AsyncioLoopManager.stop
```

````

````{py:method} submit_task(coro: typing.Coroutine, return_sync_future: bool = False, task_type: typing.Optional[str] = None) -> typing.Union[duck.utils.threading.SyncFuture, asyncio.Future]
:canonical: duck.utils.asyncio.eventloop.AsyncioLoopManager.submit_task

```{autodocx-docstring} duck.utils.asyncio.eventloop.AsyncioLoopManager.submit_task
```

````

`````

````{py:exception} ManagerNotFound()
:canonical: duck.utils.asyncio.eventloop.ManagerNotFound

Bases: {py:obj}`Exception`

```{autodocx-docstring} duck.utils.asyncio.eventloop.ManagerNotFound
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.utils.asyncio.eventloop.ManagerNotFound.__init__
```

````

````{py:data} REGISTRY
:canonical: duck.utils.asyncio.eventloop.REGISTRY
:value: >
   None

```{autodocx-docstring} duck.utils.asyncio.eventloop.REGISTRY
```

````

````{py:exception} UnknownAsyncTaskError(given_type, expected_type)
:canonical: duck.utils.asyncio.eventloop.UnknownAsyncTaskError

Bases: {py:obj}`Exception`

```{autodocx-docstring} duck.utils.asyncio.eventloop.UnknownAsyncTaskError
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.utils.asyncio.eventloop.UnknownAsyncTaskError.__init__
```

````

````{py:function} get_or_create_loop_manager(id: typing.Optional[typing.Any] = None, force_create: bool = False, strictly_get: bool = False) -> AsyncioLoopManager
:canonical: duck.utils.asyncio.eventloop.get_or_create_loop_manager

```{autodocx-docstring} duck.utils.asyncio.eventloop.get_or_create_loop_manager
```
````
