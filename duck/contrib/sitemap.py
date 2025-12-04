"""
Sitemap builder for Duck.

Class-based sitemap builder that walks the application's RouteRegistry and
builds an XML sitemap using Duck's component system (duck.html.components.to_component).

Example:
    builder = SitemapBuilder(
        server_url=None, # Parsing None will automatically resolve server URL
        save_to_file=True,
        filepath="/etc/sitemap.xml",
        extra_urls=["/about", "https://example.com/contact"],
        exclude_patterns=["^/admin", "https://example.com/secret", "^/api/.*"],
        default_priority=0.5,
        default_changefreq="weekly",
    )
    xml = builder.build(return_content=True)
"""
from __future__ import annotations

import os
import re
import copy

from datetime import date
from pathlib import Path
from urllib.parse import quote
from typing import (
    Iterable,
    List,
    Optional,
    Set,
)

from duck.html.components import to_component as _to_component
from duck.routes import RouteRegistry
from duck.settings import SETTINGS
from duck.utils.path import joinpaths
from duck.utils.urlcrack import URL
from duck.meta import Meta


# Create our own version of to_component
to_component = lambda *a, **kw: _to_component(*a, disable_lively=True, **kw)

# Create default exclude patterns
DEFAULT_EXCLUDES = [
    # 1. Static files and static folders
    (
        r"(?ix)^(?:.*\.(?:css|js|map|ico|mp3|png|jpe?g|gif|svg|webp|avif|bmp|tiff?|woff2?|ttf|eot|otf)$"
        + r"|.*/(?:static|assets|media)/.*)$"
    ),

    # 2. Dynamic paths
    r"^/sitemap.xml$", # Exclude the sitemap itself.
    r"^/ws/lively.*",       # anything starting with /ws/lively
    r"^/admin/.*",          # any subpath under /admin/
    r"^/admin$",            # strictly /admin itself
    r"^/api/.*",                # any subpath under /api/
    r"^/api$",                  # strictly /api itself
]


