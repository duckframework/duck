# {py:mod}`duck.logging.console`

```{py:module} duck.logging.console
```

```{autodocx-docstring} duck.logging.console
:allowtitles:
```

## Module Contents

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`expand_exception <duck.logging.console.expand_exception>`
  - ```{autodocx-docstring} duck.logging.console.expand_exception
    :summary:
    ```
* - {py:obj}`handle_exception <duck.logging.console.handle_exception>`
  - ```{autodocx-docstring} duck.logging.console.handle_exception
    :summary:
    ```
* - {py:obj}`log <duck.logging.console.log>`
  - ```{autodocx-docstring} duck.logging.console.log
    :summary:
    ```
* - {py:obj}`log_exception <duck.logging.console.log_exception>`
  - ```{autodocx-docstring} duck.logging.console.log_exception
    :summary:
    ```
* - {py:obj}`log_raw <duck.logging.console.log_raw>`
  - ```{autodocx-docstring} duck.logging.console.log_raw
    :summary:
    ```
* - {py:obj}`should_filter_warning <duck.logging.console.should_filter_warning>`
  - ```{autodocx-docstring} duck.logging.console.should_filter_warning
    :summary:
    ```
* - {py:obj}`warn <duck.logging.console.warn>`
  - ```{autodocx-docstring} duck.logging.console.warn
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`CRITICAL <duck.logging.console.CRITICAL>`
  - ```{autodocx-docstring} duck.logging.console.CRITICAL
    :summary:
    ```
* - {py:obj}`DEBUG <duck.logging.console.DEBUG>`
  - ```{autodocx-docstring} duck.logging.console.DEBUG
    :summary:
    ```
* - {py:obj}`ERROR <duck.logging.console.ERROR>`
  - ```{autodocx-docstring} duck.logging.console.ERROR
    :summary:
    ```
* - {py:obj}`INFO <duck.logging.console.INFO>`
  - ```{autodocx-docstring} duck.logging.console.INFO
    :summary:
    ```
* - {py:obj}`RESPECT_SILENT_CONSOLE_LOGS <duck.logging.console.RESPECT_SILENT_CONSOLE_LOGS>`
  - ```{autodocx-docstring} duck.logging.console.RESPECT_SILENT_CONSOLE_LOGS
    :summary:
    ```
* - {py:obj}`SILENT <duck.logging.console.SILENT>`
  - ```{autodocx-docstring} duck.logging.console.SILENT
    :summary:
    ```
* - {py:obj}`SUCCESS <duck.logging.console.SUCCESS>`
  - ```{autodocx-docstring} duck.logging.console.SUCCESS
    :summary:
    ```
* - {py:obj}`WARNING <duck.logging.console.WARNING>`
  - ```{autodocx-docstring} duck.logging.console.WARNING
    :summary:
    ```
* - {py:obj}`print_lock <duck.logging.console.print_lock>`
  - ```{autodocx-docstring} duck.logging.console.print_lock
    :summary:
    ```
````

### API

````{py:data} CRITICAL
:canonical: duck.logging.console.CRITICAL
:value: >
   4

```{autodocx-docstring} duck.logging.console.CRITICAL
```

````

````{py:data} DEBUG
:canonical: duck.logging.console.DEBUG
:value: >
   1

```{autodocx-docstring} duck.logging.console.DEBUG
```

````

````{py:data} ERROR
:canonical: duck.logging.console.ERROR
:value: >
   5

```{autodocx-docstring} duck.logging.console.ERROR
```

````

````{py:data} INFO
:canonical: duck.logging.console.INFO
:value: >
   0

```{autodocx-docstring} duck.logging.console.INFO
```

````

````{py:data} RESPECT_SILENT_CONSOLE_LOGS
:canonical: duck.logging.console.RESPECT_SILENT_CONSOLE_LOGS
:value: >
   False

```{autodocx-docstring} duck.logging.console.RESPECT_SILENT_CONSOLE_LOGS
```

````

````{py:data} SILENT
:canonical: duck.logging.console.SILENT
:value: >
   False

```{autodocx-docstring} duck.logging.console.SILENT
```

````

````{py:data} SUCCESS
:canonical: duck.logging.console.SUCCESS
:value: >
   2

```{autodocx-docstring} duck.logging.console.SUCCESS
```

````

````{py:data} WARNING
:canonical: duck.logging.console.WARNING
:value: >
   3

```{autodocx-docstring} duck.logging.console.WARNING
```

````

````{py:function} expand_exception(e: Exception) -> str
:canonical: duck.logging.console.expand_exception

```{autodocx-docstring} duck.logging.console.expand_exception
```
````

````{py:function} handle_exception(func: typing.Callable)
:canonical: duck.logging.console.handle_exception

```{autodocx-docstring} duck.logging.console.handle_exception
```
````

````{py:function} log(msg: str, prefix: str = '[ * ]', level: int = INFO, use_colors: bool = True, custom_color: str = None, end: str = '\n')
:canonical: duck.logging.console.log

```{autodocx-docstring} duck.logging.console.log
```
````

````{py:function} log_exception(e: Exception)
:canonical: duck.logging.console.log_exception

```{autodocx-docstring} duck.logging.console.log_exception
```
````

````{py:function} log_raw(msg: str, level: int = INFO, use_colors: bool = True, custom_color: str = None, end: str = '\n')
:canonical: duck.logging.console.log_raw

```{autodocx-docstring} duck.logging.console.log_raw
```
````

````{py:data} print_lock
:canonical: duck.logging.console.print_lock
:value: >
   'Lock(...)'

```{autodocx-docstring} duck.logging.console.print_lock
```

````

````{py:function} should_filter_warning(category, message, module=None, lineno=0)
:canonical: duck.logging.console.should_filter_warning

```{autodocx-docstring} duck.logging.console.should_filter_warning
```
````

````{py:function} warn(message: str, category: Warning = UserWarning, use_colors: bool = True, module=None, lineno=0)
:canonical: duck.logging.console.warn

```{autodocx-docstring} duck.logging.console.warn
```
````
