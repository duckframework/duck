"""
File request: Lively WebSocket utilities module.
"""
import uuid
import asyncio

from dataclasses import dataclass
from typing import Dict, List, Optional, Callable

from duck.shortcuts import jsonify, resolve
from duck.settings.loaded import SettingsLoaded
from duck.http.response import JsonResponse
from duck.http.fileuploads import BaseFileUpload, FileUploadError, FileTypeNotAllowedError
from duck.html.components.core.websocket import LivelyWebSocketView
from duck.html.components.core.opcodes import EventOpCode
from duck.views import csrf_exempt
from duck.contrib.sync import ensure_async


# Default seconds to wait for a client to start uploading
DEFAULT_FILE_TIMEOUT = 30

# Default total seconds to wait for file upload.
DEFAULT_TOTAL_FILE_TIMEOUT = 30 * 60

# Requested files
REQUESTED_FILES: Dict[str, "RequestedFileEntry"]  = {}

# Initiated File uploads
STARTED_FILE_UPLOADS: Dict[str, asyncio.Future] = {}


class FileUploadNotFoundError(FileUploadError):
    """
    Raised when a requested file upload cannot be found.
    """

class FileNotSelectedError(FileUploadError):
    """
    Raised when no selected file on file input.
    """

@dataclass(slots=True)
class RequestedFileEntry:
    """
    Requested file entry dataclass.
    """
    file_id: str
    future: asyncio.Future
    allowed_mimes: Optional[List[str]]
    token_secret: str
    on_progress: Optional[Callable]


def clean_requested_file(file_id: str):
    """
    Clean up a requested file entry after it resolves, times out, or errors.

    Args:
        file_id: Unique identifier of the requested file.
    """
    REQUESTED_FILES.pop(file_id, None)
    STARTED_FILE_UPLOADS.pop(file_id, None)


def mark_file_upload_started(file_id: str, strict: bool = False) -> bool:
    """
    Mark a pending file upload as started.

    Args:
        file_id: Unique identifier of the file upload.
        strict: Whether to raise `FileUploadNotFoundError` when the upload does not exist.

    Returns:
        True if the upload was successfully marked as started, otherwise
        False when `strict` is False.

    Raises:
        FileUploadNotFoundError: If the upload does not exist and `strict` is True.
        asyncio.InvalidStateError: If the upload has already been marked
            as started or otherwise has a completed future.
    """
    future = STARTED_FILE_UPLOADS.get(file_id)

    if future is None:
        if strict:
            raise FileUploadNotFoundError(f"File upload '{file_id}' not found.")
        return False

    if future.done():
        return True
        
    # Update future state
    future.set_result(True)
    
    # Return final state
    return True


def mark_file_upload_failed(file_id: str, reason: str = "", strict: bool = False) -> bool:
    """
    Mark a pending file upload as failed.

    Args:
        file_id: Unique identifier of the file upload.
        reason: Optional reason describing why the upload failed.
        strict: Whether to raise `FileUploadNotFoundError` when the upload does not exist.

    Returns:
        True if the upload was successfully marked as failed, otherwise
        False when `strict` is False.

    Raises:
        FileUploadNotFoundError: If the upload does not exist and `strict` is True.
        asyncio.InvalidStateError: If the upload has already been marked
            as failed or otherwise has a completed future.
    """
    future = STARTED_FILE_UPLOADS.get(file_id)
    
    if future is None:
        if strict:
            raise FileUploadNotFoundError(f"File upload '{file_id}' not found.")
        return False

    if future.done():
        return True

    # Generate message
    message = reason or f"File upload '{file_id}' failed."
    
    # Set exception
    future.set_exception(FileUploadError(message))
    
    # Return completion flag
    return True


async def notify_file_upload_progress(file_id: str, percent: float, strict: bool = False) -> bool:
    """
    Notify the server of a file upload's current progress.

    Args:
        file_id: Unique identifier of the file upload.
        percent: Upload progress as a percentage (0-100).
        strict: Whether to raise `FileUploadNotFoundError` when the upload does not exist.

    Returns:
        True if the progress was successfully notified, otherwise
        False when `strict` is False.

    Raises:
        FileUploadNotFoundError: If the upload does not exist and `strict` is True.
    """
    entry = REQUESTED_FILES.get(file_id)
    
    if entry is None:
        if strict:
            raise FileUploadNotFoundError(f"File upload '{file_id}' was not found.")
        return False

    if entry.on_progress is not None:
        await ensure_async(entry.on_progress)(percent)

    # Return final flag
    return True 


