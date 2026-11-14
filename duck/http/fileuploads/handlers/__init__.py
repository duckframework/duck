"""
Module containing classes for storing uploaded file data.
"""

import io
import os

from typing import Optional

from duck.settings import SETTINGS
from duck.contrib.sync import ensure_async
from duck.contrib.storage.backends import StorageBackend, ProgressCallback
from duck.utils.slug import slugify
from duck.utils.object_mapping import map_data_to_object



class FileUploadError(Exception):
    """
    Base exception class for file upload errors
    """


class FileVerificationError(FileUploadError):
    """
    Raised on verification failure for uploaded files.
    """


class FileTypeNotAllowedError(FileUploadError):
    """
    Raised when a detected data mimetype doesn't match any mime in allowed mimes list.
    """


class BaseFileUpload(io.BytesIO):
    """
    Base class for storing file uploads data.

    Attributes:
        initial_bytes (bytes): The initial byte content of the file.
        filename (str): The name of the file.
        name (str, optional): Name of the form field for this File. (optional)
        content_type (str, optional): The mimetype of the uploaded content. (optional)
        content_disposition (str, optional): The file upload content disposition. (optional)
    """

    def __init__(self, filename: str, initial_bytes: bytes = b"", **kw):
        self.initial_bytes = initial_bytes
        self.filename = filename
        self.name = None
        self.content_type = None
        self.content_disposition = None

        # Ensure filename provided
        assert filename or False, "Filename is required"

        if not isinstance(initial_bytes, bytes):
            raise FileUploadError(f"Bytes required not {type(initial_bytes)}")

        super().__init__(initial_bytes)

        # Map additional keyword arguments to instance attributes
        map_data_to_object(self, kw)
        
    def get_storage_backend(self) -> StorageBackend:
        """
        Returns the current storage backend for file uploads.
        """
        from duck.settings.loaded import SettingsLoaded

        return SettingsLoaded.MEDIAFILES_BACKEND.getresult()

    def normalize_filename(self) -> str:
        """
        Normalize the filename by spaces or invalid characters.

        Returns:
            str: The normalized filename.
        """
        self.filename = slugify(self.filename.strip())

        return self.filename
        
    def geturl(self, absolute: bool = True):
        """
        Get the URL for accessing the uploaded file.

        Returns:
            str: The URL for accessing the uploaded file.
        """
        from duck.shortcuts import media

        return media(self.filename, absolute=absolute)

    def getsize(self):
        """
        Returns the file IO object total bytes.
        """
        curpos = self.tell()

        # Seek to end of file
        self.seek(0, 2)

        try:
            # Get the current size
            size = self.tell()
        
        finally:
            self.seek(curpos)

        # Return the current size
        return size
    
    def guess_mimetype(self) -> Optional[str]:
        """
        Returns the guessed mimetype for the uploaded file.
        
        Notes
        - This method guesses the mimetype for the file upload using the provided bytes rather than the 
               the filename, because it bypasses altered filenames thereby increasing security.
        """
        from duck.http.mimes import guess_data_mimetype

        return guess_data_mimetype(self.getvalue())
        
    def verify(self, allowed_mimes: list[str] | None = None) -> None:
        """
        Verify the uploaded file's declared MIME type against its detected type.
    
        Args:
            allowed_mimes: Optional MIME types permitted for the upload.
    
        Raises:
            FileTypeNotAllowedError: If the detected MIME type is not allowed.
            FileVerificationError: If the declared MIME type does not match the
                detected MIME type.
    
        Notes:
            The detected MIME type should be determined from the file's content
            (for example, using magic bytes), not from its filename or extension.
        """
        normalize_mime = lambda m: m.split(";", 1)[0].strip().lower()
        
        # Set some variables
        declared = normalize_mime(getattr(self, "content_type", ""))
        detected = normalize_mime(self.guess_mimetype() or "")
        allowed_mimes = [normalize_mime(m) for m in (allowed_mimes or [])]
        
        if declared and detected:
            if declared != detected:
                raise FileVerificationError(
                    f"File upload verification failed: received "
                    f"`{declared}` but detected `{detected}`."
                )
    
        if allowed_mimes:
            if detected not in allowed_mimes:
                raise FileTypeNotAllowedError(f"Mimetype `{detected}` not allowed. Allowed mimes: {allowed_mimes}")
                
    def save_to_file(self, filepath: str):
        """
        Save the uploaded data to a file.

        Args:
            filepath (str): The path where the file will be saved.

        Returns:
            int: The number of bytes written.
        """
        with open(filepath, "wb") as f:
            return f.write(self.getvalue())

    def save(self):
        """
        Save the uploaded data. This method should be implemented by subclasses.

        Raises:
            NotImplementedError: If the method is not implemented by subclasses.
        """
        raise NotImplementedError("Implementation of the method 'save' is required")

    async def async_save(self):
        """
        Asynchronously save the data - defaults to wrapped `save()` using `ensure_async`.
        """
        await ensure_async(self.save)()
      
    def __repr__(self):
        r = f"<{self.__class__.__name__} {self.filename}"

        if hasattr(self, "content_type"):
            r += f" ({self.content_type})>"
        else:
            r += ">"
            
        return r


class TemporaryFileUpload(BaseFileUpload):
    """
    Class for temporarily storing file upload data in memory.
    """

    def save(self):
        """
        Save the uploaded data. In this case, the method does nothing.
        """
        raise NotImplementedError("TemporaryFileUpload cannot be saved as it is stored in memory, implement this method.")


class PersistentFileUpload(BaseFileUpload):
    """
    Class for persistent storage of file uploads to the mediafiles storage backend.

    Notes:
        This saves the uploaded file to the current storage backend.
    """

    def save(self, folder: str = "", on_progress: ProgressCallback | None = None):
        """
        Save file to storage backend backend with progress reporting.

        Args:
            folder (str, optional): The optional folder to save the file in, e.g., `"images"` or `"video"`.
            on_progress (ProgressCallback, optional): Function to call on save progress.
        """
        
        backend = self.get_storage_backend()

        # Save file to backend
        backend.save(self.initial_bytes, self.filename, folder=folder, on_progress=on_progress)

    async def async_save(self, folder: str = "", on_progress: ProgressCallback | None = None):
        """
        Asynchronously save file to storage backend with progress reporting.

        Args:
            folder (str, optional): The optional folder to save the file in, e.g., `"images"` or `"video"`.
            on_progress (ProgressCallback, optional): Function to call on save progress.
        """
        
        backend = self.get_storage_backend()

        # Save file to backend
        await backend.async_save(self.initial_bytes, self.filename, folder=folder, on_progress=on_progress)

