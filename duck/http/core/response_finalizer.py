"""
Module containing ResponseFinalizer class focusing on putting on the final touches to the response.

The final touches include:
- Content compression.
- Content length calculation and insertion.
- Content encoding determination and insertion.
- etc.
"""

import io

from inspect import isasyncgen
from typing import (
    Dict,
    Callable,
    Optional,
)
from duck.http.content import COMPRESS_STREAMING_RESPONSES
from duck.http.request import HttpRequest
from duck.http.response import (
    HttpResponse,
    LazyHttpResponse,
    ComponentResponse,
    StreamingHttpResponse,
    StreamingRangeHttpResponse,
    HttpRangeNotSatisfiableResponse,
)
from duck.logging.logger import handle_exception as log_failsafe
from duck.settings import SETTINGS
from duck.utils.dateutils import gmt_date
from duck.csp import csp_nonce, csp_nonce_flag
from duck.shortcuts import (
    replace_response,
    make_response,
    to_response,
    content_replace,
    streaming_content_replace,
)


# Custom templates for predefined responses
# This is a mapping of status codes to a response generating callable
CUSTOM_TEMPLATES: Dict[int, Callable] = SETTINGS["CUSTOM_TEMPLATES"] or {}

if SETTINGS["ENABLE_HTTPS"]:
    SECURITY_HEADERS = SETTINGS["SSL_SECURITY_HEADERS"]
else:
    SECURITY_HEADERS = SETTINGS["SECURITY_HEADERS"]


def set_compressable_iter_content(response):
    """
    Modifies the response `iter_content` methods with new functions to compress data as were are iterating.
    
    Note:
    - Only use this function if response data is compressable. 
    - This function modifies both sync and async version of iter_content, i.e.
           `iter_content` and `async_iter_content`.
    """
    from duck.http.content import (
        COMPRESSION_ENCODING,
        COMPRESSION_LEVEL,
        COMPRESSION_MIMETYPES,
     )
    
    content_type = response.get_header("content-type", "")
    
    def iter_and_compress():
        """
        Compress content as we are iterating.
        """
        for chunk in response.super_iter_content():
            if not chunk:
                continue  # Skip empty or None chunks
            
            # Create a fresh compression wrapper or content object per chunk
            content_obj = response.content_obj.__class__()  # Clone a fresh object
            content_obj.set_content(chunk, content_type=content_type)
            content_obj.compression_level = COMPRESSION_LEVEL
            content_obj.compression_min_size = 0
            content_obj.compression_max_size = len(chunk) + 1
            content_obj.compression_mimetypes = COMPRESSION_MIMETYPES
            _ = content_obj.compress(COMPRESSION_ENCODING)
            compressed_data = content_obj.data
            
            yield compressed_data

    async def async_iter_and_compress():
        """
        Compress content as we iterate towards it, one chunk at a time.
        """
        content = response.super_async_iter_content()
                
        if not isasyncgen(content):
            # The content is not an async generator so lets await the coroutine
            content = await content
            
            if not isasyncgen(content):
                for chunk in content:
                    if not chunk:
                        continue  # Skip empty or None chunks
                        
                    # Create a fresh compression wrapper or content object per chunk
                    content_obj = response.content_obj.__class__()  # Clone a fresh object
                    content_obj.set_content(chunk, content_type=content_type)
                    content_obj.compression_level = COMPRESSION_LEVEL
                    content_obj.compression_min_size = 0
                    content_obj.compression_max_size = len(chunk) + 1
                    content_obj.compression_mimetypes = COMPRESSION_MIMETYPES
                    _ = content_obj.compress(COMPRESSION_ENCODING)
                    compressed_data = content_obj.data
                    
                    yield compressed_data
                 
            else:
                async for chunk in content:
                    if not chunk:
                        continue  # Skip empty or None chunks
                        
                    # Create a fresh compression wrapper or content object per chunk
                    content_obj = response.content_obj.__class__()  # Clone a fresh object
                    content_obj.set_content(chunk, content_type=content_type)
                    content_obj.compression_level = COMPRESSION_LEVEL
                    content_obj.compression_min_size = 0
                    content_obj.compression_max_size = len(chunk) + 1
                    content_obj.compression_mimetypes = COMPRESSION_MIMETYPES
                    _ = content_obj.compress(COMPRESSION_ENCODING)
                    compressed_data = content_obj.data
                         
                    yield compressed_data

    # Before assigning check if the old methods are not already set to these above functions
    old_iter_content_qualname = response.iter_content.__qualname__
    old_async_iter_content_qualname = response.async_iter_content.__qualname__
    
    iter_and_compress_qualname = iter_and_compress.__qualname__
    async_iter_and_compress_qualname = async_iter_and_compress.__qualname__
    
    if old_iter_content_qualname != iter_and_compress_qualname:
        response.super_iter_content = response.iter_content
        response.iter_content = iter_and_compress
    
    if old_async_iter_content_qualname != async_iter_and_compress_qualname:
        response.super_async_iter_content = response.async_iter_content
        response.async_iter_content = async_iter_and_compress
             

