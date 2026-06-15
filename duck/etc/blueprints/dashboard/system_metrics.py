"""
System metrics service for the Duck Framework dashboard.

Reads live OS-level metrics using the standard library (psutil where
available, fallback to /proc on Linux). Each metric getter is wrapped
in a try/except so the panel always renders — failures return an error
dict that the UI displays as a graceful error placeholder.

No external dependencies are required; psutil is used opportunistically
if installed for richer cross-platform data.
"""

import os
import time
import threading


# ── psutil probe ────────────────────────────────────────────────────────────
# Try to import psutil once. If absent, fall back to /proc-based reads.

try:
    import psutil as _psutil
    _HAS_PSUTIL = True
except ImportError:
    _psutil = None
    _HAS_PSUTIL = False


def _err(label: str, exc: Exception) -> dict:
    """
    Returns a standardised error dict for unavailable metrics.

    Args:
        label: Human-readable name of the metric that failed.
        exc: The exception that was raised.

    Returns:
        Dict with keys: available (False), label, error.
    """
    return {"available": False, "label": label, "error": str(exc)}


# ── CPU ─────────────────────────────────────────────────────────────────────

def get_cpu_metrics() -> dict:
    """
    Returns current CPU utilisation and core count.

    Uses psutil.cpu_percent(interval=None) for a non-blocking read of
    the most recent CPU sample. Falls back to /proc/stat on Linux if
    psutil is unavailable.

    Returns:
        Dict with keys: available (True), percent (float 0–100),
        cores_logical (int), cores_physical (int | None), freq_mhz (float | None).
        On failure: available (False), label, error.
    """
    try:
        if _HAS_PSUTIL:
            percent = _psutil.cpu_percent(interval=None)
            cores_logical = _psutil.cpu_count(logical=True)
            cores_physical = _psutil.cpu_count(logical=False)
            freq = _psutil.cpu_freq()
            freq_mhz = round(freq.current, 1) if freq else None
            return {
                "available": True,
                "percent": percent,
                "cores_logical": cores_logical,
                "cores_physical": cores_physical,
                "freq_mhz": freq_mhz,
            }

        # Linux /proc/stat fallback — compute delta over 0.1s
        def _read_stat():
            with open("/proc/stat", "r") as f:
                line = f.readline()
            parts = list(map(int, line.split()[1:]))
            idle = parts[3] + parts[4]  # idle + iowait
            total = sum(parts)
            return idle, total

        idle1, total1 = _read_stat()
        time.sleep(0.1)
        idle2, total2 = _read_stat()
        diff_total = total2 - total1
        diff_idle = idle2 - idle1
        percent = round((1 - diff_idle / diff_total) * 100, 1) if diff_total else 0.0

        import multiprocessing
        cores_logical = multiprocessing.cpu_count()
        return {
            "available": True,
            "percent": percent,
            "cores_logical": cores_logical,
            "cores_physical": None,
            "freq_mhz": None,
        }
    except Exception as exc:
        return _err("CPU", exc)


# ── Memory ──────────────────────────────────────────────────────────────────

def get_memory_metrics() -> dict:
    """
    Returns virtual memory usage statistics.

    Returns:
        Dict with keys: available (True), total_mb (int), used_mb (int),
        free_mb (int), percent (float).
        On failure: available (False), label, error.
    """
    try:
        if _HAS_PSUTIL:
            mem = _psutil.virtual_memory()
            return {
                "available": True,
                "total_mb": mem.total // (1024 * 1024),
                "used_mb": mem.used // (1024 * 1024),
                "free_mb": mem.available // (1024 * 1024),
                "percent": mem.percent,
            }

        # Linux /proc/meminfo fallback
        info = {}
        with open("/proc/meminfo", "r") as f:
            for line in f:
                parts = line.split()
                if len(parts) >= 2:
                    info[parts[0].rstrip(":")] = int(parts[1])

        total_kb = info.get("MemTotal", 0)
        free_kb = info.get("MemAvailable", info.get("MemFree", 0))
        used_kb = total_kb - free_kb
        percent = round((used_kb / total_kb) * 100, 1) if total_kb else 0.0

        return {
            "available": True,
            "total_mb": total_kb // 1024,
            "used_mb": used_kb // 1024,
            "free_mb": free_kb // 1024,
            "percent": percent,
        }
    except Exception as exc:
        return _err("Memory", exc)


# ── Concurrency ─────────────────────────────────────────────────────────────

def get_concurrency_metrics() -> dict:
    """
    Returns active thread count and process information for the current process.

    Returns:
        Dict with keys: available (True), thread_count (int),
        process_id (int), process_name (str | None).
        On failure: available (False), label, error.
    """
    try:
        thread_count = threading.active_count()
        pid = os.getpid()
        process_name = None

        if _HAS_PSUTIL:
            proc = _psutil.Process(pid)
            process_name = proc.name()

        return {
            "available": True,
            "thread_count": thread_count,
            "process_id": pid,
            "process_name": process_name,
        }
    except Exception as exc:
        return _err("Concurrency", exc)


# ── Open files ───────────────────────────────────────────────────────────────

