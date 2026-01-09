# 🗃 Cached Views

Duck’s **cached view system** provides a high-performance, flexible way to cache the output of both synchronous and asynchronous views.
It offers fine-grained control over what contributes to the cache key: request attributes, request callables, or fully custom Python callables.

Unlike traditional caching decorators, Duck’s `cached_view` is designed for:

* **Deterministic cache keys**
* **Dynamic argument/callable resolution**
* **Async awareness**
* **Safe component caching**
* **Optional namespace isolation**
* **Per-request debugging skips**
* **Auto-adapted backends (sync/async)**

---

## ⚙️ Overview

The core concept:

```py
@cached_view(targets=..., expiry=..., namespace=..., cache_backend=...)
def view(request, ...):
    ...
```

Where the **targets** determine *what uniquely identifies* the cached result.

Duck offers:

* In-memory caching (`InMemoryCache`) as default
* Pluggable backends with `.get()` / `.set()` API
* Automatic wrapping for async ↔ sync compatibility

After the first call, subsequent invocations return the cached result instantly, skipping view execution entirely.

---

## 🛸 `cached_view` Decorator

The decorator handles:

### ✔ Request attribute-based caching

`targets=["path", "method"]`

### ✔ Callable-based caching

`targets={static_mtime: {'args': ()}}`

### ✔ Request callable targets

`targets={'get_user_id': {'args': ()}}`

### ✔ External pure functions

`targets={compute_hash: {'args': ('{request.path}',)}}`

Targets are resolved **before** executing the view.
The resolved values are then normalized into a stable, hashable structure (`frozenset + tuple`).

---

## 📌 Parameters

| Parameter                 | Type                                                        | Description                                                                                                 |
| ------------------------- | ----------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| `targets`                 | `List[str]` or `Dict[Union[str, Callable], Dict[str, Any]]` | Required. Defines which request attributes or callable results contribute to the cache key.                 |
| `expiry`                  | `Optional[float]`                                           | TTL in seconds; default is backend-defined.                                                                 |
| `cache_backend`           | any object with `get(key)` & `set(key, value, ttl)`         | Custom cache backend (sync or async).                                                                       |
| `namespace`               | `Optional[str or Callable]`                                 | Optional namespace prefix for cache isolation. Useful for per-user or per-tenant caching.                   |
| `skip_cache_attr`         | `str`                                                       | Request attribute name that forces bypass of caching (for debugging). Default `"skip_cache"`.               |
| `on_cache_result`         | `Callable`                                                  | Hook executed when a cached value is returned. Useful if the cached result requires reinitialization.       |
| `returns_static_response` | `bool`                                                      | Indicates the response is static and safe to cache even if components are returned. Avoids safety warnings. |

---

## 🧠 How Targets Work

### ✔ Attribute Targets (simple)

```py
@cached_view(targets=["path", "method"])
def handler(request):
    return HttpResponse("OK")
```

### ✔ Callable Targets (complex)

```py
@cached_view(targets={static_mtime: {'args': None}})
def serve_static(request, staticfile):
    return FileResponse(...)
```

### ✔ Request Callable Targets

```py
@cached_view(targets={'compute_key': {'args': ('{request.method}',)}})
def handler(request):
    ...
```

### ✔ External Functions

```py
@cached_view(targets={my_hash_fn: {'args': ('{request.path}',)}})
def handler(request):
    ...
```

### Dynamic formatting supported everywhere

* `{request.path}`
* `{request.user.id}`
* etc.

---

## 🧩 Namespace Support

Namespaces allow isolated cached values:

```py
@cached_view(
    targets=['path'],
    namespace=lambda request: request.COOKIES.get('session_id')
)
def dashboard(request):
    ...
```

This means:

* Each user gets their own cache bucket.
* Cache invalidation is trivial: change namespace → old keys ignored.

---

## 🐛 Debugging with Skip

```py
request.skip_cache = True
```

or with a custom attribute:

```py
@cached_view(targets=['path'], skip_cache_attr='debug_skip')
```

Allows bypassing cache for *that single request*.

---

