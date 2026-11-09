"""
Blueprint `Lively` created on Sun, 08 Nov 2026 16:18:53 GMT
"""
from duck.routes import Blueprint
from duck.urls import path, re_path
from duck.utils.path import joinpaths
from duck.settings import SETTINGS
from duck.storage import duck_storage


from . import views


def resolve_static_dir() -> str:
    """
    Resolves and returns the correct static dir for Lively.
    """
    target_dir = joinpaths(duck_storage, "html/components/core/staticfiles")
            
    if SETTINGS['NATIVE_ENABLED']:
        from duck_native.storage import NATIVE_STORAGE
        
        target_dir = NATIVE_STORAGE / "components/staticfiles"
    
    return target_dir
    

Lively = Blueprint(
    location=__file__,
    name="lively",
    urlpatterns=[
        path("/ws", views.websocket, name="ws"),
        path("/sync", views.sync_browser_state, name="browser-sync"),
        path("/ws-file", views.receive_ws_file, name="receive-ws-file"),
    ],
    prepend_name_to_urls=True,
    static_dir=resolve_static_dir(),
    template_dir="ui/templates",
    enable_static_dir=True,
    enable_template_dir=False,
    is_builtin=True,
)
