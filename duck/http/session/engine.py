"""
Module representing Duck default session engine, i.e. SessionStore class.
"""

import uuid
import datetime
import warnings

from typing import Optional, Union
from functools import wraps

from duck.settings import SETTINGS
from duck.utils.importer import import_module_once
from duck.utils.asyncio import raise_if_in_async_context
from duck.contrib.sync import ensure_async
from duck.logging import logger


# TODO: Need to make the SESSION API fully async-compatible

session_connector_mod = import_module_once("duck.http.session.connector")


class SessionError(Exception):
    """
    Session related errors.
    """


class SessionExpired(SessionError):
    """
    Raised on save operations if a session has already expired.
    """


class SessionStore(dict):
    """
    Session store for storing session data.
    """
    __slots__ = {
        "_session_key",
        "_loaded",
        "_modified",
        "disable_warnings",
        "session_storage_connector",
    }
    
    def __init__(self, session_key: str, disable_warnings: bool = False):
        """
        Initializes the session store.
        """
        super().__init__()
        self._session_key = session_key
        self._loaded = False
        self._modified = False
        self.disable_warnings = disable_warnings
        self.session_storage_connector = session_connector_mod.get_session_storage_connector()

    @property
    def session_key(self):
        return self._session_key

    @session_key.setter
    def session_key(self, key: Optional[str]):
        # Switching identities invalidates whatever we'd loaded for the old one.
        if value != self._session_id:
            self._session_key = key
            self._loaded = False
            super().clear()

    @property
    def modified(self) -> bool:
        """
        Returns the state whether the session has been modified after load or creation.
        """
        return self._modified
    
    @property
    def loaded(self) -> bool:
        """
        Returns the state whether the session has been loaded.
        """
        return self._loaded
    
    @modified.setter
    def modified(self, what: bool):
        """
        Sets whether the session has been modified.
        """
        self._modified = what
        
    def needs_update(self) -> bool:
        """
        Returns whether the session data is worthy to be saved, this is the lazy behavior of Duck.
        """
        if not self.loaded:
            # If session hasn't been loaded, we consider it as not modified to avoid unnecessary saves
            return False
        return self.modified

    @staticmethod
    def generate_session_id() -> str:
        """
        Generates and returns a random session ID.
        """
        return str(uuid.uuid4())
    
    def session_expired(self) -> bool:
        """
        Returns boolean on whether if the session has expired depending on expiry set on session.
        """
        expiry_date = self.get_expiry_date()
        now = datetime.datetime.utcnow()
        return now >= expiry_date

    def get_expiry_age(self):
        """
        Returns the session max age from current settings.
        """
        return SETTINGS["SESSION_COOKIE_AGE"]

    def get_expiry_date(self):
        """
        Returns the datetime the session is going to expire.
        """
        expire_date = self.get("expiry_date")
        
        if not expire_date:
            self.set_expiry(
                datetime.datetime.utcnow() + datetime.timedelta(seconds=self.get_expiry_age())
            )
            return self.get_expiry_date()
        return expire_date

    def set_expiry(
        self,
        expiry: Optional[Union[int, float, datetime.datetime, datetime.timedelta]] = None,
    ):
        """
        Sets the session expiry.

        Args:
            expiry Optional[Union[int, float, datetime.datetime, datetime.timedelta]]: Float or int represents the seconds to expire from now and None represents the now plus the default session max_age.
        """
        if expiry is None:
            self["expiry_date"] = (
                datetime.datetime.utcnow()
                + datetime.timedelta(seconds=self.get_expiry_age())
            )

        elif isinstance(expiry, (datetime.datetime, datetime.timedelta)):
            self["expiry_date"] = expiry

        elif isinstance(expiry, (int, float)):
            self["expiry_date"] = (
                datetime.datetime.utcnow()
                + datetime.timedelta(seconds=expiry)
            )

        else:
            raise SessionError(
                f"Invalid expiry, expected any of [int, float, datetime.datetime, datetime.timedelta, None] but got '{type(expiry)}'"
            )
    
    @staticmethod
    def check_session_storage_connector(method):
        """
        Decorator to ensure a valid session storage connector is present.

        Validates:
            - Attribute exists
            - Attribute is not None
            - Attribute is correct type
        """
        @wraps(method)
        def wrapper(self, *args, **kwargs):
            connector = getattr(self, "session_storage_connector", None)
    
            if connector is None:
                raise ValueError("Session storage connector is not set")
    
            if not isinstance(connector, session_connector_mod.SessionStorageConnector):
                raise TypeError(
                    "Invalid session storage connector provided. "
                    f"Expected {SessionStorageConnector}, got {type(connector)}"
                )
    
            # Execute the decorated method
            return method(self, *args, **kwargs)
    
        # Return wrapper
        return wrapper
    
    @staticmethod
    def ensure_session_loaded(method):
        """
        Decorator which ensures that the session is loaded.
        """
        @wraps(method)
        def wrapper(self, *args, **kwargs):
            if not self.loaded and self._session_key:
                # Load the session key
                self.load()
            
            # Execute the decorated method
            return method(self, *args, **kwargs)
    
        # Return wrapper
        return wrapper

    @check_session_storage_connector
    def load(self) -> dict:
        """
        Loads the session from storage.
        """
        if self.loaded and not self.disable_warnings:
            logger.warn(
                f"{self.__class__.__name__} is already loaded; reloading may be inefficient."
            )
        
        # Retrieve session data from storage, if session key is invalid or session doesn't exist, get_session should return None, so we can safely fallback to empty dict
        session_data = {}
        
        if self.session_key:
            session_data = self.session_storage_connector.get_session(self.session_key) or {}
            
            # Update session store with retrieved data, this will also set the modified flag if data is not empty
            super().update(session_data) # Avoids recursion error
        
        if not self.loaded:
            self._modified = False # If session hasn't been loaded for the first time, set _modified to False
            
        # Update state and return session data
        self._loaded = True
        return session_data

    def save(self):
        """
        Save the session - will set new session key if not set.
        """
        raise_if_in_async_context("Please use 'async_save' method instead.")
        self._save()

    @check_session_storage_connector
    @ensure_session_loaded
    def _save(self):
        """
        Saves the session to storage.
        """
        if not self.session_key:
            # Assign new session key.
            self.assign_new_session_key()
            
        # Normalize session data
        session_data = dict(self)
        
        if not self.session_expired():
            # Session is not expired
            expiry_age = self.get_expiry_age()
            
            # Set the session in the real storage
            self.session_storage_connector.set_session(
                self.session_key,
                session_data,
                expiry=expiry_age,
            )

            # Save the current state of session storage
            self.session_storage_connector.save()
        
        else:
            raise SessionExpired("Cannot save an expired session, use `set_expiry` to reset the session expiry.")
        
        # Reset session modification
        self._modified = False  # reset session modification.

    @check_session_storage_connector
    def exists(self, session_key: Optional[str] = None) -> bool:
        """
        Checks if a session with the specified key exists.
        
        Args:
            session_key (Optional[str]): The session key or None if you want to use the current session key.
        """
        session_key = session_key or self.session_key
        
        try:
            return bool(self.session_storage_connector.get_session(session_key))
        except KeyError:
            return False

    @check_session_storage_connector
    def assign_new_session_key(self) -> str:
        """
        Creates a new session with a new session key.
        """
        self.session_key = self.generate_session_id()
        self._loaded = True  # brand-new id, nothing in cache to fetch
        return self.session_key
        
    @check_session_storage_connector
    @ensure_session_loaded
    def get(self, *args, **kw):
        """
        Return value for a key.
        """
        return super().get(*args, **kw)

    @check_session_storage_connector
    def delete(self, session_key: Optional[str] = None):
        """
        Deletes and clears the session from session storage.
        
        Args:
            session_key (Optional[str]): The session key or None if you want to use the current session key.    
        """
        session_key = session_key or self.session_key
        self.session_storage_connector.delete_session(session_key)
        self.clear()

    @ensure_session_loaded
    def update(self, data: dict):
        """
        Overrides the update method to ensure items are tracked for modification.
        """
        super().update(data)
        
        if data:
            self._modified = True

    @ensure_session_loaded
    def clear(self):
        """
        Clears all session data.
        """
        is_empty = bool(self or None)
        
        super().clear()
        
        if not is_empty:
            self._modified = True

    @ensure_session_loaded
    def pop(self, *args, **kwargs):
        """
        Pops some session data.
        """
        data = super().pop(*args, **kwargs)
        
        # If data is not empty, we consider the session modified, otherwise we don't to avoid unnecessary saves
        if data:
            self._modified = True
        
        # Return popped data
        return data

    @ensure_session_loaded
    def popitem(self, *args, **kwargs):
        """
        Pops some session data.
        """
        data = super().popitem(*args, **kwargs)

        # If data is not empty, we consider the session modified, otherwise we don't to avoid unnecessary saves
        if data:
            self._modified = True
        
        # Return popped data
        return data
    
    # SOME ASYNC API's
    async def async_save(self):
        """
        Asynchronously save session.
        """
        await ensure_async(self._save)()

    @ensure_session_loaded
    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self._modified = True

    @ensure_session_loaded
    def __getitem__(self, key):
        value = super().__getitem__(key)
        return value

    @ensure_session_loaded
    def __delitem__(self, key):
        super().__delitem__(key)
        self._modified = True

    @ensure_session_loaded
    def __repr__(self):
        return f"<{self.__class__.__name__} {dict(self)}>"
