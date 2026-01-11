# {py:mod}`duck.contrib.sync.smart_async`

```{py:module} duck.contrib.sync.smart_async
```

```{autodocx-docstring} duck.contrib.sync.smart_async
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`TransactionThread <duck.contrib.sync.smart_async.TransactionThread>`
  - ```{autodocx-docstring} duck.contrib.sync.smart_async.TransactionThread
    :summary:
    ```
* - {py:obj}`TransactionThreadPool <duck.contrib.sync.smart_async.TransactionThreadPool>`
  - ```{autodocx-docstring} duck.contrib.sync.smart_async.TransactionThreadPool
    :summary:
    ```
* - {py:obj}`disable_transaction_context <duck.contrib.sync.smart_async.disable_transaction_context>`
  - ```{autodocx-docstring} duck.contrib.sync.smart_async.disable_transaction_context
    :summary:
    ```
* - {py:obj}`transaction_context <duck.contrib.sync.smart_async.transaction_context>`
  - ```{autodocx-docstring} duck.contrib.sync.smart_async.transaction_context
    :summary:
    ```
````

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`in_transaction_context <duck.contrib.sync.smart_async.in_transaction_context>`
  - ```{autodocx-docstring} duck.contrib.sync.smart_async.in_transaction_context
    :summary:
    ```
* - {py:obj}`is_transactional <duck.contrib.sync.smart_async.is_transactional>`
  - ```{autodocx-docstring} duck.contrib.sync.smart_async.is_transactional
    :summary:
    ```
* - {py:obj}`sync_to_async <duck.contrib.sync.smart_async.sync_to_async>`
  - ```{autodocx-docstring} duck.contrib.sync.smart_async.sync_to_async
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`T <duck.contrib.sync.smart_async.T>`
  - ```{autodocx-docstring} duck.contrib.sync.smart_async.T
    :summary:
    ```
* - {py:obj}`_TRANSACTION_THREAD_POOL <duck.contrib.sync.smart_async._TRANSACTION_THREAD_POOL>`
  - ```{autodocx-docstring} duck.contrib.sync.smart_async._TRANSACTION_THREAD_POOL
    :summary:
    ```
* - {py:obj}`_transaction_context_id_var <duck.contrib.sync.smart_async._transaction_context_id_var>`
  - ```{autodocx-docstring} duck.contrib.sync.smart_async._transaction_context_id_var
    :summary:
    ```
````

### API

````{py:data} T
:canonical: duck.contrib.sync.smart_async.T
:value: >
   'TypeVar(...)'

```{autodocx-docstring} duck.contrib.sync.smart_async.T
```

````

````{py:exception} TaskTookTooLongWarning()
:canonical: duck.contrib.sync.smart_async.TaskTookTooLongWarning

Bases: {py:obj}`UserWarning`

```{autodocx-docstring} duck.contrib.sync.smart_async.TaskTookTooLongWarning
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.contrib.sync.smart_async.TaskTookTooLongWarning.__init__
```

````

`````{py:class} TransactionThread(context_id=None)
:canonical: duck.contrib.sync.smart_async.TransactionThread

Bases: {py:obj}`threading.Thread`

```{autodocx-docstring} duck.contrib.sync.smart_async.TransactionThread
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.contrib.sync.smart_async.TransactionThread.__init__
```

````{py:method} __repr__()
:canonical: duck.contrib.sync.smart_async.TransactionThread.__repr__

````

````{py:method} __str__()
:canonical: duck.contrib.sync.smart_async.TransactionThread.__str__

````

````{py:method} current_task_executing() -> typing.Optional[typing.Any]
:canonical: duck.contrib.sync.smart_async.TransactionThread.current_task_executing

```{autodocx-docstring} duck.contrib.sync.smart_async.TransactionThread.current_task_executing
```

````

````{py:method} is_free() -> bool
:canonical: duck.contrib.sync.smart_async.TransactionThread.is_free

```{autodocx-docstring} duck.contrib.sync.smart_async.TransactionThread.is_free
```

````

````{py:method} run()
:canonical: duck.contrib.sync.smart_async.TransactionThread.run

````

````{py:method} shutdown()
:canonical: duck.contrib.sync.smart_async.TransactionThread.shutdown

```{autodocx-docstring} duck.contrib.sync.smart_async.TransactionThread.shutdown
```

````

````{py:method} submit(func: typing.Callable[..., duck.contrib.sync.smart_async.T], *args, **kwargs) -> asyncio.Future
:canonical: duck.contrib.sync.smart_async.TransactionThread.submit

```{autodocx-docstring} duck.contrib.sync.smart_async.TransactionThread.submit
```

````

`````

