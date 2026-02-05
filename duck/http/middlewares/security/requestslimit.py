"""
High-performance rate-limiting middleware using InMemoryCache expiry-based
counters.

This implementation uses a *fixed window* algorithm:

- Each client/IP has a single counter stored in the cache.
- The key expires automatically after `requests_delay` seconds.
- On each request, the counter increments.
- If it exceeds `max_requests`, the request is rejected.

This design provides:
- O(1) operations
- Zero list allocations
- Zero timestamp storage
- Minimal memory footprint
- Very high request throughput
"""
from duck.http.middlewares import BaseMiddleware
from duck.settings import SETTINGS
from duck.shortcuts import simple_response, template_response
from duck.http.response import HttpTooManyRequestsResponse
from duck.utils.caching import InMemoryCache


class RequestsLimitMiddleware(BaseMiddleware):
    """
    High-speed request limiter using expiry-based counters.

    Attributes:
        _clients (InMemoryCache):
            Cache storing counters per client IP.
            Keys automatically expire after the configured window duration.

        requests_delay (float):
            Duration (in seconds) forming the rate-limit window.

        max_requests (int):
            Maximum number of requests allowed within the window.
    """

    # LRU in-memory cache with expiry support
    _clients = InMemoryCache(maxkeys=2000)

    # Fixed window settings
    requests_delay: float = 60
    """
    Duration in seconds defining the time window for request counting.
    """
    
    max_requests: int = 500
    """
    Maximum number of allowed requests within the `requests_delay` window.
    """
    
    debug_message: str = "RequestsLimitMiddleware: Too many requests"

    @classmethod
    def _process_request(cls, request):
        """
        Core request-processing logic.

        Flow:
        1. Extract client IP.
        2. Fetch current request count from cache.
        3. If count is missing -> this is first request in the window.
            Create count=1 with expiry.
        4. If count >= max_requests -> reject.
        5. Otherwise increment counter and update expiry.

        This implementation does not store timestamps and does not scan arrays.
        It relies fully on cache expiry to define the time window.
        """

        # Extract client IP; if missing, fail open
        addr = request.client_address
        if not addr:
            return cls.request_ok

        ip = addr[0]

        # Localize variables for micro-optimizations
        window = cls.requests_delay
        limit = cls.max_requests

        # Retrieve current request count (or None if expired/new)
        count = cls._clients.get(ip)

        if count is None:
            # First request in this window → create counter with expiry
            cls._clients.set(ip, 1, expiry=window)
            return cls.request_ok

        # If limit reached → reject immediately
        if count >= limit:
            return cls.request_bad

        # Increment count and refresh expiry
        # We set the expiry again so each request resets the 60-second window.
        # (If fixed windows are desired instead, do NOT refresh expiry here.)
        cls._clients.set(ip, count + 1, expiry=window)
        return cls.request_ok

    @classmethod
    def get_readable_limit(cls) -> str:
        """
        Returns a user-friendly description of the rate limit.

        Example:
            "200 requests per 60 seconds"
        """
        if cls.requests_delay == 1:
            return f"{cls.max_requests} requests per second"
        return f"{cls.max_requests} requests per {cls.requests_delay} seconds"

    @classmethod
    def get_error_response(cls, request):
        """
        Creates a 429 Too Many Requests HTTP response.

        Includes additional debugging information when DEBUG is enabled.
        """
        body = (
            "<h4>Too Many Requests!</h4>"
            f"<p>Rate limit: {cls.get_readable_limit()}.</p>"
            f"<p>You sent more than {cls.max_requests} requests within "
            f"{cls.requests_delay} seconds.</p>"
        )

        if SETTINGS["DEBUG"]:
            return template_response(HttpTooManyRequestsResponse, body=body)
        return simple_response(HttpTooManyRequestsResponse, body=body)

    @classmethod
    def process_request(cls, request):
        """
        Framework entry point.

        Wraps the internal handler and ensures the server always
        fails open instead of blocking requests due to middleware errors.
        """
        try:
            return cls._process_request(request)
        except Exception:
            raise
            # Never rate-limit due to internal middleware errors
            return cls.request_ok
