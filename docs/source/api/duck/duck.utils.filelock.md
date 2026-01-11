# {py:mod}`duck.utils.filelock`

```{py:module} duck.utils.filelock
```

```{autodocx-docstring} duck.utils.filelock
:allowtitles:
```

## Module Contents

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`lock_file <duck.utils.filelock.lock_file>`
  - ```{autodocx-docstring} duck.utils.filelock.lock_file
    :summary:
    ```
* - {py:obj}`open_and_lock <duck.utils.filelock.open_and_lock>`
  - ```{autodocx-docstring} duck.utils.filelock.open_and_lock
    :summary:
    ```
* - {py:obj}`unlock_file <duck.utils.filelock.unlock_file>`
  - ```{autodocx-docstring} duck.utils.filelock.unlock_file
    :summary:
    ```
````

### API

````{py:function} lock_file(file_descriptor, retries=5, wait=1)
:canonical: duck.utils.filelock.lock_file

```{autodocx-docstring} duck.utils.filelock.lock_file
```
````

````{py:function} open_and_lock(filename, mode='r+')
:canonical: duck.utils.filelock.open_and_lock

```{autodocx-docstring} duck.utils.filelock.open_and_lock
```
````

````{py:function} unlock_file(file_descriptor)
:canonical: duck.utils.filelock.unlock_file

```{autodocx-docstring} duck.utils.filelock.unlock_file
```
````
