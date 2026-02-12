# Duck Framework Project Reference

This document serves as a comprehensive reference for understanding what a Duck framework project looks like. Use this information when helping users create or understand Duck projects.

## Overview

**Duck** is a powerful, open-source, full-fledged Python-based **web server**, **framework**, and **reverse proxy** designed for building modern, customizable web applications — from small sites to large-scale platforms.

## Project Types

Duck supports three types of projects, each suited for different use cases:

### 1. Mini Project (`--mini`)
- **Target Users**: Beginners, simple applications
- **Files**: Minimal configuration (9 files/7 directories)
- **Use Case**: Simple web applications that don't require extensive configuration
- **Command**: `duck makeproject myproject --mini`

### 2. Normal Project (default)
- **Target Users**: Average developers, standard applications
- **Files**: Moderate configuration (16 files/12 directories)
- **Use Case**: Default choice for most web applications
- **Command**: `duck makeproject myproject`

### 3. Full Project (`--full`)
- **Target Users**: Experienced developers, complex applications
- **Files**: Complete configuration (20 files/12 directories)
- **Use Case**: Complex applications requiring maximum customization and control (includes additional configuration files for automations, template tags, environment variables, and git integration)
- **Command**: `duck makeproject myproject --full`

## Standard Project Structure

### Full Project Structure

```
myproject/                      # Root Project Directory
├── .env                        # Environment variables file (full only)
├── .gitignore                  # Git ignore file (full only)
├── LICENSE                     # License file (normal, full)
├── README.md                   # Project readme (normal, full)
├── TODO.md                     # Todo file (normal, full)
├── requirements.txt            # Python dependencies
├── etc/                        # Configuration files directory
│   ├── README.md              # Duck etc readme file
│   └── ssl/                   # SSL certificates directory
│       ├── server.crt         # Default Duck server certificate
│       └── server.key         # Default Duck server private key
└── web/                        # Main application directory
    ├── __init__.py            # Python package marker
    ├── main.py                # Duck main app execution file
    ├── settings.py            # Duck settings configuration
    ├── urls.py                # Duck URL configuration
    ├── views.py               # Request handling views
    ├── automations.py         # Duck automations (full only)
    ├── templatetags.py        # Custom template tags/filters (full only)
    ├── backend/               # Backend integration directory
    │   └── django/            # Django integration (optional)
    │       └── duckapp/       # Default Django project
    │           ├── manage.py
    │           └── duckapp/
    │               ├── __init__.py
    │               ├── asgi.py
    │               ├── wsgi.py
    │               ├── settings.py  # Django settings (edited by Duck)
    │               ├── urls.py      # Django URL config (edited by Duck)
    │               └── views.py     # Django views
    └── ui/                    # Frontend directory
        ├── components/        # Reusable Lively components
        │   └── README.md
        ├── pages/            # Structured Lively page components
        │   └── README.md
        ├── static/           # Static files (CSS, JS, images)
        │   └── README.md
        └── templates/        # Application templates
            └── README.md
```

## Core Files Explained

### 1. main.py
**Purpose**: Main entry point for running the Duck application

**Standard Content**:
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

**Key Points**:
- Alternative to `duck runserver` command
- Configures port, address, and domain
- Can be customized for IPv6: `App(port=8000, addr='::1', uses_ipv6=True)`

### 2. settings.py
**Purpose**: Central configuration file for all Duck project settings

**Key Settings Categories**:
- **Security**: `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`
- **URL Configuration**: `URLPATTERNS_MODULE`, `BLUEPRINTS`
- **Middleware & Normalizers**: `MIDDLEWARES`, `NORMALIZERS`
- **Compression**: `CONTENT_COMPRESSION` settings
- **Automation**: `AUTOMATIONS` configuration
- **HTTP/2 & HTTPS**: `SUPPORT_HTTP_2`, `ENABLE_HTTPS`, `FORCE_HTTPS`
- **WSGI/ASGI**: `WSGI`, `ASGI`, `ASYNC_HANDLING`
- **Templates**: `TEMPLATE_DIRS`, `TEMPLATE_HTML_COMPONENTS`, `TEMPLATETAGS_MODULE`
- **Static/Media Files**: `STATIC_ROOT`, `STATIC_URL`, `MEDIA_ROOT`, `MEDIA_URL`
- **Django Integration**: `USE_DJANGO`, `DJANGO_BIND_PORT`, `DUCK_EXPLICIT_URLS`
- **Session**: `SESSION_STORAGE`
- **SSL**: `SSL_CERTFILE_LOCATION`, `SSL_PRIVATE_KEY_LOCATION`
- **Logging**: `LOGGING_DIR`, `LOG_TO_FILE`
- **Systemd**: Service management configuration

