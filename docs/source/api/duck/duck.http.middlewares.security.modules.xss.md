# {py:mod}`duck.http.middlewares.security.modules.xss`

```{py:module} duck.http.middlewares.security.modules.xss
```

```{autodocx-docstring} duck.http.middlewares.security.modules.xss
:allowtitles:
```

## Module Contents

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`check_xss_in_url <duck.http.middlewares.security.modules.xss.check_xss_in_url>`
  - ```{autodocx-docstring} duck.http.middlewares.security.modules.xss.check_xss_in_url
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`CONTEXT_PATTERNS <duck.http.middlewares.security.modules.xss.CONTEXT_PATTERNS>`
  - ```{autodocx-docstring} duck.http.middlewares.security.modules.xss.CONTEXT_PATTERNS
    :summary:
    ```
* - {py:obj}`XSS_PATTERNS <duck.http.middlewares.security.modules.xss.XSS_PATTERNS>`
  - ```{autodocx-docstring} duck.http.middlewares.security.modules.xss.XSS_PATTERNS
    :summary:
    ```
````

### API

````{py:data} CONTEXT_PATTERNS
:canonical: duck.http.middlewares.security.modules.xss.CONTEXT_PATTERNS
:value: >
   None

```{autodocx-docstring} duck.http.middlewares.security.modules.xss.CONTEXT_PATTERNS
```

````

````{py:data} XSS_PATTERNS
:canonical: duck.http.middlewares.security.modules.xss.XSS_PATTERNS
:value: >
   None

```{autodocx-docstring} duck.http.middlewares.security.modules.xss.XSS_PATTERNS
```

````

````{py:function} check_xss_in_url(url: str) -> (bool, str)
:canonical: duck.http.middlewares.security.modules.xss.check_xss_in_url

```{autodocx-docstring} duck.http.middlewares.security.modules.xss.check_xss_in_url
```
````
