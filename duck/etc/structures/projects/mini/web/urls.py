"""
This contains `URL patterns` to register for the application.

Example:

```py
from duck.urls import path
from duck.http.response import HttpResponse

def home(request):
    # Do something here
    return HttpResponse("Hello world")

urlpatterns = [
    path('/', views.home_view, 'home', ['GET'])
]
```

WebSocket Example:

```py
from duck.urls import path
from duck.contrib.websockets import WebSocketView


class SomeWebSocket(WebSocketView):
    async def on_receive(self, data: bytes, opcode):
        # Do something with the data        
        await self.send_text("Some text")
        
        # Available send methods:
        #   send_text, send_json, send_binary, send_text, send_ping, send_pong & send_close


urlpatterns = [
    path('/some_endpoint', SomeWebSocket, name="some_ws_endpoint"),
]
```

"""
from duck.urls import path, re_path


urlpatterns = [
    # add your urlpatterns here.
]
