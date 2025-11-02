"""
**Ducksight Reloader**

Watches for file changes in Duck framework projects and restarts the
webserver in DEBUG mode whenever relevant `.py` files change.

"""
import os
import sys
import time
import fnmatch
import threading
import platform
import subprocess

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from duck.settings import SETTINGS
from duck.logging import logger


class DuckSightReloader:
    """
    Monitors the project directory for Python file changes and triggers reloads.
    """
    def __init__(self, watch_dir: str):
        # Set a dynamic timeout
        timeout = SETTINGS.get("AUTO_RELOAD_POLL", 1.0)
        if platform.system().lower() == "windows":
            timeout = max(timeout, 2.0)
        
        # Create some attributes
        self.observer = Observer(timeout=timeout)
        self.watch_dir = watch_dir
        self.__force_stop = False

    def stop(self):
        """
        Stops the reloader.
        """
        self.__force_stop = True
        
    def run(self):
        """
        Start the observer loop; ensures single reloader process is active.
        
        Notes:
            This method is blocking.
        """
        try:
            event_handler = Handler()
            self.observer.schedule(event_handler, self.watch_dir, recursive=True)
            self.observer.start()
            
            while not self.__force_stop:
                time.sleep(.1)
            
        except KeyboardInterrupt:
            pass
        
        finally:
            self.observer.stop()
            if self.observer.is_alive():
                self.observer.join()


class Handler(FileSystemEventHandler):
    """
    Handles filesystem events and triggers debounced full server reloads.
    """
    def __init__(self, debounce_interval=0.6):
        super().__init__()
        self.debounce_interval = debounce_interval
        self.restart_timer = None
        self.latest_event = None
        self.restarting = threading.Lock()
        self.last_restart_time = 0

    def on_any_event(self, event):
        """
        Called on any filesystem event; filters `.py` files and schedules reload.
        """
        watch_files = SETTINGS["AUTO_RELOAD_WATCH_FILES"]
        
        if event.is_directory:
            return
        
        if not any(fnmatch.fnmatch(event.src_path, pat) for pat in watch_files):
            return

        if event.event_type not in {"created", "modified", "deleted", "moved"}:
            # Ignore event.
            return
        
        # Update the latest event    
        self.latest_event = event
        
        if self.restart_timer:
            self.restart_timer.cancel()
        
        # Set & start the timer
        self.restart_timer = threading.Timer(self.debounce_interval, self._trigger_restart)
        self.restart_timer.start()
        
    def restart_webserver(self, changed_file: str):
        """
        Perform the actual server reload.
        
        Args:
            changed_file (str): This is the path to the file which triggered this reload.
        """
        from duck.app import App
        
        mainapp = App.get_main_app()
        mainapp.stop(
            log_to_console=False,
            no_exit=True,
            kill_ducksight_reloader=False,
            close_log_file=True,
        )
        
        def restart_app():
            """
            This restarts the application.
            """
            # Was started from a file
            cmd = [sys.executable, *sys.argv, "--is-reload"]
            subprocess.run(cmd)
            
        try:
            restart_app()
        except Exception as e:
            # Log any encountered exception
            logger.log_exception(e)
                 
    def _trigger_restart(self):
        """
        Trigger the real restart.
        """
        if self.restarting.locked():
            return
        
        # Check for overlapping reloads
        now = time.time()
        if now - self.last_restart_time < 0.5:
            return  # avoid overlapping reloads

        with self.restarting:
            self.last_restart_time = now
            event = self.latest_event
            file_path = event.src_path
            
            # Log something and restart the server.
            logger.log_raw(f"\nFile {file_path} changed, attempting reload...", custom_color=logger.Fore.YELLOW)
            self.restart_webserver(file_path)
