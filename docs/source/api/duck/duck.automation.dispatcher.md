# {py:mod}`duck.automation.dispatcher`

```{py:module} duck.automation.dispatcher
```

```{autodocx-docstring} duck.automation.dispatcher
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`AutomationDispatcher <duck.automation.dispatcher.AutomationDispatcher>`
  - ```{autodocx-docstring} duck.automation.dispatcher.AutomationDispatcher
    :summary:
    ```
* - {py:obj}`DispatcherV1 <duck.automation.dispatcher.DispatcherV1>`
  -
````

### API

`````{py:class} AutomationDispatcher(application=None)
:canonical: duck.automation.dispatcher.AutomationDispatcher

```{autodocx-docstring} duck.automation.dispatcher.AutomationDispatcher
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.automation.dispatcher.AutomationDispatcher.__init__
```

````{py:attribute} __executed_automations
:canonical: duck.automation.dispatcher.AutomationDispatcher.__executed_automations
:type: list[duck.automation.Automation]
:value: >
   []

```{autodocx-docstring} duck.automation.dispatcher.AutomationDispatcher.__executed_automations
```

````

````{py:attribute} __queue
:canonical: duck.automation.dispatcher.AutomationDispatcher.__queue
:type: dict[duck.automation.trigger.AutomationTrigger, list[duck.automation.Automation]]
:value: >
   None

```{autodocx-docstring} duck.automation.dispatcher.AutomationDispatcher.__queue
```

````

````{py:property} executed_automations
:canonical: duck.automation.dispatcher.AutomationDispatcher.executed_automations
:type: list[duck.automation.Automation]

```{autodocx-docstring} duck.automation.dispatcher.AutomationDispatcher.executed_automations
```

````

````{py:method} listen()
:canonical: duck.automation.dispatcher.AutomationDispatcher.listen
:abstractmethod:

```{autodocx-docstring} duck.automation.dispatcher.AutomationDispatcher.listen
```

````

````{py:attribute} poll
:canonical: duck.automation.dispatcher.AutomationDispatcher.poll
:type: int | float
:value: >
   1

```{autodocx-docstring} duck.automation.dispatcher.AutomationDispatcher.poll
```

````

````{py:property} queue
:canonical: duck.automation.dispatcher.AutomationDispatcher.queue
:type: dict[duck.automation.trigger.AutomationTrigger, list[duck.automation.Automation]]

```{autodocx-docstring} duck.automation.dispatcher.AutomationDispatcher.queue
```

````

````{py:method} register(trigger: duck.automation.trigger.AutomationTrigger, automation: duck.automation.Automation)
:canonical: duck.automation.dispatcher.AutomationDispatcher.register

```{autodocx-docstring} duck.automation.dispatcher.AutomationDispatcher.register
```

````

````{py:method} run_automations(automations: list[duck.automation.Automation])
:canonical: duck.automation.dispatcher.AutomationDispatcher.run_automations

```{autodocx-docstring} duck.automation.dispatcher.AutomationDispatcher.run_automations
```

````

````{py:method} start()
:canonical: duck.automation.dispatcher.AutomationDispatcher.start

```{autodocx-docstring} duck.automation.dispatcher.AutomationDispatcher.start
```

````

````{py:method} stop()
:canonical: duck.automation.dispatcher.AutomationDispatcher.stop

```{autodocx-docstring} duck.automation.dispatcher.AutomationDispatcher.stop
```

````

````{py:method} unregister(trigger: duck.automation.trigger.AutomationTrigger, automation: duck.automation.Automation)
:canonical: duck.automation.dispatcher.AutomationDispatcher.unregister

```{autodocx-docstring} duck.automation.dispatcher.AutomationDispatcher.unregister
```

````

`````

````{py:exception} AutomationDispatcherError()
:canonical: duck.automation.dispatcher.AutomationDispatcherError

Bases: {py:obj}`Exception`

```{autodocx-docstring} duck.automation.dispatcher.AutomationDispatcherError
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.automation.dispatcher.AutomationDispatcherError.__init__
```

````

`````{py:class} DispatcherV1(application=None)
:canonical: duck.automation.dispatcher.DispatcherV1

Bases: {py:obj}`duck.automation.dispatcher.AutomationDispatcher`

````{py:method} listen()
:canonical: duck.automation.dispatcher.DispatcherV1.listen

````

`````
