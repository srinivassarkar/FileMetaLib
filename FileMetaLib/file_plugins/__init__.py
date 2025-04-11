# plugins/__init__.py
"""
Plugins for FileMetaLib.
"""

from ..plugins import FilePlugin  # Import from parent package

# Import specific plugins to make them available
from .image_plugin import ImagePlugin

__all__ = ["ImagePlugin"]