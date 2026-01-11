# {py:mod}`duck.etc.internals.template`

```{py:module} duck.etc.internals.template
```

```{autodocx-docstring} duck.etc.internals.template
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`InternalJinja2Engine <duck.etc.internals.template.InternalJinja2Engine>`
  - ```{autodocx-docstring} duck.etc.internals.template.InternalJinja2Engine
    :summary:
    ```
* - {py:obj}`InternalJinja2FileSystemLoader <duck.etc.internals.template.InternalJinja2FileSystemLoader>`
  -
````

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`internal_render <duck.etc.internals.template.internal_render>`
  - ```{autodocx-docstring} duck.etc.internals.template.internal_render
    :summary:
    ```
````

### API

`````{py:class} InternalJinja2Engine(autoescape: bool = True, custom_templatetags: typing.Optional[typing.List[typing.Union[duck.template.templatetags.TemplateTag, duck.template.templatetags.TemplateFilter]]] = None, environment: typing.Optional[jinja2.Environment] = None, loader: typing.Any = None)
:canonical: duck.etc.internals.template.InternalJinja2Engine

Bases: {py:obj}`duck.template.environment.Jinja2Engine`

```{autodocx-docstring} duck.etc.internals.template.InternalJinja2Engine
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.etc.internals.template.InternalJinja2Engine.__init__
```

````{py:method} get_default()
:canonical: duck.etc.internals.template.InternalJinja2Engine.get_default
:classmethod:

```{autodocx-docstring} duck.etc.internals.template.InternalJinja2Engine.get_default
```

````

`````

`````{py:class} InternalJinja2FileSystemLoader
:canonical: duck.etc.internals.template.InternalJinja2FileSystemLoader

Bases: {py:obj}`duck.template.loaders.Jinja2FileSystemLoader`

````{py:method} blueprint_template_dirs()
:canonical: duck.etc.internals.template.InternalJinja2FileSystemLoader.blueprint_template_dirs

````

````{py:method} global_template_dirs() -> typing.List[str]
:canonical: duck.etc.internals.template.InternalJinja2FileSystemLoader.global_template_dirs

````

`````

````{py:function} internal_render(request: duck.http.request.HttpRequest, template: str, context: typing.Dict[typing.Any, typing.Any] = {}, **kwargs) -> duck.http.response.TemplateResponse
:canonical: duck.etc.internals.template.internal_render

```{autodocx-docstring} duck.etc.internals.template.internal_render
```
````
