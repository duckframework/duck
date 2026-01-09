# 🔀 Request & Response

## Requests

Every time a new request comes in, **Duck** creates a request object from `duck.http.request`.  
This object gives you convenient ways to access all parts of the incoming request.

### Request Cookies

To get cookies sent by the client, use `request.COOKIES`.

### Request Session

Each user has their own session, accessible with `request.SESSION` or `request.session`.

### Request Queries

Duck separates query parameters into two types:
- **URL queries**: Parameters from the URL (e.g. `/foo?bar=1`)
- **Content queries**: Data sent in the request body (e.g. POST form data or JSON)

You can access these with `request.{REQUEST_METHOD}` (e.g. `request.GET`, `request.POST`).  
- `request.GET` contains only URL queries.
- `request.POST` contains only content/body queries.

If you need both, use:
```py
# views.py
from duck.http.response import HttpResponse

def some_view(request):
    print(request.QUERY["CONTENT_QUERY"]) # Shows content/body queries
    print(request.QUERY["URL_QUERY"])     # Shows URL queries
    return HttpResponse("Hello world")
```

### Request Authentication

If authentication info is sent in headers, you can access it with `request.AUTH`.

### Request Metadata

All metadata about the request (headers, IP address, etc) is available in `request.META`.

### Request Files

Uploaded files can be accessed with `request.FILES`.  
To work with a specific file:

```py
some_file = request.FILES["some_file"]
some_file.save() # Save the file if needed.
```
---

## Responses

All HTTP responses in Duck are based on `duck.http.response.Response`.  
Duck provides many types of responses, from basic to advanced streaming responses.

You can explore all response types in the `duck.http.response` module.

### What are Streaming Responses?

Streaming responses let you send large files or data to the client efficiently—such as videos or other big files.

Here's how you can create a simple streaming response:

```py
# views.py

from duck.http.response import StreamingHttpResponse

def get_data():
    for data in some_data_source:
        yield data
        
def some_view(request):
    stream = get_data() # The source can be a function, IO stream, or any iterable
    return StreamingHttpResponse(stream)
```

### StreamingRangeHttpResponse

This is an improved version of `StreamingHttpResponse` that supports partial content (range requests), 
allowing users to resume downloads.

To use this, your stream should be a file-like or seekable IO object.

### FileResponse

You don't need to handle partial content yourself.  
Use `FileResponse` to send files: it automatically provides resumable, partial content support.
All `FileResponse` instances are actually `StreamingRangeHttpResponse` under the hood.

### Response Shortcuts

Duck offers easy-to-use shortcuts for creating common response types, found in `duck.shortcuts`:

- **render**: Render an HTML template, returning a `TemplateResponse`.
- **json**: Serialize data as JSON, returning a `JsonResponse`.
- **redirect**: Create an HTTP redirect with `HttpRedirectResponse`.
- **to_response**: Create a response from almost any object (strings, components, etc).

Explore the `duck.shortcuts` module for more!
