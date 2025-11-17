"""
Logging module for Duck with console color support using colorama module.
"""
import os
import sys
import atexit
import datetime
import threading
import traceback
import warnings

from typing import (
    Callable,
    Optional,
    Union,
)
from colorama import Fore, Style

from duck import processes
from duck.settings import SETTINGS
from duck.utils.path import paths_are_same, joinpaths
from duck.ansi import remove_ansi_escape_codes
from duck.env import is_testing_environment


# Logging Levels
INFO = 0x0
DEBUG = 0x1
SUCCESS = 0x2
WARNING = 0x3
CRITICAL = 0x4
ERROR = 0x5

# Logging configuration
SILENT = SETTINGS["SILENT"]
LOG_TO_FILE = SETTINGS["LOG_TO_FILE"]
LOG_FILE_FORMAT = SETTINGS["LOG_FILE_FORMAT"]
LOGGING_DIR = SETTINGS["LOGGING_DIR"]
VERBOSE_LOGGING = SETTINGS["VERBOSE_LOGGING"]


def log_raw(
    msg: str,
    level: int = INFO,
    use_colors: bool = True,
    custom_color: str = None,
    end: str = "\n",
):
    """
    Logs a message to console as it is without any modifications.

    Args:
        msg (str): The message to log.
        level (int): The log level of the message.
        use_colors (bool): Whether to log message with some colors, i.e. red for Errors, Yellow for warnings, etc.
        custom_color (string): The custom color to use.
        The use colors argument is required to use custom color.
        end (str): The log suffix, defaults to `"\n"` for newline.
    """
    std = sys.stdout
    color = Fore.WHITE
    
    if SILENT:
        if LOG_TO_FILE:
            cleaned_data = remove_ansi_escape_codes([msg])[0]
            Logger.log_to_file(cleaned_data, end=end)
        return

    if level == ERROR or level == CRITICAL:
        std = sys.stderr
        color = Fore.RED
    
    elif level == WARNING:
        color = Fore.YELLOW
    
    elif level == INFO:
        color = Fore.WHITE
    
    elif level == DEBUG:
        color = Fore.CYAN
    
    elif level == SUCCESS:
        color = Fore.GREEN 
    
    if custom_color:
        color = custom_color

    if use_colors:
        colored_msg = f"{color}{msg}{Style.RESET_ALL}"
        with Logger.print_lock:
            print(colored_msg, file=std, end=end)
    else:
        with Logger.print_lock:
            print(msg, file=std, end=end)


def log(
    msg: str,
    prefix: str = "[ * ]",
    level: int = INFO,
    use_colors: bool = True,
    custom_color: str = None,
    end: str = "\n",
):
    """
    Pretty log a message to console.

    Args:
        msg (str): The message to log.
        prefix (str): The prefix to prepend to the message.
        level (int): The log level of the message.
        use_colors (bool): Whether to log message with some colors, ie, red for Errors, Yellow for warnings, etc
        custom_color (string): The custom color to use. Argument `use_colors` is required to use custom color.
        end (str): The log suffix, defaults to `"\n"` for newline.
    """
    std = sys.stdout
    color = Fore.WHITE
    formatted_msg = f"{prefix} {msg}"
    
    if SILENT:
        if LOG_TO_FILE:
            cleaned_data = remove_ansi_escape_codes([msg])[0]
            Logger.log_to_file(cleaned_data, end=end)
        return

    if level == ERROR or level == CRITICAL:
        std = sys.stderr
        color = Fore.RED
    
    elif level == WARNING:
        color = Fore.YELLOW
    
    elif level == INFO:
        color = Fore.WHITE
    
    elif level == DEBUG:
        color = Fore.CYAN
    
    elif level == SUCCESS:
        color = Fore.GREEN
    
    if custom_color:
        color = custom_color

    if use_colors:
        colored_msg = f"{color}{formatted_msg}{Style.RESET_ALL}"
        with Logger.print_lock:
            print(colored_msg, file=std, end=end)
    else:
        with Logger.print_lock:
            print(msg, file=std, end=end)


def should_filter_warning(category, message, module = None, lineno = 0):
    """
    Simulate Python's filtering logic for a warning.
    Returns True if the warning would be filtered (ignored), False otherwise.
    """
    module = module or "__main__"
    for action, msg, cat, mod, ln in warnings.filters:
        # Check if this filter matches the warning
        if ((msg is None or msg in message)
            and (cat is None or issubclass(category, cat))
            and (mod is None or mod in module)
            and (ln == 0 or lineno == ln)):
            # Actions: 'ignore', 'always', 'default', 'error', 'once', 'module'
            return action == 'ignore'
    # If no filter matches, default action is 'default' (show once per location)
    return False


