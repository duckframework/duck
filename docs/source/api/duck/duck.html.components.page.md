# {py:mod}`duck.html.components.page`

```{py:module} duck.html.components.page
```

```{autodocx-docstring} duck.html.components.page
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`ErrorPage <duck.html.components.page.ErrorPage>`
  - ```{autodocx-docstring} duck.html.components.page.ErrorPage
    :summary:
    ```
* - {py:obj}`EventHandlerChain <duck.html.components.page.EventHandlerChain>`
  - ```{autodocx-docstring} duck.html.components.page.EventHandlerChain
    :summary:
    ```
* - {py:obj}`Page <duck.html.components.page.Page>`
  - ```{autodocx-docstring} duck.html.components.page.Page
    :summary:
    ```
````

### API

`````{py:class} ErrorPage(status_code: int, message: str, *args, **kwargs)
:canonical: duck.html.components.page.ErrorPage

Bases: {py:obj}`duck.html.components.page.Page`

```{autodocx-docstring} duck.html.components.page.ErrorPage
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.html.components.page.ErrorPage.__init__
```

````{py:method} on_create()
:canonical: duck.html.components.page.ErrorPage.on_create

````

`````

`````{py:class} EventHandlerChain()
:canonical: duck.html.components.page.EventHandlerChain

```{autodocx-docstring} duck.html.components.page.EventHandlerChain
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.html.components.page.EventHandlerChain.__init__
```

````{py:attribute} __slots__
:canonical: duck.html.components.page.EventHandlerChain.__slots__
:value: >
   ('_event_handlers', '_execution_results')

```{autodocx-docstring} duck.html.components.page.EventHandlerChain.__slots__
```

````

````{py:method} add_event_handler(event_handler: typing.Callable, update_targets: typing.Set[HtmlComponent])
:canonical: duck.html.components.page.EventHandlerChain.add_event_handler

```{autodocx-docstring} duck.html.components.page.EventHandlerChain.add_event_handler
```

````

````{py:method} all_update_targets() -> typing.Set[HtmlComponent]
:canonical: duck.html.components.page.EventHandlerChain.all_update_targets

```{autodocx-docstring} duck.html.components.page.EventHandlerChain.all_update_targets
```

````

````{py:method} async_execute(args: typing.Union[typing.Tuple, typing.Iterable], restart: bool = False) -> typing.Dict[typing.Callable, typing.Any]
:canonical: duck.html.components.page.EventHandlerChain.async_execute
:async:

```{autodocx-docstring} duck.html.components.page.EventHandlerChain.async_execute
```

````

`````

````{py:exception} EventHandlerChainError()
:canonical: duck.html.components.page.EventHandlerChainError

Bases: {py:obj}`duck.html.components.page.PageError`

```{autodocx-docstring} duck.html.components.page.EventHandlerChainError
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.html.components.page.EventHandlerChainError.__init__
```

````

`````{py:class} Page(request, disable_lively: bool = False, lazy: bool = True, *args, **kwargs)
:canonical: duck.html.components.page.Page

Bases: {py:obj}`duck.html.components.InnerComponent`

```{autodocx-docstring} duck.html.components.page.Page
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.html.components.page.Page.__init__
```

````{py:method} add_child(child)
:canonical: duck.html.components.page.Page.add_child

````

````{py:method} add_google_analytics(tracking_id: str) -> typing.List[duck.html.components.script.Script]
:canonical: duck.html.components.page.Page.add_google_analytics

```{autodocx-docstring} duck.html.components.page.Page.add_google_analytics
```

````

````{py:method} add_meta(**kwargs) -> duck.html.components.NoInnerComponent
:canonical: duck.html.components.page.Page.add_meta

```{autodocx-docstring} duck.html.components.page.Page.add_meta
```

````

````{py:method} add_script(src: typing.Optional[str] = None, inline: typing.Optional[str] = None, async_: bool = False, defer: bool = False, **attrs) -> typing.Optional[duck.html.components.script.Script]
:canonical: duck.html.components.page.Page.add_script

```{autodocx-docstring} duck.html.components.page.Page.add_script
```

````

````{py:method} add_stylesheet(href: str, add_to_noscript: bool = False, **attrs) -> typing.Optional[duck.html.components.Component]
:canonical: duck.html.components.page.Page.add_stylesheet

```{autodocx-docstring} duck.html.components.page.Page.add_stylesheet
```

````

````{py:method} add_to_body(child_or_childs: typing.Union[duck.html.components.Component, typing.List[duck.html.components.Component]])
:canonical: duck.html.components.page.Page.add_to_body

```{autodocx-docstring} duck.html.components.page.Page.add_to_body
```

````

````{py:method} add_to_head(child_or_childs: typing.Union[duck.html.components.Component, typing.List[duck.html.components.Component]])
:canonical: duck.html.components.page.Page.add_to_head

```{autodocx-docstring} duck.html.components.page.Page.add_to_head
```

````

````{py:method} document_bind(event: str, event_handler: typing.Callable, force_bind: bool = False, update_targets: typing.List[HtmlComponent] = None, update_self: bool = True, event_handler_chaining: bool = False) -> None
:canonical: duck.html.components.page.Page.document_bind

```{autodocx-docstring} duck.html.components.page.Page.document_bind
```

````

````{py:method} document_unbind(event: str, failsafe: bool = True)
:canonical: duck.html.components.page.Page.document_unbind

```{autodocx-docstring} duck.html.components.page.Page.document_unbind
```

````

