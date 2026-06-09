# {py:mod}`duck.backend.django.urls`

```{py:module} duck.backend.django.urls
```

```{autodocx-docstring} duck.backend.django.urls
:allowtitles:
```

## Module Contents

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`get_correct_urlpatterns <duck.backend.django.urls.get_correct_urlpatterns>`
  - ```{autodocx-docstring} duck.backend.django.urls.get_correct_urlpatterns
    :summary:
    ```
* - {py:obj}`get_duck_urlpatterns <duck.backend.django.urls.get_duck_urlpatterns>`
  - ```{autodocx-docstring} duck.backend.django.urls.get_duck_urlpatterns
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`urlpatterns <duck.backend.django.urls.urlpatterns>`
  - ```{autodocx-docstring} duck.backend.django.urls.urlpatterns
    :summary:
    ```
````

### API

````{py:exception} DjangoURLConflict(message, **kws)
:canonical: duck.backend.django.urls.DjangoURLConflict

Bases: {py:obj}`duck.exceptions.all.RouteError`

```{autodocx-docstring} duck.backend.django.urls.DjangoURLConflict
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.backend.django.urls.DjangoURLConflict.__init__
```

````

````{py:function} get_correct_urlpatterns() -> typing.List
:canonical: duck.backend.django.urls.get_correct_urlpatterns

```{autodocx-docstring} duck.backend.django.urls.get_correct_urlpatterns
```
````

````{py:function} get_duck_urlpatterns() -> typing.List
:canonical: duck.backend.django.urls.get_duck_urlpatterns

```{autodocx-docstring} duck.backend.django.urls.get_duck_urlpatterns
```
````

````{py:data} urlpatterns
:canonical: duck.backend.django.urls.urlpatterns
:value: >
   'get_correct_urlpatterns(...)'

```{autodocx-docstring} duck.backend.django.urls.urlpatterns
```

````
