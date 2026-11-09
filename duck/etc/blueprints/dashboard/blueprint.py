"""
Blueprint definition for the Duck Framework server dashboard.

Register this in your project settings under BLUEPRINTS to mount
the dashboard at /dashboard.
"""

from duck.routes import Blueprint
from duck.urls import path
from duck.logging import logger
from duck.security.dashboard import get_dashboard_security_issues, InsecureDashboardWarning
from duck.settings import SETTINGS

from . import views


# Log a warning if blueprint has been manually added to blueprints instead of using setting ENABLE_DASHBOARD
issues = get_dashboard_security_issues()

if issues:
    logger.warn(InsecureDashboardWarning, f"Dashboard is not securely configured [{len(issues)} issue(s) found]")

if not SETTINGS["ENABLE_COMPONENT_SYSTEM"]:
    logger.log("Lively Component System is disabled yet the Dashboard requires it", level=logger.WARNING)


Dashboard = Blueprint(
    location=__file__,
    name="duck-dashboard",
    urlpatterns=[
        path(
            "/",
            views.dashboard,
            name="index",
            methods=["GET"],
        ),
        path(
            "/logout",
            views.logout,
            name="logout",
            methods=["GET"],
        ),
    ],
    prepend_name_to_urls=True,
    enable_static_dir=True,
    enable_template_dir=False,
    is_builtin=True,
)
