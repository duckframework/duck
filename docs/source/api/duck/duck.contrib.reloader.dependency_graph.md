# {py:mod}`duck.contrib.reloader.dependency_graph`

```{py:module} duck.contrib.reloader.dependency_graph
```

```{autodocx-docstring} duck.contrib.reloader.dependency_graph
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`DependencyGraph <duck.contrib.reloader.dependency_graph.DependencyGraph>`
  - ```{autodocx-docstring} duck.contrib.reloader.dependency_graph.DependencyGraph
    :summary:
    ```
````

### API

`````{py:class} DependencyGraph(project_root: str = '.')
:canonical: duck.contrib.reloader.dependency_graph.DependencyGraph

```{autodocx-docstring} duck.contrib.reloader.dependency_graph.DependencyGraph
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.contrib.reloader.dependency_graph.DependencyGraph.__init__
```

````{py:method} __repr__()
:canonical: duck.contrib.reloader.dependency_graph.DependencyGraph.__repr__

````

````{py:method} _tracked_import(name, globals=None, locals=None, fromlist=(), level=0)
:canonical: duck.contrib.reloader.dependency_graph.DependencyGraph._tracked_import

```{autodocx-docstring} duck.contrib.reloader.dependency_graph.DependencyGraph._tracked_import
```

````

````{py:method} add_runtime_dependency(module_name: str, imported_module: str)
:canonical: duck.contrib.reloader.dependency_graph.DependencyGraph.add_runtime_dependency

```{autodocx-docstring} duck.contrib.reloader.dependency_graph.DependencyGraph.add_runtime_dependency
```

````

````{py:method} build_graph_for_file(file_path: str) -> tuple[dict, str]
:canonical: duck.contrib.reloader.dependency_graph.DependencyGraph.build_graph_for_file

```{autodocx-docstring} duck.contrib.reloader.dependency_graph.DependencyGraph.build_graph_for_file
```

````

````{py:method} get_modules_to_reload(changed_module: str) -> list[str]
:canonical: duck.contrib.reloader.dependency_graph.DependencyGraph.get_modules_to_reload

```{autodocx-docstring} duck.contrib.reloader.dependency_graph.DependencyGraph.get_modules_to_reload
```

````

````{py:method} merge_graph(local_graph: dict)
:canonical: duck.contrib.reloader.dependency_graph.DependencyGraph.merge_graph

```{autodocx-docstring} duck.contrib.reloader.dependency_graph.DependencyGraph.merge_graph
```

````

````{py:method} module_name_from_path(file_path: str) -> str
:canonical: duck.contrib.reloader.dependency_graph.DependencyGraph.module_name_from_path

```{autodocx-docstring} duck.contrib.reloader.dependency_graph.DependencyGraph.module_name_from_path
```

````

````{py:method} parse_imports(source: str) -> set
:canonical: duck.contrib.reloader.dependency_graph.DependencyGraph.parse_imports
:staticmethod:

```{autodocx-docstring} duck.contrib.reloader.dependency_graph.DependencyGraph.parse_imports
```

````

````{py:method} restore_import()
:canonical: duck.contrib.reloader.dependency_graph.DependencyGraph.restore_import

```{autodocx-docstring} duck.contrib.reloader.dependency_graph.DependencyGraph.restore_import
```

````

````{py:method} stop()
:canonical: duck.contrib.reloader.dependency_graph.DependencyGraph.stop

```{autodocx-docstring} duck.contrib.reloader.dependency_graph.DependencyGraph.stop
```

````

`````
