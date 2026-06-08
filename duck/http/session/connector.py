"""
Module containing SessionConnector class which can be used to connect to
session storage to perform operations like get, set, update, delete, clear, etc.
"""

import os
import uuid

from typing import Callable

from duck.settings import SETTINGS
from duck.settings.loaded import SettingsLoaded
from duck.utils.caching import CacheBase, InMemoryCache


def get_session_storage_connector():
    """
    Returns the session storage connector object.
    """
    return SettingsLoaded.SESSION_STORAGE_CONNECTOR.getresult()


class SessionStorageConnectorError(Exception):
    """
    Raised when errors related to the session storage connector arise.
    """


class SessionStorageConnector:
    """
    Connects to the configured session storage backend and exposes a uniform
    interface for get, set, update, delete, and clear operations.

    A write-through in-memory cache sits in front of the real storage backend
    to reduce latency on repeated reads. The cache layer is bypassed entirely
    when the backend is itself an InMemoryCache.
    """

    instance = None
    initialized = False

    CACHED_SESSIONS = InMemoryCache(maxkeys=1024 * 4)
    """
    Write-through in-memory cache that fronts the real session storage backend.
    """

    def __new__(cls, session_storage_cls: type[CacheBase]):
        from duck.meta import Meta

        if cls.instance is None:
            Meta.set_metadata("SESSION_STORAGE_SET", True)
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, session_storage_cls: type[CacheBase]):
        """
        Initializes the connector with the given storage backend class.

        Initialization only runs once — subsequent calls with the same class
        are no-ops. Passing a different class after initialization raises an
        error to prevent silent misconfiguration.

        Args:
            session_storage_cls: The storage backend class to instantiate.

        Raises:
            SessionStorageConnectorError: If already initialized with a different class.
        """
        from duck.utils.caching.encrypted import EncryptedCache
        
        if self.__class__.initialized:
            if session_storage_cls is not self.session_storage_cls:
                raise SessionStorageConnectorError(
                    "SessionStorageConnector already initialized with a "
                    "different session storage class."
                )
            return

        self.session_storage_cls = session_storage_cls
        self.session_dir = SETTINGS["SESSION_DIR"]
        
        # Ensure the session directory exists if one is configured
        if self.session_dir:
            os.makedirs(self.session_dir, exist_ok=True)

        # Some backends take a directory path, others take no arguments
        try:
            raw_session_storage = session_storage_cls()
        except TypeError:
            raw_session_storage = session_storage_cls(self.session_dir)
        
        # Wrap session storage
        self._session_storage = EncryptedCache(backend=raw_session_storage, secret_key=SETTINGS["SECRET_KEY"])
        self.__class__.initialized = True

    # Convenience flag so callers can check without inspecting the class directly
    @property
    def using_memory_backend(self) -> bool:
        """
        Returns True when the backend is itself an InMemoryCache.

        When True, the write-through cache layer is bypassed to avoid
        double-storing the same data in two separate InMemoryCache instances.
        """
        return issubclass(self.session_storage_cls, InMemoryCache)

    @staticmethod
    def generate_session_id() -> str:
        """
        Returns a randomly generated session ID.
        """
        return str(uuid.uuid4())

    def set_session(
        self,
        session_id: str,
        data: dict,
        expiry: int | float | None = None,
    ) -> None:
        """
        Writes session data to the backend and updates the in-memory cache.

        Args:
            session_id: The session identifier.
            data: The session data to store.
            expiry: Optional TTL in seconds. Omitted from the call if not provided.
        """
        if expiry is not None:
            self._session_storage.set(session_id, data, expiry)
        else:
            self._session_storage.set(session_id, data)

        # Mirror into the cache only when the backend is not already in-memory
        if not self.using_memory_backend:
            if expiry is not None:
                self.CACHED_SESSIONS.set(session_id, data, expiry=expiry)
            else:
                self.CACHED_SESSIONS.set(session_id, data)

    def update_session(self, session_id: str, data: dict) -> None:
        """
        Merges new data into an existing session, preserving existing keys.

        Args:
            session_id: The session identifier.
            data: Partial data to merge into the current session.
        """
        prev_data = self.get_session(session_id) or {}
        prev_data.update(data)
        self.set_session(session_id, prev_data)

    def get_session(self, session_id: str) -> dict | None:
        """
        Retrieves session data, consulting the in-memory cache first.

        Args:
            session_id: The session identifier.

        Returns:
            The session data dict, or None if the session does not exist.
        """
        if not self.using_memory_backend:
            # Check the fast in-memory cache before hitting real storage
            cached = self.CACHED_SESSIONS.get(session_id)
            if cached is not None:
                return cached

        return self._session_storage.get(session_id)

    def delete_session(self, session_id: str) -> None:
        """
        Deletes a session from both the backend and the in-memory cache.

        Args:
            session_id: The session identifier to remove.
        """
        self._session_storage.delete(session_id)

        # Keep the cache consistent on deletion
        if not self.using_memory_backend:
            self.CACHED_SESSIONS.delete(session_id)

    def clear_all_sessions(self) -> None:
        """
        Clears all sessions from the backend and flushes the in-memory cache.
        """
        self._session_storage.clear()

        # Flush the cache so stale entries don't linger after a full clear
        if not self.using_memory_backend:
            self.CACHED_SESSIONS.clear()

    def save(self) -> None:
        """
        Persists current session state to the backend storage.
        """
        self._session_storage.save()

    def close(self) -> None:
        """
        Closes the session storage backend connection.
        """
        self._session_storage.close()
