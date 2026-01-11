# {py:mod}`duck.utils.email.collection`

```{py:module} duck.utils.email.collection
```

```{autodocx-docstring} duck.utils.email.collection
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`EmailCollector <duck.utils.email.collection.EmailCollector>`
  - ```{autodocx-docstring} duck.utils.email.collection.EmailCollector
    :summary:
    ```
````

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`async_collect_email <duck.utils.email.collection.async_collect_email>`
  - ```{autodocx-docstring} duck.utils.email.collection.async_collect_email
    :summary:
    ```
* - {py:obj}`collect_email <duck.utils.email.collection.collect_email>`
  - ```{autodocx-docstring} duck.utils.email.collection.collect_email
    :summary:
    ```
````

### API

`````{py:class} EmailCollector
:canonical: duck.utils.email.collection.EmailCollector

```{autodocx-docstring} duck.utils.email.collection.EmailCollector
```

````{py:attribute} _async_callback
:canonical: duck.utils.email.collection.EmailCollector._async_callback
:type: typing.Optional[typing.Callable[[str, typing.Optional[str]], typing.Awaitable[None]]]
:value: >
   None

```{autodocx-docstring} duck.utils.email.collection.EmailCollector._async_callback
```

````

````{py:attribute} _emails
:canonical: duck.utils.email.collection.EmailCollector._emails
:type: typing.List[typing.Tuple[str, typing.Optional[str]]]
:value: >
   []

```{autodocx-docstring} duck.utils.email.collection.EmailCollector._emails
```

````

````{py:attribute} _sync_callback
:canonical: duck.utils.email.collection.EmailCollector._sync_callback
:type: typing.Optional[typing.Callable[[str, typing.Optional[str]], None]]
:value: >
   None

```{autodocx-docstring} duck.utils.email.collection.EmailCollector._sync_callback
```

````

````{py:method} async_collect_email(email: str, category: typing.Optional[str] = None)
:canonical: duck.utils.email.collection.EmailCollector.async_collect_email
:async:
:classmethod:

```{autodocx-docstring} duck.utils.email.collection.EmailCollector.async_collect_email
```

````

````{py:method} collect_email(email: str, category: typing.Optional[str] = None)
:canonical: duck.utils.email.collection.EmailCollector.collect_email
:classmethod:

```{autodocx-docstring} duck.utils.email.collection.EmailCollector.collect_email
```

````

````{py:method} get_collected_emails() -> typing.List[typing.Tuple[str, typing.Optional[str]]]
:canonical: duck.utils.email.collection.EmailCollector.get_collected_emails
:classmethod:

```{autodocx-docstring} duck.utils.email.collection.EmailCollector.get_collected_emails
```

````

````{py:method} register(callback: typing.Union[typing.Callable[[str, typing.Optional[str]], None], typing.Callable[[str, typing.Optional[str]], typing.Awaitable[None]]])
:canonical: duck.utils.email.collection.EmailCollector.register
:classmethod:

```{autodocx-docstring} duck.utils.email.collection.EmailCollector.register
```

````

`````

````{py:function} async_collect_email(email: str, category: typing.Optional[str] = None)
:canonical: duck.utils.email.collection.async_collect_email
:async:

```{autodocx-docstring} duck.utils.email.collection.async_collect_email
```
````

````{py:function} collect_email(email: str, category: typing.Optional[str] = None)
:canonical: duck.utils.email.collection.collect_email

```{autodocx-docstring} duck.utils.email.collection.collect_email
```
````
