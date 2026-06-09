# {py:mod}`duck.html.components.core.browser_state`

```{py:module} duck.html.components.core.browser_state
```

```{autodocx-docstring} duck.html.components.core.browser_state
:allowtitles:
```

## Module Contents

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`needs_browser_state_update <duck.html.components.core.browser_state.needs_browser_state_update>`
  - ```{autodocx-docstring} duck.html.components.core.browser_state.needs_browser_state_update
    :summary:
    ```
* - {py:obj}`queue_browser_state_response <duck.html.components.core.browser_state.queue_browser_state_response>`
  - ```{autodocx-docstring} duck.html.components.core.browser_state.queue_browser_state_response
    :summary:
    ```
* - {py:obj}`sync_browser_state <duck.html.components.core.browser_state.sync_browser_state>`
  - ```{autodocx-docstring} duck.html.components.core.browser_state.sync_browser_state
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`BROWSER_STATE_REGISTRY <duck.html.components.core.browser_state.BROWSER_STATE_REGISTRY>`
  - ```{autodocx-docstring} duck.html.components.core.browser_state.BROWSER_STATE_REGISTRY
    :summary:
    ```
````

### API

````{py:data} BROWSER_STATE_REGISTRY
:canonical: duck.html.components.core.browser_state.BROWSER_STATE_REGISTRY
:value: >
   'InMemoryCache(...)'

```{autodocx-docstring} duck.html.components.core.browser_state.BROWSER_STATE_REGISTRY
```

````

````{py:function} needs_browser_state_update(component_request: duck.http.request.HttpRequest) -> bool
:canonical: duck.html.components.core.browser_state.needs_browser_state_update

```{autodocx-docstring} duck.html.components.core.browser_state.needs_browser_state_update
```
````

````{py:function} queue_browser_state_response(component_request: duck.http.request.HttpRequest, response: duck.http.response.HttpResponse)
:canonical: duck.html.components.core.browser_state.queue_browser_state_response

```{autodocx-docstring} duck.html.components.core.browser_state.queue_browser_state_response
```
````

````{py:function} sync_browser_state(request)
:canonical: duck.html.components.core.browser_state.sync_browser_state

```{autodocx-docstring} duck.html.components.core.browser_state.sync_browser_state
```
````
