# plugins/image_plugin.py
"""
Image file plugin for FileMetaLib.
"""

import os
from typing import Dict, Any

from ..file_plugins import FilePlugin
from ..exceptions import PluginError


class ImagePlugin(FilePlugin):
    """
    Plugin for extracting metadata from image files.

    This plugin uses the Pillow library to extract metadata from image files.
    """

    def __init__(self):
        """Initialize a new ImagePlugin."""
        try:
            from PIL import Image, ExifTags

            self.Image = Image
            self.ExifTags = ExifTags
        except ImportError:
            raise PluginError(
                "Pillow library not installed. Install with 'pip install Pillow'."
            )

    def supports(self, path: str) -> bool:
        """
        Check if the plugin supports a file.

        Args:
            path: Path to the file.

        Returns:
            Whether the plugin supports the file.
        """
        ext = os.path.splitext(path)[1].lower()
        return ext in [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff"]

    def extract(self, path: str) -> Dict[str, Any]:
        """
        Extract metadata from a file.

        Args:
            path: Path to the file.

        Returns:
            Extracted metadata.

        Raises:
            PluginError: If metadata extraction fails.
        """
        try:
            image = self.Image.open(path)

            metadata = {
                "width": image.width,
                "height": image.height,
                "format": image.format,
                "mode": image.mode,
            }

            # Extract EXIF data if available
            if hasattr(image, "_getexif") and image._getexif():
                exif = {
                    self.ExifTags.TAGS.get(k, k): v
                    for k, v in image._getexif().items()
                    if k in self.ExifTags.TAGS
                }

                # Convert binary data to string representation
                for key, value in exif.items():
                    if isinstance(value, bytes):
                        exif[key] = str(value)

                metadata["exif"] = exif

            return metadata
        except Exception as e:
            raise PluginError(f"Failed to extract image metadata: {str(e)}")

    @property
    def priority(self) -> int:
        """
        Get the plugin priority.

        Returns:
            Plugin priority.
        """
        return 10
