"""
View handlers for the dashboard blueprint.

Checks JWT authentication on every dashboard request.
Unauthenticated requests are served the LoginPage so auth is
handled in a single WebSocket-driven flow with no redirects.
"""

from duck.http.request import HttpRequest
from duck.contrib.auth import get_user_id, async_logout
from duck.contrib.jwt import JWTExpired, JWTInvalid
from duck.shortcuts import resolve, redirect

from .ui.pages.dashboard import DashboardPage
from .ui.pages.login import LoginPage, DASHBOARD_USER_ID


async def dashboard(request: HttpRequest):
    """
    Renders the live server dashboard if the request carries a valid JWT.

    Calls async_get_user_from_jwt to extract and verify the token from
    the request (cookie or Authorization header). Unauthenticated requests
    receive the LoginPage; authenticated requests receive the DashboardPage.

    Args:
        request: The incoming HTTP request.

    Returns:
        A rendered DashboardPage or LoginPage component.
    """
    try:
        user_id = get_user_id(request, backend="jwt")
    except (JWTInvalid, JWTExpired):
        user_id = None
        request.JWT.reset()
        
    if str(user_id) == str(DASHBOARD_USER_ID):
        return DashboardPage(request=request)
    
    return LoginPage(request=request)


async def logout(request: HttpRequest):
    """
    Clears the JWT session and redirects to the dashboard login screen.

    Args:
        request: The incoming HTTP request.

    Returns:
        An HttpResponse redirect to the dashboard index (which will show
        LoginPage since the JWT has been cleared).
    """
    # Logout user
    try:
        await async_logout(request, backend="jwt")
    except (JWTInvalid, JWTExpired):
        request.JWT.reset()
        pass
        
    # Redirect user to dashboard URL
    dashboard_url = resolve("dashboard.index")
    return redirect(dashboard_url)
