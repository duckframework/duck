# {py:mod}`duck.utils.email`

```{py:module} duck.utils.email
```

```{autodocx-docstring} duck.utils.email
:allowtitles:
```

## Submodules

```{toctree}
:titlesonly:
:maxdepth: 1

duck.utils.email.collection
```

## Package Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`Email <duck.utils.email.Email>`
  - ```{autodocx-docstring} duck.utils.email.Email
    :summary:
    ```
* - {py:obj}`Gmail <duck.utils.email.Gmail>`
  - ```{autodocx-docstring} duck.utils.email.Gmail
    :summary:
    ```
````

### API

`````{py:class} Email(smtp_host: str, smtp_port: int, username: str, password: str, from_addr: str, name: str, to: str, subject: str, body: str, recipients: typing.Optional[typing.List[str]] = None, use_bcc: bool = True, use_ssl: bool = True)
:canonical: duck.utils.email.Email

```{autodocx-docstring} duck.utils.email.Email
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.utils.email.Email.__init__
```

````{py:method} __repr__()
:canonical: duck.utils.email.Email.__repr__

````

````{py:method} __str__()
:canonical: duck.utils.email.Email.__str__

````

````{py:method} _build_message() -> typing.Tuple[email.mime.multipart.MIMEMultipart, typing.List[str]]
:canonical: duck.utils.email.Email._build_message

```{autodocx-docstring} duck.utils.email.Email._build_message
```

````

````{py:method} async_send() -> None
:canonical: duck.utils.email.Email.async_send
:async:

```{autodocx-docstring} duck.utils.email.Email.async_send
```

````

````{py:method} send() -> None
:canonical: duck.utils.email.Email.send

```{autodocx-docstring} duck.utils.email.Email.send
```

````

`````

````{py:class} Gmail(username: str, password: str, from_addr: str, name: str, to: str, subject: str, body: str, recipients: typing.Optional[typing.List[str]] = None, use_bcc: bool = True, use_ssl: bool = True)
:canonical: duck.utils.email.Gmail

Bases: {py:obj}`duck.utils.email.Email`

```{autodocx-docstring} duck.utils.email.Gmail
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.utils.email.Gmail.__init__
```

````
