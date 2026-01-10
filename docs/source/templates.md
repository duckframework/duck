# 📑 Templates

Templates in Duck are used to generate dynamic HTML responses by combining **static markup** with **runtime data** (context).  
They are typically rendered inside views and returned as HTTP responses.

Duck provides first-class support for two popular templating engines:

- **Django Templates** — familiar, batteries-included, and tightly structured
- **Jinja2** — flexible, expressive, and widely used across Python ecosystems

You can freely choose which engine to use per render call.

---

## 🛠️ Rendering Functions

Duck exposes template rendering helpers through the 'duck.shortcuts' module.  
These helpers abstract engine selection, context injection, and response creation.

### Available Functions

1. **'render'**  
   The default rendering function.  
   - Supports both **Django** and **Jinja2**
   - Engine selection is controlled via the 'engine' argument

2. **'django_render'**  
   Explicitly renders templates using the **Django** template engine.

3. **'jinja2_render'**  
   Explicitly renders templates using the **Jinja2** engine.

4. **'async_render'**  
   Asynchronous equivalent of 'render'.  
   - Designed for async views
   - Behavior and arguments match 'render'

---

## ⚙️ Template Syntax

Duck does not introduce a custom template language.  
Instead, it fully embraces the native syntax of each supported engine.

---

### 1️⃣ Django Template Syntax

Django templates use a tag-based syntax with filters and template inheritance.

```django
<h1>Hello {{ user.username }}</h1>

{% if user.is_authenticated %}
    <p>Welcome back!</p>
{% else %}
    <p>Please log in.</p>
{% endif %}
```

📖 Learn more:  
[Django Template Language Documentation](https://docs.djangoproject.com/en/6.0/topics/templates/)

---

### 2️⃣ Jinja2 Template Syntax

Jinja2 templates are expressive and Pythonic, with powerful control structures.

```jinja
<h1>Hello {{ user.username }}</h1>

{% if user.is_authenticated %}
    <p>Welcome back!</p>
{% else %}
    <p>Please log in.</p>
{% endif %}
```

📖 Learn more:  
[Jinja2 Template Documentation](https://jinja.palletsprojects.com/en/stable/templates/)

---

## 📌 Template Locations

By default, Duck looks for templates in the global directory:

```
web/ui/templates
```

This directory is shared across the entire application.

### Customizing Global Template Paths

You can override or extend global template directories by configuring:

```python
GLOBAL_TEMPLATE_DIRS
```

inside your `settings.py` file.

---

## 🧪 Rendering Templates in Views

### Synchronous View Example

```python
from duck.shortcuts import render

def sync_view(request):
    context = {
        'title': 'Home',
    }
    return render(request, 'template.html', context, status_code=200)
```

---

### Asynchronous View Example

```python
from duck.shortcuts import async_render

async def async_view(request):
    context = {
        'title': 'Home',
    }
    return await async_render(request, 'template.html', context, status_code=200)
```

---

## 📗 Blueprint Templates

Duck supports **template isolation per blueprint**, making large applications easier to organize.

### How Blueprint Templates Work

- Each blueprint can expose its own template directory
- By default, all blueprints are enabled for template rendering
- Templates must live inside a 'templates/' directory within the blueprint path

### Template Resolution

To render a blueprint template:
- Prefix the template path with the blueprint name

**Example structure:**
```
docs/
├── templates/
│   └── index.html
```

**Rendered as:**
```
docs/index.html
```

---

### Blueprint Rendering Example

```python
from duck.shortcuts import render, async_render

def sync_view(request):
    return render(
        request,
        'some_blueprint/template.html',
        context={},
        status_code=200,
    )

async def async_view(request):
    return await async_render(
        request,
        'some_blueprint/template.html',
        context={},
        status_code=200,
    )
```

This approach keeps templates:
- Modular
- Reusable
- Cleanly separated by application domain

---

## ✅ Summary

- Duck supports **Django** and **Jinja2** templates out of the box
- Rendering helpers live in 'duck.shortcuts'
- Templates can be global or blueprint-scoped
- Both sync and async rendering are supported
- No custom syntax — use native engine features

---

👉 **Next:** Learn how to extend templates with [🏷️ Template Tags](./templatetags.md)
