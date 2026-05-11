# 🔧 Configuration Guide

Learn how to configure your Duck application for different environments and use cases.

---

## 📁 Configuration File

Duck uses a `settings.py` file for configuration, located at `web/settings.py` in your project.

```python
# web/settings.py
DEBUG = True
SECRET_KEY = 'your-secret-key-here'
ALLOWED_HOSTS = ['localhost', '127.0.0.1']
```

---

## 🔑 Essential Settings

### DEBUG

Control debug mode:

```python
# Development
DEBUG = True

# Production (ALWAYS False in production!)
DEBUG = False
```

**When DEBUG = True:**
- Detailed error pages
- Auto-reload on file changes
- Development tools enabled

**When DEBUG = False:**
- Generic error pages
- No auto-reload
- Production optimizations

### SECRET_KEY

Used for cryptographic signing:

```python
# Generate a secure key
import secrets
SECRET_KEY = secrets.token_urlsafe(50)

# In production, use environment variables
import os
SECRET_KEY = os.environ.get('SECRET_KEY')
```

⚠️ **Never commit your SECRET_KEY to version control!**

### ALLOWED_HOSTS

Hosts/domains that can serve your app:

```python
# Development
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Production
ALLOWED_HOSTS = [
    'yourdomain.com',
    'www.yourdomain.com',
    '123.45.67.89'
]

# Allow all (NOT recommended for production)
ALLOWED_HOSTS = ['*']
```

---

## 🌐 Server Configuration

### HOST and PORT

```python
# Bind address
HOST = '0.0.0.0'  # Listen on all interfaces
# HOST = '127.0.0.1'  # Listen on localhost only

# Port number
PORT = 8000

# Or override via command line
# duck runserver --host 0.0.0.0 --port 3000
```

### WORKERS

Number of worker processes:

```python
# Single worker (default)
WORKERS = 1

# Multiple workers (recommended for production)
WORKERS = 4  # Usually number of CPU cores

# Auto-detect CPU count
import os
WORKERS = os.cpu_count()
```

---

## 🔒 HTTPS Configuration

### Basic HTTPS

```python
# Enable HTTPS
HTTPS = True

# HTTP redirect to HTTPS
HTTP_REDIRECT = True
```

### Manual SSL Certificate

```python
HTTPS = True
AUTO_SSL = False
SSL_CERT = '/path/to/certificate.crt'
SSL_KEY = '/path/to/private.key'
SSL_CHAIN = '/path/to/chain.pem'  # Optional
```

### Automatic SSL (Let's Encrypt)

```python
HTTPS = True
AUTO_SSL = True
DOMAIN = 'yourdomain.com'
EMAIL = 'admin@yourdomain.com'  # For renewal notifications

# Certificate storage
SSL_CERT_PATH = '/etc/ssl/duck/'
```

---

## 💾 Database Configuration

### SQLite (Default)

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite3',
    }
}
```

### PostgreSQL

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'your_db_name',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'localhost',
        'PORT': '5432',
        'CONN_MAX_AGE': 600,  # Connection pooling
    }
}
```

### MySQL/MariaDB

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'your_db_name',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
        },
    }
}
```

### Multiple Databases

```python
DATABASES = {
    'default': {
        # Primary database
    },
    'analytics': {
        # Analytics database
    },
    'cache': {
        # Cache database
    }
}

# Use in code
# User.objects.using('analytics').all()
```

---

## 🗂️ Static Files

### Configuration

```python
# URL prefix for static files
STATIC_URL = '/static/'

# Directory for collected static files
STATIC_ROOT = '/var/www/duck/static/'

# Additional static file locations
STATICFILES_DIRS = [
    'web/ui/static',
    'additional/static/path',
]
```

### Collect Static Files

```bash
duck collectstatic
```

---

## 📝 Template Configuration

```python
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            'web/ui/templates',
            'custom/templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
```

---

## 📦 Caching

### Memory Cache (Development)

```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}
```

### Redis Cache (Production)

```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'duck',
        'TIMEOUT': 300,
    }
}
```

### Memcached

```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.PyMemcacheCache',
        'LOCATION': '127.0.0.1:11211',
    }
}
```

---

## 📬 Session Configuration

```python
# Session engine
SESSION_ENGINE = 'django.contrib.sessions.backends.db'  # Database
# SESSION_ENGINE = 'django.contrib.sessions.backends.cache'  # Cache
# SESSION_ENGINE = 'django.contrib.sessions.backends.file'  # File

# Session cookie settings
SESSION_COOKIE_AGE = 1209600  # 2 weeks in seconds
SESSION_COOKIE_NAME = 'duck_session'
SESSION_COOKIE_SECURE = True  # HTTPS only
SESSION_COOKIE_HTTPONLY = True  # No JavaScript access
SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection

