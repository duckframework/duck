# {py:mod}`duck.utils.ipc`

```{py:module} duck.utils.ipc
```

```{autodocx-docstring} duck.utils.ipc
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`FileReader <duck.utils.ipc.FileReader>`
  - ```{autodocx-docstring} duck.utils.ipc.FileReader
    :summary:
    ```
* - {py:obj}`FileWriter <duck.utils.ipc.FileWriter>`
  - ```{autodocx-docstring} duck.utils.ipc.FileWriter
    :summary:
    ```
````

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`get_reader <duck.utils.ipc.get_reader>`
  - ```{autodocx-docstring} duck.utils.ipc.get_reader
    :summary:
    ```
* - {py:obj}`get_writer <duck.utils.ipc.get_writer>`
  - ```{autodocx-docstring} duck.utils.ipc.get_writer
    :summary:
    ```
````

### API

`````{py:class} FileReader(filepath: str)
:canonical: duck.utils.ipc.FileReader

```{autodocx-docstring} duck.utils.ipc.FileReader
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.utils.ipc.FileReader.__init__
```

````{py:method} __enter__()
:canonical: duck.utils.ipc.FileReader.__enter__

```{autodocx-docstring} duck.utils.ipc.FileReader.__enter__
```

````

````{py:method} __exit__(exc_type, exc_val, exc_tb)
:canonical: duck.utils.ipc.FileReader.__exit__

```{autodocx-docstring} duck.utils.ipc.FileReader.__exit__
```

````

````{py:method} close()
:canonical: duck.utils.ipc.FileReader.close

```{autodocx-docstring} duck.utils.ipc.FileReader.close
```

````

````{py:method} read_message() -> str
:canonical: duck.utils.ipc.FileReader.read_message

```{autodocx-docstring} duck.utils.ipc.FileReader.read_message
```

````

`````

`````{py:class} FileWriter(filepath: str)
:canonical: duck.utils.ipc.FileWriter

```{autodocx-docstring} duck.utils.ipc.FileWriter
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.utils.ipc.FileWriter.__init__
```

````{py:method} __enter__()
:canonical: duck.utils.ipc.FileWriter.__enter__

```{autodocx-docstring} duck.utils.ipc.FileWriter.__enter__
```

````

````{py:method} __exit__(exc_type, exc_val, exc_tb)
:canonical: duck.utils.ipc.FileWriter.__exit__

```{autodocx-docstring} duck.utils.ipc.FileWriter.__exit__
```

````

````{py:method} close()
:canonical: duck.utils.ipc.FileWriter.close

```{autodocx-docstring} duck.utils.ipc.FileWriter.close
```

````

````{py:method} write_message(message: str)
:canonical: duck.utils.ipc.FileWriter.write_message

```{autodocx-docstring} duck.utils.ipc.FileWriter.write_message
```

````

`````

````{py:function} get_reader(filepath: str = '.ipc') -> duck.utils.ipc.FileReader
:canonical: duck.utils.ipc.get_reader

```{autodocx-docstring} duck.utils.ipc.get_reader
```
````

````{py:function} get_writer(filepath: str = '.ipc') -> duck.utils.ipc.FileWriter
:canonical: duck.utils.ipc.get_writer

```{autodocx-docstring} duck.utils.ipc.get_writer
```
````
