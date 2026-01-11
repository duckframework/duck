# {py:mod}`duck.utils.threading.patch`

```{py:module} duck.utils.threading.patch
```

```{autodocx-docstring} duck.utils.threading.patch
:allowtitles:
```

## Module Contents

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`_wrap_run <duck.utils.threading.patch._wrap_run>`
  - ```{autodocx-docstring} duck.utils.threading.patch._wrap_run
    :summary:
    ```
* - {py:obj}`get_parent_thread <duck.utils.threading.patch.get_parent_thread>`
  - ```{autodocx-docstring} duck.utils.threading.patch.get_parent_thread
    :summary:
    ```
* - {py:obj}`patch_threading <duck.utils.threading.patch.patch_threading>`
  - ```{autodocx-docstring} duck.utils.threading.patch.patch_threading
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`_is_patched <duck.utils.threading.patch._is_patched>`
  - ```{autodocx-docstring} duck.utils.threading.patch._is_patched
    :summary:
    ```
* - {py:obj}`_original_init <duck.utils.threading.patch._original_init>`
  - ```{autodocx-docstring} duck.utils.threading.patch._original_init
    :summary:
    ```
* - {py:obj}`get_parent <duck.utils.threading.patch.get_parent>`
  - ```{autodocx-docstring} duck.utils.threading.patch.get_parent
    :summary:
    ```
* - {py:obj}`thread_info <duck.utils.threading.patch.thread_info>`
  - ```{autodocx-docstring} duck.utils.threading.patch.thread_info
    :summary:
    ```
````

### API

````{py:exception} PatchNotApplied()
:canonical: duck.utils.threading.patch.PatchNotApplied

Bases: {py:obj}`Exception`

```{autodocx-docstring} duck.utils.threading.patch.PatchNotApplied
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.utils.threading.patch.PatchNotApplied.__init__
```

````

````{py:data} _is_patched
:canonical: duck.utils.threading.patch._is_patched
:value: >
   False

```{autodocx-docstring} duck.utils.threading.patch._is_patched
```

````

````{py:data} _original_init
:canonical: duck.utils.threading.patch._original_init
:value: >
   None

```{autodocx-docstring} duck.utils.threading.patch._original_init
```

````

````{py:function} _wrap_run(self, original_run, pre_hook, post_hook)
:canonical: duck.utils.threading.patch._wrap_run

```{autodocx-docstring} duck.utils.threading.patch._wrap_run
```
````

````{py:data} get_parent
:canonical: duck.utils.threading.patch.get_parent
:value: >
   None

```{autodocx-docstring} duck.utils.threading.patch.get_parent
```

````

````{py:function} get_parent_thread(thread_or_ident: typing.Union[int, threading.Thread]) -> typing.Optional[threading.Thread]
:canonical: duck.utils.threading.patch.get_parent_thread

```{autodocx-docstring} duck.utils.threading.patch.get_parent_thread
```
````

````{py:function} patch_threading(*, pre_hook: typing.Optional[typing.Callable[[threading.Thread], None]] = None, post_hook: typing.Optional[typing.Callable[[threading.Thread], None]] = None, patch_existing_threads: bool = False) -> None
:canonical: duck.utils.threading.patch.patch_threading

```{autodocx-docstring} duck.utils.threading.patch.patch_threading
```
````

````{py:data} thread_info
:canonical: duck.utils.threading.patch.thread_info
:type: typing.Dict[int, typing.Dict[str, typing.Any]]
:value: >
   None

```{autodocx-docstring} duck.utils.threading.patch.thread_info
```

````
