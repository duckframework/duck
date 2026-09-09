"""
Script HTML Component.

This module defines a reusable `Script` component for embedding JavaScript code within an HTML document.
"""

from duck.html.components import InnerComponent
from duck.csp import csp_nonce, csp_nonce_flag


# Tokens after which a "/" is grammatically a regex literal, not division.
# Deliberately excludes ")" and "]" -- after those a "/" is division
# (e.g. "(a + b) / 2", "arr[0] / 2").
_JS_REGEX_PRECEDING_PUNCTUATION = set("([{,;:=!&|?+-*/%^~<>")
_JS_REGEX_PRECEDING_KEYWORDS = {
    "return", "typeof", "instanceof", "in", "of", "new", "delete", "void",
    "throw", "case", "do", "else", "yield", "await",
}


def minify_js(js: str) -> str:
    """
    Conservatively minifies JavaScript: strips comments and collapses
    incidental whitespace (indentation, blank lines, redundant inline
    spaces), without ever removing a newline that follows real code.

    JavaScript relies on newlines for Automatic Semicolon Insertion (ASI)
    -- `return\\n{ a: 1 }` and `return { a: 1 }` behave differently -- so
    merging lines the way a CSS minifier safely can is not safe here.
    This function only drops blank/whitespace-only lines, leading
    indentation, comments, and redundant runs of spaces/tabs within a
    line; every newline that separates two lines of real code is kept.

    String and regex literal contents are left completely untouched.
    Template literals (including their ``${...}`` substitutions) are
    preserved exactly as written and are not minified internally, to
    avoid any risk of misinterpreting nested code as whitespace.

    Args:
        js (str): Raw JavaScript source.

    Returns:
        The minified JavaScript.
    """
    if not js:
        return js

    return _minify_js_scan(js).strip()


def _minify_js_scan(js: str) -> str:
    """
    Single-pass scanner that strips comments and incidental whitespace
    while copying strings, template literals, and regex literals verbatim.
    """
    output = []
    length = len(js)
    last_token = ""
    i = 0

    while i < length:
        ch = js[i]

        if ch in ("'", '"'):
            start = i
            i = _skip_js_string(js, i)
            output.append(js[start:i])
            last_token = ch
            continue

        if ch == "`":
            start = i
            i = _skip_js_template(js, i)
            output.append(js[start:i])
            last_token = ch
            continue

        if ch == "/" and i + 1 < length and js[i + 1] == "/":
            j = js.find("\n", i)
            i = length if j == -1 else j
            continue

        if ch == "/" and i + 1 < length and js[i + 1] == "*":
            j = js.find("*/", i + 2)
            i = length if j == -1 else j + 2
            continue

        if ch == "/" and _js_regex_may_start(last_token):
            end = _skip_js_regex(js, i)
            if end is not None:
                output.append(js[i:end])
                last_token = "/"
                i = end
                continue
            # Not actually a regex (unterminated) -- fall through and
            # treat it as an ordinary division/punctuation character.

        if ch in " \t":
            j = i
            while j < length and js[j] in " \t":
                j += 1
            at_line_start = not output or output[-1] == "\n"
            at_line_end = j >= length or js[j] == "\n"
            if not at_line_start and not at_line_end:
                output.append(" ")
            i = j
            continue

        if ch == "\n":
            j = i
            while j < length and js[j] in " \t\r\n":
                j += 1
            if not output or output[-1] != "\n":
                output.append("\n")
            i = j
            continue

        if ch.isalnum() or ch in "_$":
            j = i
            while j < length and (js[j].isalnum() or js[j] in "_$"):
                j += 1
            word = js[i:j]
            output.append(word)
            last_token = word
            i = j
            continue

        output.append(ch)
        last_token = ch
        i += 1

    return "".join(output)


def _skip_js_string(js: str, i: int) -> int:
    """
    Returns the index just past the closing quote of the string literal
    starting at index i.
    """
    quote = js[i]
    length = len(js)
    j = i + 1

    while j < length:
        if js[j] == "\\":
            j += 2
            continue
        if js[j] == quote:
            return j + 1
        if js[j] == "\n":
            # Unterminated string -- stop here rather than swallow the rest.
            return j
        j += 1

    return j


