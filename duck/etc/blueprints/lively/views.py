"""
You can store your application `views` in a `single file` (this file) or use a `folder module` for better organization.
A folder module allows you to group different views into separate files and access them in `__init__.py`, making it easier to manage and scale your application.
This approach keeps your codebase clean and improves maintainability.

Example views:

```py
from duck.shortcuts import to_response, render

def home(request):
	return "<b>Hello world</b>"

def about(request):
	return to_response("This is the about page") # Produces HttpResponse object for the provided content.

def contact(request):
    # You can use "myapp/home.html" if template is in blueprint directory.
    return render(request, "home.html", {})
```
"""

from duck.html.components.core.browser_state import sync_browser_state
from duck.html.components.core.system import LivelyComponentSystem
from duck.html.components.lively_utils.file_request import receive_ws_file


# Alias for websocket view
websocket = LivelyComponentSystem.get_websocket_view_cls()


# All allowed imports
__all__ = [
    "websocket",
    "sync_browser_state",
    "receive_ws_file",
]
