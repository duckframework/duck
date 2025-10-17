"""
Improved SQLi detector for URLs.

- Keeps a very fast "quick safe" path for common clean URLs.
- Decodes URL components and inspects path segments + query values + fragment.
- Uses a lightweight scoring system with pre-compiled regexes to reduce false positives.
- Caps per-token scanning length to keep work bounded.
- Returns True when a potential SQL injection is detected.
"""

import re
from urllib.parse import urlparse, parse_qs, unquote_plus

# --- Config (tweakable) ---
MAX_TOKEN_LENGTH = 512        # truncate tokens longer than this for scanning
MAX_URL_LENGTH = 4096         # ignore anything beyond this in the raw URL
SCORE_THRESHOLD = 6           # score required to flag as potential SQLi
PER_TOKEN_FLAG = 5            # single-token score threshold to immediately flag

# --- Fast whitelist (common-safe characters in paths/params) ---
# allow alnum, underscore, dash, dot, tilde, slash, percent (encoded), colon, at, +, =
_QUICK_SAFE_RE = re.compile(r"^[A-Za-z0-9_\-./~:@+%=&]*$")

# --- Precompiled SQLi detection patterns (weights applied later) ---
_KEYWORD_RE = re.compile(
    r"\b(SELECT|UPDATE|INSERT|DELETE|DROP|ALTER|CREATE|TRUNCATE|REPLACE|UNION|WHERE|HAVING|ORDER\s+BY|GROUP\s+BY|FROM|INTO|JOIN|LIMIT)\b",
    re.I,
)

_UNION_SELECT_RE = re.compile(r"UNION(?:\s+ALL)?\s+SELECT", re.I)
_STACKED_QUERY_RE = re.compile(r";\s*(?:SELECT|INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|TRUNCATE|REPLACE)", re.I)
_TAUTOLOGY_RE = re.compile(r"\b(?:OR|AND)\s+\d+\s*=\s*\d+\b", re.I)
_SQL_COMMENT_RE = re.compile(r"(--\s)|(/\*)|(\*/)|(#\s)", re.I)
_ENCODED_PAYLOAD_RE = re.compile(r"(?:%27|%22|%3D|%3B|%2F%2A|%2A%2F|%2D%2D)", re.I)  # encoded ', ", =, ;, /*, */, --
_SIMPLE_SUSPICIOUS_RE = re.compile(r"\b(OR|AND|NOT|LIKE|IN|BETWEEN)\b", re.I)
_SQL_FUNCTION_RE = re.compile(r"\b(SLEEP|BENCHMARK|CHAR|CONCAT|LOAD_FILE|INTO OUTFILE|INTO DUMPFILE|BENCHMARK)\b", re.I)
_SQL_META_RE = re.compile(r"\b(XP_|@@|VERSION\(|USER\(|DATABASE\(|SCHEMA_NAME\(|INFORMATION_SCHEMA)\b", re.I)

# small words commonly used in credential-scanning (low-weight)
_SENSITIVE_WORDS_RE = re.compile(r"\b(admin|password|passwd|user|username|passwd_hash|credentials|table_name|column_name)\b", re.I)

# direct quote characters (unencoded)
_QUOTE_RE = re.compile(r"[\"']")

# fast numeric equality pattern like "1=1" or "0 = 0"
_NUMERIC_EQ_RE = re.compile(r"\b\d+\s*=\s*\d+\b")

# helper: compile list for iteration (tuple of (regex, weight))
_PATTERNS_WEIGHTS = (
    (_UNION_SELECT_RE, 6),
    (_STACKED_QUERY_RE, 6),
    (_TAUTOLOGY_RE, 5),
    (_SQL_COMMENT_RE, 4),
    (_ENCODED_PAYLOAD_RE, 3),
    (_SQL_FUNCTION_RE, 3),
    (_SQL_META_RE, 3),
    (_KEYWORD_RE, 2),
    (_SIMPLE_SUSPICIOUS_RE, 1),
    (_SENSITIVE_WORDS_RE, 1),
    (_QUOTE_RE, 1),
    (_NUMERIC_EQ_RE, 2),
)


