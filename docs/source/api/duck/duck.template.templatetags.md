# {py:mod}`duck.template.templatetags`

```{py:module} duck.template.templatetags
```

```{autodocx-docstring} duck.template.templatetags
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`BlockTemplateTag <duck.template.templatetags.BlockTemplateTag>`
  - ```{autodocx-docstring} duck.template.templatetags.BlockTemplateTag
    :summary:
    ```
* - {py:obj}`TemplateFilter <duck.template.templatetags.TemplateFilter>`
  - ```{autodocx-docstring} duck.template.templatetags.TemplateFilter
    :summary:
    ```
* - {py:obj}`TemplateTag <duck.template.templatetags.TemplateTag>`
  - ```{autodocx-docstring} duck.template.templatetags.TemplateTag
    :summary:
    ```
````

### API

`````{py:class} BlockTemplateTag(tagname: str, tagcallable: typing.Callable, takes_context: bool = False)
:canonical: duck.template.templatetags.BlockTemplateTag

Bases: {py:obj}`duck.template.templatetags.TemplateTag`

```{autodocx-docstring} duck.template.templatetags.BlockTemplateTag
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.template.templatetags.BlockTemplateTag.__init__
```

````{py:method} register_in_django(library)
:canonical: duck.template.templatetags.BlockTemplateTag.register_in_django

```{autodocx-docstring} duck.template.templatetags.BlockTemplateTag.register_in_django
```

````

````{py:method} register_in_jinja2(environment)
:canonical: duck.template.templatetags.BlockTemplateTag.register_in_jinja2

```{autodocx-docstring} duck.template.templatetags.BlockTemplateTag.register_in_jinja2
```

````

`````

`````{py:class} TemplateFilter(filtername: str, filtercallable: typing.Callable)
:canonical: duck.template.templatetags.TemplateFilter

```{autodocx-docstring} duck.template.templatetags.TemplateFilter
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.template.templatetags.TemplateFilter.__init__
```

````{py:attribute} __all_filters
:canonical: duck.template.templatetags.TemplateFilter.__all_filters
:value: >
   'defaultdict(...)'

```{autodocx-docstring} duck.template.templatetags.TemplateFilter.__all_filters
```

````

````{py:method} __repr__()
:canonical: duck.template.templatetags.TemplateFilter.__repr__

```{autodocx-docstring} duck.template.templatetags.TemplateFilter.__repr__
```

````

````{py:method} get_filter(filtername: str)
:canonical: duck.template.templatetags.TemplateFilter.get_filter
:classmethod:

```{autodocx-docstring} duck.template.templatetags.TemplateFilter.get_filter
```

````

````{py:method} register_in_django(library)
:canonical: duck.template.templatetags.TemplateFilter.register_in_django

```{autodocx-docstring} duck.template.templatetags.TemplateFilter.register_in_django
```

````

````{py:method} register_in_jinja2(environment)
:canonical: duck.template.templatetags.TemplateFilter.register_in_jinja2

```{autodocx-docstring} duck.template.templatetags.TemplateFilter.register_in_jinja2
```

````

`````

````{py:exception} TemplateFilterError()
:canonical: duck.template.templatetags.TemplateFilterError

Bases: {py:obj}`Exception`

```{autodocx-docstring} duck.template.templatetags.TemplateFilterError
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.template.templatetags.TemplateFilterError.__init__
```

````

`````{py:class} TemplateTag(tagname: str, tagcallable: typing.Callable, takes_context: bool = False)
:canonical: duck.template.templatetags.TemplateTag

```{autodocx-docstring} duck.template.templatetags.TemplateTag
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.template.templatetags.TemplateTag.__init__
```

````{py:attribute} __all_tags
:canonical: duck.template.templatetags.TemplateTag.__all_tags
:value: >
   'defaultdict(...)'

```{autodocx-docstring} duck.template.templatetags.TemplateTag.__all_tags
```

````

````{py:method} __repr__()
:canonical: duck.template.templatetags.TemplateTag.__repr__

```{autodocx-docstring} duck.template.templatetags.TemplateTag.__repr__
```

````

````{py:method} get_tag(tagname: str)
:canonical: duck.template.templatetags.TemplateTag.get_tag
:classmethod:

```{autodocx-docstring} duck.template.templatetags.TemplateTag.get_tag
```

````

````{py:method} register_in_django(library)
:canonical: duck.template.templatetags.TemplateTag.register_in_django

```{autodocx-docstring} duck.template.templatetags.TemplateTag.register_in_django
```

````

````{py:method} register_in_jinja2(environment)
:canonical: duck.template.templatetags.TemplateTag.register_in_jinja2

```{autodocx-docstring} duck.template.templatetags.TemplateTag.register_in_jinja2
```

````

`````

````{py:exception} TemplateTagError()
:canonical: duck.template.templatetags.TemplateTagError

Bases: {py:obj}`Exception`

```{autodocx-docstring} duck.template.templatetags.TemplateTagError
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.template.templatetags.TemplateTagError.__init__
```

````
