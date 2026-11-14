"""
**Duck Sight Reloader**

Watches project files and calls a callback after a burst of relevant changes.
It knows nothing about the supervisor or the app. Plug it in by passing any
callable, such as `supervisor.restart`.
"""

import fnmatch
import platform
import threading

from pathlib import Path
from typing import Callable

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

from duck.logging import logger
from duck.settings import SETTINGS


class DuckSightReloader(FileSystemEventHandler):
    """
    Calls `on_change` once after a burst of relevant file changes.

    Attributes:
        on_change (Callable[[], None]): Called after the quiet period.
        watch_dir (Path): Directory watched recursively.
        patterns (list[str]): Glob patterns for files that trigger a reload.
        observer (Observer): Filesystem observer thread.
        pending (set[str]): Changed paths waiting for the next callback.
        timer (threading.Timer | None): Pending debounce timer.
        lock (threading.Lock): Guards the pending set and the timer.
        stop_event (threading.Event): Set to end the blocking `run` call.
    """

    DEBOUNCE_SECONDS = 0.6
    WINDOWS_MIN_POLL = 2.0
    STOP_CHECK_INTERVAL = 0.1
    HANDLED_EVENTS = frozenset({"created", "modified", "deleted", "moved"})
    IGNORED_PARTS = frozenset({"__pycache__", ".git", ".venv", "venv", "node_modules"})

    def __init__(self, on_change: Callable[[], None], watch_dir: str) -> None:
        """
        Configure the observer without starting it.

        Args:
            on_change (Callable[[], None]): Called after the quiet period.
            watch_dir (str): Directory to watch recursively.
        """
        super().__init__()

        # Windows polling is slower, so keep a higher floor there.
        timeout = SETTINGS.get("AUTO_RELOAD_POLL", 1.0)

        if platform.system().lower() == "windows":
            timeout = max(timeout, self.WINDOWS_MIN_POLL)

        # Set up some attributes
        self.on_change = on_change
        self.watch_dir = Path(watch_dir).resolve()
        self.patterns = list(SETTINGS["AUTO_RELOAD_WATCH_FILES"])
        self.observer = Observer(timeout=timeout)
        self.pending: set[str] = set()
        self.timer: threading.Timer | None = None
        self.lock = threading.Lock()
        self.stop_event = threading.Event()

    def matches(self, path: str) -> bool:
        """
        Check whether a path should trigger a reload.

        Args:
            path (str): Path reported by the observer.

        Returns:
            bool: True if the path matches a pattern and is not in an ignored folder.
        """
        if self.IGNORED_PARTS & set(Path(path).parts):
            return False
        return any(fnmatch.fnmatch(path, pattern) for pattern in self.patterns)

    def on_any_event(self, event: FileSystemEvent) -> None:
        """
        Record relevant file events and schedule a debounced callback.

        Args:
            event (FileSystemEvent): Event reported by the observer.

        Returns:
            None
        """
        if event.is_directory or event.event_type not in self.HANDLED_EVENTS:
            return

        # A move affects both the old and the new path.
        paths = [event.src_path]

        if event.event_type == "moved":
            paths.append(event.dest_path)
        
        # Only keep the paths that match our patterns.
        matched = {str(path) for path in paths if self.matches(str(path))}

        if not matched:
            return

        # Reset the timer so a burst of saves produces one callback.
        with self.lock:
            self.pending |= matched

            if self.timer:
                self.timer.cancel()

            # Create a new timer to call `fire` after the debounce period.
            self.timer = threading.Timer(self.DEBOUNCE_SECONDS, self.fire)
            self.timer.daemon = True

            # Start the timer.
            self.timer.start()

    def describe(self, paths: set[str]) -> str:
        """
        Build a short summary of the changed files.

        Args:
            paths (set[str]): Changed file paths.

        Returns:
            str: First changed file relative to the watch directory, plus a count of the rest.
        """
        first = sorted(paths)[0]

        try:
            first = str(Path(first).resolve().relative_to(self.watch_dir))
        except ValueError:
            pass

        # Count how many more files changed.
        extra = len(paths) - 1

        # Return a string like "foo.py (+3 more)" or just "foo.py" if there are no extras.
        return f"{first} (+{extra} more)" if extra else first

    def fire(self) -> None:
        """
        Run the callback for the collected changes.

        Returns:
            None
        """
        with self.lock:
            paths, self.pending = self.pending, set()
            self.timer = None

        if not paths:
            return

        # Log the change and call the callback.
        logger.log_raw(
            f"\nFile {self.describe(paths)} changed, reloading...",
            custom_color=logger.Fore.YELLOW,
        )

        try:
            self.on_change()

        except Exception as error:
            logger.log_exception(error)

    def start(self) -> None:
        """
        Begin watching without blocking.

        Returns:
            None
        """
        self.observer.schedule(self, str(self.watch_dir), recursive=True)
        self.observer.start()

    def stop(self) -> None:
        """
        Cancel any pending callback and stop watching.

        Returns:
            None
        """
        self.stop_event.set()

        with self.lock:
            if self.timer:
                self.timer.cancel()
                self.timer = None

            # Clear the pending set
            self.pending.clear()

        # Stop the observer thread
        self.observer.stop()
        
        if self.observer.is_alive():
            # Wait for the observer thread to finish
            self.observer.join()

    def run(self) -> None:
        """
        Watch for changes and block until stopped.

        Notes:
            This method is blocking. Call `stop` from another thread to end it.

        Returns:
            None
        """
        self.start()

        try:
            while not self.stop_event.wait(self.STOP_CHECK_INTERVAL):
                pass

        except KeyboardInterrupt:
            pass

        finally:
            self.stop()
