# 🗨️ Build a Reactive Chat App in 5 Minutes

No heavy frontend JavaScript. No "where do I even start?" confusion.  
You'll build a working, reactive chat UI using **Duck Lively Components** — in pure Python.

## What you'll get

By the end:

- A **chat page** with a scrollable message list
- A **send form** that updates the UI instantly
- A **message bubble component** (reusable)
- Auto-refresh so messages appear without a full page reload

---

## Project structure

You'll create these files:

```
web/ui/
├── components/
│   └── message_bubble.py  # Reusable message display
├── pages/
│   ├── base.py   # Shared page layout
│   └── chat.py    # The chat page + logic
└── web/urls.py  # Routes
└── (other files)
```

---

## Step 1 — Message Bubble Component

This is a reusable UI component that displays a single message.

Create: `web/ui/components/message_bubble.py`

```python
"""
Message bubble component for displaying chat messages.
"""

from duck.html.components.container import Container
from duck.html.components.label import Label
from duck.html.components.paragraph import Paragraph


class MessageBubble(Container):
    """
    A chat message bubble displaying username and message text.

    Args:
        username: Name of the user who sent the message.
        text: The message content.
    """

    def on_create(self):
        super().on_create()

        # Get data from construction kwargs
        username = self.kwargs.get("username", "Anonymous")
        text = self.kwargs.get("text", "")

        # Clear default inner HTML
        self.inner_html = ""

        if not text:
            raise ValueError("Message text cannot be empty")

        # Style the bubble
        self.style.update({
            "padding": "12px 16px",
            "margin": "8px 0",
            "border-radius": "8px",
            "max-width": "100%",
            "word-wrap": "break-word",
        })

        # Set background color (can be overridden at construction)
        self.style.setdefault("background-color", "#e3f2fd")

        # Username label
        username_label = Label(
            text=f"👤 {username}",
            color="#666",
        )

        # Message text
        message_text = Paragraph(text=text)

        # Add both to the bubble
        self.add_children([username_label, message_text])
```

**What's happening:**
- `self.kwargs` contains data passed when creating the component
- `self.style` is CSS in a dict
- `self.add_children()` adds nested components
- This component doesn't know about sockets or forms—it just renders UI

---

## Step 2 — Base Page (shared layout)

All pages in your app share a common header and layout. Create a base class:

Create: `web/ui/pages/base.py`

```python
"""
Base page for all pages. Handles shared layout and theme.
"""

from duck.html.components.page import Page
from duck.html.components.container import FlexContainer
from duck.html.components.heading import Heading


class BasePage(Page):
    """
    Base page for all pages in the chat app.

    Handles shared layout, styling, and metadata.
    Subclasses override `build_page()` to add page-specific content.
    """

    def on_create(self):
        super().on_create()

        # Page metadata
        self.set_title("🦆 Duck Chat App")
        self.set_description("A reactive chat app built with Duck Framework")

        # Main layout container (centered, max-width 600px)
        main = FlexContainer(flex_direction="column")
        main.style.update({
            "max-width": "600px",
            "margin": "0 auto",
            "padding": "20px",
            "font-family": "Arial, sans-serif",
        })

        # Header
        header = Heading(type="h1", text="🦆 Duck Chat App")
        header.style["text-align"] = "center"
        main.add_child(header)

        # Let subclasses add their own content
        self.build_page(main)

        # Add main container to page
        self.add_to_body(main)

    def build_page(self, container):
        """
        Override in subclasses to add page-specific content.

        Args:
            container: The main FlexContainer to add content to.
        """
        pass
```

**Pattern benefit:**
Every page has the same header, same width, same font — consistency. New pages only implement `build_page()`.

---

## Step 3 — Chat Page (the main logic)

This is where the action happens: message display, form, refresh, and reactivity.

Create: `web/ui/pages/chat.py`

