"""
Style HTML Component.

This module defines a reusable `Style` component for embedding CSS styles within an HTML document.
"""

import re

from duck.html.components import InnerComponent
from duck.csp import csp_nonce, csp_nonce_flag


# Matches CSS comments and quoted strings together so string content is
# never touched by the whitespace-collapsing pass below.
_COMMENT_OR_STRING_RE = re.compile(
    r"""(?P<comment>/\*.*?\*/)|(?P<string>"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*')""",
    re.DOTALL,
)

# Collapses any run of whitespace down to a single space. Never removes a
# run entirely, so the single meaningful space in constructs like the
# descendant combinator (`.a .b`) or calc()'s `+`/`-` operators survives.
_WHITESPACE_RUN_RE = re.compile(r"[ \t\r\n\f]+")

# Whitespace directly touching these characters is never meaningful, so it
# can be trimmed on both sides. Deliberately excludes combinators
# (`+ ~ >`), since those require a space in calc() but not in selectors,
# and there's no safe way to tell the two apart with a regex.
_SAFE_PUNCTUATION_RE = re.compile(r"\s*([{};,()])\s*")

# Trailing space after a colon is always safe to drop ("color: red" ->
# "color:red"). Leading space before a colon is NOT touched, since
# ".btn :hover" (descendant pseudo-selector) and ".btn:hover" (pseudo-class
# of .btn itself) mean different things.
_COLON_TRAILING_SPACE_RE = re.compile(r":\s+")


def minify_css(css: str) -> str:
    """
    Conservatively minifies CSS: strips comments and collapses redundant
    whitespace, without ever touching whitespace inside quoted strings or
    removing spaces that change meaning (descendant combinators, calc()
    operators, ".btn :hover" style descendant pseudo-selectors).

    Args:
        css (str): Raw CSS source.

    Returns:
        The minified CSS.
    """
    if not css:
        return css

    chunks = []
    last_end = 0

    for match in _COMMENT_OR_STRING_RE.finditer(css):
        chunks.append(_minify_css_chunk(css[last_end:match.start()]))

        if match.group("string"):
            chunks.append(match.group("string"))
        # comments are dropped entirely

        last_end = match.end()

    chunks.append(_minify_css_chunk(css[last_end:]))

    return "".join(chunks).strip()


def _minify_css_chunk(chunk: str) -> str:
    """
    Minifies a chunk of CSS already known to contain no strings or comments.

    Args:
        chunk (str): A slice of CSS source outside any string/comment.

    Returns:
        The minified chunk.
    """
    chunk = _WHITESPACE_RUN_RE.sub(" ", chunk)
    chunk = _SAFE_PUNCTUATION_RE.sub(r"\1", chunk)
    chunk = _COLON_TRAILING_SPACE_RE.sub(":", chunk)
    return chunk


class Style(InnerComponent):
    """
    Style HTML Component.

    The `Style` component allows developers to define and embed custom CSS styles directly within an HTML page.
    It can be used to dynamically style elements without needing an external stylesheet.

    Args:
        inner_html (str): The raw CSS to embed.
        minify (bool): Optional. Whether to minify the CSS. Defaults to True.

    **Features:**
    - Supports inline CSS.
    - Can be dynamically added to any component.
    - Enables styling customization for other components.
    - Minifies the embedded CSS by default (comments and redundant
      whitespace only — see `minify_css`), pass `minify=False` to disable.

    **Example Usage:**
    ```py
    style = Style(
        inner_html='''
            .custom-popup {
                background-color: rgba(0, 0, 0, 0.8);
                color: white;
                padding: 10px;
                border-radius: 5px;
            }
        '''
    )
    component.add_child(style)
    ```

    This will generate the following HTML output:
    ```html
    <style>.custom-popup{background-color:rgba(0, 0, 0, 0.8);color:white;padding:10px;border-radius:5px}</style>
    ```

    **Notes:**
    - **Automatic Nonce Addition**: When `ENABLE_HEADERS_SECURITY_POLICY=True` and `csp_nonce_flag` is set in `CSP_TRUSTED_SOURCES`, the `nonce` property is automatically added.
    - **Request Resolution Required**: For the `nonce` to be set automatically, the request must be resolved. This is achieved by calling `get_request_or_raise` on the component root (or the current component if the root is `None`).
    - The `inner_html` parameter must contain valid CSS code.
    - This component is intended for **inline styles** and does not support linking to external CSS files.
    - Styles defined within this component will apply globally unless scoped using class or ID selectors.
    """

    def on_create(self) -> None:
        """
        Initializes the component and, unless disabled, minifies the embedded CSS.
        """
        super().on_create()

        if self.kwargs.get("minify", True) and self.inner_html:
            self.inner_html = minify_css(self.inner_html)

    @property
    def properties(self) -> dict:
        from duck.settings import SETTINGS

        # Get original props
        props = super().properties

        # Set CSP configuration.
        if SETTINGS['ENABLE_HEADERS_SECURITY_POLICY']:
            current_nonce = props.get("nonce")
            if not current_nonce:
                self.set_csp_nonce()
        return props

    def set_csp_nonce(self) -> None:
        """
        This tries to retrieve current request nonce.
        """
        from duck.settings import SETTINGS
        from duck.html.components.extensions import RequestNotFoundError

        try:
            root = self.get_raw_root()
            request = root.get_request_or_raise()
        except RequestNotFoundError:
            try:
                request = self.get_request_or_raise()
            except RequestNotFoundError:
                return

        # Set CSP configuration
        csp_directives = SETTINGS['CSP_TRUSTED_SOURCES']

        if csp_directives and request:
            style_src = set(csp_directives.get("style-src"))
            if csp_nonce_flag in style_src:
                nonce = csp_nonce(request)
                # Use _get_raw_props instead to avoid recursion if this method is executed
                # from properties/props property method.
                self._get_raw_props()["nonce"] = nonce

    def get_element(self) -> str:
        """
        Returns the HTML tag for the component.
        """
        return "style"
