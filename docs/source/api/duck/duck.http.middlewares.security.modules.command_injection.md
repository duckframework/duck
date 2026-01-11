# {py:mod}`duck.http.middlewares.security.modules.command_injection`

```{py:module} duck.http.middlewares.security.modules.command_injection
```

```{autodocx-docstring} duck.http.middlewares.security.modules.command_injection
:allowtitles:
```

## Module Contents

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`check_command_injection_in_url <duck.http.middlewares.security.modules.command_injection.check_command_injection_in_url>`
  - ```{autodocx-docstring} duck.http.middlewares.security.modules.command_injection.check_command_injection_in_url
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`CMD_INJ_PATTERN <duck.http.middlewares.security.modules.command_injection.CMD_INJ_PATTERN>`
  - ```{autodocx-docstring} duck.http.middlewares.security.modules.command_injection.CMD_INJ_PATTERN
    :summary:
    ```
````

### API

````{py:data} CMD_INJ_PATTERN
:canonical: duck.http.middlewares.security.modules.command_injection.CMD_INJ_PATTERN
:value: >
   'compile(...)'

```{autodocx-docstring} duck.http.middlewares.security.modules.command_injection.CMD_INJ_PATTERN
```

````

````{py:function} check_command_injection_in_url(url: str) -> bool
:canonical: duck.http.middlewares.security.modules.command_injection.check_command_injection_in_url

```{autodocx-docstring} duck.http.middlewares.security.modules.command_injection.check_command_injection_in_url
```
````
