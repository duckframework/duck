# {py:mod}`duck.cli.commands.logs`

```{py:module} duck.cli.commands.logs
```

```{autodocx-docstring} duck.cli.commands.logs
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`LogsCommand <duck.cli.commands.logs.LogsCommand>`
  - ```{autodocx-docstring} duck.cli.commands.logs.LogsCommand
    :summary:
    ```
````

### API

`````{py:class} LogsCommand
:canonical: duck.cli.commands.logs.LogsCommand

```{autodocx-docstring} duck.cli.commands.logs.LogsCommand
```

````{py:method} _get_log_files() -> typing.List[pathlib.Path]
:canonical: duck.cli.commands.logs.LogsCommand._get_log_files
:classmethod:

```{autodocx-docstring} duck.cli.commands.logs.LogsCommand._get_log_files
```

````

````{py:method} _sort_logs(logs: typing.List[pathlib.Path], sort: str) -> typing.List[pathlib.Path]
:canonical: duck.cli.commands.logs.LogsCommand._sort_logs
:staticmethod:

```{autodocx-docstring} duck.cli.commands.logs.LogsCommand._sort_logs
```

````

````{py:method} count_logs()
:canonical: duck.cli.commands.logs.LogsCommand.count_logs
:classmethod:

```{autodocx-docstring} duck.cli.commands.logs.LogsCommand.count_logs
```

````

````{py:method} get_logs_dir() -> pathlib.Path
:canonical: duck.cli.commands.logs.LogsCommand.get_logs_dir
:classmethod:

```{autodocx-docstring} duck.cli.commands.logs.LogsCommand.get_logs_dir
```

````

````{py:method} get_logs_size(fmt: str = 'kb')
:canonical: duck.cli.commands.logs.LogsCommand.get_logs_size
:classmethod:

```{autodocx-docstring} duck.cli.commands.logs.LogsCommand.get_logs_size
```

````

````{py:method} list_logs(max: int = -1, sort: str = 'oldest', show_size: bool = False)
:canonical: duck.cli.commands.logs.LogsCommand.list_logs
:classmethod:

```{autodocx-docstring} duck.cli.commands.logs.LogsCommand.list_logs
```

````

````{py:method} purge_logs(max: int = -1, sort: str = 'oldest')
:canonical: duck.cli.commands.logs.LogsCommand.purge_logs
:classmethod:

```{autodocx-docstring} duck.cli.commands.logs.LogsCommand.purge_logs
```

````

````{py:method} register_subcommands(main_command: click.Command)
:canonical: duck.cli.commands.logs.LogsCommand.register_subcommands
:classmethod:

```{autodocx-docstring} duck.cli.commands.logs.LogsCommand.register_subcommands
```

````

`````
