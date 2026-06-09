# {py:mod}`duck.automation.trigger`

```{py:module} duck.automation.trigger
```

```{autodocx-docstring} duck.automation.trigger
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`AutomationTrigger <duck.automation.trigger.AutomationTrigger>`
  - ```{autodocx-docstring} duck.automation.trigger.AutomationTrigger
    :summary:
    ```
* - {py:obj}`NoTriggerBase <duck.automation.trigger.NoTriggerBase>`
  - ```{autodocx-docstring} duck.automation.trigger.NoTriggerBase
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`NoTrigger <duck.automation.trigger.NoTrigger>`
  - ```{autodocx-docstring} duck.automation.trigger.NoTrigger
    :summary:
    ```
````

### API

`````{py:class} AutomationTrigger(name: str = None, description: str = None)
:canonical: duck.automation.trigger.AutomationTrigger

```{autodocx-docstring} duck.automation.trigger.AutomationTrigger
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.automation.trigger.AutomationTrigger.__init__
```

````{py:method} __repr__()
:canonical: duck.automation.trigger.AutomationTrigger.__repr__

```{autodocx-docstring} duck.automation.trigger.AutomationTrigger.__repr__
```

````

````{py:method} check_trigger() -> bool
:canonical: duck.automation.trigger.AutomationTrigger.check_trigger
:abstractmethod:

```{autodocx-docstring} duck.automation.trigger.AutomationTrigger.check_trigger
```

````

`````

````{py:data} NoTrigger
:canonical: duck.automation.trigger.NoTrigger
:value: >
   'NoTriggerBase(...)'

```{autodocx-docstring} duck.automation.trigger.NoTrigger
```

````

`````{py:class} NoTriggerBase(name: str = None, description: str = None)
:canonical: duck.automation.trigger.NoTriggerBase

Bases: {py:obj}`duck.automation.trigger.AutomationTrigger`

```{autodocx-docstring} duck.automation.trigger.NoTriggerBase
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.automation.trigger.NoTriggerBase.__init__
```

````{py:method} check_trigger() -> bool
:canonical: duck.automation.trigger.NoTriggerBase.check_trigger

```{autodocx-docstring} duck.automation.trigger.NoTriggerBase.check_trigger
```

````

`````
