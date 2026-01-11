# {py:mod}`duck.tests.test_server`

```{py:module} duck.tests.test_server
```

```{autodocx-docstring} duck.tests.test_server
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`TestBaseServer <duck.tests.test_server.TestBaseServer>`
  - ```{autodocx-docstring} duck.tests.test_server.TestBaseServer
    :summary:
    ```
````

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`set_settings <duck.tests.test_server.set_settings>`
  - ```{autodocx-docstring} duck.tests.test_server.set_settings
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`VERBOSE_TESTS <duck.tests.test_server.VERBOSE_TESTS>`
  - ```{autodocx-docstring} duck.tests.test_server.VERBOSE_TESTS
    :summary:
    ```
````

### API

`````{py:class} TestBaseServer(methodName='runTest')
:canonical: duck.tests.test_server.TestBaseServer

Bases: {py:obj}`unittest.TestCase`

```{autodocx-docstring} duck.tests.test_server.TestBaseServer
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.tests.test_server.TestBaseServer.__init__
```

````{py:attribute} _app
:canonical: duck.tests.test_server.TestBaseServer._app
:value: >
   None

```{autodocx-docstring} duck.tests.test_server.TestBaseServer._app
```

````

````{py:property} app
:canonical: duck.tests.test_server.TestBaseServer.app

```{autodocx-docstring} duck.tests.test_server.TestBaseServer.app
```

````

````{py:property} base_url
:canonical: duck.tests.test_server.TestBaseServer.base_url
:type: str

```{autodocx-docstring} duck.tests.test_server.TestBaseServer.base_url
```

````

````{py:method} setUp()
:canonical: duck.tests.test_server.TestBaseServer.setUp

````

````{py:attribute} settings
:canonical: duck.tests.test_server.TestBaseServer.settings
:type: typing.Dict[str, typing.Any]
:value: >
   None

```{autodocx-docstring} duck.tests.test_server.TestBaseServer.settings
```

````

`````

````{py:data} VERBOSE_TESTS
:canonical: duck.tests.test_server.VERBOSE_TESTS
:value: >
   'getenv(...)'

```{autodocx-docstring} duck.tests.test_server.VERBOSE_TESTS
```

````

````{py:function} set_settings(settings: typing.Dict[str, typing.Any])
:canonical: duck.tests.test_server.set_settings

```{autodocx-docstring} duck.tests.test_server.set_settings
```
````
