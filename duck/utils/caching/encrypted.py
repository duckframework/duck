"""
Encrypted cache wrapper using PyNaCl (libsodium).

Provides NaClEncryptor and EncryptedCache — a transparent encryption
layer that wraps any CacheBase backend. The backend never sees plaintext.
Encryption uses XSalsa20-Poly1305 AEAD: authenticated, single-pass,
and ARM-safe.
"""

import os
import json

from typing import Any

import pickle
import nacl.secret
import nacl.utils

from nacl.exceptions import CryptoError

from duck.utils.caching import CacheBase, MISSING


# SecretBox nonce size as defined by libsodium (24 bytes).
NONCE_SIZE: int = nacl.secret.SecretBox.NONCE_SIZE

# Environment variable the user must set to opt in to automatic key derivation
DUCK_NACL_DERIVE_KEY_ENV = "DUCK_NACL_DERIVE_KEY"

# NaCl SecretBox requires exactly this many bytes
NACL_KEY_SIZE = nacl.secret.SecretBox.KEY_SIZE  # 32


def resolve_nacl_key(secret_key: bytes) -> bytes:
    """
    Ensures a raw secret key meets NaCl's 32-byte requirement.

    Behaviour by key length:
    - **Exactly 32 bytes** — returned as-is, no processing.
    - **Fewer than 32 bytes** — derived to 32 bytes using BLAKE2b with a fixed
      32-byte digest. This is stable: the same input always produces the same
      output, so previously encrypted data remains decryptable.
    - **More than 32 bytes** — raises ``ValueError`` unless the environment
      variable ``DUCK_NACL_DERIVE_KEY`` is set to ``"1"``, in which case
      BLAKE2b derivation is applied to compress the key to 32 bytes.

    Args:
        secret_key: The raw key bytes to resolve.

    Returns:
        bytes: A exactly 32-byte key safe to pass to ``nacl.secret.SecretBox``.

    Raises:
        ValueError: If the key is empty, or longer than 32 bytes without the
            opt-in environment variable set.
    """
    if not secret_key:
        raise ValueError(
            "Secret key is empty. Please provide a non-empty secret key."
        )

    key_len = len(secret_key)

    if key_len == NACL_KEY_SIZE:
        # Already the correct size — nothing to do
        return secret_key

    if key_len < NACL_KEY_SIZE:
        # Derive a stable 32-byte key via BLAKE2b so existing ciphertext stays valid
        return hashlib.blake2b(secret_key, digest_size=NACL_KEY_SIZE).digest()

    # Key is longer than 32 bytes — require explicit opt-in before truncating
    if os.environ.get(DUCK_NACL_DERIVE_KEY_ENV) != "1":
        raise ValueError(
            f"Secret key is {key_len} bytes but NaCl requires exactly {NACL_KEY_SIZE}. "
            f"Set the environment variable {DUCK_NACL_DERIVE_KEY_ENV}=1 to allow "
            f"automatic key derivation via BLAKE2b, or provide a key that is "
            f"{NACL_KEY_SIZE} bytes or fewer."
        )

    # User opted in — derive down to 32 bytes
    return hashlib.blake2b(secret_key, digest_size=NACL_KEY_SIZE).digest()


def generate_secret_key() -> bytes:
    """
    Generate a 32-byte secret key for NaClEncryptor.

    Run once and persist the result in an environment variable or a
    secrets manager. Never hardcode or commit the returned value.

    Returns:
        32 cryptographically random bytes.
    """
    return nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)


