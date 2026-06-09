# {py:mod}`duck.http.middlewares.security.modules.sql_injection`

```{py:module} duck.http.middlewares.security.modules.sql_injection
```

```{autodocx-docstring} duck.http.middlewares.security.modules.sql_injection
:allowtitles:
```

## Module Contents

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`_gather_tokens <duck.http.middlewares.security.modules.sql_injection._gather_tokens>`
  - ```{autodocx-docstring} duck.http.middlewares.security.modules.sql_injection._gather_tokens
    :summary:
    ```
* - {py:obj}`_shorten <duck.http.middlewares.security.modules.sql_injection._shorten>`
  - ```{autodocx-docstring} duck.http.middlewares.security.modules.sql_injection._shorten
    :summary:
    ```
* - {py:obj}`check_sql_injection_in_url <duck.http.middlewares.security.modules.sql_injection.check_sql_injection_in_url>`
  - ```{autodocx-docstring} duck.http.middlewares.security.modules.sql_injection.check_sql_injection_in_url
    :summary:
    ```
* - {py:obj}`is_safe_url <duck.http.middlewares.security.modules.sql_injection.is_safe_url>`
  - ```{autodocx-docstring} duck.http.middlewares.security.modules.sql_injection.is_safe_url
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`MAX_TOKEN_LENGTH <duck.http.middlewares.security.modules.sql_injection.MAX_TOKEN_LENGTH>`
  - ```{autodocx-docstring} duck.http.middlewares.security.modules.sql_injection.MAX_TOKEN_LENGTH
    :summary:
    ```
* - {py:obj}`MAX_URL_LENGTH <duck.http.middlewares.security.modules.sql_injection.MAX_URL_LENGTH>`
  - ```{autodocx-docstring} duck.http.middlewares.security.modules.sql_injection.MAX_URL_LENGTH
    :summary:
    ```
* - {py:obj}`PER_TOKEN_FLAG <duck.http.middlewares.security.modules.sql_injection.PER_TOKEN_FLAG>`
  - ```{autodocx-docstring} duck.http.middlewares.security.modules.sql_injection.PER_TOKEN_FLAG
    :summary:
    ```
* - {py:obj}`SCORE_THRESHOLD <duck.http.middlewares.security.modules.sql_injection.SCORE_THRESHOLD>`
  - ```{autodocx-docstring} duck.http.middlewares.security.modules.sql_injection.SCORE_THRESHOLD
    :summary:
    ```
* - {py:obj}`_ENCODED_PAYLOAD_RE <duck.http.middlewares.security.modules.sql_injection._ENCODED_PAYLOAD_RE>`
  - ```{autodocx-docstring} duck.http.middlewares.security.modules.sql_injection._ENCODED_PAYLOAD_RE
    :summary:
    ```
* - {py:obj}`_KEYWORD_RE <duck.http.middlewares.security.modules.sql_injection._KEYWORD_RE>`
  - ```{autodocx-docstring} duck.http.middlewares.security.modules.sql_injection._KEYWORD_RE
    :summary:
    ```
* - {py:obj}`_NUMERIC_EQ_RE <duck.http.middlewares.security.modules.sql_injection._NUMERIC_EQ_RE>`
  - ```{autodocx-docstring} duck.http.middlewares.security.modules.sql_injection._NUMERIC_EQ_RE
    :summary:
    ```
* - {py:obj}`_PATTERNS_WEIGHTS <duck.http.middlewares.security.modules.sql_injection._PATTERNS_WEIGHTS>`
  - ```{autodocx-docstring} duck.http.middlewares.security.modules.sql_injection._PATTERNS_WEIGHTS
    :summary:
    ```
* - {py:obj}`_QUICK_SAFE_RE <duck.http.middlewares.security.modules.sql_injection._QUICK_SAFE_RE>`
  - ```{autodocx-docstring} duck.http.middlewares.security.modules.sql_injection._QUICK_SAFE_RE
    :summary:
    ```
* - {py:obj}`_QUOTE_RE <duck.http.middlewares.security.modules.sql_injection._QUOTE_RE>`
  - ```{autodocx-docstring} duck.http.middlewares.security.modules.sql_injection._QUOTE_RE
    :summary:
    ```
* - {py:obj}`_SENSITIVE_WORDS_RE <duck.http.middlewares.security.modules.sql_injection._SENSITIVE_WORDS_RE>`
  - ```{autodocx-docstring} duck.http.middlewares.security.modules.sql_injection._SENSITIVE_WORDS_RE
    :summary:
    ```
* - {py:obj}`_SIMPLE_SUSPICIOUS_RE <duck.http.middlewares.security.modules.sql_injection._SIMPLE_SUSPICIOUS_RE>`
  - ```{autodocx-docstring} duck.http.middlewares.security.modules.sql_injection._SIMPLE_SUSPICIOUS_RE
    :summary:
    ```
* - {py:obj}`_SQL_COMMENT_RE <duck.http.middlewares.security.modules.sql_injection._SQL_COMMENT_RE>`
  - ```{autodocx-docstring} duck.http.middlewares.security.modules.sql_injection._SQL_COMMENT_RE
    :summary:
    ```
* - {py:obj}`_SQL_FUNCTION_RE <duck.http.middlewares.security.modules.sql_injection._SQL_FUNCTION_RE>`
  - ```{autodocx-docstring} duck.http.middlewares.security.modules.sql_injection._SQL_FUNCTION_RE
    :summary:
    ```
* - {py:obj}`_SQL_META_RE <duck.http.middlewares.security.modules.sql_injection._SQL_META_RE>`
  - ```{autodocx-docstring} duck.http.middlewares.security.modules.sql_injection._SQL_META_RE
    :summary:
    ```
* - {py:obj}`_STACKED_QUERY_RE <duck.http.middlewares.security.modules.sql_injection._STACKED_QUERY_RE>`
  - ```{autodocx-docstring} duck.http.middlewares.security.modules.sql_injection._STACKED_QUERY_RE
    :summary:
    ```
* - {py:obj}`_TAUTOLOGY_RE <duck.http.middlewares.security.modules.sql_injection._TAUTOLOGY_RE>`
  - ```{autodocx-docstring} duck.http.middlewares.security.modules.sql_injection._TAUTOLOGY_RE
    :summary:
    ```
* - {py:obj}`_UNION_SELECT_RE <duck.http.middlewares.security.modules.sql_injection._UNION_SELECT_RE>`
  - ```{autodocx-docstring} duck.http.middlewares.security.modules.sql_injection._UNION_SELECT_RE
    :summary:
    ```
````

### API

````{py:data} MAX_TOKEN_LENGTH
:canonical: duck.http.middlewares.security.modules.sql_injection.MAX_TOKEN_LENGTH
:value: >
   512

```{autodocx-docstring} duck.http.middlewares.security.modules.sql_injection.MAX_TOKEN_LENGTH
```

````

````{py:data} MAX_URL_LENGTH
:canonical: duck.http.middlewares.security.modules.sql_injection.MAX_URL_LENGTH
:value: >
   4096

```{autodocx-docstring} duck.http.middlewares.security.modules.sql_injection.MAX_URL_LENGTH
```

````

````{py:data} PER_TOKEN_FLAG
:canonical: duck.http.middlewares.security.modules.sql_injection.PER_TOKEN_FLAG
:value: >
   5

```{autodocx-docstring} duck.http.middlewares.security.modules.sql_injection.PER_TOKEN_FLAG
```

````

````{py:data} SCORE_THRESHOLD
:canonical: duck.http.middlewares.security.modules.sql_injection.SCORE_THRESHOLD
:value: >
   6

```{autodocx-docstring} duck.http.middlewares.security.modules.sql_injection.SCORE_THRESHOLD
```

````

````{py:data} _ENCODED_PAYLOAD_RE
:canonical: duck.http.middlewares.security.modules.sql_injection._ENCODED_PAYLOAD_RE
:value: >
   'compile(...)'

```{autodocx-docstring} duck.http.middlewares.security.modules.sql_injection._ENCODED_PAYLOAD_RE
```

````

````{py:data} _KEYWORD_RE
:canonical: duck.http.middlewares.security.modules.sql_injection._KEYWORD_RE
:value: >
   'compile(...)'

```{autodocx-docstring} duck.http.middlewares.security.modules.sql_injection._KEYWORD_RE
```

````

````{py:data} _NUMERIC_EQ_RE
:canonical: duck.http.middlewares.security.modules.sql_injection._NUMERIC_EQ_RE
:value: >
   'compile(...)'

```{autodocx-docstring} duck.http.middlewares.security.modules.sql_injection._NUMERIC_EQ_RE
```

````

````{py:data} _PATTERNS_WEIGHTS
:canonical: duck.http.middlewares.security.modules.sql_injection._PATTERNS_WEIGHTS
:value: >
   ((), (), (), (), (), (), (), (), (), (), (), ())

```{autodocx-docstring} duck.http.middlewares.security.modules.sql_injection._PATTERNS_WEIGHTS
```

````

````{py:data} _QUICK_SAFE_RE
:canonical: duck.http.middlewares.security.modules.sql_injection._QUICK_SAFE_RE
:value: >
   'compile(...)'

```{autodocx-docstring} duck.http.middlewares.security.modules.sql_injection._QUICK_SAFE_RE
```

````

````{py:data} _QUOTE_RE
:canonical: duck.http.middlewares.security.modules.sql_injection._QUOTE_RE
:value: >
   'compile(...)'

```{autodocx-docstring} duck.http.middlewares.security.modules.sql_injection._QUOTE_RE
```

````

````{py:data} _SENSITIVE_WORDS_RE
:canonical: duck.http.middlewares.security.modules.sql_injection._SENSITIVE_WORDS_RE
:value: >
   'compile(...)'

```{autodocx-docstring} duck.http.middlewares.security.modules.sql_injection._SENSITIVE_WORDS_RE
```

````

````{py:data} _SIMPLE_SUSPICIOUS_RE
:canonical: duck.http.middlewares.security.modules.sql_injection._SIMPLE_SUSPICIOUS_RE
:value: >
   'compile(...)'

```{autodocx-docstring} duck.http.middlewares.security.modules.sql_injection._SIMPLE_SUSPICIOUS_RE
```

````

````{py:data} _SQL_COMMENT_RE
:canonical: duck.http.middlewares.security.modules.sql_injection._SQL_COMMENT_RE
:value: >
   'compile(...)'

```{autodocx-docstring} duck.http.middlewares.security.modules.sql_injection._SQL_COMMENT_RE
```

````

````{py:data} _SQL_FUNCTION_RE
:canonical: duck.http.middlewares.security.modules.sql_injection._SQL_FUNCTION_RE
:value: >
   'compile(...)'

```{autodocx-docstring} duck.http.middlewares.security.modules.sql_injection._SQL_FUNCTION_RE
```

````

````{py:data} _SQL_META_RE
:canonical: duck.http.middlewares.security.modules.sql_injection._SQL_META_RE
:value: >
   'compile(...)'

```{autodocx-docstring} duck.http.middlewares.security.modules.sql_injection._SQL_META_RE
```

````

````{py:data} _STACKED_QUERY_RE
:canonical: duck.http.middlewares.security.modules.sql_injection._STACKED_QUERY_RE
:value: >
   'compile(...)'

```{autodocx-docstring} duck.http.middlewares.security.modules.sql_injection._STACKED_QUERY_RE
```

````

````{py:data} _TAUTOLOGY_RE
:canonical: duck.http.middlewares.security.modules.sql_injection._TAUTOLOGY_RE
:value: >
   'compile(...)'

```{autodocx-docstring} duck.http.middlewares.security.modules.sql_injection._TAUTOLOGY_RE
```

````

````{py:data} _UNION_SELECT_RE
:canonical: duck.http.middlewares.security.modules.sql_injection._UNION_SELECT_RE
:value: >
   'compile(...)'

```{autodocx-docstring} duck.http.middlewares.security.modules.sql_injection._UNION_SELECT_RE
```

````

````{py:function} _gather_tokens(url: str) -> list[str]
:canonical: duck.http.middlewares.security.modules.sql_injection._gather_tokens

```{autodocx-docstring} duck.http.middlewares.security.modules.sql_injection._gather_tokens
```
````

````{py:function} _shorten(token: str) -> str
:canonical: duck.http.middlewares.security.modules.sql_injection._shorten

```{autodocx-docstring} duck.http.middlewares.security.modules.sql_injection._shorten
```
````

````{py:function} check_sql_injection_in_url(url: str) -> bool
:canonical: duck.http.middlewares.security.modules.sql_injection.check_sql_injection_in_url

```{autodocx-docstring} duck.http.middlewares.security.modules.sql_injection.check_sql_injection_in_url
```
````

````{py:function} is_safe_url(url: str) -> bool
:canonical: duck.http.middlewares.security.modules.sql_injection.is_safe_url

```{autodocx-docstring} duck.http.middlewares.security.modules.sql_injection.is_safe_url
```
````
