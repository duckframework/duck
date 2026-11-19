"""
S3 Storage backends.
"""
import hmac
import hashlib
import urllib.parse

from typing import Any, Optional
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

from duck.contrib.storage.backends import (
    EMPTY_SHA256,
    StorageBackend,
    UploadContext,
    iter_chunks,
    async_iter_chunks,
    resolve_credentials,
)
from duck.contrib.storage.exceptions import StorageError
from duck.contrib.storage.backends.core.progress import ProgressReporter
from duck.contrib.storage.backends.core.streams import (
    HTTPResponseStream,
    AsyncHTTPResponseStream,
)
from duck.utils.urlcrack import URL


try:
    import httpx
    
except ModuleNotFoundError as e:
    raise StorageError("Module httpx is missing, please install using `pip install httpx`") from e



def hmac_sha256(key: bytes, message: str) -> bytes:
    """
    Computes an HMAC-SHA256 digest.

    Args:
        key: HMAC key.
        message: Text to authenticate.

    Returns:
        The raw digest bytes.
    """
    return hmac.new(key, message.encode(), hashlib.sha256).digest()



def derive_signing_key(secret_key: str, date_stamp: str, region: str) -> bytes:
    """
    Derives the SigV4 signing key for a date, region and the S3 service.

    Args:
        secret_key: AWS or R2 secret access key.
        date_stamp: Date in ``YYYYMMDD`` form.
        region: Region name, such as ``"auto"`` for R2.

    Returns:
        The derived signing key bytes.
    """
    key = hmac_sha256(f"AWS4{secret_key}".encode(), date_stamp)
    key = hmac_sha256(key, region)
    key = hmac_sha256(key, "s3")

    # Return final signing key
    return hmac_sha256(key, "aws4_request")


def sign_s3_request(
    method: str,
    url: str,
    headers: dict[str, str],
    payload_hash: str,
    region: str,
    access_key: str,
    secret_key: str,
    now: datetime | None = None,
) -> dict[str, str]:
    """
    Adds AWS Signature Version 4 headers to an S3-compatible request.

    Args:
        method: HTTP method in uppercase, such as ``"PUT"``.
        url: Full request URL with the path already URI-encoded.
        headers: Headers to send. Signed headers are taken from this dictionary.
        payload_hash: Hex SHA-256 of the request body, or of empty bytes.
        region: Region name used in the credential scope.
        access_key: Access key ID.
        secret_key: Secret access key.
        now: Timestamp for the signature. Defaults to the current UTC time.

    Returns:
        A new headers dictionary that includes the Authorization header.
    """
    now = now or datetime.now(timezone.utc)
    amz_date = now.strftime("%Y%m%dT%H%M%SZ")
    date_stamp = now.strftime("%Y%m%d")
    url_obj = URL(url)

    # Build signed dict
    signed = {name.lower(): str(value).strip() for name, value in headers.items()}

    # Add data to signed
    signed["host"] = url_obj.netloc
    signed["x-amz-date"] = amz_date
    signed["x-amz-content-sha256"] = payload_hash

    # Get names
    names = sorted(signed)

    # Build canonical request
    canonical_request = "\n".join([
        method,
        url_obj.path or "/",
        url_obj.query,
        "".join(f"{name}:{signed[name]}\n" for name in names),
        ";".join(names),
        payload_hash,
    ])

    # Scope
    scope = f"{date_stamp}/{region}/s3/aws4_request"

    # Build string to sign
    string_to_sign = "\n".join([
        "AWS4-HMAC-SHA256",
        amz_date,
        scope,
        hashlib.sha256(canonical_request.encode()).hexdigest(),
    ])

    # Build signature
    signature = hmac.new(
        derive_signing_key(secret_key, date_stamp, region),
        string_to_sign.encode(),
        hashlib.sha256,
    ).hexdigest()

    # Build auth
    authorization = (
        f"AWS4-HMAC-SHA256 Credential={access_key}/{scope}, "
        f"SignedHeaders={';'.join(names)}, Signature={signature}"
    )

    # Return final headers
    return {
        **headers,
        "x-amz-date": amz_date,
        "x-amz-content-sha256": payload_hash,
        "Authorization": authorization,
    }


def parse_last_modified(value: str | None) -> float | None:
    """
    Parses a Last-Modified header into a UTC timestamp.

    Args:
        value: Raw header value, or None.

    Returns:
        Seconds since the epoch, or None when missing or unparseable.
    """
    if not value:
        return None

    try:
        parsed = parsedate_to_datetime(value)

    except (TypeError, ValueError, IndexError):
        return None

    # Header dates without a zone are treated as UTC
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)

    return parsed.timestamp()