def get_open_files_metrics() -> dict:
    """
    Returns the number of open file descriptors for the current process.

    Returns:
        Dict with keys: available (True), open_files (int),
        soft_limit (int | None), hard_limit (int | None).
        On failure: available (False), label, error.
    """
    try:
        pid = os.getpid()

        if _HAS_PSUTIL:
            proc = _psutil.Process(pid)
            open_count = proc.num_fds() if hasattr(proc, "num_fds") else len(proc.open_files())
        else:
            # Linux: count entries in /proc/self/fd
            fd_dir = f"/proc/{pid}/fd"
            open_count = len(os.listdir(fd_dir))

        # Read ulimit
        soft, hard = None, None
        try:
            import resource
            limits = resource.getrlimit(resource.RLIMIT_NOFILE)
            soft, hard = limits[0], limits[1]
        except Exception:
            pass

        return {
            "available": True,
            "open_files": open_count,
            "soft_limit": soft,
            "hard_limit": hard,
        }
    except Exception as exc:
        return _err("Open Files", exc)


# ── Network ──────────────────────────────────────────────────────────────────

def get_network_metrics() -> dict:
    """
    Returns cumulative network I/O byte counts for the current process.

    Returns:
        Dict with keys: available (True), bytes_sent_mb (float),
        bytes_recv_mb (float), packets_sent (int), packets_recv (int).
        On failure: available (False), label, error.
    """
    try:
        if _HAS_PSUTIL:
            net = _psutil.net_io_counters()
            return {
                "available": True,
                "bytes_sent_mb": round(net.bytes_sent / (1024 * 1024), 2),
                "bytes_recv_mb": round(net.bytes_recv / (1024 * 1024), 2),
                "packets_sent": net.packets_sent,
                "packets_recv": net.packets_recv,
            }

        # Linux /proc/net/dev fallback — sum all non-loopback interfaces
        sent_bytes = recv_bytes = sent_pkts = recv_pkts = 0
        with open("/proc/net/dev", "r") as f:
            lines = f.readlines()[2:]  # skip header rows
        for line in lines:
            parts = line.split()
            if not parts or parts[0].startswith("lo"):
                continue
            # Fields: iface | recv_bytes pkts … | sent_bytes pkts …
            recv_bytes += int(parts[1])
            recv_pkts += int(parts[2])
            sent_bytes += int(parts[9])
            sent_pkts += int(parts[10])

        return {
            "available": True,
            "bytes_sent_mb": round(sent_bytes / (1024 * 1024), 2),
            "bytes_recv_mb": round(recv_bytes / (1024 * 1024), 2),
            "packets_sent": sent_pkts,
            "packets_recv": recv_pkts,
        }
    except Exception as exc:
        return _err("Network I/O", exc)


# ── Disk / Storage ───────────────────────────────────────────────────────────
def get_storage_metrics() -> dict:
    """
    Returns disk usage for the largest available real filesystem,
    avoiding small container overlay / tmpfs mounts.
    """
    try:
        # Candidate mount points to probe — first real one wins
        candidates = ["/", "/host", "/mnt", "/data", str(os.path.expanduser("~"))]

        best = None

        if _HAS_PSUTIL:
            # Walk all mounted partitions, pick the largest total that
            # isn't a virtual/memory filesystem
            skip_fstypes = {"tmpfs", "devtmpfs", "overlay", "squashfs",
                            "proc", "sysfs", "cgroup", "devpts", "nsfs"}
            for part in _psutil.disk_partitions(all=False):
                if part.fstype in skip_fstypes:
                    continue
                try:
                    u = _psutil.disk_usage(part.mountpoint)
                    if best is None or u.total > best["_total"]:
                        best = {
                            "_total":  u.total,
                            "available": True,
                            "total_gb": round(u.total  / (1024 ** 3), 1),
                            "used_gb":  round(u.used   / (1024 ** 3), 1),
                            "free_gb":  round(u.free   / (1024 ** 3), 1),
                            "percent":  round(u.percent, 1),
                            "mount":    part.mountpoint,
                            "note":     None,
                        }
                except (PermissionError, OSError):
                    continue

        if best is None:
            # Fallback: probe candidate paths with shutil, pick largest
            import shutil
            for path in candidates:
                try:
                    u = shutil.disk_usage(path)
                    if best is None or u.total > best["_total"]:
                        pct = round((1 - u.free / u.total) * 100, 1) if u.total else 0.0
                        best = {
                            "_total":   u.total,
                            "available": True,
                            "total_gb": round(u.total / (1024 ** 3), 1),
                            "used_gb":  round(u.used  / (1024 ** 3), 1),
                            "free_gb":  round(u.free  / (1024 ** 3), 1),
                            "percent":  pct,
                            "mount":    path,
                            "note":     None,
                        }
                except (PermissionError, OSError):
                    continue

        if best is None:
            return _err("Storage", "No readable filesystem found")

        # Flag suspiciously small totals (likely still a container fs)
        if best["total_gb"] < 10.0:
            best["note"] = f"Small fs on {best['mount']} — may be container overlay"

        # Clean up internal key before returning
        best.pop("_total")
        return best

    except Exception as exc:
        return _err("Storage", exc)


# ── Aggregated snapshot ──────────────────────────────────────────────────────

def get_system_metrics() -> dict:
    """
    Returns a combined snapshot of all system metrics.

    Each sub-key contains either a metrics dict (available=True) or
    an error dict (available=False) so callers can render gracefully.

    Returns:
        Dict with keys: cpu, memory, concurrency, open_files, network, storage.
    """
    return {
        "cpu": get_cpu_metrics(),
        "memory": get_memory_metrics(),
        "concurrency": get_concurrency_metrics(),
        "open_files": get_open_files_metrics(),
        "network": get_network_metrics(),
        "storage": get_storage_metrics(),
    }
