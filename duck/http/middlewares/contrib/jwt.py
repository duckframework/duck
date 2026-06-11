"""
JWT middleware for Duck.

The JWT is extracted once on the initial HTTP handshake and attached
to the request as ``request.JWT``. Lively events share that same
request object and only need to re-encode and push the token if the
payload was mutated — no HTTP headers can be written mid-WebSocket.
"""
import datetime

from typing import Optional

from duck.settings import SETTINGS
from duck.meta import Meta
from duck.http.middlewares import BaseMiddleware
from duck.http.request import HttpRequest
from duck.http.response import HttpResponse
from duck.contrib.jwt import (
    JWTExpired,
    JWTInvalid,
    decode_token,
    get_access_lifetime,
    get_refresh_lifetime,
)


# Transport configurations
TRANSPORT_COOKIE = "cookie"
TRANSPORT_HEADER = "header"

# Valid JWT transports
VALID_TRANSPORTS = (TRANSPORT_COOKIE, TRANSPORT_HEADER)


class JWTMiddleware(BaseMiddleware):
    """
    Extracts, validates, and delivers JWTs across HTTP and Lively WebSocket flows.

    HTTP flow:
        process_request  — extract the raw token from the configured transport
                           (cookie or header), build a ``JWTStore``, and attach
                           it to ``request.JWT``.
                           
        process_response — if the payload was modified, re-encode the token and
                           write it back via ``Set-Cookie`` or a response header.
                           
    Notes:
        The store is lazy — ``JWTStore.load()`` decodes the token on first
        payload access, not on construction. Expired or missing tokens result
        in an empty, unauthenticated store rather than a hard error, so views
        can decide how to respond.
    """

    debug_message: str = "JWTMiddleware: JWT Error"

    @classmethod
    def resolve_transport(cls) -> str:
        """
        Reads and validates ``JWT_TRANSPORT`` from settings.

        Returns:
            str: The normalised transport string (``"cookie"`` or ``"header"``).

        Raises:
            ValueError: If the setting is missing or not a recognised transport.
        """
        transport = SETTINGS.get("JWT_TRANSPORT", "cookie").lower()

        if transport not in VALID_TRANSPORTS:
            raise ValueError(
                f"Invalid or missing JWT_TRANSPORT '{transport}'. "
                f"Valid options are: {VALID_TRANSPORTS}"
            )

        return transport

    @classmethod
    def get_raw_token_from_request(cls, request: HttpRequest, token_type: str = "access") -> Optional[str]:
        """
        Extracts the raw JWT string from the incoming request.

        Reads from whichever transport is configured in settings — either
        a named cookie or a custom HTTP header.

        Args:
            request (HttpRequest): The incoming Duck HTTP request.
            token_type (str): The type of token. Whether `access` or `refresh`.
            
        Returns:
            Optional[str]: The raw token string, or ``None`` if absent.
        """
        transport = cls.resolve_transport()
        is_access_token = (token_type == "access")
        
        if token_type not in ("access", "refresh"):
            raise ValueError(f"Token type must be either 'access' or 'refresh' not '{token_type}'")
            
        if transport == TRANSPORT_COOKIE:
            if is_access_token:
                cookie_name = SETTINGS.get("JWT_COOKIE_NAME", "jwt")
            else:
                cookie_name = SETTINGS.get("JWT_REFRESH_COOKIE_NAME", "jwt-refresh")
            return request.COOKIES.get(cookie_name)

        if transport == TRANSPORT_HEADER:
            if is_access_token:
                header_name = SETTINGS.get("JWT_HEADER_NAME", "X-JWT-Token")
            else:
                header_name = SETTINGS.get("JWT_REFRESH_HEADER_NAME", "X-Refresh-JWT-Token")
            return request.get_header(header_name)
            
        return None

    @classmethod
    def process_request(cls, request: HttpRequest) -> int:
        """
        Builds and attaches a ``JWTStore`` to the request.

        Expired or invalid tokens are swallowed here — the store is attached
        as empty so downstream views receive a consistent ``request.JWT``
        object regardless of token state.

        Args:
            request (HttpRequest): The incoming HTTP request.

        Returns:
            int: ``cls.request_ok`` always — JWT errors are non-fatal at this stage.
        """
        raw_token = cls.get_raw_token_from_request(request, token_type="access")

        # Attach store — decoding happens lazily on first access
        if raw_token is not None:
            request.JWT.raw_token = raw_token
        else:
            # Brand new visitor — just do nothing
            pass
        return cls.request_ok

    @classmethod
    def process_response(cls, response, request: HttpRequest):
        """
        Re-encodes and delivers the JWT if the payload was modified.

        For ``cookie`` transport, writes a ``Set-Cookie`` header.
        For ``header`` transport, sets the configured response header.

        Args:
            response: The outgoing Duck HTTP response object.
            request (HttpRequest): The corresponding HTTP request.
        """
        # When JWTStore is modified, new access & refresh tokens need to be sent nomatter what.
        # Even if the previous token expired.
        store = request.JWT
        refresh_token = cls.get_raw_token_from_request(request, token_type="refresh")
        has_work = store.needs_update() or store.is_expired() or refresh_token is not None
        
        if not has_work:
            return
            
        if refresh_token:
            # Refresh token is included, lets check it
            try:
                refresh_payload = decode_token(refresh_token)
                refresh_token_type = refresh_payload.get("type")
                
                if refresh_token_type != "refresh":
                    raise JWTInvalid(f"Expected a refresh token but got '{refresh_token_type}' token instead.")
                
                # Update the access token store but current state overrides refresh token state
                # Safer merge - don't let refresh token's exp/iat/type bleed into access token payload
                REFRESH_ONLY_FIELDS = {"type", "exp", "iat", "jti"}
                
                safe_refresh_data = {k: v for k, v in refresh_payload.items() if k not in REFRESH_ONLY_FIELDS}
                new_payload = {**safe_refresh_data, **store}
                
                # Update the store with new payload.
                store.update(new_payload)
                
            except (JWTInvalid, JWTExpired):
                # Stop setting new tokens - only stop if current store is unmodified.
                if not store.needs_update():
                    return
            
        # Re-set the store expiry.
        store.reset_expiry()
        
        # Now obtain access and refresh tokens
        tokens = store.encode_all()
        transport = cls.resolve_transport()
        
        # Write both refresh and access tokens.
        for (token_type, token) in tokens.items():
            if transport == TRANSPORT_COOKIE:
                cls.write_cookie(response, request, token, token_type)
    
            elif transport == TRANSPORT_HEADER:
                if token_type == "access":
                    header_name = SETTINGS.get("JWT_HEADER_NAME", "X-JWT-Token")
                
                elif token_type == "refresh":
                    header_name = SETTINGS.get("JWT_REFRESH_HEADER_NAME", "X-Refresh-JWT-Token")
                
                else:
                    raise ValueError(f"Token type must be either 'access' or 'refresh' not '{token_type}'")
                    
                # Set header.
                response.set_header(header_name, token)
                
        # Reset modification flag
        store.mark_updated()

    @classmethod
    def write_cookie(cls, response: HttpResponse, request: HttpRequest, token: str, token_type: str = "access"):
        """
        Writes the JWT as a ``Set-Cookie`` header on the HTTP response.

        Args:
            response: The Duck HTTP response object.
            request: The HTTP request to get `JWTStore` from.
            token (str): The encoded JWT string.
            token_type (str): The type of token, whether `access` or `refresh`.
        """
        store = request.JWT
        
        if token_type not in ("access", "refresh"):
            raise ValueError(f"Token type must be either 'access' or 'refresh' not '{token_type}'")
            
        httponly = SETTINGS.get("JWT_COOKIE_HTTPONLY", True)
        secure = SETTINGS.get("JWT_COOKIE_SECURE", False)
        samesite = SETTINGS.get("JWT_COOKIE_SAMESITE", "Lax")
        domain = SETTINGS.get("JWT_COOKIE_DOMAIN") or Meta.get_metadata("DUCK_SERVER_DOMAIN")
        
        if token_type == "access":
            cookie_name = SETTINGS.get("JWT_COOKIE_NAME", "jwt")
            max_age = store.expiry_secs or get_access_lifetime()
        else:
            cookie_name = SETTINGS.get("JWT_REFRESH_COOKIE_NAME", "jwt-refresh")
            max_age = get_refresh_lifetime()
            
        response.set_cookie(
            cookie_name,
            value=token,
            max_age=max_age,
            domain=domain,
            path="/",
            httponly=httponly,
            secure=secure,
            samesite=samesite,
        )