class NaClEncryptor:
    """
    XSalsa20-Poly1305 AEAD encryptor backed by libsodium via PyNaCl.

    Authenticated encryption and integrity verification happen in a
    single pass — they are inseparable. A unique random nonce is
    generated per message and embedded in the output so decrypt() is
    fully self-contained with no external nonce management.

    Builds cleanly on ARM, x86, and MIPS — anywhere libsodium compiles.

    Args:
        secret_key: 32 bytes from generate_secret_key().

    Raises:
        ValueError: When secret_key is not exactly 32 bytes.
    """

    def __init__(self, secret_key: bytes):
        if not secret_key:
            raise ValueError(
                f"Secret key seems to be empty, please provide secret key."
            )
        self.secret_key = resolve_nacl_key(secret_key).encode("utf-8")
        self.box = nacl.secret.SecretBox(self.secret_key)

    def encrypt(self, value: Any) -> bytes:
        """
        Serialise value using Pickle then encrypt it.

        A fresh random nonce is generated on every call so encrypting
        the same value twice always produces different ciphertext.

        Args:
            value: Any Pickle-serialisable Python object.

        Returns:
            Raw bytes containing the embedded nonce, ciphertext, and
            Poly1305 authentication tag. No base64 encoding applied.

        Raises:
            TypeError: When value is not Pickle-serialisable.
        """
        # NOTE: Pickle in general is slow but safer than JSON because it supports many types e.g. datetime objects.
        value = pickle.dumps(value)
        nonce = nacl.utils.random(NONCE_SIZE)
        
        # SecretBox.encrypt embeds the nonce so decrypt() needs no
        # separate nonce argument.
        return bytes(self.box.encrypt(value, nonce))

    def decrypt(self, data: bytes) -> Any:
        """
        Decrypt and deserialise bytes produced by encrypt().

        Args:
            data: Raw bytes from a previous encrypt() call.

        Returns:
            The original Python object.

        Raises:
            CryptoError: When data has been tampered with or was
                encrypted with a different key. Never silently returns
                bad data.
        """
        pickled = self.box.decrypt(data)
        return pickle.loads(pickled)