class SitemapBuilder:
    """
    Build an XML sitemap for a Duck application.

    The builder walks RouteRegistry.url_map, filters out dynamic or regex-like
    routes, supports explicit extra URLs, supports exclude patterns (absolute
    or relative, plain or regex), and emits a sitemap using Duck components.
    """
    
    __slots__ = (
        "server_url",
        "filepath",
        "save_to_file",
        "extra_urls",
        "exclude_patterns",
        "default_priority",
        "default_changefreq",
        "apply_default_excludes",
        "excludes_ignorecase",
    )
    
    # Characters considered indicative of regex-style routes (simple heuristic).
    _REGEX_META_CHARS = r"[\^\$\*\+\?\[\]\(\)\\]"

    def __init__(
        self,
        server_url: str = None,
        filepath: Optional[Union[str, Path]] = None,
        save_to_file: bool = True,
        extra_urls: Optional[Iterable[str]] = None,
        exclude_patterns: Optional[Iterable[str]] = None,
        default_priority: Optional[float] = 0.5,
        default_changefreq: Optional[str] = "monthly",
        apply_default_excludes: bool = True,
        excludes_ignorecase: bool = True,
    ) -> None:
        """
        Initialize the builder.
        
        Args:
            filepath (Optional[Union[str, Path]]): Optional path to save sitemap XML.
            save_to_file: Whether to persist the sitemap to disk. Filepath must be provided.
            extra_urls: Extra URL strings (absolute or path) to include in addition to the registered routes.
            
            exclude_patterns: URL strings or regex patterns to exclude. Absolute
                excludes match against the final URL; non-absolute excludes match
                against the registered route path and the final URL.
            
            default_priority: Default <priority> value for URLs (0.0 - 1.0). If
                None the <priority> element is omitted.
            
            default_changefreq: Default <changefreq> value for URLs (e.g., "daily",
                "weekly"). If None the <changefreq> element is omitted.
        
            apply_default_excludes (bool): Whether to apply default exclude patterns to your list of 
                exclude_patterns. Defaults to True.
        
            excludes_ignorecase (bool): Whether to use `re.IGNORECASE` when compiling exclude patterns. Defaults to True.
        """
        # TODO: Improve video indexing by using <video> directive
        self.filepath = str(filepath) if isinstance(filepath, Path) else filepath
        self.save_to_file = bool(save_to_file)
        self.extra_urls = list(extra_urls or [])
        self.exclude_patterns = list(exclude_patterns or [])
        self.default_priority = float(default_priority) if default_priority is not None else None
        self.default_changefreq = default_changefreq
        self.excludes_ignorecase = excludes_ignorecase
        
        # Server base URL (absolute), used to join relative routes.
        self.server_url = URL(server_url or Meta.get_absolute_server_url())
        
        # Attempt to clear explicit port for canonicalization when supported by URL.
        self.server_url.port = ""
        
        if apply_default_excludes:
            self.exclude_patterns.extend(DEFAULT_EXCLUDES)
        
    @staticmethod
    def _looks_like_regex(path: str) -> bool:
        """
        Return True if `path` contains characters that look like a regex.

        Args:
            path: Registered route string.

        Returns:
            True if the string contains regex meta characters.
        """
        return bool(re.search(SitemapBuilder._REGEX_META_CHARS, path))

    def _to_absolute_url(self, raw: str) -> URL:
        """
        Convert a raw URL or path into an absolute URL object.

        Args:
            raw: Absolute URL string or path.

        Returns:
            URL: An absolute URL object.
        """
        try:
            candidate = URL(raw)
        except Exception:
            # If parsing fails, treat as relative and join with server base
            return URL(URL.urljoin(self.server_url.to_str(), raw))

        if getattr(candidate, "is_absolute", False):
            return candidate

        return URL(URL.urljoin(self.server_url.to_str(), raw))

    def _is_excluded(self, full_url_str: str, registered_route_pattern: str) -> bool:
        """
        Decide whether a candidate URL should be excluded.

        Excludes in self.exclude_patterns can be:
        - absolute URL strings (or regexes) which match the full URL,
        - relative paths or patterns matched against registered route pattern or full URL,
        - plain strings (exact match) or regex patterns.

        Args:
            full_url_str: The absolute URL string to evaluate.
            registered_route_pattern: The registered route string or compiled
                pattern string to use for relative-match comparisons.

        Returns:
            True if the URL should be excluded.
        """
        parsed_full_url = URL(full_url_str)
        
        for pat in self.exclude_patterns:
            exclude_pattern = (re.compile(pat, re.IGNORECASE) if self.excludes_ignorecase else re.compile(pat)) if isinstance(pat, str) else pat
            if exclude_pattern.search("://"):
                # This is an absolute exclude
                if exclude_pattern.fullmatch(full_url_str):
                    return True
            else:
                # This is not an absolute URL, don't use fullmatch on relative URLs
                p = copy.copy(parsed_full_url)
                p.scheme = ""
                partial_url = p.to_str()
                
                # Try matching domain plus path
                if exclude_pattern.match(partial_url):
                    return True
                else:
                    # Try path only
                    p.netloc = ""
                    partial_url = p.to_str()
                    if exclude_pattern.match(partial_url):
                        return True
        return False

    def _collect_registered_urls(self) -> List[URL]:
        """
        Collect absolute URLs from RouteRegistry that are valid sitemap candidates.

        Returns:
            A list of absolute URL objects derived from registered routes.
        """
        collected: List[URL] = []
        seen: Set[str] = set()

        for registered_route, route_info in RouteRegistry.url_map.items():
            # Skip dynamic routes (containing angle-bracket variables)
            if "<" in registered_route:
                continue

            # Skip regex-like registered routes
            if self._looks_like_regex(registered_route):
                continue

            # Build full absolute URL
            full_str = URL.urljoin(self.server_url.to_str(), registered_route)
            full_url = URL(full_str)

            # Prefer a compiled pattern string for exclusion matching if provided
            pattern_for_match = registered_route
            try:
                if isinstance(route_info, dict):
                    for _, info in route_info.items():
                        if isinstance(info, (list, tuple)) and len(info) >= 3:
                            patt = getattr(info[2], "pattern", None)
                            if patt:
                                pattern_for_match = patt
                                break
            except Exception:
                # ignore route_info structure problems
                pass

            if self._is_excluded(full_str, pattern_for_match):
                continue

            if full_str in seen:
                continue

            seen.add(full_str)
            collected.append(full_url)

        return collected

    def _collect_extra_urls(self, existing_set: Set[str]) -> List[URL]:
        """
        Normalize and filter explicitly provided extra URLs.

        Args:
            existing_set: Set of absolute URL strings already collected.

        Returns:
            A list of extra absolute URL objects to include.
        """
        out: List[URL] = []
        for raw in self.extra_urls:
            try:
                candidate = self._to_absolute_url(raw)
            except Exception:
                candidate = URL(URL.urljoin(self.server_url.to_str(), raw))

            full = candidate.to_str()
            if full in existing_set:
                continue

            if self._is_excluded(full, raw):
                continue

            existing_set.add(full)
            out.append(candidate)

        return out

    def _build_url_component(self, url_obj: URL, lastmod_iso: str, changefreq: Optional[str], priority: Optional[float]):
        """
        Construct a <url> component for a given URL.

        Args:
            url_obj: The URL object to include.
            lastmod_iso: ISO formatted last modified date string.
            changefreq: Optional changefreq value.
            priority: Optional priority between 0.0 and 1.0.

        Returns:
            Component instance for the <url> element.
        """
        # We only quote path, query & fragment
        url_obj = copy.copy(url_obj)
        url_obj.query = quote(url_obj.query)
        url_obj.fragment = quote(url_obj.fragment)
        final_url = url_obj.to_str()
        loc = to_component(final_url, tag="loc")
        children = [loc]

        if lastmod_iso:
            children.append(to_component(lastmod_iso, tag="lastmod"))

        if changefreq:
            children.append(to_component(changefreq, tag="changefreq"))

        if priority is not None:
            priority_text = f"{priority:.1f}"
            children.append(to_component(priority_text, tag="priority"))

        return to_component(tag="url", children=children)

    def build(self, return_content: bool = True) -> Optional[str]:
        """
        Build the sitemap XML.

        Args:
            return_content: If True, return the sitemap XML as a string. If False,
                return None (but still save to file if configured).

        Returns:
            The sitemap XML string when `return_content` is True, otherwise None.
        """
        registered_urls = self._collect_registered_urls()
        seen = {str(u) for u in registered_urls}

        extra_urls = self._collect_extra_urls(seen)
        candidates = registered_urls + extra_urls

        sitemap_ns = "http://www.sitemaps.org/schemas/sitemap/0.9"
        today_iso = date.today().isoformat()

        url_nodes = []
        for u in candidates:
            node = self._build_url_component(u, lastmod_iso=today_iso, changefreq=self.default_changefreq, priority=self.default_priority)
            url_nodes.append(node)

        urlset = to_component(tag="urlset", children=url_nodes, props={"xmlns": sitemap_ns})

        sitemap_body = urlset.render()
        sitemap_xml = '<?xml version="1.0" encoding="UTF-8"?>\n' + sitemap_body

        if self.save_to_file:
            filepath = self.filepath
            
            if filepath is None:
                raise TypeError("Filepath cannot be None if save_to_file=True.")
                
            with open(filepath, "w", encoding="utf-8") as fh:
                fh.write(sitemap_xml)

        if return_content:
            return sitemap_xml
        return None
