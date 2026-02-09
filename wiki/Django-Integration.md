# 🔗 Django Integration

Integrate Duck Framework with your existing Django project to add modern features like HTTP/2, WebSockets, and more.

---

## 🌟 Why Integrate Duck with Django?

Adding Duck to your Django project gives you:

- ✅ **HTTP/2 Support** - Native HTTP/2 with backward compatibility
- ✅ **Built-in HTTPS** - Free SSL certificates with auto-renewal
- ✅ **WebSocket Support** - Real-time communication
- ✅ **Lively Components** - Reactive UI system
- ✅ **Enhanced Security** - Additional security middleware
- ✅ **Better Performance** - Content compression, caching
- ✅ **No nginx Required** - Duck handles everything

All while keeping your Django code unchanged!

---

## 🚀 Quick Start

### 1. Install Duck

```bash
pip install git+https://github.com/duckframework/duck.git
```

### 2. Create Duck Project

```bash
duck makeproject myproject
cd myproject
```

### 3. Integrate Django

```bash
duck django-add /path/to/your/django_project
```

This command will:
- Analyze your Django project
- Update necessary configurations
- Set up Duck integration
- Provide next steps

### 4. Run the Server

```bash
duck runserver -dj
```

Your Django project now runs with Duck! 🎉

---

## 📋 Prerequisites

Before integrating:

- ✅ Django 3.2 or higher
- ✅ At least one Django urlpattern defined
- ✅ Django project in working state
- ✅ Python 3.10 or higher

---

## 🔧 Manual Integration

If you prefer manual setup:

### 1. Update Django Settings

Add Duck to your Django project's `settings.py`:

```python
# Django settings.py

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Add Duck
    'duck',
    'duck.contrib.django',
    
    # Your apps
    'myapp',
]

# Duck configuration
DUCK_SETTINGS = {
    'HTTPS': True,
    'AUTO_SSL': True,
    'DOMAIN': 'yourdomain.com',
    'EMAIL': 'admin@yourdomain.com',
}
```

### 2. Create Duck Main File

Create `duck_main.py` in your Django project root:

```python
import os
import django
from duck.server import DuckServer
from duck.contrib.django import DjangoIntegration

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yourproject.settings')
django.setup()

# Create server with Django integration
server = DuckServer()
server.add_integration(DjangoIntegration())

if __name__ == '__main__':
    server.run()
```

### 3. Run the Server

```bash
python duck_main.py
```

---

## 🌐 URL Routing

Duck respects your Django URL patterns:

```python
# Django urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('', views.home, name='home'),
]
```

All routes work exactly as before!

---

## 🎨 Using Duck Components in Django

Add Lively Components to your Django templates:

### 1. Create a Component

```python
# myapp/components.py
from duck.components import Component

class LiveCounter(Component):
    def __init__(self):
        super().__init__()
        self.count = 0
    
    def increment(self):
        self.count += 1
        self.update()
    
    def render(self):
        return f'''
            <div class="counter">
                <h3>Count: {self.count}</h3>
                <button onclick="component.increment()">+</button>
            </div>
        '''
```

### 2. Use in Django View

```python
# myapp/views.py
from django.shortcuts import render
from .components import LiveCounter

def my_view(request):
    counter = LiveCounter()
    
    return render(request, 'myapp/template.html', {
        'counter': counter,
    })
```

### 3. Render in Template

```django
<!-- myapp/templates/myapp/template.html -->
{% load duck_tags %}

<!DOCTYPE html>
<html>
<head>
    <title>My Page</title>
    {% duck_component_scripts %}
</head>
<body>
    <h1>Welcome</h1>
    
    {% render_component counter %}
    
    <!-- Rest of your Django template -->
</body>
</html>
```

---

## 🔌 WebSocket Support

Add WebSockets to your Django application:

### 1. Create WebSocket Handler

```python
# myapp/websockets.py
from duck.websocket import WebSocketHandler

class ChatHandler(WebSocketHandler):
    async def on_connect(self):
        """Called when client connects"""
        await self.accept()
        await self.send_json({'message': 'Welcome to chat!'})
    
    async def on_message(self, message):
        """Handle incoming messages"""
        # Broadcast to all connected clients
        await self.broadcast_json({
            'user': self.user.username,
            'message': message
        })
    
    async def on_disconnect(self):
        """Called when client disconnects"""
        pass
```

### 2. Register WebSocket Route

```python
# duck_main.py or urls.py
from duck.routes import WebSocketPath
from myapp.websockets import ChatHandler

websocket_urlpatterns = [
    WebSocketPath('/ws/chat/', ChatHandler),
]
```

### 3. Connect from Frontend

```javascript
// In your template
const socket = new WebSocket('ws://localhost:8000/ws/chat/');

socket.onopen = function(e) {
    console.log('Connected!');
    socket.send('Hello server!');
};

socket.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Message:', data);
};
```

---

## 🔒 HTTPS for Django

Enable HTTPS for your Django project:

### 1. Configure in Settings

