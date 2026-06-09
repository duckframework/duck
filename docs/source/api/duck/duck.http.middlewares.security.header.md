# {py:mod}`duck.http.middlewares.security.header`

```{py:module} duck.http.middlewares.security.header
```

```{autodocx-docstring} duck.http.middlewares.security.header
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`HeaderInjectionMiddleware <duck.http.middlewares.security.header.HeaderInjectionMiddleware>`
  - ```{autodocx-docstring} duck.http.middlewares.security.header.HeaderInjectionMiddleware
    :summary:
    ```
* - {py:obj}`HostMiddleware <duck.http.middlewares.security.header.HostMiddleware>`
  - ```{autodocx-docstring} duck.http.middlewares.security.header.HostMiddleware
    :summary:
    ```
````

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`is_valid_host <duck.http.middlewares.security.header.is_valid_host>`
  - ```{autodocx-docstring} duck.http.middlewares.security.header.is_valid_host
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`HOSTNAME_LABEL_RE <duck.http.middlewares.security.header.HOSTNAME_LABEL_RE>`
  - ```{autodocx-docstring} duck.http.middlewares.security.header.HOSTNAME_LABEL_RE
    :summary:
    ```
* - {py:obj}`MAX_HOSTNAME_LENGTH <duck.http.middlewares.security.header.MAX_HOSTNAME_LENGTH>`
  - ```{autodocx-docstring} duck.http.middlewares.security.header.MAX_HOSTNAME_LENGTH
    :summary:
    ```
````

### API

````{py:data} HOSTNAME_LABEL_RE
:canonical: duck.http.middlewares.security.header.HOSTNAME_LABEL_RE
:value: >
   'compile(...)'

```{autodocx-docstring} duck.http.middlewares.security.header.HOSTNAME_LABEL_RE
```

````

`````{py:class} HeaderInjectionMiddleware
:canonical: duck.http.middlewares.security.header.HeaderInjectionMiddleware

Bases: {py:obj}`duck.http.middlewares.BaseMiddleware`

```{autodocx-docstring} duck.http.middlewares.security.header.HeaderInjectionMiddleware
```

````{py:attribute} debug_message
:canonical: duck.http.middlewares.security.header.HeaderInjectionMiddleware.debug_message
:type: str
:value: >
   'HeaderInjectionMiddleware: Potential header injection'

```{autodocx-docstring} duck.http.middlewares.security.header.HeaderInjectionMiddleware.debug_message
```

````

````{py:method} get_error_response(request)
:canonical: duck.http.middlewares.security.header.HeaderInjectionMiddleware.get_error_response
:classmethod:

````

````{py:method} process_request(request)
:canonical: duck.http.middlewares.security.header.HeaderInjectionMiddleware.process_request
:classmethod:

````

`````

`````{py:class} HostMiddleware
:canonical: duck.http.middlewares.security.header.HostMiddleware

Bases: {py:obj}`duck.http.middlewares.BaseMiddleware`

```{autodocx-docstring} duck.http.middlewares.security.header.HostMiddleware
```

````{py:attribute} allowed_hosts
:canonical: duck.http.middlewares.security.header.HostMiddleware.allowed_hosts
:value: >
   None

```{autodocx-docstring} duck.http.middlewares.security.header.HostMiddleware.allowed_hosts
```

````

````{py:attribute} debug_message
:canonical: duck.http.middlewares.security.header.HostMiddleware.debug_message
:type: str
:value: >
   'HostMiddleware: Host invalid/unrecognized'

```{autodocx-docstring} duck.http.middlewares.security.header.HostMiddleware.debug_message
```

````

````{py:method} get_error_response(request)
:canonical: duck.http.middlewares.security.header.HostMiddleware.get_error_response
:classmethod:

````

````{py:method} process_request(request)
:canonical: duck.http.middlewares.security.header.HostMiddleware.process_request
:classmethod:

````

`````

````{py:data} MAX_HOSTNAME_LENGTH
:canonical: duck.http.middlewares.security.header.MAX_HOSTNAME_LENGTH
:value: >
   253

```{autodocx-docstring} duck.http.middlewares.security.header.MAX_HOSTNAME_LENGTH
```

````

````{py:function} is_valid_host(host)
:canonical: duck.http.middlewares.security.header.is_valid_host

```{autodocx-docstring} duck.http.middlewares.security.header.is_valid_host
```
````
