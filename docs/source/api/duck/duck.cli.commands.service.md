# {py:mod}`duck.cli.commands.service`

```{py:module} duck.cli.commands.service
```

```{autodocx-docstring} duck.cli.commands.service
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`ServiceCommand <duck.cli.commands.service.ServiceCommand>`
  - ```{autodocx-docstring} duck.cli.commands.service.ServiceCommand
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`SERVICE_CONTENT <duck.cli.commands.service.SERVICE_CONTENT>`
  - ```{autodocx-docstring} duck.cli.commands.service.SERVICE_CONTENT
    :summary:
    ```
````

### API

````{py:data} SERVICE_CONTENT
:canonical: duck.cli.commands.service.SERVICE_CONTENT
:value: <Multiline-String>

```{autodocx-docstring} duck.cli.commands.service.SERVICE_CONTENT
```

````

`````{py:class} ServiceCommand
:canonical: duck.cli.commands.service.ServiceCommand

```{autodocx-docstring} duck.cli.commands.service.ServiceCommand
```

````{py:method} autorun(kill: bool = False, enable: bool = False, disable: bool = False, settings: str = None, show_status: bool = True)
:canonical: duck.cli.commands.service.ServiceCommand.autorun
:classmethod:

```{autodocx-docstring} duck.cli.commands.service.ServiceCommand.autorun
```

````

````{py:method} check_service()
:canonical: duck.cli.commands.service.ServiceCommand.check_service
:classmethod:

```{autodocx-docstring} duck.cli.commands.service.ServiceCommand.check_service
```

````

````{py:method} create_service(settings: str = None)
:canonical: duck.cli.commands.service.ServiceCommand.create_service
:classmethod:

```{autodocx-docstring} duck.cli.commands.service.ServiceCommand.create_service
```

````

````{py:method} disable_service()
:canonical: duck.cli.commands.service.ServiceCommand.disable_service
:classmethod:

```{autodocx-docstring} duck.cli.commands.service.ServiceCommand.disable_service
```

````

````{py:method} enable_service()
:canonical: duck.cli.commands.service.ServiceCommand.enable_service
:classmethod:

```{autodocx-docstring} duck.cli.commands.service.ServiceCommand.enable_service
```

````

````{py:method} register_subcommands(main_command: click.Command)
:canonical: duck.cli.commands.service.ServiceCommand.register_subcommands
:classmethod:

```{autodocx-docstring} duck.cli.commands.service.ServiceCommand.register_subcommands
```

````

````{py:method} reload_systemd()
:canonical: duck.cli.commands.service.ServiceCommand.reload_systemd
:classmethod:

```{autodocx-docstring} duck.cli.commands.service.ServiceCommand.reload_systemd
```

````

````{py:method} start_service()
:canonical: duck.cli.commands.service.ServiceCommand.start_service
:classmethod:

```{autodocx-docstring} duck.cli.commands.service.ServiceCommand.start_service
```

````

````{py:method} stop_service()
:canonical: duck.cli.commands.service.ServiceCommand.stop_service
:classmethod:

```{autodocx-docstring} duck.cli.commands.service.ServiceCommand.stop_service
```

````

`````
