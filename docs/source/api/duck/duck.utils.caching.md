# {py:mod}`duck.utils.caching`

```{py:module} duck.utils.caching
```

```{autodocx-docstring} duck.utils.caching
:allowtitles:
```

## Package Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`CacheBase <duck.utils.caching.CacheBase>`
  - ```{autodocx-docstring} duck.utils.caching.CacheBase
    :summary:
    ```
* - {py:obj}`CacheSpeedTest <duck.utils.caching.CacheSpeedTest>`
  - ```{autodocx-docstring} duck.utils.caching.CacheSpeedTest
    :summary:
    ```
* - {py:obj}`DynamicFileCache <duck.utils.caching.DynamicFileCache>`
  - ```{autodocx-docstring} duck.utils.caching.DynamicFileCache
    :summary:
    ```
* - {py:obj}`InMemoryCache <duck.utils.caching.InMemoryCache>`
  - ```{autodocx-docstring} duck.utils.caching.InMemoryCache
    :summary:
    ```
* - {py:obj}`KeyAsFolderCache <duck.utils.caching.KeyAsFolderCache>`
  - ```{autodocx-docstring} duck.utils.caching.KeyAsFolderCache
    :summary:
    ```
* - {py:obj}`PersistentFileCache <duck.utils.caching.PersistentFileCache>`
  - ```{autodocx-docstring} duck.utils.caching.PersistentFileCache
    :summary:
    ```
````

### API

`````{py:class} CacheBase
:canonical: duck.utils.caching.CacheBase

```{autodocx-docstring} duck.utils.caching.CacheBase
```

````{py:method} clear()
:canonical: duck.utils.caching.CacheBase.clear
:abstractmethod:

```{autodocx-docstring} duck.utils.caching.CacheBase.clear
```

````

````{py:method} delete(key: str)
:canonical: duck.utils.caching.CacheBase.delete
:abstractmethod:

```{autodocx-docstring} duck.utils.caching.CacheBase.delete
```

````

````{py:method} get(key: str) -> typing.Any
:canonical: duck.utils.caching.CacheBase.get
:abstractmethod:

```{autodocx-docstring} duck.utils.caching.CacheBase.get
```

````

````{py:method} save()
:canonical: duck.utils.caching.CacheBase.save

```{autodocx-docstring} duck.utils.caching.CacheBase.save
```

````

````{py:method} set(key: str, value: typing.Any, expiry: int | float = None)
:canonical: duck.utils.caching.CacheBase.set
:abstractmethod:

```{autodocx-docstring} duck.utils.caching.CacheBase.set
```

````

`````

`````{py:class} CacheSpeedTest(repeat: int = 1)
:canonical: duck.utils.caching.CacheSpeedTest

```{autodocx-docstring} duck.utils.caching.CacheSpeedTest
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.utils.caching.CacheSpeedTest.__init__
```

````{py:method} compare_performance()
:canonical: duck.utils.caching.CacheSpeedTest.compare_performance

```{autodocx-docstring} duck.utils.caching.CacheSpeedTest.compare_performance
```

````

````{py:method} execute_all()
:canonical: duck.utils.caching.CacheSpeedTest.execute_all

```{autodocx-docstring} duck.utils.caching.CacheSpeedTest.execute_all
```

````

````{py:method} generate_random_string(length)
:canonical: duck.utils.caching.CacheSpeedTest.generate_random_string
:staticmethod:

```{autodocx-docstring} duck.utils.caching.CacheSpeedTest.generate_random_string
```

````

````{py:attribute} instances
:canonical: duck.utils.caching.CacheSpeedTest.instances
:value: >
   None

```{autodocx-docstring} duck.utils.caching.CacheSpeedTest.instances
```

````

````{py:method} print_summary()
:canonical: duck.utils.caching.CacheSpeedTest.print_summary

```{autodocx-docstring} duck.utils.caching.CacheSpeedTest.print_summary
```

````

````{py:method} run_test(instance)
:canonical: duck.utils.caching.CacheSpeedTest.run_test

```{autodocx-docstring} duck.utils.caching.CacheSpeedTest.run_test
```

````

````{py:method} test_clear(instance)
:canonical: duck.utils.caching.CacheSpeedTest.test_clear

```{autodocx-docstring} duck.utils.caching.CacheSpeedTest.test_clear
```

````

````{py:method} test_create(instance)
:canonical: duck.utils.caching.CacheSpeedTest.test_create

```{autodocx-docstring} duck.utils.caching.CacheSpeedTest.test_create
```

````

````{py:method} test_del(instance)
:canonical: duck.utils.caching.CacheSpeedTest.test_del

```{autodocx-docstring} duck.utils.caching.CacheSpeedTest.test_del
```

````

````{py:method} test_get(instance)
:canonical: duck.utils.caching.CacheSpeedTest.test_get

```{autodocx-docstring} duck.utils.caching.CacheSpeedTest.test_get
```

````

````{py:method} test_set(instance)
:canonical: duck.utils.caching.CacheSpeedTest.test_set

```{autodocx-docstring} duck.utils.caching.CacheSpeedTest.test_set
```

````

`````