class ResponseFinalizer:
    """
    ResponseFinalizer class focusing on putting on the final touches to the response.
    """

    @log_failsafe
    def do_set_fixed_headers(self, response, request) -> None:
        """
        Sets fixed headers from settings, i.e. extra headers, cors headers and security headers.
        """
        extra = SETTINGS["EXTRA_HEADERS"] or {}
        cors = SETTINGS["CORS_HEADERS"] or {}
        security = SECURITY_HEADERS or {}
        
        for h, v in {**security, **cors,  **extra}.items():
            response.set_header_if_absent(h, v)
        
        # Set CSP header
        if request and SETTINGS["ENABLE_HEADERS_SECURITY_POLICY"]:
            csp_directives = SETTINGS['CSP_TRUSTED_SOURCES']
            nonce = csp_nonce(request)
            
            if csp_directives:
                csp_parts = []
                
                for directive, sources in csp_directives.items():
                    if not sources:
                        continue
                    # Build each source string
                    source_parts = [
                        f"'nonce-{nonce}'" if i == csp_nonce_flag else i
                        for i in sources
                    ]
                    csp_parts.append(f"{directive} {' '.join(source_parts)}")
                
                # Generate the CSP value.
                csp_value = "; ".join(csp_parts) + ";"
                
                # Finally, set the header
                response.set_header_if_absent("Content-Security-Policy", csp_value)

    @log_failsafe
    def do_set_connection_mode(self, response, request) -> None:
        """
        Sets the response connection mode according to the HTTP version,
        client request, and server connection-mode configuration.
    
        HTTP/1.1 uses persistent connections by default, while HTTP/1.0
        requires an explicit ``Connection: keep-alive`` header.
    
        The server's configured connection mode can restrict persistent
        connections, but cannot force a client to keep a connection open
        when the client explicitly requests ``Connection: close``.
    
        Args:
            response: HTTP response whose Connection header should be set.
            request: HTTP request associated with the response.
        """
        server_mode = SETTINGS["CONNECTION_MODE"].lower()
        
        if not request:
            response.set_header("Connection", "close")
            return
    
        # Initialize some variables. 
        request_mode = request.connection
        http_version = request.http_version
    
        # The client explicitly requested that the connection be closed.
        if request_mode == "close":
            connection_mode = "close"
    
        # The server does not permit persistent connections.
        elif server_mode == "close":
            connection_mode = "close"
    
        # HTTP/1.1 connections are persistent by default.
        elif http_version == "HTTP/1.1":
            connection_mode = "keep-alive"
    
        # HTTP/1.0 requires an explicit keep-alive request.
        elif http_version == "HTTP/1.0":
            connection_mode = "keep-alive" if request_mode == "keep-alive" else "close"
            
        # Unknown HTTP versions fail closed.
        else:
            connection_mode = "close"
    
        # Explicitly override any user-supplied Connection header.
        response.set_header("Connection", connection_mode)
        
    @log_failsafe
    def do_set_extra_headers(self, response, request) -> None:
        """
        Sets extra headers like Date, Cache-Control and other internal headers.
        """
        from duck.html.components.core.system import LivelyComponentSystem
        from duck.logging import logger
        
        response.set_header_if_absent("date", gmt_date())
        
        if not SETTINGS['DEBUG']:
            default_cache_control = SECURITY_HEADERS.get("Cache-Control")
            
            # Set the default cache control
            response.set_header_if_absent("cache-control", default_cache_control)
        else:
            # Set the no-cache control
            response.set_header("cache-control", "no-cache")
        
        # Set lively owner if Lively component system active
        if request and LivelyComponentSystem.is_active():
            lively_owner_token = request.META.get(LivelyComponentSystem.OWNER_TOKEN_REQUEST_KEY)
            
            if lively_owner_token is not None:
                response.set_cookie(
                    LivelyComponentSystem.OWNER_COOKIE_KEY,
                    lively_owner_token,
                    httponly=True,
                    samesite="Strict",
                    max_age=LivelyComponentSystem.OWNER_TOKEN_MAX_AGE,
                )
            
    @log_failsafe
    def do_content_compression(self, response, request) -> None:
        """
        Compresses the content if the client supports it and
        if the content is not a streaming response. (if necessary).
        """
        from duck.http.content import (
            COMPRESSION_ENCODING,
            COMPRESSION_LEVEL,
            COMPRESSION_MAX_SIZE,
            COMPRESSION_MIN_SIZE,
            CONTENT_COMPRESSION,
            COMPRESSION_MIMETYPES,
        )
        
        accept_encoding = request.get_header("accept-encoding", "").lower() if request else ""
        supported_encodings = ["gzip", "deflate", "br", "identity"]
        
        if CONTENT_COMPRESSION.get("vary_on", False):
            # Patch vary headers
            existing_vary_headers = response.get_header("Vary") or ""
            
            if existing_vary_headers:
                existing_vary_headers += ", "
            
            # Explitly set vary header
            response.set_header("Vary", existing_vary_headers + "Accept-Encoding",)
            
        if (not request or not SETTINGS["ENABLE_CONTENT_COMPRESSION"]
            or COMPRESSION_ENCODING not in accept_encoding
            or COMPRESSION_ENCODING not in supported_encodings
            or response.content_obj.correct_encoding() != "identity"
        ):
            # No need to compress content if correct_encoding is not identity (might already be compressed)
            response.set_header("Content-Encoding", response.content_obj.correct_encoding())
            return

        if not isinstance(response, StreamingHttpResponse):
            # Normal HTTP response here.
            response.content_obj.compression_level = COMPRESSION_LEVEL
            response.content_obj.compression_min_size = COMPRESSION_MIN_SIZE
            response.content_obj.compression_max_size = COMPRESSION_MAX_SIZE
            response.content_obj.compression_mimetypes = COMPRESSION_MIMETYPES
            
            # Compress the content
            compressed = response.content_obj.compress(COMPRESSION_ENCODING)
            
            if compressed:
                response.set_header("Content-Encoding", response.content_obj.encoding)
            else:
                response.set_header("Content-Encoding", response.content_obj.correct_encoding())
            
        else:
            # Streaming HTTP response here.
            if not COMPRESS_STREAMING_RESPONSES:
                # Compressing streaming responses disallowed
                return
            
            # A byte-range response's offsets refer to the representation
            # being requested, so it must not be transformed WHILE it is
            # actually serving a partial range (206). If If-Range failed
            # validation and do_set_streaming_range downgraded this to a
            # full 200, it's safe to compress like any other streaming
            # response — checking status_code rather than isinstance()
            # avoids permanently disabling compression on a
            # StreamingRangeHttpResponse instance that is no longer
            # actually serving a range.
            if isinstance(response, StreamingRangeHttpResponse) and response.status_code == 206:
                response.set_header("Content-Encoding", "identity")
                return
        
            # Get content type
            content_type = response.get_header("content-type", "")
            
            # Initialize total stream size
            total_stream_size = None
            
            if hasattr(response, "stream") and hasattr(response.stream, "tell") and hasattr(response.stream, "seek"):
                # Get the stream size
                current_position = response.stream.tell()
                
                try:
                    response.stream.seek(0, io.SEEK_END)
                    total_stream_size = response.stream.tell()
                finally:
                    response.stream.seek(current_position)
                    
            else:
                return # Quit with the compression, no stream!
                    
            if total_stream_size is not None:
                if total_stream_size < COMPRESSION_MIN_SIZE or total_stream_size > COMPRESSION_MAX_SIZE :
                    # Total stream size if beyond or below compression limits
                    return
            else:
                # Don't compress anything with unknown size
                return
            
            # Don't compress HttpProxyResponse instances as doing response.iter_content() for checking if data is compressable
            # may make content data inconsistent.
            
            compressable = False # Whether the content is compressable by trying to compress the first chunk
            
            # Check if content is compressable.
            for initial_chunk in response.iter_content():
                if initial_chunk:
                    # Create a fresh compression wrapper or content object per chunk
                    chunk = initial_chunk[:8] # Check compression using first 8 bytes to avoid performance degradation
                    content_obj = response.content_obj.__class__()  # Clone a fresh object
                    content_obj.set_content(chunk, content_type=content_type)
                    content_obj.compression_level = COMPRESSION_LEVEL
                    content_obj.compression_min_size = 0
                    content_obj.compression_max_size = 8
                    content_obj.compression_mimetypes = COMPRESSION_MIMETYPES
                    compressable = content_obj.compress(COMPRESSION_ENCODING) # sets if content is compressable
                break
                    
            if response.get_header("content-encoding", "identity") == "identity" and compressable:
                # Assume compression will not fail, this is is a bit dangerous if compression fails as response might include 
                # unmatching invalid content content encoding
                response.set_header("Content-Encoding", COMPRESSION_ENCODING)
                
                # Modify response iter_content & async_iter_content to new funcs which
                # compress data as we are iterating over it.
                set_compressable_iter_content(response)
                
    @log_failsafe
    def do_set_content_headers(self, response, request) -> None:
        """
        Sets the appropriate content headers like `Content-Type`, `Content-Encoding` & `Content-Length` if not set.
        
        Notes:
        - If response is an instance of `StreamingHttpResponse`, the `Content-Length` header is removed as a safe measure. The size
            of the response content can become unpredictable especially when data is compressed as it is being sent.
        """
        from duck.http.core.proxyhandler import HttpProxyResponse
        
        # Set some content headers if not set.
        content_length = response.get_header("content-length")
        content_encoding = response.get_header("content-encoding")
        content_type = response.get_header("content-type")
        
        if not isinstance(response, StreamingHttpResponse):
            # Normal HTTP response here
            # Set content-length if not set.
            if not content_length:
                response.set_header("content-length", response.content_length)
            
            # Set content encoding if not set.
            if not content_encoding:
                response.set_header("content-encoding", response.content_encoding or response.content_obj.correct_encoding())
            
            # Set content-type if not set.
            if not content_type:
                # Set the predicted content-type from the content object.
                response.set_header('content-type', response.content_type)
        else:
            # Streaming HTTP response here.
            # Remove content-length for streaming responses,
            # the response content may be unpredictable. This is a safe measure.
            if content_length:
                # Only ProxyResponse instance is an exception.
                if not isinstance(response, HttpProxyResponse):
                    response.delete_header("content-length")
            
            # Set the content-encoding if not set.
            if not content_encoding:
                response.set_header("content-encoding", "identity") # default encoding.
             
            # Set the content-type if not set.
            if not content_type:
                content_type = response.content_obj.content_type
                response.set_header("content-type", content_type)

    @staticmethod
    def is_range_valid(
        request: HttpRequest,
        etag: Optional[str],
        last_modified: Optional[str],
    ) -> bool:
        """
        Determines whether a `Range` request should be honored, per `If-Range`.

        `If-Range` (RFC 7233 §3.2) lets a client say "give me just this byte
        range, but only if the resource I have cached is still exactly this
        version — otherwise send me the whole thing." If no `If-Range` header
        is present, `Range` is always honored (this returns `True`).

        Unlike `If-None-Match`, `If-Range` requires a **strong** comparison —
        a weak validator (`W/"..."`) never satisfies it, even if the
        underlying value is identical, since a weak ETag only promises
        semantic equivalence, not byte-for-byte identity, which is unsafe to
        splice a partial range into. If the header value doesn't look like
        an ETag (no surrounding quotes), it's treated as an HTTP-date and
        compared against `last_modified` instead.

        Args:
            request: The incoming request, inspected for the `If-Range` header.
            etag: The response's current (strong) ETag, or `None`.
            last_modified: The response's current Last-Modified value
                (HTTP-date string), or `None`. Used only when `If-Range`
                carries a date rather than an ETag.

        Returns:
            `True` if `Range` should be honored (no `If-Range` sent, or it
            matches the current strong validator). `False` if the resource
            has changed and the full body should be sent instead.
        """
        if_range = request.get_header("If-Range")

        if if_range is None:
            # No If-Range sent — Range is unconditional, always honor it.
            return True

        if_range = if_range.strip()

        # A weak validator can never satisfy If-Range, per RFC 7233 §3.2 —
        # fail safe by treating it as non-matching (serve full body).
        if if_range.startswith("W/"):
            return False

        # ETag-shaped value (quoted) — strong comparison against our ETag.
        # Our own ETag is always strong (never W/-prefixed), so a direct
        # string match is correct here.
        if if_range.startswith('"'):
            return etag is not None and if_range == etag

        # Otherwise treat it as an HTTP-date and compare against Last-Modified.
        return last_modified is not None and if_range == last_modified

    @log_failsafe
    def do_set_streaming_range(self, response, request):
        """
        Set streaming range attributes on StreamingRangeHttpResponse. 
        This method parses the 'Range' header from the request and sets the 
        start and end positions for partial content streaming.

        If an `If-Range` header is present and does not match the response's
        current strong validator (`ETag`, falling back to `Last-Modified`),
        the `Range` header is ignored entirely and the full resource is
        served as `200`, since splicing a partial range against a changed
        resource would silently corrupt the client's reconstructed file.
    
        Args:
            response (StreamingRangeHttpResponse): The response object to set streaming range on.
            request (HttpRequest): The incoming HTTP request containing the 'Range' header.
    
        Raises:
            ValueError: If the 'Range' header is malformed or invalid.
        """
        if not request:
            return  # If no request is provided, exit early.
         
        if not isinstance(response, StreamingRangeHttpResponse):
            return # Response is incompatible.
        
        # Set the Range header.
        range_header = request.get_header('Range')
        
        # Treat the request as rangeless if no Range was sent, or if an
        # If-Range precondition was sent but failed to match — in both
        # cases we fall through to serving the full 200 body.
        honor_range = bool(range_header) and self.is_range_valid(
            request, response.etag, response.last_modified
        )
        
        if not honor_range:
            if response.status_code == 206:
                response.payload_obj.parse_status(200) # modify the response to correct status
                response.clear_content_range_headers() # clear range headers
            return  # No Range header, or If-Range failed — full body, no content range headers.
        
        # Parse Range header.
        if response.status_code == 200:
            # Invalid status (200 OK) instead of (206 Partial Content)
            response.payload_obj.parse_status(206) # modify the response to correct status
        
        try:
            # Extract start and end positions from the Range header
            # Note: Use response.start_pos & end_pos rather than start, end as they are the most recent offsets.
            start, end = StreamingRangeHttpResponse.extract_range(range_header)
            
            # Set the start and end positions on the response object
            response.parse_range(start, end) # set content range headers (if applicable)
            
        except ValueError as e:
            # Replace response data
            new_response = make_response(
                HttpRangeNotSatisfiableResponse,
                extra_context={"exception": e},
            )
                
            # Replace response with new data
            replace_response(response, new_response)
            
            # Finalize response again as it has new values
            # Set do_set_streaming_range & do_content_compression to False to avoid max recursion error
            self.finalize_response(
                response,
                request,
                do_set_streaming_range=False,
                do_content_compression=False,
            )
        
    @log_failsafe
    def do_request_response_transformation(self, response: HttpResponse, request: HttpRequest) -> bool:
        """
        Transforms the response object by applying request- and response-based modifications.
        
        This includes, but is not limited to, header changes and body alterations.
    
        Behavior Examples:
        - If the request method is `HEAD`, the response body is replaced with empty bytes.
        - If a matching template is found in the `CUSTOM_TEMPLATES` configuration, the entire response may be replaced.
        - If the response is downgraded to `304 Not Modified`, further response processing (e.g. body
          generation, streaming setup) should be skipped by the caller.
    
        Args:
            response (HttpResponse): The original response to be transformed.
            request (HttpRequest): The incoming HTTP request associated with the response.

        Returns:
            bool: `True` if the caller should continue normal response processing,
                `False` if processing should stop here (e.g. the response was
                downgraded to `304 Not Modified` and has nothing further to do).
        """
        if response:
            # Handle 304 here.
            if request:
                last_modified = response.last_modified
                etag = response.etag

                # Conditional revalidation only applies to safe methods with a
                # cacheable representation (200/206) and a validator to check against.
                if (
                    request.method in ("GET", "HEAD")
                    and response.status_code in (200, 206)
                    and (etag is not None or last_modified is not None)
                    and self.is_not_modified(request, etag, last_modified)
                ):
                    # Downgrade to 304 response
                    self.downgrade_to_not_modified(response)
                    
                    # Nothing left to do — no body, no custom template, no further transforms.
                    return False

                # HEAD never carries a body, regardless of what produced it.
                if request.method == "HEAD":
                    if isinstance(response, StreamingHttpResponse):
                        streaming_content_replace(response, stream=[b""])
                    else:
                        content_replace(response, b"", new_content_type="use_existing")
                        
            # Handle custom status code templates 
            if response.status_code in CUSTOM_TEMPLATES:
                response_callable = CUSTOM_TEMPLATES[response.status_code]
                
                if not callable(response_callable):
                    raise TypeError(f"Callable required for custom template corresponding to status code of '{response.status_code}' ")
                
                # Parse parameters and obtain the custom template response.
                new_response = response_callable(current_response=response, request=request)
                
                try:
                    new_response = to_response(new_response) # convert or check the validity of the custom response.
                except TypeError:
                    # The value returned by response_generating_callable is not valid
                    raise TypeError(f"Invalid data returned by the custom template callable corresponding to status code '{response.status_code}' ")
                
                # Replace response with new data
                replace_response(response, new_response)

        # Normal path — caller should continue processing this response.
        return True

    @staticmethod
    def is_not_modified(request: HttpRequest, etag: Optional[str], last_modified: Optional[str]) -> bool:
        """
        Determines whether a request's conditional headers match the response's validators.

        `If-None-Match` (ETag) is authoritative and checked first, since it is
        precise to the nanosecond via `FileIOStream.etag`. `If-Modified-Since`
        is only consulted as a fallback when the client sent no `If-None-Match`
        — it is never used to override a mismatching ETag, and `Last-Modified`
        is never read from response headers here since it is intentionally
        never emitted (see `HttpResponseBase.finalize_headers`); this compares
        against the response's internal `last_modified` value instead.

        Args:
            request: The incoming request, inspected for `If-None-Match` / `If-Modified-Since` headers.
            etag: The response's current ETag, or `None`.
            last_modified: The response's current Last-Modified value (HTTP-date string), or `None`.

        Returns:
            `True` if the client's cached copy is still valid and a `304`
            should be sent instead of the body.
        """
        
        def strip_weak_prefix(etag_value: str) -> str:
            """
            Strips the `W/` weak-validator prefix from an ETag value, if present.
    
            Args:
                etag_value: A raw ETag token, e.g. `'"abc-123"'` or `'W/"abc-123"'`.
    
            Returns:
                The ETag with any leading `W/` removed, e.g. `'"abc-123"'`.
            """
            if etag_value.startswith("W/"):
                return etag_value[2:]
            return etag_value
        
        if_none_match = request.headers.get("If-None-Match")
        
        if if_none_match is not None:
            if etag is None:
                return False
            
            # Support comma-separated lists and the "*" wildcard per RFC 7232 §3.2.
            if if_none_match.strip() == "*":
                return True
            
            # Create candidates
            candidates = {strip_weak_prefix(tag.strip()) for tag in if_none_match.split(",")}
            
            # Check if etag is in candidates
            return etag in candidates

        # No ETag sent by the client — fall back to Last-Modified, if we
        # have one to compare against.
        if_modified_since = request.headers.get("If-Modified-Since")
        
        if if_modified_since is not None and last_modified is not None:
            return if_modified_since == last_modified

        return False

    @staticmethod
    def downgrade_to_not_modified(response: HttpResponse) -> None:
        """
        Converts a fully-built 200/206 response in place into a 304.

        Strips the body and any representation-specific headers (since a
        `304` has no body), while preserving the validators
        (`ETag` is kept; `Last-Modified` remains unemitted as always) so
        the client can keep using its cached copy.

        Args:
            response: The response to downgrade. Mutated in place.
        """
        response.status_code = 304
        
        if isinstance(response, StreamingHttpResponse):
            streaming_content_replace(response, stream=[b""])
        else:
            content_replace(response, b"", new_content_type="use_existing")
        
        # A 304 has no representation, so headers describing the body
        # (as opposed to the resource) do not apply.
        for header in ("Content-Length", "Content-Type", "Content-Range", "Content-Encoding"):
            response.delete_header(header, failsafe=True)

        # Re-apply validators (ETag only — Last-Modified stays header-less
        # by policy) now that headers were cleared above.
        response.set_conditional_headers()
        
    def finalize_response(
        self,
        response: HttpResponse,
        request: HttpRequest,
        do_set_streaming_range: bool = True,
        do_content_compression: bool = True,
    ):
        """
        Puts the final touches to the response.
        """
        if isinstance(response, LazyHttpResponse):
            # Load if response is lazy
            response._load()
            
        # All of the following method calls are failsafe meaning failure of any method
        # will not affect the execution of other methods, thus an error encountered will be
        # logged appropriately. Decorator responsible: @log_failsafe
        continue_processing = self.do_request_response_transformation(response, request) 
        
        # Continue with next steps
        self.do_set_fixed_headers(response, request)
        self.do_set_connection_mode(response, request)
        self.do_set_extra_headers(response, request)
        
        if not continue_processing:
            # Stop further processing at this point - we would have done this immediately
            # after do_request_response_transformation but we want other headers to be set.
            return
            
        if do_set_streaming_range:
            self.do_set_streaming_range(response, request)
        
        # Do content compression in the end.
        if do_content_compression:
            self.do_content_compression(response, request)
        
        # Lastly review content headers.
        self.do_set_content_headers(response, request)


