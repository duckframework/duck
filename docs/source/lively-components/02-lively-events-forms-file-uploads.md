# Lively / HTML Components — Part 2: Events, Forms & File Uploads

> **Series index:**
> - Part 1 — Overview & Page Basics (`01-lively-overview-and-page-basics.md`)
> - **Part 2 — Events, Forms & File Uploads** *(this file)*
> - Part 3 — Advanced Rendering, Templates & Reference (`03-lively-advanced-rendering-and-reference.md`)

---

## Component Events

**Lively** components allow binding Python handlers to events like button clicks — no JS needed.

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
        # Execute some JS directly
        await websocket.execute_js('alert(`Javascript execution success`);')
    except (JSExecutionTimedOut, JSExecutionError):
        pass

def home(request):
    page = Page(request)
    
    # Create and add button to page
    btn = Button(id="some-id", text="Hello world", bg_color="green", color="white")
    page.add_to_body(btn)
    
    # Bind an event to Python handler
    btn.bind("click", on_click)
    return to_response(page) # Or just return page if you don't want control over response.
```

> Use `update_targets` when multiple components must update on an event to avoid redundant updates.

### Document-Specific Events

These are events bound directly to the `document` rather than HTML elements. **Duck** provides a way to bind to these events but it's only available on `Page` component instances.

**Here is an example:**

```py
# views.py
from duck.contrib.sync import ensure_async
from duck.html.components.page import Page

from web.services.some_module import fetch_db_items


def home(request):
    page = Page(request)

    def on_navigation(page, event, path, websocket):
        # Called whenever the browser navigates to a page.
        print(f"Navigated to page {page}")

    def on_back_navigation(page, event, path, websocket):
        # Called when the user returns to a page using browser history
        # (for example, the Back button).
        print(f"Back navigated to page {page}")

    async def on_page_load(page, event, _, websocket):
        # Called only when a page is loaded for the first time.
        # Not called when returning to a page via browser history.
        print(f"Page loaded: {page}")

        # Fetch data that should only be loaded on the initial page load.
        items = await ensure_async(fetch_db_items)()

    # Listen for document navigation events.
    page.document_bind("DuckNavigated", on_navigation, update_self=False)
    page.document_bind("DuckBackNavigated", on_back_navigation, update_self=False)

    # Listen for the initial page load event.
    page.document_bind("DOMContentLoaded", on_page_load, update_self=False)
    
    # Return page.
    return page
```

---

## Automatic Event Binding

You can now bind events directly when creating components using the `event_handlers` argument:

```python
Button(
    event_handlers=[
        {
            "click": self.on_click,
            "update_self": False,
            "update_targets": [self],
            **extra_kwargs,
        }
    ]
)
```

For document-level events such as `DOMContentLoaded`, use `document_event_handlers` on `Page`:

```python
Page(
    document_event_handlers=[
        {
            "DOMContentLoaded": self.on_loaded,
            **extra_kwargs,
        }
    ]
)
```

Both `event_handlers` and `document_event_handlers` accept additional keyword arguments that are forwarded to their respective bind methods.

---

## WebSocket Sync Convention

Any async method that pushes state to the client over an active WebSocket connection uses a `ws_` prefix (e.g. `ws_sync`, `ws_open`, `ws_dismiss`). Plain methods (`set_*`, `show_*`, or any other state mutator) only update local component state and rely on Duck's end-of-handler diffing to sync automatically — no `ws_` prefix, no async.

Use `ws_` methods only when the UI must update before the handler returns — e.g. before a slow operation, or to trigger a raw JS class toggle that Duck's diffing can't reach. Otherwise, prefer plain state mutators and let diffing handle the sync.

```python
# Prefer this when possible — no ws needed.
component.show_error("Something went wrong")

# Use ws_ only when you need immediate feedback.
component.show_info("Uploading...")

