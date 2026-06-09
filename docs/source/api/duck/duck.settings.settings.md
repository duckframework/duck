# {py:mod}`duck.settings.settings`

```{py:module} duck.settings.settings
```

```{autodocx-docstring} duck.settings.settings
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`Settings <duck.settings.settings.Settings>`
  - ```{autodocx-docstring} duck.settings.settings.Settings
    :summary:
    ```
````

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`get_combined_settings <duck.settings.settings.get_combined_settings>`
  - ```{autodocx-docstring} duck.settings.settings.get_combined_settings
    :summary:
    ```
* - {py:obj}`settings_to_dict <duck.settings.settings.settings_to_dict>`
  - ```{autodocx-docstring} duck.settings.settings.settings_to_dict
    :summary:
    ```
* - {py:obj}`warn_deprecated_settings <duck.settings.settings.warn_deprecated_settings>`
  - ```{autodocx-docstring} duck.settings.settings.warn_deprecated_settings
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`DEPRECATED_SETTINGS <duck.settings.settings.DEPRECATED_SETTINGS>`
  - ```{autodocx-docstring} duck.settings.settings.DEPRECATED_SETTINGS
    :summary:
    ```
* - {py:obj}`SETTINGS <duck.settings.settings.SETTINGS>`
  - ```{autodocx-docstring} duck.settings.settings.SETTINGS
    :summary:
    ```
* - {py:obj}`SETTINGS_MODULE <duck.settings.settings.SETTINGS_MODULE>`
  - ```{autodocx-docstring} duck.settings.settings.SETTINGS_MODULE
    :summary:
    ```
````

### API

````{py:data} DEPRECATED_SETTINGS
:canonical: duck.settings.settings.DEPRECATED_SETTINGS
:type: typing.List[typing.Tuple[str, str]]
:value: >
   [('FORCE_HTTPS', "Setting 'FORCE_HTTPS' is deprecated, please use 'HTTPS_REDIRECT' instead."), ('FOR...

```{autodocx-docstring} duck.settings.settings.DEPRECATED_SETTINGS
```

````

````{py:data} SETTINGS
:canonical: duck.settings.settings.SETTINGS
:type: duck.settings.settings.Settings
:value: >
   'get_combined_settings(...)'

```{autodocx-docstring} duck.settings.settings.SETTINGS
```

````

````{py:data} SETTINGS_MODULE
:canonical: duck.settings.settings.SETTINGS_MODULE
:value: >
   'get(...)'

```{autodocx-docstring} duck.settings.settings.SETTINGS_MODULE
```

````

`````{py:class} Settings()
:canonical: duck.settings.settings.Settings

Bases: {py:obj}`dict`

```{autodocx-docstring} duck.settings.settings.Settings
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.settings.settings.Settings.__init__
```

````{py:method} __repr__()
:canonical: duck.settings.settings.Settings.__repr__

````

````{py:method} reload()
:canonical: duck.settings.settings.Settings.reload

```{autodocx-docstring} duck.settings.settings.Settings.reload
```

````

````{py:attribute} source
:canonical: duck.settings.settings.Settings.source
:value: >
   None

```{autodocx-docstring} duck.settings.settings.Settings.source
```

````

`````

````{py:function} get_combined_settings() -> duck.settings.settings.Settings
:canonical: duck.settings.settings.get_combined_settings

```{autodocx-docstring} duck.settings.settings.get_combined_settings
```
````

````{py:function} settings_to_dict(settings_module: str) -> duck.settings.settings.Settings
:canonical: duck.settings.settings.settings_to_dict

```{autodocx-docstring} duck.settings.settings.settings_to_dict
```
````

````{py:function} warn_deprecated_settings(settings: Settings)
:canonical: duck.settings.settings.warn_deprecated_settings

```{autodocx-docstring} duck.settings.settings.warn_deprecated_settings
```
````
