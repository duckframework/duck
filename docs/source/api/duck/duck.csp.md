# {py:mod}`duck.csp`

```{py:module} duck.csp
```

```{autodocx-docstring} duck.csp
:allowtitles:
```

## Module Contents

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`csp_nonce <duck.csp.csp_nonce>`
  - ```{autodocx-docstring} duck.csp.csp_nonce
    :summary:
    ```
* - {py:obj}`refresh_nonce <duck.csp.refresh_nonce>`
  - ```{autodocx-docstring} duck.csp.refresh_nonce
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`csp_nonce_flag <duck.csp.csp_nonce_flag>`
  - ```{autodocx-docstring} duck.csp.csp_nonce_flag
    :summary:
    ```
````

### API

````{py:function} csp_nonce(request, add_nonce_prefix: bool = False) -> str
:canonical: duck.csp.csp_nonce

```{autodocx-docstring} duck.csp.csp_nonce
```
````

````{py:data} csp_nonce_flag
:canonical: duck.csp.csp_nonce_flag
:value: >
   'requires-csp-nonce'

```{autodocx-docstring} duck.csp.csp_nonce_flag
```

````

````{py:function} refresh_nonce(request) -> str
:canonical: duck.csp.refresh_nonce

```{autodocx-docstring} duck.csp.refresh_nonce
```
````
