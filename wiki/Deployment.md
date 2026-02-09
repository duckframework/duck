# 🚢 Deployment Guide

Learn how to deploy your Duck application to production.

---

## 🎯 Deployment Overview

Duck is designed to run directly in production without requiring nginx or Apache. However, it also works great behind a reverse proxy if you prefer.

### Deployment Options

1. **Standalone Server** - Duck handles everything (recommended)
2. **Behind Reverse Proxy** - Use nginx/Apache for additional features
3. **Containerized** - Deploy with Docker
4. **Cloud Platforms** - Deploy to AWS, GCP, Azure, etc.

---

## 🚀 Quick Production Deployment

### 1. Prepare Your Application

```bash
# Navigate to your project
cd myproject

# Update settings for production
# Edit web/settings.py
```

### 2. Configure Production Settings

Edit `web/settings.py`:

```python
# Production settings
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']

# HTTPS Configuration
HTTPS = True
AUTO_SSL = True
DOMAIN = 'yourdomain.com'
EMAIL = 'admin@yourdomain.com'  # For Let's Encrypt

# Security
SECRET_KEY = 'your-secret-key-here'  # Generate a strong key!
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Performance
WORKERS = 4  # Number of CPU cores

# Database (for production)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'your_db_name',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 3. Install as System Service

```bash
# Install Duck as a systemd service
sudo duck service install

# Start the service
sudo duck service start

# Enable auto-start on boot
sudo duck service enable

# Check status
sudo duck service status
```

### 4. Configure Firewall

```bash
# Allow HTTP and HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

Your application is now live! 🎉

---

## 🔒 SSL/TLS Configuration

### Automatic SSL (Let's Encrypt)

Duck can automatically obtain and renew SSL certificates:

```python
# web/settings.py
HTTPS = True
AUTO_SSL = True
DOMAIN = 'yourdomain.com'
EMAIL = 'admin@yourdomain.com'
```

**Requirements:**
- Domain must point to your server (DNS A record)
- Port 80 must be accessible (for validation)
- Port 443 must be accessible (for HTTPS)

Duck will:
1. Request certificate from Let's Encrypt
2. Install the certificate
3. Configure HTTPS
4. Set up automatic renewal

### Manual SSL Certificate

If you have your own certificate:

```python
# web/settings.py
HTTPS = True
AUTO_SSL = False
SSL_CERT = '/path/to/certificate.crt'
SSL_KEY = '/path/to/private.key'
```

### Testing SSL

```bash
# Test SSL configuration
openssl s_client -connect yourdomain.com:443

# Check certificate expiration
duck ssl-check
```

---

## 🐳 Docker Deployment

### Create Dockerfile

```dockerfile
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose ports
EXPOSE 80 443

# Run application
CMD ["duck", "runserver", "--port", "80"]
```

### Create docker-compose.yml

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./logs:/app/logs
      - ./ssl:/app/ssl
    environment:
      - DEBUG=False
      - DOMAIN=yourdomain.com
    restart: unless-stopped

  db:
    image: postgres:13
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=duckdb
      - POSTGRES_USER=duckuser
      - POSTGRES_PASSWORD=secure_password
    restart: unless-stopped

volumes:
  postgres_data:
```

### Deploy with Docker

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

---

## 🌐 Behind Reverse Proxy

### nginx Configuration

Create `/etc/nginx/sites-available/duck`:

```nginx
upstream duck {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL Configuration
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000" always;

    location / {
        proxy_pass http://duck;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket support
    location /ws/ {
        proxy_pass http://duck;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

Enable and restart nginx:

```bash
sudo ln -s /etc/nginx/sites-available/duck /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Update Duck Settings

```python
# web/settings.py
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
```

---

## ☁️ Cloud Platform Deployment

### AWS EC2

1. **Launch Instance**
   - Choose Ubuntu 20.04+ or Amazon Linux 2
   - t2.micro or larger
   - Configure security groups (ports 80, 443)

2. **Install Duck**
   ```bash
   ssh ubuntu@your-ec2-ip
   sudo apt update
   sudo apt install python3-pip
   pip3 install git+https://github.com/duckframework/duck.git
   ```

3. **Deploy Application**
   ```bash
   git clone your-repo
   cd your-app
   sudo duck service install
   sudo duck service start
   ```

### DigitalOcean Droplet

Similar to EC2, follow the same steps on a Droplet with Ubuntu.

### Google Cloud Platform

1. Create VM instance
2. Allow HTTP/HTTPS traffic
3. Follow standard installation steps

### Heroku

Create `Procfile`:
```
web: duck runserver --port $PORT
```

Deploy:
```bash
heroku create your-app-name
git push heroku main
```

---

## 📊 Monitoring

### Built-in Monitoring

```bash
# Real-time system monitoring
duck monitor

# View CPU, RAM, disk, I/O
```

### Log Management

```bash
# View logs
duck logs

# Tail logs
duck logs --tail 100

# Filter by level
duck logs --level ERROR
```

### Health Checks

Add health check endpoint:

```python
# web/ui/pages/views.py
from duck.http import JsonResponse

def health_check(request):
    return JsonResponse({
        'status': 'healthy',
        'version': '1.0.0'
    })

# web/urls.py
Path('/health', health_check, name='health'),
```

---

## 🔄 Zero-Downtime Deployment

### Using systemd

```bash
# Reload without downtime
sudo duck service reload

# Or manually
sudo systemctl reload duck
```

### Blue-Green Deployment

1. Deploy new version to different port
2. Test new version
3. Switch traffic to new version
4. Shut down old version

---

## 🛠️ Performance Tuning

### Worker Processes

```python
# web/settings.py
WORKERS = 4  # Match CPU cores
```

### Database Connection Pooling

```python
DATABASES = {
    'default': {
        # ... other settings
        'CONN_MAX_AGE': 600,  # 10 minutes
    }
}
```

### Caching

```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

### Static File Optimization

```bash
# Collect static files
duck collectstatic

# Configure CDN in settings
STATIC_URL = 'https://cdn.yourdomain.com/static/'
```

---

## 🔐 Security Checklist

Before going to production:

- [ ] Set `DEBUG = False`
- [ ] Use strong `SECRET_KEY`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Enable HTTPS
- [ ] Use environment variables for secrets
- [ ] Configure firewall
- [ ] Regular security updates
- [ ] Enable CSRF protection
- [ ] Secure session cookies
- [ ] Configure Content Security Policy
- [ ] Set up SSL/TLS properly
- [ ] Implement rate limiting
- [ ] Regular backups

---

## 📦 Database Migration

```bash
# Run migrations
duck migrate

# Create superuser
duck createsuperuser

# Backup database
duck dumpdata > backup.json
```

---

## 🆘 Troubleshooting Production Issues

### Service Won't Start

```bash
# Check service status
sudo duck service status

# View service logs
sudo journalctl -u duck -n 50

# Check permissions
ls -la /var/log/duck/
```

### High Memory Usage

```bash
# Reduce workers
WORKERS = 2  # In settings.py

# Monitor memory
duck monitor
```

### SSL Certificate Issues

```bash
# Check certificate
duck ssl-check

# Renew manually
sudo certbot renew

# Check Let's Encrypt logs
sudo cat /var/log/letsencrypt/letsencrypt.log
```

---

## 📚 Additional Resources

- [Security Best Practices](Security)
- [Performance Optimization](Performance)
- [Monitoring Guide](Monitoring)
- [Backup Strategies](Backup)

---

Need help with deployment? Ask in [GitHub Discussions](https://github.com/duckframework/duck/discussions)!
