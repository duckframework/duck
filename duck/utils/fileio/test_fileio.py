"""
Tests for FileIOStream and AsyncFileIOStream.

Run directly:
    python test_fileio.py

No external test runner or duck installation required — all duck
dependencies are stubbed inline before the module is imported.
"""

import asyncio
import io
import os
import sys
import tempfile
import time
import traceback
import types

from duck.utils import fileio as fio


# Test runner
# -------------------------------------------------------------------------

PASS = "\033[92mPASS\033[0m"
FAIL = "\033[91mFAIL\033[0m"

_results: list[tuple[str, bool, str]] = []


def run(name: str, fn):
    """
    Runs a single test function and records the outcome.

    Args:
        name: Human-readable test name shown in the summary.
        fn: Zero-argument callable or async coroutine function.
    """
    try:
        if asyncio.iscoroutinefunction(fn):
            asyncio.run(fn())
        else:
            fn()
        _results.append((name, True, ""))
        print(f"  {PASS}  {name}")
    except Exception:
        msg = traceback.format_exc()
        _results.append((name, False, msg))
        print(f"  {FAIL}  {name}")
        for line in msg.splitlines():
            print(f"         {line}")


def assert_eq(a, b, msg=""):
    """
    Raises AssertionError when ``a != b``.

    Args:
        a: Actual value.
        b: Expected value.
        msg: Optional context shown on failure.
    """
    assert a == b, f"{msg + ': ' if msg else ''}{a!r} != {b!r}"


# Fixture helpers
# -------------------------------------------------------------------------

def make_temp_file(content: bytes = b"Hello, Duck!") -> str:
    """
    Writes content to a named temporary file and returns its path.

    Args:
        content: Bytes to write into the file.

    Returns:
        Absolute path to the temporary file.
    """
    fd, path = tempfile.mkstemp()
    with os.fdopen(fd, "wb") as f:
        f.write(content)
    return path


def fresh_cache():
    """
    Clears the shared FILE_CACHE so each test starts clean.
    """
    fio.FILE_CACHE.clear()


# Tests — core read/cache behaviour
# -------------------------------------------------------------------------

def test_sync_open_and_read():
    """
    FileIOStream opens a file and reads the correct bytes.
    """
    path = make_temp_file(b"hello world")
    try:
        stream = fio.FileIOStream(path, open_now=True)
        data = stream.read()
        stream.close()
        assert_eq(data, b"hello world", "read content")
    finally:
        os.unlink(path)


def test_sync_read_populates_cache():
    """
    After a sync read, the result is stored in FILE_CACHE.
    """
    fresh_cache()
    path = make_temp_file(b"cache me")
    try:
        stream = fio.FileIOStream(path, open_now=True)
        stream.read()
        stream.close()
        cached = fio.FILE_CACHE.get(f"{path}:0:-1")
        assert cached is not None, "entry missing from cache after read"
        assert_eq(cached[0], b"cache me", "cached data")
    finally:
        os.unlink(path)


def test_sync_read_serves_cache_hit():
    """
    A second read returns the cached bytes without touching the descriptor.
    """
    fresh_cache()
    path = make_temp_file(b"from cache")
    try:
        stream = fio.FileIOStream(path, open_now=True)
        stream.read()
        stream.close()

        # Corrupt the file but restore mtime so the cache entry stays valid
        mtime = fio.FILE_CACHE.get(f"{path}:0:-1")[1]
        with open(path, "wb") as f:
            f.write(b"CORRUPTED")
        os.utime(path, (mtime, mtime))

        stream2 = fio.FileIOStream(path, open_now=True)
        second = stream2.read()
        stream2.close()
        assert_eq(second, b"from cache", "must serve cached bytes")
    finally:
        os.unlink(path)