````{py:method} get_document_event_info(event: str) -> typing.Tuple[typing.Callable, typing.Set[HtmlComponent]]
:canonical: duck.html.components.page.Page.get_document_event_info

```{autodocx-docstring} duck.html.components.page.Page.get_document_event_info
```

````

````{py:method} get_element() -> str
:canonical: duck.html.components.page.Page.get_element

````

````{py:method} get_request_or_raise() -> HttpRequest
:canonical: duck.html.components.page.Page.get_request_or_raise

```{autodocx-docstring} duck.html.components.page.Page.get_request_or_raise
```

````

````{py:method} on_create()
:canonical: duck.html.components.page.Page.on_create

````

````{py:method} render()
:canonical: duck.html.components.page.Page.render

````

````{py:property} request
:canonical: duck.html.components.page.Page.request
:type: HttpRequest

```{autodocx-docstring} duck.html.components.page.Page.request
```

````

````{py:method} set_accessibility(lang: typing.Optional[str] = None, role: typing.Optional[str] = None)
:canonical: duck.html.components.page.Page.set_accessibility

```{autodocx-docstring} duck.html.components.page.Page.set_accessibility
```

````

````{py:method} set_article_json_ld(headline: str, author_name: str, date_published: str, description: str, url: typing.Optional[str] = None)
:canonical: duck.html.components.page.Page.set_article_json_ld

```{autodocx-docstring} duck.html.components.page.Page.set_article_json_ld
```

````

````{py:method} set_author(author: str)
:canonical: duck.html.components.page.Page.set_author

```{autodocx-docstring} duck.html.components.page.Page.set_author
```

````

````{py:method} set_canonical(url: str)
:canonical: duck.html.components.page.Page.set_canonical

```{autodocx-docstring} duck.html.components.page.Page.set_canonical
```

````

````{py:method} set_description(description: str)
:canonical: duck.html.components.page.Page.set_description

```{autodocx-docstring} duck.html.components.page.Page.set_description
```

````

````{py:method} set_favicon(source: str, icon_type: str = 'image/png', rel: str = 'icon', sizes: typing.Optional[str] = None)
:canonical: duck.html.components.page.Page.set_favicon

```{autodocx-docstring} duck.html.components.page.Page.set_favicon
```

````

````{py:method} set_favicons(icons: typing.List[typing.Dict[str, str]]) -> typing.List[duck.html.components.NoInnerComponent]
:canonical: duck.html.components.page.Page.set_favicons

```{autodocx-docstring} duck.html.components.page.Page.set_favicons
```

````

````{py:method} set_json_ld(data: typing.Dict)
:canonical: duck.html.components.page.Page.set_json_ld

```{autodocx-docstring} duck.html.components.page.Page.set_json_ld
```

````

````{py:method} set_keywords(keywords: typing.List[str])
:canonical: duck.html.components.page.Page.set_keywords

```{autodocx-docstring} duck.html.components.page.Page.set_keywords
```

````

````{py:method} set_lang(lang: str)
:canonical: duck.html.components.page.Page.set_lang

```{autodocx-docstring} duck.html.components.page.Page.set_lang
```

````

````{py:method} set_opengraph(title: typing.Optional[str] = None, description: typing.Optional[str] = None, url: typing.Optional[str] = None, image: typing.Optional[str] = None, type: typing.Optional[str] = None, site_name: typing.Optional[str] = None)
:canonical: duck.html.components.page.Page.set_opengraph

```{autodocx-docstring} duck.html.components.page.Page.set_opengraph
```

````

````{py:method} set_pagination(prev_url: typing.Optional[str] = None, next_url: typing.Optional[str] = None)
:canonical: duck.html.components.page.Page.set_pagination

```{autodocx-docstring} duck.html.components.page.Page.set_pagination
```

````

````{py:method} set_product_json_ld(name: str, description: str, sku: str, brand: str, price: str, currency: str, availability: str, url: typing.Optional[str] = None, image: typing.Optional[str] = None)
:canonical: duck.html.components.page.Page.set_product_json_ld

```{autodocx-docstring} duck.html.components.page.Page.set_product_json_ld
```

````

````{py:method} set_robots(content: str)
:canonical: duck.html.components.page.Page.set_robots

```{autodocx-docstring} duck.html.components.page.Page.set_robots
```

````

````{py:method} set_title(title: str)
:canonical: duck.html.components.page.Page.set_title

```{autodocx-docstring} duck.html.components.page.Page.set_title
```

````

````{py:method} set_twitter_card(card: str = 'summary', title: typing.Optional[str] = None, description: typing.Optional[str] = None, image: typing.Optional[str] = None, site: typing.Optional[str] = None, creator: typing.Optional[str] = None)
:canonical: duck.html.components.page.Page.set_twitter_card

```{autodocx-docstring} duck.html.components.page.Page.set_twitter_card
```

````

`````

````{py:exception} PageError()
:canonical: duck.html.components.page.PageError

Bases: {py:obj}`Exception`

```{autodocx-docstring} duck.html.components.page.PageError
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.html.components.page.PageError.__init__
```

````

````{py:exception} UnrecommendedAddChildWarning()
:canonical: duck.html.components.page.UnrecommendedAddChildWarning

Bases: {py:obj}`Warning`

```{autodocx-docstring} duck.html.components.page.UnrecommendedAddChildWarning
```

```{rubric} Initialization
```

```{autodocx-docstring} duck.html.components.page.UnrecommendedAddChildWarning.__init__
```

````