class S3Storage(StorageBackend):
    """
    Stores files in an S3-compatible bucket using httpx and SigV4 signing.

    Works with AWS S3, Cloudflare R2, MinIO and Backblaze B2. Requests use
    path-style URLs, so the endpoint is the same for every bucket. Sync and
    async calls use separate httpx clients that are created once per backend.
    Downloads stream through `open_stream` and `async_open_stream`.
    """

    def __init__(
        self,
        bucket: str,
        public_base_url: str,
        endpoint_url: str | None = None,
        region_name: str = "us-east-1",
        access_key_id: str | None = None,
        secret_access_key: str | None = None,
        timeout: float = 60.0,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the S3-compatible backend.

        Args:
            bucket: Name of the bucket.
            public_base_url: CDN or public domain serving the bucket, such as `"https://cdn.example.com"`.
            endpoint_url: S3 API endpoint. Defaults to the regional AWS endpoint.
            region_name: Region name used for signing.
            access_key_id: Access key ID. Defaults to `AWS_ACCESS_KEY_ID`.
            secret_access_key: Secret key. Defaults to `AWS_SECRET_ACCESS_KEY`.
            timeout: Request timeout in seconds.
            **kwargs: Extra arguments passed to StorageBackend.
        """
        super().__init__(**kwargs)

        # Retrieve secret keys
        self.access_key_id, self.secret_access_key = resolve_credentials(
            access_key_id,
            secret_access_key,
            "AWS_ACCESS_KEY_ID",
            "AWS_SECRET_ACCESS_KEY",
        )

        # Set some attributes
        self.bucket = bucket
        self.public_base_url = public_base_url.rstrip("/")
        self.endpoint_url = (endpoint_url or f"https://s3.{region_name}.amazonaws.com").rstrip("/")
        self.region_name = region_name
        self.sync_client = httpx.Client(timeout=timeout)
        self.async_client = httpx.AsyncClient(timeout=timeout)

    def object_url(self, key: str) -> str:
        """
        Builds the path-style URL of an object in the bucket.

        Args:
            key: Object key in the bucket.

        Returns:
            The URL for the object on the S3 API endpoint.
        """
        encoded_key = urllib.parse.quote(key, safe="/-_.~")

        return f"{self.endpoint_url}/{self.bucket}/{encoded_key}"

    def signed_headers(
        self,
        method: str,
        url: str,
        payload_hash: str,
        headers: dict[str, str] | None = None,
    ) -> dict[str, str]:
        """
        Signs a request with this backend's credentials.

        Args:
            method: HTTP method in uppercase.
            url: Full request URL.
            payload_hash: Hex SHA-256 of the request body.
            headers: Additional headers to include in the signature.

        Returns:
            Headers including the Authorization header.
        """
        return sign_s3_request(
            method,
            url,
            headers or {},
            payload_hash,
            self.region_name,
            self.access_key_id,
            self.secret_access_key,
        )

    def prepare_empty(self, method: str, key: str) -> tuple[str, dict[str, str]]:
        """
        Prepares a request that has no body.

        Args:
            method: HTTP method such as `"GET"`, `"HEAD"` or `"DELETE"`.
            key: Object key in the bucket.

        Returns:
            A tuple of the request URL and signed headers.
        """
        url = self.object_url(key)

        return url, self.signed_headers(method, url, EMPTY_SHA256)

    def prepare_put(self, key: str, context: UploadContext) -> tuple[str, dict[str, str]]:
        """
        Prepares an upload request with content type, cache and metadata headers.

        Args:
            key: Object key in the bucket.
            context: Final upload state.

        Returns:
            A tuple of the request URL and signed headers.
        """
        url = self.object_url(key)
        headers = {
            "Content-Type": context.content_type,
            "Cache-Control": context.cache_control,
            "Content-Length": str(len(context.payload)),
        }

        # Add the SHA256 and metadata headers
        headers["x-amz-meta-sha256"] = context.sha256

        for name, value in context.metadata.items():
            headers[f"x-amz-meta-{name.lower()}"] = str(value)

        # Sign the request and return
        return url, self.signed_headers("PUT", url, context.sha256, headers)

    def put(self, key: str, context: UploadContext, reporter: ProgressReporter) -> None:
        """
        Uploads the payload to the bucket in chunks.

        Args:
            key: Object key in the bucket.
            context: Final upload state.
            reporter: Progress reporter advanced as chunks are sent.

        Raises:
            httpx.HTTPStatusError: If the bucket rejects the upload.
        """
        url, headers = self.prepare_put(key, context)

        response = self.sync_client.put(
            url,
            headers=headers,
            content=iter_chunks(context.payload, self.chunk_size, reporter),
        )

        # Raise exception on error.
        response.raise_for_status()

    async def async_put(self, key: str, context: UploadContext, reporter: ProgressReporter) -> None:
        """
        Async upload using `httpx.AsyncClient`.

        Args:
            key: Object key in the bucket.
            context: Final upload state.
            reporter: Progress reporter advanced as chunks are sent.

        Raises:
            httpx.HTTPStatusError: If the bucket rejects the upload.
        """
        url, headers = self.prepare_put(key, context)

        response = await self.async_client.put(
            url,
            headers=headers,
            content=async_iter_chunks(context.payload, self.chunk_size, reporter),
        )

        # Raise exception on error.
        response.raise_for_status()

    def get(self, key: str) -> bytes:
        """
        Downloads an object from the bucket.

        Args:
            key: Object key in the bucket.

        Returns:
            The object contents as bytes.

        Raises:
            httpx.HTTPStatusError: If the request fails.
        """
        url, headers = self.prepare_empty("GET", key)

        # Get response
        response = self.sync_client.get(url, headers=headers)

        # Raise exception on error.
        response.raise_for_status()

        return response.content

    async def async_get(self, key: str) -> bytes:
        """
        Async download using `httpx.AsyncClient`.

        Args:
            key: Object key in the bucket.

        Returns:
            The object contents as bytes.

        Raises:
            httpx.HTTPStatusError: If the request fails.
        """
        url, headers = self.prepare_empty("GET", key)

        # Get response
        response = await self.async_client.get(url, headers=headers)

        # Raise exception on error.
        response.raise_for_status()

        # Return the final response
        return response.content

    def open_stream(self, key: str) -> HTTPResponseStream:
        """
        Opens an object for streamed download. The caller must close it.

        The response body is not read until the stream is consumed, so memory
        use stays bounded by `chunk_size` regardless of object size.

        Args:
            key: Object key in the bucket.

        Returns:
            A synchronous stream over the object's bytes.

        Raises:
            httpx.HTTPStatusError: If the request fails.
        """
        url, headers = self.prepare_empty("GET", key)
        request = self.sync_client.build_request("GET", url, headers=headers)
        response = self.sync_client.send(request, stream=True)

        try:
            response.raise_for_status()

        except httpx.HTTPStatusError:
            # Release the connection before surfacing the error
            response.close()

            # Reraise exception
            raise

        return HTTPResponseStream(response, self.chunk_size, key)

    async def async_open_stream(self, key: str) -> AsyncHTTPResponseStream:
        """
        Async version of `open_stream` using `httpx.AsyncClient`.

        Args:
            key: Object key in the bucket.

        Returns:
            An asynchronous stream over the object's bytes.

        Raises:
            httpx.HTTPStatusError: If the request fails.
        """
        url, headers = self.prepare_empty("GET", key)
        request = self.async_client.build_request("GET", url, headers=headers)
        response = await self.async_client.send(request, stream=True)

        try:
            response.raise_for_status()

        except httpx.HTTPStatusError:
            # Release the connection before surfacing the error
            await response.aclose()

            # Reraise exception
            raise

        return AsyncHTTPResponseStream(response, self.chunk_size, key)

    def delete(self, key: str) -> None:
        """
        Deletes an object from the bucket. Missing objects are ignored.

        Args:
            key: Object key in the bucket.

        Raises:
            httpx.HTTPStatusError: If the request fails for a reason other than a missing object.
        """
        url, headers = self.prepare_empty("DELETE", key)
        response = self.sync_client.delete(url, headers=headers)

        if response.status_code != 404:
            response.raise_for_status()

    async def async_delete(self, key: str) -> None:
        """
        Async delete using `httpx.AsyncClient`.

        Args:
            key: Object key in the bucket.

        Raises:
            httpx.HTTPStatusError: If the request fails for a reason other than a missing object.
        """
        url, headers = self.prepare_empty("DELETE", key)
        response = await self.async_client.delete(url, headers=headers)

        if response.status_code != 404:
            response.raise_for_status()

    def exists(self, key: str) -> bool:
        """
        Checks whether an object exists using a HEAD request.

        Args:
            key: Object key in the bucket.

        Returns:
            True if the object exists, otherwise False.

        Raises:
            httpx.HTTPStatusError: If the request fails for a reason other than a missing object.
        """
        url, headers = self.prepare_empty("HEAD", key)
        response = self.sync_client.head(url, headers=headers)

        if response.status_code == 404:
            return False

        # Raise exception on error.
        response.raise_for_status()

        # Return the final flag
        return True

    async def async_exists(self, key: str) -> bool:
        """
        Async existence check using `httpx.AsyncClient`.

        Args:
            key: Object key in the bucket.

        Returns:
            True if the object exists, otherwise False.

        Raises:
            httpx.HTTPStatusError: If the request fails for a reason other than a missing object.
        """
        url, headers = self.prepare_empty("HEAD", key)
        response = await self.async_client.head(url, headers=headers)

        if response.status_code == 404:
            return False

        # Raise exception on error.
        response.raise_for_status()

        # Return the final flag
        return True

    def size(self, key: str) -> int:
        """
        Returns the size of an object using a HEAD request.

        Args:
            key: Object key in the bucket.

        Returns:
            The object size in bytes.

        Raises:
            FileNotFoundError: If the object does not exist.
            httpx.HTTPStatusError: If the request fails for a reason other than a missing object.
        """
        url, headers = self.prepare_empty("HEAD", key)
        response = self.sync_client.head(url, headers=headers)

        # Missing object
        if response.status_code == 404:
            raise FileNotFoundError(key)

        # Raise exception on error.
        response.raise_for_status()

        # Return the final size
        return int(response.headers["Content-Length"])

    async def async_size(self, key: str) -> int:
        """
        Async object size lookup using `httpx.AsyncClient`.

        Args:
            key: Object key in the bucket.

        Returns:
            The object size in bytes.

        Raises:
            FileNotFoundError: If the object does not exist.
            httpx.HTTPStatusError: If the request fails for a reason other than a missing object.
        """
        url, headers = self.prepare_empty("HEAD", key)
        response = await self.async_client.head(url, headers=headers)

        # Missing object
        if response.status_code == 404:
            raise FileNotFoundError(key)

        # Raise exception on error.
        response.raise_for_status()

        # Return the final size
        return int(response.headers["Content-Length"])

    def modified_time(self, key: str) -> Optional[float]:
        """
        Returns the object's Last-Modified time using a HEAD request.

        Args:
            key: Object key in the bucket.

        Returns:
            Seconds since the epoch or None if the header is missing or unparseable.

        Raises:
            FileNotFoundError: If the object does not exist.
        """
        url, headers = self.prepare_empty("HEAD", key)
        response = self.sync_client.head(url, headers=headers)

        # Missing object
        if response.status_code == 404:
            raise FileNotFoundError(key)

        # Raise exception on error.
        response.raise_for_status()

        # Return the final modified time
        return parse_last_modified(response.headers.get("Last-Modified"))

    def is_unchanged(self, key: str, context: UploadContext) -> bool:
        """
        Compares the stored sha256 metadata with the upload using one HEAD request.

        Args:
            key: Object key in the bucket.
            context: Final upload state.

        Returns:
            True if the stored object has the same content hash.
        """
        url, headers = self.prepare_empty("HEAD", key)
        response = self.sync_client.head(url, headers=headers)

        # Missing object
        if response.status_code == 404:
            return False

        # Raise exception on error.
        response.raise_for_status()

        # Trust mtime only when present and clearly newer
        if context.source_mtime is not None:
            stored = parse_last_modified(response.headers.get("Last-Modified"))
            
            if stored is not None and stored == context.source_mtime:
                return True

        # Compare the stored sha256 metadata with the upload
        return response.headers.get("x-amz-meta-sha256") == context.sha256

    async def async_is_unchanged(self, key: str, context: UploadContext) -> bool:
        """
        Async version of `is_unchanged` using `httpx.AsyncClient`.

        Args:
            key: Object key in the bucket.
            context: Final upload state.

        Returns:
            True if the stored object has the same content hash.
        """
        url, headers = self.prepare_empty("HEAD", key)
        response = await self.async_client.head(url, headers=headers)

        # Missing object
        if response.status_code == 404:
            return False

        # Raise exception on error.
        response.raise_for_status()

        # Trust mtime only when present and clearly newer
        if context.source_mtime is not None:
            stored = parse_last_modified(response.headers.get("Last-Modified"))

            if stored is not None and stored == context.source_mtime:
                return True
            
        # Compare the stored sha256 metadata with the upload
        return response.headers.get("x-amz-meta-sha256") == context.sha256

    def url_for(self, key: str) -> str:
        """
        Builds a CDN URL for an object.

        Args:
            key: Object key in the bucket.

        Returns:
            The public URL served through the CDN.
        """
        return f"{self.public_base_url}/{key}"

    def close(self) -> None:
        """
        Closes the sync httpx client.
        """
        self.sync_client.close()

    async def async_close(self) -> None:
        """
        Closes the async httpx client.
        """
        await self.async_client.aclose()
