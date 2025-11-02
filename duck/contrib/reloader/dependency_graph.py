"""
Provides a class to build a **reverse dependency graph** for Python modules,
track runtime/dynamic imports lazily, and determine safe reload order.  

Intended for use in hot-reload systems, e.g., DuckSightReloader.

---

Key Concepts:

1. Reverse Dependency Graph
   - Maps a module to the set of modules that depend on it.
   - Example:
       *module_a.py*  
       module_b.py -> imports module_a  
       module_c.py -> imports module_b  
       
       Reverse graph:
       ```py
       {
           "module_a": {"module_b"},
           "module_b": {"module_c"}
       }
       ```
   - If module_a changes, we reload module_b and module_c in safe order.

2. Static Imports
   - Collected using AST parsing from the source code.
   - Detects top-level and nested imports (in functions/classes).

3. Runtime Imports
   - Captured dynamically by patching Python's built-in __import__.
   - Tracks imports that happen inside setup functions or dynamically loaded code.

4. Safe Reload Workflow
   - Initialize DependencyGraph before importing your main app.
   - Optionally pre-build the graph for all files at startup.
   - On file change:
       1. Lazily build graph for changed file
       2. Merge into global graph
       3. Compute affected modules with get_modules_to_reload()
       4. Reload affected modules using importlib.reload()
       5. Apply SETTINGS.reload() or other mutable object updates
   - Repeat for subsequent file changes.

5. Usage Summary:

    ```py
    from duck.contrib.reloader.dependency_graph import DependencyGraph

    # Initialize BEFORE importing app
    graph = DependencyGraph(project_root=".")

    # Optional: pre-build graph for all project files
    for py_file in Path(".").rglob("*.py"):
        local_graph, _ = graph.build_graph_for_file(str(py_file))
        graph.merge_graph(local_graph)

    # Import app after graph is ready
    from duck.app import App
    app = App()
    app.run()

    # On file change:
    local_graph, changed_module = graph.build_graph_for_file(changed_file)
    graph.merge_graph(local_graph)
    affected = graph.get_modules_to_reload(changed_module)
    for mod_name in affected:
        importlib.reload(sys.modules[mod_name])
    ```

6. Notes:
   - Always initialize DependencyGraph before any other imports to capture runtime imports.
   - Supports lazy updates: only rebuild for changed files, not the whole project.
   - Leaf-first reload order ensures safe reloading of dependencies.
   - Runtime imports captured automatically; manual additions possible via add_runtime_dependency().

---

Author: Brian Musakwa
"""
import ast
import sys
import types
import builtins
import inspect

from pathlib import Path
from collections import defaultdict, deque


class DependencyGraph:
    """
    Tracks module dependencies (static and runtime) and provides
    methods to determine safe reload order for affected modules.
    """

    def __init__(self, project_root: str = "."):
        """
        Initialize the dependency graph.

        Args:
            project_root (str): Root directory of the project for module path resolution.
        """
        self.project_root = Path(project_root).resolve()
        self.reverse_graph = defaultdict(set)  # module -> set of dependents
        self.runtime_imports = set()  # modules imported dynamically

        # Patch built-in import to track runtime imports
        self._original_import = builtins.__import__
        builtins.__import__ = self._tracked_import
        
    def _tracked_import(self, name, globals=None, locals=None, fromlist=(), level=0):
        """
        Intercepts dynamic imports and updates the dependency graph lazily.

        Args:
            name (str): Name of the module being imported.
        """
        module = self._original_import(name, globals, locals, fromlist, level)

        if isinstance(module, types.ModuleType):
            self.runtime_imports.add(module.__name__)

            # Identify the module performing the import
            frame = inspect.currentframe()
            try:
                caller_module = inspect.getmodule(frame.f_back)
                if caller_module:
                    self.reverse_graph[module.__name__].add(caller_module.__name__)
            finally:
                del frame

        return module
        
    def module_name_from_path(self, file_path: str) -> str:
        """
        Convert a file path to a Python module name relative to project root.

        Args:
            file_path (str): Path to the Python file.

        Returns:
            str: Python module name (dot-separated).
        """
        path = Path(file_path).resolve()
        rel = path.relative_to(self.project_root).with_suffix("")
        return ".".join(rel.parts)
        
    @staticmethod
    def parse_imports(source: str) -> set:
        """
        Parse all imported module names in a Python source file.

        Args:
            source (str): Python source code.

        Returns:
            set: Names of imported modules.
        """
        tree = ast.parse(source)
        imports = set()

        class ImportVisitor(ast.NodeVisitor):
            def visit_Import(self, node):
                for n in node.names:
                    imports.add(n.name)

            def visit_ImportFrom(self, node):
                if node.module:
                    imports.add(node.module)

            def visit_FunctionDef(self, node):
                self.generic_visit(node)

            def visit_ClassDef(self, node):
                self.generic_visit(node)

        ImportVisitor().visit(tree)
        return imports
        
    def build_graph_for_file(self, file_path: str) -> tuple[dict, str]:
        """
        Build a reverse dependency graph for a specific file lazily.

        Args:
            file_path (str): File to parse.

        Returns:
            tuple[dict, str]: Local graph {imported_module: set([current_module])},
                              Current module name
        """
        module_name = self.module_name_from_path(file_path)
        try:
            source = Path(file_path).read_text()
        except Exception:
            return {}, module_name  # Could not read file

        imports = self.parse_imports(source)
        local_graph = {imp: set([module_name]) for imp in imports}
        return local_graph, module_name

    def merge_graph(self, local_graph: dict):
        """
        Merge a local graph into the global reverse dependency graph.

        Args:
            local_graph (dict): {imported_module: set([dependent_modules])}
        """
        for imported_module, dependents in local_graph.items():
            self.reverse_graph[imported_module].update(dependents)
            
    def get_modules_to_reload(self, changed_module: str) -> list[str]:
        """
        Return a list of modules affected by a changed module,
        in safe reload order (leaf-first).

        Args:
            changed_module (str): Module that has changed.

        Returns:
            list[str]: Modules to reload in order.
        """
        affected = set()
        queue = deque([changed_module])

        while queue:
            mod = queue.popleft()
            if mod in affected:
                continue
            affected.add(mod)
            for dependent in self.reverse_graph.get(mod, []):
                queue.append(dependent)

        # Leaf-first order: modules with fewer dots first
        return sorted(affected, key=lambda x: len(x.split(".")))
        
    def add_runtime_dependency(self, module_name: str, imported_module: str):
        """
        Manually add a runtime dependency (optional).

        Args:
            module_name (str): The module that imported another.
            imported_module (str): The module that was imported.
        """
        self.reverse_graph[imported_module].add(module_name)
        self.runtime_imports.add(imported_module)
        
    def restore_import(self):
        """
        Restore the original built-in import function.
        """
        builtins.__import__ = self._original_import
        
    def stop(self):
        """
        Cleanup the `DependancyGraph` by restoring the default `__import__` function.
        """
        self.restore_import()
        
    def __repr__(self):
        return (
            f"<DependencyGraph "
            f"modules={len(self.reverse_graph)}, "
            f"runtime_imports={len(self.runtime_imports)}>"
        )
