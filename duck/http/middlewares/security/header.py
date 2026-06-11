"""
Module for header middlewares.
"""
import re

from duck.http.middlewares import BaseMiddleware
from duck.http.middlewares.security.modules.header_injection import check_header_injection
from duck.http.response import HttpBadRequestResponse, HttpForbiddenRequestResponse
from duck.settings import SETTINGS


class HostMiddleware(BaseMiddleware):
    """
    Host Middleware class mitigating against requests from
     unknown sources and other host header issues.
    """
    allowed_hosts = SETTINGS["ALLOWED_HOSTS"]
    debug_message: str = "Host Middleware: Host invalid/unrecognized"

    @classmethod
    def get_error_response(cls, request) -> HttpBadRequestResponse:
        """
        Return the error response upon errors.
        """
        from duck.contrib.responses import make_response
        
        host = request.get_header("host")
        body = None
        
        if SETTINGS["DEBUG"]:
            body = f"<p>Host invalid/unrecognized</p>"
            
            if hasattr(request, "host_error_msg"):
                if request.host_error_msg:
                    body = f"<p>{request.host_error_msg}</p>"
        
        # Generate response.
        response = make_response(HttpForbiddenRequestResponse, body=body)    
        return response
    
    @classmethod
    def process_request(cls, request):
        """
        Process and incoming response.
        """
        from duck.utils.net import is_valid_host
        from duck.utils.wildcard import process_wildcards
        
        host = request.get_header("host", "").strip()
        valid, reason = is_valid_host(host)
        
        if not valid:
            request.host_error_msg = reason
            cls.debug_message = "Host Middleware: Host invalid: %s"%(host)
            return cls.request_bad
            
        for allowed_host in cls.allowed_hosts:
            if "]:" in host:
                host = host.rsplit("]:", 1)[0]
            else:
                host = host.split(':', 1)[0] if host.count(':') == 1 else host
            
            if process_wildcards(allowed_host, [host]):
                # host is allowed
                return cls.request_ok
        
        # Add reference to errors and return final state
        request.host_error_msg = f"Disallowed host, you may need to add {host} in ALLOWED_HOSTS"
        cls.debug_message = "Host Middleware: Host invalid/unrecognized: %s"%(host)
        return cls.request_bad


class HeaderInjectionMiddleware(BaseMiddleware):
    """
    HeaderInjectionMiddleware class mitigating against various
    header injection attacks like `Potential Session Fixation` (Multiple Cookies),
    `XSS` (Script Tag Detected), `Potential Open Redirect` (External URL),
    `Potential Cache Poisoning` (Anti-Caching Headers).
    """
    debug_message: str = "Header Injection Middleware: Potential header injection"

    @classmethod
    def get_error_response(cls, request) -> HttpBadRequestResponse:
        """
        Return necessary error response.
        """
        from duck.contrib.responses import make_response
        
        body = None
        
        if SETTINGS["DEBUG"]:
            # In debug, add attack type for debug purposes.
            attack_type = getattr(request, "header_injection_attack_type", None)
            
            if attack_type is not None:
                body = f"<p>{attack_type.title()}</p>"
        
        # Return the final response.
        response = make_response(HttpBadRequestResponse, body=body)
        return response

    @classmethod
    def process_request(cls, request):
        """
        Process an incoming request for potential header injection.
        """
        headers = request.headers
        
        # Check for header injection
        result, attack_type = check_header_injection(headers)
        
        if result:
            # Potential header injection attack
            # Set header injection type
            request.header_injection_attack_type = attack_type
            return cls.request_bad
        return cls.request_ok
