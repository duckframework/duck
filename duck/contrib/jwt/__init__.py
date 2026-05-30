"""
JWT utilities for Duck's auth system.

Provides token encoding, decoding, issuance, and rotation.
Requires PyJWT — install with: pip install PyJWT
"""

import datetime

from typing import Any, Dict

from duck.settings import SETTINGS


class JWTError(Exception):
    """
    Base class for JWT-related errors.
    """


class JWTExpired(JWTError):
    """
    Raised when a JWT has expired.
    """


class JWTInvalid(JWTError):
    """
    Raised when a JWT cannot be decoded or is structurally invalid.
    """


def get_jwt_lib():
    """
    Import and return the PyJWT module.

    Returns:
        The imported ``jwt`` module.

    Raises:
        ImportError: If the ``PyJWT`` package is not installed.
    """
    try:
        import jwt
        return jwt

    except (ImportError, ModuleNotFoundError) as e:
        raise ImportError(
            "Failed to import the 'PyJWT' package. "
            "Install it using: pip install PyJWT"
        ) from e


def get_secret_key() -> str:
    """
    Retrieve the secret key from Duck settings.

    Returns:
        The ``SECRET_KEY`` string from settings.
    """
    secret = SETTINGS.get("JWT_SECRET_KEY") or SETTINGS.get('SECRET_KEY')
    
    if not secret:
        raise JWTError(
            "JWT_SECRET_KEY is not set in Duck settings. "
            "This is required for JWT encoding and decoding."
        )
    
    # Finally, return secret
    return secret


def get_algorithm() -> str:
    """
    Retrieve the JWT signing algorithm from Duck settings.

    Defaults to ``HS256`` if ``JWT_ALGORITHM`` is not set.

    Returns:
        The algorithm string (e.g. ``"HS256"``).
    """
    return SETTINGS.get("JWT_ALGORITHM", "HS256")


def get_access_lifetime() -> datetime.timedelta:
    """
    Retrieve the access token lifetime from Duck settings.

    Defaults to 60 minutes if ``JWT_ACCESS_LIFETIME`` is not set.

    Returns:
        Seconds representing the access token lifetime.
    """
    return SETTINGS.get("JWT_ACCESS_LIFETIME", 3600)
    

def get_refresh_lifetime() -> float:
    """
    Retrieve the refresh token lifetime from Duck settings.

    Defaults to 7 days in seconds if ``JWT_REFRESH_LIFETIME`` is not set.

    Returns:
        Seconds representing the refresh token lifetime.
    """
    return SETTINGS.get("JWT_REFRESH_LIFETIME", 7 * 24 * 3600)
    

def encode_token(
    payload: dict[str, Any],
    token_type: str = "access",
) -> str:
    """
    Encode a signed JWT token from the given payload.
    
    Args:
        payload: Data to embed in the token (e.g. ``{"user_id": 1}``).
        token_type: Either ``"access"`` or ``"refresh"``. Controls the
            default expiry when ``expires_in`` is not given.
        expires_in: Custom expiry duration. Overrides settings-based defaults.

    Returns:
        A signed JWT string.
    """
    jwt = get_jwt_lib()
    
    if "exp" not in payload:
        raise JWTError(f"Expiry not set, please include key 'exp' in payload.")
    
    elif payload["exp"] is None:
        raise JWTError(f"Expiry is None, please include key 'exp' in payload.")
        
    claims = {
        **payload,
        "type": token_type,
        "iat":  int(datetime.datetime.utcnow().timestamp()),
    }
    return jwt.encode(claims, get_secret_key(), algorithm=get_algorithm())


def decode_token(token: str, verify_expiry: bool = True) -> Dict[str, Any]:
    """
    Decode and verify a signed JWT token.

    Args:
        token: The raw JWT string to decode.
        verify_expiry: Whether to verify. If True,  `JWTExpired` may be raised on expiry.

    Returns:
        The decoded payload as a dict.

    Raises:
        JWTExpired: If the token's ``exp`` claim has passed.
        JWTInvalid: If the token is malformed, tampered with, or the
            signature does not match.
    """
    jwt = get_jwt_lib()

    try:
        return jwt.decode(
            token,
            get_secret_key(),
            algorithms=[get_algorithm()],
            options={"verify_exp": verify_expiry},
        )

    except jwt.ExpiredSignatureError as e:
        raise JWTExpired("Token has expired.") from e

    except jwt.InvalidTokenError as e:
        raise JWTInvalid(f"Token is invalid: {e}") from e


def issue_token_pair(
    payload: dict[str, Any] | None = None,
) -> dict[str, str]:
    """
    Issue both an access and a refresh token for a user.

    Args:
        payload: Additional claims embedded in both tokens.
        
    Returns:
        A dict with ``"access"`` and ``"refresh"`` JWT strings.
    """
    return {
        "access":  encode_token(payload, token_type="access"),
        "refresh": encode_token(payload, token_type="refresh"),
    }
