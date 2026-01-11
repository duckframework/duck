# {py:mod}`duck.http.middlewares.security.modules.header_injection`

```{py:module} duck.http.middlewares.security.modules.header_injection
```

```{autodocx-docstring} duck.http.middlewares.security.modules.header_injection
:allowtitles:
```

## Module Contents

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`check_header_injection <duck.http.middlewares.security.modules.header_injection.check_header_injection>`
  - ```{autodocx-docstring} duck.http.middlewares.security.modules.header_injection.check_header_injection
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`CACHE_POISON_RE <duck.http.middlewares.security.modules.header_injection.CACHE_POISON_RE>`
  - ```{autodocx-docstring} duck.http.middlewares.security.modules.header_injection.CACHE_POISON_RE
    :summary:
    ```
* - {py:obj}`COOKIE_FORMAT_RE <duck.http.middlewares.security.modules.header_injection.COOKIE_FORMAT_RE>`
  - ```{autodocx-docstring} duck.http.middlewares.security.modules.header_injection.COOKIE_FORMAT_RE
    :summary:
    ```
* - {py:obj}`CRLF_RE <duck.http.middlewares.security.modules.header_injection.CRLF_RE>`
  - ```{autodocx-docstring} duck.http.middlewares.security.modules.header_injection.CRLF_RE
    :summary:
    ```
* - {py:obj}`SCRIPT_TAG_RE <duck.http.middlewares.security.modules.header_injection.SCRIPT_TAG_RE>`
  - ```{autodocx-docstring} duck.http.middlewares.security.modules.header_injection.SCRIPT_TAG_RE
    :summary:
    ```
````

### API

````{py:data} CACHE_POISON_RE
:canonical: duck.http.middlewares.security.modules.header_injection.CACHE_POISON_RE
:value: >
   'compile(...)'

```{autodocx-docstring} duck.http.middlewares.security.modules.header_injection.CACHE_POISON_RE
```

````

````{py:data} COOKIE_FORMAT_RE
:canonical: duck.http.middlewares.security.modules.header_injection.COOKIE_FORMAT_RE
:value: >
   'compile(...)'

```{autodocx-docstring} duck.http.middlewares.security.modules.header_injection.COOKIE_FORMAT_RE
```

````

````{py:data} CRLF_RE
:canonical: duck.http.middlewares.security.modules.header_injection.CRLF_RE
:value: >
   'compile(...)'

```{autodocx-docstring} duck.http.middlewares.security.modules.header_injection.CRLF_RE
```

````

````{py:data} SCRIPT_TAG_RE
:canonical: duck.http.middlewares.security.modules.header_injection.SCRIPT_TAG_RE
:value: >
   'compile(...)'

```{autodocx-docstring} duck.http.middlewares.security.modules.header_injection.SCRIPT_TAG_RE
```

````

````{py:function} check_header_injection(headers: dict)
:canonical: duck.http.middlewares.security.modules.header_injection.check_header_injection

```{autodocx-docstring} duck.http.middlewares.security.modules.header_injection.check_header_injection
```
````
