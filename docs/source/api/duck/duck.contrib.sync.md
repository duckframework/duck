# {py:mod}`duck.contrib.sync`

```{py:module} duck.contrib.sync
```

```{autodocx-docstring} duck.contrib.sync
:allowtitles:
```

## Submodules

```{toctree}
:titlesonly:
:maxdepth: 1

duck.contrib.sync.smart_async
```

## Package Contents

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`async_to_sync <duck.contrib.sync.async_to_sync>`
  - ```{autodocx-docstring} duck.contrib.sync.async_to_sync
    :summary:
    ```
* - {py:obj}`convert_to_async_if_needed <duck.contrib.sync.convert_to_async_if_needed>`
  - ```{autodocx-docstring} duck.contrib.sync.convert_to_async_if_needed
    :summary:
    ```
* - {py:obj}`convert_to_sync_if_needed <duck.contrib.sync.convert_to_sync_if_needed>`
  - ```{autodocx-docstring} duck.contrib.sync.convert_to_sync_if_needed
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`__all__ <duck.contrib.sync.__all__>`
  - ```{autodocx-docstring} duck.contrib.sync.__all__
    :summary:
    ```
* - {py:obj}`ensure_async <duck.contrib.sync.ensure_async>`
  - ```{autodocx-docstring} duck.contrib.sync.ensure_async
    :summary:
    ```
* - {py:obj}`ensure_sync <duck.contrib.sync.ensure_sync>`
  - ```{autodocx-docstring} duck.contrib.sync.ensure_sync
    :summary:
    ```
````

### API

````{py:data} __all__
:canonical: duck.contrib.sync.__all__
:value: >
   ['iscoroutine', 'iscoroutinefunction', 'sync_to_async', 'async_to_sync', 'convert_to_async_if_needed...

```{autodocx-docstring} duck.contrib.sync.__all__
```

````

````{py:function} async_to_sync(func: typing.Callable) -> asgiref.sync.AsyncToSync
:canonical: duck.contrib.sync.async_to_sync

```{autodocx-docstring} duck.contrib.sync.async_to_sync
```
````

````{py:function} convert_to_async_if_needed(func: typing.Callable) -> typing.Callable
:canonical: duck.contrib.sync.convert_to_async_if_needed

```{autodocx-docstring} duck.contrib.sync.convert_to_async_if_needed
```
````

````{py:function} convert_to_sync_if_needed(func: typing.Callable) -> typing.Callable
:canonical: duck.contrib.sync.convert_to_sync_if_needed

```{autodocx-docstring} duck.contrib.sync.convert_to_sync_if_needed
```
````

````{py:data} ensure_async
:canonical: duck.contrib.sync.ensure_async
:value: >
   None

```{autodocx-docstring} duck.contrib.sync.ensure_async
```

````

````{py:data} ensure_sync
:canonical: duck.contrib.sync.ensure_sync
:value: >
   None

```{autodocx-docstring} duck.contrib.sync.ensure_sync
```

````
