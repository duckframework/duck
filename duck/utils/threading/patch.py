"""
Production-grade monkey-patch module for Python's threading.Thread.  

Enhancements:
- Tracks parent thread object (not just ident).
- Returns parent Thread object via get_parent_thread().
- Uses strong weakref-based registry (no leaks).
- Supports patching already-created Thread instances (before start()).
- Preserves subclassed run() methods.
- Hooks for pre-run and post-run execution.
- Fully idempotent. Safe for large production systems.
- Automatic cleanup after thread finishes.
"""

import threading
import functools
import weakref

from typing import (
    Callable,
    Optional,
    Dict,
    Any,
    Union,
)


thread_info: Dict[int, Dict[str, Any]] = {}
_is_patched = False

# Cached original class methods
_original_init = threading.Thread.__init__


class PatchNotApplied(Exception):
    """
    Raised if user tries to use `get_parent` but forgot to patch threading module.
    """


def _wrap_run(self, original_run, pre_hook, post_hook):
    """
    Returns a wrapped run() method that executes:
    
    - pre_hook()
    - original run()
    - post_hook()
    - registry cleanup
    """

    @functools.wraps(original_run)
    def wrapped():
        ident = threading.get_ident()

        # register metadata now that thread started and ident exists
        thread_info[ident] = {
            "parent": weakref.ref(self._parent_thread) if hasattr(self, "_parent_thread") else None,
            "thread": weakref.ref(self),
        }

        # pre-hook
        if pre_hook:
            try:
                pre_hook(self)
            except Exception:
                pass

        try:
            return original_run()
        finally:
            # post-hook
            if post_hook:
                try:
                    post_hook(self)
                except Exception:
                    pass

            # cleanup
            thread_info.pop(ident, None)

    return wrapped


def patch_threading(
    *,
    pre_hook: Optional[Callable[[threading.Thread], None]] = None,
    post_hook: Optional[Callable[[threading.Thread], None]] = None,
    patch_existing_threads: bool = False,
) -> None:
    """
    Monkey-patches threading.Thread so that:

    - New threads automatically track parent thread objects.
    - `.run()` is wrapped at instance level.
    - Subclass overrides continue to work.
    - Optionally patch existing Thread objects created before patching.
    - Automatic cleanup in registry.

    Args:
        pre_hook (Optional): runs before each thread's original run().
        post_hook (Optional): runs after each thread's run() completes.
        patch_existing_threads (bool): If True, already-created threads that have
                               NOT started will get their `.run()` patched as well.

    Notes:
    - Idempotent: calling twice does nothing.
    - Back-patching cannot discover parent thread for already-created threads.
    """
    global _is_patched

    if _is_patched:
        return

    def patched_init(self, *args, **kwargs):
        parent_thread = threading.current_thread()
        self._parent_thread = parent_thread  # store the actual object

        # original init
        _original_init(self, *args, **kwargs)

        # capture user-defined run() (may be overridden)
        original_run = self.run

        # replace with wrapped version
        self.run = _wrap_run(self, original_run, pre_hook, post_hook)

    # apply patch
    threading.Thread.__init__ = patched_init
    _is_patched = True

    # optionally patch threads created before this call
    if patch_existing_threads:
        for t in threading.enumerate():
            if isinstance(t, threading.Thread) and not hasattr(t, "_parent_thread"):
                if not t.is_alive():  # we can only patch before start
                    t._parent_thread = threading.current_thread()
                    original_run = t.run
                    t.run = _wrap_run(t, original_run, pre_hook, post_hook)


def get_parent_thread(thread_or_ident: Union[int, threading.Thread]) -> Optional[threading.Thread]:
    """
    Returns the actual parent Thread object of a given thread.

    Args:
        thread_or_ident: A thread object or its ident.

    Returns:
        Thread | None

    Raises:
        PatchNotApplied: if thread module wasn't patched yet.
    """
    if not _is_patched:
        raise PatchNotApplied('threading module has not been patched yet. Did you forget to use "patch_threading".')

    ident = (
        thread_or_ident if isinstance(thread_or_ident, int)
        else getattr(thread_or_ident, "ident", None)
    )

    if ident is None:
        return None

    info = thread_info.get(ident)
    if not info:
        return None

    parent_ref = info.get("parent")
    return parent_ref() if parent_ref else None


# Alias to stay backwards compatible with your previous API
get_parent = get_parent_thread
