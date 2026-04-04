# ❓ Frequently Asked Questions

Get answers to common questions about Duck Framework.

---

## General Questions

### What is Duck Framework?

Duck is a full-featured Python web framework and server that provides everything you need to build modern web applications - from the HTTP server to the component system, all in one package.

### Is Duck production-ready?

Yes! Duck is used in production environments, including the official [duckframework.xyz](https://duckframework.xyz) website. It includes:
- Built-in HTTPS and HTTP/2 support
- Security middleware
- Automatic SSL renewal
- Performance optimizations
- Production deployment tools

### How does Duck compare to Django or Flask?

| Feature | Duck | Django | Flask |
|---------|------|--------|-------|
| Built-in Server | ✅ Production-ready | ❌ Dev only | ❌ Dev only |
| HTTPS/HTTP/2 | ✅ Native | ❌ Needs nginx | ❌ Needs nginx |
| Free SSL | ✅ Auto-renewal | ❌ Manual | ❌ Manual |
| Async Support | ✅ Full support | ⚠️ Partial | ⚠️ Partial |
| Components | ✅ Virtual DOM | ❌ None | ❌ None |
| WebSockets | ✅ Built-in | ⚠️ Channels | ❌ Extension |

Duck can also **integrate with Django**, giving your Django project all of Duck's features!

---

## Installation & Setup

### What are the system requirements?

- Python 3.10 or higher
- Linux, macOS, or Windows
- 512MB RAM minimum (1GB+ recommended)
- Internet connection for SSL certificates

### Can I use Duck with existing Python projects?

Yes! Duck can integrate with Django projects using the `django-add` command. For other frameworks, Duck can act as a reverse proxy or you can gradually migrate your code.

### Which project type should I choose?

- **Mini** - Learning, small projects, or simple APIs
- **Normal** (default) - Most web applications
- **Full** - Large-scale applications with advanced features

You can always add features later, so start with what you need!

---

## Development

### How do I create a new page?

1. Create a view function in `web/ui/pages/views.py`
2. Create a template in `web/ui/templates/`
3. Add a URL route in `web/urls.py`

See the [Getting Started guide](Getting-Started) for a complete example.

### Can I use JavaScript frameworks with Duck?

Yes! Duck works great with:
- React
- Vue.js
- Alpine.js
- Vanilla JavaScript

Duck also has its own **Lively Components** system with Virtual DOM if you prefer a Python-first approach.

### How do I handle forms?

```python
from duck.shortcuts import render, redirect

def contact_form(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        # Process form data
        return redirect('/thank-you')
    
    return render(request, 'contact.html')
```

### How do I work with databases?

Duck is compatible with Django ORM:

```python
from duck.db import models

class Article(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
```

Create and run migrations:
```bash
duck makemigrations
duck migrate
```

### Can I use async/await?

Absolutely! Duck has full async support:

```python
async def my_async_view(request):
    data = await fetch_data_async()
    return render(request, 'page.html', {'data': data})
```

This works even in WSGI mode!

---

## Components

### What are Lively Components?

Lively Components are Duck's reactive UI system with:
- Virtual DOM diffing
- State management
- Fast re-rendering
- Python-based (no JavaScript required)

Example:
```python
from duck.components import Component

class Counter(Component):
    def __init__(self):
        self.count = 0
    
    def increment(self):
        self.count += 1
    
    def render(self):
        return f'''
            <div>
                <p>Count: {self.count}</p>
                <button onclick="component.increment()">+</button>
            </div>
        '''
```

### Do I have to use components?

No! Components are optional. You can use:
- Traditional templates only
- Mix of templates and components
- Components everywhere

Choose what works best for your project.

---

## Deployment

### How do I deploy Duck to production?

Duck can run directly in production without nginx:

```bash
# Install as system service
sudo duck service install

# Start the service
sudo duck service start

# Enable auto-start on boot
sudo duck service enable
```

See the [Deployment Guide](Deployment) for detailed instructions.

### How do I get SSL certificates?

Duck handles SSL automatically:

```python
# In settings.py
HTTPS = True
AUTO_SSL = True
DOMAIN = 'example.com'
EMAIL = 'admin@example.com'
```

Duck will:
1. Request a Let's Encrypt certificate
2. Install the certificate
3. Automatically renew before expiration

### Can I use Duck behind a reverse proxy?

Yes! Duck works great behind:
- nginx
- Apache
- Cloudflare
- Any reverse proxy

Configure the proxy to forward to Duck's port (default 8000).

### How do I scale Duck?

Duck supports horizontal scaling:

```python
# In settings.py
WORKERS = 4  # Number of worker processes
```

For multiple servers:
1. Use a load balancer (nginx, HAProxy)
2. Share session storage (Redis, database)
3. Use shared storage for uploads
4. Configure cache backend

---

## Django Integration

### Can I use Duck with my existing Django project?

Yes! It's easy:

```bash
duck makeproject myproject
cd myproject
duck django-add /path/to/django_project
duck runserver -dj
```

Your Django project gets:
- HTTP/2 support
- Free SSL certificates
- Automatic compression
- Enhanced security
- Lively Components

### Will my Django apps still work?

Yes! All Django features continue to work:
- URL routing
- Models and migrations
- Admin interface
- Django middleware
- Third-party packages

Duck adds features, doesn't replace anything.

### Do I need to modify my Django code?

Minimal changes required:
1. Add Duck to `INSTALLED_APPS`
2. Update WSGI settings (Duck helps with this)
3. Optionally configure Duck features

See [Django Integration guide](Django-Integration) for details.

---

## Performance

### How fast is Duck?

Duck is optimized for speed:
- Async I/O for high concurrency
- Efficient virtual DOM diffing
- Content compression
- Caching support
- Connection pooling

Benchmarks show Duck handling thousands of requests per second on modest hardware.

### Does Duck support caching?

Yes! Multiple caching options:

```python
from duck.cache import cache

# Simple caching
cache.set('key', 'value', timeout=300)
value = cache.get('key')

# View caching
from duck.decorators import cache_view

@cache_view(timeout=3600)
def my_view(request):
    # Cached for 1 hour
    return render(request, 'page.html')
```

### Can Duck handle large file uploads?

Yes! Duck supports:
- Streaming uploads
- Large file handling
- Progress tracking
- Resumable uploads

Configure max upload size in settings:
```python
MAX_UPLOAD_SIZE = 100 * 1024 * 1024  # 100MB
```

---

## Security

### Is Duck secure?

Duck includes multiple security features:
- HTTPS by default
- CSRF protection
- XSS prevention
- SQL injection protection
- Command injection protection
- DoS mitigation
- Secure headers

Always keep Duck updated for latest security patches!

### How do I report security issues?

For security vulnerabilities:
1. **DO NOT** open a public issue
2. Email security@duckframework.xyz
3. Include details and reproduction steps
4. We'll respond within 48 hours

See [SECURITY.md](https://github.com/duckframework/duck/blob/main/SECURITY.md) for our security policy.

### Does Duck support authentication?

Yes! Use Django's authentication system:

```python
from django.contrib.auth import authenticate, login

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            return redirect('/')
    return render(request, 'login.html')
```

---

## Troubleshooting

### Server won't start

Check these common issues:

1. **Port already in use**
   ```bash
   duck runserver --port 8080
   ```

2. **Permission denied**
   - Ports < 1024 need root/admin
   - Use port 8000+ for development

3. **Module not found**
   - Verify you're in project directory
   - Check Python environment is activated

### SSL certificate errors

Common SSL issues:

1. **Port 80 must be accessible** - Let's Encrypt validates via HTTP
2. **Domain must point to server** - DNS must resolve correctly
3. **Firewall blocking** - Open ports 80 and 443

Test with:
```bash
duck runserver --https --debug
```

### Components not updating

Make sure:
1. Component state is changed via methods
2. JavaScript is enabled in browser
3. WebSocket connection is active
4. Check browser console for errors

### Static files not loading

Verify:
1. `STATIC_URL` is configured
2. Files are in `web/ui/static/`
3. `collectstatic` is run (if needed)
4. Check file permissions

---

## Community & Support

### How can I get help?

Multiple ways to get support:

- 📖 [Documentation](https://docs.duckframework.xyz)
- 💬 [GitHub Discussions](https://github.com/duckframework/duck/discussions)
- 🐛 [Issue Tracker](https://github.com/duckframework/duck/issues)
- 📧 [Email Support](mailto:support@duckframework.xyz)

### How can I contribute?

We welcome all contributions!

- 🐛 Report bugs
- 💡 Suggest features
- 📝 Improve documentation
- 💻 Submit code
- ⭐ Star the repo
- 📢 Spread the word

See [Contributing Guide](Contributing) for details.

### Is Duck free to use?

Yes! Duck is open source under the MIT License:
- ✅ Free for commercial use
- ✅ Free for personal use
- ✅ Free to modify
- ✅ Free to distribute

### How can I support Duck?

- ⭐ Star us on [GitHub](https://github.com/duckframework/duck)
- 💰 Sponsor via [Open Collective](https://opencollective.com/duckframework)
- 📢 Share with others
- 🤝 Contribute code or docs

---

## Still Have Questions?

- Post in [GitHub Discussions](https://github.com/duckframework/duck/discussions)
- Check the [full documentation](https://docs.duckframework.xyz)
- Review [existing issues](https://github.com/duckframework/duck/issues)

We're here to help! 🦆
