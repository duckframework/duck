# {py:mod}`duck.utils.multiprocessing`

```{py:module} duck.utils.multiprocessing
```

```{autodocx-docstring} duck.utils.multiprocessing
:allowtitles:
```

## Submodules

```{toctree}
:titlesonly:
:maxdepth: 1

duck.utils.multiprocessing.process_manager
duck.utils.multiprocessing.processpool
duck.utils.multiprocessing.proxy
```

## Package Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`ProcessSafeLRUCache <duck.utils.multiprocessing.ProcessSafeLRUCache>`
  - ```{autodocx-docstring} duck.utils.multiprocessing.ProcessSafeLRUCache
    :summary:
    ```
````

### API

`````{py:class} ProcessSafeLRUCache(maxkeys=None)
:canonical: duck.utils.multiprocessing.ProcessSafeLRUCache

```{autodocx-docstring} duck.utils.multiprocessing.ProcessSafeLRUCache
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.utils.multiprocessing.ProcessSafeLRUCache.__init__
```

````{py:attribute} __slots__
:canonical: duck.utils.multiprocessing.ProcessSafeLRUCache.__slots__
:value: >
   None

```{autodocx-docstring} duck.utils.multiprocessing.ProcessSafeLRUCache.__slots__
```

````

````{py:method} clear()
:canonical: duck.utils.multiprocessing.ProcessSafeLRUCache.clear

```{autodocx-docstring} duck.utils.multiprocessing.ProcessSafeLRUCache.clear
```

````

````{py:method} close()
:canonical: duck.utils.multiprocessing.ProcessSafeLRUCache.close

```{autodocx-docstring} duck.utils.multiprocessing.ProcessSafeLRUCache.close
```

````

````{py:method} delete(key: str)
:canonical: duck.utils.multiprocessing.ProcessSafeLRUCache.delete

```{autodocx-docstring} duck.utils.multiprocessing.ProcessSafeLRUCache.delete
```

````

````{py:method} get(key: str, default=None, pop=False)
:canonical: duck.utils.multiprocessing.ProcessSafeLRUCache.get

```{autodocx-docstring} duck.utils.multiprocessing.ProcessSafeLRUCache.get
```

````

````{py:method} has(key: str)
:canonical: duck.utils.multiprocessing.ProcessSafeLRUCache.has

```{autodocx-docstring} duck.utils.multiprocessing.ProcessSafeLRUCache.has
```

````

````{py:method} set(key: str, value, expiry=None)
:canonical: duck.utils.multiprocessing.ProcessSafeLRUCache.set

```{autodocx-docstring} duck.utils.multiprocessing.ProcessSafeLRUCache.set
```

````

`````
