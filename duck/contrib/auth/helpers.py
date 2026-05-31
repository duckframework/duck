"""
Duck auth helpers — login, logout, and authenticate.

Supports two backends:

- ``"session"``: stores user identity in ``request.SESSION`` (default).
- ``"jwt"``: reads/writes identity from ``request.JWT``.

Usage:

```python
from duck.contrib.auth import login, logout, authenticate
from duck.contrib.auth.exceptions import AuthenticationError

# Sync
try:
    user = authenticate(request, "brian@example.com", "secret")
except AuthenticationError:
    user = None
    
if user:
    login(request, user)

# Async
try:
    user = await async_authenticate(request, "brian@example.com", "secret")
except AuthenticationError:
    user = None
    
if user:
    await async_login(request, user)
```

Notes:
- These helpers only support Django models via ``get_user_model()``.
- Set a process-wide default backend with ``set_default_auth_backend()``.
"""

from typing import Any

from duck.contrib.sync import ensure_async
from duck.contrib.auth.exceptions import AuthenticationError
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password as django_check_password


# Session/JWT key where the authenticated user id is stored
USER_ID_KEY = "_auth_user_id"

# Session/JWT key that records which backend authenticated the user
BACKEND_KEY = "_auth_backend"

# Process-wide default backend, changeable via set_default_auth_backend()
DEFAULT_AUTH_BACKEND = "session"

# Supported backend identifiers
SUPPORTED_BACKENDS = ("session", "jwt")


def set_default_auth_backend(backend: str) -> None:
    """
    Set the process-wide default authentication backend.

    This affects all subsequent calls to ``login``, ``logout``, and their
    async equivalents when no explicit ``backend`` argument is passed.

    Args:
        backend: Either ``"session"`` or ``"jwt"``.

    Raises:
        ValueError: If the given backend is not a supported identifier.

    Example:
        .. code-block:: python

            from duck.contrib.auth import set_default_auth_backend

            set_default_auth_backend("jwt")
    """
    global DEFAULT_AUTH_BACKEND

    if backend not in SUPPORTED_BACKENDS:
        raise ValueError(
            f"Unknown auth backend: '{backend}'. "
            f"Supported backends are: {', '.join(SUPPORTED_BACKENDS)}."
        )

    # Update the module-level default
    DEFAULT_AUTH_BACKEND = backend


def authenticate(request: Any, username: str, password: str) -> Any:
    """
    Verify credentials against the User model and return the user if valid.

    Looks up the user by the model's ``USERNAME_FIELD``, then verifies the
    password using Django's hasher. Does not touch the session or any auth
    state — that is ``login``'s responsibility.

    Args:
        request: The Duck request object.
        username: The username or email to look up.
        password: The plain-text password to verify.

    Returns:
        The matching User instance on success.

    Raises:
        AuthenticationError: If the user does not exist, is inactive, or the
            password does not match.

    Example:
    ```py
    user = authenticate(request, "brian@example.com", "secret")
    login(request, user)
    ```
    """
    User = get_user_model()
    username_field = User.USERNAME_FIELD

    try:
        # Fetch user by the model's primary lookup field
        user = User.objects.get(**{username_field: username})
    except User.DoesNotExist as exc:
        # Constant-time fallback to prevent user enumeration via timing
        django_check_password(password, "!")
        raise AuthenticationError(f"Authentication failed: {exc}") from exc

    # Reject inactive accounts before touching the password
    if not user.is_active:
        raise AuthenticationError("Authentication failed: account is inactive.")

    if not django_check_password(password, user.password):
        raise AuthenticationError("Authentication failed: invalid credentials.")

    return user


def login(request: Any, user: Any, backend: str | None = None) -> None:
    """
    Record a successfully authenticated user on the request.

    For the session backend the user id and backend name are written into
    ``request.SESSION``. For the JWT backend the same fields are written
    into ``request.JWT``.

    Args:
        request: The Duck request object.
        user: An authenticated User instance returned by ``authenticate``.
        backend: Either ``"session"`` or ``"jwt"``. Defaults to the value
            set by ``set_default_auth_backend()`` (initially ``"session"``).

    Raises:
        AuthenticationError: If ``user`` is ``None`` or has no primary key.
        ValueError: If an unsupported backend name is given.

    Example:
        .. code-block:: python

            user = authenticate(request, "brian@example.com", "secret")
            login(request, user)
    """
    if not user or not user.pk:
        raise AuthenticationError("Cannot log in an anonymous or unsaved user.")

    # Resolve the effective backend
    resolved = backend or DEFAULT_AUTH_BACKEND

    if resolved == "session":
        # Write identity into the session store
        request.SESSION[USER_ID_KEY] = str(user.pk)
        request.SESSION[BACKEND_KEY] = resolved
        return

    if resolved == "jwt":
        # Write identity into the JWT store
        request.JWT[USER_ID_KEY] = str(user.pk)
        request.JWT[BACKEND_KEY] = resolved
        return

    raise ValueError(
        f"Unknown auth backend: '{resolved}'. "
        f"Supported backends are: {', '.join(SUPPORTED_BACKENDS)}."
    )


