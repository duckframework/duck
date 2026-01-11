# {py:mod}`duck.logging.logger`

```{py:module} duck.logging.logger
```

```{autodocx-docstring} duck.logging.logger
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`Logger <duck.logging.logger.Logger>`
  - ```{autodocx-docstring} duck.logging.logger.Logger
    :summary:
    ```
````

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`expand_exception <duck.logging.logger.expand_exception>`
  - ```{autodocx-docstring} duck.logging.logger.expand_exception
    :summary:
    ```
* - {py:obj}`handle_exception <duck.logging.logger.handle_exception>`
  - ```{autodocx-docstring} duck.logging.logger.handle_exception
    :summary:
    ```
* - {py:obj}`log <duck.logging.logger.log>`
  - ```{autodocx-docstring} duck.logging.logger.log
    :summary:
    ```
* - {py:obj}`log_exception <duck.logging.logger.log_exception>`
  - ```{autodocx-docstring} duck.logging.logger.log_exception
    :summary:
    ```
* - {py:obj}`log_raw <duck.logging.logger.log_raw>`
  - ```{autodocx-docstring} duck.logging.logger.log_raw
    :summary:
    ```
* - {py:obj}`should_filter_warning <duck.logging.logger.should_filter_warning>`
  - ```{autodocx-docstring} duck.logging.logger.should_filter_warning
    :summary:
    ```
* - {py:obj}`warn <duck.logging.logger.warn>`
  - ```{autodocx-docstring} duck.logging.logger.warn
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`CRITICAL <duck.logging.logger.CRITICAL>`
  - ```{autodocx-docstring} duck.logging.logger.CRITICAL
    :summary:
    ```
* - {py:obj}`DEBUG <duck.logging.logger.DEBUG>`
  - ```{autodocx-docstring} duck.logging.logger.DEBUG
    :summary:
    ```
* - {py:obj}`ERROR <duck.logging.logger.ERROR>`
  - ```{autodocx-docstring} duck.logging.logger.ERROR
    :summary:
    ```
* - {py:obj}`INFO <duck.logging.logger.INFO>`
  - ```{autodocx-docstring} duck.logging.logger.INFO
    :summary:
    ```
* - {py:obj}`LOGGING_DIR <duck.logging.logger.LOGGING_DIR>`
  - ```{autodocx-docstring} duck.logging.logger.LOGGING_DIR
    :summary:
    ```
* - {py:obj}`LOG_FILE_FORMAT <duck.logging.logger.LOG_FILE_FORMAT>`
  - ```{autodocx-docstring} duck.logging.logger.LOG_FILE_FORMAT
    :summary:
    ```
* - {py:obj}`LOG_TO_FILE <duck.logging.logger.LOG_TO_FILE>`
  - ```{autodocx-docstring} duck.logging.logger.LOG_TO_FILE
    :summary:
    ```
* - {py:obj}`SILENT <duck.logging.logger.SILENT>`
  - ```{autodocx-docstring} duck.logging.logger.SILENT
    :summary:
    ```
* - {py:obj}`SUCCESS <duck.logging.logger.SUCCESS>`
  - ```{autodocx-docstring} duck.logging.logger.SUCCESS
    :summary:
    ```
* - {py:obj}`VERBOSE_LOGGING <duck.logging.logger.VERBOSE_LOGGING>`
  - ```{autodocx-docstring} duck.logging.logger.VERBOSE_LOGGING
    :summary:
    ```
* - {py:obj}`WARNING <duck.logging.logger.WARNING>`
  - ```{autodocx-docstring} duck.logging.logger.WARNING
    :summary:
    ```
````

### API

````{py:data} CRITICAL
:canonical: duck.logging.logger.CRITICAL
:value: >
   4

```{autodocx-docstring} duck.logging.logger.CRITICAL
```

````

````{py:data} DEBUG
:canonical: duck.logging.logger.DEBUG
:value: >
   1

```{autodocx-docstring} duck.logging.logger.DEBUG
```

````

````{py:data} ERROR
:canonical: duck.logging.logger.ERROR
:value: >
   5

```{autodocx-docstring} duck.logging.logger.ERROR
```

````

````{py:data} INFO
:canonical: duck.logging.logger.INFO
:value: >
   0

```{autodocx-docstring} duck.logging.logger.INFO
```

````

````{py:data} LOGGING_DIR
:canonical: duck.logging.logger.LOGGING_DIR
:value: >
   None

```{autodocx-docstring} duck.logging.logger.LOGGING_DIR
```

````

````{py:data} LOG_FILE_FORMAT
:canonical: duck.logging.logger.LOG_FILE_FORMAT
:value: >
   None

```{autodocx-docstring} duck.logging.logger.LOG_FILE_FORMAT
```

