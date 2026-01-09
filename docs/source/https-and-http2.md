# 🚧 HTTP/2 and HTTPS

## Leveraging HTTP/2

**HTTP/2** is the new protocol for the web and it is a better and optimum solution
for fast webservers.
**Duck** supports **HTTP/2** using the `h2` Python package, enabling faster and more efficient communication compared to **HTTP/1.1**.
With features like **multiplexing**, **header compression**, and **lower latency**, **HTTP/2** significantly improves performance. 

``` {warning}
It is strongly recommended to use **HTTP/2** only over a **secure HTTPS** connection. Running **HTTP/2** over an unencrypted connection (h2c) in production may expose your data to security risks.
```

### Getting Started

To enable **HTTP/2** in **Duck**, simply set the following in your configuration:  

```py
HTTP_2_SUPPORT = True
```

### Switching to HTTP/2  

There are **two** ways to enable HTTP/2 in your Duck web app:  

1. **Enable HTTPS** by setting:  
   
   ```py
   ENABLE_HTTPS = True
   ```

This ensures secure communication and automatically enables **HTTP/2 support**.

2. **Send an Upgrade Header to Duck**:

```py
Upgrade: h2c
```

This allows **HTTP/1.1 clients** to request an upgrade to h2c (HTTP/2 over cleartext).

By using either of these methods, **Duck** will seamlessly switch to **HTTP/2**, improving **speed**, **efficiency**, and **overall performance**. 🚀🔥

---

## Enabling HTTPS

To activate **HTTPS**, set the following in your `settings.py`:  

```py
ENABLE_HTTPS = True
```

### Force HTTPS Redirection  

To automatically redirect **all HTTP traffic to HTTPS**, enable the redirect feature:  

```py
FORCE_HTTPS = True
```

``` {note}
**FORCE_HTTPS** requires **ENABLE_HTTPS** to be set to **True**.
```

---

## Local SSL Certificate Generation

**Duck** includes an **`ssl-gen`** command to generate self-signed SSL certificates.

### Requirements  

Ensure you have **OpenSSL** installed before running the command.

---

## Production Recommendations

Use port **80** for **HTTP** and port **443** for **HTTPS** in production.

**Secure your SSL configuration for enhanced security.**
