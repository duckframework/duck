# {py:mod}`duck.utils.eventlist`

```{py:module} duck.utils.eventlist
```

```{autodocx-docstring} duck.utils.eventlist
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`EventList <duck.utils.eventlist.EventList>`
  - ```{autodocx-docstring} duck.utils.eventlist.EventList
    :summary:
    ```
````

### API

`````{py:class} EventList(initlist=None, on_new_item: typing.Optional[typing.Callable[[typing.Any], None]] = None, on_delete_item: typing.Optional[typing.Callable[[typing.Any], None]] = None, skip_initlist_events: bool = False)
:canonical: duck.utils.eventlist.EventList

Bases: {py:obj}`list`

```{autodocx-docstring} duck.utils.eventlist.EventList
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.utils.eventlist.EventList.__init__
```

````{py:method} __delitem__(index)
:canonical: duck.utils.eventlist.EventList.__delitem__

```{autodocx-docstring} duck.utils.eventlist.EventList.__delitem__
```

````

````{py:method} __iadd__(other)
:canonical: duck.utils.eventlist.EventList.__iadd__

```{autodocx-docstring} duck.utils.eventlist.EventList.__iadd__
```

````

````{py:method} __repr__()
:canonical: duck.utils.eventlist.EventList.__repr__

````

````{py:method} __setitem__(index, value)
:canonical: duck.utils.eventlist.EventList.__setitem__

```{autodocx-docstring} duck.utils.eventlist.EventList.__setitem__
```

````

````{py:attribute} __slots__
:canonical: duck.utils.eventlist.EventList.__slots__
:value: >
   None

```{autodocx-docstring} duck.utils.eventlist.EventList.__slots__
```

````

````{py:method} __str__()
:canonical: duck.utils.eventlist.EventList.__str__

````

````{py:method} append(item: typing.Any)
:canonical: duck.utils.eventlist.EventList.append

```{autodocx-docstring} duck.utils.eventlist.EventList.append
```

````

````{py:method} clear()
:canonical: duck.utils.eventlist.EventList.clear

```{autodocx-docstring} duck.utils.eventlist.EventList.clear
```

````

````{py:method} extend(other)
:canonical: duck.utils.eventlist.EventList.extend

```{autodocx-docstring} duck.utils.eventlist.EventList.extend
```

````

````{py:method} insert(index: int, item: typing.Any)
:canonical: duck.utils.eventlist.EventList.insert

```{autodocx-docstring} duck.utils.eventlist.EventList.insert
```

````

````{py:method} on_delete_item(item: typing.Any)
:canonical: duck.utils.eventlist.EventList.on_delete_item

```{autodocx-docstring} duck.utils.eventlist.EventList.on_delete_item
```

````

````{py:method} on_new_item(item: typing.Any)
:canonical: duck.utils.eventlist.EventList.on_new_item

```{autodocx-docstring} duck.utils.eventlist.EventList.on_new_item
```

````

````{py:method} pop(index: int = -1)
:canonical: duck.utils.eventlist.EventList.pop

```{autodocx-docstring} duck.utils.eventlist.EventList.pop
```

````

````{py:method} remove(item: typing.Any)
:canonical: duck.utils.eventlist.EventList.remove

```{autodocx-docstring} duck.utils.eventlist.EventList.remove
```

````

`````
