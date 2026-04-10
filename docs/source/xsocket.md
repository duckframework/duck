# 🔌 Socket I/O (xsocket)

[![Async Ready](https://img.shields.io/badge/Async-Ready-brightgreen?style=for-the-badge&logo=python)](#)  
[![Non-Blocking](https://img.shields.io/badge/No-Blocking-blue?style=for-the-badge&logo=socketdotio)](#)  
[![Duck Framework](https://img.shields.io/badge/Powered%20By-Duck-orange?style=for-the-badge&logo=duck)](#)

---

Duck provides its own **socket implementation**: `duck.utils.xsocket`.  
This is a custom, **non-blocking replacement** for Python’s built-in `socket`, built with async-first principles 🚀.  

With `xsocket`, you get:  
- ✅ **Non-blocking calls** in async mode.  
- ⚡ Seamless async-ready APIs (`async_...` methods).  
- 🔐 SSL/TLS support via `ssl_xsocket`.  
- 🔄 Compatibility with sync and async environments.  

---

## Getting Started

To use `xsocket` for Socket I/O, import from `duck.utils.xsocket.io`.  

---

## Synchronous Example

```py
import socket
import threading

from duck.utils.xsocket import create_xsocket, xsocket, ssl_xsocket
from duck.utils.xsocket.io import SocketIO

def handle_conn(sock: xsocket, addr: tuple[str, int]):
    # Do sock.do_handshake() if you are using ssl_xsocket
    print("New connection", addr)
    
    request = SocketIO.receive_full_request(sock, timeout=1)
    
    # Parse request data here
    
    SocketIO.send(b"200 OK\r\n\r\n", sock)  # You can set timeout with the timeout argument
    
    # Close connection
    SocketIO.close(sock)


def serve_forever():
    server_sock = create_xsocket(family=socket.AF_INET, type=socket.SOCK_STREAM)
    server_sock.bind(("0.0.0.0", 5000))
    server_sock.listen(5)
   
    while True:
        sock, addr = server_sock.accept()
        sock = xsocket(sock)  # Or use ssl_xsocket for HTTPS
        threading.Thread(target=handle_conn, args=[sock, addr]).start()


if __name__ == '__main__':
    serve_forever()
```

---

## Asynchronous Example

```py
import socket
import asyncio

from duck.utils.xsocket import create_xsocket, xsocket, ssl_xsocket
from duck.utils.xsocket.io import SocketIO
from duck.utils.asyncio import create_task  # Better than default asyncio.create_task


async def handle_conn(sock: xsocket, addr: tuple[str, int]):
    # Do await sock.async_do_handshake() if you are using ssl_xsocket
    print("New connection", addr)
    
    request = await SocketIO.async_receive_full_request(sock, timeout=1)
    
    # Parse & process request here
    
    await SocketIO.async_send(b"200 OK\r\n\r\n", sock)  # Supports timeout argument
    
    # Close connection
    SocketIO.close(sock)


async def serve_forever():
    server_sock = create_xsocket(family=socket.AF_INET, type=socket.SOCK_STREAM)
    server_sock.bind(("0.0.0.0", 5000))
    server_sock.listen(5)
   
    while True:
        sock, addr = await server_sock.async_accept()
        sock = xsocket(sock)  # Or use ssl_xsocket for HTTPS
        create_task(handle_conn(sock, addr))


if __name__ == '__main__':
    asyncio.run(serve_forever())
```

---

## Notes
- 🔒 Use `ssl_xsocket` for secure HTTPS/TLS connections.  
- ⏱ Most I/O functions accept a `timeout` argument.  
- 🔄 Works seamlessly with Duck’s async runtime (`duck.utils.asyncio.create_task`).  
- ⚡ Perfect for **custom servers, proxies, or protocol implementations**.  

---

## Performance Tips
- ♻ **Reuse sockets** where possible to avoid repeated creation overhead.  
- 📏 **Tune `timeout` values** depending on expected network latency.  
- 🧩 **Handle partial reads/writes** — especially for large frames or slow clients.  
- 🛡 **SSL handshakes** can be expensive; reuse `ssl_xsocket` connections if possible.  
- 🔗 Consider **thread pools or async tasks** to prevent blocking other connections.  

---

✨ With `xsocket`, you’re not tied to blocking sockets anymore.  
Build **fast, scalable, async-native servers** with just a few lines of code 🔌⚡  

---

👉 Next: Learn how this integrates with higher-level protocols like [⚡ ASGI](./asgi.md) or [🌐 WebSockets](./websocket.md).
