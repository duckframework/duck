# {py:mod}`duck.utils.caching`

```{py:module} duck.utils.caching
```

```{autodocx-docstring} duck.utils.caching
:allowtitles:
```

## Submodules

```{toctree}
:titlesonly:
:maxdepth: 1

duck.utils.caching.encrypted
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

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`MISSING <duck.utils.caching.MISSING>`
  - ```{autodocx-docstring} duck.utils.caching.MISSING
    :summary:
    ```
````

### API

`````{py:class} CacheBase
:canonical: duck.utils.caching.CacheBase

```{autodocx-docstring} duck.utils.caching.CacheBase
```

````{py:method} clear() -> None
:canonical: duck.utils.caching.CacheBase.clear
:abstractmethod:

```{autodocx-docstring} duck.utils.caching.CacheBase.clear
```

````

````{py:method} delete(key: str) -> None
:canonical: duck.utils.caching.CacheBase.delete
:abstractmethod:

```{autodocx-docstring} duck.utils.caching.CacheBase.delete
```

````

````{py:method} get(key: str, default: typing.Any = None) -> typing.Any
:canonical: duck.utils.caching.CacheBase.get
:abstractmethod:

```{autodocx-docstring} duck.utils.caching.CacheBase.get
```

````

````{py:method} pop(key: str, default: typing.Any = MISSING) -> typing.Any
:canonical: duck.utils.caching.CacheBase.pop
:abstractmethod:

```{autodocx-docstring} duck.utils.caching.CacheBase.pop
```

````

````{py:method} save()
:canonical: duck.utils.caching.CacheBase.save

```{autodocx-docstring} duck.utils.caching.CacheBase.save
```

````

````{py:method} set(key: str, value: typing.Any, expiry: int | float | None = None) -> None
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

`````{py:class} DynamicFileCache(cache_dir: str, cache_limit: int = DEFAULT_SHARD_SIZE, cached_objs_limit: int = 128)
:canonical: duck.utils.caching.DynamicFileCache

Bases: {py:obj}`duck.utils.caching.CacheBase`

```{autodocx-docstring} duck.utils.caching.DynamicFileCache
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.utils.caching.DynamicFileCache.__init__
```

````{py:attribute} DEFAULT_SHARD_SIZE
:canonical: duck.utils.caching.DynamicFileCache.DEFAULT_SHARD_SIZE
:type: int
:value: >
   1000000000

```{autodocx-docstring} duck.utils.caching.DynamicFileCache.DEFAULT_SHARD_SIZE
```

````

````{py:method} async_clear() -> None
:canonical: duck.utils.caching.DynamicFileCache.async_clear
:async:

```{autodocx-docstring} duck.utils.caching.DynamicFileCache.async_clear
```

````

````{py:method} async_delete(key: str) -> None
:canonical: duck.utils.caching.DynamicFileCache.async_delete
:async:

```{autodocx-docstring} duck.utils.caching.DynamicFileCache.async_delete
```

````

````{py:method} async_get(key: str, default: typing.Any = None) -> typing.Any
:canonical: duck.utils.caching.DynamicFileCache.async_get
:async:

```{autodocx-docstring} duck.utils.caching.DynamicFileCache.async_get
```

````

````{py:method} async_pop(key: str, default: typing.Any = MISSING) -> typing.Any
:canonical: duck.utils.caching.DynamicFileCache.async_pop
:async:

```{autodocx-docstring} duck.utils.caching.DynamicFileCache.async_pop
```

````

````{py:method} async_set(key: str, value: typing.Any, expiry: int | float | None = None) -> None
:canonical: duck.utils.caching.DynamicFileCache.async_set
:async:

```{autodocx-docstring} duck.utils.caching.DynamicFileCache.async_set
```

````

````{py:method} clear() -> None
:canonical: duck.utils.caching.DynamicFileCache.clear

```{autodocx-docstring} duck.utils.caching.DynamicFileCache.clear
```

````

````{py:method} close() -> None
:canonical: duck.utils.caching.DynamicFileCache.close

```{autodocx-docstring} duck.utils.caching.DynamicFileCache.close
```

````

````{py:method} create_new_shard() -> str
:canonical: duck.utils.caching.DynamicFileCache.create_new_shard

```{autodocx-docstring} duck.utils.caching.DynamicFileCache.create_new_shard
```

````

````{py:method} delete(key: str) -> None
:canonical: duck.utils.caching.DynamicFileCache.delete

```{autodocx-docstring} duck.utils.caching.DynamicFileCache.delete
```

````

````{py:method} get(key: str, default: typing.Any = None) -> typing.Any
:canonical: duck.utils.caching.DynamicFileCache.get

```{autodocx-docstring} duck.utils.caching.DynamicFileCache.get
```

````

````{py:method} get_shard(path: str) -> duck.utils.caching.PersistentFileCache
:canonical: duck.utils.caching.DynamicFileCache.get_shard

```{autodocx-docstring} duck.utils.caching.DynamicFileCache.get_shard
```

````

````{py:method} get_writable_shard_path() -> str
:canonical: duck.utils.caching.DynamicFileCache.get_writable_shard_path

```{autodocx-docstring} duck.utils.caching.DynamicFileCache.get_writable_shard_path
```

````

````{py:method} pop(key: str, default: typing.Any = MISSING) -> typing.Any
:canonical: duck.utils.caching.DynamicFileCache.pop

```{autodocx-docstring} duck.utils.caching.DynamicFileCache.pop
```

````

````{py:method} reload_shard_paths() -> None
:canonical: duck.utils.caching.DynamicFileCache.reload_shard_paths

```{autodocx-docstring} duck.utils.caching.DynamicFileCache.reload_shard_paths
```

````

````{py:method} set(key: str, value: typing.Any, expiry: int | float | None = None) -> None
:canonical: duck.utils.caching.DynamicFileCache.set

```{autodocx-docstring} duck.utils.caching.DynamicFileCache.set
```

````

`````

