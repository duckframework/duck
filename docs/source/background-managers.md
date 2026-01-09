# 🔋Background Thread & Asyncio Loop Managers

[![Sync Ready](https://img.shields.io/badge/Sync-Ready-brightgreen?style=for-the-badge&logo=python)](#)  
[![Threaded](https://img.shields.io/badge/Threading-Supported-blue?style=for-the-badge&logo=windows-terminal)](#)  
[![Async Compatible](https://img.shields.io/badge/Async-Compatible-purple?style=for-the-badge&logo=fastapi)](#)  
[![Duck Framework](https://img.shields.io/badge/Powered%20By-Duck-orange?style=for-the-badge&logo=duckframework)](#)

---

**Duck** provides centralized managers for running background work in both threaded and asynchronous environments.  
These managers control how lifecycle operations, request-scoped jobs, and internal framework tasks are executed.

A **critical design detail** is that both managers attach themselves to the **current thread** and may be **inherited by descendant threads**.  
This can be powerful, but it can also lead to subtle issues if not used carefully.

---

## Threadpool Manager

In **WSGI** or other synchronous environments, Duck relies on a threadpool manager to execute request-handling and internal synchronous tasks.  
The default internal pool accepts only tasks labeled `request-handling`.

### Example

```
from duck.utils.threading.threadpool import get_or_create_thread_manager

def some_task_entry():
    manager = get_or_create_thread_manager()  # Returns a ThreadPoolManager instance
    future = manager.submit_task(...)
```

### Notes & Warnings

- Calling `get_or_create_thread_manager()` attaches a threadpool manager **to the current thread**.  
  If this is done in the **main thread**, that manager may be **inherited** by all worker threads Duck creates later.

- Duck itself may create other managers inside worker threads, which means:
  - The instance you create in the main thread may **not** be the same instance your worker threads end up using.
  - Conversely, a manager created in a worker thread may propagate to all of that worker’s child threads.

- **Always check** that the instance returned by `get_or_create_thread_manager()` is the one you intend to use for your subsystem.  
  Avoid assuming that calling it in one place configures it globally.

- **Avoid creating unnecessary managers.**  
  Every manager carries its own pool; creating many of them can fragment work, waste threads, or cause unexpected behavior.

- Always read the detailed documentation in  
  `duck.utils.threading.threadpool`.

---

## Asyncio Loop Manager

Duck also includes a thread-backed asyncio loop manager, allowing synchronous code to schedule async tasks safely.  
This is common in hybrid systems (e.g., sync request lifecycle, async I/O operations).

### Example

```
from duck.utils.asyncio.eventloop import get_or_create_loop_manager

def some_task_entry():
    manager = get_or_create_loop_manager()  # Returns an AsyncioLoopManager instance
    future = manager.submit_task(...)
```

### Notes & Warnings

- Like the threadpool manager, calling `get_or_create_loop_manager()` attaches the manager to the **current thread**.  
  Descendant threads inherit the same loop manager unless you explicitly create a separate one.

- If you call this in the **main thread**, all Duck worker threads may inherit the same loop manager — sometimes desirable, sometimes not.

- Duck may also create **its own loop managers** inside worker threads when needed.  
  As a result:
  - The loop manager you expect to use may not be the one your worker code ends up interacting with.
  - Multiple managers can exist unexpectedly if you create them without understanding thread inheritance.

- **Always verify** that the instance returned is the one your component is meant to use.  
  This is especially important in systems that spawn worker threads, background processors, or per-request handlers.

- **Do not create more managers than required.**  
  Each manager spins up its own dedicated asyncio loop thread; creating many of them fragments execution and causes unnecessary overhead.

- Read the full documentation in  
  `duck.utils.asyncio.eventloop`.

---

## Summary of Best Practices

- Prefer to let Duck create managers unless you have a specific need.
- When manually creating managers, **do so inside the worker thread**, not in the main thread.
- Always check the returned instance — do not assume you are using the same manager Duck uses internally.
- Avoid creating multiple manager instances unless you fully understand thread inheritance and isolation behavior.

By following these guidelines, you ensure consistent background execution, minimize unexpected state propagation, and prevent manager proliferation across your application.
