# {py:mod}`duck.contrib.reloader.ducksight`

```{py:module} duck.contrib.reloader.ducksight
```

```{autodocx-docstring} duck.contrib.reloader.ducksight
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`DuckSightReloader <duck.contrib.reloader.ducksight.DuckSightReloader>`
  - ```{autodocx-docstring} duck.contrib.reloader.ducksight.DuckSightReloader
    :summary:
    ```
* - {py:obj}`Handler <duck.contrib.reloader.ducksight.Handler>`
  - ```{autodocx-docstring} duck.contrib.reloader.ducksight.Handler
    :summary:
    ```
````

### API

`````{py:class} DuckSightReloader(watch_dir: str)
:canonical: duck.contrib.reloader.ducksight.DuckSightReloader

```{autodocx-docstring} duck.contrib.reloader.ducksight.DuckSightReloader
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.contrib.reloader.ducksight.DuckSightReloader.__init__
```

````{py:method} run()
:canonical: duck.contrib.reloader.ducksight.DuckSightReloader.run

```{autodocx-docstring} duck.contrib.reloader.ducksight.DuckSightReloader.run
```

````

````{py:method} stop()
:canonical: duck.contrib.reloader.ducksight.DuckSightReloader.stop

```{autodocx-docstring} duck.contrib.reloader.ducksight.DuckSightReloader.stop
```

````

`````

`````{py:class} Handler(debounce_interval=0.6)
:canonical: duck.contrib.reloader.ducksight.Handler

Bases: {py:obj}`watchdog.events.FileSystemEventHandler`

```{autodocx-docstring} duck.contrib.reloader.ducksight.Handler
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.contrib.reloader.ducksight.Handler.__init__
```

````{py:method} _trigger_restart()
:canonical: duck.contrib.reloader.ducksight.Handler._trigger_restart

```{autodocx-docstring} duck.contrib.reloader.ducksight.Handler._trigger_restart
```

````

````{py:method} on_any_event(event)
:canonical: duck.contrib.reloader.ducksight.Handler.on_any_event

```{autodocx-docstring} duck.contrib.reloader.ducksight.Handler.on_any_event
```

````

````{py:method} restart_webserver(changed_file: str)
:canonical: duck.contrib.reloader.ducksight.Handler.restart_webserver

```{autodocx-docstring} duck.contrib.reloader.ducksight.Handler.restart_webserver
```

````

`````