```python
"""
Chat page with message display and input form.
"""

from duck.html.components import ForceUpdate
from duck.html.components.container import FlexContainer
from duck.html.components.form import Form
from duck.html.components.input import Input
from duck.html.components.button import Button
from duck.html.components.label import Label

from web.ui.pages.base import BasePage
from web.ui.components.message_bubble import MessageBubble


# In-memory message storage (shared across all users)
messages = []

# Color palette for different users
COLORS = [
    "#e3f2fd", "#f3e5f5", "#e8f5e9", "#fff3e0", "#fce4ec",
    "#e0f2f1", "#f1f8e9", "#ede7f6", "#e1f5fe", "#fff9c4",
]

# Track user colors and IDs
user_colors = {}
user_ids = {}
id_counter = 1


def get_user_id(websocket) -> str:
    """
    Get a consistent user ID for this websocket connection.
    Uses the session ID from the request.
    """
    global id_counter

    session_id = websocket.request.session.session_key

    if session_id not in user_ids:
        user_ids[session_id] = id_counter
        id_counter += 1

    return f"User {user_ids[session_id]}"


def get_user_color(username: str) -> str:
    """
    Assign a consistent color to each user.
    """
    if username not in user_colors:
        user_colors[username] = COLORS[len(user_colors) % len(COLORS)]
    return user_colors[username]


class ChatPage(BasePage):
    """
    Chat page with message display and input form.
    """

    def build_page(self, container):
        """Build the chat UI."""
        
        # === Chat message box (scrollable) ===
        self.chat_box = FlexContainer(
            flex_direction="column",
            id="chat-box",
            style={
                "height": "400px",
                "overflow-y": "auto",
                "border": "1px solid #ddd",
                "padding": "12px",
                "background-color": "#f9f9f9",
                "border-radius": "8px",
                "margin-bottom": "16px",
            },
        )

        # Display existing messages
        for msg in messages:
            color = get_user_color(msg["username"])
            bubble = MessageBubble(
                username=msg["username"],
                text=msg["text"],
                style={"background-color": color},
            )
            self.chat_box.add_child(bubble)

        # === Refresh button & message counter ===
        self.refresh_btn = Button(
            id="refresh-btn",
            text="🔄 Refresh",
            bg_color="#4CAF50",
            color="white",
            style={"padding": "8px 12px", "cursor": "pointer", "border-radius": "4px"},
        )

        self.info_label = Label(
            text=f"Messages: {len(messages)}",
            color="#666",
        )

        self.refresh_btn.bind(
            "click",
            self.on_refresh_click,
            update_targets=[self.chat_box],
        )

        # === Input form ===
        chat_form = Form(
            children=[
                Input(
                    type="text",
                    name="message",
                    placeholder="Type a message...",
                    required=True,
                    props={"value": ""},  # Important: Track value for clearing later
                    style={
                        "flex": "1",
                        "padding": "10px",
                        "border": "1px solid #ddd",
                        "border-radius": "4px",
                    },
                ),
                Button(
                    text="Send 📤",
                    props={"type": "submit"},
                    bg_color="#2196F3",
                    color="white",
                    style={"padding": "10px 20px", "cursor": "pointer", "border-radius": "4px"},
                ),
            ],
            style={"display": "flex", "gap": "10px"},
        )

        chat_form.bind(
            "submit",
            self.on_message_submit,
            update_targets=[self.chat_box, self.info_label],
        )

        # === Add everything to the page ===
        controls = FlexContainer(
            flex_direction="row",
            style={"gap": "10px", "margin-bottom": "10px", "align-items": "center"},
            children=[self.refresh_btn, self.info_label],
        )

        container.add_children([controls, self.chat_box, chat_form])

        # Bind page-level events
        self.document_bind(
            "DOMContentLoaded",
            self.on_dom_ready,
            update_self=False,
            update_targets=[self.chat_box],
        )

    async def on_dom_ready(self, page, event, value, websocket):
        """
        When the page loads, auto-refresh every 2 seconds so messages appear.
        """
        ms = 2_000
        await websocket.execute_js(
            f"setInterval(() => {{ document.getElementById(`{self.refresh_btn.id}`).click() }}, {ms});"
        )

    async def on_refresh_click(self, btn, event, value, websocket):
        """
        Refresh button: reload all messages and scroll to bottom.
        """
        self.chat_box.clear_children()

        for msg in messages:
            color = get_user_color(msg["username"])
            bubble = MessageBubble(
                username=msg["username"],
                text=msg["text"],
                style={"background-color": color},
            )
            self.chat_box.add_child(bubble)

        self.info_label.text = f"Messages: {len(messages)}"

        # Auto-scroll to bottom
        await websocket.execute_js("""
            const chatBox = document.getElementById('chat-box');
            chatBox.scrollTop = chatBox.scrollHeight;
        """)

    async def on_message_submit(self, form, event, form_data, websocket):
        """
        Form submission: add message, update UI, clear input.
        """
        message = form_data.get("message", "").strip()

        if not message:
            return

        # Get unique user ID
        username = get_user_id(websocket)

        # Store message in global list
        messages.append({"username": username, "text": message})

        # Create bubble and add to chat box
        color = get_user_color(username)
        bubble = MessageBubble(
            username=username,
            text=message,
            style={"background-color": color},
        )
        self.chat_box.add_child(bubble)

        # Update counter
        self.info_label.text = f"Messages: {len(messages)}"

        # Scroll to bottom
        await websocket.execute_js("""
            const chatBox = document.getElementById('chat-box');
            chatBox.scrollTop = chatBox.scrollHeight;
        """)

        # Clear the input field
        input_elem = form.children[0]
        input_elem.props["value"] = ""
        return ForceUpdate(input_elem, ["all"])
```