````

````{py:data} LOG_TO_FILE
:canonical: duck.logging.logger.LOG_TO_FILE
:value: >
   None

```{autodocx-docstring} duck.logging.logger.LOG_TO_FILE
```

````

`````{py:class} Logger
:canonical: duck.logging.logger.Logger

```{autodocx-docstring} duck.logging.logger.Logger
```

````{py:attribute} __current_logfile_fd
:canonical: duck.logging.logger.Logger.__current_logfile_fd
:value: >
   None

```{autodocx-docstring} duck.logging.logger.Logger.__current_logfile_fd
```

````

````{py:method} close_logfile()
:canonical: duck.logging.logger.Logger.close_logfile
:classmethod:

```{autodocx-docstring} duck.logging.logger.Logger.close_logfile
```

````

````{py:method} get_current_logfile(raise_if_logging_dir_not_found: bool = True) -> str
:canonical: duck.logging.logger.Logger.get_current_logfile
:classmethod:

```{autodocx-docstring} duck.logging.logger.Logger.get_current_logfile
```

````

````{py:method} get_current_logfile_fd()
:canonical: duck.logging.logger.Logger.get_current_logfile_fd
:classmethod:

```{autodocx-docstring} duck.logging.logger.Logger.get_current_logfile_fd
```

````

````{py:method} get_latest_logfile() -> typing.Optional[str]
:canonical: duck.logging.logger.Logger.get_latest_logfile
:classmethod:

```{autodocx-docstring} duck.logging.logger.Logger.get_latest_logfile
```

````

````{py:method} log_to_file(data: typing.Union[str, bytes], end: typing.Union[str, bytes] = '\n') -> str | bytes
:canonical: duck.logging.logger.Logger.log_to_file
:classmethod:

```{autodocx-docstring} duck.logging.logger.Logger.log_to_file
```

````

````{py:attribute} print_lock
:canonical: duck.logging.logger.Logger.print_lock
:value: >
   'Lock(...)'

```{autodocx-docstring} duck.logging.logger.Logger.print_lock
```

````

````{py:method} redirect_console_output()
:canonical: duck.logging.logger.Logger.redirect_console_output
:classmethod:

```{autodocx-docstring} duck.logging.logger.Logger.redirect_console_output
```

````

````{py:method} undo_console_output_redirect()
:canonical: duck.logging.logger.Logger.undo_console_output_redirect
:classmethod:

```{autodocx-docstring} duck.logging.logger.Logger.undo_console_output_redirect
```

````

`````

````{py:data} SILENT
:canonical: duck.logging.logger.SILENT
:value: >
   None

```{autodocx-docstring} duck.logging.logger.SILENT
```

````

````{py:data} SUCCESS
:canonical: duck.logging.logger.SUCCESS
:value: >
   2

```{autodocx-docstring} duck.logging.logger.SUCCESS
```

````

````{py:data} VERBOSE_LOGGING
:canonical: duck.logging.logger.VERBOSE_LOGGING
:value: >
   None

```{autodocx-docstring} duck.logging.logger.VERBOSE_LOGGING
```

````

````{py:data} WARNING
:canonical: duck.logging.logger.WARNING
:value: >
   3

```{autodocx-docstring} duck.logging.logger.WARNING
```

````

````{py:function} expand_exception(e: Exception) -> str
:canonical: duck.logging.logger.expand_exception

```{autodocx-docstring} duck.logging.logger.expand_exception
```
````

````{py:function} handle_exception(func: typing.Callable)
:canonical: duck.logging.logger.handle_exception

```{autodocx-docstring} duck.logging.logger.handle_exception
```
````

````{py:function} log(msg: str, prefix: str = '[ * ]', level: int = INFO, use_colors: bool = True, custom_color: str = None, end: str = '\n')
:canonical: duck.logging.logger.log

```{autodocx-docstring} duck.logging.logger.log
```
````

````{py:function} log_exception(e: Exception)
:canonical: duck.logging.logger.log_exception

```{autodocx-docstring} duck.logging.logger.log_exception
```
````

````{py:function} log_raw(msg: str, level: int = INFO, use_colors: bool = True, custom_color: str = None, end: str = '\n')
:canonical: duck.logging.logger.log_raw

```{autodocx-docstring} duck.logging.logger.log_raw
```
````

````{py:function} should_filter_warning(category, message, module=None, lineno=0)
:canonical: duck.logging.logger.should_filter_warning

```{autodocx-docstring} duck.logging.logger.should_filter_warning
```
````

````{py:function} warn(message: str, category: Warning = UserWarning, use_colors: bool = True, module=None, lineno=0)
:canonical: duck.logging.logger.warn

```{autodocx-docstring} duck.logging.logger.warn
```
````
