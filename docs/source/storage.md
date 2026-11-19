# Duck Storage Backends

Duck ships a pluggable storage layer for static files, media files and user uploads. You pick a backend in `settings.py`, and the same API works for every backend, in both sync and async code.

| Backend | Class | Use it for |
|---|---|---|
| Local | `duck.contrib.storage.backends.local.LocalStorage` | Development, or servers that serve a directory directly |
| S3 | `duck.contrib.storage.backends.s3.S3Storage` | AWS S3, MinIO, Backblaze B2 and any S3-compatible service |
| Cloudflare R2 | `duck.contrib.storage.backends.cloudflare.CloudflareR2Storage` | R2 buckets served through Cloudflare's CDN |

S3 and R2 need `httpx`:

```bash
pip install httpx
```

---

## Quick Start

Define your backends in `settings.py`. Each alias maps to one backend.

```python
STORAGE_BACKENDS = {
    "default": {
        "backend": "duck.contrib.storage.backends.local.LocalStorage",
        "options": {
            "root": str(MEDIA_ROOT),
            "base_url": "/media",
        },
    },
    "staticfiles": {
        "backend": "duck.contrib.storage.backends.local.LocalStorage",
        "options": {
            "root": str(SETTINGS["STATIC_ROOT"]),
            "base_url": str(SETTINGS.get("STATIC_URL", "/static")),
        },
    },
    "mediafiles": {
        "backend": "duck.contrib.storage.backends.local.LocalStorage",
        "options": {
            "root": str(SETTINGS["MEDIA_ROOT"]),
            "base_url": str(SETTINGS.get("MEDIA_URL", "/media")),
        },
    },
}
```

Each entry has two keys:

- `backend`: dotted path to the backend class.
- `options`: keyword arguments passed to the backend's constructor.

`LocalStorage` requires `root`, so always set it in `options`.

### Switching to a cloud backend

Change the `backend` path and the options. Nothing else in your code changes.

```python
STORAGE_BACKENDS = {
    "mediafiles": {
        "backend": "duck.contrib.storage.backends.cloudflare.CloudflareR2Storage",
        "options": {
            "bucket": "my-bucket",
            "account_id": "your-cloudflare-account-id",
            "public_base_url": "https://cdn.example.com",
        },
    },
}
```

---

## Using Storage With Django

Duck provides `DuckStorage`, a Django storage class that delegates to any alias in `STORAGE_BACKENDS`. Django and Duck then share the same storage.

If your Django settings are already defined and synced, nothing else is needed. Otherwise, add this to the Django `settings.py`:

```python
# Storage Backends
STORAGES = {
    alias: {
        "BACKEND": "duck.backend.django.storage.DuckStorage",
        "OPTIONS": {
            "backend_key": alias,
        },
    } for alias in DUCK_SETTINGS["STORAGE_BACKENDS"].keys()
}
```

`backend_key` is the alias from `STORAGE_BACKENDS`. Standard Django code such as `FileField` and `default_storage` then uses the Duck backend behind it.

---

## Saving Files

Every backend exposes the same methods. Each sync method has an `async_` twin.

```python
from duck.contrib.storage.backends.local import LocalStorage

storage = LocalStorage(root="media", base_url="/media")

# Save with an auto-generated key.
stored = storage.save(b"hello", "notes.txt", folder="docs")

print(stored.key)           # docs/2cf24dba5fb0a30e/notes.txt
print(stored.url)           # /media/docs/2cf24dba5fb0a30e/notes.txt
print(stored.size)          # 5
print(stored.content_type)  # text/plain
```

In async code, use `async_save`:

```python
stored = await storage.async_save(b"hello", "notes.txt", folder="docs")
```

> Calling a sync method such as `save` inside async code raises an error. Use the `async_` version there.

### Accepted inputs

`data` can be any of:

- `bytes`
- A `FileIOStream` or `AsyncFileIOStream`
- Any binary file-like object, such as `open("a.png", "rb")`

