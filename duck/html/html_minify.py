"""
Non-destructive HTML minifier — trims payload size without ever
changing what the HTML displays or means. Built on Python's stdlib
HTMLParser so it handles real-world, occasionally malformed markup
the way a browser would, rather than guessing with regex over the
whole document.
"""

import re

from html.parser import HTMLParser


# Whitespace inside these tags is significant and must never be touched
WHITESPACE_SENSITIVE_TAGS = frozenset({"pre", "textarea", "script", "style", "code"})

# A run of whitespace collapses to exactly one space — never to nothing,
# since removing it entirely can visually merge adjacent inline content
# (e.g. "<span>a</span> <span>b</span>" would read as "ab")
WHITESPACE_RUN = re.compile(r"\s+")


class InnerHTMLMinifier(HTMLParser):
    """
    Streams HTML through HTMLParser and reconstructs it with
    whitespace collapsed and comments stripped, while leaving tags,
    attributes, entities, and whitespace-sensitive content untouched.

    Non-destructive by design: nothing that could change how the HTML
    renders — attribute values, entity encoding, the content of
    <pre>/<textarea>/<script>/<style>, or the one space that keeps
    adjacent inline elements from merging — is ever altered.
    """

    def __init__(self, keep_comments: bool = False):
        """
        Args:
            keep_comments: When True, keeps every comment. When False
                (the default), strips ordinary comments but always
                keeps IE conditional comments (`<!--[if ...]-->` /
                `<!--[endif]-->`), since those change page behavior,
                not just readability.
        """
        super().__init__(convert_charrefs=False)
        self.keep_comments = keep_comments
        self.chunks = []
        self.preserve_depth = 0

    def minify(self, html: str) -> str:
        """
        Minifies a full HTML fragment.

        Args:
            html: The HTML to minify.

        Returns:
            The minified HTML.
        """
        self.chunks = []
        self.preserve_depth = 0
        self.feed(html)
        self.close()
        return "".join(self.chunks)

    def handle_starttag(self, tag, attrs):
        """
        Emits the start tag exactly as written, and enters
        whitespace-preserving mode for sensitive tags.
        """
        self.chunks.append(self.get_starttag_text())
        
        if tag.lower() in WHITESPACE_SENSITIVE_TAGS:
            self.preserve_depth += 1

    def handle_startendtag(self, tag, attrs):
        """
        Emits a self-closed tag exactly as written.
        """
        self.chunks.append(self.get_starttag_text())

    def handle_endtag(self, tag):
        """
        Emits the end tag, and leaves whitespace-preserving mode for
        sensitive tags.
        """
        self.chunks.append(f"</{tag}>")
        
        if tag.lower() in WHITESPACE_SENSITIVE_TAGS and self.preserve_depth > 0:
            self.preserve_depth -= 1

    def handle_data(self, data):
        """
        Emits text content, collapsing whitespace runs to a single
        space unless inside a whitespace-sensitive tag.
        """
        if self.preserve_depth > 0:
            self.chunks.append(data)
        else:
            self.chunks.append(WHITESPACE_RUN.sub(" ", data))

    def handle_entityref(self, name):
        """
        Emits a named entity reference exactly as encountered, e.g.
        `&amp;`, without decoding or re-encoding it.
        """
        self.chunks.append(f"&{name};")

    def handle_charref(self, name):
        """
        Emits a numeric character reference exactly as encountered,
        e.g. `&#39;`, without decoding or re-encoding it.
        """
        self.chunks.append(f"&#{name};")

    def handle_comment(self, data):
        """
        Drops ordinary comments; always keeps IE conditional comments,
        since those affect rendering, not just readability.
        """
        stripped = data.strip()
        is_conditional = stripped.startswith("[if") or stripped.startswith("[endif")
        
        if self.keep_comments or is_conditional:
            self.chunks.append(f"<!--{data}-->")

    def handle_decl(self, decl):
        """
        Emits a declaration (e.g. `<!DOCTYPE html>`) exactly as written.
        """
        self.chunks.append(f"<!{decl}>")

    def handle_pi(self, data):
        """
        Emits a processing instruction exactly as written.
        """
        self.chunks.append(f"<?{data}>")

    def unknown_decl(self, data):
        """
        Emits an unrecognized declaration (e.g. a CDATA section)
        exactly as written, rather than dropping it.
        """
        self.chunks.append(f"<![{data}]>")


def minify_inner_html(html: str, keep_comments: bool = False) -> str:
    """
    Minifies an HTML string without changing how it renders.

    Collapses runs of whitespace in ordinary text to a single space,
    strips comments (except IE conditional comments), and leaves tags,
    attributes, entities, and the content of <pre>, <textarea>,
    <script>, and <style> completely untouched.

    Args:
        html: The HTML to minify.
        keep_comments: When True, keeps every comment instead of
            stripping ordinary ones.

    Returns:
        The minified HTML. Empty or non-string input is returned as-is.
    """
    if not html or not isinstance(html, str):
        return html

    return InnerHTMLMinifier(keep_comments=keep_comments).minify(html)
