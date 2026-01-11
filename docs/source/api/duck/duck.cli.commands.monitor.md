# {py:mod}`duck.cli.commands.monitor`

```{py:module} duck.cli.commands.monitor
```

```{autodocx-docstring} duck.cli.commands.monitor
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`MonitorCommand <duck.cli.commands.monitor.MonitorCommand>`
  - ```{autodocx-docstring} duck.cli.commands.monitor.MonitorCommand
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`console <duck.cli.commands.monitor.console>`
  - ```{autodocx-docstring} duck.cli.commands.monitor.console
    :summary:
    ```
````

### API

`````{py:class} MonitorCommand
:canonical: duck.cli.commands.monitor.MonitorCommand

```{autodocx-docstring} duck.cli.commands.monitor.MonitorCommand
```

````{py:attribute} SPARK_SYMBOLS
:canonical: duck.cli.commands.monitor.MonitorCommand.SPARK_SYMBOLS
:value: >
   '▁▂▃▄▅▆▇█'

```{autodocx-docstring} duck.cli.commands.monitor.MonitorCommand.SPARK_SYMBOLS
```

````

````{py:method} disk()
:canonical: duck.cli.commands.monitor.MonitorCommand.disk
:classmethod:

```{autodocx-docstring} duck.cli.commands.monitor.MonitorCommand.disk
```

````

````{py:method} get_duck_processes(name: str, pids: typing.Optional[typing.List[int]] = None, sort_by: str = 'cpu')
:canonical: duck.cli.commands.monitor.MonitorCommand.get_duck_processes
:classmethod:

```{autodocx-docstring} duck.cli.commands.monitor.MonitorCommand.get_duck_processes
```

````

````{py:method} get_system_metrics(prev_disk, prev_net, elapsed)
:canonical: duck.cli.commands.monitor.MonitorCommand.get_system_metrics
:classmethod:

```{autodocx-docstring} duck.cli.commands.monitor.MonitorCommand.get_system_metrics
```

````

````{py:method} main(interval: float = 1.0, duck_process_name: str = 'duck*', duck_pids: typing.Optional[typing.List[int]] = None, sort_by: str = 'cpu', cpu_warning: float = 80.0, ram_warning: float = 80.0, history_length: int = 8)
:canonical: duck.cli.commands.monitor.MonitorCommand.main
:classmethod:

```{autodocx-docstring} duck.cli.commands.monitor.MonitorCommand.main
```

````

````{py:method} make_duck_process_tables(processes)
:canonical: duck.cli.commands.monitor.MonitorCommand.make_duck_process_tables
:classmethod:

```{autodocx-docstring} duck.cli.commands.monitor.MonitorCommand.make_duck_process_tables
```

````

````{py:method} make_history_table(history: typing.List[typing.Dict[str, typing.Any]], cpu_warning: float, ram_warning: float, width: int = 30)
:canonical: duck.cli.commands.monitor.MonitorCommand.make_history_table
:classmethod:

```{autodocx-docstring} duck.cli.commands.monitor.MonitorCommand.make_history_table
```

````

````{py:method} make_system_table(cpu_per_core, ram_str, disk_str, net_str)
:canonical: duck.cli.commands.monitor.MonitorCommand.make_system_table
:classmethod:

```{autodocx-docstring} duck.cli.commands.monitor.MonitorCommand.make_system_table
```

````

````{py:method} render_trend_bar(value: float, max_value: float = 100) -> rich.text.Text
:canonical: duck.cli.commands.monitor.MonitorCommand.render_trend_bar
:classmethod:

```{autodocx-docstring} duck.cli.commands.monitor.MonitorCommand.render_trend_bar
```

````

````{py:method} sparkline_from_values(values: typing.List[float], max_value: float = 100, width: typing.Optional[int] = None) -> str
:canonical: duck.cli.commands.monitor.MonitorCommand.sparkline_from_values
:classmethod:

```{autodocx-docstring} duck.cli.commands.monitor.MonitorCommand.sparkline_from_values
```

````

`````

````{py:data} console
:canonical: duck.cli.commands.monitor.console
:value: >
   'Console(...)'

```{autodocx-docstring} duck.cli.commands.monitor.console
```

````
