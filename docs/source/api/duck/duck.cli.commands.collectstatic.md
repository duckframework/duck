# {py:mod}`duck.cli.commands.collectstatic`

```{py:module} duck.cli.commands.collectstatic
```

```{autodocx-docstring} duck.cli.commands.collectstatic
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`CollectStaticCommand <duck.cli.commands.collectstatic.CollectStaticCommand>`
  - ```{autodocx-docstring} duck.cli.commands.collectstatic.CollectStaticCommand
    :summary:
    ```
````

### API

`````{py:class} CollectStaticCommand
:canonical: duck.cli.commands.collectstatic.CollectStaticCommand

```{autodocx-docstring} duck.cli.commands.collectstatic.CollectStaticCommand
```

````{py:method} collectstatic(skip_confirmation: bool = False) -> None
:canonical: duck.cli.commands.collectstatic.CollectStaticCommand.collectstatic
:classmethod:

```{autodocx-docstring} duck.cli.commands.collectstatic.CollectStaticCommand.collectstatic
```

````

````{py:method} find_blueprint_static_dirs() -> typing.Generator[typing.Tuple[str, duck.routes.Blueprint], None, None]
:canonical: duck.cli.commands.collectstatic.CollectStaticCommand.find_blueprint_static_dirs
:classmethod:

```{autodocx-docstring} duck.cli.commands.collectstatic.CollectStaticCommand.find_blueprint_static_dirs
```

````

````{py:method} get_blueprint_staticfiles(blueprint_static_dirs: typing.Tuple[str, duck.routes.Blueprint])
:canonical: duck.cli.commands.collectstatic.CollectStaticCommand.get_blueprint_staticfiles
:classmethod:

```{autodocx-docstring} duck.cli.commands.collectstatic.CollectStaticCommand.get_blueprint_staticfiles
```

````

````{py:method} main(skip_confirmation: bool = False)
:canonical: duck.cli.commands.collectstatic.CollectStaticCommand.main
:classmethod:

```{autodocx-docstring} duck.cli.commands.collectstatic.CollectStaticCommand.main
```

````

````{py:method} recursive_getfiles(directory: str) -> typing.Generator
:canonical: duck.cli.commands.collectstatic.CollectStaticCommand.recursive_getfiles
:classmethod:

```{autodocx-docstring} duck.cli.commands.collectstatic.CollectStaticCommand.recursive_getfiles
```

````

````{py:method} setup()
:canonical: duck.cli.commands.collectstatic.CollectStaticCommand.setup
:classmethod:

```{autodocx-docstring} duck.cli.commands.collectstatic.CollectStaticCommand.setup
```

````

`````
