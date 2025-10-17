
from duck.utils.safemarkup import MarkupSafeString as MarkupSafeString
from duck.utils.safemarkup import mark_safe as mark_safe


def escape(content: str) -> str:
    """
    Escapes HTML special characters in the input string to prevent injection attacks and broken markup.

    The following replacements are made:
        &  -> &amp;
        <  -> &lt;
        >  -> &gt;
        "  -> &quot;
        '  -> &#x27;

    Args:
        content (str): Raw string to escape.

    Returns:
        str: Escaped HTML-safe string.
    """
    return (content
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#x27;"))
