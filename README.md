# Duck Framework
[![Python >=3.10](https://img.shields.io/badge/python->=3.10-blue.svg)](https://www.python.org/downloads/release/python-3100/)
[![GitHub stars](https://img.shields.io/github/stars/duckframework/duck?style=social)](https://github.com/duckframework/duck/stargazers)
[![License](https://img.shields.io/github/license/duckframework/duck)](https://github.com/duckframework/duck/blob/main/LICENSE)
[![Build Status](https://img.shields.io/github/actions/workflow/status/duckframework/duck/docs.yml?branch=main)](https://github.com/duckframework/duck/actions)
[![Open Issues](https://img.shields.io/github/issues/duckframework/duck)](https://github.com/duckframework/duck/issues)
[![Contributors](https://img.shields.io/github/contributors/duckframework/duck)](https://github.com/duckframework/duck/graphs/contributors)
[![HTTPS](https://img.shields.io/badge/HTTPS-supported-brightgreen.svg)](#)
[![HTTP/2](https://img.shields.io/badge/HTTP--2-supported-brightgreen.svg)](#)
[![WebSocket](https://img.shields.io/badge/WebSocket-supported-brightgreen.svg)](#)
[![Async Views](https://img.shields.io/badge/Async-WSGI%2FASGI-blue.svg)](#)
[![Task Automation](https://img.shields.io/badge/Task-Automation-blueviolet.svg)](#)
[![Content Compression](https://img.shields.io/badge/Compression-gzip%2C%20brotli%2C%20deflate-blue.svg)](#)
[![SSL Auto-Renewal](https://img.shields.io/badge/SSL-Auto%20Renewal-brightgreen.svg)](#)
[![Resumable Downloads](https://img.shields.io/badge/Downloads-Resumable-orange.svg)](#)
[![Security](https://img.shields.io/badge/Security-DoS%2C%20SQLi%2C%20CmdInj-red.svg)](#)
[![Duck Sight Reloader](https://img.shields.io/badge/HotReload-DuckSight-yellow.svg)](#)
[![Django Integration](https://img.shields.io/badge/Django-Integration-blue.svg)](#)
[![Monitoring](https://img.shields.io/badge/Monitoring-CPU%2FRAM%2FDisk%2FI%2FO-brightgreen.svg)](#)

**Duck Framework** is an open-source Python web framework and web server with built-in reactive UI and real-time WebSocket support. Build high-performance, scalable, server-side reactive web applications — without separate frontend frameworks or complex JavaScript stacks.

---

## Real world apps built with Duck framework:

1. [Snip - URL Shortener](https://snip.duckframework.com)
2. [Quill - AI Design Generator](https://quill.duckframework.com)
3. [Counter - Simple Counter App](https://duckframework.com/counterapp)

---

## Duck simplifies web development with:

1. [**Built-in HTTPS support**](https://docs.duckframework.com/main/https-and-http2) for secure connections  
2. **Native HTTP/2 support** with **HTTP/1** backward compatibility [link](https://docs.duckframework.com/main/https-and-http2)  
3. Hassle-free **free SSL certificate generation** with **automatic renewal** [link](https://docs.duckframework.com/main/free-ssl-certificate)  
4. [**Lively Component System**](https://docs.duckframework.com/main/lively-components) — with `VDom Diffing` (support for fast UI's) 
5. [**WebSocket support**](https://docs.duckframework.com/main/websocket) — modern websocket implementation with `per-message compression`.
6. Built-in [task automation](https://docs.duckframework.com/main/automations) — no need for [cron jobs](https://en.m.wikipedia.org/wiki/Cron)  
7. Automatic **content compression** using `gzip`, `deflate` or `brotli`
8. Support for **chunked transfer encoding**  
9. Easy integration with existing **Django** projects using [`django-add`](https://docs.duckframework.com/main/django-integration) command.
10. Organized routing with **Duck** [`Blueprints`](https://docs.duckframework.com/main/blueprint)
11. Full support for **async views** or asynchronous code even in [`WSGI`](https://docs.duckframework.com/main/wsgi) environment
12. Dynamic project generation with `makeproject` (`mini`, `normal`, or `full`)  
13. Runs on both [`WSGI`](https://docs.duckframework.com/main/wsgi) and [`ASGI`](https://docs.duckframework.com/main/asgi) environments, can even run `async` protocols like `HTTP/2` or `WebSockets` on `WSGI`.  
14. High-performance with low-latency response times  
15. **Resumable downloads** for large files  
16. Protection against **DoS**, **SQL Injection**, **Command Injection**, and other threats  
17. **Auto-reload** in debug mode for rapid development  
18. [**Free production SSL**](https://docs.duckframework.com/main/free-ssl-certificate) — no certificate costs  
19. **Automatic SSL renewal** using `certbot` plus Duck automation system
20. Comes with built-in web development tools and helpers  
21. [Log management](https://docs.duckframework.com/main/logging) with `duck logs` and file-based logging by default  
22. Real-time [system monitoring](https://docs.duckframework.com/main/monitoring) for CPU, RAM, Disk usage, and I/O activity with `duck monitor`
23. Easily generate app sitemap using command [`duck sitemap`](https://docs.duckframework.com/main/sitemap) or just use 
       the builtin blueprint [`duck.etc.apps.essentials.blueprint.Sitemap`](https://docs.duckframework.com/main/sitemap) for dynamic cached sitemap serving.
24. Comes with independant [micro applications](https://docs.duckframework.com/main/microapps) which runs on their own servers for micro services support.
25. Highly **customizable** to fit any use case  

And more — see [feature list](https://duckframework.com/features)

## Upcoming Features

1. **HTTP/3 with QUIC** – Faster, modern transport for improved performance.  
2. **QUIC WebTransport** – A next-gen alternative to WebSockets for real-time communication.  
3. **Component Pre-rendering System** – A system to preload components in the background thread to reduce initial load times of component trees.
4. **Customizable Dashboards** – Tailor interfaces to your workflow and preferences.  
5. **MQTT (Message Queuing Telementry Transport) Integration** – Run your own broker and manage IoT devices with ease.  
6. **Duck WebApp to APK** – Easily convert a Duck web application to APK.
7. **DuckSight Hot Reload** – Instead of full reload on file changes, implement **hot reload** for the **DuckSight Reloader**. This is faster and efficient than full reload.
8. **Internal Updates** – Implement logic for listing and securely applying updates when available, utilizing cryptographic code signing (using standards like TUF) to verify GitHub-sourced updates, protecting against rollbacks, and man-in-the-middle exploits.
9. ~~**Worker Processes** – Use of worker processes to utilize all available CPU cores for improved request handling.~~
10. **Complete Reverse Proxy Server** – **Duck** only acts as reverse proxy for  Django only. Need to make Duck a full-fledged reverse proxy server with optional sticky sessions.
11. ~~**Component Mutation Observer** – Need to build an optional component mutation observer for keeping track of child changes for fastest re-render (approx. 75x fast on unchanged children).~~
12. **MCP (Model Context Protocol) Server** – Need to make it easy for creating MCP servers for easy AI communication. 
13. **JWT (JSON-based Web Token) Authentication** – Need  to add JWT authentication persistent logins.
14. **...and more** – [Request a feature](./feature_request.md)

---

## 🦆 Fun Facts

- The **Duck** official website is powered by the **Duck** framework itself—showcasing a true "dogfooding" approach!
- [**Duck's Lively components**](https://docs.duckframework.com/main/lively-components) bring you a **Lively UI** that's exceptionally fast and responsive, eliminating slow page re-rendering for a seamless user experience.

---

## AI Assistance

All AI-assisted functionality is grouped under the `ai` directory in the root of this repository.

This directory includes:
- AI integration logic
- Supporting utilities and helpers
- Configuration and usage examples

Refer to it for a deeper understanding of how AI is incorporated into the project.

---

## Getting Started

**Install latest version from Github using:**

```sh
pip install git+https://github.com/duckframework/duck.git
```

**Or install from `PyPi` using:**

```sh
pip install duckframework
```

---

## Project Creation

```sh
duck makeproject myproject
```

This creates a `normal` project named `myproject`. You can also create other project types using:

- `--full` for a full-featured project  
- `--mini` for a simplified starter project

### Full Project

The full version includes everything **Duck** offers. Recommended for experienced developers.

```sh
duck makeproject myproject --full
```

### Mini Project

Beginner-friendly. Lightweight version with essential functionality.

```sh
duck makeproject myproject --mini
```

---

## Simple Startup

```sh
duck makeproject myproject
cd myproject
duck runserver   # or: python3 web/main.py
```

This starts the server at **http://localhost:8000**   

**Duck** serves a basic site by default — explore more at [Documentation](https://docs.duckframework.com/main)

---

## Understanding the Project

Duck generates a set of files and directories as you build your application. This section walks through the core ones you'll interact with most.

---

### `web/main.py`

The entry point for your Duck application. You can run it directly with `python web/main.py`, or use the `duck runserver` command instead.

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

---

### `web/urls.py`

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

---

### `web/views.py`

An optional file for organising your view functions. Import it as a module in `urls.py` to keep your routes clean.

```py
# web/urls.py
from duck.urls import path
from . import views

urlpatterns = [
    path('/', views.home, name="home"),
]
```

---

### `web/ui/`

Contains all frontend logic — components, pages, templates, and static files.

---

#### `web/ui/pages/`

Duck recommends building UI with **Pages** — Python classes that represent full HTML pages. Pages unlock the [Lively Component System](https://docs.duckframework.com/main/lively-components), which enables fast navigation and real-time interactivity without JavaScript or full page reloads.

**What is an HTML Component?**

A component is a Python class that represents an HTML element. You configure it with props and style, then render it to HTML.

```py
from duck.html.components import InnerComponent

class Button(InnerComponent):
    def get_element(self):
        return "button"

btn = Button(text="Hello world")

print(btn.render())  # <button>Hello world</button>
```

Duck ships with many built-in components — `Button`, `Navbar`, `Modal`, `Input`, and more — available under `duck.html.components`.

**Creating Pages**

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

**Using Pages in views:**

```py
# web/views.py
from duck.shortcuts import to_response

def home(request):
    return to_response(HomePage(request))
```

> Pages automatically enable fast client-side navigation via Lively. Unlike templates, switching between pages does not trigger a full reload.

---

#### `web/ui/components/`

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

---

#### `web/ui/templates/`

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

#### `web/ui/static/`

This directory contains all the static files like css/js files, images or videos for your application.

> Instead of hard-coding static file URLs in components or templates, use the `static` function in `duck.shortcuts` module.

```py
# views.py
from duck.shortcuts import static

def home(request):
    # Instead of:
    my_image_url = "/static/images/my-image.png"
    
    # Do this instead:
    my_image_url = static("images/my-image.png")
    
    return "Hello world" # Anything here.
```

> The same applies with hard-coding internal URLs, use the `resolve()` function in `duck.shortcuts`.

---

## Django Integration

If you have an existing **Django** project and want production features like **HTTPS**, **HTTP/2**, and **resumable downloads**, Duck makes it easy.  

Unlike `nginx` setups, **Duck** simplifies this with a few commands.

### Benefits

- Native [HTTP/2 & HTTPS](https://docs.duckframework.com/main/https-and-http2) implementation. 
- Extra built-in security [middleware](https://docs.duckframework.com/main/middlewares) (DoS, SQLi, etc.)  
- Duck and Django run in the same Python environment (faster communication)  
- Auto-compressed responses  
- Resumable large downloads  
- Fast and [Reactive Lively components](https://docs.duckframework.com/main/lively-components) - for beautiful & responsive UI.
- [Free SSL with renewal](https://docs.duckframework.com/main/free-ssl-certificate)
- and more

### Usage

```sh
duck makeproject myproject
cd myproject
duck django-add "path/to/your/django_project"
duck runserver -dj
```

### Notes:

- Follow instructions provided by `django-add` command carefully  
- Make sure your Django project defines at least one `urlpattern`
- Once setup, you’re good to go!

---

## Useful Links

1. [Official Website](https://duckframework.com)    
2. [Documentation](https://docs.duckframework.com)
3. [Lively UI Documentation](https://docs.duckframework.com/main/lively-components)

---

## 🚀 Premium Duck Components Coming Soon!
>  
> All our UI components are currently free and open source. Stay tuned for upcoming Pro Packs featuring advanced dashboards, e-commerce, and integrations!
>
> ⭐ Star this repo to get notified on release!


## Contributing & Issues

**Duck** is open to all forms of contribution — financial or technical.

### Sponsorship/Donations:  

Support development on [Patreon](https://patreon.com/duckframework)  

### Report issues:  

Use the [GitHub Issues page](https://github.com/duckframework/duck/issues)

---

> **Duck is updated regularly** — check the repo for improvements and bug fixes.
