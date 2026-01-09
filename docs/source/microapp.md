# ⛴️ Micro Applications

## What is a Micro App?

A **Micro App** is a small, independent application that runs on its own server (HTTP or HTTPS) and port. It can be part of a larger Duck-powered project but operates separately, handling its own requests and responses.

---

## Key Features

- **Independent Servers**: Each micro app runs on its own server, meaning it does not affect other parts of the application.
- **Custom Ports**: You can assign a specific port for your micro app, so it won’t interfere with other services.
- **Custom Views**: Micro apps handle their own requests through a `view` method or `async_view` for asynchronous support, allowing you to define custom behavior.
- **Redirect HTTP to HTTPS**: Duck includes a built-in **HttpsRedirectMicroApp**, which automatically redirects HTTP traffic to HTTPS for better security.

``` {note}
Middlewares are **not applied automatically** — you must manually attach them to either the `request` or the `response`.  
This design allows for clearer separation between your **main application** and **micro applications**, especially in cases where certain middlewares are not applicable to micro apps.

To simplify default middleware or error handling, you can use the built-in processors:

- Use the default `RequestProcessor` or `AsyncRequestProcessor`—both can be passed to a micro app’s `view` or `async_view` methods.  
  These processors provide convenient methods like:
  - `check_middlewares()`
  - `check_base_errors()`
  - `check_errors()`

- Alternatively, use the ASGI/WSGI integration via  
  `duck.settings.loaded.SettingsLoaded`.

For example, you can use:
- `apply_middlewares_to_response()` from the ASGI or WSGI settings to automatically apply **response middlewares**.
```

**Here is an example of HTTPS redirect microapp:**

```python
from duck.http.core.processor import (
    AsyncRequestProcessor,
    RequestProcessor,
)
from duck.http.request import HttpRequest
from duck.http.response import (
    HttpRedirectResponse,
    HttpResponse,
)
from duck.utils.urlcrack import URL


class HttpsRedirectMicroApp(MicroApp):
    """
    HttpsRedirectMicroApp class capable of redirecting http traffic to https.
    """

    def __init__(self, location_root_url: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.location_root_url = URL(location_root_url)
        
    def view(self, request: HttpRequest, request_processor: RequestProcessor) -> HttpResponse:
        """
        Returns an http redirect response.
        """
        query = request.META.get("QUERY_STRING", "")
        dest_url = self.location_root_url.join(request.path)
        dest_url.query = query
        dest_url = dest_url.to_str()
        redirect = HttpRedirectResponse(location=dest_url, permanent=False)
        
        # Return response
        return redirect

    async def async_view(self, request: HttpRequest, request_processor: AsyncRequestProcessor) -> HttpResponse:
        """
        Returns an http redirect response.
        """
        query = request.META.get("QUERY_STRING", "")
        dest_url = self.location_root_url.join(request.path)
        dest_url.query = query
        dest_url = dest_url.to_str()
        redirect = HttpRedirectResponse(location=dest_url, permanent=False)
        
        # Return response
        return redirect
```
---

## How to Use Micro Apps

1. **Creating a Micro App**: To create a micro app, simply instantiate the `MicroApp` class and configure its address and port.

```py
from duck.app import MicroApp

# Create a simple micro app running on port 8081
app = MicroApp(port=8080)

if __name__ == "__main__":
    app.run()
```

2. **Defining a View:** Define a view method within your micro app to handle incoming requests and generate responses.

```py

class MyMicroApp(MicroApp):
    def view(self, request, processor):
        return HttpResponse("Hello from My Micro App!")
```

3. **Handling HTTP to HTTPS Redirects:** Duck provides a built-in `HttpsRedirectMicroApp`, which automatically redirects HTTP traffic to HTTPS. This can be controlled via the configuration in Duck's settings, so you don't need to manually implement it.  

To enable **HTTPS redirection**, simply configure Duck to use the `HttpsRedirectMicroApp` in your settings:

```py
FORCE_HTTPS = True
ENABLE_HTTPS = True
```

4. **Running the Micro App:** Once your micro app is configured, you can run it independently, and it will handle requests on its own port.
