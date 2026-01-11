# {py:mod}`duck.contrib.sitemap`

```{py:module} duck.contrib.sitemap
```

```{autodocx-docstring} duck.contrib.sitemap
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`SitemapBuilder <duck.contrib.sitemap.SitemapBuilder>`
  - ```{autodocx-docstring} duck.contrib.sitemap.SitemapBuilder
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`DEFAULT_EXCLUDES <duck.contrib.sitemap.DEFAULT_EXCLUDES>`
  - ```{autodocx-docstring} duck.contrib.sitemap.DEFAULT_EXCLUDES
    :summary:
    ```
* - {py:obj}`to_component <duck.contrib.sitemap.to_component>`
  - ```{autodocx-docstring} duck.contrib.sitemap.to_component
    :summary:
    ```
````

### API

````{py:data} DEFAULT_EXCLUDES
:canonical: duck.contrib.sitemap.DEFAULT_EXCLUDES
:value: >
   None

```{autodocx-docstring} duck.contrib.sitemap.DEFAULT_EXCLUDES
```

````

`````{py:class} SitemapBuilder(server_url: str = None, filepath: typing.Optional[Union[str, pathlib.Path]] = None, save_to_file: bool = True, extra_urls: typing.Optional[typing.Iterable[str]] = None, exclude_patterns: typing.Optional[typing.Iterable[str]] = None, default_priority: typing.Optional[float] = 0.5, default_changefreq: typing.Optional[str] = 'monthly', apply_default_excludes: bool = True, excludes_ignorecase: bool = True)
:canonical: duck.contrib.sitemap.SitemapBuilder

```{autodocx-docstring} duck.contrib.sitemap.SitemapBuilder
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.contrib.sitemap.SitemapBuilder.__init__
```

````{py:attribute} _REGEX_META_CHARS
:canonical: duck.contrib.sitemap.SitemapBuilder._REGEX_META_CHARS
:value: >
   '[\\^\\$\\*\\+\\?\\[\\]\\(\\)\\\\]'

```{autodocx-docstring} duck.contrib.sitemap.SitemapBuilder._REGEX_META_CHARS
```

````

````{py:attribute} __slots__
:canonical: duck.contrib.sitemap.SitemapBuilder.__slots__
:value: >
   ('server_url', 'filepath', 'save_to_file', 'extra_urls', 'exclude_patterns', 'default_priority', 'de...

```{autodocx-docstring} duck.contrib.sitemap.SitemapBuilder.__slots__
```

````

````{py:method} _build_url_component(url_obj: duck.utils.urlcrack.URL, lastmod_iso: str, changefreq: typing.Optional[str], priority: typing.Optional[float])
:canonical: duck.contrib.sitemap.SitemapBuilder._build_url_component

```{autodocx-docstring} duck.contrib.sitemap.SitemapBuilder._build_url_component
```

````

````{py:method} _collect_extra_urls(existing_set: typing.Set[str]) -> typing.List[duck.utils.urlcrack.URL]
:canonical: duck.contrib.sitemap.SitemapBuilder._collect_extra_urls

```{autodocx-docstring} duck.contrib.sitemap.SitemapBuilder._collect_extra_urls
```

````

````{py:method} _collect_registered_urls() -> typing.List[duck.utils.urlcrack.URL]
:canonical: duck.contrib.sitemap.SitemapBuilder._collect_registered_urls

```{autodocx-docstring} duck.contrib.sitemap.SitemapBuilder._collect_registered_urls
```

````

````{py:method} _is_excluded(full_url_str: str, registered_route_pattern: str) -> bool
:canonical: duck.contrib.sitemap.SitemapBuilder._is_excluded

```{autodocx-docstring} duck.contrib.sitemap.SitemapBuilder._is_excluded
```

````

````{py:method} _looks_like_regex(path: str) -> bool
:canonical: duck.contrib.sitemap.SitemapBuilder._looks_like_regex
:staticmethod:

```{autodocx-docstring} duck.contrib.sitemap.SitemapBuilder._looks_like_regex
```

````

````{py:method} _to_absolute_url(raw: str) -> duck.utils.urlcrack.URL
:canonical: duck.contrib.sitemap.SitemapBuilder._to_absolute_url

```{autodocx-docstring} duck.contrib.sitemap.SitemapBuilder._to_absolute_url
```

````

````{py:method} build(return_content: bool = True) -> typing.Optional[str]
:canonical: duck.contrib.sitemap.SitemapBuilder.build

```{autodocx-docstring} duck.contrib.sitemap.SitemapBuilder.build
```

````

`````

````{py:data} to_component
:canonical: duck.contrib.sitemap.to_component
:value: >
   None

```{autodocx-docstring} duck.contrib.sitemap.to_component
```

````
