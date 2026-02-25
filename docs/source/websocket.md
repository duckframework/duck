# 🌐 WebSockets in Python – Real-Time Apps with Duck

[![Real-time Ready](https://img.shields.io/badge/Real--Time-Enabled-brightgreen?style=for-the-badge&logo=websocket)](#)  
[![Async First](https://img.shields.io/badge/Async-First-blue?style=for-the-badge&logo=python)](#)  
[![Duck Framework](https://img.shields.io/badge/Powered%20By-Duck-orange?style=for-the-badge&logo=duckframework)](#)

---

Duck makes **WebSocket implementation** simple and powerful 🔌.  
Forget the boilerplate — with Duck you can add real-time features in just a few lines of code 🚀.  

---

## ⚡ Quick Example

In your **`urls.py`**, define a WebSocket view:

```py
# urls.py

from duck.urls import path
from duck.contrib.websockets import WebSocketView, OpCode

class MyWebSocket(WebSocketView):
    async def on_open(self):
        print("WebSocket connection established")
        
    async def on_receive(self, data: bytes, opcode: int):
        if opcode == OpCode.TEXT:
            message = "You sent " + data.decode("utf-8")
            await self.send_text(message)
        else:
            # Handle binary frames here
            pass

# Register your WebSocket route
urlpatterns = [
    path("/ws/myws", MyWebSocket, name="mywebsocket"),
    # other patterns here.
]
```

✅ That’s it! Your app is now ready to handle **WebSocket connections**.  

---

## ⚙️ Customizing Behavior

Duck’s WebSocket views support configurable class variables:

- ⏱ **`RECEIVE_TIMEOUT`** → default: `120` seconds  
  (timeout before expecting a new frame).  
- 📦 **`MAX_FRAME_SIZE`** → default: `1 * 1024 * 1024` bytes  
  (maximum allowed size of a frame).  

Simply override these in your `WebSocketView` subclass to tweak performance.  

---

## 💬 Practical Examples

### 1️⃣ Simple Chat App

A minimal chat implementation that **echoes messages** back to all connected users.

```py
from duck.contrib.websockets import WebSocketView, OpCode

connected_clients = set()

class ChatSocket(WebSocketView):
    async def on_open(self):
        connected_clients.add(self)
        await self.send_text("👋 Welcome to the chat!")

    async def on_receive(self, data: bytes, opcode: int):
        if opcode == OpCode.TEXT:
            message = data.decode("utf-8")
            # Broadcast to all connected clients
            for client in connected_clients:
                if client != self:
                    await client.send_text(f"User: {message}")

    async def on_close(self):
        connected_clients.remove(self)
```

---

### 2️⃣ Live Notifications

Send **server-initiated notifications** to clients:

```py
import asyncio
from duck.contrib.websockets import WebSocketView
from duck.utils.asyncio import create_task # Better than default asyncio.create_task

class NotificationSocket(WebSocketView):
    async def on_open(self):
        # Push notifications every 5 seconds
        create_task(self.push_notifications())

    async def push_notifications(self):
        count = 0
        while True:
            await asyncio.sleep(5)
            count += 1
            await self.send_text(f"🔔 Notification #{count}")
```

---

✨ With Duck’s WebSocket support, you can build **chat apps, live dashboards, multiplayer games, IoT streams**, and more — all with async-native performance 🌐⚡  

---

👉 Next: Learn how async fits into the bigger picture with [⚡ ASGI](./asgi.md) or see how it plays with [🖥️ WSGI](./wsgi.md).