def test_sync_cache_miss_on_mtime_change():
    """
    When the file changes on disk, cache_get returns None (stale eviction).
    """
    fresh_cache()
    path = make_temp_file(b"version one")
    try:
        stream = fio.FileIOStream(path, open_now=True)
        stream.read()
        stream.close()

        # Force mtime forward so the cache entry is considered stale
        new_mtime = time.time() + 2
        with open(path, "wb") as f:
            f.write(b"version two")
        os.utime(path, (new_mtime, new_mtime))

        stream2 = fio.FileIOStream(path, open_now=True)
        result = stream2.read()
        stream2.close()
        assert_eq(result, b"version two", "must re-read after mtime change")
    finally:
        os.unlink(path)


# Tests — cache-on-write
# -------------------------------------------------------------------------

def test_sync_write_updates_cache():
    """
    Writing stores the written slice in the cache under (write_pos, len(data))
    and patches any overlapping entries in memory.
    """
    fresh_cache()
    path = make_temp_file(b"AAAABBBB")
    try:
        # Warm the full-read entry first so there is something to patch
        r = fio.FileIOStream(path, open_now=True)
        r.read()
        r.close()

        # Seeked write — overwrite the second half
        w = fio.FileIOStream(path, open_now=True, mode="r+b")
        w.seek(4)
        w.write(b"CCCC")
        w.close()

        # The exact written slice must be in cache under (pos=4, size=4)
        written_entry = fio.FILE_CACHE.get(f"{path}:4:4")
        assert written_entry is not None, "written slice must be cached at (pos=4, size=4)"
        assert_eq(written_entry[0], b"CCCC", "written slice cached bytes")

        # The full-read entry must have been patched in place
        full_entry = fio.FILE_CACHE.get(f"{path}:0:-1")
        assert full_entry is not None, "full-read entry must be patched, not evicted"
        assert_eq(full_entry[0], b"AAAACCCC", "full-read entry must reflect the write")
    finally:
        os.unlink(path)


def test_sync_write_cache_entry_has_fresh_mtime():
    """
    The mtime stored in cache entries after a write matches the post-flush mtime.
    """
    fresh_cache()
    path = make_temp_file(b"x")
    try:
        w = fio.FileIOStream(path, open_now=True, mode="wb")
        w.write(b"fresh")
        w.close()

        # Written slice is cached under (pos=0, size=5)
        cached = fio.FILE_CACHE.get(f"{path}:0:5")
        assert cached is not None, "written slice must be in cache"
        cached_mtime = cached[1]

        stream = fio.FileIOStream(path)
        actual_mtime = stream.current_mtime()
        assert_eq(cached_mtime, actual_mtime, "cached mtime must match disk mtime")
    finally:
        os.unlink(path)


def test_sync_read_after_write_served_from_cache():
    """
    A read of the exact written slice immediately after a write is served
    from the cache without a disk round-trip.
    """
    fresh_cache()
    path = make_temp_file(b"original")
    try:
        w = fio.FileIOStream(path, open_now=True, mode="wb")
        w.write(b"written data")
        w.close()

        # Written slice must be in cache under (pos=0, size=12)
        cached = fio.FILE_CACHE.get(f"{path}:0:12")
        assert cached is not None, "written slice must be in cache"
        assert_eq(cached[0], b"written data", "cached bytes must match written content")

        # Cached mtime must match disk
        stream = fio.FileIOStream(path)
        assert_eq(cached[1], stream.current_mtime(), "cached mtime must match disk")
    finally:
        os.unlink(path)


def test_sync_cache_mtime_updated_on_write():
    """
    _cache_mtime on the stream is updated after a write so is_modified is
    accurate without requiring a subsequent read.
    """
    fresh_cache()
    path = make_temp_file(b"x")
    try:
        w = fio.FileIOStream(path, open_now=True, mode="wb")
        w.write(b"written")
        w.close()

        assert w._cache_mtime is not None, "_cache_mtime must be set after write"
        assert w.is_modified is False, "is_modified must be False right after write"
    finally:
        os.unlink(path)