def warn(message: str, category: Warning = UserWarning, use_colors: bool = True, module = None, lineno = 0):
    """
    This logs a warning to the console. You can filter warnings by using `warnings.filterwarnings`.
    """
    if not should_filter_warning(category, message, module, lineno):
        log_raw(f"{category.__name__}: {message}", level=WARNING, use_colors=use_colors)


def expand_exception(e: Exception) -> str:
    """
    Expands an exception to show the traceback and more information.

    Args:
        e (Exception): The exception to expand.

    Returns:
        str: The expanded exception.
    """
    return "".join(
        traceback.format_exception(type(e), value=e, tb=e.__traceback__))


def handle_exception(func: Callable):
    """
    Decorator that executes a function or callable. If an exception occurs, logs the exception to console and file or both.

    Args:
        func (Callable): The function to be decorated.

    Returns:
        callable: The wrapped function with exception handling.
    """
    def wrapper(*args, **kwargs):
        """
        Wrapper function for the callable provided to the decorator.

        Args:
            *args: Variable length argument list for the callable.
            **kwargs: Arbitrary keyword arguments for the callable.

        Returns:
            Any: The return value of the callable, if no exception occurs.
        """
        try:
            return func(*args, **kwargs)
        except Exception as e:
            log_exception(e)
    return wrapper


def log_exception(e: Exception):
    """
    Logs exception to console and file or both.
    """
    exception = f"Exception: {str(e)}"
    
    if VERBOSE_LOGGING or SETTINGS['DEBUG']:
        exception = expand_exception(e)
    
    if not SILENT:
        log_raw(exception)
        
    if SILENT and LOG_TO_FILE:
        # Write the expanded exception to a file.
        # Explicitly log to file if console output not being redirected.
        Logger.log_to_file(exception)