class AsyncResponseFinalizer(ResponseFinalizer):
    """
    Asynchronous ResponseFinalizer class focusing on putting on the final touches to the response.
    """
    
    @log_failsafe
    async def do_content_compression(self, response, request) -> None:
        """
        Compresses the content if the client supports it and
        if the content is not a streaming response. (if necessary).
        """
        from duck.http.content import (
            COMPRESSION_ENCODING,
            COMPRESSION_LEVEL,
            COMPRESSION_MAX_SIZE,
            COMPRESSION_MIN_SIZE,
            CONTENT_COMPRESSION,
            COMPRESSION_MIMETYPES,
        )
        
        accept_encoding = request.get_header("accept-encoding", "").lower() if request else ""
        supported_encodings = ["gzip", "deflate", "br", "identity"]
        
        if CONTENT_COMPRESSION.get("vary_on", False):
            # Patch vary headers
            existing_vary_headers = response.get_header("Vary") or ""
            
            if existing_vary_headers:
                existing_vary_headers += ", "
            
            # Set vary header explicitly
            response.set_header("Vary", existing_vary_headers + "Accept-Encoding")
            
        if (not request or not SETTINGS["ENABLE_CONTENT_COMPRESSION"]
            or COMPRESSION_ENCODING not in accept_encoding
            or COMPRESSION_ENCODING not in supported_encodings
            or response.content_obj.correct_encoding() != "identity"
        ):
            # No need to compress content if correct_encoding is not identity (might already be compressed)
            response.set_header("Content-Encoding", response.content_obj.correct_encoding())
            return

        if not isinstance(response, StreamingHttpResponse):
            # Normal HTTP response here.
            response.content_obj.compression_level = COMPRESSION_LEVEL
            response.content_obj.compression_min_size = COMPRESSION_MIN_SIZE
            response.content_obj.compression_max_size = COMPRESSION_MAX_SIZE
            response.content_obj.compression_mimetypes = COMPRESSION_MIMETYPES
            compressed = response.content_obj.compress(COMPRESSION_ENCODING)
            
            if compressed:
                response.set_header("Content-Encoding", response.content_obj.encoding)
            else:
                response.set_header("Content-Encoding", response.content_obj.correct_encoding())
                
        else:
            # Streaming HTTP response here.
            if not COMPRESS_STREAMING_RESPONSES:
                # Compressing streaming responses disallowed
                return
            
            # A byte-range response's offsets refer to the representation
            # being requested, so it must not be transformed WHILE it is
            # actually serving a partial range (206). If If-Range failed
            # validation and do_set_streaming_range downgraded this to a
            # full 200, it's safe to compress like any other streaming
            # response — checking status_code rather than isinstance()
            # avoids permanently disabling compression on a
            # StreamingRangeHttpResponse instance that is no longer
            # actually serving a range.
            if isinstance(response, StreamingRangeHttpResponse) and response.status_code == 206:
                response.set_header("Content-Encoding", "identity")
                return
                    
            content_type = response.get_header("content-type", "")
            total_stream_size = None
            
            if hasattr(response, "stream") and hasattr(response.stream, "tell") and hasattr(response.stream, "seek"):
                # Get the stream size
                current_position = response.stream.tell()
                
                try:
                    response.stream.seek(0, io.SEEK_END)
                    total_stream_size = response.stream.tell()
                finally:
                    response.stream.seek(current_position)
    
            else:
                if not isinstance(response, ComponentResponse):
                    return # Quit with the compression, no stream!
                    
            if total_stream_size is not None:
                if total_stream_size < COMPRESSION_MIN_SIZE or total_stream_size > COMPRESSION_MAX_SIZE :
                    # Total stream size if beyond or below compression limits
                    return
            else:
                # Don't compress anything with unknown size
                return
            
            # Don't compress HttpProxyResponse instances as doing response.iter_content() for checking if data is compressable
            # may make content data inconsistent.
              
            compressable = False # Whether the content is compressable by trying to compress the first chunk
            content = response.async_iter_content()
            
            if not isasyncgen(content):
                # The content is not an async generator so lets await it.
                content = await content
            
            if not isasyncgen(content):
                for chunk in content:
                    if chunk:
                        # Create a fresh compression wrapper or content object per chunk
                        chunk = chunk[:8] # Check compression using first 8 bytes to avoid performance degradation
                        content_obj = response.content_obj.__class__()  # Clone a fresh object
                        content_obj.set_content(chunk, content_type=content_type)
                        content_obj.compression_level = COMPRESSION_LEVEL
                        content_obj.compression_min_size = 0
                        content_obj.compression_max_size = 8
                        content_obj.compression_mimetypes = COMPRESSION_MIMETYPES
                        compressable = content_obj.compress(COMPRESSION_ENCODING) # sets if content is compressable
                    break
            
            else:
                async for chunk in content:
                    if chunk:
                        # Create a fresh compression wrapper or content object per chunk
                        chunk = chunk[:8] # Check compression using first 8 bytes to avoid performance degradationt
                        content_obj = response.content_obj.__class__()  # Clone a fresh object
                        content_obj.set_content(chunk, content_type=content_type)
                        content_obj.compression_level = COMPRESSION_LEVEL
                        content_obj.compression_min_size = 0
                        content_obj.compression_max_size = 8
                        content_obj.compression_mimetypes = COMPRESSION_MIMETYPES
                        compressable = content_obj.compress(COMPRESSION_ENCODING) # sets if content is compressable
                    break
                    
            if response.get_header("content-encoding", "identity") == "identity" and compressable:
                # Assume compression will not fail, this is is a bit dangerous if compression fails as response might include 
                # unmatching invalid content content encoding
                response.set_header("Content-Encoding", COMPRESSION_ENCODING)
                
                # Modify response iter_content & async_iter_content to new funcs which
                # compress data as we are iterating over it.
                set_compressable_iter_content(response)
                
    @log_failsafe
    async def do_set_streaming_range(self, response, request):
        """
        Set streaming range attributes on StreamingRangeHttpResponse. 
        This method parses the 'Range' header from the request and sets the 
        start and end positions for partial content streaming.

        If an `If-Range` header is present and does not match the response's
        current strong validator (`ETag`, falling back to `Last-Modified`),
        the `Range` header is ignored entirely and the full resource is
        served as `200`, since splicing a partial range against a changed
        resource would silently corrupt the client's reconstructed file.
    
        Args:
            response (StreamingRangeHttpResponse): The response object to set streaming range on.
            request (HttpRequest): The incoming HTTP request containing the 'Range' header.
    
        Raises:
            ValueError: If the 'Range' header is malformed or invalid.
        """
        if not request:
            return  # If no request is provided, exit early.
         
        if not isinstance(response, StreamingRangeHttpResponse):
            return
        
        # Set the Range header.
        range_header = request.get_header('Range')
        
        # Treat the request as rangeless if no Range was sent, or if an
        # If-Range precondition was sent but failed to match — in both
        # cases we fall through to serving the full 200 body.
        honor_range = bool(range_header) and self.is_range_valid(
            request, response.etag, response.last_modified
        )
        
        if not honor_range:
            if response.status_code == 206:
                response.payload_obj.parse_status(200) # modify the response to correct status
                response.clear_content_range_headers() # clear range headers
            return  # No Range header, or If-Range failed — full body, no content range headers.
        
        # Parse Range header.
        if response.status_code == 200:
            # Invalid status (200 OK) instead of (206 Partial Content)
            response.payload_obj.parse_status(206) # modify the response to correct status
        
        try:
            # Extract start and end positions from the Range header
            # Note: Use response.start_pos & end_pos rather than start, end as they are the most recent offsets.
            start, end = StreamingRangeHttpResponse.extract_range(range_header)
            
            # Set the start and end positions on the response object
            response.parse_range(start, end) # Set content range headers (if applicable)
            
        except ValueError as e:
            # Replace response data
            new_response = make_response(
                HttpRangeNotSatisfiableResponse,
                extra_context={"exception": e},
            )
            
            # Replace response with new data
            replace_response(response, new_response)
            
            # Finalize response again as it has new values
            # Set do_set_streaming_range & do_content_compression to False to avoid max recursion error
            await self.finalize_response(
                response,
                request,
                do_set_streaming_range=False,
                do_content_compression=False,
            )
        
    async def finalize_response(
        self,
        response: HttpResponse,
        request: HttpRequest,
        do_set_streaming_range: bool = True,
        do_content_compression: bool = True,
    ):
        """
        Puts the final touches to the response.
        """
        if isinstance(response, LazyHttpResponse):
            # Load if response is lazy
            await response._async_load()
            
        # All of the following method calls are failsafe meaning failure of any method
        # will not affect the execution of other methods, thus an error encountered will be
        # logged appropriately. Decorator responsible: @log_failsafe
        # NOTE: do_request_response_transformation already handles 304 downgrading,
        # HEAD body-stripping, and custom status-code templates — kept in sync with
        # the sync class rather than duplicating HEAD-handling here.
        continue_processing = self.do_request_response_transformation(response, request)
        
        self.do_set_fixed_headers(response, request)
        self.do_set_connection_mode(response, request)
        self.do_set_extra_headers(response, request)
        
        if not continue_processing:
            # Stop further processing at this point - we would have done this immediately
            # after do_request_response_transformation but we want other headers to be set.
            return
            
        if do_set_streaming_range:
            # This implementation needs to be awaited, it uses some asynchronous implementations.    
            await self.do_set_streaming_range(response, request)
        
        # Do content compression in the end.
        if do_content_compression:
            await self.do_content_compression(response, request)
        
        # Lastly review content headers.
        self.do_set_content_headers(response, request)        


# Set & initialize response finalizers
response_finalizer = ResponseFinalizer()
async_response_finalizer = AsyncResponseFinalizer()
