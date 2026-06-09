# {py:mod}`duck.automation`

```{py:module} duck.automation
```

```{autodocx-docstring} duck.automation
:allowtitles:
```

## Submodules

```{toctree}
:titlesonly:
:maxdepth: 1

duck.automation.dispatcher
duck.automation.trigger
```

## Package Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`Automation <duck.automation.Automation>`
  - ```{autodocx-docstring} duck.automation.Automation
    :summary:
    ```
* - {py:obj}`AutomationThread <duck.automation.AutomationThread>`
  - ```{autodocx-docstring} duck.automation.AutomationThread
    :summary:
    ```
* - {py:obj}`SampleAutomationBase <duck.automation.SampleAutomationBase>`
  - ```{autodocx-docstring} duck.automation.SampleAutomationBase
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`SampleAutomation <duck.automation.SampleAutomation>`
  - ```{autodocx-docstring} duck.automation.SampleAutomation
    :summary:
    ```
````

### API

`````{py:class} Automation(callback: callable = None, name: str = None, threaded: bool = True, async_: bool = False, start_time: datetime.datetime | str = 'immediate', schedules: int = 1, interval: float | int = None, description: str = None)
:canonical: duck.automation.Automation

```{autodocx-docstring} duck.automation.Automation
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.automation.Automation.__init__
```

````{py:method} __repr__()
:canonical: duck.automation.Automation.__repr__

````

````{py:method} _async_start()
:canonical: duck.automation.Automation._async_start
:async:

```{autodocx-docstring} duck.automation.Automation._async_start
```

````

````{py:method} _start()
:canonical: duck.automation.Automation._start

```{autodocx-docstring} duck.automation.Automation._start
```

````

````{py:method} execute()
:canonical: duck.automation.Automation.execute

```{autodocx-docstring} duck.automation.Automation.execute
```

````

````{py:property} execution_cycles
:canonical: duck.automation.Automation.execution_cycles
:type: int

```{autodocx-docstring} duck.automation.Automation.execution_cycles
```

````

````{py:property} execution_times
:canonical: duck.automation.Automation.execution_times
:type: int

```{autodocx-docstring} duck.automation.Automation.execution_times
```

````

````{py:property} finished
:canonical: duck.automation.Automation.finished

```{autodocx-docstring} duck.automation.Automation.finished
```

````

````{py:property} finished_at
:canonical: duck.automation.Automation.finished_at
:type: datetime.datetime

```{autodocx-docstring} duck.automation.Automation.finished_at
```

````

````{py:property} first_execution
:canonical: duck.automation.Automation.first_execution
:type: bool

```{autodocx-docstring} duck.automation.Automation.first_execution
```

````

````{py:method} get_running_app()
:canonical: duck.automation.Automation.get_running_app

```{autodocx-docstring} duck.automation.Automation.get_running_app
```

````

````{py:method} get_short_description()
:canonical: duck.automation.Automation.get_short_description

```{autodocx-docstring} duck.automation.Automation.get_short_description
```

````

````{py:method} get_thread()
:canonical: duck.automation.Automation.get_thread

```{autodocx-docstring} duck.automation.Automation.get_thread
```

````

````{py:property} is_running
:canonical: duck.automation.Automation.is_running
:type: bool

```{autodocx-docstring} duck.automation.Automation.is_running
```

````

````{py:method} join()
:canonical: duck.automation.Automation.join

```{autodocx-docstring} duck.automation.Automation.join
```

````

````{py:property} latest_error
:canonical: duck.automation.Automation.latest_error

```{autodocx-docstring} duck.automation.Automation.latest_error
```

````

````{py:method} on_error(e)
:canonical: duck.automation.Automation.on_error

```{autodocx-docstring} duck.automation.Automation.on_error
```

````

````{py:method} on_finish()
:canonical: duck.automation.Automation.on_finish

```{autodocx-docstring} duck.automation.Automation.on_finish
```

````

````{py:method} on_post_execute()
:canonical: duck.automation.Automation.on_post_execute

```{autodocx-docstring} duck.automation.Automation.on_post_execute
```

````

````{py:method} on_pre_execute()
:canonical: duck.automation.Automation.on_pre_execute

```{autodocx-docstring} duck.automation.Automation.on_pre_execute
```

````

````{py:method} on_start()
:canonical: duck.automation.Automation.on_start

```{autodocx-docstring} duck.automation.Automation.on_start
```

````

````{py:method} prepare_stop()
:canonical: duck.automation.Automation.prepare_stop

```{autodocx-docstring} duck.automation.Automation.prepare_stop
```

````

````{py:method} set_running_app(app)
:canonical: duck.automation.Automation.set_running_app

```{autodocx-docstring} duck.automation.Automation.set_running_app
```

````

````{py:method} start()
:canonical: duck.automation.Automation.start

```{autodocx-docstring} duck.automation.Automation.start
```

````

````{py:property} started_at
:canonical: duck.automation.Automation.started_at
:type: datetime.datetime

```{autodocx-docstring} duck.automation.Automation.started_at
```

````

````{py:method} to_thread() -> duck.automation.AutomationThread
:canonical: duck.automation.Automation.to_thread

```{autodocx-docstring} duck.automation.Automation.to_thread
```

````

`````

````{py:exception} AutomationError()
:canonical: duck.automation.AutomationError

Bases: {py:obj}`Exception`

```{autodocx-docstring} duck.automation.AutomationError
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.automation.AutomationError.__init__
```

````

`````{py:class} AutomationThread(group=None, target=None, name=None, args=(), kwargs=None, *, daemon=None)
:canonical: duck.automation.AutomationThread

Bases: {py:obj}`threading.Thread`

```{autodocx-docstring} duck.automation.AutomationThread
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.automation.AutomationThread.__init__
```

````{py:method} on_stop()
:canonical: duck.automation.AutomationThread.on_stop

```{autodocx-docstring} duck.automation.AutomationThread.on_stop
```

````

````{py:method} set_on_stop_callback(callback: callable)
:canonical: duck.automation.AutomationThread.set_on_stop_callback

```{autodocx-docstring} duck.automation.AutomationThread.set_on_stop_callback
```

````

````{py:method} start(*args, **kw)
:canonical: duck.automation.AutomationThread.start

````

`````

````{py:data} SampleAutomation
:canonical: duck.automation.SampleAutomation
:value: >
   'SampleAutomationBase(...)'

```{autodocx-docstring} duck.automation.SampleAutomation
```

````

`````{py:class} SampleAutomationBase(callback: callable = None, name: str = None, threaded: bool = True, async_: bool = False, start_time: datetime.datetime | str = 'immediate', schedules: int = 1, interval: float | int = None, description: str = None)
:canonical: duck.automation.SampleAutomationBase

Bases: {py:obj}`duck.automation.Automation`

```{autodocx-docstring} duck.automation.SampleAutomationBase
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.automation.SampleAutomationBase.__init__
```

````{py:method} execute()
:canonical: duck.automation.SampleAutomationBase.execute

```{autodocx-docstring} duck.automation.SampleAutomationBase.execute
```

````

`````
