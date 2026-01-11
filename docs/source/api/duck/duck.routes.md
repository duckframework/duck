# {py:mod}`duck.routes`

```{py:module} duck.routes
```

```{autodocx-docstring} duck.routes
:allowtitles:
```

## Submodules

```{toctree}
:titlesonly:
:maxdepth: 1

duck.routes.route_blueprint
duck.routes.route_registry
```

## Package Contents

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`blueprint_joinpath <duck.routes.blueprint_joinpath>`
  - ```{autodocx-docstring} duck.routes.blueprint_joinpath
    :summary:
    ```
* - {py:obj}`register_blueprints <duck.routes.register_blueprints>`
  - ```{autodocx-docstring} duck.routes.register_blueprints
    :summary:
    ```
* - {py:obj}`register_urlpatterns <duck.routes.register_urlpatterns>`
  - ```{autodocx-docstring} duck.routes.register_urlpatterns
    :summary:
    ```
````

### API

````{py:exception} BlueprintJoinPathError(message, **kws)
:canonical: duck.routes.BlueprintJoinPathError

Bases: {py:obj}`duck.exceptions.all.BlueprintError`

```{autodocx-docstring} duck.routes.BlueprintJoinPathError
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.routes.BlueprintJoinPathError.__init__
```

````

````{py:exception} BlueprintJoinPathNameNoMatch(message, **kws)
:canonical: duck.routes.BlueprintJoinPathNameNoMatch

Bases: {py:obj}`duck.routes.BlueprintJoinPathError`

```{autodocx-docstring} duck.routes.BlueprintJoinPathNameNoMatch
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.routes.BlueprintJoinPathNameNoMatch.__init__
```

````

````{py:function} blueprint_joinpath(blueprint_subdir: str, path: str, blueprint: duck.routes.route_blueprint.Blueprint) -> str
:canonical: duck.routes.blueprint_joinpath

```{autodocx-docstring} duck.routes.blueprint_joinpath
```
````

````{py:function} register_blueprints(blueprints: typing.List[duck.routes.route_blueprint.Blueprint])
:canonical: duck.routes.register_blueprints

```{autodocx-docstring} duck.routes.register_blueprints
```
````

````{py:function} register_urlpatterns(urlpatterns: typing.List[duck.urls.URLPattern])
:canonical: duck.routes.register_urlpatterns

```{autodocx-docstring} duck.routes.register_urlpatterns
```
````
