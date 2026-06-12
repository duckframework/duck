"""
View handlers for the welcome blueprint.
"""

from duck.http.request import HttpRequest

from .ui.pages.welcome import WelcomePage


async def welcome(request: HttpRequest) -> WelcomePage:
    """
    Renders the welcome/onboarding page shown after installation.

    Args:
        request: The incoming HTTP request.

    Returns:
        A rendered WelcomePage component.
    """
    return WelcomePage(request=request)
