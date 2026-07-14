"""Validation and persistence for uploaded match recordings."""

from pathlib import Path
from typing import Protocol
from uuid import uuid4

from config import INPUT_DIR, MAX_UPLOAD_SIZE_MB


class UploadedVideo(Protocol):
    """Minimal interface supplied by Streamlit's uploaded file object."""

    name: str
    size: int

    def getbuffer(self) -> memoryview: ...


class UploadValidationError(ValueError):
    """Raised when an uploaded file cannot be used as a match recording."""


def validate_mp4_upload(upload: UploadedVideo) -> None:
    """Reject missing, non-MP4, empty, or oversized files before saving them."""
    if not upload.name.lower().endswith(".mp4"):
        raise UploadValidationError("Please upload an MP4 match recording.")
    if upload.size <= 0:
        raise UploadValidationError("The uploaded file is empty.")
    if upload.size > MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        raise UploadValidationError(
            f"The video exceeds the {MAX_UPLOAD_SIZE_MB} MB upload limit."
        )


def save_uploaded_video(upload: UploadedVideo, destination: Path = INPUT_DIR) -> Path:
    """Store an upload with a generated filename, never the user-provided path."""
    validate_mp4_upload(upload)
    destination.mkdir(parents=True, exist_ok=True)
    video_path = destination / f"match_{uuid4().hex}.mp4"
    video_path.write_bytes(upload.getbuffer())
    return video_path
