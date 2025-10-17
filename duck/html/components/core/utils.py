"""
Helper functions for the component system.
"""

from typing import Union, Optional, Any
from duck.html.components import to_component, quote
from duck.html.core.system import LivelyComponentSystem
from duck.html.core.exceptions import ExecutionError, ExecutionTimedOut


def get_websocket_view() -> LivelyComponentSystem:
    """
    Returns the current/latest websocket view for sending data and do magical staff.
    """
    

async def execute_js(
    code: str,
    script_type: str = "text/javascript",
    timeout: Union[int, float] = None,
    wait_for_result: bool = True,
) -> Optional[Any]:
    """
    Executes JavaScript on the client and optionally waits for a result.

    Args:
        code (str): JavaScript code to execute.
        script_type (str): MIME type of the script. Defaults to "text/javascript".
        timeout (Union[int, float], optional): Max time (in seconds) to wait for result.
        wait_for_result (bool): Whether to wait for a return value. Defaults to True.

    Returns:
        Optional[Any]: Result from the client if wait_for_result is True, otherwise None.

    Raises:
        ExecutionError: If execution is cancelled (e.g., WebSocket disconnected).
        ExecutionTimedOut: If no result is received within timeout.
    """
    return await LivelyComponentSystem.execute_js(
        code, script_type, timeout, wait_for_result
    )


async def get_js_result(
    code: str,
    variable: str,
    script_type: str = "text/javascript",
    timeout: Union[int, float, None] = None,
) -> Any:
    """
    Executes JavaScript on the client and retrieves the value of a specific variable.

    Args:
        code (str): JavaScript code to execute.
        variable (str): Name of the variable to retrieve.
        script_type (str): MIME type of the script. Defaults to "text/javascript".
        timeout (Union[int, float], optional): Max time (in seconds) to wait for result.

    Returns:
        Any: Value of the specified variable from the client.

    Raises:
        ExecutionError: If execution is cancelled (e.g., WebSocket disconnected).
        ExecutionTimedOut: If no result is received within timeout.
    """
    return await LivelyComponentSystem.get_js_result(
        code, variable, script_type, timeout
    )

