"""
Process supervisor for Duck applications.

Launches the application in its own process group, restarts it after crashes
and replaces it on request. The supervisor never imports or builds the
application, and it knows nothing about what triggers a restart.
"""

import enum
import os
import signal
import time
import subprocess
import threading

from typing import Sequence

from setproctitle import setproctitle
from duck.logging import logger


IS_WINDOWS = os.name == "nt"


def run_supervised_app() -> None:
    """
    Start the supervised app process and the DuckSight reloader, then block.
    """
    setproctitle("duck-supervisor")

    from duck.settings import SETTINGS
    from duck.app.app import App
    from duck.app.utils import get_run_command
    from duck.app.supervisor import Supervisor
    from duck.contrib.reloader.ducksight import DuckSightReloader

    # Keep the kill timeout above the app's own shutdown watchdog.
    supervisor = Supervisor(
        get_run_command(),
        terminate_timeout=App.SHUTDOWN_TIMEOUT + 2.0,
    )

    # Initialize empty reloader
    reloader = None

    if SETTINGS["AUTO_RELOAD"] and SETTINGS["DEBUG"]:
        # Initialize the reloader with a callback that restarts the app process.
        reloader = DuckSightReloader(on_change=supervisor.restart, watch_dir=os.getcwd())

        # Start the reloader first so it can catch changes during the app's startup.
        reloader.start()

    try:
        # The main thread runs the supervisor so it can handle SIGTERM and SIGINT.
        supervisor.run()

    finally:
        if reloader is not None:
            # Stop the reloader so it cannot restart the app after shutdown.
            reloader.stop()


def in_supervised_mode() -> bool:
    """
    Returns True if the current process is running under the supervisor.

    Returns:
        bool: True if the current process is supervised.
    """
    return os.environ.get(Supervisor.CHILD_ENV) == "1"


class State(enum.Enum):
    """
    Lifecycle states of the supervised application.
    """

    STOPPED = "stopped"
    RUNNING = "running"
    BACKOFF = "backoff"
    FAILED = "failed"


