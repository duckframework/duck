# 🎨 Components Guide

Learn about Duck's powerful Lively Components system for building reactive user interfaces.

---

## 🌟 What are Lively Components?

Lively Components are Duck's answer to modern UI frameworks like React or Vue. They provide:

- **Virtual DOM** - Efficient UI updates with minimal re-renders
- **State Management** - Built-in reactive state handling
- **Python-Based** - Write UI logic in Python, not JavaScript
- **Server-Side** - Components render on the server
- **WebSocket Updates** - Real-time UI synchronization

---

## 🚀 Quick Example

Here's a simple counter component:

```python
from duck.components import Component

class Counter(Component):
    """A simple counter component."""
    
    def __init__(self):
        super().__init__()
        self.count = 0
    
    def increment(self):
        """Increment the counter."""
        self.count += 1
        self.update()  # Trigger re-render
    
    def decrement(self):
        """Decrement the counter."""
        self.count -= 1
        self.update()
    
    def render(self):
        """Render the component UI."""
        return f'''
            <div class="counter">
                <h2>Count: {self.count}</h2>
                <button onclick="component.increment()">+</button>
                <button onclick="component.decrement()">-</button>
            </div>
        '''
```

### Using the Component

```python
# In your view
from duck.shortcuts import render_component

def counter_page(request):
    counter = Counter()
    return render_component(request, counter)
```

---

## 📚 Component Basics

### Creating a Component

```python
from duck.components import Component

class MyComponent(Component):
    def __init__(self, title="Default"):
        super().__init__()
        self.title = title
    
    def render(self):
        return f'<h1>{self.title}</h1>'
```

### Component Lifecycle

```python
class LifecycleComponent(Component):
    def on_mount(self):
        """Called when component is first mounted."""
        print("Component mounted!")
    
    def on_update(self):
        """Called before each update."""
        print("Component updating...")
    
    def on_unmount(self):
        """Called when component is removed."""
        print("Component unmounted!")
    
    def render(self):
        return '<div>Hello</div>'
```

---

## 🎯 State Management

### Component State

State is any data that can change over time:

```python
class TodoList(Component):
    def __init__(self):
        super().__init__()
        self.todos = []
        self.input_value = ""
    
    def add_todo(self):
        if self.input_value:
            self.todos.append({
                'id': len(self.todos),
                'text': self.input_value,
                'done': False
            })
            self.input_value = ""
            self.update()
    
    def toggle_todo(self, todo_id):
        for todo in self.todos:
            if todo['id'] == todo_id:
                todo['done'] = not todo['done']
        self.update()
    
    def render(self):
        todo_items = ''.join([
            f'''
            <li>
                <input type="checkbox" 
                       {'checked' if todo['done'] else ''} 
                       onchange="component.toggle_todo({todo['id']})">
                <span class="{'done' if todo['done'] else ''}">{todo['text']}</span>
            </li>
            '''
            for todo in self.todos
        ])
        
        return f'''
            <div class="todo-list">
                <h2>My Todos</h2>
                <input type="text" 
                       value="{self.input_value}"
                       oninput="component.input_value = this.value">
                <button onclick="component.add_todo()">Add</button>
                <ul>{todo_items}</ul>
            </div>
        '''
```

---

## 🔄 Component Updates

### Manual Updates

```python
def my_method(self):
    self.data = new_value
    self.update()  # Trigger re-render
```

### Automatic Updates

Some methods trigger automatic updates:

```python
class AutoUpdateComponent(Component):
    def __init__(self):
        super().__init__()
        self.count = 0
    
    @Component.auto_update
    def increment(self):
        """Automatically calls update() after execution."""
        self.count += 1
```

---

## 🧩 Nested Components

Components can contain other components:

```python
class Button(Component):
    def __init__(self, text, color="blue"):
        super().__init__()
        self.text = text
        self.color = color
    
    def render(self):
        return f'<button class="btn-{self.color}">{self.text}</button>'

class Card(Component):
    def __init__(self, title):
        super().__init__()
        self.title = title
        self.button = Button("Click me", "green")
    
    def render(self):
        return f'''
            <div class="card">
                <h3>{self.title}</h3>
                {self.button.render()}
            </div>
        '''
```

---

## 🎪 Event Handling

### Click Events

```python
def render(self):
    return '''
        <button onclick="component.handleClick()">
            Click Me
        </button>
    '''

def handleClick(self):
    print("Button clicked!")
    self.update()
```

### Input Events

```python
def render(self):
    return f'''
        <input type="text" 
               value="{self.value}"
               oninput="component.handleInput(this.value)">
    '''

def handleInput(self, value):
    self.value = value
    self.update()
```

