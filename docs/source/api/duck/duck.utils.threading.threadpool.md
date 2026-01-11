# {py:mod}`duck.utils.threading.threadpool`

```{py:module} duck.utils.threading.threadpool
```

```{autodocx-docstring} duck.utils.threading.threadpool
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`ThreadPoolManager <duck.utils.threading.threadpool.ThreadPoolManager>`
  - ```{autodocx-docstring} duck.utils.threading.threadpool.ThreadPoolManager
    :summary:
    ```
````

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`get_or_create_thread_manager <duck.utils.threading.threadpool.get_or_create_thread_manager>`
  - ```{autodocx-docstring} duck.utils.threading.threadpool.get_or_create_thread_manager
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`REGISTRY <duck.utils.threading.threadpool.REGISTRY>`
  - ```{autodocx-docstring} duck.utils.threading.threadpool.REGISTRY
    :summary:
    ```
````

### API

````{py:exception} ManagerNotFound()
:canonical: duck.utils.threading.threadpool.ManagerNotFound

Bases: {py:obj}`Exception`

```{autodocx-docstring} duck.utils.threading.threadpool.ManagerNotFound
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.utils.threading.threadpool.ManagerNotFound.__init__
```

````

````{py:data} REGISTRY
:canonical: duck.utils.threading.threadpool.REGISTRY
:value: >
   None

```{autodocx-docstring} duck.utils.threading.threadpool.REGISTRY
```

````

`````{py:class} ThreadPoolManager(creator_thread: typing.Optional[threading.Thread] = None)
:canonical: duck.utils.threading.threadpool.ThreadPoolManager

```{autodocx-docstring} duck.utils.threading.threadpool.ThreadPoolManager
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.utils.threading.threadpool.ThreadPoolManager.__init__
```

````{py:attribute} __instances
:canonical: duck.utils.threading.threadpool.ThreadPoolManager.__instances
:value: >
   []

```{autodocx-docstring} duck.utils.threading.threadpool.ThreadPoolManager.__instances
```

````

````{py:method} __repr__()
:canonical: duck.utils.threading.threadpool.ThreadPoolManager.__repr__

````

````{py:method} __str__()
:canonical: duck.utils.threading.threadpool.ThreadPoolManager.__str__

````

````{py:method} _worker_init()
:canonical: duck.utils.threading.threadpool.ThreadPoolManager._worker_init

```{autodocx-docstring} duck.utils.threading.threadpool.ThreadPoolManager._worker_init
```

````

````{py:method} all_instances() -> typing.List[duck.utils.threading.threadpool.ThreadPoolManager]
:canonical: duck.utils.threading.threadpool.ThreadPoolManager.all_instances
:classmethod:

```{autodocx-docstring} duck.utils.threading.threadpool.ThreadPoolManager.all_instances
```

````

````{py:method} get_pool() -> concurrent.futures.ThreadPoolExecutor
:canonical: duck.utils.threading.threadpool.ThreadPoolManager.get_pool

```{autodocx-docstring} duck.utils.threading.threadpool.ThreadPoolManager.get_pool
```

````

````{py:method} registry() -> typing.Dict[int, typing.Dict[typing.Any, duck.utils.threading.threadpool.ThreadPoolManager]]
:canonical: duck.utils.threading.threadpool.ThreadPoolManager.registry
:classmethod:

```{autodocx-docstring} duck.utils.threading.threadpool.ThreadPoolManager.registry
```

````

````{py:method} start(max_workers: int, task_type: typing.Optional[str] = None, daemon: bool = False, thread_name_prefix: typing.Optional[str] = None)
:canonical: duck.utils.threading.threadpool.ThreadPoolManager.start

```{autodocx-docstring} duck.utils.threading.threadpool.ThreadPoolManager.start
```

````

````{py:method} stop(wait: bool = True)
:canonical: duck.utils.threading.threadpool.ThreadPoolManager.stop

```{autodocx-docstring} duck.utils.threading.threadpool.ThreadPoolManager.stop
```

````

````{py:method} submit_task(task: typing.Callable, task_type: typing.Optional[str] = None, log_exception: bool = True) -> concurrent.futures.Future
:canonical: duck.utils.threading.threadpool.ThreadPoolManager.submit_task

```{autodocx-docstring} duck.utils.threading.threadpool.ThreadPoolManager.submit_task
```

````

`````

````{py:exception} UnknownTaskError(task_type, pool_task_type)
:canonical: duck.utils.threading.threadpool.UnknownTaskError

Bases: {py:obj}`Exception`

```{autodocx-docstring} duck.utils.threading.threadpool.UnknownTaskError
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.utils.threading.threadpool.UnknownTaskError.__init__
```

````

````{py:function} get_or_create_thread_manager(id: typing.Optional[typing.Any] = None, force_create: bool = False, strictly_get: bool = False) -> ThreadPoolManager
:canonical: duck.utils.threading.threadpool.get_or_create_thread_manager

```{autodocx-docstring} duck.utils.threading.threadpool.get_or_create_thread_manager
```
````
