"""
Console Logging Module - Log messages to console only!

This module provides utility functions to log messages to the console in a 
customizable format. It supports raw logging (plain messages) and formatted 
logging with prefixes, log levels, and optional colored output.

Features:
- Log messages with predefined log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL.
- Support for colored output using ANSI escape codes.
- Customizable prefixes and colors for better message clarity.
- Automatically directs error-level logs to `stderr` and others to `stdout`.

Dependencies:
- Requires the `colorama` library for colored console output.

Constants:
- CRITICAL (int): Log level for critical messages.
- ERROR (int): Log level for error messages.
- WARNING (int): Log level for warning messages.
- INFO (int): Log level for informational messages.
- DEBUG (int): Log level for debug messages.
- SUCCESS (int): Log level for success message.

Functions:
- log_raw(msg, level, use_colors, custom_color): Logs a plain message.
- log(msg, prefix, level, use_colors, custom_color): Logs a formatted message with a prefix.

Example Usage:

```py
log("This is an info message.", level=INFO)
log("This is a warning!", level=WARNING)
log("This is an error!", level=ERROR)
log_raw("Raw debug message", level=DEBUG, use_colors=True, custom_color=Fore.MAGENTA)
```
"""

import sys
import threading
import warnings

from colorama import Fore, Style


# Whether to silence all logs
SILENT = False
RESPECT_SILENT_CONSOLE_LOGS = False

try:
    # If the below import succeeds, this means we are in a Duck project env.
    from duck.settings import SETTINGS
    
    SILENT = SETTINGS['SILENT']
    RESPECT_SILENT_CONSOLE_LOGS = SETTINGS.get("RESPECT_SILENT_CONSOLE_LOGS", False)
except Exception:
    pass

        
# Logging Levels
INFO = 0x0
DEBUG = 0x1
SUCCESS = 0x2
WARNING = 0x3
CRITICAL = 0x4
ERROR = 0x5

# Global print lock
print_lock = threading.Lock()


def log_raw(
    msg: str,
    level: int = INFO,
    use_colors: bool = True,
    custom_color: str = None,
    end: str = "\n"
):
    """
    Logs a raw message to the console without any modifications or prefixes.
    
    Args:
        msg (str): The message to log.
        level (int): The log level of the message (e.g., DEBUG, INFO, WARNING, ERROR, CRITICAL).
        use_colors (bool): Whether to apply color formatting to the message.
        custom_color (str): A custom ANSI color code for the message.
            Requires `use_colors` to be `True`.
        end (str): The log suffix, defaults to `"\n"` for newline.
    """
    if SILENT and RESPECT_SILENT_CONSOLE_LOGS:
        # Do not log anything in this mode.
        return
        
    std = sys.stderr if level in {ERROR, CRITICAL} else sys.stdout
    color = Fore.WHITE
    
    # Determine color based on log level
    if level == ERROR or level == CRITICAL:
        color = Fore.RED
    
    elif level == WARNING:
        color = Fore.YELLOW
    
    elif level == DEBUG:
        color = Fore.CYAN
    
    elif level == SUCCESS:
        color = Fore.GREEN 
        
    # Apply custom color if provided
    if custom_color:
        color = custom_color

    # Print the message with or without color
    if use_colors:
        with print_lock:
            print(f"{color}{msg}{Style.RESET_ALL}", file=std, end=end)
    else:
        with print_lock:
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
    Logs a formatted message to the console with a prefix and optional colors.
    
    Args:
        msg (str): The message to log.
        prefix (str): A prefix to prepend to the message, e.g., '[ * ]', 'INFO', 'ERROR'.
        level (int): The log level of the message (e.g., DEBUG, INFO, WARNING, ERROR, CRITICAL).
        use_colors (bool): Whether to apply color formatting to the message.
        custom_color (str): A custom ANSI color code for the message.
            Requires `use_colors` to be `True`.
        end (str): The log suffix, defaults to `"\n"` for newline.
    """
    if SILENT and RESPECT_SILENT_CONSOLE_LOGS:
        # Do not log anything in this mode.
        return
        
    formatted_msg = f"{prefix} {msg}"
    std = sys.stderr if level in {ERROR, CRITICAL} else sys.stdout
    color = Fore.WHITE
    
    # Determine color based on log level
    if level == ERROR or level == CRITICAL:
        color = Fore.RED
    
    elif level == WARNING:
        color = Fore.YELLOW
    
    elif level == DEBUG:
        color = Fore.CYAN
    
    elif level == SUCCESS:
        color = Fore.GREEN
        
    # Apply custom color if provided
    if custom_color:
        color = custom_color

    # Print the message with or without color
    if use_colors:
        with print_lock:
            print(f"{color}{formatted_msg}{Style.RESET_ALL}", file=std, end=end)
    else:
        with print_lock:
            print(formatted_msg, file=std, end=end)


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