### 3. urls.py
**Purpose**: Maps URL endpoints to views

**Standard Pattern**:
```python
from duck.urls import path, re_path

urlpatterns = [
    path("/", views.home, "home", methods=["GET"]),
    # Additional URL patterns...
]
```

**URL Mapping Features**:
- **Simple paths**: `path("/", view, "name", methods=["GET"])`
- **Dynamic segments**: `path("/user/<user_id>", view, "user_detail")`
- **Regex patterns**: `re_path("/books/ids/.*", view, "book_ids")`
- **WebSocket support**: Can map WebSocket views

### 4. views.py
**Purpose**: Contains logic for generating content for URL endpoints

**View Types Supported**:
```python
from duck.views import View

# Function-based view
def home(request):
    return "<h1>Hello world</h1>"

# Async function-based view
async def async_home(request):
    return "<h1>Hello world</h1>"

# Class-based view
class SomeView(View):
    def run(self):
        return "<h1>Hello world</h1>"

# Async class-based view
class SomeAsyncView(View):
    async def run(self):
        return "<h1>Hello world</h1>"
```

**Key Points**:
- Every view expects a `request` argument
- Can return plain HTML strings or `HttpResponse` objects
- Supports both sync and async views

### 5. automations.py (Full project only)
**Purpose**: Define automation tasks and triggers

**Standard Structure**:
```python
from duck.automation import Automation
from duck.automation.trigger import AutomationTrigger

class CustomTrigger(AutomationTrigger):
    def check_trigger(self):
        # Return True if condition is met
        return condition_met

class CustomAutomation(Automation):
    def execute(self):
        # Execute automation tasks
        pass
```

### 6. templatetags.py (Full project only)
**Purpose**: Define custom template tags and filters

**Standard Structure**:
```python
from duck.template import TemplateTag, TemplateFilter

TAGS = [
    # TemplateTag("name", function, takes_context=False)
]

FILTERS = [
    # TemplateFilter("name", function)
]
```

## Key Features by Project Type

| Feature | Mini | Normal | Full |
|---------|------|--------|------|
| main.py | ✓ | ✓ | ✓ |
| settings.py | ✓ | ✓ | ✓ |
| urls.py | ✓ | ✓ | ✓ |
| views.py | ✓ | ✓ | ✓ |
| LICENSE | ✗ | ✓ | ✓ |
| README.md | ✗ | ✓ | ✓ |
| TODO.md | ✗ | ✓ | ✓ |
| .env | ✗ | ✗ | ✓ |
| .gitignore | ✗ | ✗ | ✓ |
| automations.py | ✗ | ✗ | ✓ |
| templatetags.py | ✗ | ✗ | ✓ |
| ui/ directories | ✗ | ✓ | ✓ |
| Django integration | ✓ | ✓ | ✓ |

## Starting a Duck Project

### Basic Workflow

1. **Create project**:
   ```bash
   duck makeproject myproject [--mini|--full]
   ```

2. **Navigate to project**:
   ```bash
   cd myproject
   ```

3. **Run server**:
   ```bash
   duck runserver
   # OR
   python3 web/main.py
   ```

4. **Access application**:
   - Default: http://localhost:8000

## Django Integration

Duck can integrate with existing Django projects:

```bash
duck makeproject myproject
cd myproject
duck django-add "path/to/your/django_project"
duck runserver -dj
```

**Benefits**:
- Native HTTP/2 & HTTPS
- Built-in security middleware
- Auto-compressed responses
- Resumable downloads
- Free SSL with renewal
- Same Python environment (faster communication)

## Important Directories

### etc/
- **Purpose**: Configuration and external files
- **Contains**: SSL certificates, configuration files
- **SSL Certificates**: Default self-signed certificates included

### web/
- **Purpose**: Main application code
- **Contains**: Python scripts for application logic

### web/ui/
- **Purpose**: Frontend components and assets
- **Subdirectories**:
  - `components/`: Reusable Lively components
  - `pages/`: Structured page components
  - `static/`: CSS, JavaScript, images
  - `templates/`: HTML templates

### web/backend/
- **Purpose**: Backend integration
- **Supports**: Django integration (extendable)

