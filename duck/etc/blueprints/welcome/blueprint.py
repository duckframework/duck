"""
Blueprint `Welcome` for the welcome page.
"""
from duck.routes import Blueprint
from duck.urls import path, re_path

from . import views

Welcome = Blueprint(
    location=__file__,
    name="welcome",
    urlpatterns=[
        # URL patterns here
    ],
    prepend_name_to_urls=False,
    static_dir="ui/static",
    template_dir="ui/templates",
    enable_static_dir=True,
    enable_template_dir=False,
)
