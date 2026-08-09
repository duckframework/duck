# 🔐 Authentication in Duck

Duck ships authentication helpers in `duck.contrib.auth` with two backends:

- `session` (default): stores auth state in `request.SESSION`
- `jwt`: stores auth state in `request.JWT`

Helpers support both sync and async usage.

---

## Available Helpers

Sync:

- `authenticate(request, username, password)`
- `login(request, user=None, user_id=None, backend=None)`
- `logout(request, backend=None)`
- `get_user_id(request, backend=None)`
- `get_user(request, backend=None)`
- `get_user_from_session(request)`
- `get_user_from_jwt(request)`
- `set_default_auth_backend("session" | "jwt")`

Async:

- `async_authenticate(...)`
- `async_login(...)`
- `async_logout(...)`
- `async_get_user_id(...)`
- `async_get_user(...)`
- `async_get_user_from_session(...)`
- `async_get_user_from_jwt(...)`

Errors:

- `duck.contrib.auth.exceptions.AuthenticationError`

---

## Available Decorators

All three decorators below live in `duck.contrib.auth.decorators`, work on plain
view functions and `View.run` methods alike, and support both sync and async
handlers.

### `@login_required()`

The lightest check: confirms a `user_id` is present in the session/JWT without
touching the database. Use this when the view doesn't need user fields, just
proof someone is signed in.

Arguments:

- `login_url`: The URL to redirect unauthenticated users to. Static URLs must
  start with `/` (e.g. `/dashboard`). Dynamic URL values are resolved using
  `resolve()`.
- `login_url_resolver`: A callable that dynamically resolves the login URL.
  Mutually exclusive with `login_url`.

If neither is given, the values set via `set_default_login_url` /
`set_default_login_url_resolver` are used instead.

**Example:**

```py
from duck.contrib.auth.decorators import set_default_login_url

# Once, e.g. in settings/startup code
set_default_login_url("login")

# Now this works without repeating login_url everywhere
@login_required
def handle_dashboard(request):
    ...

class SettingsView(View):
    @login_required  # still uses the default
    def run(self, request, **kwargs):
        ...

# Per-view override still works as before
@login_required(login_url="admin-login")
def handle_admin(request):
    ...
```

### `@user_required()`

A step up from `login_required`: resolves the full user model (a DB read) and
sets `request.user` before calling the handler. Use this when the view body
needs user fields, not just the fact that someone is logged in.

Arguments:

- `login_url` / `login_url_resolver`: Same as `login_required`. Falls back to
  the same shared defaults if neither is given.
- `**get_user_kwargs`: Forwarded to `get_user`/`async_get_user` after
  `request`, e.g. `backend="jwt"`.

**Example:**

```py
from duck.contrib.auth.decorators import user_required

@user_required(login_url="login")
def handle_profile(request):
    return HttpResponse(f"Hello {request.user.username}")

@user_required(login_url="login", backend="jwt")
def handle_billing(request):
    ...
```

### `@condition_required()`

The most general decorator: gates access on any predicate evaluated against
`request`, instead of an auth check specifically. Use this to build things
like staff-only, verified-only, or feature-flagged views on top of
`request.user` or any other request attribute.

Arguments:

- `condition`: A callable receiving `request` (plus any `condition_args` /
  `condition_kwargs`) and returning a bool. Can be sync or async regardless
  of the view's own sync/async nature — Duck runs it correctly either way.
- `redirect_url` / `redirect_url_resolver`: Same idea as `login_url` /
  `login_url_resolver`, just renamed since the check isn't necessarily about
  login. Falls back to the same shared defaults if neither is given.
- `condition_args` / `condition_kwargs`: Forwarded to `condition` after
  `request`.

**Example:**

```py
from duck.contrib.auth.decorators import condition_required

def is_staff(request):
    return request.user.is_staff

@condition_required(is_staff, redirect_url="not-authorized")
def handle_admin_panel(request):
    ...

# condition_kwargs example
def has_role(request, role):
    return request.user.role == role

@condition_required(has_role, redirect_url="not-authorized", condition_kwargs={"role": "editor"})
def handle_editor_tools(request):
    ...
```

---

## Order of Decorators

Decorators run outer-to-inner, top-to-bottom — the **topmost** decorator is
the outermost wrapper and runs first when a request comes in. This matters
whenever one decorator produces something on `request` that another
decorator consumes.

`condition_required` almost always needs `request.user`, which only
`user_required` sets. So `user_required` must sit **above**
`condition_required`:

```py
@user_required(login_url="login")
@condition_required(is_staff, redirect_url="not-authorized")
def handle_admin_panel(request):
    ...
```

Execution order: `user_required` resolves the user and sets `request.user` →
`condition_required` evaluates `is_staff(request)` → `handle_admin_panel`
runs.

Reversing the order breaks it — `condition_required` would try to read
`request.user` before it's ever been set:

```py
# ❌ Wrong order — request.user isn't set yet
@condition_required(is_staff, redirect_url="not-authorized")
@user_required(login_url="login")
def handle_admin_panel(request):
    ...
```

**Rule of thumb:** whichever decorator *produces* something on `request`
goes above whichever decorator *consumes* it.

`login_required` and `user_required` are interchangeable in terms of
ordering since neither depends on the other, but there's no reason to stack
both on the same view — `user_required` already implies the user is logged
in.

---

## How Authentication Works

### 1) Credential verification

`authenticate(...)`:

- Uses Django's `get_user_model()`
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

- `get_user_id(...)` helps with fast login when user ID is already known.
- `get_user_from_session(...)` reads `_auth_user_id` from session
- `get_user_from_jwt(...)` reads `_auth_user_id` from JWT claims
- All these functions return `None` if user no longer exists

### 4) Logout behavior

- Session backend: clears session store
- JWT backend: clears JWT claims in `request.JWT`

For JWT flows, client-side token discard/invalidation policy is still your
responsibility.

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

- Most auth helpers rely on Django auth models/ORM.
- For JWT auth persistence, keep `JWTMiddleware` enabled so tokens can be
  read and re-issued correctly.

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

    # Login user and return response.
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

    # Login user and return response.
    login(request, user, backend="jwt")
    return HttpResponse("signed in")
```

`JWTMiddleware` then writes updated tokens in the response.
