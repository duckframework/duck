# 🖥️ Web Server Gateway (WSGI)

[![Sync Ready](https://img.shields.io/badge/Sync-Ready-brightgreen?style=for-the-badge&logo=python)](#)  
[![Threaded](https://img.shields.io/badge/Threading-Supported-blue?style=for-the-badge&logo=windows-terminal)](#)  
[![Async Compatible](https://img.shields.io/badge/Async-Compatible-purple?style=for-the-badge&logo=fastapi)](#)  
[![Duck Framework](https://img.shields.io/badge/Powered%20By-Duck-orange?style=for-the-badge&logo=duckframework)](#)

---

Duck’s **WSGI** implementation brings you the best of both worlds:  
⚡ Traditional multithreading for sync workloads, plus support for **async protocols like HTTP/2 & WebSockets**.  

Unlike most WSGI servers, Duck’s version isn’t limited — it runs a [**background event loop**](./background-managers.md) so async tasks can still flow smoothly 🚀.  

---

## 🔧 Enabling WSGI Mode

In your **`settings.py`**, simply set:

```py
ASYNC_HANDLING = False
```

This switches the server into **WSGI (synchronous) mode**.  

---

## 🌀 Working with the Event Loop

Duck automatically runs a background **asyncio event loop** to handle async protocols even in sync mode.  

You can access it with:  
[`duck.utils.asyncio.eventloop.get_or_create_loop_manager`](./background-managers.md)  

- 🛠 Run coroutines in the background with `submit_task`.  
- 🔄 Returns either an **async future** or a **sync future** (so you can `.wait()` in synchronous code).  
- 📖 Use `help(duck.utils.asyncio.eventloop)` for more details.  

---

## 📝 Notes

- ✅ The default **WSGI** does everything for you — only override if necessary.  
- 🔄 In synchronous environments, define your views as **regular sync functions**.  
- ⚡ Async views are also supported — they’ll be **automatically converted to sync**.  

---

## 👨‍💻 Defining Sync Views

### 1️⃣ Function-based Views

```py
# views.py

def myview(request):
    # Some code here to return HttpResponse
    ...
```

---

### 2️⃣ Class-based Views

```py
# views.py

from duck.views import View

class MyView(View):
    def run(self):
        # Some code to return HttpResponse
        ...
```

---

✨ With Duck’s WSGI, you get **classic sync stability** with a touch of **modern async compatibility**.  
Perfect for apps that need **threading performance** while still being ready for protocols like **WebSockets & HTTP/2** 🌐  

---

👉 Looking for **full async mode**? Check out [⚡ ASGI](./asgi.md)
