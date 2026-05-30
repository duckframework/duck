"""
Duck auth helpers — login, logout, and authenticate.

Supports two backends:
- `"session"`: stores user identity in request.session (default)
- `"jwt"`: issues a signed token pair, requires PyJWT

Usage:

```py
from duck.contrib.auth import login, logout, authenticate

# Sync
user = authenticate(request, "brian@example.com", "secret")

if user:
    login(request, user)

# Async
user = await async_authenticate(request, "brian@example.com", "secret")

if user:
    await async_login(request, user)
```

**Notes:** These only support Django models.

"""

import asyncio

from typing import Any

from duck.contrib.sync import ensure_async
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password as django_check_password


# Session key where the authenticated user id is stored
SESSION_USER_ID_KEY = "_auth_user_id"

# Session key that records which backend authenticated the user
SESSION_BACKEND_KEY = "_auth_backend"


# Lazy PyJWT import — avoids a hard dependency at module level
def get_jwt_lib():
    """
    Imports and returns the PyJWT library.

    Raises:
        ImportError: If PyJWT is not installed in the environment.
    """
    try:
        import jwt
        return jwt
    except ImportError:
        raise ImportError(
            "PyJWT is required for JWT support. Install it with: pip install PyJWT"
        )


def authenticate(request: Any, username: str, password: str) -> Any | None:
    """
    Verify credentials against the User model and return the user if valid.

    Looks up the user by username (or email if no username field match),
    then verifies the password using Django's hasher. Does not touch
    request.SESSION or any auth state — that is login's responsibility.

    Args:
        request: The Duck request object.
        username: The username or email to look up.
        password: The plain-text password to verify.

    Returns:
        The matching User instance on success, or ``None`` on failure.
    """
    User = get_user_model()

    # Try username field first, then fall back to email
    username_field = User.USERNAME_FIELD
    
    try:
        user = User.objects.get(**{username_field: username})
    except User.DoesNotExist:
        # Constant-time fallback to prevent user enumeration via timing
        django_check_password(password, "!")
        return None

    # Reject inactive accounts before checking the password
    if not user.is_active:
        return None

    if not django_check_password(password, user.password):
        return None

    return user


def login(request: Any, user: Any, backend: str = "session") -> dict | None:
    """
    Log a user in using the specified backend.

    For the session backend, the user id and backend name are written
    into `request.SESSION`. For the JWT backend, a token pair is
    returned and nothing is written to the session.

    Args:
        request: The Duck request object.
        user: An authenticated User instance (from `authenticate`).
        backend: Either `"session"` (default) or `"jwt"`.

    Returns:
        `None` for the session backend.
        A `{"access": str, "refresh": str}` dict for the JWT backend.

    Raises:
        ValueError: If an unsupported backend name is given.
        ImportError: If the jwt backend is requested but PyJWT is not installed.
    """
    if backend == "session":
        # Store user identity in the session
        request.SESSION[SESSION_USER_ID_KEY] = str(user.pk)
        request.SESSION[SESSION_BACKEND_KEY] = backend
        return None

    if backend == "jwt":
        from duck.contrib.jwt import issue_token_pair
        
        # Get acccess and refresh tokens.
        pair = issue_token_pair(user.pk)
        
        # Set some meta.
        request.JWT.update(pair)
        
        # Finally, return token pair.
        return pair
        
    raise ValueError(
        f"Unknown auth backend: '{backend}'. "
        "Supported backends are 'session' and 'jwt'."
    )


def logout(request: Any, backend: str = "session") -> None:
    """
    Log the current user out.

    For the session backend, the session is fully flushed. For the JWT
    backend this is a no-op — JWT is stateless and token invalidation
    is the client's responsibility (discard the token).

    Args:
        request: The Duck request object.
        backend: Either ``"session"`` (default) or ``"jwt"``.

    Raises:
        ValueError: If an unsupported backend name is given.
    """
    if backend == "session":
        # Flush the entire session, not just the auth keys
        request.SESSION.clear()
        return

    if backend == "jwt":
        request.JWT.clear()
        return

    raise ValueError(
        f"Unknown auth backend: '{backend}'. "
        "Supported backends are 'session' and 'jwt'."
    )


def get_user_from_session(request: Any) -> Any | None:
    """
    Resolve the currently logged-in user from the session.

    Args:
        request: The Duck request object.

    Returns:
        The User instance if a valid session exists, otherwise ``None``.
    """
    user_id = request.SESSION.get(SESSION_USER_ID_KEY)

    if user_id is None:
        return None

    # Retrieve user model
    User = get_user_model()
    
    try:
        return User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return None


def get_user_from_jwt(request: Any) -> Any | None:
    """
    Resolve the currently authenticated user from a JWT in the request.

    Reads the ``Authorization: Bearer <token>`` header. Returns ``None``
    if the header is missing, malformed, or the token is invalid/expired.

    Args:
        request: The Duck request object.

    Returns:
        The User instance if a valid token exists, otherwise ``None``.
    """
    from duck.contrib.jwt import decode_token, InvalidTokenError
    
    # Get authorization.
    auth_header = request.AUTH.get("auth")
    
    if not auth_header.startswith("Bearer "):
        return None

    # Get request token.
    token = auth_header[len("Bearer "):]
    
    try:
        payload = decode_token(token)
    except InvalidTokenError:
        return None

    user_id = payload.get("user_id")
    if user_id is None:
        return None

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
) -> Any | None:
    """
    Async version of ``authenticate``.

    Wraps the sync ORM calls in ``asyncio.to_thread`` so the event loop
    is never blocked.

    Args:
        request: The Duck request object.
        username: The username or email to look up.
        password: The plain-text password to verify.

    Returns:
        The matching User instance on success, or ``None`` on failure.
    """
    return await ensure_async(authenticate)(request, username, password)


async def async_login(
    request: Any,
    user: Any,
    backend: str = "session",
) -> dict | None:
    """
    Async version of ``login``.

    Args:
        request: The Duck request object.
        user: An authenticated User instance.
        backend: Either ``"session"`` (default) or ``"jwt"``.

    Returns:
        ``None`` for the session backend, or a token pair dict for JWT.
    """
    return await ensure_asynx(login)(request, user, backend)


async def async_logout(request: Any, backend: str = "session") -> None:
    """
    Async version of ``logout``.

    Args:
        request: The Duck request object.
        backend: Either ``"session"`` (default) or ``"jwt"``.
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
        The User instance if a valid token exists, otherwise ``None``.
    """
    return await ensure_async(get_user_from_jwt)(request)
