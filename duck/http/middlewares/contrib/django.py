"""
Module containing middleware class for Fixing request before reaching to Django server.
"""
from duck.settings import SETTINGS
from duck.http.middlewares import BaseMiddleware
from duck.utils.urlcrack import URL


class DjangoRequestFixerMiddleware(BaseMiddleware):
    """
    Middleware for fixing and ensuring correct headers and info before request is sent to Django server.
    """
    
    @classmethod
    def process_request(cls, request):
        # Fix some request fields
        # Ensure HTTP version is HTTP/1.1
        if "/2" in str(request.http_version):
            request.http_version = "HTTP/1.1"
            
        # Add a forward slash to Django requests
        # Not doing this may cause unending redirects from django admin page.
        if not request.path.endswith("/"):
            new_fullpath = request.path + "/"
            query_string = request.META.get("QUERY_STRING", "")
            if query_string:
                new_fullpath += "?" + query_string
            if not new_fullpath.endswith("/"):
                new_fullpath += "/"
            request.fullpath = new_fullpath
        
        # Fix some headers
        secret_domain = SETTINGS["DJANGO_SHARED_SECRET_DOMAIN"]
        
        if not secret_domain:
            return cls.request_ok
        
        # Add headers on the real http headers before they are modified
        if request.host:
            request.headers["D-Host"] = request.host
        
        if request.origin:
            request.headers["D-Origin"] = request.origin
        
        host_obj = URL(request.host)
        host_obj.host = secret_domain
        
        if host_obj.scheme:
            # Convert scheme to http
            host_obj.scheme = "http"
        
        # Also set ports to None because Django doesnt support Host with port according to RFC 1034/1035.
        host_obj.port = None
        
        # Headers to modify
        modify_headers = {'host': host_obj.to_str()}
        
        if request.referer:
            referer = URL(request.referer)
            referer.scheme = "http" # modify to correct scheme
            referer.host = secret_domain
            referer.port = None
            if referer.path and not referer.path.endswith('/'):
                # Add django forward slash again if not found
                referer.path = referer.path + "/"
            modify_headers['referer'] = referer.to_str()
        
        if request.origin:
            origin = URL(request.origin)
            origin.scheme = "http" # modify to correct scheme
            origin.host = secret_domain
            origin.port = None
            modify_headers['origin'] = origin.to_str()
            
        # Modify some headers: host, referer and origin
        request.headers.update(modify_headers)
        return cls.request_ok
