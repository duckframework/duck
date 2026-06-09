# {py:mod}`duck.template.loaders`

```{py:module} duck.template.loaders
```

```{autodocx-docstring} duck.template.loaders
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`BaseLoader <duck.template.loaders.BaseLoader>`
  - ```{autodocx-docstring} duck.template.loaders.BaseLoader
    :summary:
    ```
* - {py:obj}`DjangoFileSystemLoader <duck.template.loaders.DjangoFileSystemLoader>`
  - ```{autodocx-docstring} duck.template.loaders.DjangoFileSystemLoader
    :summary:
    ```
* - {py:obj}`Jinja2FileSystemLoader <duck.template.loaders.Jinja2FileSystemLoader>`
  - ```{autodocx-docstring} duck.template.loaders.Jinja2FileSystemLoader
    :summary:
    ```
````

### API

`````{py:class} BaseLoader
:canonical: duck.template.loaders.BaseLoader

```{autodocx-docstring} duck.template.loaders.BaseLoader
```

````{py:method} blueprint_template_dirs() -> typing.Generator[typing.Tuple[duck.routes.Blueprint, str], None, None]
:canonical: duck.template.loaders.BaseLoader.blueprint_template_dirs

```{autodocx-docstring} duck.template.loaders.BaseLoader.blueprint_template_dirs
```

````

````{py:method} global_template_dirs() -> typing.List[str]
:canonical: duck.template.loaders.BaseLoader.global_template_dirs

```{autodocx-docstring} duck.template.loaders.BaseLoader.global_template_dirs
```

````

`````

`````{py:class} DjangoFileSystemLoader(engine)
:canonical: duck.template.loaders.DjangoFileSystemLoader

Bases: {py:obj}`duck.template.loaders.BaseLoader`, {py:obj}`django.template.loaders.base.Loader`

```{autodocx-docstring} duck.template.loaders.DjangoFileSystemLoader
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.template.loaders.DjangoFileSystemLoader.__init__
```

````{py:method} get_contents(origin)
:canonical: duck.template.loaders.DjangoFileSystemLoader.get_contents

```{autodocx-docstring} duck.template.loaders.DjangoFileSystemLoader.get_contents
```

````

````{py:method} get_template_sources(template_name: str) -> typing.Generator[django.template.Origin, None, None]
:canonical: duck.template.loaders.DjangoFileSystemLoader.get_template_sources

````

`````

`````{py:class} Jinja2FileSystemLoader
:canonical: duck.template.loaders.Jinja2FileSystemLoader

Bases: {py:obj}`duck.template.loaders.BaseLoader`, {py:obj}`jinja2.loaders.BaseLoader`

```{autodocx-docstring} duck.template.loaders.Jinja2FileSystemLoader
```

````{py:method} get_source(environment, template: str) -> typing.Tuple[str, str, typing.Callable]
:canonical: duck.template.loaders.Jinja2FileSystemLoader.get_source

````

`````
