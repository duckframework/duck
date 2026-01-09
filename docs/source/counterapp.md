# 📟 Simple Counter App

![Badge](https://img.shields.io/badge/feature-CounterApp-blue)
![Badge](https://img.shields.io/badge/system-Lively_Component-green)

**Duck** includes a builtin **Simple Counter App** built using the **Lively Component System** for demonstration and testing.

---

## 🗂️ views/__init__.py

```py
from duck.views import View
from duck.shortcuts import to_response
from duck.html.components import to_component
from duck.html.components.container import FlexContainer
from duck.html.components.button import Button
from duck.html.components.label import Label
from duck.html.components.page import Page


class HomePage(Page):
    def on_create(self):
        super().on_create()
        self.style["font-family"] = "system-ui"
        self.set_title("Simple Counter App")
        
        # Initialize counter
        self.counter = 0
        
        def on_btn_click(btn, *_):
            self.counter += 1
            self.label.text = counter
            
        # Container for components alignment
        self.container = FlexContainer()
        self.container.style.update({
            "gap": "50px",
            "flex-direction": "column",
            "align-items": "center",
            "justify-content": "center",
            "padding": "20px"
        })
        
        # Add heading
        self.heading = to_component("Counter App", "h1", color="#bbb")
        self.container.add_child(self.heading)
        
        # Add label showing live counter
        self.label = Label(text=self.counter)
        self.label.color = "black"
        self.label.style["font-size"] = "1.5rem"
        self.container.add_child(self.label)
        
        # Initialize button
        self.btn = Button(text="Increment")
        self.btn.color = "white"
        self.btn.bg_color = "green"
        self.btn.style.update({
            "padding": "20px",
            "font-size": "1.2rem"
        })
        
        # Bind button to increment counter
        self.btn.bind(
            "click",
            on_btn_click,
            update_targets=[self.label],
            update_self=False,
        )
        
        # Add button to container and container to page
        self.container.add_child(self.btn)
        self.add_to_body(self.container)


class HomeView(View):
    def run(self):
        # Return component as HTTP response
        page = HomePage(self.request)
        return to_response(page)
```

---

## How to use

To use or to test out the builtin counterapp, you just need to follow the steps below:

1. Include the counterapp blueprint in settings.
    ```py
    # settings.py
    
    BLUEPRINTS = [
        "duck.etc.apps.counterapp.blueprint.CounterApp",
        # Other blueprints...
    ]
    ```
2. Whats left is to go to `/counterapp` URL path.

---

## 📝 Notes

- Requires the **Lively Component System** to be active.
- Demonstrates **real-time updates**: the label updates automatically when the counter increments.
- Great for testing component events and bindings.
