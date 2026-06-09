# 🔑 JWT in Duck

Duck provides first-class JWT support through:

- `request.JWT` (a JWT payload store attached to every request)
- `duck.http.middlewares.contrib.JWTMiddleware` (token extraction + delivery)
- `duck.contrib.jwt` (encoding/decoding helpers)

---

## How JWT Works in Duck

1. Every incoming request gets a `request.JWT` store.
2. `JWTMiddleware` reads the access token from cookie or header (based on settings).
3. The token is decoded lazily when `request.JWT` is accessed.
4. Your view/component updates JWT claims using `request.JWT`.
5. If claims changed (or token expired / refresh token supplied), middleware re-issues access + refresh tokens in the response.

---

## Request JWT Store (`request.JWT`)

Duck uses `JWTStore` (default engine: `duck.http.jwt.engine`) for payload access and mutation.

Common operations:

- Read a claim: `request.JWT.get("key")` or `request.JWT["key"]`
- Set a claim: `request.JWT["key"] = value` or `request.JWT.set("key", value)`
- Remove a claim: `request.JWT.delete("key")`
- Clear all claims: `request.JWT.clear()`
- Check dirty state: `request.JWT.needs_update()`
- Check expiry: `request.JWT.is_expired()`

Notes:

- The store is lazy-loaded.
- If no token is present, store starts empty (not an error).
- If you encode manually, `exp` must exist in payload.
- Expiry can be controlled with `set_expiry(...)` / `reset_expiry()`.

---

## JWT Middleware Behavior

`JWTMiddleware` is included in Duck’s recommended middleware list.

### Request phase

- Resolves transport via `JWT_TRANSPORT` (`cookie` or `header`).
- Reads access token from configured cookie/header.
- Attaches raw token to `request.JWT` for lazy decode.

### Response phase

- If JWT changed, expired, or refresh token exists, middleware re-issues tokens.
- Refresh token (if provided) is validated and merged safely.
- New access + refresh tokens are written back using configured transport.

---

## Settings

Core settings used by JWT:

- `JWT_SECRET_KEY` (falls back to `SECRET_KEY`)
- `JWT_ALGORITHM` (default: `HS256`)
- `JWT_ACCESS_LIFETIME` (default: `3600` seconds)
- `JWT_REFRESH_LIFETIME` (default: `7 * 24 * 3600` seconds)
- `JWT_ENGINE` (default: `duck.http.jwt.engine`)

Transport settings:

- `JWT_TRANSPORT`: `cookie` or `header` (default: `cookie`)

Cookie transport:

- `JWT_COOKIE_NAME` (default: `jwt`)
- `JWT_REFRESH_COOKIE_NAME` (default: `jwt-refresh`)
- `JWT_COOKIE_HTTPONLY` (default: `True`)
- `JWT_COOKIE_SECURE` (default: `False`)
- `JWT_COOKIE_SAMESITE` (default: `Lax`)
- `JWT_COOKIE_DOMAIN` (defaults to Duck server domain)

Header transport:

- `JWT_HEADER_NAME` (default: `X-JWT-Token`)
- `JWT_REFRESH_HEADER_NAME` (default: `X-Refresh-JWT-Token`)

---

## Low-level JWT Helpers

`duck.contrib.jwt` exposes:

- `encode_token(payload, token_type="access")`
- `decode_token(token, verify_expiry=True)`
- `issue_token_pair(payload)`
- `JWTError`, `JWTExpired`, `JWTInvalid`

Use these for custom token flows when needed.

---

## Lively / WebSocket State Sync

During Lively interactions, request state is reused.  
If JWT/session/CSRF state changes, Duck queues a browser-state sync response so sensitive updates (including `HttpOnly` cookies) are applied through a secure follow-up fetch.

---

## Minimal Example

```py
from duck.http.response import HttpResponse

def login_like_view(request):
    request.JWT["user_id"] = "42"
    request.JWT["role"] = "member"
    request.JWT.set_expiry()  # use JWT_ACCESS_LIFETIME
    return HttpResponse("ok")
```

On response, `JWTMiddleware` issues updated access/refresh tokens.
