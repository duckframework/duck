"""
Metrics collection middleware and in-memory store for the dashboard blueprint.

Drop MetricsMiddleware into your MIDDLEWARES list and the dashboard will
immediately have real data — no configuration required.

The store is a module-level singleton protected by a threading.Lock so it
is safe across Duck's multi-worker environment. All data lives in memory
and resets on server restart; swap the store backend here if persistence
is needed.

"""

import time
import logging
import platform
import threading

from collections import deque, defaultdict
from datetime import datetime, timezone

from duck.http.middlewares import BaseMiddleware
from duck.http.request import HttpRequest
from duck.http.response import HttpResponse
from duck.utils.ansi import remove_ansi_escape_codes_str
from duck.logging import logger


# Maximum log entries kept in the ring buffer
MAX_LOG_ENTRIES = 200

# Maximum unique route entries tracked
MAX_ROUTE_ENTRIES = 100

# WebSocket upgrade header value
WS_UPGRADE_VALUE = "websocket"


class MetricsStore:
    """
    Thread-safe singleton that accumulates all request metrics.

    All public methods acquire the internal lock and are safe to call
    from any thread. The dashboard service layer reads from this store
    directly via the module-level `store` instance.
    """

    def __init__(self) -> None:
        """
        Initialises all counters, buffers, and the lock.
        """
        self.lock = threading.Lock()

        # Server start time — set once on first middleware load
        self.start_time: float = time.time()

        # Request counters
        self.total_requests: int = 0
        self.success_requests: int = 0
        self.error_requests: int = 0

        # Per-method counters — key: method string, value: int
        self.method_counts: dict[str, int] = defaultdict(int)

        # Per-status-code counters — key: int status code, value: int
        self.status_counts: dict[int, int] = defaultdict(int)

        # Latency history — ring buffer of recent response times in ms
        self.latency_history: deque = deque(maxlen=200)

        # Per-route stats — key: (method, path), value: {hits, total_ms}
        self.route_stats: dict[tuple, dict] = {}

        # Log entries ring buffer
        self.log_entries: deque = deque(maxlen=MAX_LOG_ENTRIES)

        # Requests in the last 60 seconds — timestamps for rate calculation
        self.recent_request_times: deque = deque(maxlen=1000)

    def record_request(
        self,
        method: str,
        path: str,
        status_code: int,
        duration_ms: float,
        is_ws: bool,
    ) -> None:
        """
        Records a completed request into all relevant counters and buffers.

        Args:
            method: HTTP method string, e.g. "GET".
            path: Request path, e.g. "/api/products".
            status_code: HTTP response status code.
            duration_ms: Response time in milliseconds.
            is_ws: True when the request is a WebSocket upgrade.
        """
        with self.lock:
            now = time.time()
            display_method = "WS" if is_ws else method.upper()

            # Increment global totals
            self.total_requests += 1
            self.recent_request_times.append(now)

            # Classify success vs error by status code range
            if status_code < 400:
                self.success_requests += 1
            else:
                self.error_requests += 1

            # Method and status breakdown
            self.method_counts[display_method] += 1
            self.status_counts[status_code] += 1

            # Latency ring buffer
            self.latency_history.append(duration_ms)

            # Per-route accumulation — cap total tracked routes
            route_key = (display_method, path)
            
            if route_key in self.route_stats or len(self.route_stats) < MAX_ROUTE_ENTRIES:
                entry = self.route_stats.setdefault(
                    route_key, {"hits": 0, "total_ms": 0.0}
                )
                entry["hits"] += 1
                entry["total_ms"] += duration_ms

    def append_log(self, level: str, message: str) -> None:
        """
        Appends a log entry to the ring buffer.

        Args:
            level: Log level string — INFO, WARNING, ERROR, or DEBUG.
            message: The log message text.
        """
        with self.lock:
            ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
            self.log_entries.appendleft({
                "level": level,
                "message": message,
                "ts": ts,
                "source": "",
            })

    def get_uptime_str(self) -> str:
        """
        Returns a human-readable uptime string from server start time.

        Returns:
            String in the format "03h 12m 45s".
        """
        elapsed = int(time.time() - self.start_time)
        hours, remainder = divmod(elapsed, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}h {minutes:02d}m {seconds:02d}s"

    def get_requests_per_minute(self) -> int:
        """
        Returns the number of requests received in the last 60 seconds.

        Returns:
            Integer count of recent requests.
        """
        now = time.time()
        cutoff = now - 60
        return sum(1 for t in self.recent_request_times if t >= cutoff)

    def get_latency_percentiles(self) -> dict:
        """
        Returns latency percentile values from the history buffer.

        Returns:
            Dict with keys p50, p90, p95, p99, avg, history.
            All values are integers in milliseconds.
            Returns zeros when no data is available.
        """
        with self.lock:
            history = list(self.latency_history)

        if not history:
            return {"p50": 0, "p90": 0, "p95": 0, "p99": 0, "avg": 0, "history": []}

        sorted_ms = sorted(history)
        count = len(sorted_ms)

        def percentile(p: float) -> int:
            index = int((p / 100) * count)
            return int(sorted_ms[min(index, count - 1)])

        # Return the last 20 data points for the sparkline
        sparkline = [int(v) for v in history[-20:]]

        return {
            "p50": percentile(50),
            "p90": percentile(90),
            "p95": percentile(95),
            "p99": percentile(99),
            "avg": int(sum(sorted_ms) / count),
            "history": sparkline,
        }

    def snapshot(self) -> dict:
        """
        Returns a consistent read of all metrics under a single lock.

        Returns:
            Dict with copies of method_counts, status_counts,
            route_stats, total, success, error request counts,
            requests_per_minute, start_time, and log_entries.
        """
        with self.lock:
            return {
                "total_requests": self.total_requests,
                "success_requests": self.success_requests,
                "error_requests": self.error_requests,
                "method_counts": dict(self.method_counts),
                "status_counts": dict(self.status_counts),
                "route_stats": dict(self.route_stats),
                "log_entries": list(self.log_entries),
                "requests_per_minute": self.get_requests_per_minute(),
                "uptime": self.get_uptime_str(),
                "start_time": datetime.fromtimestamp(
                    self.start_time, tz=timezone.utc
                ).strftime("%Y-%m-%d %H:%M UTC"),
            }