### assets/ (Created at runtime)
- **Purpose**: Runtime generated files
- **Contains**:
  - `logs/`: Application logs
  - `staticfiles/`: Collected static files
  - `media/`: User uploaded files

## Configuration Files

### .gitignore (Full project)
Standard ignores:
- `__pycache__/`
- `assets/*`
- `.venv/`
- `.logs/`
- `.ducksight-state`
- `.processes.json`

### .env (Full project)
Environment variables file for sensitive configuration

### requirements.txt
Standard dependencies:
```
Django>=5.1.5
Jinja2>=3.1.5
watchdog>=4.0.1
requests>=2.31.0
h2>=4.2.0
msgpack>=1.1.1
diskcache
colorama
tzdata
click
asgiref>=3.8.1
psutil>=7.0.0
rich>=14.1.0
setproctitle
```

## Duck Framework Features

### Core Capabilities
1. **Web Server**: Built-in HTTPS support
2. **HTTP/2**: Native support with HTTP/1 backward compatibility
3. **SSL/TLS**: Free SSL certificate generation (via Let's Encrypt/certbot) with automatic renewal using Duck's automation system
4. **WebSocket**: Modern implementation with per-message compression
5. **Task Automation**: Built-in scheduling (no cron jobs needed)
6. **Content Compression**: Automatic gzip, deflate, brotli
7. **Django Integration**: Easy integration with existing Django projects
8. **Blueprints**: Organized routing system
9. **Async Support**: Full async/await support even in WSGI
10. **Security**: DoS, SQL Injection, Command Injection protection
11. **Hot Reload**: Auto-reload in debug mode
12. **Monitoring**: CPU, RAM, Disk, I/O monitoring with `duck monitor`
13. **Lively Components**: Fast, reactive UI components with VDom Diffing

### CLI Commands
- `duck makeproject <name> [--mini|--full]`: Create new project
- `duck makeblueprint <name>`: Create new blueprint
- `duck runserver`: Run development server
- `duck django-add <path>`: Integrate Django project
- `duck runtests`: Run test suite
- `duck monitor`: System monitoring
- `duck logs`: View application logs
- `duck sitemap`: Generate sitemap
- `duck collectstatic`: Collect static files
- `duck service`: Manage systemd service
- `duck ssl_gen`: Generate SSL certificates

## Best Practices

### Project Selection
- **Choose Mini**: Simple apps, learning Duck, minimal configuration
- **Choose Normal**: Most applications, balanced features
- **Choose Full**: Complex apps, maximum customization, production-ready

### File Organization
- Keep views organized (single file or folder module)
- Use blueprints for modular applications
- Store static files in `web/ui/static/`
- Store templates in `web/ui/templates/`
- Use `backend/django/` for Django integration

### Configuration
- Always change `SECRET_KEY` in production
- Set `DEBUG=False` in production
- Configure `ALLOWED_HOSTS` appropriately
- Use environment variables for sensitive data
- Enable HTTPS in production (`ENABLE_HTTPS=True`)

### Development Workflow
1. Create project with appropriate type
2. Configure `settings.py` for your needs
3. Define URL patterns in `urls.py`
4. Implement views in `views.py`
5. Create templates in `web/ui/templates/`
6. Add static files to `web/ui/static/`
7. Test with `duck runserver` or `python web/main.py`
8. Deploy with systemd service management

## Python Version
- **Minimum**: Python 3.10+
- **Supported**: 3.10, 3.11, 3.12, 3.13

## Official Resources
- **Website**: https://duckframework.xyz
- **Documentation**: https://docs.duckframework.xyz
- **Repository**: https://github.com/duckframework/duck
- **Issues**: https://github.com/duckframework/duck/issues

## Installation
```bash
# Using uv (recommended)
uv pip install git+https://github.com/duckframework/duck.git

# Using pip
pip install git+https://github.com/duckframework/duck.git
```

## Summary

A Duck framework project is characterized by:
- **Modular structure** with clear separation of concerns
- **Flexible configuration** through `settings.py`
- **URL-based routing** with `urls.py` and `urlpatterns`
- **View-based content generation** supporting sync/async
- **Built-in security** and performance features
- **Easy Django integration** for existing projects
- **Comprehensive CLI** for project management
- **Three project types** catering to different complexity levels
- **Production-ready** features (HTTPS, HTTP/2, SSL auto-renewal)
- **Developer-friendly** with hot reload and debugging tools

This structure provides a solid foundation for building modern web applications with Python, whether starting from scratch or integrating with existing Django projects.
