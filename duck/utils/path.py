"""
Module for Path Operations, .e.g path sanitization, manipulations, joining etc.
"""
import re
import os
import pathlib

from typing import List, Optional, Union

from .urlcrack import URL


# Allowed characters for URL path as defined by RFC 3986 (safe and reserved)
URL_PATH_REGEX = r'^[a-zA-Z0-9\-._~:/?#@!$&\()*+,;=%]*$'


def url_normalize(url: str, ignore_chars: Optional[List[str]] = None) -> str:
    """
    Normalizes a URL by removing consecutive slashes, adding a leading slash, removing trailing slashes, removing disallowed characters, e.g "<", string quotes (etc), replacing back slashes and lowercasing the scheme.
    """
    return URL.normalize_url(url)
    

def normalize_url_path(url_path: str, ignore_chars: Optional[List[str]] = None) -> str:
    """
    Normalizes a URL path by removing consecutive slashes, adding a leading slash, removing trailing slashes, removing disallowed characters, e.g "<", string quotes (etc), replacing back slashes and lowercasing the scheme.
    """
    return URL.normalize_url_path(url_path, ignore_chars)


def joinpaths(path1: Union[str, pathlib.Path], path2: Union[str, pathlib.Path], *more):
    """
    Returns joined paths but makes sure all paths are included in the final path rather than `os.path.join`.
    """
    path1 = str(path1) if isinstance(path1, pathlib.Path) else path1
    path2 = str(path2) if isinstance(path2, pathlib.Path) else path2
    
    # Clean paths and join
    path1 = path1.replace("\\","/").rstrip("/")
    path2 = path2.replace("\\","/").lstrip("/")
    finalpath = os.path.join(path1, path2)

    for p in more:
        finalpath = joinpaths(finalpath, p)
    return finalpath


def sanitize_path_segment(segment):
    """
    Sanitize a path segment to prevent directory traversal attacks. (same as `normalize_url_path`)

    Args:
            segment: The path segment to sanitize.

    Returns:
            str: The sanitized path segment.
    """
    return normalize_url_path(segment)


def paths_are_same(path1, path2):
    """
    Checks if two paths point to the same location, handling case-insensitivity and different separators.
    """

    # Convert to Path objects for easier manipulation
    path1 = pathlib.Path(path1)
    path2 = pathlib.Path(path2)

    # Normalize paths for case-insensitive comparison (important on Windows)
    path1 = path1.resolve().as_posix()
    path2 = path2.resolve().as_posix()
    return path1 == path2


def build_absolute_uri(root_url: str, path: str, normalization_ignore_chars: Optional[List[str]] = None) -> str:
    """
    This builds an absolute url from provided root_url and path.
    
    Args:
        path (str): The path to join with the root url.
        normalization_ignore_chars (Optional[List[str]]): List of characters to ignore when normalizing the url path.
            By default, all unsafe characters are stripped. 
    """
    url_obj = URL(root_url, normalization_ignore_chars)
    path = "/" + path
    
    if not url_obj.scheme:
        raise ValueError("Root URL provided should start with a scheme (e.g 'http' or 'https'): "+ root_url)
    
    url_obj.innerjoin(path, normalization_ignore_chars=normalization_ignore_chars)
    
    return url_obj.to_str()


def is_absolute_url(url: str):
    """
    Check whether a URL is s complete url including scheme (e.g. 'https')
    """
    url_obj = URL(url)
    if not url_obj.scheme:
        return False
    if not url_obj.netloc:
        return False
    return True


def is_good_url_path(url_path: str) -> bool:
    """
    Validates if the URL path conforms to RFC 3986 standards.
    Only allows specific special characters.
    Also checks for disallowed characters like space, tilde (~), etc.

    Args:
        url_path: The URL path string to validate.

    Returns:
        bool: True if the URL is in the specified format and has no disallowed characters, False otherwise.
    """
    if not url_path:
        return False
    if re.match(URL_PATH_REGEX, url_path):
        return True
    return False


def replace_hostname(
    url: str,
    hostname: str,
) -> str:
    """
    Replaces the hostname in a URL.
    
    If URL doesn't have scheme (e.g https) or is a urlpath, no modifications will be done.
    
    Args:
        url (str): The target URL.
        new_hostname (str): The new hostname or domain.
    """
    url_obj = URL(url)
    url_obj.host = hostname
    return url_obj.to_str()
