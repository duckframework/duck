"""
Cloudflare storage backends.
"""
import os

from typing import Any

from duck.contrib.storage.backends import resolve_credentials
from duck.contrib.storage.backends.s3 import S3Storage
from duck.contrib.storage.exceptions import StorageError


try:
    import httpx
    
except ModuleNotFoundError as e:
    raise StorageError("Module httpx is missing, please install using `pip install httpx`") from e


CLOUDFLARE_API_URL = "https://api.cloudflare.com/client/v4"


class CloudflareR2Storage(S3Storage):
    """
    Stores files in Cloudflare R2 and serves them through Cloudflare's CDN.

    Builds the R2 endpoint from the account ID and reads credentials from
    environment variables when they are not passed explicitly. Deleting a
    file also purges its CDN cache when an API token and zone ID are set.
    """

    def __init__(
        self,
        bucket: str,
        account_id: str,
        public_base_url: str,
        access_key_id: str | None = None,
        secret_access_key: str | None = None,
        api_token: str | None = None,
        zone_id: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the Cloudflare R2 backend.

        Args:
            bucket: Name of the R2 bucket.
            account_id: Cloudflare account ID, found in the dashboard sidebar.
            public_base_url: Domain connected to the bucket, such as `"https://cdn.example.com"`.
            access_key_id: R2 access key ID. Defaults to `R2_ACCESS_KEY_ID`.
            secret_access_key: R2 secret key. Defaults to `R2_SECRET_ACCESS_KEY`.
            api_token: API token with cache purge permission. Defaults to `CLOUDFLARE_API_TOKEN`.
            zone_id: Zone ID of the domain serving the bucket. Defaults to `CLOUDFLARE_ZONE_ID`.
            **kwargs: Extra arguments passed to S3Storage.
        """
        self.api_token = api_token or os.environ.get("CLOUDFLARE_API_TOKEN")
        self.zone_id = zone_id or os.environ.get("CLOUDFLARE_ZONE_ID")

        # Resolve access and secret keys
        access, secret = resolve_credentials(
            access_key_id,
            secret_access_key,
            "R2_ACCESS_KEY_ID",
            "R2_SECRET_ACCESS_KEY",
        )

        # Super initialization
        super().__init__(
            bucket=bucket,
            public_base_url=public_base_url,
            endpoint_url=f"https://{account_id}.r2.cloudflarestorage.com",
            region_name="auto",
            access_key_id=access,
            secret_access_key=secret,
            **kwargs,
        )

    def can_purge(self) -> bool:
        """
        Checks whether cache purging is configured.

        Returns:
            True if both the API token and zone ID are set.
        """
        return bool(self.api_token and self.zone_id)

    def purge_request(self, urls: list[str]) -> tuple[str, dict[str, str], dict[str, list[str]]]:
        """
        Builds the purge endpoint, headers and body for a set of URLs.

        Args:
            urls: Full public URLs to purge.

        Returns:
            A tuple of the endpoint URL, headers and JSON body.

        Raises:
            RuntimeError: If the API token or zone ID is missing.
        """
        if not self.can_purge():
            raise RuntimeError("CLOUDFLARE_API_TOKEN and CLOUDFLARE_ZONE_ID are required to purge the cache")

        # Build URL and headers
        url = f"{CLOUDFLARE_API_URL}/zones/{self.zone_id}/purge_cache"
        headers = {"Authorization": f"Bearer {self.api_token}"}

        # Return url, headers and json body
        return url, headers, {"files": urls}

    def check_purge_response(self, response: httpx.Response) -> None:
        """
        Raises an error when Cloudflare rejects a purge request.

        Args:
            response: Response returned by the purge endpoint.

        Raises:
            httpx.HTTPStatusError: If the HTTP status indicates an error.
            RuntimeError: If the response body reports `success: false`.
        """
        response.raise_for_status()

        # Parse body to JSON
        body = response.json()

        if not body.get("success"):
            raise RuntimeError(f"Cache purge failed: {body.get('errors')}")

    def purge_cache(self, urls: list[str]) -> None:
        """
        Removes the given URLs from Cloudflare's CDN cache.

        Args:
            urls: Full public URLs to purge.
        """
        url, headers, payload = self.purge_request(urls)

        # Get response
        response = self.sync_client.post(url, headers=headers, json=payload)

        # Check ability to purge
        self.check_purge_response(response)

    async def async_purge_cache(self, urls: list[str]) -> None:
        """
        Async cache purge using `httpx.AsyncClient`.

        Args:
            urls: Full public URLs to purge.
        """
        url, headers, payload = self.purge_request(urls)

        # Get response
        response = await self.async_client.post(url, headers=headers, json=payload)

        # Check ability to purge
        self.check_purge_response(response)

    def delete(self, key: str) -> None:
        """
        Deletes an object from R2 and purges its CDN cache when configured.

        Args:
            key: Object key in the bucket.
        """
        super().delete(key)
        
        if self.can_purge():
            self.purge_cache([self.url_for(key)])

    async def async_delete(self, key: str) -> None:
        """
        Async delete that also purges the CDN cache when configured.

        Args:
            key: Object key in the bucket.
        """
        await super().async_delete(key)

        if self.can_purge():
            await self.async_purge_cache([self.url_for(key)])
