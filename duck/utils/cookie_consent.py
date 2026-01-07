"""
Utility functions for managing cookie consent in Duck framework apps.

**This module helps you:**
- Parse and check cookie consent categories from incoming requests.
- Set cookie consent on the response (server-driven).
- Generate a cookie string for use in client-side (JavaScript) dynamic consent banners.

Consent is stored as a JSON-encoded cookie, e.g.:

```json
{"analytics": true, "marketing": false}
```

**Recommended usage:**
- Use the same cookie name (default: "cookie_consent") on both backend and frontend.
- Set cookie via backend `set_cookie_consent()` after user accepts/rejects consent, or
- Generate a cookie string with `generate_cookie_consent_str()` for frontend use in dynamic modals.

**Example:** 

```py
# Check consent in a view
if has_cookie_consent(request, "analytics"):
    # Run analytics logic
    ...

# Set consent on response (server-driven)
set_cookie_consent(response, {"analytics": True, "marketing": False})

# Generate cookie string for JS (dynamic modal)
cookie_str = generate_cookie_consent_str({"analytics": True}, max_age=31536000)

# In JS: document.cookie = "{{ cookie_str }}";
```

**Functions:**
- get_cookie_consents(request, cookie_name)
- has_cookie_consent(request, category, cookie_name)
- set_cookie_consent(response, consents, cookie_name, **kwargs)
- generate_cookie_consent_str(consents, cookie_name, **kwargs)

------
USAGE EXAMPLES

1. **Server-Driven Approach (Recommended for backend-controlled consent):**

```py
from duck.utils.cookie_consent import set_cookie_consent, has_cookie_consent

def accept_cookies_view(request):
    response = HttpResponse("Consent updated")
    set_cookie_consent(response, {"analytics": True, "marketing": False})
    return response

def view(request):
    if has_cookie_consent(request, "analytics"):
        # Analytics code here
        pass
```

2. **Dynamic JS Approach (Frontend-driven banners):**

```py
from duck.utils.cookie_consent import generate_cookie_consent_str
from duck.html.components.page import Page
from duck.html.components.button import Button

def consent_banner_js(request):
    # Used to prefill consent state in JS, or as an example for your modal
    page = Page(request)
    accept_btn = Button(text="Accept All")
    page.add_to_body(accept_btn)
    
    async def on_accept(btn, event, value, ws):
        cookie_str = generate_cookie_consent_str({"analytics": True, "marketing": True})
        await ws.execute_js(f"document.cookie='{cookie_str}'';")
    
    # Bind event on click
    accept_btn.bind("click", on_accept, update_self=False, update_targets=[])    
    return page
```
"""

import json
from datetime import timedelta, datetime


def get_cookie_consents(request, cookie_name="cookie_consent"):
    """
    Retrieves the user's cookie consent preferences from the request cookies.

    Args:
        request: The Duck request object, which provides a COOKIES dictionary.
        cookie_name (str): The name of the consent cookie. Default is 'cookie_consent'.

    Returns:
        dict: Mapping of category names to booleans (e.g., {"analytics": True, "marketing": False}).
              Returns {} if the cookie is missing or invalid.
    """
    consent_raw = request.COOKIES.get(cookie_name)
    if not consent_raw:
        return {}
    try:
        try:
            # Try unquoting
            consent_raw = _urldecode(consent_raw)
        except Exception:
            pass
        return json.loads(consent_raw)
    except (ValueError, TypeError):
        return {}


def has_cookie_consent(request, category, cookie_name="cookie_consent"):
    """
    Checks if a user has given consent for a specific category.

    Args:
        request: The Duck request object.
        category (str): The category to check (e.g., "analytics", "marketing").
        cookie_name (str): The name of the consent cookie. Default is 'cookie_consent'.

    Returns:
        bool: True if consent is given for the category, False otherwise.
    """
    consents = get_cookie_consents(request, cookie_name)
    return bool(consents.get(category, False))


def set_cookie_consent(
    response,
    consents,
    cookie_name="cookie_consent",
    max_age=60*60*24*365,  # 1 year
    path="/",
    domain=None,
    secure=False,
    httponly=False,
    samesite="Lax",
    expires=None,
):
    """
    Sets the consent cookie on the response object (server-driven approach).

    Args:
        response: The Duck response object (must support set_cookie method).
        consents (dict): Consent dictionary (e.g., {"analytics": True, "marketing": False}).
        cookie_name (str): Name of the cookie to set.
        max_age (int): Cookie duration in seconds. Default: 1 year.
        path (str): Path for cookie. Default: "/".
        domain (str): Domain for cookie. Default: None.
        secure (bool): Set True for HTTPS sites. Default: False.
        httponly (bool): Prevent JS access if True. Default: False.
        samesite (str): SameSite policy. Default: "Lax".
        expires (datetime|str|None): Optional absolute expiration.

    Returns:
        None
    """
    value = json.dumps(consents)
    value = _urlencode(value)
    response.set_cookie(
        cookie_name,
        value=value,
        max_age=max_age,
        path=path,
        domain=domain,
        secure=secure,
        httponly=httponly,
        samesite=samesite,
        expires=expires
    )


def generate_cookie_consent_str(
    consents,
    cookie_name="cookie_consent",
    max_age=60*60*24*365,  # 1 year
    path="/",
    domain=None,
    secure=False,
    samesite="Lax",
    expires=None,
):
    """
    Generates a cookie string suitable for setting document.cookie in JS (dynamic banner approach).

    Args:
        consents (dict): Consent dictionary (e.g., {"analytics": True, "marketing": False}).
        cookie_name (str): Name of the cookie to set.
        max_age (int): Cookie duration in seconds. Default: 1 year.
        path (str): Path for cookie. Default: "/".
        domain (str): Domain for cookie. Default: None.
        secure (bool): Add "; Secure" if True. Defaults to False.
        samesite (str): SameSite policy. Default: "Lax".
        expires (datetime|str|None): Optional absolute expiration.

    Returns:
        str: Cookie string (e.g., 'cookie_consent=%7B%22analytics%22%3Atrue%7D; path=/; max-age=31536000; samesite=Lax; Secure')
    """
    value = json.dumps(consents)
    cookie = f"{cookie_name}={_urlencode(value)}"
    cookie += f"; path={path}"
    if domain:
        cookie += f"; domain={domain}"
    if max_age:
        cookie += f"; max-age={int(max_age)}"
    if expires:
        if isinstance(expires, datetime):
            expires_str = expires.strftime('%a, %d %b %Y %H:%M:%S GMT')
        else:
            expires_str = str(expires)
        cookie += f"; expires={expires_str}"
    if samesite:
        cookie += f"; samesite={samesite}"
    if secure:
        cookie += "; Secure"
    return cookie


def _urlencode(value):
    """
    Helper for JS-safe cookie encoding.
    """
    try:
        from urllib.parse import quote
        return quote(value)
    except ImportError:
        # Python 2 fallback, not needed in Duck/Python3
        import urllib
        return urllib.quote(value)


def _urldecode(value):
    """
    Helper for JS-safe cookie decoding.
    """
    try:
        from urllib.parse import unquote
        return unquote(value)
    except ImportError:
        # Python 2 fallback, not needed in Duck/Python3
        import urllib
        return urllib.unquote(value)