`````{py:class} DynamicFileCache(cache_dir: str, cache_limit=1000000000.0, cached_objs_limit: int = 128)
:canonical: duck.utils.caching.DynamicFileCache

Bases: {py:obj}`duck.utils.caching.CacheBase`

```{autodocx-docstring} duck.utils.caching.DynamicFileCache
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.utils.caching.DynamicFileCache.__init__
```

````{py:method} _create_new_cache_path()
:canonical: duck.utils.caching.DynamicFileCache._create_new_cache_path

```{autodocx-docstring} duck.utils.caching.DynamicFileCache._create_new_cache_path
```

````

````{py:method} _get_cache_path() -> str
:canonical: duck.utils.caching.DynamicFileCache._get_cache_path

```{autodocx-docstring} duck.utils.caching.DynamicFileCache._get_cache_path
```

````

````{py:method} _reload_cache_files()
:canonical: duck.utils.caching.DynamicFileCache._reload_cache_files

```{autodocx-docstring} duck.utils.caching.DynamicFileCache._reload_cache_files
```

````

````{py:property} cache_obj
:canonical: duck.utils.caching.DynamicFileCache.cache_obj

```{autodocx-docstring} duck.utils.caching.DynamicFileCache.cache_obj
```

````

````{py:method} clear()
:canonical: duck.utils.caching.DynamicFileCache.clear

```{autodocx-docstring} duck.utils.caching.DynamicFileCache.clear
```

````

````{py:method} close()
:canonical: duck.utils.caching.DynamicFileCache.close

```{autodocx-docstring} duck.utils.caching.DynamicFileCache.close
```

````

````{py:method} delete(key: str)
:canonical: duck.utils.caching.DynamicFileCache.delete

```{autodocx-docstring} duck.utils.caching.DynamicFileCache.delete
```

````

````{py:method} get(key: str) -> typing.Any
:canonical: duck.utils.caching.DynamicFileCache.get

```{autodocx-docstring} duck.utils.caching.DynamicFileCache.get
```

````

````{py:method} get_cache_obj(path: str) -> duck.utils.caching.PersistentFileCache
:canonical: duck.utils.caching.DynamicFileCache.get_cache_obj
:staticmethod:

```{autodocx-docstring} duck.utils.caching.DynamicFileCache.get_cache_obj
```

````

````{py:method} set(key: str, data: typing.Any, expiry: float | int = None)
:canonical: duck.utils.caching.DynamicFileCache.set

```{autodocx-docstring} duck.utils.caching.DynamicFileCache.set
```

````

`````