**Key points:**
- `messages` is a global list shared across all users
- `get_user_id()` assigns a consistent ID per browser session
- `on_message_submit()` is called when form is submitted
- `ForceUpdate()` resets the input field to empty after sending
- Auto-refresh every 2 seconds shows new messages

---

## Step 4 — Wire up the route

Edit `web/urls.py`:

```python
"""
URL routing for the chat app.
"""
from duck.urls import path

from web.ui.pages.chat import ChatPage


def chat(request):
    return ChatPage(request=request)


urlpatterns = [
    path("/", chat, name="home"),
]
```

---

## Run it

```bash
duck runserver # Or use python3 web/main.py
```

Visit **http://localhost:8000** and start chatting!

Open it in **two browser tabs** to see messages appear in real-time.

---

## How it works (under the hood)

1. **Page loads** → `DOMContentLoaded` fires
2. **Auto-refresh starts** → clicks refresh button every 2 seconds
3. **User types & sends** → `on_message_submit()` runs
4. **Message added** → global `messages` list updated
5. **UI re-renders** → new bubble appears instantly
6. **Input clears** → `ForceUpdate()` resets the field

All communication between browser and Python happens over **WebSocket** — super fast, minimal data sent.

---

## Improvements (next level)

1. **Persist messages** → Save to a database instead of in-memory
2. **User names** → Add a login form so users pick their own name
3. **Timestamps** → Show when each message was sent
4. **Typing indicator** → Show "User X is typing..."
5. **Delete messages** → Add a delete button on each bubble
6. **Emoji reactions** → Click a reaction emoji on a message
7. **Private messages** → Allow 1-on-1 conversations

---

## Common issues

### "Nothing happens when I click Send"

Check that:
- Form has `name="message"` on the input
- `on_message_submit` is bound to the form's `"submit"` event
- No errors in the console (open browser dev tools: F12)

### "Messages don't persist after refresh"

That's expected — we're using in-memory storage. For persistence use this [link](https://docs.duckframework.com/main/database) to learn 
more on DB persistence.

### "Only one browser sees messages"

Each browser session gets a unique user ID. Both see all messages, but they're shown differently (different colors). This is intentional — it's a **shared chat**.

---

## Next: Deploy it

Once happy with your chat app, deploy to production:

- [Deployment](https://docs.duckframework.com/main/deployment)

---

**You built a reactive chat app with zero JavaScript. 🎉**
