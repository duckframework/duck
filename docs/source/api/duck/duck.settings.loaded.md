# {py:mod}`duck.settings.loaded`

```{py:module} duck.settings.loaded
```

```{autodocx-docstring} duck.settings.loaded
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`Loaded <duck.settings.loaded.Loaded>`
  - ```{autodocx-docstring} duck.settings.loaded.Loaded
    :summary:
    ```
````

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`get_asgi <duck.settings.loaded.get_asgi>`
  - ```{autodocx-docstring} duck.settings.loaded.get_asgi
    :summary:
    ```
* - {py:obj}`get_automation_dispatcher <duck.settings.loaded.get_automation_dispatcher>`
  - ```{autodocx-docstring} duck.settings.loaded.get_automation_dispatcher
    :summary:
    ```
* - {py:obj}`get_blueprints <duck.settings.loaded.get_blueprints>`
  - ```{autodocx-docstring} duck.settings.loaded.get_blueprints
    :summary:
    ```
* - {py:obj}`get_content_compression_settings <duck.settings.loaded.get_content_compression_settings>`
  - ```{autodocx-docstring} duck.settings.loaded.get_content_compression_settings
    :summary:
    ```
* - {py:obj}`get_file_upload_handler <duck.settings.loaded.get_file_upload_handler>`
  - ```{autodocx-docstring} duck.settings.loaded.get_file_upload_handler
    :summary:
    ```
* - {py:obj}`get_normalizers <duck.settings.loaded.get_normalizers>`
  - ```{autodocx-docstring} duck.settings.loaded.get_normalizers
    :summary:
    ```
* - {py:obj}`get_preferred_log_style <duck.settings.loaded.get_preferred_log_style>`
  - ```{autodocx-docstring} duck.settings.loaded.get_preferred_log_style
    :summary:
    ```
* - {py:obj}`get_proxy_handlers <duck.settings.loaded.get_proxy_handlers>`
  - ```{autodocx-docstring} duck.settings.loaded.get_proxy_handlers
    :summary:
    ```
* - {py:obj}`get_request_class <duck.settings.loaded.get_request_class>`
  - ```{autodocx-docstring} duck.settings.loaded.get_request_class
    :summary:
    ```
* - {py:obj}`get_request_handling_task_executor <duck.settings.loaded.get_request_handling_task_executor>`
  - ```{autodocx-docstring} duck.settings.loaded.get_request_handling_task_executor
    :summary:
    ```
* - {py:obj}`get_session_storage <duck.settings.loaded.get_session_storage>`
  - ```{autodocx-docstring} duck.settings.loaded.get_session_storage
    :summary:
    ```
* - {py:obj}`get_session_store <duck.settings.loaded.get_session_store>`
  - ```{autodocx-docstring} duck.settings.loaded.get_session_store
    :summary:
    ```
* - {py:obj}`get_triggers_and_automations <duck.settings.loaded.get_triggers_and_automations>`
  - ```{autodocx-docstring} duck.settings.loaded.get_triggers_and_automations
    :summary:
    ```
* - {py:obj}`get_user_middlewares <duck.settings.loaded.get_user_middlewares>`
  - ```{autodocx-docstring} duck.settings.loaded.get_user_middlewares
    :summary:
    ```
* - {py:obj}`get_user_templatetags <duck.settings.loaded.get_user_templatetags>`
  - ```{autodocx-docstring} duck.settings.loaded.get_user_templatetags
    :summary:
    ```
* - {py:obj}`get_user_urlpatterns <duck.settings.loaded.get_user_urlpatterns>`
  - ```{autodocx-docstring} duck.settings.loaded.get_user_urlpatterns
    :summary:
    ```
* - {py:obj}`get_wsgi <duck.settings.loaded.get_wsgi>`
  - ```{autodocx-docstring} duck.settings.loaded.get_wsgi
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`SettingsLoaded <duck.settings.loaded.SettingsLoaded>`
  - ```{autodocx-docstring} duck.settings.loaded.SettingsLoaded
    :summary:
    ```
````

### API

