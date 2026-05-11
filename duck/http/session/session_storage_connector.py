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
    Raised when errors related to the session storage connector arises
    """


class SessionStorageConnector:
    """
    This class is used to connect to the session storage and perform almost all the operations on the session storage
    """

    _instance = None
    _initialized = False
    
    CACHED_SESSIONS = InMemoryCache(maxkeys=1024 * 4)
    """
    In Memory cache for sessions.
    """

    def __init__(self, session_storage_cls: Callable):
        """
        Initialize SessionStorageConnector

        Args:
            session_storage_cls (Callable): Class to initialize the session storage object
        """
        if self.__class__._initialized:
            if session_storage_cls is not self.session_storage_cls:
                raise SessionStorageConnectorError(
                    "SessionStorageConnector already initialized with a different session storage class."
                )
            return

        self.session_dir = SETTINGS["SESSION_DIR"]
        self.session_storage_cls = session_storage_cls

        if self.session_dir:
            os.makedirs(self.session_dir, exist_ok=True)

        try:
            self._session_storage = session_storage_cls()
        except TypeError:
            self._session_storage = session_storage_cls(self.session_dir)

        self.__class__._initialized = True

    @staticmethod
    def generate_session_id() -> str:
        """
        Retrieve a random generated session ID.
        """
        return str(uuid.uuid4())

    def set_session(
        self,
        session_id: str,
        data: dict,
        expiry: int | float = None
    ):
        """
        Set the session data.
        """
        if expiry:
            self._session_storage.set(session_id, data, expiry)
        else:
            self._session_storage.set(session_id, data)
        
        # Update cache in memory also - only if not in memory cache is used
        if not issubclass(self.session_storage_cls, InMemoryCache):
            self.CACHED_SESSIONS.set(session_id, data, expiry=expiry)

    def update_session(self, session_id: str, data: dict):
        """
        Update the session data.
        """
        prev_data = self.get_session(session_id) or {}
        prev_data.update(data)
        self.set_session(session_id, prev_data)

    def get_session(self, session_id: str):
        """
        Get the session data.
        """
        # Get session from cache - only if not in memory cache is used
        if not issubclass(self.session_storage_cls, InMemoryCache):
            session = self.CACHED_SESSIONS.get(session_id)

            if session is not None:
                return session
        
        # Get session from real storage
        return self._session_storage.get(session_id)

    def delete_session(self, session_id: str):
        """
        Delete session data.
        """
        self._session_storage.delete(session_id)

    def clear_all_sessions(self):
        """
        Clear all session data.
        """
        self._session_storage.clear()

    def save(self):
        """
        Saves the current sessions to session storage.
        """
        self._session_storage.save()

    def close(self):
        """
        Close the session storage.
        """
        self._session_storage.close()

    def __new__(cls, session_storage_cls: CacheBase):
        from duck.meta import Meta

        if cls._instance is None:
            Meta.set_metadata("SESSION_STORAGE_SET", True)
            cls._instance = super().__new__(cls)
        return cls._instance
