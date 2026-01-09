# 💡Duck Shortcuts

The **Duck Shortcuts Module** provides utility functions to simplify various tasks, such as rendering HTML templates, generating HTTP responses, and resolving URLs. These shortcuts streamline the process of handling requests and responses within the Duck framework.

> Module Reference: **duck.shortcuts**

---

## Features

- **Template Rendering**: Easily render Jinja2 or Django templates.
- **Response Handling**: Generate common HTTP responses, including JSON, redirects, and 404 errors.
- **URL Utilities**: Resolve named URLs dynamically.
- **Security**: Retrieve CSRF tokens for request validation.
- **Static & Media Paths**: Get absolute paths for static and media resources.

---

## Available Functions

### 1. `csrf_token(request) -> str`

Retrieves the CSRF token for the request.

```py
token = csrf_token(request)
```

### 2. `static(resource_path: str) -> str`

Returns the absolute static URL path for a resource.

```py
static_url = static("css/styles.css")
```

### 3. `media(resource_path: str) -> str`

Returns the absolute media URL path for a resource.

```py
media_url = media("uploads/profile.jpg")
```

### 4. `jinja2_render(request, template: str, context: dict = {}, **kw) -> TemplateResponse`

Renders a Jinja2 template.

```py
response = jinja2_render(request, "index.html", {"title": "Home"})
```

### 5. `django_render(request, template: str, context: dict = {}, **kw) -> TemplateResponse`

Renders a Django template.

```py
response = django_render(request, "home.html", {"user": "Brian"})
```

### 6. render(request, template: str, context: dict = {}, engine: str = "django", **kw) -> TemplateResponse

Renders a template using the specified engine (django or jinja2).

```py
response = render(request, "dashboard.html", {"page": "Dashboard"}, engine="jinja2")
```

### 7. `redirect(location: str, permanent: bool = False, content_type="text/html", **kw) -> HttpRedirectResponse`

Generates a redirect response.

```py
response = redirect("/home/")
```

### 8. `jsonify(data: Any, status_code: int = 200, **kw) -> JsonResponse`

Returns a JSON response.

```
response = jsonify({"message": "Success", "status": 200})
```

### 9. `not_found404(body: Optional[str] = None, content_type="text/html", **kw) -> HttpNotFoundResponse`

Generates a 404 Not Found response.

```py
response = not_found404("Page not found")
```

### 10. `merge(base_response: HttpResponse, take_response: HttpResponse, merge_headers: bool = False) -> HttpResponse`

Merges two HTTP response objects.

```py
merged_response = merge(response1, response2)
```

### 11. `content_replace(response: HttpResponse, new_data: Union[bytes, str], new_content_type: str = "auto", new_content_filepath: str = "use_existing")`

Replaces the content of an HTTP response.

```py
updated_response = content_replace(response, b"New content")
```

### 12. `replace_response(old_response, new_response) -> HttpResponse`

Transforms an old response into a new response while preserving certain attributes.

```py
new_response = replace_response(response1, response2)
```

### 13. `resolve(name: str, absolute: bool = True, fallback_url: Optional[str] = None) -> str`

Resolves a named URL.

```py
url = resolve("home")
```

### 14. `to_response(value: Any) -> Union[BaseResponse, HttpResponse]`

Converts any value to an HTTP response.

```py
response = to_response("Hello, world!")
```

### Error Handling

> URLResolveError

Raised if URL resolution fails.

```py
try:
    url = resolve("non_existent_url")
except URLResolveError as e:
    print(f"Error: {e}")
```

### Summary

> The Duck Shortcuts Module simplifies web development by providing helper functions for template rendering, HTTP responses, URL resolution, and more. By utilizing these utilities, developers can efficiently manage request handling within the Duck framework.
