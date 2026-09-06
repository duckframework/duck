# Lively / HTML Components — Part 3: Advanced Rendering, Templates & Reference

> **Series index:**
> - Part 1 — Overview & Page Basics (`01-lively-overview-and-page-basics.md`)
> - Part 2 — Events, Forms & File Uploads (`02-lively-events-forms-file-uploads.md`)
> - **Part 3 — Advanced Rendering, Templates & Reference** *(this file)*

---

## Fast Navigation

- URL paths returning **Component responses** allow vdom-diffing for minimal DOM updates.
- Use `duckNavigate` for fast page navigation.
- All links do partial page reload whenever possible. Exempt links from partial page reloading by setting the `data-no-duck` attribute.
- The default `window.open` has been altered to use fast navigation whenever possible.
- Whenever a user wants to visit a next page, fast navigation is used whenever possible. If you want to override this — for example, if you want the user to apply new page headers — you can set `fullpage_reload` or `fullpage_reload_headers` (headers that force a full-page reload when set on a `Page`'s request) on `Page` components.

---

## Pre-Rendering Components

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

## Counter App (Demo Blueprint)

Include the built-in counter **blueprint** to test:

```py
BLUEPRINTS = [
    "duck.etc.blueprints.counterapp.blueprint.CounterApp",
]
```

Visit `/counterapp` after adding it.

**Notes:**
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

> Only add components to `TEMPLATE_HTML_COMPONENTS` in `settings.py` for template usage.

---

## Custom Components

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

## Component Extensions

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
- By default, all **Lively** components come with 2 built-in component extensions:
  - **BasicExtension:** The basic extension which enables setting attributes like `color`, `bg_color`, and more, to actually alter the component `style`.
  - **StyleCompatibilityExtension:** Enables compatibility of style properties — e.g. setting `backdrop-filter` will also set `-webkit-backdrop-filter` and other compatibility style properties.

---

## Predefined Components

All predefined components are available in `duck.html.components` and in the default `SETTINGS['TEMPLATE_HTML_COMPONENTS']`.

> Use these components to rapidly build responsive, interactive UIs in **Duck**.

---

## Force Updates on Lively Components

It is possible to modify values set with `Javascript` with the use of **Force updates** or the `ws.update_now` method.

**The following example showcases this technique:**

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
    # Add a javascript callback to click event.
    # This always gets called first before Duck event callback.
    btn = Button(text="Click me", id="btn", props={"onclick": "btnClick()"})
    
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
    
    # Bind click event to python callable.
    btn.bind("click", on_btn_click, update_self=False)
    
    # Return btn, will be converted to response by Duck.
    return btn
```

**Critical rule:** Lively performs **non-destructive syncing**.

It only updates props and styles it is aware of from the server state, and ignores anything it didn't create or track.

- New props/styles set from Python (e.g. in event handlers) will sync normally.
- Props/styles added externally (e.g. via `execute_js`) **are not tracked**.
- Untracked properties will **not be removed or overridden**, even when patches are applied.

This means Lively will **merge updates**, not replace the entire prop/style object.

```python
# Initial render — no background-color
btn = Button(text="Click")

# Later in Python (event handler) — this WILL sync
btn.style.update({"background-color": "red"})
```

```javascript
// Added externally — Lively does NOT track this
element.style.border = "1px solid blue"
```

Even after future updates from Python:

```python
btn.style.update({"background-color": "green"})
```

The `border` style will remain untouched because Lively never tracked it.

### Key Takeaway

Lively behaves like a **partial diff system**, not a full state replacement system:

- ✅ Updates known fields
- ✅ Adds new fields from server-side changes
- ❌ Does not remove unknown/external fields

> **Note:** In cases where a property's presence resolves to `true` regardless of its value — e.g. the presence of `disabled` or `true` — you can just execute JavaScript (using `execute_js`) to alter the component directly.

---

## Immediate Syncing (`update_now`)

```{note}
Added in version 1.1.0
```

Method `update_now` synchronizes the current component state with the client immediately, without waiting for the dispatch loop's final VDOM diff. Unlike deferred updates, this applies changes right away and can be safely called within a component event handler — useful when the client needs to reflect an intermediate state before the handler continues, restores state, or performs longer-running work.

```{note}
This method internally performs a `ForceUpdate`, sending the specified updates unconditionally — even if the resulting state is identical to what the client already has. Use this when you know a change occurred and want to guarantee it reaches the client without paying for a diff.
```

**Example:**

```python
# Immediately sync state before continuing execution
async def on_click(btn, _, __, ws):
    btn.text = "Clicking..."
    await ws.update_now(btn, updates=["text"])

    # Continue processing after UI reflects the change

btn = Button(text="Click me")
btn.bind("click", on_click, update_self=True)
```

---

## Diffed Immediate Syncing (`sync_now`)

```{note}
Added in version 2.3.0
```

Method `sync_now` also synchronizes state with the client immediately from within an event handler, but unlike `update_now`, it **diffs** the component against its own last checkpoint first and sends only the patches that actually changed — no patch is sent for a no-op update. It is scoped to the target component's own subtree, so syncing a deeply nested descendant (e.g. a button inside a page) never re-renders or re-diffs its ancestors.

```{note}
`sync_now` requires the target component to be a descendant of one of the event's `update_targets` (or an `update_target` itself). Calling it on an unrelated component raises a `ForceUpdateError`.
```

**Example:**

```python
# Diff and sync only if the state actually changed
async def on_click(btn, _, __, ws):
    btn.text = "Clicking..."
    await ws.sync_now(btn)

    # Continue processing after UI reflects the change, with no
    # patch sent at all if btn.text ends up unchanged by handler's end

btn = Button(text="Click me")
btn.bind("click", on_click, update_self=True)
```

### `sync_now` vs `update_now`

| | `update_now` | `sync_now` |
|---|---|---|
| Sends a patch | Always, unconditionally | Only if state actually changed |
| Cost | Skips diffing — cheaper per call if you're certain state changed | Diffs first — avoids wasted network writes on no-ops |
| Scope | Whatever component/updates you pass | Automatically scoped to the target's own subtree |
| Best for | Small, definitely-changed components where a diff isn't worth the CPU | Any case with risk of a no-op, or when targeting a nested descendant without touching its ancestors |

---

## Component Lifecycle

Whenever each component is created or added to the component tree, the following methods are executed:

### `on_root_finalized`

Called whenever a root component is finalized, meaning it is never going to change. Use this for doing tasks on root components, e.g. using `document_bind` on `Page` components.

*Args:*
- **root:** This is the root component.

### `on_parent`

Called whenever a child component is added to a parent component.

*Args:*
- **parent:** The parent component.

---

## Other Points to Note

- **Duck** only keeps track of `props` (attributes) and `style` (style attributes) that are initially set using **Duck**. This means that **Duck** will not touch any prop or style attribute set solely using **Javascript** that is never declared on **Lively** components.
- The `value` argument passed to a **Duck** event handler is variable and can be any datatype depending on the event.
- Component traversal can be done using the `root`, `parent`, or `children` properties.
- JS execution is done asynchronously, so all code that is passed in `LivelyWebSocketView.execute_js` or `get_js_result` is awaited by default.
- DOM mutation/updates using Javascript — like moving, adding, or removing components without using **Lively** — will cause issues and, by default, will be flagged in the browser.