await component.ws_open(ws)
```

---

## Handling Forms

**Duck** has an easy mechanism you can use to easily handle form data.

### Example

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

From the above example, whenever a `submit` event is bound to a component, the JS method `preventDefault()` is called to avoid page reload.

Also, only file metadata (size, type & name) is received on the `submit` event because `Lively` is not designed to handle file uploads. You need to manually call internal APIs or views for file uploads and update the UI once complete. One way to do this is to execute JS for an `AJAX` request and update the UI once the response is received.

---

## File Uploads in Lively

Lively supports requesting file uploads from the client directly inside event handlers via `ws_request_file`. When called, it waits for the user to select a file on the target input and uploads it automatically once selected, with progress and status reported back in real time.

### Basic Usage

```python
from duck.html.components.lively_utils.file_request import ws_request_file
from duck.http.fileuploads import FileVerificationError, FileTypeNotAllowedError


async def on_form_submit(..., ws):
    file = await ws_request_file(form_id="...", name="...", ws)

    # Verify file contents - only if allowed_mimes not passed to ws_request_file.
    try:
        file.verify()  # You can pass allowed_mimes here as well
    except (FileVerificationError, FileTypeNotAllowedError):
        # Do something here
        raise

    # Do whatever you want with the file here - maybe saving
    await file.async_save()
```

### Advanced Usage

```python
from duck.html.components.lively_utils.file_request import (
    ws_request_file,
    FileTypeNotAllowedError,
    FileNotSelectedError,
    FileUploadError,
)

async def on_form_submit(..., ws):
    try:
        file = await ws_request_file(form_id="...", name="...", ws, allowed_mimes=["image/png"])

    except TimeoutError:
        # Client did not upload a file in the given timeout
        raise

    except FileTypeNotAllowedError:
        # Do something here
        raise

    except FileNotSelectedError:
        # Do something here
        raise

    except FileUploadError:
        # Catch-all for file upload related exceptions
        raise

    # No file.verify() needed - already called because allowed_mimes was passed
    await file.async_save()
```

### With Real-Time Progress

```python
from duck.html.components.lively_utils.file_request import (
    ws_request_file,
    FileTypeNotAllowedError,
    FileNotSelectedError,
    FileUploadError,
)

async def on_progress(progress):
    # Maybe update UI here
    print(progress)

async def on_form_submit(..., ws):
    try:
        file = await ws_request_file(
            form_id="...", name="...", ws,
            allowed_mimes=["image/png"],
            on_progress=on_progress,
        )

    except TimeoutError:
        raise

    except FileTypeNotAllowedError:
        raise

    except FileNotSelectedError:
        raise

    except FileUploadError:
        raise

    await file.async_save()
```

> **Note:** Exception classes from `duck.http.fileuploads` and `duck.html.components.lively_utils.file_request` refer to the same thing. Run `help(ws_request_file)` to see all available configurations.

---

## Custom Events

You can create custom `Lively` events with `window.LIVELY_APPLICATION.createDuckEvent`, dispatch them like any other DOM event, and bind them on the Python side.

```javascript
// Create a custom event
const event = lively.createDuckEvent("ReportBounds", detail, false, true);

// Fire event at root level
document.dispatchEvent(event);
```

`createDuckEvent(eventName, detailOverrides, addToDuckEvents = true, raw = true)`:

- **`eventName`** — name of the event (e.g. `"ReportBounds"`).
- **`detailOverrides`** — data to attach to the event's `detail`.
- **`addToDuckEvents`** — whether to add the event to Duck's tracked event list.
- **`raw`** — when `true`, Duck skips its default per-field processing (e.g. extracting `value` from a `button`) and passes `detail` through directly.

On the Python side, bind the event by name:

```python
page.document_bind("ReportBounds", on_report_bounds, force_bind=True)
```

`on_report_bounds` receives the event just like any other bound handler — no special handling needed for it being custom.

---

**Next:** Part 3 covers fast navigation, pre-rendering, templates, custom components, extensions, force updates, immediate/diffed syncing, component lifecycle, and other notes.
