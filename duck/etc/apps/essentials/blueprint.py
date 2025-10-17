"""
Module containing Duck's essesntials blueprint.
"""
# yapf: disable
from duck.urls import path
from duck.routes import Blueprint
from duck.settings import SETTINGS
from duck.utils.path import normalize_url_path

from . import views


STATIC_URL = normalize_url_path(str(SETTINGS["STATIC_URL"]))
MEDIA_URL = normalize_url_path(str(SETTINGS["MEDIA_URL"]))


MediaFiles = Blueprint(
    location=__file__,
    name="media",
    urlpatterns=[
        path(
            f"{MEDIA_URL}/<mediafile>",
            views.mediafiles_view,
            name="mediafiles",
            methods=["GET"],
        ),
    ],
    prepend_name_to_urls=False,
    enable_template_dir=False,
    enable_static_dir=False,
    is_builtin=True,
)


StaticFiles = Blueprint(
    location=__file__,
    name="static",
    urlpatterns=[
        path(
            f"{STATIC_URL}/<staticfile>",
            views.staticfiles_view,
            name="staticfiles",
            methods=["GET"],
        ),
    ],
    prepend_name_to_urls=False,
    enable_template_dir=False,
    enable_static_dir=False,
    is_builtin=True,
)