`````{py:class} InMemoryCache(maxkeys: int | None = None)
:canonical: duck.utils.caching.InMemoryCache

Bases: {py:obj}`duck.utils.caching.CacheBase`

```{autodocx-docstring} duck.utils.caching.InMemoryCache
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.utils.caching.InMemoryCache.__init__
```

````{py:method} _evict(key: str) -> None
:canonical: duck.utils.caching.InMemoryCache._evict

```{autodocx-docstring} duck.utils.caching.InMemoryCache._evict
```

````

````{py:method} _is_expired(key: str) -> bool
:canonical: duck.utils.caching.InMemoryCache._is_expired

```{autodocx-docstring} duck.utils.caching.InMemoryCache._is_expired
```

````

````{py:method} async_clear() -> None
:canonical: duck.utils.caching.InMemoryCache.async_clear
:async:

```{autodocx-docstring} duck.utils.caching.InMemoryCache.async_clear
```

````

````{py:method} async_delete(key: str) -> None
:canonical: duck.utils.caching.InMemoryCache.async_delete
:async:

```{autodocx-docstring} duck.utils.caching.InMemoryCache.async_delete
```

````

````{py:method} async_get(key: str, default: typing.Any = None) -> typing.Any
:canonical: duck.utils.caching.InMemoryCache.async_get
:async:

```{autodocx-docstring} duck.utils.caching.InMemoryCache.async_get
```

````

````{py:method} async_pop(key: str, default: typing.Any = MISSING) -> typing.Any
:canonical: duck.utils.caching.InMemoryCache.async_pop
:async:

```{autodocx-docstring} duck.utils.caching.InMemoryCache.async_pop
```

````

````{py:method} async_set(key: str, value: typing.Any, expiry: int | float | None = None) -> None
:canonical: duck.utils.caching.InMemoryCache.async_set
:async:

```{autodocx-docstring} duck.utils.caching.InMemoryCache.async_set
```

````

````{py:method} clear() -> None
:canonical: duck.utils.caching.InMemoryCache.clear

```{autodocx-docstring} duck.utils.caching.InMemoryCache.clear
```

````

````{py:method} close() -> None
:canonical: duck.utils.caching.InMemoryCache.close

```{autodocx-docstring} duck.utils.caching.InMemoryCache.close
```

````

````{py:method} delete(key: str) -> None
:canonical: duck.utils.caching.InMemoryCache.delete

```{autodocx-docstring} duck.utils.caching.InMemoryCache.delete
```

````

````{py:method} get(key: str, default: typing.Any = None) -> typing.Any
:canonical: duck.utils.caching.InMemoryCache.get

```{autodocx-docstring} duck.utils.caching.InMemoryCache.get
```

````

````{py:method} has(key: str) -> bool
:canonical: duck.utils.caching.InMemoryCache.has

```{autodocx-docstring} duck.utils.caching.InMemoryCache.has
```

````

````{py:method} pop(key: str, default: typing.Any = MISSING) -> typing.Any
:canonical: duck.utils.caching.InMemoryCache.pop

```{autodocx-docstring} duck.utils.caching.InMemoryCache.pop
```

````

````{py:method} set(key: str, value: typing.Any, expiry: int | float | None = None) -> None
:canonical: duck.utils.caching.InMemoryCache.set

```{autodocx-docstring} duck.utils.caching.InMemoryCache.set
```

````

`````

