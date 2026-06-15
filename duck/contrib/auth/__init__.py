"""
Duck's built-in authentication helpers.

Provides session and JWT-based login, logout, and credential
verification that work directly on Duck's request object.

Sync usage::

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
"""
from duck.contrib.auth.exceptions import AuthenticationError
from duck.contrib.auth.helpers import (
    authenticate,
    login,
    logout,
    get_user_id,
    get_user_from_session,
    get_user_from_jwt,
    async_authenticate,
    async_login,
    async_logout,
    async_get_user_from_session,
    async_get_user_from_jwt,
    set_default_auth_backend,
)


__all__ = [
    # Sync
    "authenticate",
    "login",
    "logout",
    "get_user_id",
    "get_user_from_session",
    "get_user_from_jwt",
    # Async
    "async_authenticate",
    "async_login",
    "async_logout",
    "async_get_user_from_session",
    "async_get_user_from_jwt",
    # Other
    "set_default_auth_backend",
]
