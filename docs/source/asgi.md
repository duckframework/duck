# ⚡ Asynchronous Server Gateway (ASGI)

[![Async Ready](https://img.shields.io/badge/Async-Ready-brightgreen?style=for-the-badge&logo=python)](#)  
[![WebSocket Support](https://img.shields.io/badge/WebSocket-Supported-blue?style=for-the-badge&logo=websocket)](#)  
[![HTTP/2 Support](https://img.shields.io/badge/HTTP%2F2-Supported-purple?style=for-the-badge&logo=fastapi)](#)  

---

Duck comes with **built-in asynchronous support** right out of the box.  
From custom sockets (`xsockets`) to full async handling, everything is designed for **speed, scalability, and modern protocols** 🚀

---

## 🔧 Enabling Async Handling

Simply add the following setting in your **`settings.py`**:

```py
ASYNC_HANDLING = True
```

This single flag turns on **asynchronous request handling** in your app.  

---

## 📝 Notes

- ✅ The default **ASGI** handles everything automatically – no need to modify unless you want custom behavior.  
- 🌐 Async environment supports protocols like **WebSockets** and **HTTP/2** natively.  
- 🌀 While it’s recommended to define your views as async, **non-async views will still work** (they’re automatically converted).  
- ⚙️ Want a different event loop? Set `ASYNC_LOOP` (e.g. `uvloop`) in your settings.  

---

## 👨‍💻 Defining Async Views

You can define async views in two main ways:

### 1️⃣ Async Views as Functions

```py
# views.py

async def myview(request):
    # Some async code to return HttpResponse
    ...
```

---

### 2️⃣ Async Views as Classes

```py
# views.py

from duck.views import View

class MyView(View):
    def strictly_async(self):
        # Return True to force this view to always use async
        # (disables automatic sync → async conversion).
        ...
        
    async def run(self):
        # Some async code to return HttpResponse
        ...
```

---

✨ With Duck’s ASGI, you get **true async support**, seamless integration with modern protocols, and the flexibility to use **function-based** or **class-based async views**.  
Start writing async today and unlock maximum performance! 🚀