# Tests — is_modified
# -------------------------------------------------------------------------

def test_is_modified_false_before_read():
    """
    is_modified returns False before any read or write has taken place.
    """
    path = make_temp_file(b"data")
    try:
        stream = fio.FileIOStream(path)
        assert stream.is_modified is False, "no baseline — must be False"
    finally:
        os.unlink(path)


def test_is_modified_false_after_read_unchanged():
    """
    is_modified returns False immediately after a read with no external changes.
    """
    fresh_cache()
    path = make_temp_file(b"stable")
    try:
        stream = fio.FileIOStream(path, open_now=True)
        stream.read()
        stream.close()
        assert stream.is_modified is False, "file unchanged — must be False"
    finally:
        os.unlink(path)


def test_is_modified_true_after_external_write():
    """
    is_modified returns True when another process modifies the file after a read.
    """
    fresh_cache()
    path = make_temp_file(b"original")
    try:
        stream = fio.FileIOStream(path, open_now=True)
        stream.read()
        stream.close()

        # Simulate an external modification with a future mtime
        os.utime(path, (time.time() + 10, time.time() + 10))
        assert stream.is_modified is True, "file modified externally — must be True"
    finally:
        os.unlink(path)


# Tests — on_read hook
# -------------------------------------------------------------------------

def test_on_read_hook_fires_on_cache_miss():
    """
    on_read hook is called when data is read fresh from disk.
    """
    fresh_cache()
    path = make_temp_file(b"hook data")
    log = []
    try:
        stream = fio.FileIOStream(path, open_now=True)
        stream.hook("on_read", lambda s, data, n: log.append(("read", data, n)))
        stream.read()
        stream.close()
        assert len(log) == 1, "hook must fire exactly once"
        assert_eq(log[0], ("read", b"hook data", 9), "hook args")
    finally:
        os.unlink(path)


def test_on_read_hook_fires_on_cache_hit():
    """
    on_read hook fires even when data is served from cache.
    """
    fresh_cache()
    path = make_temp_file(b"cached hook")
    log = []
    try:
        # First read populates cache
        s1 = fio.FileIOStream(path, open_now=True)
        s1.read()
        s1.close()

        # Second read must still fire the hook
        s2 = fio.FileIOStream(path, open_now=True)
        s2.hook("on_read", lambda s, data, n: log.append(n))
        s2.read()
        s2.close()
        assert len(log) == 1, "hook must fire on cache hit too"
        assert_eq(log[0], len(b"cached hook"))
    finally:
        os.unlink(path)


def test_on_read_multiple_hooks():
    """
    Multiple on_read hooks all fire in registration order.
    """
    fresh_cache()
    path = make_temp_file(b"multi")
    order = []
    try:
        stream = fio.FileIOStream(path, open_now=True)
        stream.hook("on_read", lambda s, d, n: order.append("first"))
        stream.hook("on_read", lambda s, d, n: order.append("second"))
        stream.read()
        stream.close()
        assert_eq(order, ["first", "second"], "hooks must fire in order")
    finally:
        os.unlink(path)


# Tests — on_write hook
# -------------------------------------------------------------------------

def test_on_write_hook_fires():
    """
    on_write hook is called after a successful write.
    """
    fresh_cache()
    path = make_temp_file(b"")
    log = []
    try:
        stream = fio.FileIOStream(path, open_now=True, mode="wb")
        stream.hook("on_write", lambda s, data, n: log.append(("write", data, n)))
        stream.write(b"written bytes")
        stream.close()
        assert len(log) == 1, "hook must fire exactly once"
        assert_eq(log[0], ("write", b"written bytes", 13), "hook args")
    finally:
        os.unlink(path)