### Save methods

| Method | Description |
|---|---|
| `save(data, filename, folder="", metadata=None, on_progress=None)` | Saves under an auto-generated key |
| `save_as(data, key, folder="", metadata=None, on_progress=None, source_mtime=None)` | Saves under an exact key you choose, such as `"css/app.css"` |
| `async_save`, `async_save_as` | Async versions |

Both return a `StoredFile`:

| Field | Description |
|---|---|
| `key` | Backend-relative path that identifies the file |
| `url` | Public URL of the file |
| `size` | Size in bytes |
| `content_type` | MIME type |

### Keys and filenames

- Filenames are sanitized. Anything outside `A-Z a-z 0-9 . _ -` becomes `-`.
- The default key is `folder/<first 16 chars of sha256>/<filename>`.
- Identical content is **skipped** on re-upload. Backends compare the existing file with the new one before writing.

---

## Reading and Managing Files

| Method | Returns | Description |
|---|---|---|
| `get(key)` | `bytes` | Reads the whole file |
| `exists(key)` | `bool` | Checks whether the file exists |
| `size(key)` | `int` | Size in bytes. Raises `FileNotFoundError` if missing |
| `modified_time(key)` | `float \| None` | Last modified time as a UTC timestamp |
| `delete(key)` | `None` | Deletes the file. Missing files are ignored |
| `url_for(key)` | `str` | Public URL of the file |
| `open_stream(key)` | stream | Chunked reading for large files |

Every method above also has an `async_` version, for example `await storage.async_get(key)`.

### Streaming large files

`open_stream` reads in chunks, so memory stays bounded. Always close the stream.

```python
stream = storage.open_stream("videos/abc/movie.mp4")

try:
    chunk = stream.read(65536)
finally:
    stream.close()
```

On S3 and R2, streams are also context managers and iterables:

```python
async with await storage.async_open_stream(key) as stream:
    async for chunk in stream:
        ...
```

---

## Upload Progress

Progress events fire at 0%, at every `progress_step` percent (default `5.0`), and at 100%.

```python
# Per-save callback.
def show(event):
    print(f"{event.filename}: {event.percent:.0f}%")

storage.save(data, "video.mp4", on_progress=show)

# Global callback for every upload.
@storage.on_progress
def log_progress(event):
    ...
```

`ProgressEvent` fields: `key`, `filename`, `sent`, `total`, `percent`.

Callbacks can be plain functions or coroutine functions. Coroutines are awaited in `async_save`.

---

## Processors and Callbacks

### Processors

A processor runs before every save. It receives an `UploadContext`, changes it and returns it.

```python
@storage.processor
def force_png(context):
    context.content_type = "image/png"
    context.metadata["processed"] = True

    return context
```

You can change `payload`, `filename`, `folder`, `content_type`, `cache_control` and `metadata`. The hash and key are computed **after** processors run.

### Saved callbacks

Run code after each successful save:

```python
@storage.on_saved
def notify(stored):
    print("Saved", stored.url)
```

### Custom key builder

```python
def date_key(context):
    return f"{context.folder}/{context.filename}"

storage = LocalStorage(root="media", key_builder=date_key)
```

---

## Backend Options

### Shared options (all backends)

| Option | Default | Description |
|---|---|---|
| `cache_control` | `public, max-age=31536000, immutable` | Cache-Control header stored with files |
| `key_builder` | content-addressed key | Function that assigns the storage key |
| `processors` | `[]` | Processors run before every save |
| `chunk_size` | `65536` | Bytes per upload or download chunk |
| `progress_step` | `5.0` | Percent between progress events. Must be above 0 |

### LocalStorage

| Option | Default | Description |
|---|---|---|
| `root` | required | Directory where files are written |
| `base_url` | `/media` | URL prefix your web server maps to `root` |

Local writes preserve the source file's modified time, so unchanged files are detected quickly.

