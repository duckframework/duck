"""
Logging module for websockets.
"""

from typing import Optional, List, Union

from duck.http.request import HttpRequest
from duck.utils.dateutils import (
    django_short_local_date,
    short_local_date,
)
from duck.settings import SETTINGS
from duck.logging import logger


def get_django_formatted_log(
    request: Optional[HttpRequest] = None,
    debug_message: Optional[Union[str, List[str]]] = None,
) -> str:
    """
    Returns a log message formatted similarly to Django logs with color support.
    
    Useful for logging WebSockets messages.
    
    Args:
        request (Optional[HttpRequest]): The HTTP request object. Optional, used for adding more detailed log information.
        debug_message (Optional[Union[str, List[str]]]): A custom debug message or a list of messages to append to the log.

    Returns:
        str: The formatted log message with color code.
    """
    # Initialize variables
    debug_message = debug_message or ""
    reset = logger.Style.RESET_ALL
    color = logger.Fore.CYAN
    
    # Add the main log information
    if isinstance(debug_message, list):
        first_msg = debug_message[0]
        info = ""
        debug_messages = debug_message[1:]
        
        # Add second to last message on top before the first message.
        info += "\n".join(debug_messages)
        
        info += (
            f"[{django_short_local_date()}] {color}" + f"{first_msg}"
        )
        
    else:
        info = (
            f"[{django_short_local_date()}] {color}" + f"{debug_message}"
        )
    return info + reset  # Restore default color


def get_duck_formatted_log(
    request: Optional[HttpRequest] = None,
    debug_message: Optional[Union[str, List[str]]] = None ,
) -> str:
    """
    This returns default duck formatted log with color support.
    
    Useful for logging WebSockets messages.
    
    Args:
        request (Optional[HttpRequest]): The http request object.
        debug_message (Optional[Union[str, List[str]]]): Custom debug message or a list of messages to add to log.
    """
    debug_message = debug_message or ""
    reset = logger.Style.RESET_ALL
    color = logger.Fore.CYAN
    addr = ("unknown", "unknown")
    
    if request and request.client_address:
        addr = request.client_address
    
    if isinstance(debug_message, list):
        # List of messages
        first_msg = debug_message[0]
        
        info = (
            f'[{short_local_date()}] {color}{first_msg}'
        ) 
        
        debug_messages = debug_message[1:]
        
        for msg in debug_messages:
            info += f"\n  {reset}├── {msg} "
            
    else:    
        info = (
            f'[{short_local_date()}] {color}{debug_message}'
        )
    
    info += f"\n  {reset}└── ADDR {list(addr)} "
    
    return info + reset  # Restore default color (default)


def log_message(
    request: Optional[HttpRequest] = None,
    debug_message: Optional[Union[str, List[str]]] = None,
) -> None:
    """
    Logs a WebSocket message to the console.

    Args:
        request (Optional[Request]): The http request object.
        debug_message (Optional[Union[str, List[str]]]): Custom message or list of messages to display.
    """
    logdata = ""
    
    if SETTINGS["USE_DJANGO"]:
        if SETTINGS['PREFERRED_LOG_STYLE'] == "duck":
            logdata = get_duck_formatted_log(request, debug_message)
            # Add newline to separate requests for duck formatted logs
            logdata += "\n"  
        else:
            logdata = get_django_formatted_log(request, debug_message)
    else:
        if SETTINGS['PREFERRED_LOG_STYLE'] == "django":
            logdata = get_django_formatted_log(request, debug_message)
        else:
            logdata = get_duck_formatted_log(request, debug_message)
            # Add newline to separate requests for duck formatted logs
            logdata += "\n"  
    
    # Log response, use_colors=False to because logdata already has colors
    logger.log_raw(logdata, use_colors=False)