class EncryptedCache(CacheBase):
    """
    Transparent encryption wrapper around any CacheBase backend.

    Values are encrypted with NaClEncryptor before being passed to the
    inner backend and decrypted transparently on retrieval. The backend
    never sees or stores plaintext. Tampering or wrong-key errors cause
    the offending entry to be evicted immediately rather than returned.

    All methods delegate locking to the inner backend — no double-locking.
    The async_* variants are forwarded to the inner backend's async_*
    methods when available, falling back to the sync methods otherwise.

    Args:
        backend: Any CacheBase instance to use as the storage layer.
        secret_key: 32-byte key from generate_secret_key().

    Example:
    ```py
        import os
        
        from duck.settings import SETTINGS
        from duck.caching import PersistentFileCache
        from duck.caching.encrypted import EncryptedCache, generate_secret_key

        # Unencrypted cache for general use.
        cache = PersistentFileCache("./var/cache")

        # Encrypted cache for sessions or any sensitive data.
        session_cache = EncryptedCache(
            backend=PersistentFileCache("./var/sessions"),
            secret_key=SETTINGS["SECRET_KEY"].encode(),
        )

        session_cache.set("sid:abc123", {"user_id": 42}, expiry=3600)
        data = session_cache.get("sid:abc123")
    ```
    """

    def __init__(self, backend: CacheBase, secret_key: bytes):
        self.backend = backend
        self.encryptor = NaClEncryptor(secret_key)

    def set(self, key: str, value: Any, expiry: int | float | None = None) -> None:
        """
        Encrypt value and store it in the backend under key.

        Args:
            key: Cache key.
            value: Any JSON-serialisable value to store.
            expiry: TTL in seconds. None means no expiry.

        Raises:
            TypeError: When value is not JSON-serialisable.
        """
        self.backend.set(key, self.encryptor.encrypt(value), expiry)

    def get(self, key: str, default: Any = None) -> Any:
        """
        Retrieve and decrypt a value from the backend.

        Returns default when the key is absent, expired, or the
        ciphertext fails authentication — tampered entries are evicted
        immediately and never returned.

        Args:
            key: Cache key to look up.
            default: Returned on miss, expiry, or tamper detection.

        Returns:
            The decrypted value or default.
        """
        raw = self.backend.get(key)

        if raw is None:
            return default

        try:
            return self.encryptor.decrypt(raw)
        except CryptoError:
            # Tampered or wrong key — evict and return default cleanly.
            self.backend.delete(key)
            return default

    def delete(self, key: str) -> None:
        """
        Remove key from the backend. Silent if absent.

        Args:
            key: Cache key to remove.
        """
        self.backend.delete(key)

    def pop(self, key: str, default: Any = MISSING) -> Any:
        """
        Retrieve, decrypt, and atomically remove a value.

        The raw value is popped from the backend first so that a
        tampered entry is always removed regardless of whether
        decryption succeeds.

        Args:
            key: Cache key to retrieve and delete.
            default: Returned when absent. Raises KeyError if omitted.

        Returns:
            The decrypted value or default.

        Raises:
            KeyError: When the key is missing and no default was given.
        """
        raw = self.backend.pop(key, default=None)

        if raw is None:
            if default is MISSING:
                raise KeyError(key)
            return default

        try:
            return self.encryptor.decrypt(raw)
        except CryptoError:
            # Entry was already popped — nothing left to evict.
            if default is MISSING:
                raise KeyError(key)
            return default

    def clear(self) -> None:
        """
        Evict all entries from the underlying backend.
        """
        self.backend.clear()

    # Async variants — delegate to backend async methods where available.

    async def async_set(
        self, key: str, value: Any, expiry: int | float | None = None
    ) -> None:
        """
        Async-safe version of set.

        Args:
            key: Cache key.
            value: JSON-serialisable value to store.
            expiry: TTL in seconds.
        """
        from duck.contrib.sync import ensure_async
        
        encrypted = self.encryptor.encrypt(value)

        if hasattr(self.backend, "async_set"):
            await self.backend.async_set(key, encrypted, expiry)
        else:
            await ensure_async(self.backend.set)(key, encrypted, expiry)

    async def async_get(self, key: str, default: Any = None) -> Any:
        """
        Async-safe version of get.

        Args:
            key: Cache key to look up.
            default: Returned on miss, expiry, or tamper detection.

        Returns:
            The decrypted value or default.
        """
        from duck.contrib.sync import ensure_async
        
        if hasattr(self.backend, "async_get"):
            raw = await self.backend.async_get(key)
        else:
            raw = await ensure_async(self.backend.get)(key)

        if raw is None:
            return default

        try:
            return self.encryptor.decrypt(raw)
        except CryptoError:
            await self.async_delete(key)
            return default

    async def async_pop(self, key: str, default: Any = MISSING) -> Any:
        """
        Async-safe version of pop.

        Args:
            key: Cache key to retrieve and delete.
            default: Returned when absent. Raises KeyError if omitted.

        Returns:
            The decrypted value or default.

        Raises:
            KeyError: When the key is missing and no default was given.
        """
        from duck.contrib.sync import ensure_async
        
        if hasattr(self.backend, "async_pop"):
            raw = await self.backend.async_pop(key, default=None)
        else:
            raw = await ensure_async(self.backend.pop)(key, default=None)

        if raw is None:
            if default is MISSING:
                raise KeyError(key)
            return default

        try:
            return self.encryptor.decrypt(raw)
        except CryptoError:
            if default is MISSING:
                raise KeyError(key)
            return default

    async def async_delete(self, key: str) -> None:
        """
        Async-safe version of delete.

        Args:
            key: Cache key to remove.
        """
        from duck.contrib.sync import ensure_async
        
        if hasattr(self.backend, "async_delete"):
            await self.backend.async_delete(key)
        else:
            await ensure_async(self.backend.delete)(key)

    async def async_clear(self) -> None:
        """
        Async-safe version of clear.
        """
        from duck.contrib.sync import ensure_async
        
        if hasattr(self.backend, "async_clear"):
            await self.backend.async_clear()
        else:
            await ensure_async(self.backend.clear)()

    def close(self) -> None:
        """
        Close the underlying backend.
        """
        self.backend.close()