def test_on_write_hook_receives_correct_stream():
    """
    The stream argument passed to the hook is the stream that fired it.
    """
    fresh_cache()
    path = make_temp_file(b"")
    received = []
    try:
        stream = fio.FileIOStream(path, open_now=True, mode="wb")
        stream.hook("on_write", lambda s, d, n: received.append(s))
        stream.write(b"x")
        stream.close()
        assert received[0] is stream, "hook must receive the firing stream"
    finally:
        os.unlink(path)


def test_hook_invalid_event_raises():
    """
    hook() raises ValueError for unknown event names.
    """
    path = make_temp_file(b"x")
    try:
        stream = fio.FileIOStream(path)
        try:
            stream.hook("on_teleport", lambda s, d, n: None)
            raise AssertionError("expected ValueError not raised")
        except ValueError as e:
            assert "on_teleport" in str(e), "error message must name the bad event"
    finally:
        os.unlink(path)


def test_on_read_and_write_hooks_independent():
    """
    on_read hooks do not fire on writes and vice versa.
    """
    fresh_cache()
    path = make_temp_file(b"")
    reads, writes = [], []
    try:
        w = fio.FileIOStream(path, open_now=True, mode="wb")
        w.hook("on_read",  lambda s, d, n: reads.append(n))
        w.hook("on_write", lambda s, d, n: writes.append(n))
        w.write(b"hello")
        w.close()

        assert reads  == [],  "on_read must not fire on write"
        assert writes == [5], "on_write must fire once"

        r = fio.FileIOStream(path, open_now=True)
        r.hook("on_read",  lambda s, d, n: reads.append(n))
        r.hook("on_write", lambda s, d, n: writes.append(n))

        # Ensure cache miss so the read goes to disk
        fresh_cache()
        r.read()
        r.close()

        assert reads  == [5], "on_read must fire on read"
        assert writes == [5], "on_write must not fire on read"
    finally:
        os.unlink(path)


# Tests — async on_read / on_write hooks
# -------------------------------------------------------------------------

async def test_async_hook_on_read():
    """
    Async hooks registered with hook() are awaited on AsyncFileIOStream reads.
    """
    fresh_cache()
    path = make_temp_file(b"async hook read")
    log = []
    try:
        async def async_read_hook(s, data, n):
            log.append(("async_read", n))

        stream = fio.AsyncFileIOStream(path)
        stream.hook("on_read", async_read_hook)
        await stream.read()
        await stream.close()
        assert_eq(log, [("async_read", len(b"async hook read"))], "async hook args")
    finally:
        os.unlink(path)


async def test_async_hook_on_write():
    """
    Async hooks registered with hook() are awaited on AsyncFileIOStream writes.
    """
    fresh_cache()
    path = make_temp_file(b"")
    log = []
    try:
        async def async_write_hook(s, data, n):
            log.append(("async_write", data))

        stream = fio.AsyncFileIOStream(path, mode="wb")
        stream.hook("on_write", async_write_hook)
        await stream.write(b"async written")
        await stream.close()
        assert_eq(log, [("async_write", b"async written")], "async write hook args")
    finally:
        os.unlink(path)


async def test_mixed_sync_and_async_hooks():
    """
    Sync and async hooks can both be registered on the same event and
    both fire in registration order.
    """
    fresh_cache()
    path = make_temp_file(b"mixed")
    order = []
    try:
        def sync_hook(s, d, n): order.append("sync")
        async def async_hook(s, d, n): order.append("async")

        stream = fio.AsyncFileIOStream(path)
        stream.hook("on_read", sync_hook)
        stream.hook("on_read", async_hook)
        await stream.read()
        await stream.close()
        assert_eq(order, ["sync", "async"], "hooks must fire in registration order")
    finally:
        os.unlink(path)


# Tests — async cache-on-write
# -------------------------------------------------------------------------

