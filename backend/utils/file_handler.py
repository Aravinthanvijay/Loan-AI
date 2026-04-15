"""
File upload and download handler.
Manages secure file storage and retrieval for uploaded documents.
"""

import os
import uuid
import aiofiles
import hashlib
import logging
from typing import Tuple, Optional
from datetime import datetime
from fastapi import UploadFile, HTTPException

from backend.config import settings

logger = logging.getLogger(__name__)

ALLOWED_MIME_TYPES = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/jpg": "jpg",
    "application/pdf": "pdf",
}


class FileHandler:
    """Handle secure file upload and management."""

    @staticmethod
    async def save_upload(
        file: UploadFile,
        subfolder: str = "documents",
        user_id: str = None,
    ) -> Tuple[str, str, int]:
        """
        Save uploaded file securely.

        Args:
            file: FastAPI UploadFile object
            subfolder: Subdirectory within uploads folder
            user_id: Associated user ID (used in filename)

        Returns:
            Tuple of (filename, file_path, file_size)
        """
        # Validate file type
        content_type = file.content_type or ""
        if content_type not in ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"File type {content_type} not allowed. Use JPG, PNG, or PDF."
            )

        # Read file content
        content = await file.read()
        file_size = len(content)

        # Check size limit
        max_size = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        if file_size > max_size:
            raise HTTPException(
                status_code=400,
                detail=f"File size {file_size / 1024 / 1024:.1f}MB exceeds limit of {settings.MAX_UPLOAD_SIZE_MB}MB"
            )

        # Generate secure filename
        ext = ALLOWED_MIME_TYPES[content_type]
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        uid = str(uuid.uuid4())[:8]
        user_prefix = f"{user_id[:8]}_" if user_id else ""
        filename = f"{user_prefix}{timestamp}_{uid}.{ext}"

        # Create directory
        save_dir = os.path.join(settings.UPLOAD_DIR, subfolder)
        os.makedirs(save_dir, exist_ok=True)
        file_path = os.path.join(save_dir, filename)

        # Save file
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(content)

        logger.info(f"Saved uploaded file: {file_path} ({file_size} bytes)")
        return filename, file_path, file_size

    @staticmethod
    async def read_file(file_path: str) -> bytes:
        """Read file contents as bytes."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        async with aiofiles.open(file_path, 'rb') as f:
            return await f.read()

    @staticmethod
    def delete_file(file_path: str) -> bool:
        """Delete a file safely."""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
        except Exception as e:
            logger.error(f"Failed to delete file {file_path}: {e}")
        return False

    @staticmethod
    def get_file_hash(file_path: str) -> str:
        """Get SHA256 hash of file (for duplicate detection)."""
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256.update(chunk)
        return sha256.hexdigest()