# 🔐 Authentication in Duck

Duck ships authentication helpers in `duck.contrib.auth` with two backends:

- `session` (default): stores auth state in `request.SESSION`
- `jwt`: stores auth state in `request.JWT`

Helpers support both sync and async usage.

---

## Available Helpers

Sync:

- `authenticate(request, username, password)`
- `login(request, user, backend=None)`
- `logout(request, backend=None)`
- `get_user_from_session(request)`
- `get_user_from_jwt(request)`
- `set_default_auth_backend("session" | "jwt")`

Async:

- `async_authenticate(...)`
- `async_login(...)`
- `async_logout(...)`
- `async_get_user_from_session(...)`
- `async_get_user_from_jwt(...)`

Errors:

- `duck.contrib.auth.exceptions.AuthenticationError`

---

## How Authentication Works

### 1) Credential verification

`authenticate(...)`:

- Uses Django’s `get_user_model()`
- Looks up user by `User.USERNAME_FIELD`
- Verifies password with Django hashers
- Rejects inactive users
- Raises `AuthenticationError` on failure

### 2) Login persistence

`login(...)` stores:

- `_auth_user_id`
- `_auth_backend`

Storage target depends on backend:

- `session` backend → `request.SESSION`
- `jwt` backend → `request.JWT`

### 3) User resolution

- `get_user_from_session(...)` reads `_auth_user_id` from session
- `get_user_from_jwt(...)` reads `_auth_user_id` from JWT claims
- Both return `None` if user no longer exists

### 4) Logout behavior

- Session backend: clears session store
- JWT backend: clears JWT claims in `request.JWT`

For JWT flows, client-side token discard/invalidation policy is still your responsibility.

---

## Backend Selection

`login`, `logout`, and async equivalents use:

1. explicit `backend` argument if provided
2. otherwise the process-wide default backend

Default backend starts as `session`.  
You can change it with:

```py
from duck.contrib.auth import set_default_auth_backend
set_default_auth_backend("jwt")
```

---

## Requirements

- Auth helpers rely on Django auth models/ORM.
- For JWT auth persistence, keep `JWTMiddleware` enabled so tokens can be read and re-issued correctly.

---

## Session Backend Example

```py
from duck.contrib.auth import authenticate, login, get_user_from_session
from duck.contrib.auth.exceptions import AuthenticationError
from duck.http.response import HttpResponse

def sign_in(request):
    try:
        user = authenticate(request, "user@example.com", "secret")
    except AuthenticationError:
        return HttpResponse("invalid credentials", status_code=401)

    login(request, user, backend="session")
    return HttpResponse("signed in")
```

---

## JWT Backend Example

```py
from duck.contrib.auth import authenticate, login, get_user_from_jwt
from duck.contrib.auth.exceptions import AuthenticationError
from duck.http.response import HttpResponse

def sign_in_jwt(request):
    try:
        user = authenticate(request, "user@example.com", "secret")
    except AuthenticationError:
        return HttpResponse("invalid credentials", status_code=401)

    login(request, user, backend="jwt")
    request.JWT.set_expiry()
    return HttpResponse("signed in")
```

`JWTMiddleware` then writes updated tokens in the response.
