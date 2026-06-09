# {py:mod}`duck.utils.safemarkup`

```{py:module} duck.utils.safemarkup
```

```{autodocx-docstring} duck.utils.safemarkup
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`MarkupSafeString <duck.utils.safemarkup.MarkupSafeString>`
  - ```{autodocx-docstring} duck.utils.safemarkup.MarkupSafeString
    :summary:
    ```
````

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`mark_safe <duck.utils.safemarkup.mark_safe>`
  - ```{autodocx-docstring} duck.utils.safemarkup.mark_safe
    :summary:
    ```
````

### API

````{py:class} MarkupSafeString()
:canonical: duck.utils.safemarkup.MarkupSafeString

Bases: {py:obj}`django.utils.safestring.SafeString`, {py:obj}`markupsafe.Markup`

```{autodocx-docstring} duck.utils.safemarkup.MarkupSafeString
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.utils.safemarkup.MarkupSafeString.__init__
```

````

````{py:function} mark_safe(func_or_str) -> duck.utils.safemarkup.MarkupSafeString
:canonical: duck.utils.safemarkup.mark_safe

```{autodocx-docstring} duck.utils.safemarkup.mark_safe
```
````
