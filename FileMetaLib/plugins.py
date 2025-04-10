# plugins.py
"""
Plugin system for FileMetaLib.
"""

import os
import threading
from typing import Dict, List, Any, Optional, Set, Callable
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor

from .exceptions import PluginError


class FilePlugin(ABC):
    """
    Base class for file plugins.

    File plugins extract metadata from specific file types.
    """

    @abstractmethod
    def supports(self, path: str) -> bool:
        """
        Check if the plugin supports a file.

        Args:
            path: Path to the file.

        Returns:
            Whether the plugin supports the file.
        """
        pass

    @abstractmethod
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
        pass

    @property
    def priority(self) -> int:
        """
        Get the plugin priority.

        Higher priority plugins are executed first.

        Returns:
            Plugin priority.
        """
        return 0


class PluginRegistry:
    """
    Registry for file plugins.

    This class manages file plugins and dispatches file processing to them.
    """

    def __init__(self, max_workers: int = 4):
        """
        Initialize a new PluginRegistry.

        Args:
            max_workers: Maximum number of worker threads.
        """
        self._plugins = []
        self._executor = ThreadPoolExecutor(max_workers=max_workers)

    def register(self, plugin: FilePlugin) -> None:
        """
        Register a plugin.

        Args:
            plugin: Plugin to register.
        """
        self._plugins.append(plugin)

        # Sort plugins by priority (descending)
        self._plugins.sort(key=lambda p: p.priority, reverse=True)

    def process_file(self, path: str) -> Dict[str, Any]:
        """
        Process a file with all supporting plugins.

        Args:
            path: Path to the file.

        Returns:
            Combined metadata from all plugins.

        Raises:
            PluginError: If all plugins fail.
        """
        if not os.path.exists(path):
            raise PluginError(f"File not found: {path}")

        # Find supporting plugins
        supporting_plugins = [p for p in self._plugins if p.supports(path)]

        if not supporting_plugins:
            return {}

        # Process file with each plugin
        results = {}
        errors = []

        for plugin in supporting_plugins:
            try:
                metadata = plugin.extract(path)
                if metadata:
                    results.update(metadata)
            except Exception as e:
                errors.append(f"{plugin.__class__.__name__}: {str(e)}")

        # If all plugins failed, raise an error
        if errors and not results:
            raise PluginError(f"All plugins failed: {'; '.join(errors)}")

        return results

    def process_file_async(
        self, path: str, callback: Callable[[Dict[str, Any]], None]
    ) -> None:
        """
        Process a file asynchronously.

        Args:
            path: Path to the file.
            callback: Callback function to call with the results.
        """

        def _process():
            try:
                result = self.process_file(path)
                callback(result)
            except Exception as e:
                callback({"error": str(e)})

        self._executor.submit(_process)
