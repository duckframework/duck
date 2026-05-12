"""
Module containing function for decoding encoded urls.
"""

import urllib.parse


def url_decode(encoded_url):
    """
    Decodes a URL-encoded string.

    Args:
        encoded_url (str): The URL-encoded string.

    Returns:
        str: The decoded URL string.
    """
    try:
        return urllib.parse.unquote(encoded_url)
    except UnicodeDecodeError:
        # Handle potential decoding errors (e.g., invalid encoding)
        return encoded_url  # Return original string if decoding fails


def url_encode(raw_url):
    """
    Encodes a string into URL-encoded format.

    Args:
        raw_url (str): The raw string to be URL-encoded.

    Returns:
        str: The URL-encoded string.
    """
    try:
        return urllib.parse.quote(raw_url, safe="")
    except Exception:
        # Handle potential encoding errors
        return raw_url  # Return original string if encoding fails