class Logger:
    """
    Logging class.
    """
    
    print_lock = threading.Lock() 
    """
    Lock used by `log` & `log_raw` functions.
    """
    
    __current_logfile_fd = None
    """
    The file descriptor for the current logfile.
    """
    
    @classmethod
    def get_current_logfile(cls, raise_if_logging_dir_not_found: bool = True) -> str:
        """
        Returns the current log file.
        
        Args:
            raise_if_logging_dir_not_found (bool): Whether to raise an exception if logging directory is not found.
            
        Returns:
            str: The path to the current log file.
    
        Raises:
            FileNotFoundError: If the log directory does not exist.
        """
        logfile_format = LOG_FILE_FORMAT
        current_logfile = os.getenv("DUCK_CURRENT_LOG_FILE")
        
        if "--reload" in sys.argv:
            # This is a reload so lets use previous latest log file because its a continuation
            try:
                return processes.get_process_data("main").get("log_file")
            except KeyError:
                # Failed to retrieve last log file used by the main app.
                pass
        
        if not os.path.isdir(LOGGING_DIR) and raise_if_logging_dir_not_found:
            raise FileNotFoundError("Directory to save log files doesn't exist.")
    
        if current_logfile:
            # Returns the logfile saved in os.environ
            return current_logfile
    
        # Format the new logfile name with the given LOG_FILE_FORMAT
        now = datetime.datetime.now()
        
        # Create log name
        logname = logfile_format.format(
            day=now.day,
            month=now.month,
            year=now.year,
            hours=now.hour,
            minutes=now.minute,
            seconds=now.second,
        )
        
        # Generate new logfile
        new_logfile = joinpaths(LOGGING_DIR, logname + ".log")
        
        # Save logfile to os.environ
        os.environ["DUCK_CURRENT_LOG_FILE"] = new_logfile
        
        # Finally return new logfile.
        return new_logfile
    
    @classmethod
    def get_current_logfile_fd(cls):
        """
        Get the opened file descriptor for the current log file in bytes append mode.
        """
        # Refetches the current log file, maybe it has changed.
        filepath = cls.get_current_logfile()
        
        if cls.__current_logfile_fd is not None:
            if paths_are_same(cls.__current_logfile_fd.name, filepath):
                # Reuse the FD, files are the same.
                fd = cls.__current_logfile_fd
                
                if not fd.closed:
                    # Only return the fd if not closed else,
                    # reopen file and return new opened fd.
                    return fd
                
        # Open filepath and return FD
        cls.__current_logfile_fd = open(filepath, "ab")
        return cls.__current_logfile_fd
        
    @classmethod
    def redirect_console_output(cls):
        """
        Redirects all console output (stdout and stderr) to a log file, i.e current log file.
    
        This function locks sys.stdout and sys.stderr so that they cannot be modified by another process.
        """
        if not LOG_TO_FILE or SILENT:
            # Do not log to any file if logging is disabled in settings.
            return
    
        # Redirect stdout and stderr to a file
        file_fd = cls.get_current_logfile_fd()
        
        # Record default write methods
        cls._original_stdout_write = default_stdout_write = sys.stdout.write
        cls._original_stderr_write = default_stderr_write = sys.stderr.write
        
        # Create a lock for synchronized writing
        write_lock = threading.Lock()
    
        def stdout_write(data):
            """
            Writes data to both the default stdout and the specified file.
    
            Args:
                data (str): The data to be written.
            """
            cleaned_data = remove_ansi_escape_codes([data])[0]  # remove ansi escape codes if present
            
            with write_lock:
                file_fd.write(bytes(cleaned_data, "utf-8"))
                file_fd.flush()  # Ensure data is written to the file immediately
                default_stdout_write(data)
    
        def stderr_write(data):
            """
            Writes data to both the default stderr and the specified file.
    
            Args:
                data (str): The data to be written.
            """
            cleaned_data = remove_ansi_escape_codes([data])[0]  # remove ansi escape codes if present
            
            with write_lock:
                file_fd.write(bytes(cleaned_data, "utf-8"))
                file_fd.flush()  # Ensure data is written to the file immediately
                default_stderr_write(data)
    
        # Assign new write methods
        sys.stdout.write = stdout_write
        sys.stderr.write = stderr_write
    
    @classmethod
    def undo_console_output_redirect(cls):
        """
        Undo redirecting of console output.
        """
        original_stdout_write = getattr(cls, "_original_stdout_write", None)
        original_stderr_write = getattr(cls, "_original_stderr_write", None)
        if all([original_stdout_write, original_stderr_write]):
            sys.stdout.write = original_stdout_write
            sys.stderr.write = original_stderr_write
            
    @classmethod
    def get_latest_logfile(cls) -> Optional[str]:
        """
        Returns the latest created file in `LOGGING_DIR`.
        """
        if os.path.isdir(LOGGING_DIR):
            scan = {i.stat().st_ctime: i for i in os.scandir(LOGGING_DIR)}
            return "%s"%scan.get(sorted(scan)[-1]).path if scan else None
            
    @classmethod
    def log_to_file(cls, data: Union[str, bytes], end: Union[str, bytes] = "\n") -> str | bytes:
        """
        This writes data to the log file.
    
        Args:
            data (Union[str, bytes]): Data to write.
            end (Union[str, bytes]): The suffix to add to data before writting to file.
            
        Returns:
             bytes: Data that was written (in bytes).
        
        Raises:
            DisallowedAction: If SILENT=False or LOG_TO_FILE=False in settings.
        """
        if not SILENT:
             raise DisallowedAction(
                 "SILENT is not True in settings. No need for using this method as all console output"
                 " is redirected to file by default."
             )
             
        if not LOG_TO_FILE:
             raise DisallowedAction(
                 "LOG_TO_FILE is not True in settings. This is required to allow file logging."
             )
             
        logfile_fd = cls.get_current_logfile_fd()
        
        data = b"".join([
            data.encode("utf-8") if isinstance(data, str) else data,
            end.encode("utf-8") if isinstance(end, str) else end
        ])
        
        # Write to logfile and return data written
        with logfile_fd:
            logfile_fd.write(data)
            logfile_fd.flush()
        
        # Finally, return data written
        return data

    @classmethod
    def close_logfile(cls):
        """
        Closes the current logfile if opened.
        """
        logfile_fd = cls.__current_logfile_fd
        if logfile_fd is not None:
            logfile_fd.close()
            cls.undo_console_output_redirect()
            

if not os.path.isdir(LOGGING_DIR):
    # If not in testing environment.
    if not is_testing_environment():
        os.makedirs(LOGGING_DIR, exist_ok=True)


# Register some callback at exit (just in case the file is not yet closed)
atexit.register(Logger.close_logfile)
