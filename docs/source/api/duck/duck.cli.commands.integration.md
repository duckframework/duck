# {py:mod}`duck.cli.commands.integration`

```{py:module} duck.cli.commands.integration
```

```{autodocx-docstring} duck.cli.commands.integration
:allowtitles:
```

## Submodules

```{toctree}
:titlesonly:
:maxdepth: 1

duck.cli.commands.integration._django_settings
duck.cli.commands.integration._django_urls
```

## Package Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`DjangoAddCommand <duck.cli.commands.integration.DjangoAddCommand>`
  - ```{autodocx-docstring} duck.cli.commands.integration.DjangoAddCommand
    :summary:
    ```
````

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`copy_template_settings_and_urls <duck.cli.commands.integration.copy_template_settings_and_urls>`
  - ```{autodocx-docstring} duck.cli.commands.integration.copy_template_settings_and_urls
    :summary:
    ```
* - {py:obj}`ignore_pycache <duck.cli.commands.integration.ignore_pycache>`
  - ```{autodocx-docstring} duck.cli.commands.integration.ignore_pycache
    :summary:
    ```
* - {py:obj}`move_settings_py <duck.cli.commands.integration.move_settings_py>`
  - ```{autodocx-docstring} duck.cli.commands.integration.move_settings_py
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`ASGI_PY_CONTENT <duck.cli.commands.integration.ASGI_PY_CONTENT>`
  - ```{autodocx-docstring} duck.cli.commands.integration.ASGI_PY_CONTENT
    :summary:
    ```
* - {py:obj}`EXECUTION_CONFIG_CONTENT <duck.cli.commands.integration.EXECUTION_CONFIG_CONTENT>`
  - ```{autodocx-docstring} duck.cli.commands.integration.EXECUTION_CONFIG_CONTENT
    :summary:
    ```
* - {py:obj}`MANAGE_PY_CONTENT <duck.cli.commands.integration.MANAGE_PY_CONTENT>`
  - ```{autodocx-docstring} duck.cli.commands.integration.MANAGE_PY_CONTENT
    :summary:
    ```
* - {py:obj}`WSGI_PY_CONTENT <duck.cli.commands.integration.WSGI_PY_CONTENT>`
  - ```{autodocx-docstring} duck.cli.commands.integration.WSGI_PY_CONTENT
    :summary:
    ```
````

### API

````{py:data} ASGI_PY_CONTENT
:canonical: duck.cli.commands.integration.ASGI_PY_CONTENT
:value: >
   'lstrip(...)'

```{autodocx-docstring} duck.cli.commands.integration.ASGI_PY_CONTENT
```

````

`````{py:class} DjangoAddCommand
:canonical: duck.cli.commands.integration.DjangoAddCommand

```{autodocx-docstring} duck.cli.commands.integration.DjangoAddCommand
```

````{py:method} integrate_django(django_project_path: str, django_project_mainapp_name: str = None, destination_name: str = 'duckapp')
:canonical: duck.cli.commands.integration.DjangoAddCommand.integrate_django
:classmethod:

```{autodocx-docstring} duck.cli.commands.integration.DjangoAddCommand.integrate_django
```

````

````{py:method} main(django_project_path: str, django_project_mainapp_name: str = None, destination_name: str = 'duckapp')
:canonical: duck.cli.commands.integration.DjangoAddCommand.main
:classmethod:

```{autodocx-docstring} duck.cli.commands.integration.DjangoAddCommand.main
```

````

````{py:method} setup()
:canonical: duck.cli.commands.integration.DjangoAddCommand.setup
:classmethod:

```{autodocx-docstring} duck.cli.commands.integration.DjangoAddCommand.setup
```

````

`````

````{py:data} EXECUTION_CONFIG_CONTENT
:canonical: duck.cli.commands.integration.EXECUTION_CONFIG_CONTENT
:value: >
   'lstrip(...)'

```{autodocx-docstring} duck.cli.commands.integration.EXECUTION_CONFIG_CONTENT
```

````

````{py:data} MANAGE_PY_CONTENT
:canonical: duck.cli.commands.integration.MANAGE_PY_CONTENT
:value: >
   'lstrip(...)'

```{autodocx-docstring} duck.cli.commands.integration.MANAGE_PY_CONTENT
```

````

````{py:data} WSGI_PY_CONTENT
:canonical: duck.cli.commands.integration.WSGI_PY_CONTENT
:value: >
   'lstrip(...)'

```{autodocx-docstring} duck.cli.commands.integration.WSGI_PY_CONTENT
```

````

````{py:function} copy_template_settings_and_urls(settings_py: str, urls_py: str) -> None
:canonical: duck.cli.commands.integration.copy_template_settings_and_urls

```{autodocx-docstring} duck.cli.commands.integration.copy_template_settings_and_urls
```
````

````{py:function} ignore_pycache(dir_path, contents)
:canonical: duck.cli.commands.integration.ignore_pycache

```{autodocx-docstring} duck.cli.commands.integration.ignore_pycache
```
````

````{py:function} move_settings_py(src, dest)
:canonical: duck.cli.commands.integration.move_settings_py

```{autodocx-docstring} duck.cli.commands.integration.move_settings_py
```
````
