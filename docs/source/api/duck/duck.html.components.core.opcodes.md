# {py:mod}`duck.html.components.core.opcodes`

```{py:module} duck.html.components.core.opcodes
```

```{autodocx-docstring} duck.html.components.core.opcodes
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`EventOpCode <duck.html.components.core.opcodes.EventOpCode>`
  - ```{autodocx-docstring} duck.html.components.core.opcodes.EventOpCode
    :summary:
    ```
* - {py:obj}`PatchCode <duck.html.components.core.opcodes.PatchCode>`
  - ```{autodocx-docstring} duck.html.components.core.opcodes.PatchCode
    :summary:
    ```
````

### API

`````{py:class} EventOpCode()
:canonical: duck.html.components.core.opcodes.EventOpCode

Bases: {py:obj}`enum.IntEnum`

```{autodocx-docstring} duck.html.components.core.opcodes.EventOpCode
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.html.components.core.opcodes.EventOpCode.__init__
```

````{py:attribute} APPLY_PATCH
:canonical: duck.html.components.core.opcodes.EventOpCode.APPLY_PATCH
:value: >
   1

```{autodocx-docstring} duck.html.components.core.opcodes.EventOpCode.APPLY_PATCH
```

````

````{py:attribute} COMPONENT_UNKNOWN
:canonical: duck.html.components.core.opcodes.EventOpCode.COMPONENT_UNKNOWN
:value: >
   150

```{autodocx-docstring} duck.html.components.core.opcodes.EventOpCode.COMPONENT_UNKNOWN
```

````

````{py:attribute} DISPATCH_COMPONENT_EVENT
:canonical: duck.html.components.core.opcodes.EventOpCode.DISPATCH_COMPONENT_EVENT
:value: >
   100

```{autodocx-docstring} duck.html.components.core.opcodes.EventOpCode.DISPATCH_COMPONENT_EVENT
```

````

````{py:attribute} EXECUTE_JS
:canonical: duck.html.components.core.opcodes.EventOpCode.EXECUTE_JS
:value: >
   101

```{autodocx-docstring} duck.html.components.core.opcodes.EventOpCode.EXECUTE_JS
```

````

````{py:attribute} JS_EXECUTION_RESULT
:canonical: duck.html.components.core.opcodes.EventOpCode.JS_EXECUTION_RESULT
:value: >
   111

```{autodocx-docstring} duck.html.components.core.opcodes.EventOpCode.JS_EXECUTION_RESULT
```

````

````{py:attribute} NAVIGATE_TO
:canonical: duck.html.components.core.opcodes.EventOpCode.NAVIGATE_TO
:value: >
   120

```{autodocx-docstring} duck.html.components.core.opcodes.EventOpCode.NAVIGATE_TO
```

````

````{py:attribute} NAVIGATION_RESULT
:canonical: duck.html.components.core.opcodes.EventOpCode.NAVIGATION_RESULT
:value: >
   121

```{autodocx-docstring} duck.html.components.core.opcodes.EventOpCode.NAVIGATION_RESULT
```

````

`````

`````{py:class} PatchCode()
:canonical: duck.html.components.core.opcodes.PatchCode

Bases: {py:obj}`enum.IntEnum`

```{autodocx-docstring} duck.html.components.core.opcodes.PatchCode
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.html.components.core.opcodes.PatchCode.__init__
```

````{py:attribute} ALTER_TEXT
:canonical: duck.html.components.core.opcodes.PatchCode.ALTER_TEXT
:value: >
   3

```{autodocx-docstring} duck.html.components.core.opcodes.PatchCode.ALTER_TEXT
```

````

````{py:attribute} INSERT_NODE
:canonical: duck.html.components.core.opcodes.PatchCode.INSERT_NODE
:value: >
   2

```{autodocx-docstring} duck.html.components.core.opcodes.PatchCode.INSERT_NODE
```

````

````{py:attribute} REMOVE_NODE
:canonical: duck.html.components.core.opcodes.PatchCode.REMOVE_NODE
:value: >
   1

```{autodocx-docstring} duck.html.components.core.opcodes.PatchCode.REMOVE_NODE
```

````

````{py:attribute} REPLACE_NODE
:canonical: duck.html.components.core.opcodes.PatchCode.REPLACE_NODE
:value: >
   0

```{autodocx-docstring} duck.html.components.core.opcodes.PatchCode.REPLACE_NODE
```

````

````{py:attribute} REPLACE_PROPS
:canonical: duck.html.components.core.opcodes.PatchCode.REPLACE_PROPS
:value: >
   4

```{autodocx-docstring} duck.html.components.core.opcodes.PatchCode.REPLACE_PROPS
```

````

````{py:attribute} REPLACE_STYLE
:canonical: duck.html.components.core.opcodes.PatchCode.REPLACE_STYLE
:value: >
   5

```{autodocx-docstring} duck.html.components.core.opcodes.PatchCode.REPLACE_STYLE
```

````

`````
