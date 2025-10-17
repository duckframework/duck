"""
Module containing ResponseFinalizer class focusing on putting on the final touches to the response.

The final touches include:
- Content compression.
- Content length calculation and insertion.
- Content encoding determination and insertion.
- etc.
"""
import re
import io
import fnmatch

from inspect import isasyncgen
from typing import (
    Dict,
    Optional,
    Callable,
)
from duck.http.content import COMPRESS_STREAMING_RESPONSES
from duck.http.request import HttpRequest
from duck.http.response import (
    HttpResponse,
    FileResponse,
    StreamingHttpResponse,
    StreamingRangeHttpResponse,
    HttpRangeNotSatisfiableResponse,
)
from duck.logging import logger
from duck.logging.logger import (
    handle_exception as log_failsafe,
)
from duck.settings import SETTINGS
from duck.utils.dateutils import gmt_date
from duck.utils.asyncio import in_async_context
from duck.shortcuts import (
    replace_response,
    template_response,
    simple_response,
    to_response,
)
from duck.meta import Meta
from duck.csp import csp_nonce, csp_nonce_flag


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
        COMPRESSION_MAX_SIZE,
        COMPRESSION_MIN_SIZE,
        CONTENT_COMPRESSION,
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
            compressed = content_obj.compress(COMPRESSION_ENCODING)
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
                    compressed = content_obj.compress(COMPRESSION_ENCODING)
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
                    compressed = content_obj.compress(COMPRESSION_ENCODING)
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
            response.headers[h] = v
        
        # Set CSP header
        if request and SETTINGS["ENABLE_HEADERS_SECURITY_POLICY"]:
            csp_directives = SETTINGS['CSP_TRUSTED_SOURCES']
            nonce = csp_nonce(request)
            if csp_directives:
                # Build CSP header string
                csp_value = "; ".join(
                    f"{directive} {' '.join([f"'nonce-{nonce}'" if i == csp_nonce_flag else i for i in sources])}"
                    for directive, sources in csp_directives.items() if sources
                ) + ";"
                response.set_header("Content-Security-Policy", csp_value)
            
    @log_failsafe
    def do_set_connection_mode(self, response, request) -> None:
        """
        Sets the correct response connection mode, i.e. `keep-alive` or `close`.
        """
        connection_mode = None
        server_mode = SETTINGS["CONNECTION_MODE"].lower()

        if not request:
            response.set_header("Connection", "close")
            return

        if request.connection == server_mode:
            connection_mode = server_mode
        else:
            connection_mode = "close"
        response.set_header("Connection", connection_mode)

    @log_failsafe
    def do_set_extra_headers(self, response, request) -> None:
        """
        Sets last final extra headers like Date.
        """
        response.set_header("date", gmt_date())
        
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
            
            response.set_header(
                "Vary",
                existing_vary_headers + "Accept-Encoding",
            )
            
        if (not request or not SETTINGS["ENABLE_CONTENT_COMPRESSION"]
            or COMPRESSION_ENCODING not in accept_encoding
            or COMPRESSION_ENCODING not in supported_encodings
            or response.content_obj.correct_encoding() != "identity"
            ):
            # No need to compress content if correct_encoding is not identity (might already be compressed)
            response.set_header(
                "Content-Encoding",
                response.content_obj.correct_encoding(),
            )
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
                response.set_header(
                    "Content-Encoding",
                    response.content_obj.correct_encoding(),
                )
            
        else:
            # Streaming HTTP response here.
            if not COMPRESS_STREAMING_RESPONSES:
                # Compressing streaming responses disallowed
                return
            
             # Check if we are dealing with a StreamingRangeHttpResponse
            if isinstance(response, StreamingRangeHttpResponse):
                start_pos, end_pos = response.start_pos, response.end_pos
                content_size = end_pos - start_pos
                
                if not (content_size >= COMPRESSION_MIN_SIZE and content_size <= COMPRESSION_MAX_SIZE):
                    # Compression not applicable.
                    return
                    
            content_type = response.get_header("content-type", "")
            total_stream_size = None
            
            if hasattr(response, "stream") and hasattr(response.stream, "tell") and hasattr(response.stream, "seek"):
                response.stream.seek(0, io.SEEK_END) # seek to EOF
                total_stream_size = response.stream.tell()
            else:
                return # Quit with the compression
                    
            if total_stream_size is not None:
                if total_stream_size < COMPRESSION_MIN_SIZE or total_stream_size > COMPRESSION_MAX_SIZE :
                    # Total stream size if beyond or below compression limits
                    return
            else:
                return
            
            # Don't compress HttpProxyResponse instances as doing response.iter_content() for checking if data is compressable
            # may make content data inconsistent.
            
            compressable = False # Whether the content is compressable by trying to compress the first chunk
            
            # Check if content is compressable.
            for initial_chunk in response.iter_content():
                if initial_chunk:
                    # Create a fresh compression wrapper or content object per chunk
                    chunk = initial_chunk[:8] # Check compression using first 8 bytes to avoid performance degradationt
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
        from duck.http.content import COMPRESSION_ENCODING
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
                response.set_header("content-type", "application/octet-stream") # default content type for streaming responses.
                
    @log_failsafe
    def do_set_streaming_range(self, response, request):
        """
        Set streaming range attributes on StreamingRangeHttpResponse. 
        This method parses the 'Range' header from the request and sets the 
        start and end positions for partial content streaming.
    
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
        
        if not range_header:
            if isinstance(response, StreamingRangeHttpResponse):
                if response.status_code == 206:
                    response.payload_obj.parse_status(200) # modify the response to correct status
                    response.clear_content_range_headers() # clear range headers
            return  # If no Range header exists, no need to set content range headers.
        
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
            # replace response data
            new_response = None
            
            if SETTINGS["DEBUG"]:
                new_response = template_response(
                    HttpRangeNotSatisfiableResponse,
                    body=(
                        f"<p>Range is not satisfiable, could not resolve: {range_header}</p>"
                        f"<p>Exception: {e}</p>"
                    )
                )
            else:
                new_response = simple_response(HttpRangeNotSatisfiableResponse)
            
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
    def do_request_response_transformation(self, response: HttpResponse, request: HttpRequest):
        """
        Transforms the response object by applying request- and response-based modifications.
        
        This includes, but is not limited to, header changes and body alterations.
    
        Behavior Examples:
        - If the request method is `HEAD`, the response body is replaced with empty bytes.
        - If a matching template is found in the `CUSTOM_TEMPLATES` configuration, the entire response may be replaced.
    
        Args:
            response (HttpResponse): The original response to be transformed.
            request (HttpRequest): The incoming HTTP request associated with the response.
        """
        # Check if a custom template is configured for this response
        
        # Return the http response object.
        if request and str(request.method).upper() == "HEAD":
            # Reset content
            request.set_content(b"", auto_add_content_headers=True)
        
        if response:
            if response.status_code in CUSTOM_TEMPLATES:
                response_callable = CUSTOM_TEMPLATES[response.status_code]
                if not callable(response_callable):
                    raise TypeError(f"Callable required for custom template corresponding to status code of '{response.status_code}' ")
                
                # Parse parameters and obtain the custom template response.
                new_response = response_callable(
                    current_response=response,
                    request=request,
                )
                try:
                    new_response = to_response(new_response) # convert or check the validity of the custom response.
                except TypeError:
                    # The value returned by response_generating_callable is not valid
                    raise TypeError(f"Invalid data returned by the custom template callable corresponding to status code '{response.status_code}' ")
                
                # Replace response with new data
                replace_response(response, new_response)
        
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
        # All of the following method calls are failsafe meaning failure of any method
        # will not affect the execution of other methods, thus an error encountered will be
        # logged appropriately. Decorator responsible: @log_failsafe
        
        self.do_request_response_transformation(response, request) 
        self.do_set_fixed_headers(response, request)
        self.do_set_connection_mode(response, request)
        self.do_set_extra_headers(response, request)
            
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
            
            response.set_header(
                "Vary",
                existing_vary_headers + "Accept-Encoding",
            )
            
        if (not request or not SETTINGS["ENABLE_CONTENT_COMPRESSION"]
            or COMPRESSION_ENCODING not in accept_encoding
            or COMPRESSION_ENCODING not in supported_encodings
            or response.content_obj.correct_encoding() != "identity"
            ):
            # No need to compress content if correct_encoding is not identity (might already be compressed)
            response.set_header(
                "Content-Encoding",
                response.content_obj.correct_encoding(),
            )
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
                response.set_header(
                    "Content-Encoding",
                    response.content_obj.correct_encoding(),
                )
            
        else:
            # Streaming HTTP response here.
            if not COMPRESS_STREAMING_RESPONSES:
                # Compressing streaming responses disallowed
                return
            
            # Check if we are dealing with a StreamingRangeHttpResponse
            if isinstance(response, StreamingRangeHttpResponse):
                start_pos, end_pos = response.start_pos, response.end_pos
                content_size = end_pos - start_pos
                
                if not(content_size >= COMPRESSION_MIN_SIZE and content_size <= COMPRESSION_MAX_SIZE):
                    # Compression not applicable.
                    return
                    
            content_type = response.get_header("content-type", "")
            total_stream_size = None
            
            if hasattr(response, "stream") and hasattr(response.stream, "tell") and hasattr(response.stream, "seek"):
                response.stream.seek(0, io.SEEK_END) # seek to EOF
                total_stream_size = response.stream.tell()
            else:
                return # Quit with the compression
                    
            if total_stream_size is not None:
                if total_stream_size < COMPRESSION_MIN_SIZE or total_stream_size > COMPRESSION_MAX_SIZE :
                    # Total stream size if beyond or below compression limits
                    return
            else:
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
        
        if not range_header:
            if isinstance(response, StreamingRangeHttpResponse):
                if response.status_code == 206:
                    response.payload_obj.parse_status(200) # modify the response to correct status
                    response.clear_content_range_headers() # clear range headers
            return  # If no Range header exists, no need to set content range headers.
        
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
            # replace response data
            new_response = None
            
            if SETTINGS["DEBUG"]:
                new_response = template_response(
                    HttpRangeNotSatisfiableResponse,
                    body=(
                        f"<p>Range is not satisfiable, could not resolve: {range_header}</p>"
                        f"<p>Exception: {e}</p>"
                    )
                )
            else:
                new_response = simple_response(HttpRangeNotSatisfiableResponse)
            
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
        # All of the following method calls are failsafe meaning failure of any method
        # will not affect the execution of other methods, thus an error encountered will be
        # logged appropriately. Decorator responsible: @log_failsafe
        
        self.do_request_response_transformation(response, request) 
        self.do_set_fixed_headers(response, request)
        self.do_set_connection_mode(response, request)
        self.do_set_extra_headers(response, request)
            
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
