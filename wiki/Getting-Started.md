# 🎯 Getting Started with Duck

Welcome! This guide will help you install Duck and create your first web application.

---

## 📋 Prerequisites

Before installing Duck, make sure you have:

- **Python 3.10 or higher** - [Download Python](https://www.python.org/downloads/)
- **pip** - Python package installer (comes with Python)
- **Git** - For cloning the repository

### Check Your Python Version

```bash
python --version  # or python3 --version
```

---

## 📦 Installation

### Option 1: Install with uv (Recommended)

[uv](https://github.com/astral-sh/uv) is a fast Python package installer:

```bash
uv pip install git+https://github.com/duckframework/duck.git
```

### Option 2: Install with pip

```bash
pip install git+https://github.com/duckframework/duck.git
```

### Verify Installation

```bash
duck --version
```

You should see the Duck version number displayed.

---

## 🚀 Create Your First Project

Duck offers three project templates:

### 1. **Mini Project** (Recommended for Beginners)

Perfect for learning or small applications:

```bash
duck makeproject myproject --mini
```

Features:
- ✅ Basic structure
- ✅ Simple routing
- ✅ Essential features only
- ✅ Quick to understand

### 2. **Normal Project** (Default)

Balanced setup for most applications:

```bash
duck makeproject myproject
```

Features:
- ✅ Standard structure
- ✅ Common middleware
- ✅ Database support
- ✅ Component system

### 3. **Full Project**

Complete setup for large-scale applications:

```bash
duck makeproject myproject --full
```

Features:
- ✅ Advanced features
- ✅ Task automation
- ✅ Multiple apps structure
- ✅ Production-ready configuration

---

## 🏃 Run Your Project

Navigate to your project and start the server:

```bash
cd myproject
duck runserver
```

Or alternatively:

```bash
cd myproject
python web/main.py
```

### Server Options

```bash
# Run on a different port
duck runserver --port 3000

# Run with debug mode
duck runserver --debug

# Run with HTTPS (requires SSL certificate)
duck runserver --https
```

---

## 🌐 Access Your Application

Open your browser and visit:

```
http://localhost:8000
```

You should see the Duck welcome page! 🎉

---

## 📁 Project Structure

Here's what Duck creates for you:

```
myproject/
├── web/
│   ├── main.py          # Application entry point
│   ├── settings.py      # Configuration settings
│   ├── urls.py          # URL routing
│   └── ui/              # User interface files
│       ├── components/  # Reusable UI components
│       ├── pages/       # Page views
│       ├── static/      # CSS, JS, images
│       └── templates/   # HTML templates
├── apps/                # Custom applications
├── etc/                 # Configuration files
└── logs/                # Application logs
```

---

## ✏️ Create Your First View

Let's create a simple "Hello World" view:

### 1. Create a View Function

Edit `web/ui/pages/views.py`:

```python
from duck.shortcuts import render

def hello(request):
    """Simple hello world view"""
    return render(request, 'hello.html', {
        'message': 'Hello from Duck!'
    })
```

### 2. Create a Template

Create `web/ui/templates/hello.html`:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Hello Duck</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .container {
            text-align: center;
        }
        h1 {
            font-size: 3em;
            margin: 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>{{ message }}</h1>
        <p>Your Duck application is running!</p>
    </div>
</body>
</html>
```

### 3. Add URL Route

Edit `web/urls.py`:

```python
from duck.routes import Path
from web.ui.pages.views import hello

urlpatterns = [
    Path('/hello', hello, name='hello'),
]
```

### 4. Visit Your Page

Navigate to `http://localhost:8000/hello` to see your new page!

---

## 🎨 Next Steps

Now that you have Duck running, explore more features:

- 📘 Learn about [Components](Components) for building reactive UIs
- 🔧 Configure your app with [Settings](Configuration)
- 🚀 Deploy to production with [Deployment Guide](Deployment)
- 🔗 Integrate with Django using [Django Integration](Django-Integration)

---

## 🆘 Troubleshooting

### Port Already in Use

If port 8000 is busy, use a different port:

```bash
duck runserver --port 8080
```

### Module Not Found

Make sure you're in the project directory:

```bash
cd myproject
duck runserver
```

### Permission Errors

On Linux/Mac, you might need to use `python3` instead of `python`:

```bash
python3 web/main.py
```

---

## 📚 Additional Resources

- [Full Documentation](https://docs.duckframework.xyz)
- [Examples Repository](https://github.com/duckframework/duck-examples)
- [Community Forum](https://github.com/duckframework/duck/discussions)

---

Ready to build something amazing? Let's go! 🚀