`````{py:class} KeyAsFolderCache(cache_dir: str, cached_objs_limit: int = DEFAULT_CACHE_OBJ_LIMIT)
:canonical: duck.utils.caching.KeyAsFolderCache

Bases: {py:obj}`duck.utils.caching.CacheBase`

```{autodocx-docstring} duck.utils.caching.KeyAsFolderCache
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.utils.caching.KeyAsFolderCache.__init__
```

````{py:attribute} DEFAULT_CACHE_OBJ_LIMIT
:canonical: duck.utils.caching.KeyAsFolderCache.DEFAULT_CACHE_OBJ_LIMIT
:type: int
:value: >
   128

```{autodocx-docstring} duck.utils.caching.KeyAsFolderCache.DEFAULT_CACHE_OBJ_LIMIT
```

````

````{py:method} _remove_key_dir(key_dir: str) -> None
:canonical: duck.utils.caching.KeyAsFolderCache._remove_key_dir

```{autodocx-docstring} duck.utils.caching.KeyAsFolderCache._remove_key_dir
```

````

````{py:method} async_clear() -> None
:canonical: duck.utils.caching.KeyAsFolderCache.async_clear
:async:

```{autodocx-docstring} duck.utils.caching.KeyAsFolderCache.async_clear
```

````

````{py:method} async_delete(key: str) -> None
:canonical: duck.utils.caching.KeyAsFolderCache.async_delete
:async:

```{autodocx-docstring} duck.utils.caching.KeyAsFolderCache.async_delete
```

````

````{py:method} async_get(key: str, default: typing.Any = None) -> typing.Any
:canonical: duck.utils.caching.KeyAsFolderCache.async_get
:async:

```{autodocx-docstring} duck.utils.caching.KeyAsFolderCache.async_get
```

````

````{py:method} async_pop(key: str, default: typing.Any = MISSING) -> typing.Any
:canonical: duck.utils.caching.KeyAsFolderCache.async_pop
:async:

```{autodocx-docstring} duck.utils.caching.KeyAsFolderCache.async_pop
```

````

````{py:method} async_set(key: str, value: typing.Any, expiry: int | float | None = None) -> None
:canonical: duck.utils.caching.KeyAsFolderCache.async_set
:async:

```{autodocx-docstring} duck.utils.caching.KeyAsFolderCache.async_set
```

````

````{py:method} clear() -> None
:canonical: duck.utils.caching.KeyAsFolderCache.clear

```{autodocx-docstring} duck.utils.caching.KeyAsFolderCache.clear
```

````

````{py:method} close() -> None
:canonical: duck.utils.caching.KeyAsFolderCache.close

```{autodocx-docstring} duck.utils.caching.KeyAsFolderCache.close
```

````

````{py:method} delete(key: str) -> None
:canonical: duck.utils.caching.KeyAsFolderCache.delete

```{autodocx-docstring} duck.utils.caching.KeyAsFolderCache.delete
```

````

````{py:method} get(key: str, default: typing.Any = None) -> typing.Any
:canonical: duck.utils.caching.KeyAsFolderCache.get

```{autodocx-docstring} duck.utils.caching.KeyAsFolderCache.get
```

````

````{py:method} get_key_dir(key: str) -> str
:canonical: duck.utils.caching.KeyAsFolderCache.get_key_dir

```{autodocx-docstring} duck.utils.caching.KeyAsFolderCache.get_key_dir
```

````

````{py:method} get_shard(path: str) -> duck.utils.caching.PersistentFileCache
:canonical: duck.utils.caching.KeyAsFolderCache.get_shard

```{autodocx-docstring} duck.utils.caching.KeyAsFolderCache.get_shard
```

````

````{py:method} live_key_dirs() -> list[pathlib.Path]
:canonical: duck.utils.caching.KeyAsFolderCache.live_key_dirs

```{autodocx-docstring} duck.utils.caching.KeyAsFolderCache.live_key_dirs
```

````

````{py:method} pop(key: str, default: typing.Any = MISSING) -> typing.Any
:canonical: duck.utils.caching.KeyAsFolderCache.pop

```{autodocx-docstring} duck.utils.caching.KeyAsFolderCache.pop
```

````

````{py:method} set(key: str, value: typing.Any, expiry: int | float | None = None) -> None
:canonical: duck.utils.caching.KeyAsFolderCache.set

```{autodocx-docstring} duck.utils.caching.KeyAsFolderCache.set
```

````

`````