class Supervisor:
    """
    Keeps one application process running, restarting it after crashes.

    Attributes:
        cmd (list[str]): Command that launches the application process.
        max_crashes (int | None): Consecutive crashes tolerated, None for unlimited.
        terminate_timeout (float): Seconds to wait for a graceful exit before force-killing.
        state (State): Current lifecycle state.
        child (subprocess.Popen | None): The running application process.
        lock (threading.RLock): Serializes lifecycle changes.
        stop_event (threading.Event): Set once the supervisor is shutting down.
        started_at (float): Monotonic time of the last launch.
        retry_at (float): Monotonic time of the next crash restart.
        crashes (int): Consecutive quick crashes since the last stable run.
    """

    CHILD_ENV = "DUCK_SUPERVISED"
    RESTART_FLAG = "--is-reload"
    DEFAULT_TERMINATE_TIMEOUT = 5.0
    KILL_TIMEOUT = 2.0
    POLL_INTERVAL = 0.5
    BACKOFF_START = 0.5
    BACKOFF_MAX = 10.0
    STABLE_SECONDS = 10.0

    def __init__(
        self,
        cmd: Sequence[str],
        max_crashes: int | None = 5,
        terminate_timeout: float = DEFAULT_TERMINATE_TIMEOUT,
    ) -> None:
        """
        Store how the application process should be launched.

        Args:
            cmd (Sequence[str]): Command that launches the application process.
            max_crashes (int | None): Consecutive crashes tolerated before giving up. None retries forever.
            terminate_timeout (float): Seconds to wait for a graceful exit before force-killing. Keep it above the app's shutdown timeout.
        """
        self.cmd = list(cmd)
        self.max_crashes = max_crashes
        self.terminate_timeout = terminate_timeout
        self.state = State.STOPPED
        self.child: subprocess.Popen | None = None
        self.lock = threading.RLock()
        self.stop_event = threading.Event()
        self.started_at = 0.0
        self.retry_at = 0.0
        self.crashes = 0

    def start(self, restart: bool = False) -> None:
        """
        Launch the application in its own process group.

        Args:
            restart (bool): Whether this launch replaces an earlier process.

        Returns:
            None
        """
        with self.lock:
            if self.stop_event.is_set() or self.state is State.RUNNING:
                return

            # The restart flag tells a reload apart from a first launch.
            cmd = [*self.cmd, self.RESTART_FLAG] if restart else self.cmd
            env = {**os.environ, self.CHILD_ENV: "1"}

            # A separate group lets the supervisor signal only the child.
            group = (
                {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP} # type: ignore
                if IS_WINDOWS
                else {"start_new_session": True}
            )

            # Launch the child process
            self.child = subprocess.Popen(cmd, env=env, **group) # type: ignore

            # Record the launch time and switch to the running state.
            self.started_at = time.monotonic()
            self.state = State.RUNNING

    def stop(self, reload: bool = False) -> None:
        """
        Stop the application, forcing a kill only if it hangs.

        Args:
            reload (bool): Whether this stop is part of a restart, so the app
                skips its exit message.

        Returns:
            None
        """
        with self.lock:
            if self.child is not None and self.child.poll() is None:
                # Signal the child process group and wait for it to exit.
                self.terminate(reload=reload)

                try:
                    # Wait for the child to exit, but don't block forever.
                    self.child.wait(timeout=self.terminate_timeout)

                except subprocess.TimeoutExpired:
                    self.terminate(force=True)
                    self.child.wait(timeout=self.KILL_TIMEOUT)

            # Clear the child reference and switch to the stopped state.
            self.child = None
            self.state = State.STOPPED

    def terminate(self, reload: bool = False, force: bool = False) -> None:
        """
        Signal the application's process group.

        Args:
            reload (bool): Send the quiet reload signal instead of SIGTERM (POSIX only).
            force (bool): Kill instead of asking for a graceful exit.

        Returns:
            None
        """
        if self.child is None:
            return
        
        try:
            if IS_WINDOWS:
                # Windows has one graceful channel, delivered to the app as SIGBREAK.
                if force:
                    self.child.kill()
                else:
                    self.child.send_signal(signal.SIGBREAK) if reload else signal.SIGTERM # type: ignore
            else:
                if force:
                    sig = signal.SIGKILL
                else:
                    sig = signal.SIGUSR1 if reload else signal.SIGTERM

                # Send the signal to the entire process group, not just the child.
                os.killpg(self.child.pid, sig)

        except (ProcessLookupError, OSError):
            pass

    def restart(self) -> None:
        """
        Replace the application process and clear its crash history.

        Safe to call from any thread, and works from every state including FAILED.

        Returns:
            None
        """
        with self.lock:

            if self.stop_event.is_set():
                return

            # Reset the crash counter so a restart doesn't count as a crash.
            self.crashes = 0

            # Stop the current process
            self.stop(reload=True)
            
            # Start a new process
            self.start(restart=True)

    def shutdown(self) -> None:
        """
        Stop the application and prevent any further starts.

        Returns:
            None
        """
        self.stop_event.set()
        self.stop()

    def handle_exit(self, code: int) -> bool:
        """
        Decide what to do after the application exited on its own.

        Args:
            code (int): Exit code; negative means killed by a signal.

        Returns:
            bool: True if the supervisor should shut down as well.
        """
        self.child = None

        # A clean exit means the application chose to quit.
        if code == 0:
            self.state = State.STOPPED
            return True

        # A long, stable run before the crash resets the counter.
        if time.monotonic() - self.started_at >= self.STABLE_SECONDS:
            self.crashes = 0

        # Increment the crash counter
        self.crashes += 1

        if self.max_crashes is not None and self.crashes > self.max_crashes:
            self.state = State.FAILED

            # Log something
            logger.log_raw(
                f"\nApp crashed {self.max_crashes} times in a row, giving up. "
                "Call restart() to try again.",
                level=logger.WARNING
            )

            return False

        # Get the delay for the next restart, with exponential backoff.
        delay = min(self.BACKOFF_START * 2 ** (self.crashes - 1), self.BACKOFF_MAX)

        # Schedule the next restart and switch to the backoff state.
        self.retry_at = time.monotonic() + delay
        self.state = State.BACKOFF

        # Log something
        logger.log_raw(f"\nApp exited with code {code}, restarting in {delay:.1f}s...", level=logger.INFO)

        # Return False to keep the supervisor alive, even if the app is in FAILED state.
        return False

    def check(self) -> bool:
        """
        Advance the state machine once: detect exits and run due restarts.

        Returns:
            bool: True if the supervisor should shut down.
        """
        with self.lock:
            if self.state is State.RUNNING and self.child is not None:
                code = self.child.poll()
                return False if code is None else self.handle_exit(code)

            if self.state is State.BACKOFF and time.monotonic() >= self.retry_at:
                self.start(restart=True)

            return False

    def run(self) -> None:
        """
        Start the application and keep it alive until shutdown is requested.

        Notes:
            Must be called from the main thread because it installs a SIGTERM handler.
            After giving up, it stays alive in the FAILED state until `restart`
            or `shutdown` is called.

        Returns:
            None
        """
        # The handler only sets a flag, so no locks are taken inside it.
        signal.signal(signal.SIGTERM, lambda _, __: self.stop_event.set())

        # Start the first application process
        self.start()

        try:
            while not self.stop_event.wait(self.POLL_INTERVAL):
                if self.check():
                    break
        except KeyboardInterrupt:
            pass

        finally:
            self.shutdown()
