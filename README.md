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
[![Auto Reload](https://img.shields.io/badge/AutoReload-DuckSight-yellow.svg)](#)
[![Django Integration](https://img.shields.io/badge/Django-Integration-blue.svg)](#)
[![Monitoring](https://img.shields.io/badge/Monitoring-CPU%2FRAM%2FDisk%2FI%2FO-brightgreen.svg)](#)

**Duck Framework** is an open-source Python web framework and web server with a built-in reactive UI engine and real-time WebSocket support.

Build high-performance, scalable, server-side reactive web applications — without a separate frontend framework or a complex JavaScript stack.

---

## Real-World Apps Built With Duck

1. [Snip — URL Shortener](https://snip.duckframework.com)
2. [Quill — AI Design Generator](https://quill.duckframework.com)
3. [Counter — Simple Counter App](https://duckframework.com/counterapp)

---

## Duck Framework Features

### 🚀 Build Faster, Ship Sooner

1. Dynamic project generation with `makeproject` (`mini`, `normal`, or `full`)
2. Easy integration with existing **Django** projects via the [`django-add`](https://docs.duckframework.com/main/django-integration) command
3. Organized routing with Duck [`Blueprints`](https://docs.duckframework.com/main/blueprint)
4. Built-in web development tools and helpers
5. [**MCP (Model Context Protocol) server**](https://docs.duckframework.com/main/mcp) — make it easy to build MCP servers for seamless AI communication
6. [**Builtin Dashboard**](https://docs.duckframework.com/main/dashboard) — tailor interfaces to your workflow and preferences
7. [Official MCP Server](https://duckframework.com/blog/official-duck-framework-mcp-server-now-available) at https://duckframework.com/mcp

### ⚡ Reactive & High Performance

1. [**Lively Component System**](https://docs.duckframework.com/main/lively-components) with `VDom diffing` for fast UI updates
2. [**WebSocket support**](https://docs.duckframework.com/main/websocket) — a modern implementation with per-message compression
3. **Component mutation observer** — an optional mutation observer to track child changes for faster re-renders (75x faster on unchanged children)
4. Automatic **content compression** using `gzip`, `deflate`, or `brotli`
5. Support for **chunked transfer encoding**
6. High performance with low-latency response times
7. **Resumable downloads** for large files
8. **Worker processes/threads** — use worker processes/threads to utilize all available CPU cores for improved request handling

### 🌐 Modern Web Platform

1. [**Built-in HTTPS support**](https://docs.duckframework.com/main/https-and-http2) for secure connections
2. **Native HTTP/2 support** with **HTTP/1** backward compatibility — [details](https://docs.duckframework.com/main/https-and-http2)
3. Hassle-free **free SSL certificate generation** with **automatic renewal** — [details](https://docs.duckframework.com/main/free-ssl-certificate)
4. [**Free production SSL**](https://docs.duckframework.com/main/free-ssl-certificate) — no certificate costs
5. **Automatic SSL renewal** using `certbot` plus Duck's automation system
6. Runs on both [`WSGI`](https://docs.duckframework.com/main/wsgi) and [`ASGI`](https://docs.duckframework.com/main/asgi) — can even serve async protocols like `HTTP/2` or WebSockets over WSGI
7. Full support for **async views** and asynchronous code, even in a [`WSGI`](https://docs.duckframework.com/main/wsgi) environment

### 🔒 Secure by Default

1. Protection against **DoS**, **SQL injection**, **command injection**, and other threats
2. **JWT (JSON Web Token) authentication** — persistent logins via [JWT](https://docs.duckframework.com/main/jwt).

### ⚙️ Automation & Operations

1. Built-in [task automation](https://docs.duckframework.com/main/automations) — no need for [cron jobs](https://en.m.wikipedia.org/wiki/Cron)
2. [Log management](https://docs.duckframework.com/main/logging) via `duck logs`, with file-based logging by default
3. Real-time [system monitoring](https://docs.duckframework.com/main/monitoring) for CPU, RAM, disk usage, and I/O activity via `duck monitor`
4. Built-in [dashboard](https://docs.duckframework.com/main/dashboard) for monitoring requests, latency, and system metrics
5. Instant sitemap generation via [`duck sitemap`](https://docs.duckframework.com/main/sitemap), or the built-in [`duck.etc.blueprints.essentials.blueprint.Sitemap`](https://docs.duckframework.com/main/sitemap) blueprint for dynamic, cached sitemap serving
6. **Auto-reload** in debug mode for rapid development

### 🏗️ Scalable Architecture

1. Independent [microapps](https://docs.duckframework.com/main/microapp) that run on their own servers, for microservices support
2. Highly **customizable** to fit any use case

---

## Upcoming Features

1. **HTTP/3 with QUIC** — faster, modern transport for improved performance
2. **QUIC WebTransport** — a next-gen alternative to WebSockets for real-time communication
3. **Component pre-rendering system** — preload components on a background thread to reduce initial load times of component trees
4. **MQTT (Message Queuing Telemetry Transport) integration** — run your own broker and manage IoT devices with ease
5. **Duck WebApp ➝ APK** — easily convert a Duck web application to an APK
6. **DuckSight hot reload** — hot reload for the DuckSight Reloader instead of a full reload on file changes, for faster, more efficient dev cycles
7. **Internal updates** — securely list and apply updates using cryptographic code signing (e.g. TUF) to verify GitHub-sourced updates, protecting against rollbacks and man-in-the-middle attacks
8. **Complete reverse proxy server** — Duck currently proxies only Django; the goal is a full-fledged reverse proxy server with optional sticky sessions
9. **...and more** — [request a feature](./feature_request.md)

---

## Fun Facts

- The official **Duck** website is powered by the **Duck** framework itself — true dogfooding.
- [**Duck's Lively components**](https://docs.duckframework.com/main/lively-components) deliver a fast, responsive UI that eliminates slow page re-renders for a seamless user experience.

---

## AI Guidelines

Guidelines for AI agents and assistants working with Duck Framework live in the [`ai/`](./ai) directory:

- [`ai/DUCK_PROJECT_GUIDE.md`](./ai/DUCK_PROJECT_GUIDE.md) — project structure, conventions, and general coding rules
- [`ai/HTML_COMPONENTS_GUIDE.md`](./ai/HTML_COMPONENTS_GUIDE.md) — component/UI building guide

### Vibe Coding

When vibe-coding with Duck Framework, point your AI assistant to the `ai/` directory, or provide its files directly, for best results.

**Example prompts:**
```
Using the guidelines in the `ai` directory of https://github.com/duckframework/duck, create a project named `xyz`.
Using the guidelines in the `ai` directory of https://github.com/duckframework/duck, improve my project `xyz`.
Using the guidelines in the `ai` directory of https://github.com/duckframework/duck, improve my project UI — make it modern and beautiful.
```

---

## Getting Started

**Install the latest version from GitHub:**

```sh
pip install git+https://github.com/duckframework/duck.git
```

**Or install from PyPI:**

```sh
pip install duckframework
```

---

## Project Creation

```sh
duck makeproject myproject
```

This creates a `normal` project named `myproject`. You can also create other project types:

- `--full` — a full-featured project
- `--mini` — a simplified starter project

### Full Project

Includes everything Duck offers. Recommended for experienced developers.

```sh
duck makeproject myproject --full
```

### Mini Project

Beginner-friendly, with essential functionality only.

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

This starts the server at **http://localhost:8000**.

Duck serves a basic site by default — explore more in the [documentation](https://docs.duckframework.com/main).

---

## Understanding the Project

Duck generates a set of files and directories as you build your application. This section walks through the core ones you'll interact with most.

### `web/main.py`

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

### `web/views.py`

An optional file for organizing your view functions. Import it as a module in `urls.py` to keep your routes clean.

```py
# web/urls.py
from duck.urls import path
from . import views

urlpatterns = [
    path('/', views.home, name="home"),
]
```

### `web/ui/`

Contains all frontend logic — components, pages, templates, and static files.

#### `web/ui/pages/`

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

## Django Integration

If you have an existing Django project and want production features like HTTPS, HTTP/2, and resumable downloads, Duck makes it easy — no `nginx` setup required.

### Benefits

- Native [HTTP/2 & HTTPS](https://docs.duckframework.com/main/https-and-http2) implementation
- Extra built-in security [middleware](https://docs.duckframework.com/main/middlewares) (DoS, SQLi, etc.)
- Duck and Django run in the same Python environment for faster communication
- Auto-compressed responses
- Resumable large downloads
- Fast, [reactive Lively components](https://docs.duckframework.com/main/lively-components) for a beautiful, responsive UI
- [Free SSL with auto-renewal](https://docs.duckframework.com/main/free-ssl-certificate)
- And more

### Usage

```sh
duck makeproject myproject
cd myproject
duck django-add "path/to/your/django_project"
duck runserver -dj
```

### Notes

- Follow the instructions provided by the `django-add` command carefully.
- Make sure your Django project defines at least one `urlpattern`.
- Once set up, you're good to go!

---

## Useful Links

1. [Official Website](https://duckframework.com)
2. [Blog](https://duckframework.com/blog)
3. [Documentation](https://docs.duckframework.com)
4. [Lively UI Documentation](https://docs.duckframework.com/main/lively-components)

---

## 🚀 Premium Duck Components Coming Soon!

All UI components are currently free and open source. Stay tuned for upcoming Pro Packs featuring advanced dashboards, e-commerce, and integrations!

⭐ Star this repo to get notified on release!

---

## Contributing & Issues

**Duck** is open to all forms of contribution — financial or technical.

### Sponsorship / Donations

Support development on [Patreon](https://patreon.com/duckframework).

### Report Issues

Use the [GitHub Issues page](https://github.com/duckframework/duck/issues).

---

> **Duck is updated regularly** — check the repo for improvements and bug fixes.
