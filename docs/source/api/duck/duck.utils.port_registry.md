# {py:mod}`duck.utils.port_registry`

```{py:module} duck.utils.port_registry
```

```{autodocx-docstring} duck.utils.port_registry
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`PortRegistry <duck.utils.port_registry.PortRegistry>`
  - ```{autodocx-docstring} duck.utils.port_registry.PortRegistry
    :summary:
    ```
````

### API

`````{py:class} PortRegistry
:canonical: duck.utils.port_registry.PortRegistry

```{autodocx-docstring} duck.utils.port_registry.PortRegistry
```

````{py:attribute} _occupied_ports
:canonical: duck.utils.port_registry.PortRegistry._occupied_ports
:type: dict[int, str]
:value: >
   None

```{autodocx-docstring} duck.utils.port_registry.PortRegistry._occupied_ports
```

````

````{py:method} get_port_occupier(port: int) -> str | None
:canonical: duck.utils.port_registry.PortRegistry.get_port_occupier
:classmethod:

```{autodocx-docstring} duck.utils.port_registry.PortRegistry.get_port_occupier
```

````

````{py:method} is_port_occupied(port: int) -> bool
:canonical: duck.utils.port_registry.PortRegistry.is_port_occupied
:classmethod:

```{autodocx-docstring} duck.utils.port_registry.PortRegistry.is_port_occupied
```

````

````{py:method} register_port(port: int, occupier: str) -> None
:canonical: duck.utils.port_registry.PortRegistry.register_port
:classmethod:

```{autodocx-docstring} duck.utils.port_registry.PortRegistry.register_port
```

````

````{py:method} unregister_port(port: int) -> None
:canonical: duck.utils.port_registry.PortRegistry.unregister_port
:classmethod:

```{autodocx-docstring} duck.utils.port_registry.PortRegistry.unregister_port
```

````

`````
