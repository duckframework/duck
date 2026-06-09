# {py:mod}`duck.http.core.httpd.task_executor`

```{py:module} duck.http.core.httpd.task_executor
```

```{autodocx-docstring} duck.http.core.httpd.task_executor
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`RequestHandlingExecutor <duck.http.core.httpd.task_executor.RequestHandlingExecutor>`
  - ```{autodocx-docstring} duck.http.core.httpd.task_executor.RequestHandlingExecutor
    :summary:
    ```
````

### API

`````{py:class} RequestHandlingExecutor()
:canonical: duck.http.core.httpd.task_executor.RequestHandlingExecutor

```{autodocx-docstring} duck.http.core.httpd.task_executor.RequestHandlingExecutor
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.http.core.httpd.task_executor.RequestHandlingExecutor.__init__
```

````{py:method} execute(task: typing.Union[typing.Callable, typing.Coroutine])
:canonical: duck.http.core.httpd.task_executor.RequestHandlingExecutor.execute

```{autodocx-docstring} duck.http.core.httpd.task_executor.RequestHandlingExecutor.execute
```

````

````{py:method} on_task_complete(future: typing.Union[concurrent.futures.Future, asyncio.Future])
:canonical: duck.http.core.httpd.task_executor.RequestHandlingExecutor.on_task_complete

```{autodocx-docstring} duck.http.core.httpd.task_executor.RequestHandlingExecutor.on_task_complete
```

````

`````