def _shorten(token: str) -> str:
    """Truncate token to MAX_TOKEN_LENGTH for safety and performance."""
    if len(token) > MAX_TOKEN_LENGTH:
        return token[:MAX_TOKEN_LENGTH]
    return token


def _gather_tokens(url: str) -> list[str]:
    """
    Parse URL and return a list of decoded tokens to analyze:
    - path segments
    - query parameter values
    - fragment
    - the entire query string (small)
    """
    if len(url) > MAX_URL_LENGTH:
        url = url[:MAX_URL_LENGTH]

    parsed = urlparse(url)
    tokens: list[str] = []

    # path segments
    path = parsed.path or ""
    for seg in path.split("/"):
        if not seg:
            continue
        try:
            dec = unquote_plus(seg)
        except Exception:
            dec = seg
        tokens.append(_shorten(dec))

    # query parameter values
    try:
        params = parse_qs(parsed.query, keep_blank_values=True)
    except Exception:
        params = {}
    for values in params.values():
        for v in values:
            try:
                dec = unquote_plus(v)
            except Exception:
                dec = v
            tokens.append(_shorten(dec))

    # fragment
    if parsed.fragment:
        try:
            dec = unquote_plus(parsed.fragment)
        except Exception:
            dec = parsed.fragment
        tokens.append(_shorten(dec))

    # include raw query string as a token (decoded)
    if parsed.query:
        try:
            decq = unquote_plus(parsed.query)
        except Exception:
            decq = parsed.query
        tokens.append(_shorten(decq))

    return tokens


def is_safe_url(url: str) -> bool:
    """
    Fast check: returns True if URL appears trivially safe (all components
    contain only very common safe characters). This is a cheap fast-path used
    to avoid deeper scanning for the majority of benign requests.

    Note: we intentionally allow common path/file characters (., -, digits).
    """
    if not url:
        return True

    # check raw url quickly (fast path)
    try:
        to_check = url if len(url) <= MAX_URL_LENGTH else url[:MAX_URL_LENGTH]
        # decode a bit to catch encoded bad characters folded into allowed set
        decoded = unquote_plus(to_check)
    except Exception:
        decoded = to_check

    # If the whole decoded URL contains only quick-safe chars, treat as safe
    if _QUICK_SAFE_RE.fullmatch(decoded):
        return True

    # Otherwise, check path + params quickly: if every token is quick-safe, return True
    for token in _gather_tokens(url):
        if not _QUICK_SAFE_RE.fullmatch(token):
            return False
    return True


def check_sql_injection_in_url(url: str) -> bool:
    """
    Returns True if a potential SQL injection is detected in the URL.
    Strategy:
      1) Quick safe path (very fast). If safe, return False.
      2) Tokenize (path segments, query values, fragment) and score each token
         based on presence of suspicious patterns. Flag when score crosses
         thresholds.

    This function is written to be fast in the common case and conservative
    about false positives.
    """
    if not url:
        return False

    # 1) quick safe path (short-circuits most URLs)
    if is_safe_url(url):
        return False

    # 2) gather tokens for analysis
    tokens = _gather_tokens(url)

    # defensive: if no tokens (weird url), inspect the raw decoded url once
    if not tokens:
        try:
            tokens = [unquote_plus(url[:MAX_TOKEN_LENGTH])]
        except Exception:
            tokens = [url[:MAX_TOKEN_LENGTH]]

    total_score = 0

    for token in tokens:
        token_score = 0
        # immediate short-circuit: very suspicious constructs
        if _UNION_SELECT_RE.search(token) or _STACKED_QUERY_RE.search(token):
            return True

        # weighted pattern checks
        for regex, weight in _PATTERNS_WEIGHTS:
            if regex.search(token):
                token_score += weight
                # small optimization: if token_score large enough, flag immediately
                if token_score >= PER_TOKEN_FLAG:
                    return True

        total_score += token_score

        # small early exit if total score already crosses global threshold
        if total_score >= SCORE_THRESHOLD:
            return True

    # final decision: high total score => suspicious
    return total_score >= SCORE_THRESHOLD
