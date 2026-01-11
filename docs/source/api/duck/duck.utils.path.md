# {py:mod}`duck.utils.path`

```{py:module} duck.utils.path
```

```{autodocx-docstring} duck.utils.path
:allowtitles:
```

## Module Contents

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`build_absolute_uri <duck.utils.path.build_absolute_uri>`
  - ```{autodocx-docstring} duck.utils.path.build_absolute_uri
    :summary:
    ```
* - {py:obj}`is_absolute_url <duck.utils.path.is_absolute_url>`
  - ```{autodocx-docstring} duck.utils.path.is_absolute_url
    :summary:
    ```
* - {py:obj}`is_good_url_path <duck.utils.path.is_good_url_path>`
  - ```{autodocx-docstring} duck.utils.path.is_good_url_path
    :summary:
    ```
* - {py:obj}`joinpaths <duck.utils.path.joinpaths>`
  - ```{autodocx-docstring} duck.utils.path.joinpaths
    :summary:
    ```
* - {py:obj}`normalize_url_path <duck.utils.path.normalize_url_path>`
  - ```{autodocx-docstring} duck.utils.path.normalize_url_path
    :summary:
    ```
* - {py:obj}`paths_are_same <duck.utils.path.paths_are_same>`
  - ```{autodocx-docstring} duck.utils.path.paths_are_same
    :summary:
    ```
* - {py:obj}`replace_hostname <duck.utils.path.replace_hostname>`
  - ```{autodocx-docstring} duck.utils.path.replace_hostname
    :summary:
    ```
* - {py:obj}`sanitize_path_segment <duck.utils.path.sanitize_path_segment>`
  - ```{autodocx-docstring} duck.utils.path.sanitize_path_segment
    :summary:
    ```
* - {py:obj}`url_normalize <duck.utils.path.url_normalize>`
  - ```{autodocx-docstring} duck.utils.path.url_normalize
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`URL_PATH_REGEX <duck.utils.path.URL_PATH_REGEX>`
  - ```{autodocx-docstring} duck.utils.path.URL_PATH_REGEX
    :summary:
    ```
````

### API

````{py:data} URL_PATH_REGEX
:canonical: duck.utils.path.URL_PATH_REGEX
:value: >
   '^[a-zA-Z0-9\\-._~:/?#\ue001\ue001@!$&\\()*+,;=%]*$'

```{autodocx-docstring} duck.utils.path.URL_PATH_REGEX
```

````

````{py:function} build_absolute_uri(root_url: str, path: str, normalization_ignore_chars: typing.Optional[typing.List[str]] = None) -> str
:canonical: duck.utils.path.build_absolute_uri

```{autodocx-docstring} duck.utils.path.build_absolute_uri
```
````

````{py:function} is_absolute_url(url: str)
:canonical: duck.utils.path.is_absolute_url

```{autodocx-docstring} duck.utils.path.is_absolute_url
```
````

````{py:function} is_good_url_path(url_path: str) -> bool
:canonical: duck.utils.path.is_good_url_path

```{autodocx-docstring} duck.utils.path.is_good_url_path
```
````

````{py:function} joinpaths(path1: typing.Union[str, pathlib.Path], path2: typing.Union[str, pathlib.Path], *more)
:canonical: duck.utils.path.joinpaths

```{autodocx-docstring} duck.utils.path.joinpaths
```
````

````{py:function} normalize_url_path(url_path: str, ignore_chars: typing.Optional[typing.List[str]] = None) -> str
:canonical: duck.utils.path.normalize_url_path

```{autodocx-docstring} duck.utils.path.normalize_url_path
```
````

````{py:function} paths_are_same(path1, path2)
:canonical: duck.utils.path.paths_are_same

```{autodocx-docstring} duck.utils.path.paths_are_same
```
````

````{py:function} replace_hostname(url: str, hostname: str) -> str
:canonical: duck.utils.path.replace_hostname

```{autodocx-docstring} duck.utils.path.replace_hostname
```
````

````{py:function} sanitize_path_segment(segment)
:canonical: duck.utils.path.sanitize_path_segment

```{autodocx-docstring} duck.utils.path.sanitize_path_segment
```
````

````{py:function} url_normalize(url: str, ignore_chars: typing.Optional[typing.List[str]] = None) -> str
:canonical: duck.utils.path.url_normalize

```{autodocx-docstring} duck.utils.path.url_normalize
```
````