````{py:data} MISSING
:canonical: duck.utils.caching.MISSING
:value: >
   'object(...)'

```{autodocx-docstring} duck.utils.caching.MISSING
```

````

`````{py:class} PersistentFileCache(path: str, cache_size: int | None = None)
:canonical: duck.utils.caching.PersistentFileCache

Bases: {py:obj}`duck.utils.caching.CacheBase`

```{autodocx-docstring} duck.utils.caching.PersistentFileCache
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.utils.caching.PersistentFileCache.__init__
```

````{py:method} _require_open() -> None
:canonical: duck.utils.caching.PersistentFileCache._require_open

```{autodocx-docstring} duck.utils.caching.PersistentFileCache._require_open
```

````

````{py:method} async_clear() -> None
:canonical: duck.utils.caching.PersistentFileCache.async_clear
:async:

```{autodocx-docstring} duck.utils.caching.PersistentFileCache.async_clear
```

````

````{py:method} async_delete(key: str) -> None
:canonical: duck.utils.caching.PersistentFileCache.async_delete
:async:

```{autodocx-docstring} duck.utils.caching.PersistentFileCache.async_delete
```

````

````{py:method} async_get(key: str, default: typing.Any = None) -> typing.Any
:canonical: duck.utils.caching.PersistentFileCache.async_get
:async:

```{autodocx-docstring} duck.utils.caching.PersistentFileCache.async_get
```

````

````{py:method} async_pop(key: str, default: typing.Any = MISSING) -> typing.Any
:canonical: duck.utils.caching.PersistentFileCache.async_pop
:async:

```{autodocx-docstring} duck.utils.caching.PersistentFileCache.async_pop
```

````

````{py:method} async_set(key: str, value: typing.Any, expiry: int | float | None = None) -> None
:canonical: duck.utils.caching.PersistentFileCache.async_set
:async:

```{autodocx-docstring} duck.utils.caching.PersistentFileCache.async_set
```

````

````{py:method} clear() -> None
:canonical: duck.utils.caching.PersistentFileCache.clear

```{autodocx-docstring} duck.utils.caching.PersistentFileCache.clear
```

````

````{py:method} close() -> None
:canonical: duck.utils.caching.PersistentFileCache.close

```{autodocx-docstring} duck.utils.caching.PersistentFileCache.close
```

````

````{py:method} delete(key: str) -> None
:canonical: duck.utils.caching.PersistentFileCache.delete

```{autodocx-docstring} duck.utils.caching.PersistentFileCache.delete
```

````

````{py:method} get(key: str, default: typing.Any = None) -> typing.Any
:canonical: duck.utils.caching.PersistentFileCache.get

```{autodocx-docstring} duck.utils.caching.PersistentFileCache.get
```

````

````{py:method} pop(key: str, default: typing.Any = MISSING) -> typing.Any
:canonical: duck.utils.caching.PersistentFileCache.pop

```{autodocx-docstring} duck.utils.caching.PersistentFileCache.pop
```

````

````{py:method} set(key: str, value: typing.Any, expiry: int | float | None = None) -> None
:canonical: duck.utils.caching.PersistentFileCache.set

```{autodocx-docstring} duck.utils.caching.PersistentFileCache.set
```

````

`````
