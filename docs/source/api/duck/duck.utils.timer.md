# {py:mod}`duck.utils.timer`

```{py:module} duck.utils.timer
```

```{autodocx-docstring} duck.utils.timer
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`OverlappingTimer <duck.utils.timer.OverlappingTimer>`
  - ```{autodocx-docstring} duck.utils.timer.OverlappingTimer
    :summary:
    ```
* - {py:obj}`SharedOverlappingTimer <duck.utils.timer.SharedOverlappingTimer>`
  - ```{autodocx-docstring} duck.utils.timer.SharedOverlappingTimer
    :summary:
    ```
* - {py:obj}`Timer <duck.utils.timer.Timer>`
  - ```{autodocx-docstring} duck.utils.timer.Timer
    :summary:
    ```
* - {py:obj}`TimerThreadPool <duck.utils.timer.TimerThreadPool>`
  - ```{autodocx-docstring} duck.utils.timer.TimerThreadPool
    :summary:
    ```
````

### API

`````{py:class} OverlappingTimer()
:canonical: duck.utils.timer.OverlappingTimer

```{autodocx-docstring} duck.utils.timer.OverlappingTimer
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.utils.timer.OverlappingTimer.__init__
```

````{py:method} _schedule(function: callable, seconds: int) -> None
:canonical: duck.utils.timer.OverlappingTimer._schedule
:staticmethod:

```{autodocx-docstring} duck.utils.timer.OverlappingTimer._schedule
```

````

````{py:method} _schedule_interval(function: callable, seconds: int) -> None
:canonical: duck.utils.timer.OverlappingTimer._schedule_interval
:staticmethod:

```{autodocx-docstring} duck.utils.timer.OverlappingTimer._schedule_interval
```

````

````{py:method} get_running_thread()
:canonical: duck.utils.timer.OverlappingTimer.get_running_thread

```{autodocx-docstring} duck.utils.timer.OverlappingTimer.get_running_thread
```

````

````{py:method} schedule(function: callable, seconds: int)
:canonical: duck.utils.timer.OverlappingTimer.schedule

```{autodocx-docstring} duck.utils.timer.OverlappingTimer.schedule
```

````

````{py:method} schedule_interval(function: callable, seconds: int)
:canonical: duck.utils.timer.OverlappingTimer.schedule_interval

```{autodocx-docstring} duck.utils.timer.OverlappingTimer.schedule_interval
```

````

`````

`````{py:class} SharedOverlappingTimer
:canonical: duck.utils.timer.SharedOverlappingTimer

```{autodocx-docstring} duck.utils.timer.SharedOverlappingTimer
```

````{py:method} _schedule(function: callable, seconds: int) -> None
:canonical: duck.utils.timer.SharedOverlappingTimer._schedule
:staticmethod:

```{autodocx-docstring} duck.utils.timer.SharedOverlappingTimer._schedule
```

````

````{py:method} _schedule_interval(function: callable, seconds: int) -> None
:canonical: duck.utils.timer.SharedOverlappingTimer._schedule_interval
:staticmethod:

```{autodocx-docstring} duck.utils.timer.SharedOverlappingTimer._schedule_interval
```

````

````{py:attribute} all_threads
:canonical: duck.utils.timer.SharedOverlappingTimer.all_threads
:type: list[threading.Thread]
:value: >
   []

```{autodocx-docstring} duck.utils.timer.SharedOverlappingTimer.all_threads
```

````

````{py:method} get_running_thread()
:canonical: duck.utils.timer.SharedOverlappingTimer.get_running_thread

```{autodocx-docstring} duck.utils.timer.SharedOverlappingTimer.get_running_thread
```

````

````{py:method} schedule(function: callable, seconds: int)
:canonical: duck.utils.timer.SharedOverlappingTimer.schedule

```{autodocx-docstring} duck.utils.timer.SharedOverlappingTimer.schedule
```

````

````{py:method} schedule_interval(function: callable, seconds: int)
:canonical: duck.utils.timer.SharedOverlappingTimer.schedule_interval

```{autodocx-docstring} duck.utils.timer.SharedOverlappingTimer.schedule_interval
```

````

`````

`````{py:class} Timer
:canonical: duck.utils.timer.Timer

```{autodocx-docstring} duck.utils.timer.Timer
```

````{py:method} _schedule(function: callable, seconds: int)
:canonical: duck.utils.timer.Timer._schedule
:classmethod:

```{autodocx-docstring} duck.utils.timer.Timer._schedule
```

````

````{py:method} _schedule_interval(function: callable, seconds: int)
:canonical: duck.utils.timer.Timer._schedule_interval
:classmethod:

```{autodocx-docstring} duck.utils.timer.Timer._schedule_interval
```

````

````{py:attribute} all_threads
:canonical: duck.utils.timer.Timer.all_threads
:type: list[threading.Thread]
:value: >
   []

```{autodocx-docstring} duck.utils.timer.Timer.all_threads
```

````

````{py:method} schedule(function: callable, seconds: int)
:canonical: duck.utils.timer.Timer.schedule
:classmethod:

```{autodocx-docstring} duck.utils.timer.Timer.schedule
```

````

````{py:method} schedule_interval(function: callable, seconds: int)
:canonical: duck.utils.timer.Timer.schedule_interval
:classmethod:

```{autodocx-docstring} duck.utils.timer.Timer.schedule_interval
```

````

`````

`````{py:class} TimerThreadPool
:canonical: duck.utils.timer.TimerThreadPool

```{autodocx-docstring} duck.utils.timer.TimerThreadPool
```

````{py:attribute} all
:canonical: duck.utils.timer.TimerThreadPool.all
:type: list
:value: >
   []

```{autodocx-docstring} duck.utils.timer.TimerThreadPool.all
```

````

`````
