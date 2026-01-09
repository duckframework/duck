# 🛡️ Duck Middlewares

[![Middleware](https://img.shields.io/badge/Feature-Middleware-blue?style=for-the-badge)](#)  
[![Duck Framework](https://img.shields.io/badge/Powered%20By-Duck-orange?style=for-the-badge&logo=duckframework)](#)

---

Duck middlewares allow you to **intercept, process, and modify HTTP requests and responses**.  
They provide a flexible mechanism for **logging, validation, authentication, and more**.

---

## 🏗️ Base Middleware Class

All custom middlewares in Duck inherit from **`BaseMiddleware`**:

```py
from duck.http.middlewares import BaseMiddleware
from duck.http.request import HttpRequest
from duck.http.response import HttpBadRequestResponse, HttpResponse


class MyMiddleware(BaseMiddleware):
    @classmethod
    def process_request(cls, request: HttpRequest) -> int:
        # Custom request processing logic
        return cls.request_ok  # or cls.request_bad

    @classmethod
    def process_response(cls, response: HttpResponse, request: HttpRequest) -> None:
        # Modify response before sending
        pass
```

---

### ⚡ Key Attributes

| Attribute          | Type      | Description |
|-------------------|----------|-------------|
| `debug_message`    | `str`    | Message for debugging errors in middleware (default: `"Middleware error"`) |
| `request_ok`       | `int`    | Indicates request is valid (default: `1`) |
| `request_bad`      | `int`    | Indicates request has issues (default: `0`) |

> Each middleware subclass manages its own attributes independently.  
> Middleware class names must be unique to behave independently.

---

### 🔧 Class Methods

#### `process_request(request: HttpRequest) -> int`

- Implement this method to **inspect incoming requests**.  
- Return `BaseMiddleware.request_ok` if valid or `BaseMiddleware.request_bad` to indicate an error.  

#### `get_error_response(request: HttpRequest) -> HttpResponse`

- Returns the **default error response** when `process_request` returns `request_bad`.

```py
HttpBadRequestResponse("Sorry there is an error in Request, that's all we know!")
```

#### `process_response(response: HttpResponse, request: HttpRequest) -> None`

- Modify the outgoing response before it is sent to the client.  
- Optional to override depending on your middleware logic.

---

### 💡 Notes

- You can return `request_bad` **even if the request has no errors** to override the final response from `get_error_response`.  
- Use middlewares for **authentication, logging, validation, rate-limiting**, or any cross-cutting concerns.  
- Duck middlewares are **class-based**, so no instance creation is required.

---

✨ Duck’s middleware system gives you **powerful control over request/response flow** while keeping the API simple and flexible.
