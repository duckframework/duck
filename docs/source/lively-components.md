# 🖥️ Lively Component System

![Badge](https://img.shields.io/badge/feature-Lively_Components-blue)

**Duck** now includes the **Lively Component System**—a real-time, component-based system that enables responsive page updates without full reloads.  
It leverages **WebSockets with msgpack** for fast communication and supports navigation to new URLs without full page reloads.

> Recommended: Use Duck components over traditional templates. Components are flexible, Pythonic, and allow pluggable, reusable UI elements.

---

## 🚀 What Is the Lively Component System?

The **Lively Component System** is Duck’s way of building interactive web pages using pure Python.

Instead of writing JavaScript for buttons, forms, or live updates, you write Python classes. Duck automatically handles the real-time communication between the browser and the server for you.

Think of it like this:

> You write Python.  
> Duck makes the browser react instantly.

---

## 🤔 What Problem Does It Solve?

Normally, web apps need:

- HTML for structure  
- CSS for styling  
- JavaScript for interactivity  
- A backend language for logic  

With Lively Components, you can:

- Define UI elements in Python  
- Attach event handlers in Python  
- Update the page dynamically  
- Avoid writing JavaScript for most interactions  

The system keeps the page updated without full reloads.

---

## ⚙️ How It Works (Simple Explanation)

1. You create a **Page class** in Python.
2. You add components (like buttons, text, forms).
3. You attach Python functions to events (like button clicks).
4. When a user interacts with the page:
   - The browser sends the event to the server.
   - Your Python function runs.
   - Only the changed parts of the page update.

This feels similar to React or other reactive frameworks — but controlled from Python.

---

## 💡 Why It’s Powerful

- Real-time updates without manual JavaScript
- Cleaner architecture (UI + logic in one place)
- Fast navigation between pages
- Component reuse
- Built-in lifecycle handling

---

## 🧠 Beginner Mental Model

If you’re new, think of it like this:

- A **Page** = a screen  
- A **Component** = a piece of UI (button, text, input)  
- An **Event** = something the user does (click, type)  
- Your Python method = what should happen next  

And Duck handles the browser synchronization automatically.

---

## 📄 Page Component Example

```py
from duck.html.components.page import Page
from duck.html.components.button import Button

class HomePage(Page):
    def on_create(self):
        super().on_create()
        self.set_title("Home - MySite")
        self.set_description("Welcome to MySite, the premier platform...")
        self.set_favicon("/static/favicon.ico")
        self.set_opengraph(
            title="Home - MySite",
            description="Welcome to MySite, the premier platform...",
            url="https://mysite.com",
            image="https://mysite.com/og-image.png",
            type="website",
            site_name="MySite"
        )
        self.set_twitter_card(card="summary_large_image", title="Home - MySite")
        self.set_json_ld({
            "@context": "https://schema.org",
            "@type": "WebSite",
            "url": "https://mysite.com",
            "name": "MySite",
            "description": "Welcome to MySite, the premier platform..."
        })
        self.add_to_body(Button(text="Hello world"))
```

> Organizing pages this way isolates page-specific logic in dedicated classes, making code easier to maintain, extend, and debug.

---

## 🖱️ Component Events

**Lively** components allow binding Python handlers to events like button clicks—no JS needed.

```py
from duck.shortcuts import to_response
from duck.html.components.button import Button
from duck.html.components.page import Page
from duck.html.core.websocket import LivelyWebSocketView
from duck.html.core.exceptions import JSExecutionError, JSExecutionTimedOut


async def on_click(btn: Button, event: str, value: Any, websocket: LivelyWebSocketView):
    """
    Button onclick event.
    
    Args:
        btn (Button): Button component.
        event (str): Event name.
        value (str): Current button value.
        websocket (LivelyWebSocketView): Active WebSocket.
    """
    btn.bg_color = "red" if btn.bg_color != "red" else "green"
    try:
        await websocket.execute_js(
            code='alert(`Javascript execution success`);',
            timeout=2,
            wait_for_result=True
        )
    except (JSExecutionTimedOut, JSExecutionError):
        pass

def home(request):
    page = Page(request)
    btn = Button(id="some-id", text="Hello world", bg_color="green", color="white")
    page.add_to_body(btn)
    btn.bind("click", on_click)
    return to_response(page) # Or just return page if you don't want control over response.
```

> Use `update_targets` when multiple components must update on an event to avoid redundant updates.

### Document-specific events

These are events bound directly to the `document` rather than HTML elements. **Duck** provides a way to bind to these events
but it's only available on `Page` component instances. 

**Here is an example:**  

```py
# views.py
from duck.html.components.page import Page

def home(request):
    page = Page(request)
    
    def on_navigation(page, *_):
        print(f"Navigated to page {page}")
    
    def on_page_load(page, *_):
        print(f"Page loaded, {page}")
        
    # Bind to the document.    
    page.document_bind("DuckNavigated", on_navigation, update_self=False)
    page.document_bind("DOMContentLoaded", on_page_load, update_self=False)
    return page
```

---

## ⚡ Fast Navigation

- URL paths returning **Component responses** allow vdom-diffing for minimal DOM updates.
- Use `duckNavigate` for fast page navigation.
- All links do partial page reload whenever possible. Exempt links from partial page reloading by setting `data-no-duck` attribute.
- The default `window.open` has been altered to use fast navigation whenever possible.
- Whenever a user want to visit a next page, whenever possible, fast navigation is used. If you want to override this, let's say you want the user to
   apply new page headers, you can set `fullpage_reload` or `fullpage_reload_headers (_headers that force a fullpage reload when set on Page's request_)` on `Page` components.

---

## ⏱️ Pre-rendering Components

Pre-rendering caches component outputs for faster loading.  

**Example:**
```py
from duck.html.components.page import Page
from duck.shortcuts import to_response

def home(request):
    page = Page(request=request)
    background_thread.submit_task(
        lambda: page.pre_render(deep_traversal=True, reverse_traversal=True)
    )
    return to_response(page)
```

---

## Counter App

Include the built-in counter **blueprint** to test:

```py
BLUEPRINTS = [
    "duck.etc.apps.counterapp.blueprint.CounterApp",
]
```

Visit `/counterapp` after adding it.

---

## 📝 Notes

- Component responses maximize the benefits of Lively Component System.
- Fast navigation works best with component responses in views.

---

## Components in Templates

Components can be used in **Jinja2** and **Django** templates.

**Jinja2 Example:**

```jinja
{{ Button(
      id="btn",
      text="Hello world",
    )
}}
```

**Django Example:**

```django
{% Button %}
    id="btn",
    text="Hello world",
{% endButton %}
```

> Only add components to `TEMPLATE_HTML_COMPONENTS` in [settings.py](settings.md) for template usage.

---

## 🏗️ Custom Components

```py
from duck.html.components import InnerComponent
from duck.html.components.button import Button
from duck.shortcuts import to_response

class MyComponent(InnerComponent):
    def get_element(self):
        return "div"

    def on_create(self):
        super().on_create()
        self.add_child(Button(text="Hi there"))

def home(request):
    comp = MyComponent(request=request)
    return to_response(comp)
```

---

## 🔌 Component Extensions

Extensions enhance component functionality.

```py
from duck.html.components.button import Button
from duck.html.components.extensions import Extension

class MyExtension(Extension):
    def apply_extension(self):
        super().apply_extension()
        self.style["background-color"] = "red"

class MyButton(MyExtension, Button):
    pass

btn = MyButton() # Button with background-color "red"
```

**Notes:**
- By default, all **Lively** components comes up with 2 builtin component extensions as follows:
  - **BasicExtension:** This is the basic extension which enables setting attributes like `color`, `bg_color` & more to actually alter the component `style`.
  - **StyleCompatibilityExtension:** This enables compatibility of style properties like setting `backdrop-filter` will also set the `-webkit-backdrop-filter` and other compatibility style properties.

---

## 📦 Predefined Components

All predefined components are available in `duck.html.components` and in default `SETTINGS['TEMPLATE_HTML_COMPONENTS']`.

> Use these components to rapidly build responsive, interactive UIs in **Duck**.

---

## Force Updates on Lively Components

It is possible to modify values set with `Javascript` with the use of `Force updates`.  

**The following example will showcase this technique:**

```py
from duck.html.components import ForceUpdate
from duck.html.components.button import Button
from duck.html.components.script import Script


def on_btn_click(btn, *_):
    # Return a force update to reset btn text to the initial text set on btn
    # First argument to ForceUpdate is the component and second is list of updates.
    # List of updates are "text"/"inner_html", "props", "style" and "all".
    return ForceUpdate(btn, ["text"])

    
def home(request):
    btn = Button(text="Click me", id="btn")
    
    # Add some Javascript
    script = Script(
        inner_html="""
        function btnClick() {
          const btn = document.getElementId(`btn`);
          btn.textContent = "Clicking..";
        }
        """
    )
    
    # Add script to button
    btn.add_child(script)
    
    # Add a javascript callback to click event.
    # This always gets called first before Duck event callback.'
    btn.props["onclick"] = "btnClick()"
    
    # Bind click event to python callable.
    btn.bind("click", on_btn_click, update_self=False)
    
    # Return btn, will be converted to response by Duck.
    return btn
```

## Handling Forms

**Duck** has got an easy mechanism you can use to easily handle form data.

### Example:

```py
from duck.html.components.form import Form
from duck.html.components.input import Input
from duck.html.components.fileinput import FileInput


def on_form_submit(form, event, value: dict, _):
    name = value.get("name")
    email = value.get("email")
    file_metadata: dict = value.get("file") # Only file metadata will be resolved.
    
    # Do something with the form data, maybe validation

def home(request):
    form = Form(
        fields=[
            Input(type="text", name="name", placeholder="Name"),
            Input(type="email", name="email", placeholder="email"),
            FileInput(name="file"),
        ],
    )
    
    # Bind an event to form submission
    form.bind("submit", on_form_submit)
    
    # Return form or any parent
    return form
```

From the above example, whenever `submit` event is bound to a component, 
the JS method `preventDefault()` is called to avoid page reload.  

Also, only file metadata (size, type & name) is received on `submit` event because `Lively` is not designed
to handle file uploads. You need to manually call internal api's or views for file uploads and update the UI 
if complete. One case you can do this is that you may execute JS for doing an `AJAX` request and update
the UI once the response is received.


## Component Lifecycle

Whenever each component is created or added to the component tree, the following methods are executed:

### `on_root_finalized`:

This will be called whenever a root component is finalized, meaning it is never going to change. Use the for doing staff on root components e.g.,
using `document_bind` on `Page` components.  

*Args:*
- **root:** This is the root component.    
        
### on_parent

Called whenever a child component is added to a parent component.  

*Args:*
 - **parent:** The parent component.

## Other points to Note

- **Duck** only keeps track of `props` (attributes) and `style` (style attributes) that are initially set using **Duck**. 
  This means that **Duck** will not touch any prop or style attributes set soley using **Javascript** and are never declared on 
   **Lively** components.
- The `value` argument parsed to a **Duck** event handler is variable and can be any datatype depending on the event.  
- Component traversal can be done using `root`, `parent` or `children` properties.
- JS execution is done asynchronously so all code that is parsed in `LivelyWebSocketView.execute_js` or `get_js_result` is awaited by default.
- DOM mutation/updates using Javascript like moving, adding or removing components without using **Lively** will cause issues and by default, 
  this will be flagged in the browser.
