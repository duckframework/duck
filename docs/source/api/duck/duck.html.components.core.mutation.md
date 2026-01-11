# {py:mod}`duck.html.components.core.mutation`

```{py:module} duck.html.components.core.mutation
```

```{autodocx-docstring} duck.html.components.core.mutation
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`Mutation <duck.html.components.core.mutation.Mutation>`
  - ```{autodocx-docstring} duck.html.components.core.mutation.Mutation
    :summary:
    ```
* - {py:obj}`MutationCode <duck.html.components.core.mutation.MutationCode>`
  -
````

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`on_mutation <duck.html.components.core.mutation.on_mutation>`
  - ```{autodocx-docstring} duck.html.components.core.mutation.on_mutation
    :summary:
    ```
````

### API

`````{py:class} Mutation(target, code: duck.html.components.core.mutation.MutationCode, payload: typing.Dict[typing.Any, typing.Any])
:canonical: duck.html.components.core.mutation.Mutation

```{autodocx-docstring} duck.html.components.core.mutation.Mutation
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.html.components.core.mutation.Mutation.__init__
```

````{py:method} __repr__()
:canonical: duck.html.components.core.mutation.Mutation.__repr__

````

````{py:attribute} __slots__
:canonical: duck.html.components.core.mutation.Mutation.__slots__
:value: >
   ('target', 'code', 'payload')

```{autodocx-docstring} duck.html.components.core.mutation.Mutation.__slots__
```

````

````{py:attribute} __str__
:canonical: duck.html.components.core.mutation.Mutation.__str__
:value: >
   None

```{autodocx-docstring} duck.html.components.core.mutation.Mutation.__str__
```

````

`````

`````{py:class} MutationCode()
:canonical: duck.html.components.core.mutation.MutationCode

Bases: {py:obj}`enum.IntEnum`

````{py:attribute} DELETE_CHILD
:canonical: duck.html.components.core.mutation.MutationCode.DELETE_CHILD
:value: >
   0

```{autodocx-docstring} duck.html.components.core.mutation.MutationCode.DELETE_CHILD
```

````

````{py:attribute} DELETE_PROP
:canonical: duck.html.components.core.mutation.MutationCode.DELETE_PROP
:value: >
   2

```{autodocx-docstring} duck.html.components.core.mutation.MutationCode.DELETE_PROP
```

````

````{py:attribute} DELETE_STYLE
:canonical: duck.html.components.core.mutation.MutationCode.DELETE_STYLE
:value: >
   4

```{autodocx-docstring} duck.html.components.core.mutation.MutationCode.DELETE_STYLE
```

````

````{py:attribute} INSERT_CHILD
:canonical: duck.html.components.core.mutation.MutationCode.INSERT_CHILD
:value: >
   1

```{autodocx-docstring} duck.html.components.core.mutation.MutationCode.INSERT_CHILD
```

````

````{py:attribute} SET_INNER_HTML
:canonical: duck.html.components.core.mutation.MutationCode.SET_INNER_HTML
:value: >
   None

```{autodocx-docstring} duck.html.components.core.mutation.MutationCode.SET_INNER_HTML
```

````

````{py:attribute} SET_PROP
:canonical: duck.html.components.core.mutation.MutationCode.SET_PROP
:value: >
   3

```{autodocx-docstring} duck.html.components.core.mutation.MutationCode.SET_PROP
```

````

````{py:attribute} SET_STYLE
:canonical: duck.html.components.core.mutation.MutationCode.SET_STYLE
:value: >
   5

```{autodocx-docstring} duck.html.components.core.mutation.MutationCode.SET_STYLE
```

````

`````

````{py:function} on_mutation(target, mutation: duck.html.components.core.mutation.Mutation)
:canonical: duck.html.components.core.mutation.on_mutation

```{autodocx-docstring} duck.html.components.core.mutation.on_mutation
```
````
