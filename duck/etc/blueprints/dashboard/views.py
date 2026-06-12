"""
View handlers for the dashboard blueprint.
"""

from duck.http.request import HttpRequest
from duck.contrib.auth import async_get_user_from_jwt

from .ui.pages.dashboard import DashboardPage


async def dashboard(request: HttpRequest) -> DashboardPage:
    """
    Renders the live server dashboard page.

    Args:
        request: The incoming HTTP request.

    Returns:
        A rendered DashboardPage component.
    """
    user = await async_get_user_from_jwt(request)
    if user or 1:
        return DashboardPage(request=request)
    return DashboardLoginPage(request=request)
