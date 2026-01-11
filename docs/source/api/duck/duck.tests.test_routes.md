# {py:mod}`duck.tests.test_routes`

```{py:module} duck.tests.test_routes
```

```{autodocx-docstring} duck.tests.test_routes
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`TestBaseRoutes <duck.tests.test_routes.TestBaseRoutes>`
  - ```{autodocx-docstring} duck.tests.test_routes.TestBaseRoutes
    :summary:
    ```
* - {py:obj}`TestMiddlewareResponses <duck.tests.test_routes.TestMiddlewareResponses>`
  - ```{autodocx-docstring} duck.tests.test_routes.TestMiddlewareResponses
    :summary:
    ```
````

### API

`````{py:class} TestBaseRoutes(methodName='runTest')
:canonical: duck.tests.test_routes.TestBaseRoutes

Bases: {py:obj}`duck.tests.test_server.TestBaseServer`

```{autodocx-docstring} duck.tests.test_routes.TestBaseRoutes
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.tests.test_routes.TestBaseRoutes.__init__
```

````{py:method} test_about_url()
:canonical: duck.tests.test_routes.TestBaseRoutes.test_about_url

```{autodocx-docstring} duck.tests.test_routes.TestBaseRoutes.test_about_url
```

````

````{py:method} test_contact_url()
:canonical: duck.tests.test_routes.TestBaseRoutes.test_contact_url

```{autodocx-docstring} duck.tests.test_routes.TestBaseRoutes.test_contact_url
```

````

````{py:method} test_root_url()
:canonical: duck.tests.test_routes.TestBaseRoutes.test_root_url

```{autodocx-docstring} duck.tests.test_routes.TestBaseRoutes.test_root_url
```

````

`````

`````{py:class} TestMiddlewareResponses(methodName='runTest')
:canonical: duck.tests.test_routes.TestMiddlewareResponses

Bases: {py:obj}`duck.tests.test_routes.TestBaseRoutes`

```{autodocx-docstring} duck.tests.test_routes.TestMiddlewareResponses
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.tests.test_routes.TestMiddlewareResponses.__init__
```

````{py:method} test_csrf_protection()
:canonical: duck.tests.test_routes.TestMiddlewareResponses.test_csrf_protection

```{autodocx-docstring} duck.tests.test_routes.TestMiddlewareResponses.test_csrf_protection
```

````

````{py:method} test_not_found()
:canonical: duck.tests.test_routes.TestMiddlewareResponses.test_not_found

```{autodocx-docstring} duck.tests.test_routes.TestMiddlewareResponses.test_not_found
```

````

````{py:method} test_url_attacks()
:canonical: duck.tests.test_routes.TestMiddlewareResponses.test_url_attacks

```{autodocx-docstring} duck.tests.test_routes.TestMiddlewareResponses.test_url_attacks
```

````

`````
