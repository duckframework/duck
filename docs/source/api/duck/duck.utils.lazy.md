# {py:mod}`duck.utils.lazy`

```{py:module} duck.utils.lazy
```

```{autodocx-docstring} duck.utils.lazy
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`Lazy <duck.utils.lazy.Lazy>`
  - ```{autodocx-docstring} duck.utils.lazy.Lazy
    :summary:
    ```
* - {py:obj}`LiveResult <duck.utils.lazy.LiveResult>`
  - ```{autodocx-docstring} duck.utils.lazy.LiveResult
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`_dunder_forward <duck.utils.lazy._dunder_forward>`
  - ```{autodocx-docstring} duck.utils.lazy._dunder_forward
    :summary:
    ```
* - {py:obj}`skip_dunders <duck.utils.lazy.skip_dunders>`
  - ```{autodocx-docstring} duck.utils.lazy.skip_dunders
    :summary:
    ```
````

### API

`````{py:class} Lazy(_callable: typing.Callable, nocache: bool = False, *args, **kwargs)
:canonical: duck.utils.lazy.Lazy

```{autodocx-docstring} duck.utils.lazy.Lazy
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.utils.lazy.Lazy.__init__
```

````{py:method} __aenter__()
:canonical: duck.utils.lazy.Lazy.__aenter__
:async:

```{autodocx-docstring} duck.utils.lazy.Lazy.__aenter__
```

````

````{py:method} __aexit__(exc_type, exc_val, exc_tb)
:canonical: duck.utils.lazy.Lazy.__aexit__
:async:

```{autodocx-docstring} duck.utils.lazy.Lazy.__aexit__
```

````

````{py:method} __aiter__()
:canonical: duck.utils.lazy.Lazy.__aiter__

```{autodocx-docstring} duck.utils.lazy.Lazy.__aiter__
```

````

````{py:attribute} __all_private_attrs
:canonical: duck.utils.lazy.Lazy.__all_private_attrs
:value: >
   None

```{autodocx-docstring} duck.utils.lazy.Lazy.__all_private_attrs
```

````

````{py:method} __anext__()
:canonical: duck.utils.lazy.Lazy.__anext__
:async:

```{autodocx-docstring} duck.utils.lazy.Lazy.__anext__
```

````

````{py:method} __await__()
:canonical: duck.utils.lazy.Lazy.__await__

```{autodocx-docstring} duck.utils.lazy.Lazy.__await__
```

````

````{py:method} __bool__()
:canonical: duck.utils.lazy.Lazy.__bool__

```{autodocx-docstring} duck.utils.lazy.Lazy.__bool__
```

````

````{py:method} __call__(*args, **kwargs)
:canonical: duck.utils.lazy.Lazy.__call__

```{autodocx-docstring} duck.utils.lazy.Lazy.__call__
```

````

````{py:method} __enter__()
:canonical: duck.utils.lazy.Lazy.__enter__

```{autodocx-docstring} duck.utils.lazy.Lazy.__enter__
```

````

````{py:method} __exit__(exc_type, exc_val, exc_tb)
:canonical: duck.utils.lazy.Lazy.__exit__

```{autodocx-docstring} duck.utils.lazy.Lazy.__exit__
```

````

````{py:method} __getattribute__(key)
:canonical: duck.utils.lazy.Lazy.__getattribute__

````

````{py:method} __setattr__(key, value)
:canonical: duck.utils.lazy.Lazy.__setattr__

````

````{py:attribute} __slots__
:canonical: duck.utils.lazy.Lazy.__slots__
:value: >
   ('_Lazy__callable', '_Lazy__args', '_Lazy__kwargs', '_Lazy__result', '_Lazy__nocache', '_Lazy__extra...

```{autodocx-docstring} duck.utils.lazy.Lazy.__slots__
```

````

````{py:attribute} _global_cache
:canonical: duck.utils.lazy.Lazy._global_cache
:type: collections.OrderedDict[typing.Tuple[typing.Callable, typing.Tuple, typing.Tuple], typing.Any]
:value: >
   'OrderedDict(...)'

```{autodocx-docstring} duck.utils.lazy.Lazy._global_cache
```

````

````{py:attribute} _max_size
:canonical: duck.utils.lazy.Lazy._max_size
:type: int
:value: >
   256

```{autodocx-docstring} duck.utils.lazy.Lazy._max_size
```

````

````{py:property} extra_data
:canonical: duck.utils.lazy.Lazy.extra_data
:type: dict

```{autodocx-docstring} duck.utils.lazy.Lazy.extra_data
```

````

````{py:method} getresult() -> typing.Any
:canonical: duck.utils.lazy.Lazy.getresult

```{autodocx-docstring} duck.utils.lazy.Lazy.getresult
```

````

`````

````{py:exception} LazyError()
:canonical: duck.utils.lazy.LazyError

Bases: {py:obj}`Exception`

```{autodocx-docstring} duck.utils.lazy.LazyError
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.utils.lazy.LazyError.__init__
```

````

````{py:class} LiveResult(callable_: typing.Callable, *args, **kwargs)
:canonical: duck.utils.lazy.LiveResult

Bases: {py:obj}`duck.utils.lazy.Lazy`

```{autodocx-docstring} duck.utils.lazy.LiveResult
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.utils.lazy.LiveResult.__init__
```

````

````{py:data} _dunder_forward
:canonical: duck.utils.lazy._dunder_forward
:value: >
   ['__len__', '__str__', '__repr__', '__bytes__', '__iter__', '__reversed__', '__contains__', '__getit...

```{autodocx-docstring} duck.utils.lazy._dunder_forward
```

````

````{py:data} skip_dunders
:canonical: duck.utils.lazy.skip_dunders
:value: >
   None

```{autodocx-docstring} duck.utils.lazy.skip_dunders
```

````