### S3Storage

| Option | Default | Description |
|---|---|---|
| `bucket` | required | Bucket name |
| `public_base_url` | required | CDN or public domain serving the bucket |
| `endpoint_url` | AWS regional endpoint | Set this for MinIO, B2 and other S3-compatible services |
| `region_name` | `us-east-1` | Region used for signing |
| `access_key_id` | env `AWS_ACCESS_KEY_ID` | Access key |
| `secret_access_key` | env `AWS_SECRET_ACCESS_KEY` | Secret key |
| `timeout` | `60.0` | Request timeout in seconds |

Requests are signed with a built-in AWS Signature V4 signer over `httpx`. Call `close()` or `await async_close()` to release the HTTP clients when you are done.

```python
STORAGE_BACKENDS = {
    "default": {
        "backend": "duck.contrib.storage.backends.s3.S3Storage",
        "options": {
            "bucket": "my-bucket",
            "public_base_url": "https://cdn.example.com",
            "region_name": "eu-west-1",
        },
    },
}
```

### CloudflareR2Storage

Extends `S3Storage`, so it accepts all S3 options except `endpoint_url` and `region_name`, which it sets itself.

| Option | Default | Description |
|---|---|---|
| `bucket` | required | R2 bucket name |
| `account_id` | required | Cloudflare account ID |
| `public_base_url` | required | Domain connected to the bucket |
| `access_key_id` | env `R2_ACCESS_KEY_ID` | R2 access key |
| `secret_access_key` | env `R2_SECRET_ACCESS_KEY` | R2 secret key |
| `api_token` | env `CLOUDFLARE_API_TOKEN` | Token with cache purge permission |
| `zone_id` | env `CLOUDFLARE_ZONE_ID` | Zone ID of the domain serving the bucket |

**CDN purging:** when `api_token` and `zone_id` are both set, `delete()` also purges the file from Cloudflare's cache. You can purge manually too:

```python
storage.purge_cache(["https://cdn.example.com/docs/abc/notes.txt"])
await storage.async_purge_cache([...])
```

---

## Creating a Custom Backend

Subclass `StorageBackend` and implement six methods: `put`, `get`, `delete`, `exists`, `size` and `url_for`.

```python
from duck.contrib.storage.backends import StorageBackend


class MyStorage(StorageBackend):
    """
    Stores files in my own system.
    """

    def put(self, key, context, reporter):
        # Send context.payload, then report bytes sent.
        reporter.advance(len(context.payload))

    def get(self, key): ...
    def delete(self, key): ...
    def exists(self, key): ...
    def size(self, key): ...
    def url_for(self, key): ...
```

Then use it in `settings.py` by its dotted path:

```python
STORAGE_BACKENDS = {
    "default": {
        "backend": "myapp.storage.MyStorage",
        "options": {},
    },
}
```

Optional overrides:

- `async_put`, `async_get` and the other `async_` methods for native async I/O. By default they run the sync version in a worker thread.
- `open_stream` and `async_open_stream` for real streaming. The default loads the whole file into memory.
- `is_unchanged` for an exact duplicate check. The default compares existence and size only.
- `modified_time` if your system can provide it.

### Building backends from a config dict

`create_backend` builds a backend from a dict, and `register_backend` adds your own short name. Built-in names are `"local"`, `"s3"` and `"cloudflare_r2"`.

```python
from duck.contrib.storage.backends.utils import create_backend, register_backend

register_backend("my", MyStorage)

storage = create_backend({"type": "local", "root": "media"})
```

---

## Errors

| Error | When |
|---|---|
| `StorageError` | Base error of the storage layer, and raised when `httpx` is missing |
| `ValueError` | Missing credentials, unknown backend type, or a non-positive `progress_step` |
| `FileNotFoundError` | `size()` or `modified_time()` on a missing file |
| `httpx.HTTPStatusError` | S3 or R2 rejected a request |
