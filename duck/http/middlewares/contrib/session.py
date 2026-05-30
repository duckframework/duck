"""
Session middleware for Duck.

The session cookie is established once on the initial HTTP handshake.
"""
from typing import Optional

from duck.settings import SETTINGS
from duck.http.middlewares import BaseMiddleware
from duck.http.request import HttpRequest
from duck.meta import Meta


class SessionMiddleware(BaseMiddleware):
    """
    Creates, loads, and persists user sessions across both HTTP and Lively events.

    HTTP flow:
        process_request  — load or create the session from the cookie.
        process_response — if the session was modified, save it and set the
                           Set-Cookie header for new or expired sessions.
                           
    Notes:
        Duck is lazy — it does not save the session automatically. This
        middleware is the single place responsible for all persistence.
        Never call request.SESSION.save() manually in a view or component
        if you want the Set-Cookie header to be handled correctly.
    """

    debug_message: str = "SessionMiddleware: Session Error"

    @classmethod
    def get_session_key_from_cookie(cl, request: HttpRequest) -> Optional[str]:
        """
        Returns the session key from request COOKIE.
        """
        session_cookie_name = SETTINGS["SESSION_COOKIE_NAME"]
        return request.COOKIES.get(session_cookie_name)
        
    @classmethod
    def process_request(cls, request: HttpRequest) -> int:
        """
        Load an existing session from the cookie, or create a fresh one.

        Sets request.session_exists so process_response knows whether to
        send a Set-Cookie header.

        Args:
            request: The incoming HTTP request.

        Returns:
            int: cls.request_ok always — session errors are non-fatal.
        """
        # NOTE: Sessions are now loaded lazily on access/update
        session_key = cls.get_session_key_from_cookie(request)
        
        if session_key is not None:
            request.SESSION.session_key = session_key
        else:
            # Brand new visitor — generate session key
            request.SESSION.assign_new_session_key()
        return cls.request_ok

    @classmethod
    def process_response(cls, response, request):
        """
        Persist a modified session and set the Set-Cookie header when needed.

        The cookie is only written for new sessions or sessions that expired
        and were recreated. Existing sessions already have the cookie in the
        browser, so resending it is unnecessary.

        Args:
            response: The outgoing HTTP response object.
            request: The corresponding HTTP request.
        """
        # Set session
        session = request.SESSION
        
        if not session.needs_update():
            # Nothing changed — skip the DB write and cookie overhead
            return

        # Initialize variable for storing session info.
        session_expired = session.session_expired()
        session_key_from_cookie = cls.get_session_key_from_cookie(request)
        session_cookie_present = bool(session_key_from_cookie)

        if session_expired:
            # Session expired between request and response — reset it
            session.set_expiry(None)  # Falls back to SESSION_COOKIE_AGE from settings

        # Save the session to the DB, generating a new session key if it expired
        session.save()

        # Decide whether to send session cookie
        if session_cookie_present and not session_expired:
            # Client already holds a valid cookie — no need to resend it
            return

        # New session — build and attach the Set-Cookie header
        path = SETTINGS["SESSION_COOKIE_PATH"]
        secure = SETTINGS["SESSION_COOKIE_SECURE"]
        httponly = SETTINGS["SESSION_COOKIE_HTTPONLY"]
        samesite = SETTINGS["SESSION_COOKIE_SAMESITE"]
        expire_at_browser_close = SETTINGS["SESSION_EXPIRE_AT_BROWSER_CLOSE"]
        expires = session.get_expiry_date() if not expire_at_browser_close else None
        session_cookie_name = SETTINGS["SESSION_COOKIE_NAME"]
        session_cookie_domain = SETTINGS["SESSION_COOKIE_DOMAIN"] or Meta.get_metadata("DUCK_SERVER_DOMAIN")
        
        if session_cookie_name in response.cookies:
            # Something else already wrote the cookie — don't overwrite it
            return
        
        response.set_cookie(
            session_cookie_name,
            value=session.session_key,
            domain=session_cookie_domain,
            path=path,
            expires=expires,
            secure=secure,
            httponly=httponly,
            samesite=samesite,
        )
