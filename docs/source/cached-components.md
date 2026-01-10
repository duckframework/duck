# 🌀 Component Caching Utilities

**Module:** `duck.html.components.utils.caching`

This module provides a flexible, high-performance caching system for Duck HTML components.  
It allows component instances to be reused across renders while preserving correctness, immutability, and thread safety.  

Caching is especially useful for:
- Expensive component initialization
- Static or semi-static UI elements
- Reducing render latency under load

---

## Key Concepts

### What Is Cached?

- **Component instances**, not rendered HTML
- Cached components may be **frozen** to enable fast re-rendering
- Returned components are **copied by default** to avoid tree ownership conflicts

### Threading Model

- Cached components may trigger background tasks (load, pre-render, VDOM computation)
- Background execution uses a shared component thread pool
- Excessive background activity may increase latency — use caching thoughtfully

---

## Default Cache Backend

```py
DEFAULT_CACHE_BACKEND = InMemoryCache(maxkeys=2048)
```

- Uses an in-memory LRU-style cache
- Automatically evicts older entries when the limit is reached
- Custom backends may be supplied

---

## Exceptions

### `ComponentCachingError`

Raised when:
- Invalid cache configuration is provided
- Target keys are missing
- Cache key computation fails

---

## Cache Key Generation

### `make_cache_key(...)`

```py
make_cache_key(
    component_cls,
    args,
    kwargs,
    namespace: Optional[str | Callable] = None
) -> Tuple
```

**How keys are constructed:**
- Optional namespace prefix
- Component class
- Frozen positional arguments
- Frozen keyword arguments

Namespaces allow **bulk invalidation** and logical grouping.

---

## `cached_component` Decorator

```py
@cached_component(...)
class MyComponent(Component):
    ...
```

This decorator enables component-level caching with fine-grained control.

---

### Parameters

#### `targets`

```py
Optional[List[str | Callable]]
```

Explicitly define what participates in caching.

- Strings → keyword argument names
- Callables → custom cache key extractors

Example:
```py
targets=['id', lambda *a, **k: k['user'].id]
```

> When `targets` is used:
> - Positional args are ignored
> - `ignore_args` and `ignore_kwargs` are invalid

---

#### `cache_backend`
Custom backend implementing:
- `get(key)`
- `set(key, value, expiry=None)`

Defaults to `InMemoryCache`.

---

#### `expiry`
```py
Optional[float]
```
Cache TTL in seconds.

---

#### `namespace`
```py
Optional[str | Callable]
```
Adds a prefix to cache keys.

Useful for:
- Versioning
- Bulk invalidation
- Feature grouping

---

#### `ignore_args`
```py
Optional[List[int]]
```
Indices of positional arguments to exclude from the cache key.

---

#### `ignore_kwargs`
```py
Optional[List[str]]
```
Keyword argument names to exclude from the cache key.

---

#### `skip_cache_attr`
```py
str = 'skip_cache'
```
If a component instance has this attribute set to `True`, caching is skipped.

Useful for:
- Debugging
- One-off renders

---

#### `on_cache_result`

```py
Optional[Callable]
```
Hook executed when a cached component is returned.  

Typical use cases:
- Reinitializing transient state
- Rebinding event handlers

---

#### `freeze`

```py
bool = False
```
If enabled:
- Cached components are frozen
- Enables fast, immutable re-rendering
- Required for static components

---

#### `return_copy`

```py
bool = True
```
Controls whether a copy of the cached component is returned.  

Why this matters:
- Prevents component tree ownership conflicts
- Avoids `ComponentCopyError`
- Ensures isolation between renders

Special rules:
- Frozen `Page` components are **never copied**

---

#### `_no_caching`

Internal flag used by higher-level decorators to disable caching.

---

## Runtime Behavior

### Cache Miss

1. Component is instantiated
2. Cached if allowed
3. Frozen if requested
4. Background tasks may be scheduled
5. Copy returned (if enabled)

### Cache Hit

1. Cached component retrieved
2. `_is_from_cache` flag set
3. Copy returned (if enabled)
4. `on_cache_result` hook executed

---

## Background Optimization

When returning a copy:
- The **original cached component** may perform:
  - `load()`
  - `pre_render()`
  - `render()`
  - `to_vdom`

This ensures subsequent cache hits are faster.

Task execution strategy:
- Loaded components → fine-grained tasks
- Unloaded components → batched execution

---

## Functional API

### `CachedComponent(...)`

```py
CachedComponent(component_cls: Type, **cache_options)
```
Creates a cached component factory **without decorators**.

#### Example

```py
cached_btn = CachedComponent(
    Button,
    namespace='welcome-btn',
    targets=['id', 'text'],
)

btn = cached_btn(id='btn-1', text='Hello')
btn.is_from_cache()  # False on first call
```

---

# Static Component Utilities

**Module:** `duck.html.components.utils.static`

This module builds on the caching system to define **static (fully frozen) components**.

Static components:
- Are cached
- Are frozen immediately
- Are safe to reuse across requests
- Offer maximal rendering performance

---

## `static_component` Decorator

```py
@static_component(...)
class MyStaticComponent(Component):
    ...
```

This is a specialized wrapper around `cached_component` with:
- `freeze=True`
- Optional caching toggle
- Simplified API

---

### Parameters

#### `use_caching`

```py
bool = True
```
Allows static freezing **without caching** when disabled.

---

#### `cache_targets`

Equivalent to `targets` in `cached_component`.

---

#### `cache_backend`

Custom cache backend.

---

#### `cache_expiry`

TTL for static cache entries.

---

#### `cache_namespace`

Namespace prefix for static components.

---

#### `cache_ignore_args`

Indices of positional arguments to ignore.

---

#### `cache_ignore_kwargs`

Keyword argument names to ignore.

---

#### `skip_cache_attr`

Attribute name used to skip caching.

---

#### `on_cache_result`

Hook executed on cache hits.

---

#### `return_copy`

Controls whether copies are returned.

- Defaults to `True`
- Frozen `Page` components are still returned as-is

---

### Example

```py
@static_component()
class MyStaticButton(Button):
    pass

btn = MyStaticButton(text='Hello')
btn.is_frozen()        # True
btn.is_from_cache()    # False

btn2 = MyStaticButton(text='Hello')
btn2.is_from_cache()   # True
```

---

## Functional API

### `StaticComponent(...)`

```py
StaticComponent(component_cls: Type, **static_options)
```
Creates a static component factory without decorators.

#### Example

```py
static_btn = StaticComponent(
    Button,
    cache_targets=['id', 'text'],
)

btn = static_btn(id='btn', text='Hello')
btn.is_frozen()       # True
btn.is_from_cache()   # False initially
```

---

## When to Use What

| Use Case | Recommended |
|--------|-------------|
| Expensive dynamic components | `cached_component` |
| Fully static UI elements | `static_component` |
| Functional factories | `CachedComponent` / `StaticComponent` |
| Maximum performance | Static + freeze |

---

## Summary

- Caching operates at the **component instance level**
- Copies ensure safety across render trees
- Freezing enables near-zero-cost re-rendering
- Static components are the fastest option
- Background execution optimizes future cache hits

This system is designed to scale cleanly under high concurrency while preserving correctness and developer control.