## 🪝 on_cache_result Hook

A callable executed whenever a cached result is retrieved:

```py
def rehydrate(component):
    component.rebind_runtime_state()

@cached_view(targets=['path'], on_cache_result=rehydrate)
def handler(request):
    ...
```

Useful for UI components, objects with state, etc.

---

## 🧱 Internal Behavior

### 1. **Target Resolution**

Extract values from:

* request attributes
* request callables
* external Python callables

### 2. **Key Construction**

A stable structure:

```
(
    namespace_string_or_empty,
    frozenset(resolved_targets.items()),
    call_args,
    frozenset(call_kwargs.items())
)
```

This guarantees:

* Deterministic hashing
* Reproducibility
* No collision from dict order

### 3. **Backend Lookup**

Sync wrappers for async backends and vice-versa are created automatically.

### 4. **View Execution or Cache Return**

### 5. **Cache Update (if allowed)**

Stored with expiry if provided.

---

## 🛠 Examples

### Simple

```py
@cached_view(targets=['path'])
def handler(request):
    return HttpResponse("OK")
```

### Async Class-Based View

```py
class MyView(View):
    @cached_view(targets=['fullpath', 'method'])
    async def run(self):
        return HttpResponse("OK")
```

### Callable-based Caching

```py
@cached_view(targets={compute_hash: {'args': ('{request.path}',)}})
def handler(request):
    return HttpResponse("OK")
```

### Static file caching

```py
@cached_view(targets={static_mtime: {'args': None}})
def staticfiles(request, staticfile):
    return FileResponse(...)
```

---

## ⚡ Best Practices

1. Cache **expensive** or **read-heavy** views.
2. Avoid caching highly personalized output unless namespaced.
3. Use callable targets for:

   * mtime-based invalidation
   * database-derived cache keys
   * user-scoped session keys
4. Use `SkipViewCaching` to disable caching when prerequisites fail.

---

## ⚖ Comparison to Other Frameworks

### Django (`cache_page`, low-level API)

| Feature                 | Django           | Duck               |
| ----------------------- | ---------------- | ------------------ |
| Async support           | partial          | full & automatic   |
| Callable targets        | ❌                | ✔ full             |
| Per-request skip        | ❌                | ✔                  |
| Namespaces              | manual prefixing | built-in           |
| Deterministic keys      | basic            | strong, structured |
| Auto backend sync/async | ❌                | ✔                  |
| Dynamic format args     | ❌                | ✔                  |

### Flask (`flask-caching`)

| Feature                | Flask   | Duck                  |
| ---------------------- | ------- | --------------------- |
| Async                  | ❌       | ✔                     |
| Callable targets       | limited | ✔ arbitrary callables |
| Namespaced keys        | manual  | ✔                     |
| Request attribute keys | partial | ✔ full                |

### FastAPI (`Depends` + custom caching)

| Feature                       | FastAPI          | Duck |
| ----------------------------- | ---------------- | ---- |
| Decorator-based caching       | ❌ (not built-in) | ✔    |
| Sync/async backend adaptation | manual           | ✔    |
| Dynamic request formatting    | ❌                | ✔    |

### Next.js (Edge/Static)

| Feature                 | Next.js | Duck                            |
| ----------------------- | ------- | ------------------------------- |
| Static response caching | strong  | ✔ via `returns_static_response` |
| Dynamic callable keys   | ❌       | ✔                               |
| Per-user namespaces     | tricky  | ✔                               |

Overall:

**Duck’s cached_view is more granular, callable-aware, async-adaptive, and flexible than traditional caching decorators** found in popular Python frameworks.

---

## ✅ Summary

Duck’s cached view system delivers:

* **Deterministic, stable cache keys**
* **Full sync/async compatibility**
* **Advanced callable & dynamic target resolution**
* **Namespace-powered isolation**
* **Instant debugging skip**
* **Safe component caching**
* **Backend abstraction**

The result is a caching mechanism that is:

* **Faster**
* **Safer**
* **More expressive**
* **More adaptive**
* **More predictable**

than typical caching decorators in Python frameworks.
 