async def ws_request_file(
    form_id: str,
    name: str,
    ws: LivelyWebSocketView,
    *,
    allowed_mimes: Optional[List[str]] = None,
    on_progress: Optional[Callable[[int], None]] = None,
    timeout: float = DEFAULT_FILE_TIMEOUT,
    total_timeout = DEFAULT_TOTAL_FILE_TIMEOUT,
) -> BaseFileUpload:
    """
    Request a file from the client inside a Lively event handler.

    Sends a command over the websocket telling the client to open a file
    picker and upload the selected file to the receiving view, then waits
    for that upload to complete.

    Args:
        form_id: The ID of the form to target.
        name: Name of the file to request (usually the name of the file input).
        ws: Active Lively websocket connection for the current client.
        allowed_mimes: Optional list of mimetypes to expect from client.
        on_progress: Optional sync/async callable to call on file upload progress. Defaults to None.
        timeout: Seconds to wait before giving up on the upload.
        total_timeout: Total seconds in overall for the whole file upload to finish.
        
    Returns:
        BaseFileUpload instance inheriting from `io.BytesIO`.

    Raises:
        TimeoutError: If the client does not upload a file in time.
        ValueError: If on_progress is not None and not a callable.
    """
    from duck.http.middlewares.security.csrf import (
        generate_csrf_secret,
        mask_cipher_secret,
    )
    
    if on_progress and not callable(on_progress):
        raise ValueError("Argument on_progress must be a callable or None.")
    
    file_id = str(uuid.uuid4()) # Generate unique file ID
    event_loop = asyncio.get_event_loop()
    file_future = event_loop.create_future()
    file_started_future = event_loop.create_future()
    allowed_mimes = allowed_mimes or []
    upload_url = resolve("lively-receive-ws-file")
    auth_secret = generate_csrf_secret()
    auth_token = mask_cipher_secret(auth_secret)
    fire_on_progress = bool(on_progress)
    
    # Add file upload started future
    STARTED_FILE_UPLOADS[file_id] = file_started_future
    
    # Add future to the requested files
    REQUESTED_FILES[file_id] = RequestedFileEntry(
        file_id=file_id,
        future=file_future,
        allowed_mimes=allowed_mimes,
        token_secret=auth_secret,
        on_progress=on_progress,
    )

    # Tell client to open its file picker and upload to the receiving view
    await ws.send_data([EventOpCode.REQUEST_FILE, [form_id, file_id, name, upload_url, allowed_mimes, fire_on_progress, auth_token], ])
    
    try:
        try:
            file_started = await asyncio.wait_for(file_started_future, timeout=timeout)
        except asyncio.TimeoutError as e:
            raise TimeoutError(f"File upload did not start in {timeout} seconds.")
            
        try:
            uploaded_file = await asyncio.wait_for(file_future, timeout=total_timeout)
        except asyncio.TimeoutError:
            raise TimeoutError(f"File upload slow, total file upload failed to complete in {total_timeout} seconds.")
            
        if fire_on_progress:
            # When progress reaches 100, the requested file might be already cleaned up in finally block so
            # Lets simulate it, the tradeoff is that progress for 100 might sometimes be called twice.
            await notify_file_upload_progress(file_id, 100)
            
        # Return the final uploaded file.
        return uploaded_file
    
    except FileTypeNotAllowedError:
        raise
        
    except FileUploadError as e:
        error = str(e)
        error_lower = error.lower()
        
        if "no file selected" in error_lower:
            raise FileNotSelectedError(error)
        
        if "file type" in error_lower and "allowed" in error_lower:
            raise FileTypeNotAllowedError(error)
        
        # Reraise exception
        raise
    
    finally:
        # Clean data after if not done yet.
        clean_requested_file(file_id)


@csrf_exempt
async def receive_ws_file(request) -> JsonResponse:
    """
    View for receiving an uploaded file from the client.

    Saves the file using the configured upload handler and resolves the
    matching future so the waiting async_request_file call can continue.

    Args:
        request: Incoming Duck request carrying the multipart file upload.

    Returns:
        JSON response acknowledging receipt or describing the error.
    """
    from duck.http.middlewares.security.csrf import unmask_cipher_token
    
    file_id: Optional[str] = request.POST.get("id")
    auth_token: Optional[str] = request.POST.get("token", "")
    uploaded_file: Optional[BaseFileUpload] = request.FILES.get(file_id)
    requested_file_entry: Optional[RequestedFileEntry] = REQUESTED_FILES.get(file_id, None)
    
    # Reject uploads with no matching pending request
    if not requested_file_entry or not uploaded_file:
        return jsonify({"error": "Invalid or expired file_id"}, status_code=400)
    
    # Verify auth token
    auth_secret = requested_file_entry.token_secret
    
    try:
        declared_secret = unmask_cipher_token(auth_token)
        
        if declared_secret != auth_secret:
            raise ValueError("Invalid file token")
            
    except ValueError:
        return jsonify({"error": "Invalid or empty file token"}, status_code=400)
          
    # Get the future
    future = requested_file_entry.future
    
    if future.done():
        return jsonify({"error": "Upload already completed"}, status_code=409)

    # Do some validations here.
    allowed_mimes = requested_file_entry.allowed_mimes
    
    try:
        # Verify allowed file upload data
        uploaded_file.verify(allowed_mimes=allowed_mimes)
        
        # Set future result
        future.set_result(uploaded_file)
        
    except Exception as e:
        future.set_exception(e)
        
    return jsonify({"status": "received", "id": file_id})
