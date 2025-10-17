"""
Module containing the LogsCommand class for Duck project log management.
"""
import os
import click

from pathlib import Path
from typing import List

from duck.logging import console


class LogsCommand:
    """
    CLI command group for managing Duck project logs.
    """
    @classmethod
    def get_logs_dir(cls) -> Path:
        """
        Get the resolved path to the project's logs directory.
        """
        from duck.settings import SETTINGS
        logsdir = SETTINGS['LOGGING_DIR']
        return Path(logsdir).resolve() if not isinstance(logsdir, Path) else logsdir.resolve()

    @classmethod
    def _get_log_files(cls) -> List[Path]:
        """
        Return a list of log file paths in the logs directory.
        """
        logsdir = cls.get_logs_dir()
        
        if not logsdir.exists():
            console.log_raw(f"Log directory not found: {logsdir}", level=console.WARNING)
            return []
        
        return [p for p in logsdir.iterdir() if p.is_file()]

    @staticmethod
    def _sort_logs(logs: List[Path], sort: str) -> List[Path]:
        """
        Sort logs based on criteria.
        """
        if sort == "oldest":
            return sorted(logs, key=lambda f: f.stat().st_mtime)
        
        elif sort == "newest":
            return sorted(logs, key=lambda f: f.stat().st_mtime, reverse=True)
        
        elif sort == "largest":
            return sorted(logs, key=lambda f: f.stat().st_size, reverse=True)
        
        else:
            console.log_raw(f"Unknown sort type '{sort}', defaulting to 'oldest'.", level=console.WARNING)
            return sorted(logs, key=lambda f: f.stat().st_mtime)

    @classmethod
    def list_logs(cls, max: int = -1, sort: str = "oldest", show_size: bool = False):
        """
        List Duck project logs.
        """
        logs = cls._get_log_files()
        maxlogs = max
        
        if not logs:
            console.log_raw("No logs found.", level=console.WARNING)
            return

        logs = cls._sort_logs(logs, sort)
        
        if maxlogs > 0:
            logs = logs[:maxlogs]

        for log in logs:
            size_info = f" ({log.stat().st_size / 1024:.2f} KB)" if show_size else ""
            console.log_raw(f"{log.name}{size_info}", custom_color=console.Fore.GREEN)

    @classmethod
    def purge_logs(cls, max: int = -1, sort: str = "oldest"):
        """
        Delete logs, optionally limited by count and sorted by criteria.
        """
        logs = cls._get_log_files()
        maxlogs = max
        
        if not logs:
            console.log_raw("No logs to delete", level=console.WARNING)
            return

        logs = cls._sort_logs(logs, sort)
        
        if maxlogs > 0:
            logs = logs[:maxlogs]

        for log in logs:
            try:
                log.unlink()
                console.log_raw(f"Deleted {log.name}", level=console.WARNING)
            except OSError as e:
                console.print(f"Failed to delete {log.name}: {e}", level=console.ERROR)

    @classmethod
    def count_logs(cls):
        """
        Count the number of log files.
        """
        logs = cls._get_log_files()
        console.log_raw(f"{len(logs)} log(s) found.", level=console.DEBUG)

    @classmethod
    def get_logs_size(cls, fmt: str = "kb"):
        """
        Get the total size of all logs.
        """
        logs = cls._get_log_files()
        total_size = sum(log.stat().st_size for log in logs)

        unit_map = {"b": 1, "kb": 1024, "mb": 1024**2, "gb": 1024**3}
        fmt = fmt.lower()
        divisor = unit_map.get(fmt, 1024)
        formatted_size = total_size / divisor
        
        # Print to console
        console.log_raw(f"Total logs size: {formatted_size:.2f} {fmt.upper()}", level=console.DEBUG)

    @classmethod
    def register_subcommands(cls, main_command: click.Command):
        """
        Register the log management subcommands.
        """
        data = {
            "list": {
                "callback": cls.list_logs,
                "params": [
                    click.Option(('-n', "--max"), type=int, default=-1, help="Max number of logs."),
                    click.Option(("-s", "--sort"), type=str, default="oldest", help="Sort: oldest, newest, largest."),
                    click.Option(("-ss", "--show-size"), is_flag=True, default=False, help="Show log sizes."),
                ],
                "help": "List project logs."
            },
            "purge": {
                "callback": cls.purge_logs,
                "params": [
                    click.Option(('-n', "--max"), type=int, default=-1, help="Max number of logs."),
                    click.Option(("-s", "--sort"), type=str, default="oldest", help="Sort: oldest, newest, largest."),
                ],
                "help": "Delete project logs."
            },
            "count": {
                "callback": cls.count_logs,
                "params": [],
                "help": "Count the number of logs."
            },
            "size": {
                "callback": cls.get_logs_size,
                "params": [
                    click.Option(('-f', "--fmt"), type=str, default="kb", help="Size unit: b, kb, mb, gb."),
                ],
                "help": "Get the total size of logs."
            },
        }

        for cmd_name, info in data.items():
            cmd = click.Command(cmd_name, callback=info["callback"], params=info["params"], help=info["help"])
            main_command.add_command(cmd)
