# {py:mod}`duck.utils.urlcrack`

```{py:module} duck.utils.urlcrack
```

```{autodocx-docstring} duck.utils.urlcrack
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`URL <duck.utils.urlcrack.URL>`
  - ```{autodocx-docstring} duck.utils.urlcrack.URL
    :summary:
    ```
````

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`joinpaths <duck.utils.urlcrack.joinpaths>`
  - ```{autodocx-docstring} duck.utils.urlcrack.joinpaths
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`__author__ <duck.utils.urlcrack.__author__>`
  - ```{autodocx-docstring} duck.utils.urlcrack.__author__
    :summary:
    ```
* - {py:obj}`__email__ <duck.utils.urlcrack.__email__>`
  - ```{autodocx-docstring} duck.utils.urlcrack.__email__
    :summary:
    ```
````

### API

````{py:exception} InvalidPortError()
:canonical: duck.utils.urlcrack.InvalidPortError

Bases: {py:obj}`Exception`

```{autodocx-docstring} duck.utils.urlcrack.InvalidPortError
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.utils.urlcrack.InvalidPortError.__init__
```

````

````{py:exception} InvalidURLAuthorityError()
:canonical: duck.utils.urlcrack.InvalidURLAuthorityError

Bases: {py:obj}`Exception`

```{autodocx-docstring} duck.utils.urlcrack.InvalidURLAuthorityError
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.utils.urlcrack.InvalidURLAuthorityError.__init__
```

````

````{py:exception} InvalidURLError()
:canonical: duck.utils.urlcrack.InvalidURLError

Bases: {py:obj}`Exception`

```{autodocx-docstring} duck.utils.urlcrack.InvalidURLError
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.utils.urlcrack.InvalidURLError.__init__
```

````

````{py:exception} InvalidURLPathError()
:canonical: duck.utils.urlcrack.InvalidURLPathError

Bases: {py:obj}`Exception`

```{autodocx-docstring} duck.utils.urlcrack.InvalidURLPathError
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.utils.urlcrack.InvalidURLPathError.__init__
```

````

`````{py:class} URL(url: str, normalize_url: bool = True, normalization_ignore_chars: typing.Optional[typing.List[str]] = None)
:canonical: duck.utils.urlcrack.URL

```{autodocx-docstring} duck.utils.urlcrack.URL
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.utils.urlcrack.URL.__init__
```

````{py:method} __repr__()
:canonical: duck.utils.urlcrack.URL.__repr__

```{autodocx-docstring} duck.utils.urlcrack.URL.__repr__
```

````

````{py:attribute} __slots__
:canonical: duck.utils.urlcrack.URL.__slots__
:value: >
   None

```{autodocx-docstring} duck.utils.urlcrack.URL.__slots__
```

````

````{py:method} build_url_string(scheme: typing.Optional[str] = None, netloc: typing.Optional[str] = None, path: typing.Optional[str] = None, query: typing.Optional[str] = None, fragment: typing.Optional[str] = None) -> str
:canonical: duck.utils.urlcrack.URL.build_url_string

```{autodocx-docstring} duck.utils.urlcrack.URL.build_url_string
```

````

````{py:property} host
:canonical: duck.utils.urlcrack.URL.host
:type: typing.Optional[str]

```{autodocx-docstring} duck.utils.urlcrack.URL.host
```

````

````{py:method} innerjoin(head_url: str, normalize_url: bool = True, normalization_ignore_chars: typing.Optional[typing.List[str]] = None) -> duck.utils.urlcrack.URL
:canonical: duck.utils.urlcrack.URL.innerjoin

```{autodocx-docstring} duck.utils.urlcrack.URL.innerjoin
```

````

````{py:property} is_absolute
:canonical: duck.utils.urlcrack.URL.is_absolute
:type: bool

```{autodocx-docstring} duck.utils.urlcrack.URL.is_absolute
```

````

````{py:method} join(head_url: str, normalize_url: bool = True, normalization_ignore_chars: typing.Optional[typing.List[str]] = None) -> duck.utils.urlcrack.URL
:canonical: duck.utils.urlcrack.URL.join

```{autodocx-docstring} duck.utils.urlcrack.URL.join
```

````

````{py:method} normalize_url(url: str, ignore_chars: typing.Optional[typing.List[str]] = None)
:canonical: duck.utils.urlcrack.URL.normalize_url
:classmethod:

```{autodocx-docstring} duck.utils.urlcrack.URL.normalize_url
```

````

````{py:method} normalize_url_path(url_path: str, ignore_chars: typing.Optional[typing.List[str]] = None)
:canonical: duck.utils.urlcrack.URL.normalize_url_path
:classmethod:

```{autodocx-docstring} duck.utils.urlcrack.URL.normalize_url_path
```

````

````{py:method} parse(url: str, normalize_url: bool = True, normalization_ignore_chars: typing.Optional[typing.List[str]] = None)
:canonical: duck.utils.urlcrack.URL.parse

```{autodocx-docstring} duck.utils.urlcrack.URL.parse
```

````

````{py:property} port
:canonical: duck.utils.urlcrack.URL.port
:type: typing.Optional[int]

```{autodocx-docstring} duck.utils.urlcrack.URL.port
```

````

````{py:method} split_host_and_port(authority: str, convert_port_to_int: bool = True) -> typing.Tuple[str, typing.Union[str, int]]
:canonical: duck.utils.urlcrack.URL.split_host_and_port

```{autodocx-docstring} duck.utils.urlcrack.URL.split_host_and_port
```

````

````{py:method} split_path_components(url_path: str) -> typing.Tuple[str, str, str]
:canonical: duck.utils.urlcrack.URL.split_path_components

```{autodocx-docstring} duck.utils.urlcrack.URL.split_path_components
```

````

````{py:method} split_scheme_and_authority(url: str) -> typing.Tuple[str, str, str]
:canonical: duck.utils.urlcrack.URL.split_scheme_and_authority

```{autodocx-docstring} duck.utils.urlcrack.URL.split_scheme_and_authority
```

````

````{py:method} to_str() -> str
:canonical: duck.utils.urlcrack.URL.to_str

```{autodocx-docstring} duck.utils.urlcrack.URL.to_str
```

````

````{py:method} urljoin(base_url: str, head_url: str, replace_authority: bool = False, full_path_replacement: bool = True, normalize_urls: bool = True, normalization_ignore_chars: typing.Optional[typing.List[str]] = None) -> str
:canonical: duck.utils.urlcrack.URL.urljoin
:classmethod:

```{autodocx-docstring} duck.utils.urlcrack.URL.urljoin
```

````

````{py:property} user_info
:canonical: duck.utils.urlcrack.URL.user_info
:type: typing.Optional[str]

```{autodocx-docstring} duck.utils.urlcrack.URL.user_info
```

````

`````

````{py:data} __author__
:canonical: duck.utils.urlcrack.__author__
:value: >
   'Brian Musakwa'

```{autodocx-docstring} duck.utils.urlcrack.__author__
```

````

````{py:data} __email__
:canonical: duck.utils.urlcrack.__email__
:value: >
   'digreatbrian@gmail.com'

```{autodocx-docstring} duck.utils.urlcrack.__email__
```

````

````{py:function} joinpaths(path1: str, path2: str, *more)
:canonical: duck.utils.urlcrack.joinpaths

```{autodocx-docstring} duck.utils.urlcrack.joinpaths
```
````