def _skip_js_template(js: str, i: int) -> int:
    """
    Returns the index just past the closing backtick of the template
    literal starting at index i, treating any ``${...}`` substitution
    (including nested template literals within it) as opaque.
    """
    length = len(js)
    j = i + 1

    while j < length:
        ch = js[j]

        if ch == "\\":
            j += 2
            continue
        if ch == "`":
            return j + 1
        if ch == "$" and j + 1 < length and js[j + 1] == "{":
            j = _skip_js_template_expression(js, j + 2)
            continue
        j += 1

    return j


def _skip_js_template_expression(js: str, i: int) -> int:
    """
    Returns the index just past the "}" that closes a ``${...}``
    substitution, given i just after its opening "${".
    """
    length = len(js)
    depth = 1
    j = i

    while j < length and depth > 0:
        ch = js[j]

        if ch == "\\":
            j += 2
            continue
        if ch in ("'", '"'):
            j = _skip_js_string(js, j)
            continue
        if ch == "`":
            j = _skip_js_template(js, j)
            continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return j + 1
        j += 1

    return j


def _skip_js_regex(js: str, i: int) -> int:
    """
    Attempts to find the end of a regex literal starting at index i.

    Returns:
        The index just past the closing "/" and its flags, or None if
        this doesn't look like a valid regex literal (the caller should
        then treat the "/" as division instead).
    """
    length = len(js)
    j = i + 1
    in_class = False

    while j < length:
        ch = js[j]

        if ch == "\\":
            j += 2
            continue
        if ch == "\n":
            return None
        if ch == "[":
            in_class = True
        elif ch == "]":
            in_class = False
        elif ch == "/" and not in_class:
            j += 1
            while j < length and js[j].isalpha():
                j += 1
            return j
        j += 1

    return None


def _js_regex_may_start(last_token: str) -> bool:
    """
    Heuristic: is a "/" at this point grammatically a regex literal
    rather than division, based on the preceding token?
    """
    if not last_token:
        return True
    if last_token[-1] in _JS_REGEX_PRECEDING_PUNCTUATION:
        return True
    return last_token in _JS_REGEX_PRECEDING_KEYWORDS


class Script(InnerComponent):
    """
    Script HTML Component.

    The `Script` component allows developers to embed JavaScript code within an HTML page dynamically.
    It can be used to define inline scripts that interact with other components.

    Args:
        inner_html (str): The raw JavaScript to embed.
        minify (bool): Optional. Whether to minify the JavaScript. Defaults to True.

    **Features:**
    - Supports inline JavaScript execution.
    - Can be dynamically added to any component.
    - Provides flexibility for defining custom client-side logic.
    - Minifies the embedded script by default (comments, indentation, and
      blank lines only -- see `minify_js`), pass `minify=False` to disable.

    **Example Usage:**
    ```py
    script = Script(
        inner_html='''
            function showAlert() {
                alert("Hello, world!");
            }
        '''
    )
    component.add_child(script)
    ```

    This will generate the following HTML output:
    ```html
    <script>
    function showAlert() {
    alert("Hello, world!");
    }
    </script>
    ```

    **Notes:**
    - **Automatic Nonce Addition**: When `ENABLE_HEADERS_SECURITY_POLICY=True` and `csp_nonce_flag` is set in `CSP_TRUSTED_SOURCES`, the `nonce` property is automatically added.
    - **Request Resolution Required**: For the `nonce` to be set automatically, the request must be resolved. This is achieved by calling `get_request_or_raise` on the component root (or the current component if the root is `None`).
    """

    def on_create(self) -> None:
        """
        Initializes the component and, unless disabled, minifies the embedded script.
        """
        super().on_create()

        if self.kwargs.get("minify", True) and self.inner_html:
            self.inner_html = minify_js(self.inner_html)

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
            script_src = set(csp_directives.get("script-src"))
            if csp_nonce_flag in script_src:
                nonce = csp_nonce(request)
                # Use _get_raw_props instead to avoid recursion if this method is executed
                # from properties/props property method.
                self._get_raw_props()["nonce"] = nonce

    def get_element(self) -> str:
        """
        Returns the HTML tag for the component.
        """
        return "script"