### Form Events

```python
def render(self):
    return f'''
        <form onsubmit="event.preventDefault(); component.handleSubmit()">
            <input name="email" type="email">
            <button type="submit">Submit</button>
        </form>
    '''

def handleSubmit(self):
    # Process form
    self.update()
```

---

## 💾 Component Caching

Improve performance with caching:

```python
from duck.components import Component, cached_component

@cached_component(timeout=3600)  # Cache for 1 hour
class ExpensiveComponent(Component):
    def render(self):
        # Expensive computation
        result = self.calculate_something()
        return f'<div>{result}</div>'
```

---

## 🎨 Styling Components

### Inline Styles

```python
def render(self):
    style = '''
        .my-component {
            background: #f0f0f0;
            padding: 20px;
            border-radius: 8px;
        }
    '''
    return f'''
        <style>{style}</style>
        <div class="my-component">
            Content here
        </div>
    '''
```

### CSS Classes

```python
def render(self):
    classes = ['component']
    if self.active:
        classes.append('active')
    if self.disabled:
        classes.append('disabled')
    
    return f'<div class="{" ".join(classes)}">Content</div>'
```

---

## 🔌 WebSocket Integration

Components use WebSockets for real-time updates:

```python
class RealtimeComponent(Component):
    def __init__(self):
        super().__init__()
        self.enable_websocket = True  # Enable WebSocket
    
    def on_websocket_message(self, message):
        """Handle incoming WebSocket messages."""
        if message['type'] == 'update':
            self.data = message['data']
            self.update()
    
    def send_message(self, data):
        """Send message to client."""
        self.emit('custom_event', data)
```

---

## 📊 Advanced Patterns

### Loading States

```python
class DataComponent(Component):
    def __init__(self):
        super().__init__()
        self.loading = True
        self.data = None
        self.error = None
    
    async def on_mount(self):
        try:
            self.data = await self.fetch_data()
        except Exception as e:
            self.error = str(e)
        finally:
            self.loading = False
            self.update()
    
    def render(self):
        if self.loading:
            return '<div class="spinner">Loading...</div>'
        
        if self.error:
            return f'<div class="error">{self.error}</div>'
        
        return f'<div class="data">{self.data}</div>'
```

### Conditional Rendering

```python
def render(self):
    if not self.is_logged_in:
        return self.render_login()
    
    if self.is_admin:
        return self.render_admin_panel()
    
    return self.render_user_panel()
```

### List Rendering

```python
def render(self):
    items = ''.join([
        f'<li key="{item.id}">{item.name}</li>'
        for item in self.items
    ])
    return f'<ul>{items}</ul>'
```

---

## ⚡ Performance Optimization

### Virtual DOM Diffing

Duck automatically optimizes re-renders:

```python
# Only changed elements are updated
class OptimizedComponent(Component):
    def render(self):
        # Use 'key' attribute for list items
        return '''
            <div>
                <p key="title">Title (never changes)</p>
                <p key="counter">Count: {self.count}</p>
            </div>
        '''
```

### Memoization

```python
from functools import lru_cache

class MemoizedComponent(Component):
    @lru_cache(maxsize=128)
    def expensive_calculation(self, arg):
        """This result is cached."""
        return complex_computation(arg)
    
    def render(self):
        result = self.expensive_calculation(self.value)
        return f'<div>{result}</div>'
```

---

## 🧪 Testing Components

```python
import unittest
from duck.components import Component

class TestCounter(unittest.TestCase):
    def setUp(self):
        self.counter = Counter()
    
    def test_initial_state(self):
        self.assertEqual(self.counter.count, 0)
    
    def test_increment(self):
        self.counter.increment()
        self.assertEqual(self.counter.count, 1)
    
    def test_render(self):
        html = self.counter.render()
        self.assertIn('Count: 0', html)
```

---

## 📚 Best Practices

### Do's ✅

- Keep components small and focused
- Use meaningful component names
- Handle errors gracefully
- Use keys for list items
- Cache expensive computations
- Write tests for components

### Don'ts ❌

- Don't mutate state directly without `update()`
- Don't create too many nested components
- Don't forget to handle loading/error states
- Don't ignore performance warnings
- Don't mix concerns (keep logic separate)

---

## 🔗 Related Documentation

- [Getting Started](Getting-Started)
- [Templates Guide](Templates)
- [WebSocket Support](WebSockets)
- [Performance Tips](Performance)

---

Ready to build reactive UIs? Start creating components! 🎨
