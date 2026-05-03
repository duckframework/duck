"""
Session middleware for Duck — covers both HTTP request/response
and Lively WebSocket events.

The session cookie is established once on the initial HTTP handshake.
Lively events share that same request object, so they only need to
persist any session mutations — no cookie header can be sent mid-WebSocket.
"""

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

    Lively (WebSocket) flow:
        process_lively_event — called after each Lively component dispatch event.
                                Saves the session if it was modified. No cookie
                                header is written because the WS connection
                                already shares the original HTTP session.

    Notes:
        Duck is lazy — it does not save the session automatically. This
        middleware is the single place responsible for all persistence.
        Never call request.SESSION.save() manually in a view or component
        if you want the Set-Cookie header to be handled correctly.
    """

    debug_message: str = "SessionMiddleware: Session Error"

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
        session_cookie_name = SETTINGS["SESSION_COOKIE_NAME"]
        session_key = request.COOKIES.get(session_cookie_name)
        session_exists = False

        if session_key:
            request.SESSION.session_key = session_key
            try:
                data = request.SESSION.load()
                if data:
                    session_exists = True
            except KeyError:
                # Cookie present but session no longer in storage — treat as new
                pass

        if not session_exists and not session_key:
            # Brand new visitor — allocate a session slot now
            request.SESSION.create()

        request.session_exists = session_exists
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
        from duck.http.session.engine import SessionExpired

        if not request.SESSION.needs_update():
            # Nothing changed — skip the DB write and cookie overhead
            return

        # Initialize variable for storing session expiry.
        session_expired = False

        try:
            request.SESSION.save()
        except SessionExpired:
            # Session TTL elapsed between request and response — reset it
            session_expired = True
            request.set_expiry(None)  # Falls back to SESSION_AGE from settings
            request.SESSION.save()

        if request.session_exists or session_expired:
            # Client already holds a valid cookie — no need to resend it
            return

        # New session — build and attach the Set-Cookie header
        expire_at_browser_close = SETTINGS["SESSION_EXPIRE_AT_BROWSER_CLOSE"]
        expires = request.SESSION.get_expiry_date() if not expire_at_browser_close else None
        session_key = request.SESSION.session_key
        session_cookie_name = SETTINGS["SESSION_COOKIE_NAME"]
        session_cookie_domain = (
            SETTINGS["SESSION_COOKIE_DOMAIN"]
            or Meta.get_metadata("DUCK_SERVER_DOMAIN")
        )
        path = SETTINGS["SESSION_COOKIE_PATH"]
        secure = SETTINGS["SESSION_COOKIE_SECURE"]
        httponly = SETTINGS["SESSION_COOKIE_HTTPONLY"]
        samesite = SETTINGS["SESSION_COOKIE_SAMESITE"]

        if session_cookie_name in response.cookies:
            # Something else already wrote the cookie — don't overwrite it
            return

        response.set_cookie(
            session_cookie_name,
            value=session_key,
            domain=session_cookie_domain,
            path=path,
            expires=expires,
            secure=secure,
            httponly=httponly,
            samesite=samesite,
        )

    @classmethod
    async def process_lively_event(cls, ws, request: HttpRequest) -> None:
        """
        Persist a modified session after a Lively WebSocket event completes.

        If the session is new (client has no cookie yet), the session key is
        pushed to the browser via document.cookie over the WebSocket — the only
        channel available once the HTTP handshake is done.

        Args:
            ws: The LivelyWebSocketView handling the current event.
            request: The shared HTTP request.
        """
        from duck.http.session.engine import SessionExpired
        from duck.contrib.sync import ensure_async
        
        print("Processing lively event")
        if not request.SESSION.needs_update():
            return

        session_expired = False

        try:
            await ensure_async(request.SESSION.save)()
        except SessionExpired:
            session_expired = True
            request.set_expiry(None)
            await ensure_async(request.SESSION.save)()

        # Cookie already in the browser — nothing more to do
        if request.session_exists and not session_expired:
            return

        # New or expired session — push the cookie via JS since no HTTP
        # response headers are available over an active WebSocket connection
        session_key = request.SESSION.session_key
        session_cookie_name = SETTINGS["SESSION_COOKIE_NAME"]
        session_cookie_domain = (
            SETTINGS["SESSION_COOKIE_DOMAIN"]
            or Meta.get_metadata("DUCK_SERVER_DOMAIN")
        )
        expire_at_browser_close = SETTINGS["SESSION_EXPIRE_AT_BROWSER_CLOSE"]
        path = SETTINGS["SESSION_COOKIE_PATH"]
        secure = SETTINGS["SESSION_COOKIE_SECURE"]
        samesite = SETTINGS["SESSION_COOKIE_SAMESITE"]

        # Build the cookie string the same way a Set-Cookie header would
        cookie_parts = [f"{session_cookie_name}={session_key}"]

        if not expire_at_browser_close:
            expires = request.SESSION.get_expiry_date()
            # Format as UTC string that document.cookie understands
            cookie_parts.append(f"expires={expires.strftime('%a, %d %b %Y %H:%M:%S GMT')}")

        if path:
            cookie_parts.append(f"path={path}")

        if session_cookie_domain:
            cookie_parts.append(f"domain={session_cookie_domain}")

        if samesite:
            cookie_parts.append(f"SameSite={samesite}")

        if secure:
            cookie_parts.append("Secure")

        cookie_str = "; ".join(cookie_parts)

        # Set on client — only way to deliver a cookie over WebSocket
        await ws.execute_js(f"document.cookie = {cookie_str!r};")
        
        # Mark session as existing so subsequent events in the same WS
        # connection don't re-send the cookie unnecessarily
        request.session_exists = True
