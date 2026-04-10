# 🚀 Getting Started with Duck

*Simple. Powerful. Reactive web apps in pure Python — no JavaScript, no extra tools.*  

This guide will get you from **zero ➝‬ running app ➝‬ understanding structure** in a few minutes.

---

## 1. Install Duck

```bash
pip install duckframework
```

---

## 2. Create Your First Project

```bash
duck makeproject myproject
cd myproject
```

---

## 3. Run the Server

```bash
duck runserver # Or use python3 web/main.py
```

Open your browser:

``` 
http://localhost:8000
```

🎉 Your Duck app is now running.

---

## 4. Understand the Project Structure

Duck keeps things organized but simple. The most important files are:

``` 
web/
 ├── main.py
 ├── urls.py
 └── views.py
```

Let’s break them down 👇

---

## web/main.py ➝‬ Entry Point (starts your app)

```python
#!/usr/bin/env python
"""
Main py script for application creation and execution.
"""

from duck.app import App

app = App(port=8000, addr="0.0.0.0", domain="localhost")

if __name__ == "__main__":
    app.run()
```

### What it does:

- Creates your Duck application (`App`)
- Configures server settings (port, address, domain)
- Starts the server with `app.run()`

👉 Think of this as: **"booting up your backend"**

---

## web/urls.py ➝‬ URL Routing (maps URLs to logic)

Example:

```python
from duck.urls import path
from . import views

urlpatterns = [
    path("/", views.home),
]
```

### What it does:

- Defines **which URL calls which function**
- Connects user requests ➝‬ your code

👉 Example:

- Visiting `/` ➝‬ calls `views.home`

---

## web/views.py ➝‬ Logic (what your app does)

Example:

```python
def home():
    return "Hello, Duck 🦆"
```

### What it does:

- Contains your **business logic**
- Returns responses (text, JSON, HTML, etc.)

👉 This is where you build your app behavior

---

## How Everything Connects

When a user visits your app:

1. Duck server starts (`main.py`)
2. Request comes in (e.g. `/`)
3. `urls.py` decides which function to call
4. `views.py` runs the logic
5. Response is returned to the browser

👉 That’s the full request flow.

---

## Run Built-in Tests

```bash
duck runtests
```

Use verbose mode if needed:

```bash
duck runtests -v
```

---

## Requirements

- Python **3.10+**

---

## What Makes Duck Different?

With most frameworks, you need extra tools like:

- Reverse proxy (NGINX)
- App server (Gunicorn)
- SSL setup

👉 Duck handles these **out of the box**.

---

## Final Thought

Duck is designed to be:

- Simple to start 🧠
- Powerful to scale ⚡
- Flexible to control 🧩

Start small. Explore the files. Build something real.

Welcome to Duck.
