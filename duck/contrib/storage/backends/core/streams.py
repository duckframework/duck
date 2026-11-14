"""
Streams for storage backends.
"""
import io
import httpx

from typing import Iterator, AsyncIterator

from duck.contrib.storage.backends import DEFAULT_CHUNK_SIZE


class HTTPResponseStream:
    """
    Synchronous read-only stream over a streaming httpx response.

    Pulls the body in chunks as `read` asks for data, so the whole object is
    never held in memory. Supports `read`, `tell`, iteration, `close` and
    the context manager protocol, matching FileIOStream's interface.
    """

    def __init__(self, response: httpx.Response, chunk_size: int, key: str) -> None:
        """
        Initializes the stream.

        Args:
            response: Open httpx response created with `stream=True`.
            chunk_size: Bytes requested from the network per chunk.
            key: Storage key being streamed.
        """
        self.response = response
        self.iterator = response.iter_bytes(chunk_size)
        self.buffer = bytearray()
        self.position = 0
        self.closed = False
        self.key = key
        self.size = int(response.headers.get("content-length", -1))

    def read(self, size: int = -1) -> bytes:
        """
        Reads up to `size` bytes, pulling network chunks as needed.

        Args:
            size: Number of bytes to read. A negative value reads to the end.

        Returns:
            The bytes read. Shorter than `size` only at end of stream.

        Raises:
            ValueError: If the stream is closed.
        """
        if self.closed:
            raise ValueError("I/O operation on closed stream")

        # Read everything that remains
        if size < 0:
            self.buffer.extend(b"".join(self.iterator))
            count = len(self.buffer)
        else:
            # Pull chunks until the buffer can satisfy the request
            while len(self.buffer) < size:
                chunk = next(self.iterator, None)

                if chunk is None:
                    break

                self.buffer.extend(chunk)

            count = min(size, len(self.buffer))

        data = bytes(self.buffer[:count])
        del self.buffer[:count]
        self.position += len(data)
        return data

    def tell(self) -> int:
        """
        Returns the number of bytes read so far.

        Returns:
            The current stream position.
        """
        return self.position

    def __iter__(self) -> Iterator[bytes]:
        """
        Yields the remaining data in chunks.

        Yields:
            Successive chunks of the stream.
        """
        while True:
            chunk = self.read(DEFAULT_CHUNK_SIZE)

            if not chunk:
                break

            yield chunk

    def close(self) -> None:
        """
        Closes the stream and releases the network connection.
        """
        if not self.closed:
            self.response.close()
            self.closed = True

    def __enter__(self) -> HTTPResponseStream:
        """
        Enters the context manager.

        Returns:
            This stream.
        """
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        """
        Closes the stream on exit from the context manager.
        """
        self.close()


class AsyncHTTPResponseStream:
    """
    Asynchronous read-only stream over a streaming httpx response.

    Async counterpart of HTTPResponseStream. Each network chunk is awaited, so
    the event loop stays free while data arrives.
    """

    def __init__(self, response: httpx.Response, chunk_size: int, key: str) -> None:
        """
        Initializes the stream.

        Args:
            response: Open httpx response created with `stream=True`.
            chunk_size: Bytes requested from the network per chunk.
            key: Storage key being streamed.
        """
        self.response = response
        self.iterator = response.aiter_bytes(chunk_size)
        self.buffer = bytearray()
        self.position = 0
        self.closed = False
        self.key = key
        self.size = int(response.headers.get("content-length", -1))

    async def read(self, size: int = -1) -> bytes:
        """
        Asynchronously reads up to `size` bytes.

        Args:
            size: Number of bytes to read. A negative value reads to the end.

        Returns:
            The bytes read. Shorter than `size` only at end of stream.

        Raises:
            ValueError: If the stream is closed.
        """
        if self.closed:
            raise ValueError("I/O operation on closed stream")

        # Read everything that remains
        if size < 0:
            async for chunk in self.iterator:
                self.buffer.extend(chunk)

            count = len(self.buffer)
        else:
            # Pull chunks until the buffer can satisfy the request
            while len(self.buffer) < size:
                try:
                    self.buffer.extend(await anext(self.iterator))
                except StopAsyncIteration:
                    break

            count = min(size, len(self.buffer))

        data = bytes(self.buffer[:count])
        del self.buffer[:count]
        self.position += len(data)
        return data

    def tell(self) -> int:
        """
        Returns the number of bytes read so far.

        Returns:
            The current stream position.
        """
        return self.position

    async def __aiter__(self) -> AsyncIterator[bytes]:
        """
        Yields the remaining data in chunks.

        Yields:
            Successive chunks of the stream.
        """
        while True:
            chunk = await self.read(DEFAULT_CHUNK_SIZE)

            if not chunk:
                break

            yield chunk

    async def close(self) -> None:
        """
        Closes the stream and releases the network connection.
        """
        if not self.closed:
            await self.response.aclose()
            self.closed = True

    async def __aenter__(self) -> AsyncHTTPResponseStream:
        """
        Enters the async context manager.

        Returns:
            This stream.
        """
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        """
        Closes the stream on exit from the async context manager.
        """
        await self.close()


class AsyncBytesStream:
    """
    Async wrapper around an in-memory buffer.

    Used as the default async stream for backends that only implement the
    synchronous primitives and have no native streaming download.
    """

    def __init__(self, data: bytes) -> None:
        """
        Initializes the stream.

        Args:
            data: Bytes to serve.
        """
        self.buffer = io.BytesIO(data)

    async def read(self, size: int = -1) -> bytes:
        """
        Asynchronously reads up to `size` bytes.

        Args:
            size: Number of bytes to read. A negative value reads to the end.

        Returns:
            The bytes read.
        """
        return self.buffer.read(size)

    def tell(self) -> int:
        """
        Returns the current position.

        Returns:
            The current stream position.
        """
        return self.buffer.tell()

    async def close(self) -> None:
        """
        Closes the buffer.
        """
        self.buffer.close()

    async def __aenter__(self) -> AsyncBytesStream:
        """
        Enters the async context manager.

        Returns:
            This stream.
        """
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        """
        Closes the stream on exit from the async context manager.
        """
        await self.close()

