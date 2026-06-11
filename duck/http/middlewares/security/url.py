"""
Module containing middleware classes for inspecting URLs for various attacks like XSS and SQL Injection.
"""

from duck.http.middlewares import BaseMiddleware
from duck.http.middlewares.security.modules.command_injection import check_command_injection_in_url
from duck.http.middlewares.security.modules.sql_injection import check_sql_injection_in_url
from duck.http.middlewares.security.modules.xss import check_xss_in_url
from duck.http.response import HttpBadRequestResponse
from duck.utils.path import is_good_url_path
from duck.settings import SETTINGS


class URLSecurityMiddleware(BaseMiddleware):
    """
    URLSecurityMiddleware class checking URL correctness.
    """
    debug_message: str = "URL Security Middleware: Malformed URL"

    @classmethod
    def get_error_response(cls, request) -> HttpBadRequestResponse:
        """
        Returns an appropriate response upon error.
        """
        from duck.contrib.responses import make_response
        
        body = None
        
        if SETTINGS["DEBUG"]:
            # Add extra debug message in DEBUG
            body = "<p>URL is Invalid or Malformed.</p>"
        
        # Construct and return the final response.    
        response = make_response(HttpBadRequestResponse, body=body)
        return response
        
    @classmethod
    def process_request(cls, request):
        """
        Process basic URL checks on the request.
        """
        url_path_ok = is_good_url_path(request.path)
        
        if url_path_ok:
            return cls.request_ok
        
        # URL is malformed at this point
        return cls.request_bad


class XSSMiddleware(BaseMiddleware):
    """
    XSSMiddleware class mitigating against XSS attacks.
    """
    debug_message: str = "XSS Middleware: Potential URL XSS"

    @classmethod
    def get_error_response(cls, request) -> HttpBadRequestResponse:
        """
        Returns appropriate error response.
        """
        from duck.contrib.responses import make_response
        
        body = None
        
        if SETTINGS["DEBUG"]:
            body = "<p>URL contains Potential XSS Attack Signature.</p>"
            url_xss_attack = getattr(request, "url_xss_attack", None)
            
            if url_xss_attack:
                body = f"<p>{url_xss_attack}</p>"
        
        # Build and return final response.
        response = make_response(HttpBadRequestResponse, body=body)
        return response

    @classmethod
    def process_request(cls, request):
        """
        Process and check for URL XSS in request.
        """
        url = request.fullpath
        xss_found, msg = check_xss_in_url(url)
        
        if xss_found:
            request.url_xss_attack = msg
            return cls.request_bad
        
        # Request URL is probably fine.
        return cls.request_ok


class SQLInjectionMiddleware(BaseMiddleware):
    """
    SQLInjectionMiddleware class mitigating against SQL injection attacks.
    """
    debug_message: str = "SQL Injection Middleware: Potential URL SQL injection"

    @classmethod
    def get_error_response(cls, request) -> HttpBadRequestResponse:
        """
        Returns appropriate error response.
        """
        from duck.contrib.responses import make_response
        
        body = None
        
        if SETTINGS["DEBUG"]:
            # Add extra debug message.
            body = "<p>URL contains Potential SQL Injection.</p>"
        
        # Build final response.
        response = make_response(HttpBadRequestResponse, body=body)
        return response

    @classmethod
    def process_request(cls, request):
        """
        Check for SQL injection in request's URL
        """
        url = request.fullpath
        
        if not check_sql_injection_in_url(url):
            return cls.request_ok
        
        # Request is not safe.
        return cls.request_bad


class CommandInjectionMiddleware(BaseMiddleware):
    """
    CommandInjectionMiddleware class mitigating against command injection attacks.
    """
    debug_message = "Command Injection Middleware: Potential URL command injection"

    @classmethod
    def get_error_response(cls, request) -> HttpBadRequestResponse:
        """
        Returns appropriate error response.
        """
        from duck.contrib.responses import make_response
        
        body = None
        
        if SETTINGS["DEBUG"]:
            body = "<p>URL contains Potential Command Injection.</p>"
        
        # Build and return final response
        response = make_response(HttpBadRequestResponse, body=body)
        return response

    @classmethod
    def process_request(cls, request):
        """
        Check request's URL for potential command injection.
        """
        # Don't use request.path but request.fullpath (this is better for finding command inj)
        
        url = request.fullpath
        target_1 = url.split("?", 1)[0] # Removing all queries
        target_2 = url.replace("&", "") # Replace all &
        
        if not check_command_injection_in_url(target_1) and not check_command_injection_in_url(target_2):
            return cls.request_ok
        
        # Request potentially unsafe.
        return cls.request_bad
