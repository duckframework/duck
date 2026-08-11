"""
Module containing classes for storing uploaded file data.
"""

import io
import os

from typing import Optional

from duck.settings import SETTINGS
from duck.contrib.sync import ensure_async
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
        assert filename or False, "Filename is required"

        if not isinstance(initial_bytes, bytes):
            raise FileUploadError(f"Bytes required not {type(initial_bytes)}")

        super().__init__(initial_bytes)

        # Map additional keyword arguments to instance attributes
        map_data_to_object(self, kw)
        
    def normalize_filename(self) -> str:
        """
        Normalize the filename by spaces or invalid characters.

        Returns:
            str: The normalized filename.
        """
        self.filename = self.filename.strip().replace(" ", "-")
        return self.filename
        
    def geturl(self, absolute=True):
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
        self.seek(0, 2) # end of file
        size = self.tell()
        self.seek(curpos)
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
                raise DisallowedMimeError(f"Mimetype `{detected}` not allowed. Allowed mimes: {allowed_mimes}")
                
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
    Class for persistent storage of file uploads on disk in a specified directory.

    Attributes:
        filename (str): The name of the file.
        initial_bytes (bytes): The initial byte content of the file.
        directory (str): The directory where the file will be saved.
        overwrite_existing_file (bool): Whether to overwrite existing file in directory when saving
    """

    def __init__(
        self,
        filename: str,
        initial_bytes: bytes = b"",
        directory: str = SETTINGS["FILE_UPLOAD_DIR"],
        overwrite_existing_file=True,
        **kw,
    ):
        self.initial_bytes = initial_bytes
        self.directory = directory
        self.filename = filename
        self.overwrite_existing_file = overwrite_existing_file

        if not os.path.isdir(directory):
            raise FileNotFoundError(f"Directory {directory} does not exist")

        if not filename:
            raise FileUploadError(f"Please provide filename, should not be '{filename}' ")
            
        self.filepath = os.path.join(directory, filename)

        if os.path.isfile(self.filepath) and not overwrite_existing_file:
            raise FileUploadError(
                f"File '{self.filepath}' already exists and argument 'overwrite_existing_file' is not True "
            )
            
        super().__init__(filename, initial_bytes, **kw)

    def save_to_file(self):
        """
        Save the uploaded data to the specified file path.

        Returns:
            int: The number of bytes written.
        """
        return super().save_to_file(self.filepath)

    def save(self):
        """
        Save the uploaded data by writing it to the specified file path.
        """
        self.save_to_file()
