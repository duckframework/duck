"""
Real-time Duck system monitor with per-process metrics and a visuals history table.

New features:
- Rolling history buffer for key metrics (cpu_total, ram_percent, disk_percent, net_up, net_down)
- Visuals table below process tables with sparklines, min/max/avg/current
- History length is configurable (default 8 samples)
"""
import os
import time
import psutil
import fnmatch
import platform

from typing import (
    Optional,
    List,
    Dict,
    Any,
)

from rich.console import Console, Group
from rich.table import Table
from rich.live import Live
from rich.text import Text
from rich import box
from duck.utils.platform import is_phone

console = Console()


class MonitorCommand:
    """
    Real-time Duck system monitor with per-process metrics and a visuals history table.

    New features:
    - Rolling history buffer for key metrics (cpu_total, ram_percent, disk_percent, net_up, net_down)
    - Visuals table below process tables with sparklines, min/max/avg/current
    - History length is configurable (default 30 samples)
    """

    SPARK_SYMBOLS = "▁▂▃▄▅▆▇█"
    
    @classmethod
    def disk(cls):
        """
        Return root disk usage in GB as a dictionary:
        {'root': str, 'used': float, 'total': float, 'free': float, 'percent': float}
        """
        # Determine root path depending on OS
        system = platform.system().lower()
        
        if "windows" in system:
            root_path = os.environ.get("SystemDrive", "C:\\")
        
        if is_phone():
            root_path = "/storage/emulated/0"
            
            if "ios" in system:
                root_path = "/" 
            
        else:
            root_path = "/"
        
        # Get disk usage
        usage = psutil.disk_usage(root_path)
        
        return {
            "root": root_path,
            "used": usage.used / (1024 ** 3),
            "total": usage.total / (1024 ** 3),
            "free": usage.free / (1024 ** 3),
            "percent": usage.percent
        }
        
    @classmethod
    def render_trend_bar(cls, value: float, max_value: float = 100) -> Text:
        """
        Return a slim unicode trend block with color based on value.
        """
        symbols = "▏▎▍▌▋▊▉█"
        
        try:
            level = min(int((value / max_value) * (len(symbols) - 1)), len(symbols) - 1)
        except Exception:
            level = 0
        
        bar = Text(symbols[level])
        
        if value >= 80:
            bar.stylize("bold red")
        
        elif value >= 70:
            bar.stylize("yellow")
        
        else:
            bar.stylize("green")
        
        return bar

    @classmethod
    def sparkline_from_values(cls, values: List[float], max_value: float = 100, width: Optional[int] = None) -> str:
        """
        Create a compact sparkline string from a list of values.
        """
        if not values:
            return "N/A"
        
        symbols = cls.SPARK_SYMBOLS
        mx = max_value if max_value and max_value > 0 else max(values) or 1.0
        
        # optionally trim/scale to width
        vals = values if (width is None or len(values) <= width) else values[-width:]
        chars = []
        
        for v in vals:
            try:
                idx = int((v / mx) * (len(symbols) - 1))
            except Exception:
                idx = 0
            idx = max(0, min(idx, len(symbols) - 1))
            chars.append(symbols[idx])
        return "".join(chars)

    @classmethod
    def get_duck_processes(cls, name: str, pids: Optional[List[int]] = None, sort_by: str = "cpu"):
        """
        Return filtered Duck processes sorted by CPU or RAM.
        
        Features:
        - Wildcard support: use '*' or '?' in the `name` parameter.
        - Filter by PID list if provided.
        - Sort by 'cpu' or 'ram'.
        
        Example:
        - name='duck*' matches 'duck', 'duck_server', etc.
        - name='*server*' matches any process containing 'server'.
        """
        processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'num_threads']):
            try:
                # Filter by PID if given
                if pids and proc.info['pid'] in pids:
                    if proc not in processes:
                        processes.append(proc)
                        continue

                # Wildcard matching for name
                proc_name = (proc.info.get('name') or "").lower()
                if fnmatch.fnmatch(proc_name, name.lower()):
                    if proc not in processes:
                        processes.append(proc)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        # Sort processes by CPU or RAM
        if sort_by == "cpu":
            processes.sort(key=lambda p: p.info.get('cpu_percent', 0.0), reverse=True)
        else:
            processes.sort(key=lambda p: p.info.get('memory_percent', 0.0), reverse=True)
        return processes

    @classmethod
    def get_system_metrics(cls, prev_disk, prev_net, elapsed):
        """
        Return CPU, RAM, Disk, Network metrics with failsafe handling.
        """
        # CPU
        try:
            cpu_total = psutil.cpu_percent(interval=None)
            cpu_per_core = psutil.cpu_percent(interval=None, percpu=True)
        except Exception:
            cpu_total, cpu_per_core = 0.0, []

        # RAM
        try:
            mem = psutil.virtual_memory()
            ram_percent = mem.percent
            ram_used = mem.used // (1024**2)
            ram_total = mem.total // (1024**2)
        except Exception:
            ram_percent, ram_used, ram_total = 0.0, 0, 1

        # Disk
        try:
            disk = cls.disk()
            if prev_disk:
                disk_io = psutil.disk_io_counters()
                read_speed = (disk_io.read_bytes - prev_disk.read_bytes) / elapsed / (1024**2)
                write_speed = (disk_io.write_bytes - prev_disk.write_bytes) / elapsed / (1024**2)
                prev_disk = disk_io
            else:
                read_speed = write_speed = 0.0
        except Exception:
            disk = {'percent': 0, 'used': 0, 'total': 0}
            read_speed = write_speed = 0.0

        # Network
        try:
            if prev_net:
                net_io = psutil.net_io_counters()
                net_up = (net_io.bytes_sent - prev_net.bytes_sent) / elapsed / (1024**2)
                net_down = (net_io.bytes_recv - prev_net.bytes_recv) / elapsed / (1024**2)
                prev_net = net_io
            else:
                net_up = net_down = 0.0
        except Exception:
            net_up = net_down = "N/A"

        return (cpu_total, cpu_per_core, ram_percent, ram_used, ram_total,
                disk["percent"], disk["used"], disk["total"], read_speed, write_speed,
                net_up, net_down, prev_disk, prev_net)

    @classmethod
    def make_system_table(cls, cpu_per_core, ram_str, disk_str, net_str):
        """
        Return the main system metrics table.
        """
        table = Table(title="🐥 Duck System Monitor", expand=True, box=box.SIMPLE_HEAVY, padding=(0, 1))
        table.add_column("CPU", style="cyan")
        table.add_column("RAM", style="magenta")
        table.add_column("Disk", style="green")
        table.add_column("Network", style="blue")

        cpu_str = "\n".join([f"Core {i}: {v:.1f}% {cls.render_trend_bar(v)}" for i, v in enumerate(cpu_per_core)]) if cpu_per_core else "N/A"
        table.add_row(cpu_str, ram_str, disk_str, net_str)
        return table

    @classmethod
    def make_duck_process_tables(cls, processes):
        """
        Return two tables for Duck processes:
        1. PID, Name, CPU%, RAM%, Threads
        2. Disk Read, Disk Write, Network Sent, Network Received
        """
        if not processes:
            tbl = Table(title="🐥 Duck Processes", expand=True, box=box.SIMPLE_HEAVY, padding=(0, 1))
            tbl.add_column("Status", justify="center")
            tbl.add_row("[red]No Duck processes found[/red]")
            return tbl, None

        table_main = Table(title="🐥 Duck Processes (Top 10)", expand=True, box=box.SIMPLE_HEAVY, padding=(0, 1))
        table_io = Table(title="🐥 Duck Processes I/O", expand=True, box=box.SIMPLE_HEAVY, padding=(0, 1))

        # Main table columns
        table_main.add_column("PID", justify="center", style="cyan")
        table_main.add_column("Name", style="green")
        table_main.add_column("CPU%", justify="center", style="yellow")
        table_main.add_column("MEM%", justify="center", style="magenta")
        table_main.add_column("Threads", justify="center", style="blue")

        # IO table columns
        table_io.add_column("PID", justify="center", style="cyan")
        table_io.add_column("Read (MB)", justify="center", style="green")
        table_io.add_column("Write (MB)", justify="center", style="magenta")
        table_io.add_column("Net ⇑ (MB)", justify="center", style="yellow")
        table_io.add_column("Net ⇓ (MB)", justify="center", style="blue")

        for idx, proc in enumerate(processes[:10]):
            try:
                style = "bold bright_white" if idx < 3 else None
                
                # Main metrics
                table_main.add_row(
                    str(proc.pid),
                    proc.name(),
                    f"{proc.info.get('cpu_percent', proc.cpu_percent()):.1f}%",
                    f"{proc.info.get('memory_percent', proc.memory_percent()):.2f}%",
                    str(proc.info.get('num_threads', proc.num_threads())),
                    style=style
                )
                
                # Per-process IO
                try:
                    io_counters = proc.io_counters()
                    read_mb = f"{io_counters.read_bytes / 1024**2:.2f}"
                    write_mb = f"{io_counters.write_bytes / 1024**2:.2f}"
                except Exception:
                    read_mb = write_mb = "N/A"

                # Optional: per-process network (N/A if not available)
                # Per-process net io counters not available.
                net_sent_str = net_recv_str = "N/A"  # default fallback

                table_io.add_row(
                    str(proc.pid), read_mb, write_mb, net_sent_str, net_recv_str
                )
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        return table_main, table_io

    @classmethod
    def make_history_table(cls, history: List[Dict[str, Any]], cpu_warning: float, ram_warning: float, width: int = 30):
        """
        Build a visuals/history table showing sparklines and summary stats.
        history: list of dict entries with keys 'cpu', 'ram', 'disk', 'net_up', 'net_down'
        """
        tbl = Table(title="📈 Visuals (History)", expand=True, box=box.SIMPLE_HEAVY, padding=(0, 1))
        tbl.add_column("Metric", style="bold")
        tbl.add_column("History", overflow="fold")
        tbl.add_column("Min", justify="center")
        tbl.add_column("Avg", justify="center")
        tbl.add_column("Max", justify="center")
        tbl.add_column("Current", justify="center")

        # helper to extract series
        def series(key: str) -> List[float]:
            return [entry.get(key, 0.0) for entry in history]

        metrics = [
            ("CPU %", "cpu", 100.0, cpu_warning),
            ("RAM %", "ram", 100.0, ram_warning),
            ("Disk %", "disk", 100.0, None),
            ("Net Up mb/s", "net_up", max((h.get("net_up") or 1.0) for h in history) if history else 1.0, None),
            ("Net Down mb/s", "net_down", max((h.get("net_down") or 1.0) for h in history) if history else 1.0, None),
        ]

        for label, key, max_v, warn in metrics:
            vals = series(key)
            if not vals:
                hist = "N/A"
                mn = av = mx = cur = "N/A"
            else:
                hist = cls.sparkline_from_values(vals, max_value=max_v, width=width)
                mn = f"{min(vals):.2f}"
                av = f"{(sum(vals) / len(vals)):.2f}"
                mx = f"{max(vals):.2f}"
                cur = f"{vals[-1]:.2f}"

            # color current if above warning thresholds
            cur_text = Text(cur)
            if warn is not None and vals:
                try:
                    if float(vals[-1]) >= warn:
                        cur_text.stylize("bold red")
                    elif float(vals[-1]) >= warn * 0.85:
                        cur_text.stylize("yellow")
                    else:
                        cur_text.stylize("green")
                except Exception:
                    pass

            tbl.add_row(label + "\n", hist, mn, av, mx, cur_text)

        return tbl

    @classmethod
    def main(
        cls,
        interval: float = 1.0,
        duck_process_name: str = "duck*",
        duck_pids: Optional[List[int]] = None,
        sort_by: str = "cpu",
        cpu_warning: float = 80.0,
        ram_warning: float = 80.0,
        history_length: int = 8,
    ):
        """
        Start a live monitoring loop for system metrics and Duck processes, with
        visualized history of CPU and RAM usage.
    
        This method continuously updates a live console display showing system-wide
        metrics (CPU, RAM, Disk, Network) alongside per-process metrics for Duck
        processes filtered by name or PID. A rolling history table provides a visual
        representation of recent usage trends.
    
        Args:
            interval (float, optional): Refresh interval in seconds. Defaults to 1.0.
            duck_process_name (str, optional): Process name pattern to monitor (supports wildcards). Defaults to "duck*".
            duck_pids (Optional[List[int]], optional): Specific process IDs to monitor. If None, all matching processes are included. Defaults to None.
            sort_by (str, optional): Metric to sort Duck processes by; either 'cpu' or 'ram'. Defaults to "cpu".
            cpu_warning (float, optional): CPU usage threshold (%) to highlight warnings. Defaults to 80.0.
            ram_warning (float, optional): RAM usage threshold (%) to highlight warnings. Defaults to 80.0.
            history_length (int, optional): Number of recent samples to retain for the visuals/history table. Defaults to 8.
    
        Returns:
            None: This method runs indefinitely until interrupted by the user.
        """
        prev_time = time.time()
        
        try:
            prev_disk = psutil.disk_io_counters()
        except Exception:
            prev_disk = None
        try:
            prev_net = psutil.net_io_counters()
        except Exception:
            prev_net = None

        history: List[Dict[str, float]] = []

        with Live(console=console, refresh_per_second=4, screen=True) as live:
            while True:
                now = time.time()
                elapsed = max(0.0001, now - prev_time)
                prev_time = now

                # System metrics
                (cpu_total, cpu_per_core, ram_percent, ram_used, ram_total,
                 disk_percent, disk_used, disk_total, read_speed, write_speed,
                 net_up, net_down, prev_disk, prev_net) = cls.get_system_metrics(prev_disk, prev_net, elapsed)

                # Append to history (rolling buffer)
                history.append({
                    "cpu": cpu_total,
                    "ram": ram_percent,
                    "disk": disk_percent,
                    "net_up": net_up,
                    "net_down": net_down
                })
                
                if len(history) > history_length:
                    history.pop(0)

                # Apply warning coloring
                ram_style = "red" if ram_percent >= ram_warning else "magenta"
                cpu_style = "red" if cpu_total >= cpu_warning else "cyan"
                
                if not disk_used and not disk_total:
                    # Failed to get disk
                    disk_used = disk_total = 'N/A'
                
                ram_str = f"[{ram_style}]{ram_percent:.1f}% ({ram_used} MB / {ram_total} MB)[/{ram_style}]"
                disk_str = f"{disk_percent:.1f}% ({disk_used:.1f} GB / {disk_total:.1f} GB)\nRead: {read_speed:.2f} MB/s \nWrite: {write_speed:.2f} MB/s"
                net_str = f"Up: {net_up:.2f} MB/s \nDown: {net_down:.2f} MB/s"
                
                # System table
                sys_table = cls.make_system_table(cpu_per_core, ram_str, disk_str, net_str)

                # Duck process tables
                processes = cls.get_duck_processes(duck_process_name, duck_pids, sort_by)
                proc_main, proc_io = cls.make_duck_process_tables(processes)

                # Visuals/history table
                hist_table = cls.make_history_table(history, cpu_warning=cpu_warning, ram_warning=ram_warning, width=history_length)

                # Compose everything and update once to avoid flicker
                group = Group(
                    sys_table,
                    Text("\n"),
                    proc_main,
                    Text("\n"),
                    proc_io if proc_io else Text(""),
                    Text("\n"),
                    hist_table
                )

                live.update(group)
                time.sleep(interval)