async def test_async_write_updates_cache():
    """
    AsyncFileIOStream.write caches the written slice under (write_pos, len(data)).
    """
    fresh_cache()
    path = make_temp_file(b"")
    try:
        stream = fio.AsyncFileIOStream(path, mode="wb")
        await stream.write(b"async written data")
        await stream.close()

        # Written slice cached under (pos=0, size=18)
        cached = fio.FILE_CACHE.get(f"{path}:0:18")
        assert cached is not None, "written slice must be in cache after async write"
        assert_eq(cached[0], b"async written data", "cached bytes must match written bytes")
    finally:
        os.unlink(path)


async def test_async_read_after_write_served_from_cache():
    """
    A read of the exact written slice immediately after an async write is
    served from cache without a disk round-trip.
    """
    fresh_cache()
    path = make_temp_file(b"old")
    try:
        w = fio.AsyncFileIOStream(path, mode="wb")
        await w.write(b"new content")
        await w.close()

        # Written slice cached under (pos=0, size=11)
        cached = fio.FILE_CACHE.get(f"{path}:0:11")
        assert cached is not None, "written slice must be in cache after async write"
        assert_eq(cached[0], b"new content", "cached bytes must match written content")

        # Mtime in cache must match disk
        stream = fio.FileIOStream(path)
        assert_eq(cached[1], stream.current_mtime(), "cached mtime must match disk")
    finally:
        os.unlink(path)


# Tests — seek correctness
# -------------------------------------------------------------------------

def test_seeked_full_read_uses_own_cache_slot():
    """
    A full read after seek() is cached under its own (pos, size) key so
    the same data is returned on a second read without touching the disk.
    """
    fresh_cache()
    path = make_temp_file(b"ABCDEFGH")
    try:
        s = fio.FileIOStream(path, open_now=True)
        s.seek(4)
        first  = s.read()     # cache miss → disk → stores "path:4:-1"
        s.seek(4)
        second = s.read()     # cache hit  → "path:4:-1"
        s.close()
        assert_eq(first,  b"EFGH", "first seeked read must return correct bytes")
        assert_eq(second, b"EFGH", "second seeked read must be served from cache")

        # Verify the cache entry exists under the correct key
        cached = fio.FILE_CACHE.get(f"{path}:4:-1")
        assert cached is not None, "cache entry must exist at (pos=4, size=-1)"
        assert_eq(cached[0], b"EFGH", "cached bytes must match read result")
    finally:
        os.unlink(path)


def test_seeked_partial_read_independent_slot():
    """
    A partial read from a seeked position occupies its own cache slot and
    does not collide with a pos-0 read of the same size.
    """
    fresh_cache()
    path = make_temp_file(b"ABCDEFGH")
    try:
        s = fio.FileIOStream(path, open_now=True)
        s.read(4)       # stores "path:0:4" → b"ABCD"
        s.seek(4)
        got = s.read(4) # stores "path:4:4" → b"EFGH"
        s.close()
        assert_eq(got, b"EFGH", "seeked partial read must return bytes from offset 4")

        entry_pos0 = fio.FILE_CACHE.get(f"{path}:0:4")
        entry_pos4 = fio.FILE_CACHE.get(f"{path}:4:4")
        assert entry_pos0 is not None, "pos-0 entry must still exist"
        assert entry_pos4 is not None, "pos-4 entry must exist"
        assert_eq(entry_pos0[0], b"ABCD", "pos-0 entry must be unchanged")
        assert_eq(entry_pos4[0], b"EFGH", "pos-4 entry must hold seeked bytes")
    finally:
        os.unlink(path)


