# 🚀 Deployment Guide  

![Python Version](https://img.shields.io/badge/python-≥3.10%20|%203.12+-blue.svg)
![Platform](https://img.shields.io/badge/platform-Linux-green.svg)
![Deployment](https://img.shields.io/badge/deployment-easy-brightgreen.svg)
![HTTPS](https://img.shields.io/badge/https-supported-blue.svg)
![Duck](https://img.shields.io/badge/framework-Duck-orange.svg)

Deploying your **Duck** web application is simple, fast, and beginner-friendly — no need for extra tools like **NGINX**, **Daphne**, or other ASGI/WSGI gateways.  

---

### 🧠 Prerequisites  

```{note}
**Required Python version:** `>= 3.10` (recommended: **3.12+**)  
**Recommended OS:** Linux (many Duck features rely on Linux system features).  
```

---

## Steps to Deploy Your Duck Application  

### 1. Create and Activate a Virtual Environment  

A [**virtual environment (venv)**](https://www.w3schools.com/python/python_virtualenv.asp) helps keep your project dependencies isolated and clean.  

Run these commands in your project directory:  

```bash
python3.12 -m venv .venv # Or python3.10 upto latest python version
```

Then activate it:  

```bash
source .venv/bin/activate
```

You should now see something like:  

```bash
$ (venv)
```

After activation, install your dependencies using `pip`.  

```{note}
✅ Use Python **3.12 or later** for best performance and compatibility.  
✅ On Linux, you can install a modern Python version using `sudo apt install python3.12` or [`pyenv`](https://github.com/pyenv/pyenv).  
🚫 Avoid misusing `sudo` as this grants you admin rights.  
```

---

### 2. Run Duck as Root  

When running your **Duck** app on a VPS or remote server, you may want to use **port 80** (HTTP) or **443** (HTTPS).  
These ports require **admin privileges**, so a normal command like `duck runserver` won’t work directly.  

To solve this, use the following command that gives **Duck** the necessary permissions safely:  

```bash
sudo $(python -c "import sys; print(sys.executable)") -m duck runserver ... # Or run web/main.py
```

💡 **Explanation:**  
This command runs **Duck** using the exact Python executable you installed it with, avoiding common issues like  
`ModuleNotFoundError: No module named 'duck'`.

---

### 3. Obtain an SSL Certificate  

Duck provides **built-in, free SSL support** via [Let’s Encrypt](https://letsencrypt.org/).  

Follow the [Free SSL Certificate Guide](./free-ssl-certificate.md) for step-by-step instructions.  
Once configured, Duck can **auto-renew certificates** without manual action.  

---

### 4. Enable HTTPS & HTTP/2  

After obtaining your SSL certificate, enable **HTTPS** and **HTTP/2** for secure and faster connections.  

See [HTTPS and HTTP/2 setup guide](./https-and-http2.md) for full configuration details.  

---

### 5. Redirect All HTTP Traffic to HTTPS  

Ensure users visiting your site via `http://` are automatically redirected to `https://`.  

In your `settings.py`, enable HTTPS redirection:  

```python
FORCE_HTTPS = True
FORCE_HTTPS_BIND_PORT = 80  # Optional: specify the port to redirect from
```

Duck uses a built-in **MicroApp** called `HttpsRedirectMicroApp` to handle redirects efficiently.  
See [MicroApp documentation](./microapp.md) for customization details.  

---

### 6. Run the App as a Background Service  

```{warning}
The `duck service` command works only on **Linux**.
```

To keep your app running even after closing your terminal, run it as a background service:  

```bash
$ (venv) sudo $(python -c "import sys; print(sys.executable)") -m duck service autorun # or just use duck service autorun for less privileges
```

This command will:  
- Automatically create a **systemd service** for your app  
- Save it under your system’s service directory  
- Start it instantly  

``` {note}
- Do not forget to customize `SYSTEMD_EXEC_COMMAND` in `settings.py`, this is the command that will be run 
by `systemd`. By default the command points to `f"{sys.executable} web/main.py"`. Usually, it's only 
necessary to configure this if you are explicitly using `duck runserver` instead of `web/main.py`. 
- Do not forget to activate your virtual environment where you installed `Duck`.
```

For advanced options, see [Service Management](./service-management.md).  

💡 **Tip:** On non-Linux systems, you can use tools like **systemd**, **supervisord**, or **pm2** as alternatives.  

---

## 📝 Notes & Best Practices  

``` {note}
It is strongly recommended to use the asynchronous implementation ([ASGI](./asgi.md)) 
rather than the synchronous ([WSGI](./wsgi.md)) interface in production environments. 
ASGI provides superior scalability and efficiency by leveraging a non-blocking event 
loop, making it better suited for modern high-concurrency workloads.
```

Before going live, make sure your application is optimized and secure:  

- **Make sure you set the app domain:**
  ```bash
  python3 -m duck runserver -d mysite.com # Or just use your IP if no domain
  ```
  
  **Or provide it to `App` instance:**
  ```
  app = App(domain="mysite.com") # Or your IP if no domain
  ```
  
  But also, don't forget to set it in `SYSTEMD_EXEC_COMMAND` in `settings.py` if you are explicilty using `duck runserver` 
  instead of `web/main.py`.
  
- **Use workers:**
  ```python
  # From command line
  duck runserver --workers auto # Or just specify number of workers.
  ```
  
  ```python
  # From web/main.py
  app = App(..., workers=os.cpu_count() or 4, force_https_workers=2)
  ```
  
  The above examples runs the server using worker processes, thus, utilizing 
  the available CPU cores. This improves overall performance. As this brings more benefits, it 
  also uses more system resources as some background threads will be restarted in each process.

- **Turn off debug mode:**  
  ```python
  DEBUG = False
  ```
  
- **Silence unnecessary logs:**  
  ```python
  SILENT = True
  LOG_TO_FILE = True
  ```
  
- **Reduce log verbosity (optional):**  
  ```python
  VERBOSE_LOGGING = False
  ```
  
- **Monitor your application:**  
  ```bash
  duck monitor # Auto-detect all processes starting with duck
  ```
  
  or explicitly provide target processes:
  ```bash
  duck monitor --duck-process "duck*"  # Matches all processes starting with duck
  ```
  
  or explicitly provide target process IDs: 
  ```bash
  duck monitor --pid <process_id>
  ```
  
- **Open required ports:**  
  Make sure ports **80** (HTTP), **443** (HTTPS) and other ports like **465** (SMTPS port for sending and receiving emails) are open in your VPS or hosting firewall settings.  

---

## 🎉 You’re Done!  

Your **Duck** web app is now fully deployed and production-ready.  
Keep your environment updated, monitor performance, and enjoy a smooth deployment process — all powered by **Duck**.  
