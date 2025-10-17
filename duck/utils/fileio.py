"""
FileIOStream module.

Provides both synchronous and asynchronous file streaming interfaces.
Ideal for efficient reading of large files using chunked reads and supporting
standard `seek`, `tell`, and `close` operations in both environments.

**Methods that do not need to be async:**  
Even in async context, the below methods don't necessarily need to be async:

1. `open` - Time complexity is O(1)
2. `seek` - Time complexity is O(1)
3. `tell` - Time complexity is O(1)

In async context, only `read`, `write`, and `close` need to be asynchronous.
"""

import io
import os
import asyncio
from typing import Optional

from duck.exceptions.all import AsyncViolationError
from duck.utils.asyncio import create_task, in_async_context
from duck.contrib.sync import sync_to_async


def to_async_fileio_stream(fileio_stream: "FileIOStream") -> "AsyncFileIOStream":
    """
    Converts file_io_stream to async file io stream if not already async.
    """
    assert isinstance(fileio_stream, FileIOStream), f"Provided file io stream not recognized, expected an instance of FileIOStream not {type(file_io_stream)}."
    
    if isinstance(fileio_stream, AsyncFileIOStream):
        return fileio_stream
        
    new_stream = AsyncFileIOStream(
        filepath=fileio_stream.filepath,
        chunk_size=fileio_stream.chunk_size,
        open_now=False,
        mode=fileio_stream._mode,
    )
    
    if not new_stream._file_size:
        # Set file size if not set
        new_stream._file_size = fileio_stream._file_size
    
    # Set _file
    new_stream._file = fileio_stream._file
    new_stream._pos = fileio_stream._pos
    
    # Modify old strem __del__ to do nothing instead of raising
    # "file must be closed before delete" error
    fileio_stream.ignore_file_open_on_delete = True
    
    # Return new stream
    return new_stream


class FileIOStream(io.IOBase):
    """
    Synchronous file streaming class that mimics `io.IOBase`.

    This class provides an interface to stream file contents using
    standard file operations such as `read`, `write`, `seek`, `tell`, and `close`.
    It is optimized for chunked reading of large files and is designed
    to be used strictly in synchronous contexts.
    """
    __slots__ = {
        "filepath",
        "chunk_size",
        "open_now",
        "ignore_file_open_on_delete",
        "_file",
        "_pos",
        "_mode",
        "_file_size",
        "_lock",
    }
    
    def __init__(
        self,
        filepath: str,
        chunk_size: int = 2 * 1024 * 1024,
        open_now: bool = False,
        mode: str = "rb",
    ):
        """
        Initialize the FileIOStream object.

        Args:
            filepath (str): Path to the file to be streamed.
            chunk_size (int): Maximum number of bytes to read or write at once. Default is 2MB.
            open_now (bool): Whether to open the file immediately. Defaults to False.
            mode (str): File open mode (default: 'rb').
        """
        self.filepath = filepath
        self.chunk_size = chunk_size
        self.ignore_file_open_on_delete = False
        self._file: Optional[io.BufferedIOBase] = None
        self._pos = 0
        self._mode = mode
        self._file_size = os.path.getsize(filepath) if os.path.exists(filepath) else 0
        
        if open_now:
            self.open()

    def is_open(self) -> bool:
        """
        Check if the file is currently open.
        """
        return self._file is not None

    def raise_if_in_async_context(self, message: str):
        """
        Raise an error if used inside an async context.
        """
        if in_async_context():
            raise AsyncViolationError(message)

    def open(self):
        """
        Open the file using the provided mode.
        """
        if not self._file:
            self._file = open(self.filepath, self._mode)

    def read(self, size: int = -1) -> bytes:
        """
        Synchronously read data from the file.

        Args:
            size (int): Number of bytes to read. -1 reads all.

        Returns:
            bytes: File data.
        """
        self.raise_if_in_async_context(
            "This method must be used in a synchronous environment. "
            "Consider using `AsyncFileIOStream.read` instead."
        )
        
        if not self.is_open():
            raise ValueError("File not opened. Call `open()` first.")

        data = self._file.read() if size == -1 else self._file.read(min(size, self.chunk_size))
        self._pos += len(data)
        return data

    def write(self, data: bytes) -> int:
        """
        Synchronously write data to the file.

        Args:
            data (bytes): Data to write.

        Returns:
            int: Number of bytes written.
        """
        self.raise_if_in_async_context(
            "This method must be used in a synchronous environment. "
            "Consider using `AsyncFileIOStream.write` instead."
        )
        
        if not self.is_open():
            raise ValueError("File not opened. Call `open()` first.")

        written = self._file.write(data)
        self._pos += written
        return written

    def seek(self, offset: int, whence: int = os.SEEK_SET):
        """
        Move the file pointer to a new location.
        """
        if not self.is_open():
            raise ValueError("File not opened. Call `open()` first.")
        self._file.seek(offset, whence)
        self._pos = self._file.tell()

    def tell(self) -> int:
        """
        Get the current position in the file.
        """
        return self._pos

    def close(self):
        """
        Close the file.
        """
        self.raise_if_in_async_context(
            "This method must be used in a synchronous environment. "
            "Consider using `AsyncFileIOStream.close` instead."
        )
        if self._file:
            self._file.close()
            self._file = None
    
    def __del__(self):
        """
        Ensure the file is closed on delete else it raises a RuntimeError if file not closed.
        """
        if self.is_open() and not self.ignore_file_open_on_delete:
            raise RuntimeError("File is not closed yet, please ensure the file is closed before deletion.")


class AsyncFileIOStream(FileIOStream):
    """
    Asynchronous file streaming class.

    Provides async-compatible methods for reading and writing files in
    a non-blocking way using threads via `asyncio.to_thread`.
    
    Notes:
    - This implementation is compatible with context managers.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._lock = asyncio.Lock()

    async def async_open(self): # instead of overriding open
        """
        Asynchronously open the file.
        """
        if not self.is_open():
            await sync_to_async(super().open)(self.filepath, self._mode)

    async def read(self, size: int = -1) -> bytes:
        """
        Asynchronously read from the file.

        Args:
            size (int): Max bytes to read. -1 reads full content.

        Returns:
            bytes: Data read from file.
        """
        async with self._lock:
            await self.async_open()
            
            # Seek is very fast, no need to make it async
            self._file.seek(self._pos)
            
            if size == -1:
                data = await sync_to_async(self._file.read)()
            
            else:
                data = await sync_to_async(self._file.read)(min(size, self.chunk_size))
            
            self._pos += len(data)
            return data

    async def write(self, data: bytes) -> int:
        """
        Asynchronously write data to the file.

        Args:
            data (bytes): Bytes to write.

        Returns:
            int: Number of bytes written.
        """
        async with self._lock:
            await self.async_open()
            
            # Seek musn't be async its very fast.
            self._file.seek(self._pos)
            
            written = await sync_to_async(self._file.write)(data)
            self._pos += written
            return written

    async def close(self):
        """
        Asynchronously close the file.
        """
        async with self._lock:
            if self.is_open():
                await sync_to_async(super().close)()
                
    async def __aenter__(self):
        await self.async_open()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()
