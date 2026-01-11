# {py:mod}`duck.html.components.extensions`

```{py:module} duck.html.components.extensions
```

```{autodocx-docstring} duck.html.components.extensions
:allowtitles:
```

## Package Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`BasicExtension <duck.html.components.extensions.BasicExtension>`
  - ```{autodocx-docstring} duck.html.components.extensions.BasicExtension
    :summary:
    ```
* - {py:obj}`Extension <duck.html.components.extensions.Extension>`
  - ```{autodocx-docstring} duck.html.components.extensions.Extension
    :summary:
    ```
* - {py:obj}`StyleCompatibilityExtension <duck.html.components.extensions.StyleCompatibilityExtension>`
  - ```{autodocx-docstring} duck.html.components.extensions.StyleCompatibilityExtension
    :summary:
    ```
````

### API

`````{py:class} BasicExtension
:canonical: duck.html.components.extensions.BasicExtension

Bases: {py:obj}`duck.html.components.extensions.Extension`

```{autodocx-docstring} duck.html.components.extensions.BasicExtension
```

````{py:method} apply_extension()
:canonical: duck.html.components.extensions.BasicExtension.apply_extension

```{autodocx-docstring} duck.html.components.extensions.BasicExtension.apply_extension
```

````

````{py:property} bg_color
:canonical: duck.html.components.extensions.BasicExtension.bg_color
:type: typing.Optional[str]

```{autodocx-docstring} duck.html.components.extensions.BasicExtension.bg_color
```

````

````{py:property} color
:canonical: duck.html.components.extensions.BasicExtension.color
:type: typing.Optional[str]

```{autodocx-docstring} duck.html.components.extensions.BasicExtension.color
```

````

````{py:method} get_kwarg_or_raise(kwarg: str) -> typing.Any
:canonical: duck.html.components.extensions.BasicExtension.get_kwarg_or_raise

```{autodocx-docstring} duck.html.components.extensions.BasicExtension.get_kwarg_or_raise
```

````

````{py:method} get_request_or_raise() -> duck.http.request.HttpRequest
:canonical: duck.html.components.extensions.BasicExtension.get_request_or_raise

```{autodocx-docstring} duck.html.components.extensions.BasicExtension.get_request_or_raise
```

````

````{py:property} id
:canonical: duck.html.components.extensions.BasicExtension.id
:type: typing.Optional[str]

```{autodocx-docstring} duck.html.components.extensions.BasicExtension.id
```

````

````{py:property} klass
:canonical: duck.html.components.extensions.BasicExtension.klass
:type: typing.Optional[str]

```{autodocx-docstring} duck.html.components.extensions.BasicExtension.klass
```

````

````{py:property} text
:canonical: duck.html.components.extensions.BasicExtension.text
:type: str

```{autodocx-docstring} duck.html.components.extensions.BasicExtension.text
```

````

`````

`````{py:class} Extension
:canonical: duck.html.components.extensions.Extension

```{autodocx-docstring} duck.html.components.extensions.Extension
```

````{py:method} apply_extension()
:canonical: duck.html.components.extensions.Extension.apply_extension

```{autodocx-docstring} duck.html.components.extensions.Extension.apply_extension
```

````

````{py:method} on_create()
:canonical: duck.html.components.extensions.Extension.on_create

```{autodocx-docstring} duck.html.components.extensions.Extension.on_create
```

````

`````

````{py:exception} ExtensionError()
:canonical: duck.html.components.extensions.ExtensionError

Bases: {py:obj}`Exception`

```{autodocx-docstring} duck.html.components.extensions.ExtensionError
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.html.components.extensions.ExtensionError.__init__
```

````

````{py:exception} KwargError()
:canonical: duck.html.components.extensions.KwargError

Bases: {py:obj}`duck.html.components.extensions.ExtensionError`

```{autodocx-docstring} duck.html.components.extensions.KwargError
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.html.components.extensions.KwargError.__init__
```

````

````{py:exception} RequestNotFoundError()
:canonical: duck.html.components.extensions.RequestNotFoundError

Bases: {py:obj}`duck.html.components.extensions.ExtensionError`

```{autodocx-docstring} duck.html.components.extensions.RequestNotFoundError
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.html.components.extensions.RequestNotFoundError.__init__
```

````

`````{py:class} StyleCompatibilityExtension(*args, **kw)
:canonical: duck.html.components.extensions.StyleCompatibilityExtension

Bases: {py:obj}`duck.html.components.extensions.Extension`

```{autodocx-docstring} duck.html.components.extensions.StyleCompatibilityExtension
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.html.components.extensions.StyleCompatibilityExtension.__init__
```

````{py:method} apply_extension()
:canonical: duck.html.components.extensions.StyleCompatibilityExtension.apply_extension

````

`````
