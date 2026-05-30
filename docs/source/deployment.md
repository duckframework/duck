# 🚀 Deployment Guide  

![Python Version](https://img.shields.io/badge/python-≥3.10%20|%203.12+-blue.svg)
![Platform](https://img.shields.io/badge/platform-Linux-green.svg)
![Deployment](https://img.shields.io/badge/deployment-easy-brightgreen.svg)
![HTTPS](https://img.shields.io/badge/https-supported-blue.svg)
![Duck](https://img.shields.io/badge/framework-Duck-orange.svg)

Deploying your Duck web application is simple, fast, and beginner-friendly — no need for extra tools like NGINX, Daphne, or other ASGI/WSGI gateways.

---

## Prerequisites

**Required Python version:** `>= 3.10` (recommended: **3.12+**)
**Recommended OS:** Linux (many Duck features rely on Linux system features).

---

## Deploying on a VPS (Manual)

### 1. Create and Activate a Virtual Environment

A virtual environment keeps your project dependencies isolated and clean.

Run these commands in your project directory:

```bash
python3.12 -m venv .venv  # Or python3.10 up to the latest Python version
```

Then activate it:

```bash
source .venv/bin/activate
```

You should now see something like:

```
(venv) $
```

After activation, install your dependencies using pip.

> ✅ Use Python **3.12 or later** for best performance and compatibility.
> ✅ On Linux, install a modern Python version via `sudo apt install python3.12` or [`pyenv`](https://github.com/pyenv/pyenv).
> 🚫 Avoid misusing `sudo` — it grants full admin rights.

---

### 2. Run Duck as Root

When running on a VPS, you may want to bind to port 80 (HTTP) or 443 (HTTPS). These ports require elevated privileges.

Use this command to run Duck with the correct Python executable safely:

```bash
sudo $(python -c "import sys; print(sys.executable)") web/main.py
```

> 💡 This ensures Duck uses the exact Python executable from your virtual environment, avoiding `ModuleNotFoundError: No module named 'duck'`.

It is **recommended to run your app via `web/main.py`** rather than `duck runserver`. `main.py` gives you full programmatic control over the `App` instance — workers, domains, HTTPS, and more — making it more flexible for production use.

---

### 3. Obtain an SSL Certificate

Duck provides built-in, free SSL support via Let's Encrypt.

Follow the [Free SSL Certificate Guide](./ssl.md) for step-by-step instructions. Once configured, Duck can auto-renew certificates without manual action.

---

### 4. Enable HTTPS & HTTP/2

After obtaining your SSL certificate, enable HTTPS and HTTP/2 for secure, faster connections.

See the [HTTPS and HTTP/2 setup guide](./https.md) for full configuration details.

---

### 5. Redirect HTTP Traffic to HTTPS

Ensure users visiting via `http://` are automatically redirected to `https://`.

In your `settings.py`:

```python
HTTPS_REDIRECT = True
HTTPS_REDIRECT_BIND_PORT = 80  # Optional: port to redirect from
```

Duck uses a built-in `HttpsRedirectMicroApp` to handle redirects efficiently. See the [MicroApp documentation](./microapp.md) for customization details.

To redirect `www` traffic to your non-www domain, add this middleware at the second position in your default middlewares in `settings.py`:

```
duck.http.middlewares.contrib.WWWRedirectMiddleware
```

---

### 6. Run as a Background Service

> ⚠️ The `duck service` command works on **Linux only**.

To keep your app running after closing your terminal, register it as a systemd service:

```bash
sudo $(python -c "import sys; print(sys.executable)") -m duck service autorun
```

This will:

- Automatically create a systemd service for your app
- Save it to your system's service directory
- Start it immediately

**Important:**

- Set `SYSTEMD_EXEC_COMMAND` in `settings.py` to the command systemd will run. It defaults to `f"{sys.executable} web/main.py"`. You only need to change this if you're explicitly using `duck runserver` instead of `web/main.py`.
- Make sure your virtual environment is activated before running this command.

For advanced options, see [Service Management](./service.md).

> 💡 On non-Linux systems, alternatives like `supervisord` or `pm2` can manage background processes.

---

## Deploying via an External Hosting Provider

When deploying to an external platform (e.g., Heroku, Render, Railway, or similar), Duck still handles everything internally — no additional ASGI/WSGI server needed.

### Key Difference: Set Your Server URL

External hosting platforms typically place your app behind a **reverse proxy**, which means Duck may not be able to infer the correct public-facing URL automatically. You must set `server_url` explicitly.

In `web/main.py`:

```python
app = App(
    domain="mysite.com",
    server_url="https://mysite.com",  # Required when behind a reverse proxy
)
```

> ⚠️ Skipping `server_url` on hosted platforms can cause incorrect redirect URLs, broken WebSocket connections, and other subtle issues.

### Platform-Specific Notes

- Most platforms assign a dynamic port via the `PORT` environment variable. Make sure your `main.py` reads it:

```python
import os

app = App(
    domain="mysite.com",
    server_url="https://mysite.com",
    port=int(os.environ.get("PORT", 8000)),
)
```

- SSL is usually handled by the platform's proxy — you typically do **not** need to configure Let's Encrypt yourself.
- The `duck service` command is **not applicable** on managed platforms. Use the platform's process manager (e.g., a `Procfile` on Heroku).

---

## Notes & Best Practices

It is strongly recommended to use the **asynchronous (ASGI)** implementation rather than the synchronous (WSGI) interface in production. 
ASGI provides superior scalability by leveraging a non-blocking event loop — better suited for high-concurrency workloads.

### Domain

```python
# web/main.py
app = App(domain="mysite.com")  # Or your IP if no domain
```

### Workers

```python
# web/main.py
app = App(
    ...,
    workers=os.cpu_count() or 4,
    https_redirect_workers=4,
)
```

Or via CLI:

```bash
duck runserver --workers auto
```

Workers improve throughput by handling requests concurrently. By default, worker **threads** are used (suitable for most apps requiring worker synchronization). If your app does not require inter-worker synchronization, you can switch to worker **processes** for better CPU isolation:

```python
app = App(
    ...,
    workers=os.cpu_count() or 4,
    force_worker_processes=False,
    https_redirect_force_worker_processes=True,
)
```

### Production Checklist

```python
# settings.py

DEBUG = False

SILENT = True        # Suppress unnecessary output
LOG_TO_FILE = True   # Persist logs to disk

VERBOSE_LOGGING = False  # Reduce log verbosity
```

### Monitoring

```bash
duck monitor  # Auto-detects all Duck processes
```

Or target specific processes:

```bash
duck monitor --duck-process "duck*"   # Match by name pattern
duck monitor --pid <process_id>       # Match by PID


### Open Required Ports

Ensure the following ports are open in your VPS or hosting firewall:

| Port | Purpose |
|------|---------|
| 80   | HTTP |
| 443  | HTTPS |
| 465  | SMTPS (email) |

---

## You're Done!

Your Duck web app is now fully deployed and production-ready. Keep your environment updated, monitor performance, and enjoy a smooth deployment process — all powered by Duck. 🦆