def test_multiple_seek_positions_all_cached():
    """
    Repeated reads at multiple offsets are all individually cached and
    served on a second pass without touching the disk.

    This is the key benefit of pos-keyed caching: high-seek workloads
    accumulate warm entries across many positions.
    """
    fresh_cache()
    content = b"0123456789ABCDEF"    # 16 bytes
    path = make_temp_file(content)
    positions = [0, 4, 8, 12]
    try:
        # First pass — all cache misses, goes to disk
        s = fio.FileIOStream(path, open_now=True)
        first_pass = []
        for pos in positions:
            s.seek(pos)
            first_pass.append(s.read(4))
        s.close()

        # Second pass — all must be cache hits returning identical data
        s2 = fio.FileIOStream(path, open_now=True)
        second_pass = []
        for pos in positions:
            s2.seek(pos)
            second_pass.append(s2.read(4))
        s2.close()

        for i, pos in enumerate(positions):
            expected = content[pos:pos + 4]
            assert_eq(first_pass[i],  expected, f"first pass pos={pos}")
            assert_eq(second_pass[i], expected, f"second pass pos={pos} (must hit cache)")
    finally:
        os.unlink(path)


def test_seeked_write_patches_overlapping_cached_entries():
    """
    A seeked write patches cached entries in memory without a disk re-read.

    Cached entries that overlap the written region are updated in place;
    non-overlapping entries are left untouched.
    """
    fresh_cache()
    path = make_temp_file(b"AAAABBBB")
    try:
        # Warm the cache with a full read at pos 0 and a chunk at pos 0
        s = fio.FileIOStream(path, open_now=True)
        s.read()        # stores "path:0:-1" → b"AAAABBBB"
        s.seek(0)
        s.read(4)       # stores "path:0:4"  → b"AAAA"
        s.close()

        # Write to the second half — overlaps the full-read entry but not pos-0:4
        w = fio.FileIOStream(path, open_now=True, mode="r+b")
        w.seek(4)
        w.write(b"CCCC")
        w.close()

        # Full-read entry at pos 0 must reflect the patch
        full_entry = fio.FILE_CACHE.get(f"{path}:0:-1")
        assert full_entry is not None, "full-read cache entry must still exist"
        assert_eq(full_entry[0], b"AAAACCCC", "full-read entry must be patched in place")

        # Pos-0:4 entry covers only b"AAAA" — no overlap, must be untouched
        chunk_entry = fio.FILE_CACHE.get(f"{path}:0:4")
        assert chunk_entry is not None, "non-overlapping entry must survive"
        assert_eq(chunk_entry[0], b"AAAA", "non-overlapping entry must be unchanged")

        # Exact written slice must also be in cache
        write_entry = fio.FILE_CACHE.get(f"{path}:4:4")
        assert write_entry is not None, "written slice must be cached"
        assert_eq(write_entry[0], b"CCCC", "written slice cache entry must be correct")
    finally:
        os.unlink(path)


def test_seeked_write_evicts_boundary_partial_overlaps():
    """
    A write that partially overlaps a cached entry at a boundary evicts
    that entry rather than storing corrupted data.
    """
    fresh_cache()
    path = make_temp_file(b"ABCDEFGH")
    try:
        # Cache bytes at pos 2, size 4 → b"CDEF"
        s = fio.FileIOStream(path, open_now=True)
        s.seek(2)
        s.read(4)
        s.close()
        assert fio.FILE_CACHE.get(f"{path}:2:4") is not None, "pre-condition: entry must exist"

        # Write at pos 0, size 4 → overlaps "CDEF" entry at its start (boundary partial)
        w = fio.FileIOStream(path, open_now=True, mode="r+b")
        w.write(b"XXXX")    # writes pos 0–3; cached entry covers 2–5 (partial overlap)
        w.close()

        # Boundary-partial overlap must be evicted, not patched with wrong data
        assert fio.FILE_CACHE.get(f"{path}:2:4") is None, "boundary-partial entry must be evicted"
    finally:
        os.unlink(path)


async def test_async_seeked_full_read_independent_slot():
    """
    AsyncFileIOStream: a seeked full read is cached under its own pos key.
    """
    fresh_cache()
    path = make_temp_file(b"ABCDEFGH")
    try:
        s = fio.AsyncFileIOStream(path)
        await s.read()      # cache "path:0:-1"
        s.seek(4)
        got = await s.read()  # must return b"EFGH", not the cached pos-0 bytes
        await s.close()
        assert_eq(got, b"EFGH", "async seeked full read must return correct bytes")
        assert fio.FILE_CACHE.get(f"{path}:4:-1") is not None, "pos-4 entry must be cached"
    finally:
        os.unlink(path)


