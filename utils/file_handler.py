import os
import tempfile
import logging
from pathlib import Path
from typing import Optional
from fastapi import UploadFile, HTTPException

logger = logging.getLogger(__name__)

# Configuration from environment
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", 100))
ALLOWED_EXTENSIONS = os.getenv(
    "ALLOWED_EXTENSIONS",
    "wav,mp3,m4a,flac,ogg,mp4,avi,mov"
).split(",")


def validate_audio_file(file: UploadFile) -> None:
    """
    Validate uploaded audio file

    Args:
        file: Uploaded file

    Raises:
        ValueError: If file validation fails
    """
    # Check if file exists
    if not file:
        raise ValueError("No file provided")

    # Check filename
    if not file.filename:
        raise ValueError("Invalid filename")

    # Check file extension
    file_ext = Path(file.filename).suffix.lower().lstrip(".")
    if file_ext not in ALLOWED_EXTENSIONS:
        raise ValueError(
            f"Invalid file type: {file_ext}. "
            f"Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    logger.info(f"File validation passed: {file.filename}")


async def save_upload_file(file: UploadFile) -> str:
    """
    Save uploaded file to temporary location

    Args:
        file: Uploaded file

    Returns:
        Path to saved temporary file
    """
    try:
        # Get file extension
        file_ext = Path(file.filename).suffix

        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=file_ext,
            prefix="audio_"
        )

        # Read and write file in chunks to handle large files
        chunk_size = 1024 * 1024  # 1MB chunks
        total_size = 0
        max_size = MAX_FILE_SIZE_MB * 1024 * 1024

        while True:
            chunk = await file.read(chunk_size)
            if not chunk:
                break

            total_size += len(chunk)
            if total_size > max_size:
                temp_file.close()
                os.unlink(temp_file.name)
                raise ValueError(
                    f"File too large. Maximum size: {MAX_FILE_SIZE_MB}MB"
                )

            temp_file.write(chunk)

        temp_file.close()
        logger.info(f"File saved to: {temp_file.name} ({total_size / 1024 / 1024:.2f}MB)")

        return temp_file.name

    except Exception as e:
        logger.error(f"Error saving file: {str(e)}")
        raise


def cleanup_file(file_path: str) -> None:
    """
    Delete temporary file

    Args:
        file_path: Path to file to delete
    """
    try:
        if file_path and os.path.exists(file_path):
            os.unlink(file_path)
            logger.info(f"Cleaned up file: {file_path}")
    except Exception as e:
        logger.warning(f"Error cleaning up file {file_path}: {str(e)}")
