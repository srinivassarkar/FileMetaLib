# utils.py
"""
Utility functions for FileMetaLib.
"""

import os
import time
from typing import Dict, Any


def normalize_path(path: str) -> str:
    """
    Normalize a file path.

    Args:
        path: Path to normalize.

    Returns:
        Normalized path.
    """
    # Convert to absolute path
    if not os.path.isabs(path):
        path = os.path.abspath(path)

    # Normalize separators
    path = os.path.normpath(path)

    return path


def get_system_metadata(path: str) -> Dict[str, Any]:
    """
    Get system metadata for a file.

    Args:
        path: Path to the file.

    Returns:
        System metadata.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")

    stat = os.stat(path)

    return {
        "path": path,
        "filename": os.path.basename(path),
        "extension": os.path.splitext(path)[1].lower()[1:],
        "size": stat.st_size,
        "created": stat. st_birthtime,
        "modified": stat.st_mtime,
        "accessed": stat.st_atime,
    }


def format_timestamp(timestamp: float) -> str:
    """
    Format a timestamp as a string.

    Args:
        timestamp: Timestamp to format.

    Returns:
        Formatted timestamp.
    """
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))


def format_size(size: int) -> str:
    """
    Format a file size as a human-readable string.

    Args:
        size: Size in bytes.

    Returns:
        Formatted size.
    """
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024 or unit == "TB":
            return f"{size:.2f} {unit}"
        size /= 1024