```python
# Django settings.py

# Duck HTTPS configuration
DUCK_SETTINGS = {
    'HTTPS': True,
    'AUTO_SSL': True,
    'DOMAIN': 'yourdomain.com',
    'EMAIL': 'admin@yourdomain.com',
    'HTTP_REDIRECT': True,  # Redirect HTTP to HTTPS
}

# Django HTTPS settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
```

### 2. Run with HTTPS

```bash
duck runserver -dj --https
```

Duck automatically obtains and renews SSL certificates!

---

## 📦 Middleware Compatibility

Duck works with Django middleware:

```python
# Django settings.py
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
    # Duck middleware (optional)
    'duck.middleware.CompressionMiddleware',
    'duck.middleware.SecurityMiddleware',
]
```

---

## 💾 Database Integration

Duck uses your Django database configuration:

```python
# Django settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'mydb',
        'USER': 'myuser',
        'PASSWORD': 'mypassword',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

All Django ORM features work normally!

---

## 🎭 Static Files

Duck serves your Django static files:

```python
# Django settings.py
STATIC_URL = '/static/'
STATIC_ROOT = 'staticfiles/'

STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
```

Collect static files:
```bash
python manage.py collectstatic
```

Duck automatically serves them with compression!

---

## 👤 Authentication

Django authentication works seamlessly:

```python
# myapp/views.py
from django.contrib.auth.decorators import login_required

@login_required
def protected_view(request):
    user = request.user
    return render(request, 'protected.html', {'user': user})
```

Duck respects all Django authentication:
- Login/logout
- Permissions
- User sessions
- Password management

---

## 📊 Django Admin

The Django admin continues to work:

```python
# myapp/admin.py
from django.contrib import admin
from .models import MyModel

@admin.register(MyModel)
class MyModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
```

Access at: `https://yourdomain.com/admin/`

---

## 🚀 Performance Benefits

### Automatic Compression

Duck compresses responses automatically:
- Brotli compression (best)
- Gzip compression
- Deflate compression

No configuration needed!

### HTTP/2 Multiplexing

Multiple requests over single connection:
- Faster page loads
- Reduced latency
- Better resource utilization

### Connection Pooling

Efficient database connections:
```python
DATABASES = {
    'default': {
        # ...
        'CONN_MAX_AGE': 600,  # 10 minutes
    }
}
```

---

## 🔄 Migration Path

### Phase 1: Add Duck (Day 1)

```bash
duck makeproject myproject
duck django-add /path/to/django_project
duck runserver -dj
```

Everything works as before!

### Phase 2: Add Components (Week 1)

Start using Lively Components in new features:
```python
# Keep existing views as-is
# Add components to new pages
```

### Phase 3: Add WebSockets (Week 2)

Add real-time features where needed:
```python
# Chat, notifications, live updates
```

### Phase 4: Full Integration (Month 1)

Gradually adopt Duck features:
- Refactor complex pages with components
- Add WebSocket updates
- Optimize with caching

---

## 🧪 Testing

Your Django tests continue to work:

```python
# myapp/tests.py
from django.test import TestCase, Client

class MyTestCase(TestCase):
    def setUp(self):
        self.client = Client()
    
    def test_my_view(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
```

Run tests normally:
```bash
python manage.py test
```

---

## 📚 Comparison: Before and After

### Before Duck

```
[Browser] → [nginx] → [Gunicorn] → [Django]
            ↓
        [Certbot for SSL]
```

**Issues:**
- Complex setup
- Multiple services to manage
- Manual SSL renewal
- No HTTP/2
- No WebSockets (needs Channels)

### After Duck

```
[Browser] → [Duck + Django]
```

**Benefits:**
- Simple setup
- Single service
- Automatic SSL renewal
- Native HTTP/2
- Built-in WebSockets

---

## ⚙️ Configuration Options

```python
# Django settings.py
DUCK_SETTINGS = {
    # Server
    'HOST': '0.0.0.0',
    'PORT': 8000,
    'WORKERS': 4,
    
    # HTTPS
    'HTTPS': True,
    'AUTO_SSL': True,
    'DOMAIN': 'yourdomain.com',
    'EMAIL': 'admin@yourdomain.com',
    
    # Performance
    'COMPRESSION': True,
    'COMPRESSION_LEVEL': 6,
    
    # WebSocket
    'WEBSOCKET_ENABLED': True,
    'WEBSOCKET_PATH': '/ws/',
    
    # Security
    'RATE_LIMIT': True,
    'RATE_LIMIT_REQUESTS': 100,
    'RATE_LIMIT_WINDOW': 60,
}
```

---

## 🆘 Troubleshooting

### URLs Not Working

Check Django urlpatterns are properly defined:
```python
# urls.py must have at least one pattern
urlpatterns = [
    path('', views.home),
]
```

### Static Files 404

Collect static files first:
```bash
python manage.py collectstatic
```

### Components Not Updating

Include Duck JavaScript:
```django
{% load duck_tags %}
{% duck_component_scripts %}
```

### Import Errors

Ensure Duck is installed:
```bash
pip install git+https://github.com/duckframework/duck.git
```

---

## 📖 Learn More

- [Getting Started](Getting-Started)
- [Components Guide](Components)
- [Deployment Guide](Deployment)
- [Configuration](Configuration)

---

Supercharge your Django project with Duck! 🦆
