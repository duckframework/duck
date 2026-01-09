# 📄 Sitemap

Producing and serving a **sitemap** in Duck is straightforward. A sitemap is an XML file that lists all the pages of your website so search engines like Google can efficiently crawl your content.

In **Duck**, you can **lazily generate and serve a sitemap** using the `duck.etc.apps.essentials.blueprint.Sitemap` blueprint.

* The sitemap is generated the **first time `/sitemap.xml` is visited**.
* Subsequent visits return a **cached response**, thanks to the `duck.views.cached_view` decorator.
* This ensures the sitemap is only generated once per session, improving performance.

> Learn more about cached views [here](./cached-views.md).

---

## ⚙️ Configuration

To start serving the sitemap, add the blueprint in your settings:

```python
# settings.py

BLUEPRINTS = [
    # Other blueprints
    "duck.etc.apps.essentials.blueprint.Sitemap",
]
```

This is enough for **basic sitemap serving**, but for **fine-grained control**, Duck provides several settings:

```py
SITEMAP_EXTRA_URLS = SETTINGS.get("SITEMAP_EXTRA_URLS", [])
SITEMAP_EXCLUDE_PATTERNS = SETTINGS.get("SITEMAP_EXCLUDE_PATTERNS", [])
SITEMAP_DEFAULT_PRIORITY = SETTINGS.get("SITEMAP_DEFAULT_PRIORITY", 0.5)
SITEMAP_CHANGE_FREQUENCY = SETTINGS.get("SITEMAP_CHANGE_FREQUENCY", "monthly")
SITEMAP_SAVE_TO_FILE = SETTINGS.get("SITEMAP_SAVE_TO_FILE", False)
SITEMAP_FILEPATH = SETTINGS.get("SITEMAP_FILEPATH", None)
SITEMAP_APPLY_DEFAULT_EXCLUDES = SETTINGS.get("SITEMAP_APPLY_DEFAULT_EXCLUDES", True)
```

---

### 📝 Setting Details

| Setting                          | Description                                    | Notes / Tips                                                     |
| -------------------------------- | ---------------------------------------------- | ---------------------------------------------------------------- |
| `SITEMAP_EXTRA_URLS`             | Extra URLs to include beyond registered routes | Can include absolute URLs (https://…) or relative paths (/about) |
| `SITEMAP_EXCLUDE_PATTERNS`       | List of URL strings or regexes to exclude      | Example: `["^/admin", "^/api/.*", "/secret-page"]`               |
| `SITEMAP_DEFAULT_PRIORITY`       | Default `<priority>` for each URL (0.0–1.0)    | Higher priority signals importance to search engines             |
| `SITEMAP_CHANGE_FREQUENCY`       | Default `<changefreq>` value                   | Examples: `"daily"`, `"weekly"`, `"monthly"`                     |
| `SITEMAP_SAVE_TO_FILE`           | Whether to save sitemap XML to disk            | Set `True` and provide `SITEMAP_FILEPATH` to persist             |
| `SITEMAP_FILEPATH`               | Path to save sitemap                           | Example: `"/etc/sitemap.xml"`                                    |
| `SITEMAP_APPLY_DEFAULT_EXCLUDES` | Apply Duck’s default exclusions                | Includes static files, `/admin`, `/api`, `/ws/lively`            |

> **Tip:** Duck automatically excludes static files like CSS, JS, images, fonts, and media by default. You can safely **include PDFs and videos** by customizing `SITEMAP_EXCLUDE_PATTERNS`.

---

## 📌 Best Practices

1. **Include PDFs** in your sitemap if they contain meaningful content, like manuals or guides.
2. **Videos** should only be included if they are valuable content. For large or auxiliary media, consider a **separate video sitemap**.
3. Avoid including test, temporary, or duplicate URLs to maintain a clean sitemap.
4. Use **explicit `SITEMAP_EXTRA_URLS`** for pages that are not registered as routes.
5. Keep your sitemap under ~50k URLs per file and under 50MB uncompressed for SEO performance.

---

## 🏗 Using `SitemapBuilder`

The `SitemapBuilder` class provides a **programmatic interface** for building sitemaps:

```python
from duck.contrib.sitemap import SitemapBuilder

builder = SitemapBuilder(
    server_url=None,  # Automatically resolved if None
    save_to_file=True,
    filepath="/etc/sitemap.xml",
    extra_urls=["/about", "https://example.com/contact"],
    exclude_patterns=["^/admin", "https://example.com/secret", "^/api/.*"],
    default_priority=0.5,
    default_changefreq="monthly",
)

xml = builder.build(return_content=True)  # Returns sitemap XML as string
```

### 🔹 Features

* Walks Duck’s `RouteRegistry` and collects valid routes.
* Filters out **dynamic routes** (e.g., `/user/<id>`) and regex-like patterns.
* Supports **extra URLs** and **exclude patterns** (plain or regex).
* Builds XML using Duck components (`duck.html.components.to_component`).
* Can **persist the sitemap** to a file if configured.

---

### ⚡ Exclude Patterns Example

Duck provides **default exclusions** to avoid indexing unnecessary content:

```py
DEFAULT_EXCLUDES = [
# Static files and folders
r"(?ix)^(?:.*.(?:css|js|map|ico|mp3|mp4|png|jpe?g|gif|svg|webp|avif|bmp|tiff?|woff2?|ttf|eot|otf)$|.*/(?:static|assets|media)/.*)$",

# Dynamic or admin paths
r"^/sitemap.xml$",   # Exclude the sitemap itself
r"^/ws/lively.*",   # Anything starting with /ws/lively
r"^/admin/.*",      # Any subpath under /admin/
r"^/admin$",        # Strictly /admin itself
r"^/api/.*",        # Any subpath under /api/
r"^/api$",          # Strictly /api itself
]
```

* These exclusions ensure **static assets, admin routes, API routes, and the sitemap itself** are not included in the generated sitemap.

---

### Generating sitemap from CMD

Yes, you can generate a sitemap from the command line. This is made possible by the `duck sitemap` command. Here is 
an example:

```py
duck sitemap create
```

The above command will generate `sitemap.xml` located at `etc/sitemap.xml`. You can 
also customize options by providing arguments to the command. Use command `duck sitemap --help` to view more 
more information on this command usage.

---

### ✅ Summary

Duck’s sitemap system is:

* **Lazy** — generated only when first requested.
* **Cached** — subsequent requests are fast.
* **Flexible** — add extra URLs, define exclusions, adjust priorities and change frequency.
* **SEO-friendly** — automatically avoids unnecessary static files and system routes.

> By combining `SitemapBuilder` with `SITEMAP_EXTRA_URLS` and `SITEMAP_EXCLUDE_PATTERNS`, you can fully control what appears in your sitemap while keeping it optimized for search engines.
