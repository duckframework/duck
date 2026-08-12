# Understanding the Project

Duck generates a set of files and directories as you build your application. This section walks through the core ones you'll interact with most.

## `web/main.py`

The entry point for your Duck application. Run it directly with `python web/main.py`, or use the `duck runserver` command.

```py
#!/usr/bin/env python
"""
Main script for creating and running the Duck application.
"""

from duck.app import App

app = App(port=8000, addr="0.0.0.0", domain="localhost")

if __name__ == "__main__":
    app.run()
```

## `web/urls.py`

Defines the URL routes for your application. Each route maps a static or dynamic path to a **view** — a callable that handles incoming requests for that path.

By default, `urlpatterns` is an empty list. Add your own routes to wire up the app.

**HTTP route example:**

```py
from duck.urls import path
from duck.http.response import HttpResponse

def home(request):
    return HttpResponse("Hello world")

urlpatterns = [
    path('/', home, name="home"),
]
```

**WebSocket route example:**

```py
from duck.urls import path
from duck.contrib.websockets import WebSocketView

class SomeWebSocket(WebSocketView):
    async def on_receive(self, data: bytes, opcode):
        # Handle incoming WebSocket data
        await self.send_text("Some text")

        # Other available send methods:
        # send_json, send_binary, send_ping, send_pong, send_close

urlpatterns = [
    path('/some_endpoint', SomeWebSocket, name="some_ws_endpoint"),
]
```

## `web/views.py`

An optional file for organizing your view functions. Import it as a module in `urls.py` to keep your routes clean.

```py
# web/urls.py
from duck.urls import path
from . import views

urlpatterns = [
    path('/', views.home, name="home"),
]
```

## `web/ui/`

Contains all frontend logic — components, pages, templates, and static files.

### `web/ui/pages/`

Duck recommends building UI with **Pages** — Python classes that represent full HTML pages. Pages unlock the [Lively Component System](https://docs.duckframework.com/main/lively-components), enabling fast navigation and real-time interactivity without JavaScript or full page reloads.

**What is an HTML component?**

A component is a Python class that represents an HTML element. Configure it with props and style, then render it to HTML.

```py
from duck.html.components import InnerComponent

class Button(InnerComponent):
    def get_element(self):
        return "button"

btn = Button(text="Hello world")

print(btn.render())  # <button>Hello world</button>
```

Duck ships with many built-in components — `Button`, `Navbar`, `Modal`, `Input`, and more — available under `duck.html.components`.

**Creating pages**

Subclass `duck.html.components.page.Page` to create a page. The recommended pattern is a `BasePage` that defines the shared layout, with individual pages overriding only what they need.

```py
# web/ui/pages/base.py
from duck.html.components.container import FlexContainer
from duck.html.components.page import Page

class BasePage(Page):
    def on_create(self):
        super().on_create()
        self.set_title("MySite")
        self.set_description("Some base description ...")

        # Set up the root layout container
        self.main = FlexContainer(flex_direction="column")
        self.add_to_body(self.main)

        self.build_layout(self.main)

    def build_layout(self, main):
        # Override in subclasses to define page-specific layout
        pass
```

```py
# web/ui/pages/home.py
from duck.html.components.container import Container
from web.ui.pages.base import BasePage

class HomePage(BasePage):
    def build_layout(self, main):
        main.add_child(Container(text="Hello world"))
```

**Using pages in views:**

```py
# web/views.py
from duck.shortcuts import to_response

def home(request):
    return to_response(HomePage(request))
```

> Pages automatically enable fast client-side navigation via Lively. Unlike templates, switching between pages does not trigger a full reload.

### `web/ui/components/`

Where your custom reusable components live. The example below shows a feedback form with real-time UI updates powered by Lively.

```py
# web/ui/components/form.py
from duck.html.components.form import Form
from duck.html.components.input import Input, InputWithLabel
from duck.html.components.textarea import TextArea
from duck.html.components.button import Button
from duck.html.components.label import Label

class MyFeedbackForm(Form):
    def on_create(self):
        super().on_create()

        # Status label for displaying feedback or errors
        self.label = Label(text="")

        self.add_children([
            self.label,
            InputWithLabel(
                label_text="Your name",
                input=Input(name="name", type="text", placeholder="Enter your name", required=True),
            ),
            InputWithLabel(
                label_text="Your message",
                input=TextArea(name="message", placeholder="Your message", required=True),
            ),
            Button(text="Submit", props={"type": "submit"}),
        ])

        # Bind submit event — update_targets lists components to re-render on the client
        self.bind("submit", self.on_form_submit, update_self=True, update_targets=[self.label])

    async def on_form_submit(self, form, event, form_inputs, ws):
        name = form_inputs.get("name").strip()
        message = form_inputs.get("message").strip()

        # Validate and persist the message here

        # Patch the label in-place on the client
        self.label.text = "Your message has been received"
        self.label.color = "green"
```

### `web/ui/templates/`

Prefer classic server-rendered templates? Store them here. Duck supports both **Django** and **Jinja2** template engines.

```django
{# web/ui/templates/home.html #}
{% extends 'base.html' %}

{% block main %}
  Hello world!
{% endblock main %}
```

```py
# web/views.py
from duck.shortcuts import render, async_render

def home(request):
    return render("home.html", engine="django")  # or engine="jinja2"

async def async_home(request):
    return await async_render("home.html", engine="django")
```

> You can also use HTML components inside templates. See [Lively Components](https://docs.duckframework.com/main/lively-components) for details.

### `web/ui/static/`

Contains static files for your application — CSS, JS, images, and videos.

> Instead of hard-coding static file URLs in components or templates, use the `static` function from `duck.shortcuts`.

```py
# views.py
from duck.shortcuts import static

def home(request):
    # Instead of:
    my_image_url = "/static/images/my-image.png"

    # Do this instead:
    my_image_url = static("images/my-image.png")

    return "Hello world"  # Anything here.
```

> The same applies to internal URLs — use the `resolve()` function from `duck.shortcuts` instead of hard-coding them.

---

**Next:** [Django Integration](./django-integration.md) — bring Duck's HTTP/2, HTTPS, and security features to an existing Django project.
