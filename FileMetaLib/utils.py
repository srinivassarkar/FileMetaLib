# utils.py
"""
Utility functions for FileMetaLib.
"""

import os
import time
from typing import Dict, Any
from datetime import datetime
from typing import Dict, Any
import os
import platform

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




def format_time(epoch_time: float) -> str:
    """Convert epoch time to human-readable format."""
    return datetime.fromtimestamp(epoch_time).strftime("%Y-%m-%d %H:%M:%S")

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

    # Handle platforms that may not have st_birthtime
    if hasattr(stat, "st_birthtime"):
        created_time = stat.st_birthtime
    else:
        created_time = stat.st_ctime if platform.system() == "Windows" else stat.st_mtime

    return {
        "path": path,
        "filename": os.path.basename(path),
        "extension": os.path.splitext(path)[1].lower()[1:],
        "size": stat.st_size,
        "created": format_time(created_time),
        "modified": format_time(stat.st_mtime),
        "accessed": format_time(stat.st_atime),
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
