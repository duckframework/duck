# {py:mod}`duck.utils.asyncio`

```{py:module} duck.utils.asyncio
```

```{autodocx-docstring} duck.utils.asyncio
:allowtitles:
```

## Submodules

```{toctree}
:titlesonly:
:maxdepth: 1

duck.utils.asyncio.eventloop
```

## Package Contents

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`create_task <duck.utils.asyncio.create_task>`
  - ```{autodocx-docstring} duck.utils.asyncio.create_task
    :summary:
    ```
* - {py:obj}`in_async_context <duck.utils.asyncio.in_async_context>`
  - ```{autodocx-docstring} duck.utils.asyncio.in_async_context
    :summary:
    ```
````

### API

````{py:function} create_task(coro: typing.Coroutine, on_complete: typing.Optional[typing.Callable[[asyncio.Task], None]] = None, raise_on_exception: bool = True, ignore_errors: typing.Optional[typing.List[typing.Type[BaseException]]] = None, loop: typing.Optional = None) -> asyncio.Task
:canonical: duck.utils.asyncio.create_task

```{autodocx-docstring} duck.utils.asyncio.create_task
```
````

````{py:function} in_async_context() -> bool
:canonical: duck.utils.asyncio.in_async_context

```{autodocx-docstring} duck.utils.asyncio.in_async_context
```
````
