# {py:mod}`duck.template.environment`

```{py:module} duck.template.environment
```

```{autodocx-docstring} duck.template.environment
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`DjangoEngine <duck.template.environment.DjangoEngine>`
  - ```{autodocx-docstring} duck.template.environment.DjangoEngine
    :summary:
    ```
* - {py:obj}`Engine <duck.template.environment.Engine>`
  - ```{autodocx-docstring} duck.template.environment.Engine
    :summary:
    ```
* - {py:obj}`Jinja2Engine <duck.template.environment.Jinja2Engine>`
  - ```{autodocx-docstring} duck.template.environment.Jinja2Engine
    :summary:
    ```
* - {py:obj}`Template <duck.template.environment.Template>`
  - ```{autodocx-docstring} duck.template.environment.Template
    :summary:
    ```
````

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`default_django_engine <duck.template.environment.default_django_engine>`
  - ```{autodocx-docstring} duck.template.environment.default_django_engine
    :summary:
    ```
* - {py:obj}`default_jinja2_engine <duck.template.environment.default_jinja2_engine>`
  - ```{autodocx-docstring} duck.template.environment.default_jinja2_engine
    :summary:
    ```
````

### API

`````{py:class} DjangoEngine(autoescape: bool = True, libraries: typing.Optional[typing.List[str]] = None, _django_engine: typing.Optional[typing.Any] = None, loaders: typing.List[str] = None)
:canonical: duck.template.environment.DjangoEngine

Bases: {py:obj}`duck.template.environment.Engine`

```{autodocx-docstring} duck.template.environment.DjangoEngine
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.template.environment.DjangoEngine.__init__
```

````{py:attribute} __slots__
:canonical: duck.template.environment.DjangoEngine.__slots__
:value: >
   None

```{autodocx-docstring} duck.template.environment.DjangoEngine.__slots__
```

````

````{py:method} apply_templatetags(builtin_libraries: typing.Optional[typing.List[str]] = None, custom_libraries: typing.Optional[typing.Dict[str, str]] = None)
:canonical: duck.template.environment.DjangoEngine.apply_templatetags

```{autodocx-docstring} duck.template.environment.DjangoEngine.apply_templatetags
```

````

````{py:method} get_default()
:canonical: duck.template.environment.DjangoEngine.get_default
:classmethod:

```{autodocx-docstring} duck.template.environment.DjangoEngine.get_default
```

````

````{py:method} get_default_django_engine()
:canonical: duck.template.environment.DjangoEngine.get_default_django_engine

```{autodocx-docstring} duck.template.environment.DjangoEngine.get_default_django_engine
```

````

````{py:method} render_template(template: duck.template.environment.Template) -> str
:canonical: duck.template.environment.DjangoEngine.render_template

```{autodocx-docstring} duck.template.environment.DjangoEngine.render_template
```

````

````{py:method} setup_django_engine()
:canonical: duck.template.environment.DjangoEngine.setup_django_engine

```{autodocx-docstring} duck.template.environment.DjangoEngine.setup_django_engine
```

````

`````

`````{py:class} Engine
:canonical: duck.template.environment.Engine

```{autodocx-docstring} duck.template.environment.Engine
```

````{py:method} get_default()
:canonical: duck.template.environment.Engine.get_default
:classmethod:

```{autodocx-docstring} duck.template.environment.Engine.get_default
```

````

````{py:method} get_template(template_name: str) -> str
:canonical: duck.template.environment.Engine.get_template

```{autodocx-docstring} duck.template.environment.Engine.get_template
```

````

````{py:method} render_template(template: duck.template.environment.Template)
:canonical: duck.template.environment.Engine.render_template
:abstractmethod:

```{autodocx-docstring} duck.template.environment.Engine.render_template
```

````

`````

`````{py:class} Jinja2Engine(autoescape: bool = True, custom_templatetags: typing.Optional[typing.List[typing.Union[duck.template.templatetags.TemplateTag, duck.template.templatetags.TemplateFilter]]] = None, environment: typing.Optional[jinja2.Environment] = None, loader: typing.Any = None)
:canonical: duck.template.environment.Jinja2Engine

Bases: {py:obj}`duck.template.environment.Engine`

```{autodocx-docstring} duck.template.environment.Jinja2Engine
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.template.environment.Jinja2Engine.__init__
```

````{py:attribute} __slots__
:canonical: duck.template.environment.Jinja2Engine.__slots__
:value: >
   None

```{autodocx-docstring} duck.template.environment.Jinja2Engine.__slots__
```

````

````{py:method} apply_templatetags(templatetags: typing.Optional[typing.List[typing.Union[duck.template.templatetags.TemplateTag, duck.template.templatetags.TemplateFilter]]] = None)
:canonical: duck.template.environment.Jinja2Engine.apply_templatetags

```{autodocx-docstring} duck.template.environment.Jinja2Engine.apply_templatetags
```

````

````{py:method} get_default_environment() -> jinja2.Environment
:canonical: duck.template.environment.Jinja2Engine.get_default_environment

```{autodocx-docstring} duck.template.environment.Jinja2Engine.get_default_environment
```

````

````{py:method} render_template(template: duck.template.environment.Template) -> str
:canonical: duck.template.environment.Jinja2Engine.render_template

```{autodocx-docstring} duck.template.environment.Jinja2Engine.render_template
```

````

````{py:method} setup_environment()
:canonical: duck.template.environment.Jinja2Engine.setup_environment

```{autodocx-docstring} duck.template.environment.Jinja2Engine.setup_environment
```

````

`````

`````{py:class} Template(context: typing.Optional[typing.Dict] = None, name: typing.Optional[str] = None, origin: typing.Optional[str] = None, engine: duck.template.environment.Engine = None)
:canonical: duck.template.environment.Template

```{autodocx-docstring} duck.template.environment.Template
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.template.environment.Template.__init__
```

````{py:attribute} __slots__
:canonical: duck.template.environment.Template.__slots__
:value: >
   None

```{autodocx-docstring} duck.template.environment.Template.__slots__
```

````

````{py:method} render_template() -> str
:canonical: duck.template.environment.Template.render_template

```{autodocx-docstring} duck.template.environment.Template.render_template
```

````

`````

````{py:function} default_django_engine() -> DjangoEngine
:canonical: duck.template.environment.default_django_engine

```{autodocx-docstring} duck.template.environment.default_django_engine
```
````

````{py:function} default_jinja2_engine() -> Jinja2Engine
:canonical: duck.template.environment.default_jinja2_engine

```{autodocx-docstring} duck.template.environment.default_jinja2_engine
```
````
