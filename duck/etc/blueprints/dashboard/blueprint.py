"""
Blueprint definition for the Duck Framework server dashboard.

Register this in your project settings under BLUEPRINTS to mount
the dashboard at /dashboard.
"""

from duck.routes import Blueprint
from duck.urls import path

from . import views


Dashboard = Blueprint(
    location=__file__,
    name="dashboard",
    urlpatterns=[
        path(
            "/",
            views.dashboard,
            name="index",
            methods=["GET"],
        ),
    ],
    prepend_name_to_urls=True,
    enable_static_dir=True,
    enable_template_dir=False,
    is_builtin=True,
)
