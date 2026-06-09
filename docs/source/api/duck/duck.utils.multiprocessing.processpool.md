# {py:mod}`duck.utils.multiprocessing.processpool`

```{py:module} duck.utils.multiprocessing.processpool
```

```{autodocx-docstring} duck.utils.multiprocessing.processpool
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`ProcessPoolManager <duck.utils.multiprocessing.processpool.ProcessPoolManager>`
  - ```{autodocx-docstring} duck.utils.multiprocessing.processpool.ProcessPoolManager
    :summary:
    ```
````

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`get_or_create_process_manager <duck.utils.multiprocessing.processpool.get_or_create_process_manager>`
  - ```{autodocx-docstring} duck.utils.multiprocessing.processpool.get_or_create_process_manager
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`REGISTRY <duck.utils.multiprocessing.processpool.REGISTRY>`
  - ```{autodocx-docstring} duck.utils.multiprocessing.processpool.REGISTRY
    :summary:
    ```
````

### API

````{py:exception} ManagerNotFound()
:canonical: duck.utils.multiprocessing.processpool.ManagerNotFound

Bases: {py:obj}`Exception`

```{autodocx-docstring} duck.utils.multiprocessing.processpool.ManagerNotFound
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.utils.multiprocessing.processpool.ManagerNotFound.__init__
```

````

`````{py:class} ProcessPoolManager(creator_process: typing.Optional[multiprocessing.Process] = None)
:canonical: duck.utils.multiprocessing.processpool.ProcessPoolManager

```{autodocx-docstring} duck.utils.multiprocessing.processpool.ProcessPoolManager
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.utils.multiprocessing.processpool.ProcessPoolManager.__init__
```

````{py:attribute} __instances
:canonical: duck.utils.multiprocessing.processpool.ProcessPoolManager.__instances
:value: >
   []

```{autodocx-docstring} duck.utils.multiprocessing.processpool.ProcessPoolManager.__instances
```

````

````{py:method} __repr__()
:canonical: duck.utils.multiprocessing.processpool.ProcessPoolManager.__repr__

````

````{py:method} __str__()
:canonical: duck.utils.multiprocessing.processpool.ProcessPoolManager.__str__

````

````{py:method} _worker_init()
:canonical: duck.utils.multiprocessing.processpool.ProcessPoolManager._worker_init

```{autodocx-docstring} duck.utils.multiprocessing.processpool.ProcessPoolManager._worker_init
```

````

````{py:method} all_instances() -> typing.List[duck.utils.multiprocessing.processpool.ProcessPoolManager]
:canonical: duck.utils.multiprocessing.processpool.ProcessPoolManager.all_instances
:classmethod:

```{autodocx-docstring} duck.utils.multiprocessing.processpool.ProcessPoolManager.all_instances
```

````

````{py:method} get_pool() -> concurrent.futures.ProcessPoolExecutor
:canonical: duck.utils.multiprocessing.processpool.ProcessPoolManager.get_pool

```{autodocx-docstring} duck.utils.multiprocessing.processpool.ProcessPoolManager.get_pool
```

````

````{py:method} registry() -> typing.Dict[int, typing.Dict[typing.Any, duck.utils.multiprocessing.processpool.ProcessPoolManager]]
:canonical: duck.utils.multiprocessing.processpool.ProcessPoolManager.registry
:classmethod:

```{autodocx-docstring} duck.utils.multiprocessing.processpool.ProcessPoolManager.registry
```

````

````{py:method} start(max_workers: int, task_type: typing.Optional[str] = None, daemon: bool = False, process_name_prefix: typing.Optional[str] = None, mp_context: typing.Optional[multiprocessing.context.BaseContext] = None)
:canonical: duck.utils.multiprocessing.processpool.ProcessPoolManager.start

```{autodocx-docstring} duck.utils.multiprocessing.processpool.ProcessPoolManager.start
```

````

````{py:method} stop(wait: bool = True)
:canonical: duck.utils.multiprocessing.processpool.ProcessPoolManager.stop

```{autodocx-docstring} duck.utils.multiprocessing.processpool.ProcessPoolManager.stop
```

````

````{py:method} submit_task(task: typing.Callable, *args, task_type: typing.Optional[str] = None, **kwargs) -> concurrent.futures.Future
:canonical: duck.utils.multiprocessing.processpool.ProcessPoolManager.submit_task

```{autodocx-docstring} duck.utils.multiprocessing.processpool.ProcessPoolManager.submit_task
```

````

`````

````{py:data} REGISTRY
:canonical: duck.utils.multiprocessing.processpool.REGISTRY
:type: typing.Dict[int, typing.Dict[typing.Any, duck.utils.multiprocessing.processpool.ProcessPoolManager]]
:value: >
   None

```{autodocx-docstring} duck.utils.multiprocessing.processpool.REGISTRY
```

````

````{py:exception} UnknownTaskError(task_type, pool_task_type)
:canonical: duck.utils.multiprocessing.processpool.UnknownTaskError

Bases: {py:obj}`Exception`

```{autodocx-docstring} duck.utils.multiprocessing.processpool.UnknownTaskError
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.utils.multiprocessing.processpool.UnknownTaskError.__init__
```

````

````{py:function} get_or_create_process_manager(id: typing.Optional[typing.Any] = None, force_create: bool = False, strictly_get: bool = False) -> ProcessPoolManager
:canonical: duck.utils.multiprocessing.processpool.get_or_create_process_manager

```{autodocx-docstring} duck.utils.multiprocessing.processpool.get_or_create_process_manager
```
````
