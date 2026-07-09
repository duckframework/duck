"""
MCP session store.

Sessions are stored entirely in the configured InMemoryCache, which provides
LRU eviction and TTL expiration automatically.
"""

from __future__ import annotations

import uuid

from typing import Optional
from functools import wraps

from duck.utils.caching import InMemoryCache

from duck.contrib.mcp.exceptions import SessionError


# Registry for all sessions
DEFAULT_SESSION_REGISTRY = InMemoryCache(maxkeys=2048)


class SessionStore(dict):
    """
    Represents a single MCP session.

    Session data is cached in-memory using the provided cache instance.
    """

    __slots__ = ("_session_id", "_cache", "_ttl", "_loaded", "_modified")

    def __init__(
        self,
        cache: Optional[InMemoryCache] = None,
        session_id: Optional[str] = None,
        ttl: int = 3600,
    ):
        """
        Initialize a session.

        Args:
            cache: Shared in-memory cache.
            session_id: Existing session ID. A new one is generated if omitted.
            ttl: Session lifetime in seconds.
        """
        super().__init__()
        
        # Initialize the session store.
        self._session_id = session_id
        
        # Some private attributes
        self._cache = cache or DEFAULT_SESSION_REGISTRY
        self._ttl = ttl
        self._loaded = False
        self._modified = False

    @property
    def session_id(self) -> Optional[str]:
        return self._session_id

    @session_id.setter
    def session_id(self, value: Optional[str]):
        # Switching identities invalidates whatever we'd loaded for the old one.
        if value != self._session_id:
            self._session_id = value
            self._loaded = False
            self._modified = False
            super().clear()

    @property
    def loaded(self) -> bool:
        return self._loaded

    @property
    def modified(self) -> bool:
        """
        Whether the session data has changed since it was last loaded or saved.
        """
        return self._modified

    @staticmethod
    def generate_session_id() -> str:
        """
        Generate a new session identifier.
        """
        return str(uuid.uuid4().hex)

    @staticmethod
    def ensure_session_loaded(method):
        """
        Decorator which ensures that the session is loaded.
        """
        @wraps(method)
        def wrapper(self, *args, **kwargs):
            if not self.loaded and self._session_id:
                # Load from session cache
                self.load()
            
            # Execute the decorated method
            return method(self, *args, **kwargs)
    
        # Return wrapper
        return wrapper
        
    def assign_new_session_id(self) -> str:
        """
        Creates a new session with a new session id.
        """
        self.session_id = self.generate_session_id()
        self._loaded = True  # brand-new id, nothing in cache to fetch
        return self.session_id
        
    def load(self) -> dict:
        """
        Load session data from cache.
        """
        super().clear()
        
        # Fetch new data.
        data = self._cache.get(self.session_id)

        if data:
            super().update(data)

        # Flag that session has been loaded
        self._loaded = True

        # Freshly loaded data reflects what's in cache, so nothing's dirty yet.
        self._modified = False

        # Return loaded data.
        return dict(self)

    @ensure_session_loaded
    def save(self) -> None:
        """
        Persist the session to cache.
        """
        if not self.session_id:
            raise SessionError("Cannot save session without session ID assigned.")
        # Set the session in cache.
        self._cache.set(self.session_id, dict(self), expiry=self._ttl)

        # Persisted, so there are no pending changes anymore.
        self._modified = False

    @ensure_session_loaded
    def delete(self) -> None:
        """
        Delete the session.
        """
        self._cache.delete(self.session_id)
        super().clear()
        self._modified = False

    @ensure_session_loaded
    def exists(self) -> bool:
        """
        Return whether the session exists.
        """
        return self._cache.get(self.session_id) is not None

    def touch(self) -> None:
        """
        Refresh the session TTL.
        """
        self.save()

    def needs_update(self) -> bool:
        """
        Return whether the session has pending changes that haven't been saved yet.
        """
        return self.modified

    @ensure_session_loaded
    def setdefault(self, *a, **kw):
        """
        Set a default value for a key if it's not already present, marking the
        session as modified.
        """
        self._modified = True
        return super().setdefault(*a, **kw)

    @ensure_session_loaded
    def __setitem__(self, key, value):
        """
        Set a key's value, marking the session as modified.
        """
        self._modified = True
        super().__setitem__(key, value)

    @ensure_session_loaded
    def __delitem__(self, key):
        """
        Delete a key, marking the session as modified.
        """
        self._modified = True
        super().__delitem__(key)

    @ensure_session_loaded
    def update(self, *a, **kw):
        """
        Update multiple keys at once, marking the session as modified.
        """
        self._modified = True
        super().update(*a, **kw)

    @ensure_session_loaded
    def pop(self, *a, **kw):
        """
        Remove and return a key's value, marking the session as modified.
        """
        self._modified = True
        return super().pop(*a, **kw)

    @ensure_session_loaded
    def popitem(self):
        """
        Remove and return a (key, value) pair, marking the session as modified.
        """
        self._modified = True
        return super().popitem()

    @ensure_session_loaded
    def clear(self):
        """
        Remove all data from the session, marking the session as modified.
        """
        self._modified = True
        super().clear()

    @ensure_session_loaded
    def __getitem__(self, key):
        return super().__getitem__(key)

    @ensure_session_loaded
    def __contains__(self, key):
        return super().__contains__(key)
            
    @ensure_session_loaded
    def __repr__(self) -> str:
        return f"<SessionStore {dict(self)}>"
    
    def __str__(self) -> str:
        return self.__repr__()
