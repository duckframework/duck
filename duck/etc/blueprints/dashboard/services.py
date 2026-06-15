"""
Dashboard service — reads real request metrics from MetricsStore.

All functions in this module pull live data collected by MetricsMiddleware.
No simulation — every value reflects actual server activity since startup.

The only external dependency is the module-level `store` singleton from
middleware.py. Swap the import target if you move to a persistent backend.
"""

import platform

from datetime import datetime, timezone

from .middleware import store


# Status codes classified as errors and their human-readable labels
ERROR_STATUS_LABELS = {
    400: "Bad Request",
    401: "Unauthorized",
    403: "Forbidden",
    404: "Not Found",
    405: "Method Not Allowed",
    408: "Request Timeout",
    409: "Conflict",
    422: "Unprocessable",
    429: "Too Many Requests",
    500: "Server Error",
    502: "Bad Gateway",
    503: "Unavailable",
    504: "Gateway Timeout",
}


def get_server_state() -> dict:
    """
    Returns current server health and uptime metadata.

    Reads uptime from the store start time and system info from
    the platform module. Worker count is pulled from the Duck App
    instance when available.

    Returns:
        Dict with keys: status, uptime, uptime_seconds,
        python_version, platform, worker_count, start_time.
    """
    snap = store.snapshot()

    # Attempt to read real worker count from the Duck App
    worker_count = read_worker_count()

    return {
        "status": "running",
        "uptime": snap["uptime"],
        "python_version": platform.python_version(),
        "platform": platform.system(),
        "worker_count": worker_count,
        "start_time": snap["start_time"],
    }


def get_request_stats() -> dict:
    """
    Returns aggregated request counts and success/failure breakdown.

    Returns:
        Dict with keys: total, success, errors, per_minute,
        success_rate (float 0–100).
    """
    snap = store.snapshot()

    total = snap["total_requests"]
    success = snap["success_requests"]
    errors = snap["error_requests"]
    per_minute = snap["requests_per_minute"]
    success_rate = round((success / total) * 100, 1) if total else 0.0

    return {
        "total": total,
        "success": success,
        "errors": errors,
        "per_minute": per_minute,
        "success_rate": success_rate,
    }


def get_latency_stats() -> dict:
    """
    Returns latency percentile metrics computed from the request history.

    Returns:
        Dict with keys: p50, p90, p95, p99, avg, history (list[int]).
        All latency values are in milliseconds.
    """
    return store.get_latency_percentiles()


def get_error_breakdown() -> list[dict]:
    """
    Returns counts for each 4xx/5xx status code seen since startup.

    Only status codes that have been observed at least once are included,
    supplemented with any codes listed in ERROR_STATUS_LABELS that have
    a zero count so the UI always shows a consistent set.

    Returns:
        List of dicts with keys: code (int), label (str), count (int).
        Sorted by status code ascending.
    """
    snap = store.snapshot()
    status_counts = snap["status_counts"]

    # Build the full error list from known labels, merging real counts
    entries = []
    seen_codes = set()

    for code, label in ERROR_STATUS_LABELS.items():
        count = status_counts.get(code, 0)
        entries.append({"code": code, "label": label, "count": count})
        seen_codes.add(code)

    # Include any unexpected error codes the app emitted
    for code, count in status_counts.items():
        if code >= 400 and code not in seen_codes:
            entries.append({"code": code, "label": f"HTTP {code}", "count": count})

    return sorted(entries, key=lambda e: e["code"])


def get_method_breakdown() -> list[dict]:
    """
    Returns request counts broken down by HTTP method.

    Returns:
        List of dicts with keys: method (str), count (int), percent (float).
        Sorted by count descending.
    """
    snap = store.snapshot()
    method_counts = snap["method_counts"]

    total = sum(method_counts.values())
    return [
        {
            "method": method,
            "count": count,
            "percent": round((count / total) * 100, 1) if total else 0.0,
        }
        for method, count in sorted(
            method_counts.items(), key=lambda x: x[1], reverse=True
        )
    ]


def get_top_routes(limit: int = 15) -> list[dict]:
    """
    Returns the most-hit routes with their request count and avg latency.

    Args:
        limit: Maximum number of routes to return.

    Returns:
        List of dicts with keys: path (str), method (str), hits (int),
        avg_ms (int), status (str — "ok" or "slow").
        Sorted by hits descending.
    """
    snap = store.snapshot()
    route_stats = snap["route_stats"]

    results = []
    for (method, path), data in route_stats.items():
        hits = data["hits"]
        avg_ms = int(data["total_ms"] / hits) if hits else 0
        status = "slow" if avg_ms >= 200 else "ok"
        results.append({
            "path": path,
            "method": method,
            "hits": hits,
            "avg_ms": avg_ms,
            "status": status,
        })

    # Return top routes by hit count
    return sorted(results, key=lambda r: r["hits"], reverse=True)[:limit]


def get_recent_logs(limit: int = 40) -> list[dict]:
    """
    Returns recent server log entries captured by DashboardLogHandler.

    Args:
        limit: Maximum number of log entries to return.

    Returns:
        List of dicts with keys: level (str), message (str),
        ts (str), source (str). Most recent entries first.
    """
    snap = store.snapshot()
    return snap["log_entries"][:limit]


def get_full_snapshot() -> dict:
    """
    Returns a complete dashboard snapshot combining all metric sources.

    Calls store.snapshot() once and distributes the data to each
    sub-function to avoid multiple lock acquisitions.

    Returns:
        Dict with keys: server, requests, latency, errors,
        methods, routes, logs.
    """
    return {
        "server": get_server_state(),
        "requests": get_request_stats(),
        "latency": get_latency_stats(),
        "errors": get_error_breakdown(),
        "methods": get_method_breakdown(),
        "routes": get_top_routes(),
        "logs": get_recent_logs(),
    }


def read_worker_count() -> int:
    """
    Attempts to read the configured worker count from the Duck App instance.

    Falls back to 1 if the App or server attribute is not accessible,
    which can happen when the dashboard is called before the server
    is fully initialised.

    Returns:
        Integer worker count, or 1 as a safe fallback.
    """
    try:
        from duck.app import App
        app = App.get_main_app()
        return app.server.workers or 1
    except Exception:
        return 1
