# {py:mod}`duck.contrib.asyncio`

```{py:module} duck.contrib.asyncio
```

```{autodocx-docstring} duck.contrib.asyncio
:allowtitles:
```

## Module Contents

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`get_available_event_loop <duck.contrib.asyncio.get_available_event_loop>`
  - ```{autodocx-docstring} duck.contrib.asyncio.get_available_event_loop
    :summary:
    ```
* - {py:obj}`run_on_available_loop <duck.contrib.asyncio.run_on_available_loop>`
  - ```{autodocx-docstring} duck.contrib.asyncio.run_on_available_loop
    :summary:
    ```
````

### API

````{py:function} get_available_event_loop() -> asyncio.AbstractEventLoop
:canonical: duck.contrib.asyncio.get_available_event_loop

```{autodocx-docstring} duck.contrib.asyncio.get_available_event_loop
```
````

````{py:function} run_on_available_loop(coro: typing.Coroutine, return_sync_future: bool = False) -> typing.Union[duck.utils.asyncio.eventloop.SyncFuture, asyncio.Future]
:canonical: duck.contrib.asyncio.run_on_available_loop

```{autodocx-docstring} duck.contrib.asyncio.run_on_available_loop
```
````