async def test_async_seeked_write_patches_cache():
    """
    AsyncFileIOStream: a seeked write patches overlapping cache entries.
    """
    fresh_cache()
    path = make_temp_file(b"AAAABBBB")
    try:
        # Warm the full-read entry
        r = fio.AsyncFileIOStream(path)
        await r.read()
        await r.close()

        # Seeked write
        w = fio.AsyncFileIOStream(path, mode="r+b")
        await w.async_open()
        w.seek(4)
        await w.write(b"CCCC")
        await w.close()

        full_entry = fio.FILE_CACHE.get(f"{path}:0:-1")
        assert full_entry is not None, "full-read entry must still exist after async write"
        assert_eq(full_entry[0], b"AAAACCCC", "async seeked write must patch full-read entry")
    finally:
        os.unlink(path)


# Tests — misc
# -------------------------------------------------------------------------

def test_seek_and_tell():
    """
    seek moves the file pointer; tell reports the new position.
    """
    path = make_temp_file(b"ABCDEFGH")
    try:
        stream = fio.FileIOStream(path, open_now=True)
        stream.seek(4)
        assert_eq(stream.tell(), 4, "tell after seek(4)")
        data = stream.read(4)
        assert_eq(data, b"ABCDEFGH"[4:4 + min(4, stream.chunk_size)], "read after seek")
        stream.close()
    finally:
        os.unlink(path)


def test_total_read_bytes_accumulates():
    """
    _total_read_bytes grows correctly across reads with different sizes.
    """
    fresh_cache()
    path = make_temp_file(b"ABCDEFGH")
    try:
        stream = fio.FileIOStream(path, chunk_size=8, open_now=True)
        stream.read(3)   # cache key "path:3" → "ABC"
        stream.read(4)   # cache key "path:4" → "DEFG"
        stream.close()
        assert b"ABC" in stream._total_read_bytes, "first chunk missing"
        assert b"DEF" in stream._total_read_bytes, "second chunk missing"
    finally:
        os.unlink(path)


def test_read_raises_if_not_open():
    """
    read() raises ValueError when called before open().
    """
    path = make_temp_file(b"x")
    try:
        stream = fio.FileIOStream(path)
        try:
            stream.read()
            raise AssertionError("expected ValueError not raised")
        except ValueError:
            pass
    finally:
        os.unlink(path)


def test_to_async_preserves_hooks():
    """
    to_async_fileio_stream copies hooks to the new stream.
    """
    fresh_cache()
    path = make_temp_file(b"convert")
    log = []
    try:
        sync_stream = fio.FileIOStream(path, open_now=True)
        sync_stream.hook("on_read", lambda s, d, n: log.append(n))
        sync_stream.ignore_file_open_on_delete = True

        async_stream = fio.to_async_fileio_stream(sync_stream)
        assert len(async_stream._on_read_hooks) == 1, "hook must be copied"
    finally:
        os.unlink(path)


def test_lru_eviction():
    """
    When maxkeys is exceeded the least-recently-used entry is evicted.
    """
    small_cache = fio.FILE_CACHE.__class__(maxkeys=3)
    small_cache.set("a", 1)
    small_cache.set("b", 2)
    small_cache.set("c", 3)
    small_cache.get("a")           # promote "a" to most-recently-used
    small_cache.set("d", 4)        # "b" is now LRU → evicted
    assert small_cache.get("b") is None, "'b' should have been LRU-evicted"
    assert small_cache.get("a") is not None, "'a' should survive"
    assert small_cache.get("c") is not None, "'c' should survive"
    assert small_cache.get("d") is not None, "'d' should survive"


