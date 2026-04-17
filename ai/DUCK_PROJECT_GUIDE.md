# Duck Framework — Project Guide

A comprehensive reference for writing clean, maintainable, performant, and scalable
Duck Framework projects. Follow every rule in this guide — always, in every file.

> **Docs:** https://docs.duckframework.com/main/
> **Components:** Refer to [`HTML_COMPONENTS_GUIDE.md`](./ai/HTML_COMPONENTS_GUIDE_GUIDE.md) for the full component API reference.
> **GitHub:** https://github.com/duckframework/duck

---

## Table of Contents

1. [Project Structure](#project-structure)
2. [Code Style](#code-style)
3. [Docstrings](#docstrings)
4. [Comments](#comments)
5. [Imports](#imports)
6. [Centralized Systems — No Repetition](#centralized-systems--no-repetition)
7. [Pages](#pages)
8. [Components](#components)
9. [Async & Performance](#async--performance)
10. [Views](#views)
11. [Routing & Blueprints](#routing--blueprints)
12. [Django Integration](#django-integration)
13. [Middleware](#middleware)
14. [Caching — Views & Components](#caching--views--components)
15. [Task Automation](#task-automation)
16. [Background Managers](#background-managers)
17. [Theming & Styling](#theming--styling)
18. [SEO](#seo)
19. [Shortcuts Reference](#shortcuts-reference)
20. [Security & Settings](#security--settings)
21. [Deployment](#deployment)
22. [General Best Practices](#general-best-practices)

---

## Project Structure

Standard layout after `duck makeproject myproject`:

```
myproject/
├── web/
│   ├── main.py               # Auto-generated — never edit
│   ├── urls.py               # Route definitions
│   ├── views.py              # View functions or class-based views
│   ├── settings.py           # Auto-generated — never edit
│   ├── ui/
│   │   ├── pages/            # Duck page classes (one per route)
│   │   │   ├── __init__.py
│   │   │   ├── base.py       # BasePage — all pages inherit this
│   │   │   └── home.py
│   │   └── components/       # Reusable Duck components
│   │       ├── __init__.py
│   │       ├── theme.py      # Centralized theme tokens
│   │       ├── nav.py
│   │       └── footer.py
│   ├── static/
│   │   ├── images/
│   │   ├── css/
│   │   └── js/
│   └── templates/            # Jinja2 / Django templates (if used)
├── automations.py            # Duck automation tasks
├── meta.py                   # Centralized site metadata
└── web/backend/django/       # Django sub-project (if integrated)
    └── duckapp/
```

> **Never touch** `main.py` or `settings.py` — they are auto-generated and will be
> overwritten. App-level config belongs in your own modules.

### Points to Note

- Use `duck makeproject myproject --mini` for creating mini project for beginners or simple projects. Always refer to the README for the
- Always refer to README for the repo to get a clear picture on project structure.
- This is in markdown format and all headings, sections or codeblock must be parsed as markdown and not to be treated as plain text.

### Strict Rule:

- Always check for and reuse existing components before creating new ones — never duplicate functionality. Composite components must include unique IDs and minimal comments separating logical sections.
- Never introduce invisible or non-standard characters into any file.
- Never hardcode metadata such as brand name, year, email, or location, etc. Always source these from a central config — this is critical.
- Always use consistent, predictable patterns across the entire codebase.
- Never create unnecessary files, create only relavant files not creating files which are not referrenced or used anywhere in the project.
- Never use uncertain or inconsistent values in any file — for example: 
```python
  # BAD:
  # Confusing on which to use or configure.
  class Theme:
      accent = "red" 
      accent_color = "red"
  
  # GOOD:
  # Clear on which one is in use and changing it here is safe
  class Theme:
      accent_color = "red"
  
  ```
  
  Another inconsistent pattern:
  ```python
  # BAD:
  # Confusing on which to use or configure.
  class Theme:
      accent = "red" 
  
  THEME = {
      "accent": "blue",
  }
  
  # GOOD:
  # Clean and clear on which to use or configure.
  class Theme:
      accent = "red" 
  
  ```
---

## Code Style

Write clean, intentional Python. Code should read as clearly as it runs.

### Naming

- `snake_case` for functions, variables, and module names.
- `PascalCase` for classes.
- No leading underscores on methods or globals unless Python forces it (`__init__` etc.).
  Use `build_nav` not `_build_nav`. Use `SITE_URL` not `_SITE_URL`.
- Constants belong on the class itself unless they are truly project-wide globals.
- Async methods or functions must start with `async_` e.g. `def async_get_products():s`
- Use `PascalCase` for components e.g. `MyComponent`

```python
# Good
class ProductCard(InnerComponent):
    CARD_RADIUS = "10px"

    def build_price_tag(self):
        ...

# Avoid
CARD_RADIUS = "10px"

class ProductCard(InnerComponent):
    def _build_price_tag(self):
        ...
```

### Formatting

- Max line length: **88 characters** (Black-compatible).
- One blank line between logical blocks inside a function.
- Two blank lines between top-level definitions.
- Use f-strings over `.format()` or `%`.
- Type-hint all public function signatures.
- Avoid adding unecessary spacing  around variables, characters or at the end of line e.g.:
  
  ```python
  # GOOD:
  class Theme:
      """
      All design tokens in one place
      """  
      # Background palette
      primary = "#000000" # main dark background
      surface = "#111" # slightly lighter dark surface
  
  # BAD:
  class Theme:
      """
      All design tokens in one place
      """  
      # Background palette
      primary       = "#000000"               # main dark background
      surface       = "#111"                  # slightly lighter dark surface
  
  ```
---

## Docstrings

**Every module, class, and non-trivial function must have a docstring.**
No exceptions. Docstrings are the documentation layer for this codebase.

### Format Rules

- **Google-style** docstrings exclusively.
- Triple quotes always go on their own lines — never inline.
- Keep them purposeful: explain *what* and *why*, not what the code literally does.

```python
"""
Defines the homepage page class and its primary content sections.
"""


def get_greeting(username: str, fallback: str = "Guest") -> str:
    """
    Returns a personalised greeting for the given username.

    Args:
        username: The display name of the user.
        fallback: Value used when username is empty or None.

    Returns:
        A greeting string, e.g. "Hello, Brian!".
    """
    name = username or fallback
    return f"Hello, {name}!"
```

```python
class StatCard(Card):
    """
    Displays a single numeric metric with a descriptive label.

    Props:
        value (str): The metric to display prominently.
        label (str): A short description of the metric.
        color (str): Optional accent color for the value text.
    """

    def on_create(self):
        """
        Builds the stat card with a large value heading and label below.
        """
        super().on_create()
        ...
```

### What needs a docstring

| Target | Required |
|---|---|
| Every module (`.py` file) | Yes |
| Every class | Yes |
| Public methods and functions | Yes |
| Simple one-liner helpers | Optional but encouraged |
| `__init__` with meaningful params | Yes |

---

## Comments

**Comments are mandatory.** They create breathing room, explain intent, and separate
logical concerns inside code — like invisible section headings.

### Rules

- Every logical block gets a short `# Action phrase` above it.
- Comments explain *what* is happening and *why*, not what the syntax says.
- **Separator-style comments are banned.** No `# ---- section ----` or `# === block ===`.
- Write in natural English. Keep them concise.

```python
# Bad — separator noise
# ---- Fetch user ----
user = get_user(request)

# ---- Build response ----
return JsonResponse({"user": user.username})
```

```python
# Good — clean, purposeful
# Fetch the authenticated user from the session
user = get_user(request)

# Return the serialized user as JSON
return JsonResponse({"user": user.username})
```

```python
def on_create(self):
    """
    Builds the card layout with image, heading, description, and CTA button.
    """
    super().on_create()

    # Apply card container base styles
    self.style.update({"border-radius": "12px", "padding": "1rem"})

    # Add product image at the top
    image = Image(source=self.kwargs.get("image"), alt="Product")
    self.add_child(image)

    # Add title and description text
    heading = Heading(type="h3", text=self.kwargs.get("title", "Untitled"))
    description = Paragraph(text=self.kwargs.get("description", ""))
    self.add_children([heading, description])

    # Bind the buy button to handle purchase flow
    btn = RaisedButton(text="Buy Now", style={"background-color": ""})
    btn.bind("click", self.handle_buy, update_self=True)
    self.add_child(btn)
```

---

## Imports

- Use absolute imports for project modules except for importing views where you can do `from . import views`:
    ```python
    # CORRECT:
    from web.ui.components.cards import SomeCard
    
    # WRONG
    from ..ui.components.cards import SomeCard
    ```

- Separate local and non-local imports:
  ```python
  # GOOD
  from duck.html.components.button import Button
  
  from web.ui.components.nav import SiteNavBar
  
  # BAD:
  from duck.html.components.button import Button
  from web.ui.components.nav import SiteNavBar
  
  ```

- Use centralized imports wherever possible.

- For components, import specific component you want to use rather than the whole module:
  ```python
  # GOOD:
   from duck.html.components.button import FlatButton, RoundButton
   
  # BAD:
  from duck.html.components import button
  ```
  
- Arrange and format imports so that they look clean and structured:
  ```python
  # GOOD:
  import os
  import some_module
  
  from duck.app import App
  from duck.contrib.sync import ensure_async
  
  # Local imports here
  from web.ui.pages.home import HomePage
  
  # BAD:
  from duck.app import App
  from duck.contrib.sync import ensure_async
  import os
  import some_module
  from web.ui.pages.home import HomePage
  
  ```

- Always use absolute imports because Duck is run from the base directory even for Django. This includes local django modules must have this prefix `web.backend.django.duckapp`:
  ```python
  # web/backend/django/duckapp/duckapp/settings.py
  # GOOD:
  INSTALLED_APPS = ["web.backend.django.duckapp.<appname>"]
  # Other settings here...
  
  # BAD:
  INSTALLED_APPS = ["<appname>"]
  # Other settings here...
  
  ```
  
  Application entry modules:
  
  ```python
  # web/backend/django/duckapp/myapp/apps.py
  # GOOD:
  from django.apps import AppConfig
  
  class MyAppConfig(AppConfig):
      default_auto_field = "django.db.models.BigAutoField"
      name = "web.backend.django.duckapp.myapp"

  # BAD:
  from django.apps import AppConfig
  
  class MyAppConfig(AppConfig):
      default_auto_field = "django.db.models.BigAutoField"
      name = "myapp"
  ```
  
  **This applies as well to other files `urls.py`, `views.py`, etc
---

## Centralized Systems — No Repetition

**Repeated code is prohibited.** If something appears more than once, it belongs in a
shared module, base class, service function, or constant. This is non-negotiable.

### What "centralized" means in this project

| Scenario | Solution |
|---|---|
| Same styles across components | `Theme` class in `web/ui/components/theme.py` |
| Same SEO tags on multiple pages | `BasePage` with overridable class attributes |
| Same nav/footer on every page | `SiteNav` and `SiteFooter` components |
| Same API call logic in multiple views | `services.py` or `api.py` module |
| Same Django model query repeated | Model manager method or service function |
| Same validation logic | Shared `validators.py` |
| Same error response pattern | Centralized handler or middleware |
| Same site URL / domain / name | `meta.py` module |
| Shared card/container styles | `CardBase` or similar base component |

### Example — centralized metadata

```python
# meta.py
"""
Centralized site metadata — shared across pages, SEO, and Open Graph tags.
"""

SITE_NAME = "Duck App"
SITE_URL = "https://myapp.duckframework.com"
SITE_DESCRIPTION = "A fast, reactive web app built with Duck Framework."
OG_IMAGE = "/static/images/og-default.png"
TWITTER_HANDLE = "@duckframework"
```

### Example — base page pattern

```python
# web/ui/pages/base.py
"""
Base page class. Every page in the project inherits from this.
"""

from duck.html.components.page import Page
from duck.shortcuts import resolve, static
from duck.utils.urlcrack import URL

from web.ui.components.nav import SiteNav
from web.ui.components.footer import SiteFooter
import meta


class BasePage(Page):
    """
    Provides shared layout, SEO defaults, and theme setup for all pages.

    Subclasses override `page_title`, `page_description`, and `build_page`
    to supply page-specific content and metadata.
    """

    # Override in subclasses for page-specific SEO
    page_title = meta.SITE_NAME
    page_description = meta.SITE_DESCRIPTION
    page_url = meta.SITE_URL

    def on_create(self):
        """
        Sets up theme, SEO, shared layout, and calls build_page for page content.
        """
        super().on_create()

        # Compute full canonical URL from request path
        home_url = resolve("home", absolute=True)
        self.page_url = URL(home_url).join(self.request.path).to_str()

        # Set all standard SEO meta tags
        self.set_title(self.page_title)
        self.set_description(self.page_description)
        self.set_canonical(self.page_url)
        self.set_opengraph(
            title=self.page_title,
            description=self.page_description,
            url=self.page_url,
            image=static(meta.OG_IMAGE),
            type="website",
            site_name=meta.SITE_NAME,
        )
        self.set_twitter_card(
            card="summary_large_image",
            title=self.page_title,
            description=self.page_description,
        )
        self.set_favicon("/static/favicon.ico")
        self.set_accessibility(lang="en")
        self.set_json_ld(self.get_json_ld())

        # Add shared layout — nav first, then page content, then footer
        self.add_to_body(SiteNav())
        self.build_page()
        self.add_to_body(SiteFooter())

    def build_page(self):
        """
        Override in subclasses to add page-specific body content.
        """
        pass

    def get_json_ld(self) -> dict:
        """
        Returns JSON-LD structured data for this page.

        Override in subclasses to provide schema markup (article, product, org, etc).

        Returns:
            A JSON-LD dict, or empty dict if not applicable.
        """
        return {}
```

---

## Pages

Each page class maps to one URL. Keep `on_create` and `build_page` focused —
delegate all content to components and helpers.

```python
# web/ui/pages/home.py
"""
Homepage page — the public landing page of the application.
"""

from web import meta
from web.ui.pages.base import BasePage
from web.ui.components.hero import HeroSection
from web.ui.components.features import FeaturesGrid


class HomePage(BasePage):
    """
    Renders the homepage with hero banner and features grid.
    """

    page_title = f"Home | {meta.SITE_NAME}"
    page_description = "Build reactive web apps in pure Python with Duck Framework."

    def build_page(self):
        """
        Adds hero banner and features grid to the page body.
        """
        # Add main hero section at the top
        self.add_to_body(HeroSection())

        # Add feature highlights below the hero
        self.add_to_body(FeaturesGrid())
```

### Page rules

- Always subclass `BasePage` — never `Page` directly unless you are building `BasePage`.
- Use `add_to_body()` for content, `add_to_head()` for head-level injections.
- Never call `page.add_child()` — raises `UnrecommendedAddChildWarning`.
- All common SEO logic lives in `BasePage`. Page subclasses only override what's different.

---

## Components

For the full built-in component API (Button, Container, Modal, Input, Form, etc.) plus other component related information
refer to **`HTML_COMPONENTS_GUIDE.md`**. The rules below apply to all component code in this project.

### Construction rules

Always pass everything via kwargs at construction time. Never mutate components
outside of lifecycle methods (`on_create`, `on_parent`, `on_root_finalized`).

```python
# Good — declarative, all at construction time
card = Card(
    id="featured-card",
    klass="card featured",
    style={"background": "var(--theme-surface)", "padding": "1rem"},
    children=[
        Heading(type="h3", text="Title"),
        Paragraph(text="Some description."),
    ]
)

# Bad — imperative mutation after construction
card = Card()
card.id = "featured-card"
card.style["background"] = "var(--theme-surface)"
card.add_child(Heading(type="h3", text="Title"))
```

### Component builders belong on the component

Builder methods must be methods of the component class they serve.
Never define standalone helper functions for building components.

```python
# Good
class ProductSection(InnerComponent):
    """
    Displays a grid of product cards with a section heading.
    """

    def on_create(self):
        """
        Builds the heading and product grid.
        """
        super().on_create()

        # Add section heading above the grid
        self.add_child(self.build_heading())

        # Add the product card grid
        self.add_child(self.build_product_grid())

    def build_heading(self):
        """
        Returns the section heading component.

        Returns:
            A Heading component with the section title.
        """
        return Heading(type="h2", text="Featured Products")

    def build_product_grid(self):
        """
        Returns a flex grid populated with product cards.

        Returns:
            A FlexContainer populated with ProductCard components.
        """
        products = self.kwargs.get("products", [])
        return FlexContainer(
            style={"flex-wrap": "wrap", "gap": "1rem"},
            children=[ProductCard(product=p) for p in products],
        )

# Bad — standalone function, disconnected from any component
def build_heading():
    return Heading(type="h2", text="Featured Products")
```

### Lively tracking rule

Lively only tracks style/prop values declared during the initial server render.
Always initialise every property you intend to update later, even if empty.

```python
# Good — Lively tracks display and background-color for later updates
btn = Button(text="Toggle", style={"display": "block", "background-color": ""})

# Bad — Lively cannot sync display later, it was never declared
btn = Button(text="Toggle")
```

### ID discipline

Every complex or composite component must have a meaningful `id`. IDs must be
stable, unique, and debug-friendly.

```python
Modal(id="confirm-delete-modal", title="Confirm Delete")
Card(id="pricing-pro-card")
```

### Event handler rules

- Prefer async handlers for any I/O-bound work.
- Only include `update_targets` components that actually change.
- Bind events that depend on a stable root inside `on_root_finalized`, not `on_create`.

---

## Async & Performance

Duck ships with full ASGI async support. Async is the correct default for any
I/O-bound work: database calls, HTTP requests, file operations, WebSocket events.

### Enable ASGI in settings

```python
# In your project settings (not the auto-generated settings.py)
ASYNC_HANDLING = True

# Use a faster event loop in production (install uvloop first)
ASYNC_LOOP = "uvloop"
```

### Prefer async views

```python
# Function-based async view
async def product_detail(request, slug: str):
    """
    Returns the product detail page for the given slug.

    Args:
        request: The incoming HTTP request.
        slug: The product URL slug.

    Returns:
        A rendered ProductDetailPage or 404 response.
    """
    # Fetch product asynchronously via service layer
    product = await get_product_by_slug_async(slug)

    if not product:
        return not_found404()

    # Render and return the product page
    return ProductDetailPage(request=request, product=product)
```

```python
# Class-based async view
from duck.views import View

class ProductDetailView(View):
    """
    Handles product detail requests asynchronously.
    """

    async def run(self):
        """
        Fetches and returns the product detail page.

        Returns:
            Rendered page or 404 response.
        """
        slug = self.request.kwargs.get("slug", "")

        # Delegate data fetching to the service layer
        product = await get_product_by_slug_async(slug)

        if not product:
            return not_found404()

        return ProductDetailPage(request=self.request, product=product)
```

### Never block the event loop

Blocking calls inside async code freeze the entire event loop and negate
all performance benefits of async. This includes `time.sleep`, `requests.get`,
synchronous file reads, and blocking Django ORM calls.

```python
# BAD — blocking I/O inside async context
async def on_click(btn, event, value, ws):
    import time
    time.sleep(2)                          # Blocks the loop
    result = requests.get("https://...")   # Blocking HTTP call
    data = open("file.txt").read()         # Blocking file read


# GOOD — async equivalents
import asyncio
import aiohttp
import aiofiles

async def on_click(btn, event, value, ws):
    # Non-blocking sleep
    await asyncio.sleep(2)

    # Async HTTP request
    async with aiohttp.ClientSession() as session:
        async with session.get("https://...") as response:
            data = await response.json()

    # Async file read
    async with aiofiles.open("file.txt") as f:
        content = await f.read()
```

### Converting sync code to async

When working with sync-only code (Django ORM, third-party libraries), use Duck's
contrib utilities to safely wrap it without blocking the event loop.

```python
from duck.contrib.sync import sync_to_async, convert_to_async_if_needed

# Wrap a known sync function into an awaitable
result = await sync_to_async(some_sync_function)(arg1, arg2)

# Automatically handles both sync and async callables
result = await convert_to_async_if_needed(maybe_sync_or_async_fn)(arg1) # ensure_async() does the same thing
```

**Rule:** Never call Django ORM directly in an async view or handler. Always wrap it.

```python
async def on_submit(form, event, form_inputs, ws):
    """
    Saves a contact form entry, wrapping the sync ORM call for async safety.

    Args:
        form: The Form component that fired the submit event.
        event: The event name.
        form_inputs: Dict of {name: value} from all named inputs.
        ws: The active WebSocket connection.
    """
    name = form_inputs.get("name", "").strip()

    # Wrap sync Django ORM call — must not block the event loop
    await ensure_async(save_contact_sync)(name=name)

    # Update status label to confirm submission
    self.status_label.text = "Saved!"
```

### Async component event handlers

All event handlers that touch I/O must be async:

```python
async def handle_load_data(self, btn, event, value, ws):
    """
    Loads dashboard stats asynchronously and updates the display.

    Args:
        btn: The component that fired the event.
        event: The event name.
        value: Event payload.
        ws: The active WebSocket connection.
    """
    # Fetch fresh data from the service layer
    stats = await fetch_dashboard_stats_async()

    # Reflect updated data in the stats panel component
    self.stats_panel.update(stats)
```

---

## Views

Keep views thin. They receive requests, delegate work to services, and return responses.
No ORM queries, business logic, or raw SQL inside views.

```python
# web/views.py
"""
View handlers for the project's main URL routes.
"""

from duck.shortcuts import not_found404, redirect, jsonify, resolve
from duck.views import View

from web.ui.pages.home import HomePage
from web.ui.pages.about import AboutPage
from web.services.products import async_get_product_by_slug


async def home(request):
    """
    Renders the homepage.

    Args:
        request: The incoming HTTP request.

    Returns:
        A rendered HomePage component.
    """
    return HomePage(request=request)


async def about(request):
    """
    Renders the about page.

    Args:
        request: The incoming HTTP request.

    Returns:
        A rendered AboutPage component.
    """
    return AboutPage(request=request)


class ProductDetailView(View):
    """
    Returns the detail page for a product identified by URL slug.
    """

    async def run(self):
        """
        Fetches the product and renders its detail page.

        Returns:
            Rendered ProductDetailPage or 404 response.
        """
        from web.ui.pages.product import ProductDetailPage
        
        slug = self.request.kwargs.get("slug", "")

        # Fetch via service — never query ORM directly in views
        product = await async_get_product_by_slug(slug)

        if not product:
            return not_found404() # Or return a custom 404 error Page.

        return ProductDetailPage(request=self.request, product=product)
```

---

## Routing & Blueprints

### Basic routing

Routes live in `web/urls.py`. Flat, one per line, grouped by concern with a comment.

```python
# web/urls.py
"""
URL routing — maps patterns to page and view handlers.
"""

from duck.urls import path

from . import views


urlpatterns = [
    # Public pages
    path("/", views.home, name="home"),
    path("/about", views.about, name="about"),

    # Product routes
    path("/products/<slug>", views.ProductDetailView, name="product-detail"),
]
```

### Blueprints for large projects

Use [Blueprints](https://docs.duckframework.com/main/blueprints) to group related routes under a shared namespace. The right choice
whenever a feature area has multiple routes (API, blog, shop, auth, etc).

```
web/
└── api/
    ├── blueprint.py
    └── views.py
```

```python
# web/api/blueprint.py
"""
Blueprint for all API endpoints under the /api/ namespace.
"""

from duck.routes import Blueprint
from duck.urls import path

from . import views


ApiBlueprint = Blueprint(
    location=__file__,
    name="api",
    urlpatterns=[
        path("/products", views.product_list, name="products", methods=["GET"]),
        path("/products/<slug>", views.product_detail, name="product-detail"),
    ],
    prepend_name_to_urls=True,
    enable_static_dir=False,
    enable_template_dir=False,
)
```

Register the blueprint in `settings.py`:

```python
BLUEPRINTS = [
    "web.api.blueprint.ApiBlueprint",
]
```

Resolve blueprint URLs with their namespaced name:

```python
# Resolves to /api/products
url = resolve("api.products")
```

Render blueprint templates with their namespaced name:

```python
# Render a template at web/api/templates/product.html
response = render("api/product.html")
```

Resolve blueprint static/media URLs with their namespaced name:

```python
# Resolve to /static/api/images/logo.png
url = static("api/images/logo.png")
```

### Routing rules

- Never hardcode URL strings — always use `resolve()` from `duck.shortcuts`.
- Use `not_found404()` and `redirect()` from `duck.shortcuts`, never raw responses.
- Route `<param>` converters are defined directly inside `path()`.

---

## Django Integration

Duck and Django run in the same Python environment — they communicate with zero
network overhead. Use Django for its ORM and ecosystem; use Duck for the UI and server.

### Setup

```bash
duck makeproject myproject
cd myproject
duck django-add "path/to/your/django_project"
duck runserver -dj
```

### Rules

- Django app code goes in `web/backend/django/duckapp/<appname>/`.
- Always run `python manage.py makemigrations <appname>` by explicit app name.
- Add apps to `INSTALLED_APPS` with their full dotted path.
- Set `USE_DJANGO = 1` in Duck's environment config.
- Never perform ORM queries inside Duck pages or components — delegate to services.
- Never call Django ORM synchronously in an async view — use `ensure_async` from
  `duck.contrib.sync` to wrap it safely.
- Duck mostly use Django for it's ORM so the best app to create for Django is `core`. Django project structure in 
  Django is auto-created. Read the contents to understand the structure.
- Never try to manually create Django files and directories inside the directory `web/backend/django` (unless necessary), they are auto-generated by Duck.
- Use absolute imports in auto-generated Django projects e.g. `ROOT_URLCONF = "web.backend.django.duckapp.duckapp.urls"`.

```python
# web/services/users.py
"""
User service module — bridges Duck async views and Django's sync ORM.
"""

from duck.contrib.sync import ensure_async


async def async_get_user_profile(user_id: int):
    """
    Retrieves a user profile by ID, wrapping the sync ORM call.

    Args:
        user_id: The primary key of the target user.

    Returns:
        A UserProfile instance, or None if not found.
    """
    from web.backend.django.duckapp.myapp.models import UserProfile
    
    # Django ORM is sync — wrap it to avoid blocking the event loop
    return await ensure_async(UserProfile.objects.filter)(pk=user_id).first
```

**Other Operations to Perform:**

If models are present and being used, register them in the app's admin.py.
- If models are in use, update the auto-generated URL patterns in web/backend/django/duckapp/duckapp/urls.py — include the admin URL and configure the admin site to match the brand:
  ```
  # web/backend/django/duckapp/duckapp/urls.py
  from django.urls import path
  from django.contrib import admin
  from duck.backend.django import urls as duck_urls
    
  from web.ui.components.theme import Theme
    
  # Brand the admin site
  admin.site.site_header = Theme.brand_name
  admin.site.site_title = ""
  admin.site.index_title = "Dashboard"
    
  urlpatterns = duck_urls.urlpatterns + [
      path("admin/", admin.site.urls),
      # Add your URL patterns here
  ]
  ```

---

## Middleware

Middlewares intercept all requests and responses. Use them for cross-cutting
concerns: authentication, rate-limiting, logging, security headers.

```python
# web/middlewares/auth.py
"""
Authentication middleware — blocks unauthenticated requests to protected routes.
"""

from duck.http.middlewares import BaseMiddleware
from duck.http.request import HttpRequest
from duck.http.response import HttpResponse, HttpBadRequestResponse


class AuthMiddleware(BaseMiddleware):
    """
    Rejects requests to protected routes that lack a valid session.
    """

    # All paths that require authentication
    PROTECTED_PREFIXES = ("/dashboard", "/admin", "/api/private")
    
    # Debug error message which may be logged to the console for debugging purposes.
    debug_message: str = "'AuthMiddleware: Authentication error"
    
    @classmethod
    def get_error_response(cls, request):
        """
        Returns the error response when `process_request` returns `cls.request_bad`.
        """
        error_response = HttpBadRequestResponse("Sorry there is an error in Request, that's all we know!")
        return error_response
        
    @classmethod
    def process_request(cls, request: HttpRequest) -> int:
        """
        Checks session authentication for protected route prefixes.

        Args:
            request: The incoming HTTP request.

        Returns:
            request_ok for public routes or authenticated requests,
            request_bad for unauthenticated access to protected paths.
        """
        # Pass all public routes through without checking
        is_protected = any(
            request.path.startswith(p) for p in cls.PROTECTED_PREFIXES
        )
        if not is_protected:
            return cls.request_ok

        # Reject requests with no active session
        if not request.session.get("user_id"):
            return cls.request_bad

        return cls.request_ok

    @classmethod
    def process_response(cls, response: HttpResponse, request: HttpRequest) -> None:
        """
        Injects security headers into every outgoing response.

        Args:
            response: The outgoing HTTP response.
            request: The originating HTTP request.
        """
        # Add standard security headers to prevent common attacks
        response.set_header("X-Frame-Options", "DENY")
        response.set_header("X-Content-Type-Options", "nosniff")
```

Register in `settings.py`:

```python
MIDDLEWARES = [
    "web.middlewares.auth.AuthMiddleware",
]
```

---

## Caching — Views & Components

Caching reduces server load for content that doesn't change every request.
Duck supports both view-level and component-level caching.

### Cached views

```python
from duck.views.utils.caching import cached_view

@cached_view(expiry=300, targets=["method"])
async def landing(request):
    """
    Renders the landing page, cached per user method for 5 minutes.

    Args:
        request: The incoming HTTP request.

    Returns:
        A rendered LandingPage component.
    """
    return LandingPage(request=request)
```

### Cached components

**Caching components based on arguments parsed to the component cls:**

```python
from duck.html.components.utils.caching import cached_component, static_component


@cached_component()
class HeroSection(FlexContainer):
    """
    Hero banner — cached but can be dynamic, new mutations can happen after construction.
    """

    def on_create(self):
        """
        Builds the hero content.
        """
        super().on_create()
        ...


@static_component()
class FooterLinks(FlexContainer):
    """
    Footer link grid — fully static, frozen, cached indefinitely - no mutations are allowed after construction.
    """

    def on_create(self):
        """
        Builds the static footer links.
        """
        super().on_create()
        ...
```

### When to cache

| Scenario | Strategy |
|---|---|
| Component too big | `@cached_view` |
| Component never changes | `@static_component()` |
| Content is user-specific | No caching — render fresh every request |

> For advanced caching or a deep understing of this, checkout [Component Caching](https://docs.duckframework.com/main/cached-components) or 
> [View Caching](https://docs.duckframework.com/main/cached-views)

---

## Task Automation

Duck's automation system replaces `cron` and `Celery` for most use cases.
Define automations in `automations.py`, register them in `settings.py`.

```python
# web/automations.py
"""
Background automation tasks for scheduled and lifecycle-driven operations.
"""

from duck.automation import Automation
from duck.automation.trigger import NoTrigger


class CleanExpiredSessionsAutomation(Automation):
    """
    Deletes expired Django sessions from the database once per day.
    """

    def execute(self):
        """
        Removes all session records that have passed their expiry date.
        """
        from django.contrib.sessions.models import Session
        from django.utils import timezone

        # Delete expired sessions in a single query
        Session.objects.filter(expire_date__lt=timezone.now()).delete()


# Schedule to run daily, with no end
CleanExpiredSessions = CleanExpiredSessionsAutomation(
    name="Clean Expired Sessions",
    description="Removes expired Django session records from the database.",
    start_time="immediate",
    schedules=-1,      # -1 = run indefinitely
    interval=86400,    # Every 24 hours
)
```

Register in `settings.py`:

```python
RUN_AUTOMATIONS = True

AUTOMATIONS = {
    "automations.CleanExpiredSessions": {
        "trigger": "duck.automation.trigger.NoTrigger",
    },
}
```

### Asynchronous Automations

```python
# web/automations.py
"""
Asynchronous background automation tasks for scheduled and lifecycle-driven operations.
"""

from duck.automation import Automation
from duck.automation.trigger import NoTrigger
from duck.contrib.sync import ensure_async


class CleanExpiredSessionsAutomation(Automation):
    """
    Deletes expired Django sessions from the database once per day.
    """

    async def execute(self):
        """
        Removes all session records that have passed their expiry date.
        """
        from django.contrib.sessions.models import Session
        from django.utils import timezone

        # Delete expired sessions in a single query
        await ensure_async(
            lambda: Session.objects.filter(expire_date__lt=timezone.now()).delete()
        )()
        
# Schedule to run daily, with no end
CleanExpiredSessions = CleanExpiredSessionsAutomation(
    name="Clean Expired Sessions",
    description="Removes expired Django session records from the database.",
    start_time="immediate",
    schedules=-1,      # -1 = run indefinitely
    interval=86400,    # Every 24 hours
    async_=True, # Run in asyncio event loop
)
```

### Custom triggers

```python
from duck.automation.trigger import AutomationTrigger


class LowDiskSpaceTrigger(AutomationTrigger):
    """
    Fires when available disk space drops below a defined threshold.
    """

    THRESHOLD_GB = 2.0

    def listen(self) -> bool:
        """
        Returns True when disk space is critically low.

        Returns:
            True if available GB is below the threshold, False otherwise.
        """
        import shutil

        # Check current free disk space in gigabytes
        free_gb = shutil.disk_usage("/").free / (1024 ** 3)
        return free_gb < self.THRESHOLD_GB
```

---

## Background Managers

Duck provides `ThreadPoolManager` and `AsyncioLoopManager` for background work.
Read the docs carefully: https://docs.duckframework.com/main/background-managers.html

### Key rules

- **Let Duck create its own managers unless you have a specific need.** Creating
  extra managers fragments execution and wastes resources.
- If you must create one, do so **inside the worker thread**, not the main thread.
  Managers created in the main thread propagate to all worker threads Duck spawns.
- Always verify the returned instance is the one you intend to use.
- Never create more manager instances than necessary.

```python
from duck.utils.asyncio.eventloop import get_or_create_loop_manager


def schedule_background_task(async_fn, *args):
    """
    Submits an async task to the current thread's event loop manager.

    Args:
        async_fn: The async callable to run in the background.
        *args: Positional arguments passed to async_fn.

    Returns:
        A Future representing the submitted task.
    """
    # Get the loop manager for this thread — call inside worker, not main thread
    manager = get_or_create_loop_manager()

    # Submit — do not assume this is Duck's internal manager
    return manager.submit_task(async_fn, *args)
```

---

## Theming & Styling

Never scatter raw color, font, or spacing values across components. Use a
centralized `Theme` class as the single source of truth for all design tokens.  

Reference CSS variables in component styles — never raw hex or pixel values:

```python
# Good — uses theme CSS variables, stays in sync with Theme class
card = Card(
    style={
        "background": Theme.surface_color,
        "border-radius": Theme.radius_md,
        "color": Theme.text_color,
    },
)

# Bad — hardcoded, breaks when the theme changes
card = Card(style={"background": "#1a1a1a", "border-radius": "10px"})
```

---

## SEO

Use Duck's built-in SEO methods exclusively. Never manually build `<meta>` tags.
All baseline SEO logic lives in `BasePage` — pages only override what's different.

```python
# Full SEO setup in BasePage.on_create
self.set_title(self.page_title)
self.set_description(self.page_description)
self.set_canonical(self.page_url)
self.set_author("Brian Musakwa")
self.set_robots("index, follow")
self.set_lang("en")
self.set_opengraph(
    title=self.page_title,
    description=self.page_description,
    url=self.page_url,
    image=static(meta.OG_IMAGE),
    type="website",
    site_name=meta.SITE_NAME,
)
self.set_twitter_card(
    card="summary_large_image",
    title=self.page_title,
    description=self.page_description,
    image=static(meta.OG_IMAGE),
    site=meta.TWITTER_HANDLE,
)
self.set_json_ld(self.get_json_ld())
self.set_favicon("/static/favicon.ico")
```

### JSON-LD per page

```python
class AboutPage(BasePage):
    """
    About page with Organization schema markup.
    """

    page_title = f"About | {meta.SITE_NAME}"

    def get_json_ld(self) -> dict:
        """
        Returns Organization JSON-LD for the about page.

        Returns:
            A JSON-LD dict with schema.org Organization type.
        """
        return {
            "@context": "https://schema.org",
            "@type": "Organization",
            "name": meta.SITE_NAME,
            "url": meta.SITE_URL,
        }
```

### SEO rules

- Every page sets at minimum: `title`, `description`, `canonical`, `opengraph`, `twitter_card`.
- Keep descriptions between 120–160 characters.
- `set_canonical` must be called on every page — prevents duplicate content penalties.
- Just like JSON-LD per page approach. You can also set fields like title, opengraph, description, etc dynamically per page for maximum SEO.

---

## Shortcuts Reference

Always import and use these from `duck.shortcuts`. Never construct raw responses manually.

| Function | Purpose |
|---|---|
| `redirect(location, permanent=False)` | HTTP redirect response |
| `not_found404(body=None)` | 404 Not Found response |
| `jsonify(data, status_code=200)` | JSON response |
| `render(request, template, context, engine="django")` | Render a Jinja2 or Django template |
| `jinja2_render(request, template, context)` | Render Jinja2 template explicitly |
| `django_render(request, template, context)` | Render Django template explicitly |
| `resolve(name, absolute=True, fallback_url=None)` | Resolve a named URL |
| `static(resource_path)` | Absolute static file URL |
| `media(resource_path)` | Absolute media file URL |
| `static_filepath(relative_filepath, blueprint=None)` | Absolute static file path |
| `media_filepath(relative_filepath, blueprint=None)` | Absolute media file path |
| `csrf_token(request)` | CSRF token string |
| `to_response(value)` | Convert any value to HttpResponse |
| `merge(base, take)` | Merge two HTTP response objects |

```python
from duck.shortcuts import redirect, not_found404, jsonify, resolve, static

# Redirect after successful form submission
return redirect(resolve("dashboard"))

# 404 for a missing resource
return not_found404()

# JSON API response with 201 status
return jsonify({"status": "created", "id": new_id}, status_code=201)

# Absolute static file URL for use in components
logo_url = static("images/logo.svg")
```

### Strict Rules: Points to Note

- Every Information here is important, follow it.
- Never hardcode data like URLs, always use these helpers e.g. `resolve`, `static`, `media`.
- For more info on the API Documentation look at https://docs.duckframework.com/main/api/duck.shortcuts
- For more customization on responses see https://docs.duckframework.com/main/api/duck.http.response
- For dynamic urls with <param> returned by resolve, use string method `replace()` for replacing the dynamic parameter e.g.:
  
  ```python
  # Route: /products/<id>
  product_url = resolve("product").replace("<id>", "1234")
  ```
  
---

## Security & Settings

- Never commit secrets. Use environment variables via `python-decouple` or similar.
- `SECRET_KEY`, database credentials, and API keys go in `.env`, never in code.
- Duck manages HTTPS and SSL — always run production over HTTPS.
- Use Duck CSRF protection for all state-changing endpoints.
- Validate and sanitize all `form_inputs` before any database interaction.
- Use middleware for authentication guards, rate-limiting, and security header injection.

```python
# config.py
"""
Environment-based config loader — all secrets come from the environment.
"""

from decouple import config

SECRET_KEY = config("SECRET_KEY")
DATABASE_URL = config("DATABASE_URL")
DEBUG = config("DEBUG", default=False, cast=bool)
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="localhost").split(",")
```

---

## Deployment

Full deployment guide: https://docs.duckframework.com/main/deployment

### Pre-deployment checklist

- `DEBUG = False` in production settings.
- `ASYNC_HANDLING = True` set for all async views.
- Configure [`certbot auto ssl automation`](https://docs.duckframework.com/main/free-ssl-certificate) if you are not using managed SSL service.
- Static files collected with `duck collectstatic`.
- All database migrations applied.
- `RUN_AUTOMATIONS = True` in settings.
- Monitor app health with `duck monitor`.
- Service management configured via `duck service` commands for auto-restart.

---

## General Best Practices

### Keep it clean

- No dead code. Remove unused imports, variables, and commented-out blocks.
- No magic numbers — name constants and place them on the class or in `meta.py`.
- One responsibility per function. If it does two things, split it.
- Short, focused functions over long ones. Extract when in doubt.

### Keep it centralized

- Styles ->`Theme` class.
- SEO -> `BasePage`.
- Shared layout -> base components (`SiteNav`, `SiteFooter`, `CardBase`, etc.).
- Data access -> service modules in `services/`.
- URL strings -> resolved via `resolve()`, `static()`, `media()` never hardcoded.
- Site metadata -> `meta.py`.

### Keep it async

- Default to async views and handlers for all I/O.
- Never block the event loop with sync calls.
- Wrap Django ORM and other sync code with `ensure_async` or
  `convert_to_async_if_needed` from `duck.contrib.sync`.

### Keep it documented

- Every `.py` file starts with a module docstring.
- Every class and public method has a Google-style docstring.
- Every logical block has a short `# Action phrase` comment above it.
- Comments explain intent, not syntax.

### Keep it honest

- If something is a known limitation or temporary fix, say so in a comment.
- If a function has side effects, document them in the docstring.
- If a component requires specific props, list them in the class docstring.
- If unsure about a component's API, fetch its docs before writing any code:
  `https://docs.duckframework.com/main/api/duck/duck.html.components.<module>.html`

### Rules

- Don't assume, if unsure about anything, fetch info from the docs at https://docs.duckframework.com/main/
- Follow this guideline
- Read this twice to avoid making mistakes.
- Always generate code that is future proof and ready to scale at any point.
- Do not overengineer on simple functionality, introducing unnecessary complexity e.g. introducing Mixins, etc.
- For this arrow character (→), use ➝‬ instead.

---

*Docs: https://docs.duckframework.com/main/*
