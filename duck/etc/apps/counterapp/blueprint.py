"""
Blueprint `CounterApp` created on Tue, 12 Aug 2025 14:37:51 GMT

CounterApp for the Lively Component System.
"""
from duck.routes import Blueprint
from duck.urls import path, re_path
from duck.html.components.core.system import LivelyComponentSystem

from . import views


class CounterAppError(Exception):
    """
    Raised on CounterApp related errors.
    """
    
if not LivelyComponentSystem.is_active():
    raise CounterAppError(
        "CounterApp requires lively component system to be active. "
        "Please set `ENABLE_COMPONENT_SYSTEM` to True in settings.py."
    )


CounterApp = Blueprint(
    location=__file__,
    name="counterapp",
    urlpatterns=[
        path("/", views.HomeView, name="counterapp"),
    ],
    prepend_name_to_urls=True,
    static_dir="static",
    template_dir="templates",
    enable_static_dir=True,
    enable_template_dir=False,
    is_builtin=True,
)