`````{py:class} InMemoryCache(maxkeys=None, *_)
:canonical: duck.utils.caching.InMemoryCache

Bases: {py:obj}`duck.utils.caching.CacheBase`

```{autodocx-docstring} duck.utils.caching.InMemoryCache
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.utils.caching.InMemoryCache.__init__
```

````{py:method} clear()
:canonical: duck.utils.caching.InMemoryCache.clear

````

````{py:method} close()
:canonical: duck.utils.caching.InMemoryCache.close

```{autodocx-docstring} duck.utils.caching.InMemoryCache.close
```

````

````{py:method} delete(key: str)
:canonical: duck.utils.caching.InMemoryCache.delete

````

````{py:method} get(key: str, default: typing.Any = None, pop: bool = False) -> typing.Any
:canonical: duck.utils.caching.InMemoryCache.get

```{autodocx-docstring} duck.utils.caching.InMemoryCache.get
```

````

````{py:method} has(key: str)
:canonical: duck.utils.caching.InMemoryCache.has

```{autodocx-docstring} duck.utils.caching.InMemoryCache.has
```

````

````{py:method} set(key: str, value: typing.Any, expiry=None)
:canonical: duck.utils.caching.InMemoryCache.set

```{autodocx-docstring} duck.utils.caching.InMemoryCache.set
```

````

`````

`````{py:class} KeyAsFolderCache(cache_dir: str)
:canonical: duck.utils.caching.KeyAsFolderCache

Bases: {py:obj}`duck.utils.caching.CacheBase`

```{autodocx-docstring} duck.utils.caching.KeyAsFolderCache
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.utils.caching.KeyAsFolderCache.__init__
```

````{py:method} clear()
:canonical: duck.utils.caching.KeyAsFolderCache.clear

```{autodocx-docstring} duck.utils.caching.KeyAsFolderCache.clear
```

````

````{py:method} close()
:canonical: duck.utils.caching.KeyAsFolderCache.close

```{autodocx-docstring} duck.utils.caching.KeyAsFolderCache.close
```

````

````{py:method} delete(key: str)
:canonical: duck.utils.caching.KeyAsFolderCache.delete

```{autodocx-docstring} duck.utils.caching.KeyAsFolderCache.delete
```

````

````{py:method} get(key: str) -> typing.Any
:canonical: duck.utils.caching.KeyAsFolderCache.get

```{autodocx-docstring} duck.utils.caching.KeyAsFolderCache.get
```

````

````{py:method} get_cache_files(d: str)
:canonical: duck.utils.caching.KeyAsFolderCache.get_cache_files
:staticmethod:

```{autodocx-docstring} duck.utils.caching.KeyAsFolderCache.get_cache_files
```

````

````{py:method} get_cache_obj(path: str) -> duck.utils.caching.PersistentFileCache
:canonical: duck.utils.caching.KeyAsFolderCache.get_cache_obj
:staticmethod:

```{autodocx-docstring} duck.utils.caching.KeyAsFolderCache.get_cache_obj
```

````

````{py:method} set(key: str, data: typing.Any, expiry: int | float = None)
:canonical: duck.utils.caching.KeyAsFolderCache.set

```{autodocx-docstring} duck.utils.caching.KeyAsFolderCache.set
```

````

`````

`````{py:class} PersistentFileCache(path: str, cache_size: int = None)
:canonical: duck.utils.caching.PersistentFileCache

Bases: {py:obj}`duck.utils.caching.CacheBase`

```{autodocx-docstring} duck.utils.caching.PersistentFileCache
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.utils.caching.PersistentFileCache.__init__
```

````{py:method} clear()
:canonical: duck.utils.caching.PersistentFileCache.clear

```{autodocx-docstring} duck.utils.caching.PersistentFileCache.clear
```

````

````{py:method} close()
:canonical: duck.utils.caching.PersistentFileCache.close

```{autodocx-docstring} duck.utils.caching.PersistentFileCache.close
```

````

````{py:property} closed
:canonical: duck.utils.caching.PersistentFileCache.closed

```{autodocx-docstring} duck.utils.caching.PersistentFileCache.closed
```

````

````{py:method} delete(key: str)
:canonical: duck.utils.caching.PersistentFileCache.delete

```{autodocx-docstring} duck.utils.caching.PersistentFileCache.delete
```

````

````{py:method} get(key: str)
:canonical: duck.utils.caching.PersistentFileCache.get

```{autodocx-docstring} duck.utils.caching.PersistentFileCache.get
```

````

````{py:method} set(key: str, _obj: typing.Any, expiry: int | float = None)
:canonical: duck.utils.caching.PersistentFileCache.set

```{autodocx-docstring} duck.utils.caching.PersistentFileCache.set
```

````

`````