# Module-level singleton — imported by both middleware and services
store = MetricsStore()


class MetricsMiddleware(BaseMiddleware):
    """
    Request/response middleware that records metrics into MetricsStore.

    Captures request start time in process_request, then measures
    elapsed time and records the full request into the store in
    process_response. WebSocket upgrades are detected via the
    Upgrade header and reported as method "WS".

    Register in settings.py:
        MIDDLEWARES = [
            "web.dashboard.middleware.MetricsMiddleware",
        ]
    """
    # Request-scoped start time key stored in META
    START_TIME_KEY = "dashboard.metrics.start_time"
    debug_message = "Metrics Middleware: Request metrics collection error"
    access_times = 0
    
    LOG_LEVEL_MAP = {
        logger.DEBUG: "DEBUG",
        logger.INFO: "INFO",
        logger.WARNING: "WARNING",
        logger.ERROR: "ERROR",
        logger.CRITICAL: "CRITICAL",
    }

    @classmethod
    def record_log(cls, level: int, message: str) -> None:
        """
        Writes a log record into the metrics store ring buffer.
        """
        level = cls.LOG_LEVEL_MAP.get(level, "INFO")
        message = remove_ansi_escape_codes_str(message)
        store.append_log(level=level, message=message)
        
    @classmethod
    def process_request(cls, request: HttpRequest) -> int:
        """
        Stamps the request start time into META for latency measurement.

        Args:
            request: The incoming HTTP request.

        Returns:
            Always request_ok — this middleware never blocks.
        """
        from duck.logging.handler import register_handler
        
        if cls.access_times == 0:
            # First time access.
            register_handler(cls.record_log)
            
        # Increment access times - it's useful
        cls.access_times += 1
        
        # Record start time so process_response can compute duration
        request.META[cls.START_TIME_KEY] = time.perf_counter()
        return cls.request_ok

    @classmethod
    def process_response(
        cls,
        response: HttpResponse,
        request: HttpRequest,
    ) -> None:
        """
        Records the completed request into the metrics store.

        Computes elapsed time from the META start timestamp, detects
        WebSocket upgrades via the Upgrade header, and calls
        store.record_request with all gathered data.

        Args:
            response: The outgoing HTTP response.
            request: The originating HTTP request.
        """
        if not request:
            return
            
        # Compute response duration in milliseconds
        start = request.META.get(cls.START_TIME_KEY)
        duration_ms = (time.perf_counter() - start) * 1000 if start else 0.0

        # Detect WebSocket upgrade — browsers send GET + Upgrade: websocket
        upgrade_header = request.get_header("upgrade", "").lower()
        is_ws = upgrade_header == WS_UPGRADE_VALUE

        # Record into the shared store
        store.record_request(
            method=request.method,
            path=request.path,
            status_code=response.status_code,
            duration_ms=round(duration_ms, 2),
            is_ws=is_ws,
        )