def logout(request: Any, backend: str | None = None) -> None:
    """
    Clear the current user's auth state from the request.

    For the session backend the entire session is flushed. For the JWT
    backend the JWT store is cleared. JWT is stateless, so token
    invalidation on the client side (discarding the token) is still
    the caller's responsibility.

    Args:
        request: The Duck request object.
        backend: Either ``"session"`` or ``"jwt"``. Defaults to the value
            set by ``set_default_auth_backend()`` (initially ``"session"``).

    Raises:
        ValueError: If an unsupported backend name is given.

    Example:
        .. code-block:: python

            logout(request)
    """
    resolved = backend or DEFAULT_AUTH_BACKEND

    if resolved == "session":
        # Flush the entire session, not just the auth keys
        request.SESSION.clear()
        return

    if resolved == "jwt":
        request.JWT.clear()
        return

    raise ValueError(
        f"Unknown auth backend: '{resolved}'. "
        f"Supported backends are: {', '.join(SUPPORTED_BACKENDS)}."
    )


def get_user_from_session(request: Any) -> Any | None:
    """
    Resolve the currently logged-in user from the session.

    Args:
        request: The Duck request object.

    Returns:
        The User instance if a valid session entry exists, otherwise ``None``.

    Example:
    
    ````py
    user = get_user_from_session(request)

    if user:
        print(f"Logged in as {user}")
    ```
    """
    user_id = request.SESSION.get(USER_ID_KEY)

    if user_id is None:
        return None

    # Look up the stored primary key against the User model
    User = get_user_model()

    try:
        return User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return None


def get_user_from_jwt(request: Any) -> Any | None:
    """
    Resolve the currently authenticated user from the JWT store.

    Reads the user id written by ``login`` from ``request.JWT``. Returns
    ``None`` if the entry is absent or the referenced user no longer exists.

    Args:
        request: The Duck request object.

    Returns:
        The User instance if a valid JWT entry exists, otherwise ``None``.

    Example:
    
    ```py
    user = get_user_from_jwt(request)

    if user:
        print(f"JWT user: {user}")
    ```
    """
    user_id = request.JWT.get(USER_ID_KEY)

    if user_id is None:
        return None

    # Resolve the stored primary key
    User = get_user_model()

    try:
        return User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return None


# Async API

async def async_authenticate(
    request: Any,
    username: str,
    password: str,
) -> Any:
    """
    Async version of ``authenticate``.

    Wraps the sync ORM calls via ``ensure_async`` so the event loop is
    never blocked.

    Args:
        request: The Duck request object.
        username: The username or email to look up.
        password: The plain-text password to verify.

    Returns:
        The matching User instance on success.

    Raises:
        AuthenticationError: Propagated from ``authenticate``.
    """
    return await ensure_async(authenticate)(request, username, password)


async def async_login(
    request: Any,
    user: Any,
    backend: str | None = None,
) -> None:
    """
    Async version of ``login``.

    Args:
        request: The Duck request object.
        user: An authenticated User instance.
        backend: Either ``"session"`` or ``"jwt"``. Defaults to the value
            set by ``set_default_auth_backend()`` (initially ``"session"``).

    Raises:
        AuthenticationError: Propagated from ``login``.
        ValueError: Propagated from ``login``.
    """
    await ensure_async(login)(request, user, backend)


async def async_logout(request: Any, backend: str | None = None) -> None:
    """
    Async version of ``logout``.

    Args:
        request: The Duck request object.
        backend: Either ``"session"`` or ``"jwt"``. Defaults to the value
            set by ``set_default_auth_backend()`` (initially ``"session"``).

    Raises:
        ValueError: Propagated from ``logout``.
    """
    await ensure_async(logout)(request, backend)


async def async_get_user_from_session(request: Any) -> Any | None:
    """
    Async version of ``get_user_from_session``.

    Args:
        request: The Duck request object.

    Returns:
        The User instance if a valid session exists, otherwise ``None``.
    """
    return await ensure_async(get_user_from_session)(request)


async def async_get_user_from_jwt(request: Any) -> Any | None:
    """
    Async version of ``get_user_from_jwt``.

    Args:
        request: The Duck request object.

    Returns:
        The User instance if a valid JWT entry exists, otherwise ``None``.
    """
    return await ensure_async(get_user_from_jwt)(request)