async def test_async_context_manager():
    """
    AsyncFileIOStream works as an async context manager.
    """
    fresh_cache()
    path = make_temp_file(b"ctx manager")
    try:
        async with fio.AsyncFileIOStream(path) as stream:
            data = await stream.read()
        assert_eq(data, b"ctx manager", "data via context manager")
        assert not stream.is_open(), "stream must be closed after __aexit__"
    finally:
        os.unlink(path)


# Entry point
# -------------------------------------------------------------------------

if __name__ == "__main__":
    print("\nFileIOStream test suite\n" + "─" * 44)

    print("\n  Core read / cache")
    run("open and read",                           test_sync_open_and_read)
    run("read populates cache",                    test_sync_read_populates_cache)
    run("read serves cache hit",                   test_sync_read_serves_cache_hit)
    run("cache miss on mtime change",              test_sync_cache_miss_on_mtime_change)

    print("\n  Cache-on-write")
    run("write updates cache",                     test_sync_write_updates_cache)
    run("write cache entry has fresh mtime",       test_sync_write_cache_entry_has_fresh_mtime)
    run("read after write served from cache",      test_sync_read_after_write_served_from_cache)
    run("_cache_mtime updated on write",           test_sync_cache_mtime_updated_on_write)

    print("\n  is_modified")
    run("False before read",                       test_is_modified_false_before_read)
    run("False after read (unchanged)",            test_is_modified_false_after_read_unchanged)
    run("True after external write",               test_is_modified_true_after_external_write)

    print("\n  on_read hooks")
    run("fires on cache miss",                     test_on_read_hook_fires_on_cache_miss)
    run("fires on cache hit",                      test_on_read_hook_fires_on_cache_hit)
    run("multiple hooks fire in order",            test_on_read_multiple_hooks)

    print("\n  on_write hooks")
    run("fires on write",                          test_on_write_hook_fires)
    run("receives correct stream",                 test_on_write_hook_receives_correct_stream)
    run("invalid event raises ValueError",         test_hook_invalid_event_raises)
    run("on_read and on_write are independent",    test_on_read_and_write_hooks_independent)

    print("\n  Async hooks")
    run("async on_read hook awaited",              test_async_hook_on_read)
    run("async on_write hook awaited",             test_async_hook_on_write)
    run("mixed sync+async hooks fire in order",    test_mixed_sync_and_async_hooks)

    print("\n  Async cache-on-write")
    run("async write updates cache",               test_async_write_updates_cache)
    run("async read after write from cache",       test_async_read_after_write_served_from_cache)

    print("\n  Seek correctness")
    run("seeked full read uses own cache slot",        test_seeked_full_read_uses_own_cache_slot)
    run("seeked partial read independent slot",        test_seeked_partial_read_independent_slot)
    run("multiple seek positions all cached",          test_multiple_seek_positions_all_cached)
    run("seeked write patches overlapping entries",    test_seeked_write_patches_overlapping_cached_entries)
    run("seeked write evicts boundary overlaps",       test_seeked_write_evicts_boundary_partial_overlaps)
    run("async: seeked full read independent slot",    test_async_seeked_full_read_independent_slot)
    run("async: seeked write patches cache",           test_async_seeked_write_patches_cache)

    print("\n  Misc")
    run("seek and tell",                           test_seek_and_tell)
    run("_total_read_bytes accumulates",           test_total_read_bytes_accumulates)
    run("read raises if not open",                 test_read_raises_if_not_open)
    run("to_async preserves hooks",                test_to_async_preserves_hooks)
    run("LRU eviction",                            test_lru_eviction)
    run("async context manager",                   test_async_context_manager)

    passed = sum(1 for _, ok, _ in _results if ok)
    total  = len(_results)
    print(f"\n{'─' * 44}")
    print(f"  {passed}/{total} passed")
    if passed < total:
        sys.exit(1)