`````{py:class} TransactionThreadPool(max_threads: typing.Optional[int] = None, auto_free_general_threads: bool = True, general_threads_free_level: int = 50)
:canonical: duck.contrib.sync.smart_async.TransactionThreadPool

```{autodocx-docstring} duck.contrib.sync.smart_async.TransactionThreadPool
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.contrib.sync.smart_async.TransactionThreadPool.__init__
```

````{py:method} _maybe_free_general_threads(ignore_threads: typing.Optional[typing.List[duck.contrib.sync.smart_async.TransactionThread]] = None) -> None
:canonical: duck.contrib.sync.smart_async.TransactionThreadPool._maybe_free_general_threads

```{autodocx-docstring} duck.contrib.sync.smart_async.TransactionThreadPool._maybe_free_general_threads
```

````

````{py:method} get_thread(context_id: typing.Optional[str] = None) -> duck.contrib.sync.smart_async.TransactionThread
:canonical: duck.contrib.sync.smart_async.TransactionThreadPool.get_thread

```{autodocx-docstring} duck.contrib.sync.smart_async.TransactionThreadPool.get_thread
```

````

````{py:method} shutdown(wait: bool = True)
:canonical: duck.contrib.sync.smart_async.TransactionThreadPool.shutdown

```{autodocx-docstring} duck.contrib.sync.smart_async.TransactionThreadPool.shutdown
```

````

````{py:method} submit(func: typing.Callable[..., duck.contrib.sync.smart_async.T], *args, context_id=None, **kwargs) -> asyncio.Future
:canonical: duck.contrib.sync.smart_async.TransactionThreadPool.submit

```{autodocx-docstring} duck.contrib.sync.smart_async.TransactionThreadPool.submit
```

````

`````

````{py:data} _TRANSACTION_THREAD_POOL
:canonical: duck.contrib.sync.smart_async._TRANSACTION_THREAD_POOL
:value: >
   'TransactionThreadPool(...)'

```{autodocx-docstring} duck.contrib.sync.smart_async._TRANSACTION_THREAD_POOL
```

````

````{py:data} _transaction_context_id_var
:canonical: duck.contrib.sync.smart_async._transaction_context_id_var
:value: >
   'ContextVar(...)'

```{autodocx-docstring} duck.contrib.sync.smart_async._transaction_context_id_var
```

````

`````{py:class} disable_transaction_context
:canonical: duck.contrib.sync.smart_async.disable_transaction_context

```{autodocx-docstring} duck.contrib.sync.smart_async.disable_transaction_context
```

````{py:method} __enter__()
:canonical: duck.contrib.sync.smart_async.disable_transaction_context.__enter__

```{autodocx-docstring} duck.contrib.sync.smart_async.disable_transaction_context.__enter__
```

````

````{py:method} __exit__(exc_type, exc_val, exc_tb)
:canonical: duck.contrib.sync.smart_async.disable_transaction_context.__exit__

```{autodocx-docstring} duck.contrib.sync.smart_async.disable_transaction_context.__exit__
```

````

`````

````{py:function} in_transaction_context() -> typing.Optional[str]
:canonical: duck.contrib.sync.smart_async.in_transaction_context

```{autodocx-docstring} duck.contrib.sync.smart_async.in_transaction_context
```
````

````{py:function} is_transactional(func: typing.Callable) -> bool
:canonical: duck.contrib.sync.smart_async.is_transactional

```{autodocx-docstring} duck.contrib.sync.smart_async.is_transactional
```
````

````{py:function} sync_to_async(func: typing.Callable[..., duck.contrib.sync.smart_async.T], *outer_args, **outer_kwargs) -> typing.Callable[..., asyncio.Future]
:canonical: duck.contrib.sync.smart_async.sync_to_async

```{autodocx-docstring} duck.contrib.sync.smart_async.sync_to_async
```
````

`````{py:class} transaction_context
:canonical: duck.contrib.sync.smart_async.transaction_context

```{autodocx-docstring} duck.contrib.sync.smart_async.transaction_context
```

````{py:method} __enter__()
:canonical: duck.contrib.sync.smart_async.transaction_context.__enter__

```{autodocx-docstring} duck.contrib.sync.smart_async.transaction_context.__enter__
```

````

````{py:method} __exit__(exc_type, exc_val, exc_tb)
:canonical: duck.contrib.sync.smart_async.transaction_context.__exit__

```{autodocx-docstring} duck.contrib.sync.smart_async.transaction_context.__exit__
```

````

`````