````{py:class} Loaded()
:canonical: duck.settings.loaded.Loaded

```{autodocx-docstring} duck.settings.loaded.Loaded
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.settings.loaded.Loaded.__init__
```

````

````{py:data} SettingsLoaded
:canonical: duck.settings.loaded.SettingsLoaded
:value: >
   'Lazy(...)'

```{autodocx-docstring} duck.settings.loaded.SettingsLoaded
```

````

````{py:function} get_asgi() -> typing.Any
:canonical: duck.settings.loaded.get_asgi

```{autodocx-docstring} duck.settings.loaded.get_asgi
```
````

````{py:function} get_automation_dispatcher() -> duck.automation.dispatcher.AutomationDispatcher
:canonical: duck.settings.loaded.get_automation_dispatcher

```{autodocx-docstring} duck.settings.loaded.get_automation_dispatcher
```
````

````{py:function} get_blueprints() -> typing.List[duck.routes.Blueprint]
:canonical: duck.settings.loaded.get_blueprints

```{autodocx-docstring} duck.settings.loaded.get_blueprints
```
````

````{py:function} get_content_compression_settings()
:canonical: duck.settings.loaded.get_content_compression_settings

```{autodocx-docstring} duck.settings.loaded.get_content_compression_settings
```
````

````{py:function} get_file_upload_handler() -> typing.Any
:canonical: duck.settings.loaded.get_file_upload_handler

```{autodocx-docstring} duck.settings.loaded.get_file_upload_handler
```
````

````{py:function} get_normalizers()
:canonical: duck.settings.loaded.get_normalizers

```{autodocx-docstring} duck.settings.loaded.get_normalizers
```
````

````{py:function} get_preferred_log_style() -> str
:canonical: duck.settings.loaded.get_preferred_log_style

```{autodocx-docstring} duck.settings.loaded.get_preferred_log_style
```
````

````{py:function} get_proxy_handlers() -> typing.List[typing.Type[typing.Any]]
:canonical: duck.settings.loaded.get_proxy_handlers

```{autodocx-docstring} duck.settings.loaded.get_proxy_handlers
```
````

````{py:function} get_request_class() -> typing.Type[typing.Any]
:canonical: duck.settings.loaded.get_request_class

```{autodocx-docstring} duck.settings.loaded.get_request_class
```
````

````{py:function} get_request_handling_task_executor()
:canonical: duck.settings.loaded.get_request_handling_task_executor

```{autodocx-docstring} duck.settings.loaded.get_request_handling_task_executor
```
````

````{py:function} get_session_storage()
:canonical: duck.settings.loaded.get_session_storage

```{autodocx-docstring} duck.settings.loaded.get_session_storage
```
````

````{py:function} get_session_store()
:canonical: duck.settings.loaded.get_session_store

```{autodocx-docstring} duck.settings.loaded.get_session_store
```
````

````{py:function} get_triggers_and_automations() -> typing.List[typing.Tuple[duck.automation.trigger.AutomationTrigger, duck.automation.Automation]]
:canonical: duck.settings.loaded.get_triggers_and_automations

```{autodocx-docstring} duck.settings.loaded.get_triggers_and_automations
```
````

````{py:function} get_user_middlewares() -> typing.List[typing.Type]
:canonical: duck.settings.loaded.get_user_middlewares

```{autodocx-docstring} duck.settings.loaded.get_user_middlewares
```
````

````{py:function} get_user_templatetags() -> typing.List[duck.template.templatetags.TemplateTag | duck.template.templatetags.TemplateFilter]
:canonical: duck.settings.loaded.get_user_templatetags

```{autodocx-docstring} duck.settings.loaded.get_user_templatetags
```
````

````{py:function} get_user_urlpatterns()
:canonical: duck.settings.loaded.get_user_urlpatterns

```{autodocx-docstring} duck.settings.loaded.get_user_urlpatterns
```
````

````{py:function} get_wsgi() -> typing.Any
:canonical: duck.settings.loaded.get_wsgi

```{autodocx-docstring} duck.settings.loaded.get_wsgi
```
````
