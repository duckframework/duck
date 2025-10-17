"""
Content-Security utility module.
"""
import os

from duck.secrets import generate_ascii_secret


# Flag to alert the server that this requires a CSP flag.
csp_nonce_flag = "requires-csp-nonce"


def csp_nonce(request, add_nonce_prefix: bool = False) -> str:
    """
    Returns the current nonce token for the strict `Content-Security-Policy`.
    
    Args:
        request (HttpRequest): The target HTTP request.
        add_nonce_prefix (bool): Whether to add the prefix `nonce-` to the nonce value.    
    """
    nonce = request.META.get('DUCK_CSP_NONCE', None)
    if not nonce:
        nonce = generate_ascii_secret(16)
        request.META['DUCK_CSP_NONCE'] = nonce
    if add_nonce_prefix:
        return f"nonce-{nonce}"
    return nonce


def refresh_nonce(request) -> str:
    """
    Refreshes and returns a newly generated nonce value.
    """
    if "DUCK_CSP_NONCE" in request.META:
        del request.META["DUCK_CSP_NONCE"]
        return csp_nonce(request)