# Save session on every request
SESSION_SAVE_EVERY_REQUEST = False
```

---

## 🔐 Security Settings

### CSRF Protection

```python
# Enable CSRF protection (default)
CSRF_COOKIE_SECURE = True  # HTTPS only
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_TRUSTED_ORIGINS = ['https://yourdomain.com']
```

### Security Headers

```python
# Security headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# HSTS (HTTP Strict Transport Security)
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# SSL/HTTPS
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

### Content Security Policy

```python
CSP_DEFAULT_SRC = ["'self'"]
CSP_SCRIPT_SRC = ["'self'", "'unsafe-inline'", "cdn.example.com"]
CSP_STYLE_SRC = ["'self'", "'unsafe-inline'"]
CSP_IMG_SRC = ["'self'", "data:", "https:"]
```

---

## 📊 Logging Configuration

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/duck.log',
            'maxBytes': 1024 * 1024 * 10,  # 10MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'duck': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
```

---

## 🗜️ Compression

```python
# Enable compression
COMPRESSION_ENABLED = True

# Compression algorithms (in order of preference)
COMPRESSION_ALGORITHMS = ['br', 'gzip', 'deflate']

# Minimum response size to compress (bytes)
COMPRESSION_MIN_SIZE = 500

# Compression level (1-9, higher = more compression)
COMPRESSION_LEVEL = 6

# Don't compress streaming responses
COMPRESS_STREAMING_RESPONSES = False
```

---

## 🌐 CORS Configuration

```python
# Enable CORS
CORS_ENABLED = True

# Allowed origins
CORS_ALLOWED_ORIGINS = [
    'https://example.com',
    'https://subdomain.example.com',
]

# Or allow all (NOT recommended for production)
CORS_ALLOW_ALL_ORIGINS = True

# Allowed methods
CORS_ALLOWED_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

# Allowed headers
CORS_ALLOWED_HEADERS = [
    'accept',
    'authorization',
    'content-type',
]
```

---

## ⚡ Performance Settings

### Connection Limits

```python
# Maximum concurrent connections
MAX_CONNECTIONS = 1000

# Connection timeout (seconds)
CONNECTION_TIMEOUT = 30

# Keep-alive timeout (seconds)
KEEP_ALIVE_TIMEOUT = 5
```

### Request Limits

```python
# Maximum request size (bytes)
MAX_REQUEST_SIZE = 10 * 1024 * 1024  # 10MB

# Maximum upload size (bytes)
MAX_UPLOAD_SIZE = 100 * 1024 * 1024  # 100MB

# Request timeout (seconds)
REQUEST_TIMEOUT = 60
```

---

## 🔄 WebSocket Configuration

```python
# Enable WebSocket support
WEBSOCKET_ENABLED = True

# WebSocket path
WEBSOCKET_PATH = '/ws/'

# WebSocket timeout (seconds)
WEBSOCKET_TIMEOUT = 300

# Per-message compression
WEBSOCKET_COMPRESSION = True
```

---

## 📧 Email Configuration

```python
# Email backend
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# SMTP settings
# IMPORTANT: Use environment variables for sensitive credentials!
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')  # Never hardcode passwords!
DEFAULT_FROM_EMAIL = 'noreply@yourdomain.com'
```

---

## 🌍 Internationalization

```python
# Language code
LANGUAGE_CODE = 'en-us'

# Time zone
TIME_ZONE = 'UTC'

# Enable internationalization
USE_I18N = True

# Enable localization
USE_L10N = True

# Enable timezone support
USE_TZ = True

# Available languages
LANGUAGES = [
    ('en', 'English'),
    ('es', 'Spanish'),
    ('fr', 'French'),
]
```

---

## 🔧 Environment-Specific Configuration

### Using Environment Variables

```python
import os

# Load from environment
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
SECRET_KEY = os.environ.get('SECRET_KEY')
DATABASE_URL = os.environ.get('DATABASE_URL')

# Parse database URL
import dj_database_url
DATABASES = {
    'default': dj_database_url.config(default=DATABASE_URL)
}
```

### Multiple Configuration Files

```python
# settings/__init__.py
from .base import *

if os.environ.get('ENVIRONMENT') == 'production':
    from .production import *
else:
    from .development import *
```

---

## 📚 Additional Resources

- [Deployment Guide](Deployment)
- [Security Best Practices](Security)
- [Performance Optimization](Performance)
- [Full Documentation](https://docs.duckframework.xyz)

---

Configuration is key to a successful deployment! 🔧
