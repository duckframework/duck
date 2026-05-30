"""
Module representing Duck's JWT store — payload management only.

Transport extraction and client delivery live in JWTMiddleware.
This store is concerned only with decoding, encoding, and mutating
the JWT payload — mirroring what SessionStore does for session data.
"""

import datetime

from typing import Optional, Union, Dict
from functools import wraps

from duck.settings import SETTINGS
from duck.logging import logger
from duck.contrib.jwt import (
    encode_token,
    decode_token,
    get_access_lifetime,
    get_refresh_lifetime,
    JWTInvalid,
)


class JWTStore:
    """
    Store for decoding, encoding, and managing a JWT payload.

    Mirrors the lazy-load pattern of ``SessionStore`` — the payload is
    decoded on first access and mutations are tracked via ``modified``.

    Example usage:

    ```py
    store = JWTStore(raw_token="eyJ...")
    store.load()

    user_id = store.get("user_id")
    store.set("role", "distributor")

    if store.needs_update():
        # Reset expiry - None will resolve expiry in settings.
        store.set_expiry(store.expiry_secs)
        
        # Retrieve access and refresh tokens
        access, refresh = store.encode_all()

        # Send token to client here.

        # Mark the token as synced with the client.
        store.mark_updated()
    ```

    Settings keys consumed:

    - ``JWT_SECRET_KEY`` — signing secret (required).
    - ``JWT_ALGORITHM``  — defaults to ``"HS256"``.
    - ``JWT_ACCESS_LIFETIME`` — default expiry in seconds, defaults to ``3600``.
    """

    # Slots declared as a tuple, not a set literal
    __slots__ = (
        "raw_token",
        "payload",
        "loaded",
        "modified",
    )

    def __init__(self, raw_token: Optional[str] = None):
        """
        Initializes the JWT store.

        Args:
            raw_token (Optional[str]): Encoded JWT string to decode on load,
                or ``None`` to start with an empty payload.
        """
        self.raw_token: Optional[str] = raw_token
        self.payload: dict = {}
        self.loaded: bool = False
        self.modified: bool = False
        
    @property
    def expiry_secs(self) -> Optional[float]:
        """
        Returns the remaining seconds until the token expires.

        Computed live from the ``exp`` claim rather than the originally
        set duration, so it reflects actual time-to-expiry at call time.
        Returns ``None`` if no ``exp`` claim is present, and ``0.0`` if
        already expired.

        Returns:
            Optional[float]: Seconds remaining, ``0.0`` if expired, or
                ``None`` if ``exp`` is not set.
        """
        exp = self.payload.get("exp")

        if exp is None:
            return get_access_lifetime()

        # exp may be a datetime or a numeric unix timestamp
        if isinstance(exp, datetime.datetime):
            remaining = (exp - datetime.datetime.utcnow()).total_seconds()
        else:
            remaining = exp - datetime.datetime.utcnow().timestamp()

        return float(max(0.0, remaining))
        
    # Decorator

    @staticmethod
    def ensure_loaded(method):
        """
        Decorator that auto-loads the store before the method executes.
        """
        @wraps(method)
        def wrapper(self, *args, **kwargs):
            if not self.loaded:
                self.load()
            return method(self, *args, **kwargs)

        return wrapper

    # Core load / encode

    def load(self) -> dict:
        """
        Decodes the raw token and populates the internal payload.

        If no raw token was provided, the store loads with an empty payload
        and is treated as an unauthenticated context — no error is raised.

        Returns:
            dict: The decoded JWT payload.

        Raises:
            JWTExpired: If the token's ``exp`` claim is in the past.
            JWTInvalid: If the token is malformed or signature verification fails.
        """
        if not self.raw_token:
            # No token — empty unauthenticated store
            self.payload = {}
            self.loaded = True
            return self.payload
        
        # Decode token but ignore expiry checks, the responsible middleware will check `is_expired` method 
        try:
            self.payload = decode_token(self.raw_token, verify_expiry=False)
        except JWTInvalid as e:
            raise JWTInvalid("Token invalid, try using `reset()` to reset the JWT.") from e
            
        # Mark clean after fresh decode
        self.loaded = True
        self.modified = False
        return self.payload

    def reset(self):
        """
        This will reset the set raw token.
        """
        self.raw_token = None
        
    def encode(self) -> str:
        """
        Encodes the current payload into a signed JWT string.

        Also updates ``raw_token`` with the newly encoded value.

        Returns:
            str: The signed JWT token string.

        Raises:
            JWTError: If ``exp`` has not been set on the payload.
        """
        if "exp" not in self.payload:
            raise JWTError("Expiry not set, please set it using `set_expiry` or `reset_expiry` method.")
            
        token: str = encode_token(
            payload=self.payload,
            token_type="access",
        )

        # PyJWT >=2.0 returns str; older versions return bytes
        if isinstance(token, bytes):
            token = token.decode("utf-8")

        # Keep raw_token in sync
        self.raw_token = token
        return token

    def encode_all(self) -> Dict[str, str]:
        """
        Returns a dictionary containing both access and refresh token.
        """
        return {"access": self.encode(), "refresh": self.encode_refresh_token()}
        
    def encode_refresh_token(self) -> str:
        """
        This retrieves a refresh token for this store.
        """
        token = encode_token({"exp": get_refresh_lifetime()}, token_type="refresh")
        
        # PyJWT >=2.0 returns str; older versions return bytes
        if isinstance(token, bytes):
            token = token.decode("utf-8")
        
        return token
        
    # Payload access
    @ensure_loaded
    def get(self, key: str, default=None):
        """
        Returns a claim value from the payload.

        Args:
            key (str): Claim key to look up.
            default: Returned if the key is absent.
        """
        return self.payload.get(key, default)

    @ensure_loaded
    def set(self, key: str, value):
        """
        Sets a claim and marks the store as modified.

        Args:
            key (str): Claim key.
            value: Value to store.
        """
        self.payload[key] = value
        self.modified = True

    @ensure_loaded
    def delete(self, key: str):
        """
        Removes a claim from the payload.

        Args:
            key (str): Claim key to remove.
        """
        if key in self.payload:
            del self.payload[key]
            self.modified = True

    @ensure_loaded
    def update(self, data: dict):
        """
        Merges a dict of claims into the payload.

        Args:
            data (dict): Claims to merge in.
        """
        if data:
            self.payload.update(data)
            self.modified = True

    @ensure_loaded
    def clear(self):
        """
        Clears all claims from the payload.
        """
        if self.payload:
            self.payload.clear()
            self.modified = True

    @ensure_loaded
    def keys(self):
        return self.payload.keys()
    
    @ensure_loaded
    def values(self):
        return self.payload.values()
    
    @ensure_loaded
    def items(self):
        return self.payload.items()
        
    # Expiry helpers

    def set_expiry(
        self,
        expiry: Optional[Union[int, float, datetime.datetime, datetime.timedelta]] = None,
    ):
        """
        Sets the ``exp`` claim on the payload.

        Args:
            expiry (Optional[Union[int, float, datetime.datetime, datetime.timedelta]]):
                - ``int`` / ``float`` — seconds from now.
                - ``datetime.timedelta`` — duration added to now.
                - ``datetime.datetime`` — absolute expiry datetime.
                - ``None`` — falls back to ``JWT_ACCESS_LIFETIME_AGE`` from settings.

        Raises:
            JWTError: If the expiry type is not supported.
        """
        now = datetime.datetime.utcnow()

        if expiry is None:
            age = get_access_lifetime()
            self.payload["exp"] = now + datetime.timedelta(seconds=age)

        elif isinstance(expiry, (int, float)):
            self.payload["exp"] = now + datetime.timedelta(seconds=expiry)

        elif isinstance(expiry, datetime.timedelta):
            # total_seconds() is the correct method (not .to_seconds())
            self.payload["exp"] = now + expiry

        elif isinstance(expiry, datetime.datetime):
            # Subtraction yields a timedelta, extract float seconds
            self.payload["exp"] = expiry
            
        else:
            raise JWTError(
                f"Unsupported expiry type '{type(expiry)}'. "
                "Expected int, float, timedelta, datetime, or None."
            )

        self.modified = True

    def reset_expiry(self):
        """
        Reset the expiry to the exact seconds last used for the JWT or the seconds set in settings or default seconds.
        """
        self.set_expiry(self.expiry_secs)
        
    def is_expired(self) -> bool:
        """
        Returns whether the ``exp`` claim is in the past.

        Returns:
            bool: ``True`` if expired or if no ``exp`` claim is present.
        """
        exp = self.payload.get("exp")

        if exp is None:
            return False # None expirying

        if isinstance(exp, datetime.datetime):
            return datetime.datetime.utcnow() >= exp

        # Numeric unix timestamp
        return datetime.datetime.utcnow().timestamp() >= exp

    def mark_updated(self):
        """
        Resets the modified flag after the token has been sent to the client.
        """
        self.modified = False

    def needs_update(self) -> bool:
        """
        Returns whether the payload has unsaved modifications.

        Mirrors ``SessionStore.needs_update`` — only meaningful once loaded.

        Returns:
            bool: ``True`` if the store is loaded and has been modified.
        """
        if not self.loaded:
            return False
        return self.modified

    # Dunder helpers

    @ensure_loaded
    def __setitem__(self, key, value):
        self.payload[key] = value
        self.modified = True

    @ensure_loaded
    def __getitem__(self, key):
        return self.payload[key]

    @ensure_loaded
    def __delitem__(self, key):
        del self.payload[key]
        self.modified = True

    @ensure_loaded
    def __contains__(self, key):
        return key in self.payload

    @ensure_loaded
    def __repr__(self):
        return f"<{self.__class__.__name__} {self.payload}>"

    @ensure_loaded
    def __iter__(self):
        return iter(self.payload)
