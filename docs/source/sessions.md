# 🔐 Sessions in Duck

[![Session Management](https://img.shields.io/badge/Feature-Session-blue?style=for-the-badge)](#)  
[![Duck Framework](https://img.shields.io/badge/Powered%20By-Duck-orange?style=for-the-badge&logo=duckframework)](#)

---

Duck provides **robust session management** using `SessionMiddleware`.  
This middleware is responsible for **loading, saving, and managing sessions** in a flexible way.

---

## 🗃️ Session Storage Options

Duck supports multiple session storage backends:

- **In-memory cache:** `duck.utils.caching.InMemoryCache` — fast but temporary.  
- **Key-as-folder cache:** `duck.utils.caching.KeyAsFolderCache` — stores sessions in filesystem folders.  
- **Dynamic file cache:** `duck.utils.caching.DynamicFileCache` — flexible file-based storage.  

> You can also implement a **custom cache class**, but it must provide: `set`, `get`, `delete`, `clear`, and `save` methods.

---

## ⚡ Accessing Sessions

- Access the request session via `request.SESSION` or `request.session`.  
- Sessions are **lazily saved**, meaning they are written only if there are changes.  
- To change session storage, set `SESSION_STORAGE` in `settings.py`.  

### Example:

```py
# views.py
from duck.http.response import HttpResponse

def some_view(request):
    request.SESSION["some_key"] = some_value # Or use request.session
    return HttpResponse("Hello world")
```

**Notes:**
- Request sessions are lazily saved if changes are detected.
- For important sessions or sessions that require immediate saving, you can use the method `save` on request session to explicitly save the request session. 

---

## 🛠️ Session Settings

Most defaults are safe, but you can customize as needed:

### Session Engine

The engine handling session operations.

- Avoid overriding unless necessary.  
- For Django integration (`USE_DJANGO=True`), you must implement a custom Django session backend.

### Session Directory

Directory where session files are stored (if using file-based storage).

- Database-backed sessions: set to `None`.  
- Directory will be auto-created if it doesn’t exist.

### Session Cookie Name

Name of the cookie storing the session ID.  
- Default: `session_id`

### Session Duration

Lifetime of the session in seconds.  
- Default: 7 days (`604800` seconds)

### Session Cookie Path

Path attribute for session cookie.  
- Default: `'/'`

### Session Cookie Domain

Domain attribute for session cookie.  
- Default: `None` → resolves to Duck app domain

### Session Expire at Browser Close

Whether the session expires when the browser is closed.  
- Default: `False`

### Session Cookie Secure

Restricts cookie to HTTPS.  
- Default: `False`

### Session Cookie HttpOnly

Restricts access via JavaScript.  
- Default: `True`

### Session Cookie SameSite

Controls cross-site request behavior.  
- Default: `"Lax"`

---

## 💡 Notes & Tips

- Duck sessions are **lightweight and flexible** for both short and long-lasting sessions.  
- Always pick a session backend that fits your **performance and persistence needs**.  
- Combine with Duck’s **middleware and async features** for secure, scalable web apps.

---

✨ With Duck sessions, you can **manage user data efficiently** while keeping control over cookies, storage, and lifetime 🚀  

