"""
Duck's built-in authentication helpers.

Provides session and JWT-based login, logout, and credential
verification that work directly on Duck's request object.

Sync usage::

    from duck.auth import authenticate, login, logout

    user = authenticate(request, "brian", "secret")
    if user:
        login(request, user)               # session (default)
        tokens = login(request, user, backend="jwt")

    logout(request)
    logout(request, backend="jwt")

Async usage::

    from duck.auth import async_authenticate, async_login, async_logout

    user = await async_authenticate(request, "brian", "secret")
    if user:
        await async_login(request, user)
        tokens = await async_login(request, user, backend="jwt")

    await async_logout(request)
"""

from duck.contrib.auth.helpers import (
    authenticate,
    login,
    logout,
    get_user_from_session,
    get_user_from_jwt,
    async_authenticate,
    async_login,
    async_logout,
    async_get_user_from_session,
    async_get_user_from_jwt,
)

from duck.contrib.jwt import (
    encode_token,
    decode_token,
    issue_token_pair,
    rotate_refresh_token,
)

__all__ = [
    # Sync
    "authenticate",
    "login",
    "logout",
    "get_user_from_session",
    "get_user_from_jwt",
    # Async
    "async_authenticate",
    "async_login",
    "async_logout",
    "async_get_user_from_session",
    "async_get_user_from_jwt",
    # JWT tokens
    "encode_token",
    "decode_token",
    "issue_token_pair",
    "rotate_refresh_token",
]