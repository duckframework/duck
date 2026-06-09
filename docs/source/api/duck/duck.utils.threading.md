# {py:mod}`duck.utils.threading`

```{py:module} duck.utils.threading
```

```{autodocx-docstring} duck.utils.threading
:allowtitles:
```

## Submodules

```{toctree}
:titlesonly:
:maxdepth: 1

duck.utils.threading.patch
duck.utils.threading.thread_manager
duck.utils.threading.threadpool
```

## Package Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`SyncFuture <duck.utils.threading.SyncFuture>`
  - ```{autodocx-docstring} duck.utils.threading.SyncFuture
    :summary:
    ```
````

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`async_to_sync_future <duck.utils.threading.async_to_sync_future>`
  - ```{autodocx-docstring} duck.utils.threading.async_to_sync_future
    :summary:
    ```
* - {py:obj}`get_max_workers <duck.utils.threading.get_max_workers>`
  - ```{autodocx-docstring} duck.utils.threading.get_max_workers
    :summary:
    ```
````

### API

`````{py:class} SyncFuture()
:canonical: duck.utils.threading.SyncFuture

```{autodocx-docstring} duck.utils.threading.SyncFuture
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.utils.threading.SyncFuture.__init__
```

````{py:method} exception() -> typing.Optional[Exception]
:canonical: duck.utils.threading.SyncFuture.exception

```{autodocx-docstring} duck.utils.threading.SyncFuture.exception
```

````

````{py:method} result()
:canonical: duck.utils.threading.SyncFuture.result

```{autodocx-docstring} duck.utils.threading.SyncFuture.result
```

````

````{py:method} set_exception(exception)
:canonical: duck.utils.threading.SyncFuture.set_exception

```{autodocx-docstring} duck.utils.threading.SyncFuture.set_exception
```

````

````{py:method} set_result(value)
:canonical: duck.utils.threading.SyncFuture.set_result

```{autodocx-docstring} duck.utils.threading.SyncFuture.set_result
```

````

`````

````{py:function} async_to_sync_future(async_future: asyncio.Future) -> SyncFuture
:canonical: duck.utils.threading.async_to_sync_future

```{autodocx-docstring} duck.utils.threading.async_to_sync_future
```
````

````{py:function} get_max_workers() -> int
:canonical: duck.utils.threading.get_max_workers

```{autodocx-docstring} duck.utils.threading.get_max_workers
```
````
