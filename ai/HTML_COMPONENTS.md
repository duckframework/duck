# Duck Framework — Complete Component Guide for AI Assistants

> This document is the single source of truth for AI assistants working with
> Duck Framework components. Read every section before writing any Duck code.
> When in doubt about a specific component's API, fetch its docs page at:
> `https://docs.duckframework.com/main/api/duck/duck.html.components.<module>.html`

---

**Note:** This file is formatted in Markdown. All content, including headings, code blocks, and inline formatting, must be parsed and interpreted according to Markdown syntax rules rather than treated as plain text. Read this file twice to avoid making mistakes.

---

## Table of Contents

1. [What Is Duck Framework?](#1-what-is-duck-framework)
2. [The Lively Component System](#2-the-lively-component-system)
3. [Component Base Classes](#3-component-base-classes)
4. [Component Lifecycle](#4-component-lifecycle)
5. [Constructing Components — The Right Way](#5-constructing-components--the-right-way)
6. [Styling and Props](#6-styling-and-props)
7. [Events and Reactivity](#7-events-and-reactivity)
8. [Page Components](#8-page-components)
9. [Container vs Non-Container Components](#9-container-vs-non-container-components)
10. [All Built-in Components](#10-all-built-in-components)
11. [Custom Components](#11-custom-components)
12. [Component Extensions](#12-component-extensions)
13. [Forms](#13-forms)
14. [Force Updates](#14-force-updates)
15. [JavaScript Execution](#15-javascript-execution)
16. [Utility Functions](#16-utility-functions)
17. [Caching](#17-caching)
18. [Navigation](#18-navigation)
19. [Base Page Pattern — Best Practice](#19-base-page-pattern--best-practice)
20. [Code Style Rules](#20-code-style-rules)
21. [Common Mistakes to Avoid](#21-common-mistakes-to-avoid)
22. [How to Look Up Any Component](#22-how-to-look-up-any-component)
23. [Helpful Sources](#23-helpful-sources)

---

## 1. What Is Duck Framework?

Duck is a Python web framework that lets you build fully interactive web UIs
**without writing JavaScript**. It uses WebSockets (msgpack) to sync component
state between the Python server and the browser in real time.

Key facts:
- UI is defined as Python classes (components)
- Events (clicks, inputs, submits) are handled in Python
- The DOM updates automatically — only changed parts re-render
- Fast navigation between pages without full reloads (vdom diffing)
- Templates (Jinja2/Django) are supported but components are preferred

---

## 2. The Lively Component System

The Lively system is Duck's reactive engine. It:
- Tracks component `props` and `style` set during initial render
- Sends minimal DOM patches over WebSocket when state changes
- Handles event routing from browser ➝‬ Python handler ➝‬ DOM patch

**Critical rule:** Lively only knows about props/style that were declared on
the server during the initial render. If you set a style property for the
first time in an event handler, Lively will not sync it. Always initialise
every property you intend to control, even to an empty string:

```python
# Good — Lively will track background-color
btn = Button(text="Click", style={"background-color": ""})

# Bad — Lively cannot sync background-color later
btn = Button(text="Click")
```

---

## 3. Component Base Classes

All components ultimately inherit from `HtmlComponent`. You will mostly use:

| Class | Import | Use when |
|---|---|---|
| `InnerComponent` | `duck.html.components` | Component has children / inner body |
| `NoInnerComponent` | `duck.html.components` | Self-closing element (like `<input>`) |
| `Page` | `duck.html.components.page` | Full HTML page |

```python
from duck.html.components import InnerComponent, NoInnerComponent
from duck.html.components.page import Page
```

### Key properties on every component

| Property | Type | Description |
|---|---|---|
| `style` | `StyleStore` (dict-like) | CSS styles |
| `props` | `PropertyStore` (dict-like) | HTML attributes |
| `id` | str | HTML id (set via `id=` kwarg) |
| `klass` | str | CSS class (use instead of `class`) |
| `parent` | Component or None | Parent in the tree |
| `root` | Component or None | Root of the tree |
| `children` | ChildrenList | Child components (InnerComponent only) |
| `uid` | str | Auto-assigned unique ID |
| `kwargs` | dict | All extra kwargs passed at construction |
| `inner_html` | str | Raw HTML inner content |

---

## 4. Component Lifecycle

These methods are called in order. Always call `super()` first.

### `on_create()`
Called immediately on component instantiation. This is where you build
the component's structure — add children, set styles, read kwargs.

```python
def on_create(self):
    super().on_create()
    # Build structure here
    self.title = Heading(type="h2", text="Hello")
    self.add_child(self.title)
```

### `on_parent(parent)`
Called when this component is added to a parent. Use it when you need
to know about the parent before doing something, e.g. adding a sibling script.

```python
def on_parent(self, parent):
    parent.add_child(Script(inner_html="..."))
```

### `on_root_finalized(root)`
Called once the root component (usually the Page) is permanently set.  

You can use this to bind events if you require a stable root i.e. the Page component.

```python
def on_root_finalized(self, root):
    async def on_ready(page, event, value, ws):
        print("DOM loaded")
    root.document_bind("DOMContentLoaded", on_ready, update_self=False)
```

### Lifecycle order summary

```
Component() ➝‬ on_create() ➝‬ [added to parent] ➝‬ on_parent() ➝‬ on_root_finalized()
```

---

## 5. Constructing Components — The Right Way

**Always pass everything at construction time via kwargs.** Do not set
attributes after construction unless inside a lifecycle method.

### Correct way:

```python
# CORRECT — clean, declarative
card = Card(
    id="featured-card",
    klass="card featured",
    style={"background": "var(--theme-surface)", "padding": "16px"},
    props={"data-type": "featured"},
    children=[
        Heading(type="h3", text="Title"),
        Paragraph(text="Some description here."),
    ]
)
```

### Wrong way:

```python
# WRONG — imperative, scattered
card = Card()
card.id = "featured-card"
card.style["background"] = "var(--theme-surface)"
card.add_child(Heading(type="h3", text="Title"))
```

### Reading kwargs inside components

Use `self.kwargs` to access anything passed at construction:

```python
def on_create(self):
    super().on_create()
    title = self.kwargs.get("title", "Default")           # optional
    user = self.get_kwarg_or_raise("user")                # required — raises if missing
```

---

## 6. Styling and Props

### Style

`self.style` is a dict-like store. Set styles using CSS property names:

```python
comp.style["background-color"] = "red"
comp.style["font-size"] = "1rem"
comp.style["display"] = "flex"
```

Or pass at construction:

```python
FlexContainer(style={"gap": "16px", "flex-direction": "column"})
```

### BasicExtension shortcuts

All components include `BasicExtension`, which provides convenience kwargs:

| Kwarg | Effect |
|---|---|
| `id` | Sets `id` property |
| `klass` | Sets CSS `class` property |
| `bg_color` | Sets `background-color` style |
| `color` | Sets `color` style |
| `inner_html` | Sets the RAW `innerHTML` of container component |
| `text` | Sets ESCAPED `safe innerHTML` of a container component |


```python
Button(text="Click me", bg_color="green", color="white")
```

### StyleCompatibilityExtension

Also included by default. Automatically adds vendor prefixes:
setting `backdrop-filter` also sets `-webkit-backdrop-filter`, etc.

### Props

`self.props` holds HTML attributes. Use for `onclick`, `data-*`, `aria-*`, etc:

```python
btn.props["onclick"] = "myJsFunction()"
btn.props["aria-label"] = "Close modal"
btn.props["data-id"] = "123"
```

### CSS classes

Use `klass` (not `class`) to set CSS classes:

```python
Container(klass="hero-section full-width")
```

---

## 7. Events and Reactivity

### Binding events

```python
component.bind(
    event,           # e.g. "click", "input", "submit", "change"
    handler,         # callable (sync or async)
    update_self=True,         # whether this component re-renders
    update_targets=[other],   # other components to re-render
)
```

### Event handler signature

```python
async def on_click(component, event: str, value, ws):
    """
    Args:
        component: The component that fired the event.
        event: Event name string.
        value: Event value (varies by event type).
        ws: LivelyWebSocketView — use for JS execution.
    """
    component.bg_color = "red"
```

Handlers can be sync or async. Async is preferred for any I/O.

### update_targets

Only pass components that actually change. Unnecessary targets waste bandwidth:

```python
# Good — only re-renders what changed
btn.bind("click", handler, update_self=False, update_targets=[counter_label])

# Bad — re-renders everything unnecessarily
btn.bind("click", handler, update_targets=[comp1, comp2, comp3, comp4])
```

### Document events

Bind to document-level events only on `Page` instances:

```python
page.document_bind("DOMContentLoaded", on_load, update_self=False)
page.document_bind("DuckNavigated", on_navigate, update_self=False)
```

### Unbinding

```python
component.unbind("click")              # failsafe by default
component.unbind("click", failsafe=False)  # raises if not bound
```

---

## 8. Page Components

`Page` is the root component for full HTML pages. Always subclass it.

### Initialisation

```python
from duck.html.components.page import Page

class HomePage(Page):
    def on_create(self):
        super().on_create()
        # Page setup goes here
```

In views:

```python
def home(request):
    return HomePage(request=request)
```

### Page API — all available methods

#### Content

```python
page.add_to_body(component)          # add to <body>
page.add_to_head(component)          # add to <head>
# Note: never use page.add_child() — use add_to_body/add_to_head
```

`add_to_body` accepts a single component or a list:

```python
page.add_to_body([Nav(), Hero(), Footer()])
```

#### Metadata and SEO

```python
page.set_title("Page Title")
page.set_description("Meta description text.")
page.set_author("Author Name")
page.set_keywords(["duck", "python", "web"])
page.set_canonical("https://example.com/page")
page.set_robots("index, follow")
page.set_lang("en")
```

#### Social / Open Graph

```python
page.set_opengraph(
    title="Title",
    description="Description",
    url="https://example.com",
    image="https://example.com/og.png",
    type="website",
    site_name="My Site",
)
page.set_twitter_card(
    card="summary_large_image",
    title="Title",
    description="Description",
    image="https://example.com/og.png",
    site="@handle",
)
```

#### Favicons

```python
page.set_favicon("/static/favicon.ico", icon_type="image/x-icon")
page.set_favicons([
    {"href": "/static/icon-32.png", "sizes": "32x32", "type": "image/png"},
    {"href": "/static/icon-apple.png", "rel": "apple-touch-icon"},
])
```

#### Scripts and Stylesheets

```python
page.add_stylesheet("/static/css/main.css")
page.add_script(src="/static/js/app.js", defer=True)
page.add_script(inline="console.log('hello')")
```

#### Structured Data

```python
page.set_json_ld({
    "@context": "https://schema.org",
    "@type": "WebSite",
    "url": "https://example.com",
    "name": "My Site",
})
page.set_article_json_ld(
    headline="Article Title",
    author_name="Author",
    date_published="2026-01-01",
    description="Article description",
    url="https://example.com/article",
)
```

#### Accessibility

```python
page.set_accessibility(lang="en", role="main")
```

#### Analytics

```python
page.add_google_analytics("UA-XXXXX-Y")
```

#### Meta tags (custom)

```python
page.add_meta(name="theme-color", content="#F5C842")
```

#### Page reload control

```python
page.fullpage_reload = True   # force full page reload on navigation
```

---

## 9. Container vs Non-Container Components

This distinction is critical. Getting it wrong raises errors.

### Container components (accept `children=`)

These extend `InnerHtmlComponent` / `InnerComponent`. They can hold children.

- `Container`, `FlexContainer`, `GridContainer`, `FixedContainer`
- `Section`, `Card`, `Modal`, `Form`, `Hero`
- `Page` (uses `add_to_body`/`add_to_head` instead of `children=`)
- Any custom `InnerComponent` subclass

```python
FlexContainer(
    style={"gap": "12px"},
    children=[
        Button(text="One"),
        Button(text="Two"),
    ]
)
```

Content is set via specific kwargs like `text=`, `src=`, `inner_html=`:

```python
Heading(type="h1", text="Welcome")
Paragraph(text="Some body text.")
Script(inner_html="console.log('loaded')")
```

### Non-container components (no `children=`)

These extend `NoInnerHtmlComponent` / `NoInnerComponent`. Self-closing or
content-only elements.

- `Input`, `FileInput`
- `etc` - elements with no closing tags.

```python
Image(source="/static/img.png", alt="Description")
```

### Adding children imperatively (when needed inside on_create)

```python
def on_create(self):
    super().on_create()
    self.add_child(Button(text="One"))
    self.add_children([Button(text="Two"), Button(text="Three")])

    # Remove children
    self.remove_child(some_child)
    self.clear_children()
```

---

## 10. All Built-in Components

Always fetch the specific module docs before using a component to get the
exact kwargs. Pattern:
`https://docs.duckframework.com/main/api/duck/duck.html.components.<module>.html`

| Component | Module | Type | Notes |
|---|---|---|---|
| `Button` | `button` | Non-container | `text=`, `bg_color=`, `color=` |
| `FlatButton` | `button` | Non-container | Flat variant |
| `RaisedButton` | `button` | Non-container | Elevated variant |
| `Card` | `card` | Container | |
| `Checkbox` | `checkbox` | Non-container | `name=`, `checked=`, `disabled=` |
| `Code` | `code` | Non-container | Code block display |
| `Container` | `container` | Container | Basic `<div>` |
| `FlexContainer` | `container` | Container | `display:flex` div |
| `GridContainer` | `container` | Container | `display:grid` div |
| `FixedContainer` | `container` | Container | `position:fixed` div |
| `FileInput` | `fileinput` | Non-container | File upload input |
| `Footer` | `footer` | Container | Page footer |
| `Form` | `form` | Container | Bind `submit` event |
| `Heading` | `heading` | Non-container | `type="h1"..."h6"`, `text=` |
| `Hero` | `hero` | Container | Hero section |
| `Icon` | `icon` | Non-container | Icon component |
| `Image` | `image` | Non-container | `source=`, `alt=` |
| `Input` | `input` | Non-container | `type=`, `name=`, `placeholder=` |
| `InputWithLabel` | `input` | Container | Wraps Input with a Label |
| `Label` | `label` | Non-container | `text=` |
| `Link` | `link` | Non-container | `url=`, `text=` |
| `Modal` | `modal` | Container | `title=`, `show_close=`, `open_on_ready=`, `modal_style=` |
| `Navbar` | `navbar` | Container | Requires jQuery — avoid extending, build custom instead |
| `Page` | `page` | Special | Root page component |
| `Paragraph` | `paragraph` | Non-container | `text=` |
| `ProgressBar` | `progressbar` | Non-container | |
| `Script` | `script` | Non-container | `inner_html=` or `src=` |
| `Section` | `section` | Container | Semantic `<section>` |
| `Select` | `select` | Non-container | Dropdown |
| `Snackbar` | `snackbar` | Container | Toast notification |
| `Style` | `style` | Non-container | Inline `<style>` block |
| `TableOfContents` | `table_of_contents` | Container | Auto TOC |
| `TextArea` | `textarea` | Non-container | `name=`, `placeholder=` |
| `Video` | `video` | Non-container | Video embed |

### Navbar note

The built-in `Navbar` depends on jQuery. **Do not extend it.** Build custom
navbars from `FlexContainer` + `Link` components instead.

### Modal kwargs

```python
Modal(
    title="Dialog Title",         # optional header title
    show_close=True,              # show × button (default True)
    open_on_ready=True,           # auto-open on page load
    modal_style={"max-width": "500px", "background": "#111"},
    modal_props={},               # extra props on modal content box
)
```

Access modal internals after `super().on_create()`:

```python
self.modal_content_container  # outer positioning wrapper
self.modal_content            # the visible card
self.modal_header             # title + close button row
```

Use Duck's built-in JS functions for toggling:

```python
btn.props["onclick"] = f"openModal(document.getElementById('{modal.id}'))"
btn.props["onclick"] = f"closeModal(document.getElementById('{modal.id}'))"
```

---

## 11. Custom Components

### InnerComponent (has children)

```python
from duck.html.components import InnerComponent
from duck.html.components.heading import Heading
from duck.html.components.paragraph import Paragraph

class InfoCard(InnerComponent):
    """
    A simple info card with a title and body text.
    """

    def get_element(self):
        return "div"

    def on_create(self):
        super().on_create()

        title = self.get_kwarg_or_raise("title")
        body = self.kwargs.get("body", "")

        self.style.update({"padding": "16px", "border-radius": "8px"})

        self.add_children([
            Heading(type="h3", text=title),
            Paragraph(text=body),
        ])
```

### NoInnerComponent (no children)

```python
from duck.html.components import NoInnerComponent

class Divider(NoInnerComponent):
    """
    A horizontal rule divider.
    """

    def get_element(self):
        return "hr"

    def on_create(self):
        super().on_create()
        self.style["border"] = "none"
        self.style["border-top"] = "1px solid var(--theme-border)"
        self.style["margin"] = "24px 0"
```

### Extending built-in components

Only extend a built-in if it does not pull in external dependencies.
Always call `super().on_create()` first:

```python
from duck.html.components.modal import Modal

class ConfirmModal(Modal):
    """
    A confirmation modal with accept/cancel buttons.
    """

    def on_create(self):
        self.kwargs["title"] = "Are you sure?"
        self.kwargs["open_on_ready"] = False
        super().on_create()

        # Add content after super() sets up modal internals
        self.add_child(Button(text="Confirm", bg_color="red"))
```

---

## 12. Component Extensions

Extensions are mixins that add behaviour to components. They come before
the base class in the MRO:

```python
from duck.html.components.extensions import Extension

class BorderExtension(Extension):
    """
    Adds a themed border to any component.
    """

    def apply_extension(self):
        super().apply_extension()
        self.style["border"] = "1px solid var(--theme-border)"

class BorderedCard(BorderExtension, Card):
    pass
```

All components already include:
- `BasicExtension` — `bg_color`, `color`, `id`, `klass`, etc.
- `StyleCompatibilityExtension` — vendor prefix handling

---

## 13. Forms

Use `Form` component with `Input` fields. Bind the `submit` event to handle
form data. All inputs need a `name=` prop.

```python
from duck.html.components.form import Form
from duck.html.components.input import Input
from duck.html.components.button import Button

def on_submit(form, event, value: dict, ws):
    """
    Args:
        value: Dict of {name: value} from all named inputs.
    """
    name = value.get("name")
    email = value.get("email")

form = Form(
    children=[
        Input(type="text", name="name", placeholder="Your name"),
        Input(type="email", name="email", placeholder="Email"),
        Input(type="submit", value="Send"),
    ]
)
form.bind("submit", on_submit)
```

Notes:
- `submit` event auto-calls `preventDefault()` — no page reload
- File inputs only return metadata (name, size, type) — not file contents
- For file uploads, use AJAX from JS side and update UI after response

---

## 14. Force Updates

When JavaScript modifies a component's DOM directly, Lively loses track.
Use `ForceUpdate` to reset specific properties back to their server state:

```python
from duck.html.components import ForceUpdate

def on_click(btn, event, value, ws):
    # Reset btn text to its server-declared value
    return ForceUpdate(btn, ["text"])
    # Options: "text", "inner_html", "props", "style", "all"
```

**Rule:** Only properties that were declared on initial render can be
force-updated. If a property was never set server-side, Lively ignores it.

---

## 15. JavaScript Execution

Execute JS on the client from an async event handler:

```python
from duck.html.core.exceptions import JSExecutionError, JSExecutionTimedOut

async def on_click(btn, event, value, ws):
    # Fire and forget
    await ws.execute_js("document.title = 'Updated'")

    # Wait for result
    try:
        result = await ws.get_js_result("return window.scrollY", timeout=2)
    except (JSExecutionTimedOut, JSExecutionError):
        pass
```

JS executes before Lively sends DOM patches. Plan timing accordingly.

---

## 16. Utility Functions

### `to_component` / `quote`

Wrap raw HTML strings as components:

```python
from duck.html.components import to_component

raw = to_component("<strong>Bold text</strong>", tag="span") # You can provide an arguments applicable to InnerComponent
raw_no_close = to_component("<br>", tag="br", no_closing_tag=True)
```

### `duckNavigate` (JS)

Client-side fast navigation — triggers vdom diff instead of full reload:

```html
<a href="/about" onclick="duckNavigate('/about'); return false;">About</a>
```

All `<a>` tags use fast navigation by default. Opt out with `data-no-duck`:

```python
Link(url="/external", text="External", props={"data-no-duck": "true"})
```

> You can even use JS `window.open()`, it's patched to use `duckNavigate()` by default.

---

## 17. Caching

### `@cached_component`

Cache a component's output keyed by a function that inspects the request:

```python
from duck.html.components.utils.caching import cached_component

def is_logged_in(request):
    return request.user.is_authenticated

@cached_component(cache_key_func=is_logged_in)
class HeroSection(FlexContainer):
    def on_create(self):
        super().on_create()
        # ...
```

### Pre-rendering (custom)

Warm the cache before responding:

```python
from duck.shortcuts import to_response

def home(request):
    page = HomePage(request=request)
    background_thread.submit_task(
        lambda: page.pre_render(deep_traversal=True, reverse_traversal=True)
    )
    return to_response(page)
```
> Pre-rendering is not implemented by default, you can implement it own your own. For now, don't use it unless required.

---

## 18. Navigation

- All `<a>` tags automatically use fast navigation (partial DOM update)
- Fast navigation only works if both pages return component responses
- `DuckNavigated` fires after each fast navigation
- `DOMContentLoaded` fires on every page load including fast navigations
- Use `fullpage_reload = True` on a page to force a full browser reload

---

## 19. Base Page Pattern — Best Practice

Always create a base page class. Every page in your project extends it.
This is the single most impactful structural decision you can make.

```python
# web/ui/pages/base.py
from duck.shortcuts import static, resolve
from duck.utils.urlcrack import URL
from duck.html.components.page import Page

from web.ui.components.theme import ThemedPageMixin
from web.ui.components.nav import SiteNav
from web.ui.components.footer import SiteFooter
from web.ui.components.cookie_consent import CookieConsentBanner, has_cookie_consent
from web.ui.components.onboarding import VisitorOnboardingModal, has_seen_onboarding

SITE_NAME = "My Site"


class BasePage(ThemedPageMixin, Page):
    """
    Base page for all site pages.

    Handles theme injection, nav, footer, SEO defaults, cookie consent,
    and visitor onboarding. Subclasses only override what they need.
    """
    OG_IMAGE = static("images/opengraph/og-image.png")
    
    # Override in subclasses for page-specific SEO
    page_title = SITE_NAME
    page_description = "Default site description."
    page_url = None
     
    def on_create(self):
        super().on_create()
        
        # Resolve the page url from home url
        self.home_url = resolve("home", absolute=True)
        self.page_url = URL(self.home_url).join(self.request.path).to_str()
        
        # Theme — injects CSS vars, fonts, toggle script
        self.set_theme(DuckThemePack)

        # SEO defaults — subclasses override page_title etc.
        self.set_title(self.page_title)
        self.set_description(self.page_description)
        self.set_canonical(self.page_url)
        self.set_opengraph(
            title=self.page_title,
            description=self.page_description,
            url=self.page_url,
            image=self.OG_IMAGE,
            type="website",
            site_name=SITE_NAME,
        )
        self.set_twitter_card(
            card="summary_large_image",
            title=self.page_title,
        )
        self.set_favicon("/static/favicon.ico")
        self.set_accessibility(lang="en")

        # Shared layout
        self.add_to_body(SiteNav())
        self.build_page()              # subclass fills body here
        self.add_to_body(SiteFooter())

        # Cookie consent banner — shown if analytics consent not given
        if not has_cookie_consent(self.request, category="analytics"):
            self.add_to_body(CookieConsentBanner())

        # Visitor onboarding — homepage only, tracked via cookie
        if self.should_show_onboarding():
            self.add_to_body(VisitorOnboardingModal())

    def build_page(self):
        """
        Override in subclasses to add page-specific body content.
        """
        pass

    def should_show_onboarding(self) -> bool:
        """
        Returns True if onboarding modal should be shown.
        Override in non-homepage pages to return False.
        """
        return False
```

### Subclass pattern

```python
# web/ui/pages/home.py
from web.ui.pages.base import BasePage
from web.ui.components.hero import HeroSection
from web.ui.components.features import FeaturesGrid

class HomePage(BasePage):
    """
    Homepage — public landing page.
    """
    page_title = "Duck Framework — Build Web Apps in Pure Python"
    page_description = "Duck is a Python web framework with no JavaScript required."
    page_url = "https://duckframework.com"

    def build_page(self):
        self.add_to_body(HeroSection())
        self.add_to_body(FeaturesGrid())

    def should_show_onboarding(self):
        from web.ui.components.onboarding import has_seen_onboarding
        return not has_seen_onboarding(self.request)
```

```python
# views.py
def home(request):
    return HomePage(request=request)

def about(request):
    return AboutPage(request=request)
```

---

## 20. Theming Patterns — Best Practice

Instead of hardcording colors, the best approach is to use a central system for storing 
theme data. This can be done by creating a `web/ui/components/theme.py` which stores a class named `Theme`, then 
theming can be done through using `Theme's` class attributes e.g., `Theme.accent_color`.

### Example of theme.py

```python
# web/ui/components/theme.py

class Theme:
    accent_color = "rgba(0, 35, 6, 1)"
    border_radius = "12px"
    font_size = "1rem"
    # Other theming options here
```

> For a Duck project, a centralized system is recommended not only for theming but also for metadata and this 
> type of data can be stored in `web/meta.py` (optional).

---

## 21. Code Style Rules

These are project-specific conventions for Duck Framework codebase.
Follow them on all code written for this project.  

> Accompanying components and Pages must be stored in different directories for max flexibility. Pages must be stored in `web/ui/pages` whilst components must be stored in `web/ui/components`.

### Naming
- No leading underscores on methods or globals (`build_nav` not `_build_nav`)
- No leading underscores on module-level variables (`SITE_URL` not `_SITE_URL`)

### Docstrings
- Google-style docstrings
- Multiline triple-quotes on their own lines:

```python
def build_card(self, title: str) -> Card:
    """
    Build a themed card component.

    Args:
        title: Card heading text.

    Returns:
        A configured Card component.
    """
```

- Never inline: `"""Some docstring"""`

### Comments
- Short `# Some step` comment above every logical block
- Comments serve as breathing room and visual rhythm
- No wall-of-code without comments
- No separator comments like `# ----- section -----`

### Construction
- Always pass everything at construction time via kwargs
- Use `children=` for container components instead of `add_child` later
- Exception: inside lifecycle methods like `on_create`, `add_child` is fine

---

## 22. Common Mistakes to Avoid

### Setting styles/props after construction (outside lifecycle)

```python
# Wrong
btn = Button(text="Click")
btn.style["color"] = "red"    # set this at construction instead

# Right
btn = Button(text="Click", color="red")
```

### Using add_child on Page

```python
# Wrong — raises UnrecommendedAddChildWarning
page.add_child(SomeComponent())

# Right
page.add_to_body(SomeComponent())
```

### Binding events before root is finalized

Events that require a stable root must be binded inside `on_root_finalized`, not `on_create`:

```python
# Wrong — root may not be set yet
def on_create(self):
    super().on_create()
    self.bind("click", self.on_click, update_targets=[self.root.some_component])   # risky

# Right
def on_root_finalized(self, root):
    self.bind("click", self.on_click, update_targets=[root.some_component])
```

### Forgetting `name=` on form inputs

Without `name=`, the field won't appear in `value` dict on submit:

```python
Input(type="text", placeholder="Name")           # won't be in form data
Input(type="text", name="name", placeholder="Name")  # correct
```

### Extending Navbar

The built-in Navbar requires jQuery. Always build custom navs instead:

```python
# Wrong — pulls in jQuery
from duck.html.components.navbar import Navbar
class MyNav(Navbar): ...

# Right — pure Duck
class SiteNav(FlexContainer):
    def on_create(self):
        super().on_create()
        self.style.update({"justify-content": "space-between", ...})
        self.add_children([Logo(), NavLinks(), CTAButton()])
```

### Not initialising properties you intend to control with Lively

```python
# Wrong — Lively won't sync display later
btn = Button(text="Toggle")

async def on_click(btn, *_):
    btn.style["display"] = "none"   # Lively doesn't know about this

# Right — initialise it so Lively tracks it
btn = Button(text="Toggle", style={"display": "block"})
```

---

## 23. How to Look Up Any Component

Before writing code that uses a Duck component you're unsure about:

1. Fetch the components index:
   `https://docs.duckframework.com/main/api/duck/duck.html.components.html`
   ➝‬ Check the **Submodules** section for all available modules.

2. Fetch the specific module page:
   `https://docs.duckframework.com/main/api/duck/duck.html.components.<module>.html`
   ➝‬ e.g. `duck.html.components.button` for Button

3. Check the **Lively overview** for system-level behaviour:
   `https://docs.duckframework.com/main/lively-components`

4. When fetching real-time docs, use the exact API endpoint format above.
   Do not guess kwargs from memory — always verify.

---

## 24. Helpful Sources

The following sources may help in digging more info on components:
- **https://github.com/duckframework/duck?tab=readme-ov-file#webui**
- **https://docs.duckframework.com/main/lively-components**
- **https://docs.duckframework.com/main/api/duck/duck.html.components**

---

*Last updated from live Duck Framework docs — April 2026.*
*Source: https://docs.duckframework.com/main/lively-components*
*Source: https://docs.duckframework.com/main/api/duck/duck.html.components.html*
*Source: https://docs.duckframework.com/main/api/duck/duck.html.components.page.html*
