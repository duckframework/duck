# Lively / HTML Components — Part 1: Overview & Page Basics

*Reactive Python UI Without JavaScript*

![Badge](https://img.shields.io/badge/feature-Lively_Components-blue)

> **Series index:** This is Part 1 of 3.
> - **Part 1 — Overview & Page Basics** *(this file)*
> - Part 2 — Events, Forms & File Uploads (`02-lively-events-forms-file-uploads.md`)
> - Part 3 — Advanced Rendering, Templates & Reference (`03-lively-advanced-rendering-and-reference.md`)

---

## Introduction

**Duck** now includes the **Lively Component System** — a real-time, component-based system that enables responsive page updates without full reloads.

It leverages **WebSockets with msgpack** for fast communication and supports navigation to new URLs without full page reloads.

> **Recommended:** Use Lively/HTML components over traditional templates. Components are flexible, Pythonic, and allow pluggable, reusable UI elements.

---

## What Is the Lively Component System?

The **Lively Component System** is Duck's way of building interactive web pages using pure Python.

Instead of writing JavaScript for buttons, forms, or live updates, you write Python classes. Duck automatically handles the real-time communication between the browser and the server for you.

Think of it like this:

> You write Python.
> Duck makes the browser react instantly.

---

## What Problem Does It Solve?

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

## How It Works (Simple Explanation)

1. You create a **Page class** in Python.
2. You add components (like buttons, text, forms).
3. You attach Python functions to events (like button clicks).
4. When a user interacts with the page:
   - The browser sends the event to the server.
   - Your Python function runs.
   - Only the changed parts of the page update.

This feels similar to React or other reactive frameworks — but controlled from Python.

---

## Why It's Powerful

- Real-time updates without manual JavaScript
- Cleaner architecture (UI + logic in one place)
- Fast navigation between pages
- Component reuse
- Built-in lifecycle handling

---

## Beginner Mental Model

If you're new, think of it like this:

- A **Page** = a screen
- A **Component** = a piece of UI (button, text, input)
- An **Event** = something the user does (click, type)
- Your Python method = what should happen next

And Duck handles the browser synchronization automatically.

---

## Page Component Example

```py
from duck.html.components.page import Page
from duck.html.components.button import Button

class HomePage(Page):
    def on_create(self):
        super().on_create()
        self.set_title("Home - MySite")
        self.set_description("Welcome to MySite, the premier platform...")
        self.set_favicon("/static/favicon.ico", icon_type="image/x-icon")
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

## Guidelines

When vibecoding or working with these components, refer to the guidelines directory in our GitHub repository:
https://github.com/duckframework/duck/tree/main/ai

This directory provides best practices for building scalable, maintainable components and structuring projects effectively.

---

**Next:** Part 2 covers component events, document-specific events, automatic event binding, forms, and file uploads.
