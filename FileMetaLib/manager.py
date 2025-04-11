# manager.py
"""
Core manager class for FileMetaLib.
"""


import os
import time
import threading
from typing import Dict, List, Any, Optional, Union, Callable, Iterable

from .storage import StorageBackend, MemoryDB
from .registry import MetadataRegistry
from .plugins  import PluginRegistry, FilePlugin  
from .query import QueryEngine
from .exceptions import FileAccessError, PluginError
from .utils import normalize_path, get_system_metadata


class FileMetaManager:
    """
    Main interface for the FileMetaLib library.

    This class coordinates all components of the library:
    - Metadata Registry (in-memory index)
    - Storage Backend (persistence layer)
    - Plugin Registry (file type handlers)
    - Query Engine (search processor)

    Examples:
        >>> manager = FileMetaManager()
        >>> manager.add_file("document.pdf", {"tags": ["important", "work"], "owner": "Alice"})
        >>> metadata = manager.get_metadata("document.pdf")
        >>> files = manager.search({"tags": {"$contains": "important"}})
    """

    def __init__(
        self,
        storage_backend: Optional[StorageBackend] = None,
        auto_sync: bool = False,
        sync_interval: int = 300,
        thread_safe: bool = False,
    ):
        """
        Initialize a new FileMetaManager.

        Args:
            storage_backend: Storage backend to use. Defaults to MemoryDB.
            auto_sync: Whether to automatically sync with the file system.
            sync_interval: Interval in seconds for auto sync.
            thread_safe: Whether to use thread-safe operations.
        """
        self.storage = storage_backend or MemoryDB()
        self.registry = MetadataRegistry()
        self.plugins = PluginRegistry()
        self.query_engine = QueryEngine(self.registry)

        self.auto_sync = auto_sync
        self.sync_interval = sync_interval
        self.thread_safe = thread_safe
        self._lock = threading.RLock() if thread_safe else None

        # Load existing metadata from storage
        self._load_from_storage()

        # Start auto sync if enabled
        if auto_sync:
            self._start_auto_sync()

    def add_file(
        self, path: str, metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Add a file with metadata.

        Args:
            path: Path to the file.
            metadata: User-defined metadata to attach.

        Returns:
            Complete metadata including system metadata.

        Raises:
            FileAccessError: If the file cannot be accessed.
        """
        path = normalize_path(path)

        if not os.path.exists(path):
            raise FileAccessError(f"File not found: {path}")

        # Get system metadata
        system_meta = get_system_metadata(path)

        # Combine with user metadata
        full_metadata = {"system": system_meta, "user": metadata or {}}

        # Run plugins to extract additional metadata
        try:
            plugin_metadata = self._run_plugins(path)
            if plugin_metadata:
                full_metadata["plugin"] = plugin_metadata
        except PluginError as e:
            # Log error but continue
            print(f"Plugin error for {path}: {e}")

        # Store metadata
        if self.thread_safe and self._lock is not None:
            with self._lock:
                self.registry.add(path, full_metadata)
                self.storage.save(path, full_metadata)
        else:
            self.registry.add(path, full_metadata)
            self.storage.save(path, full_metadata)

        return full_metadata

    def get_metadata(self, path: str) -> Dict[str, Any]:
        """
        Get all metadata for a file.

        Args:
            path: Path to the file.

        Returns:
            Complete metadata for the file.

        Raises:
            FileAccessError: If the file has no metadata.
        """
        path = normalize_path(path)

        if self.thread_safe and self._lock is not None:
            with self._lock:
                metadata = self.registry.get(path)
        else:
            metadata = self.registry.get(path)

        if not metadata:
            raise FileAccessError(f"No metadata found for: {path}")

        return metadata

    def update_metadata(self, path: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update specific metadata fields for a file.

        Args:
            path: Path to the file.
            metadata: Metadata fields to update.

        Returns:
            Updated complete metadata.

        Raises:
            FileAccessError: If the file has no metadata.
        """
        path = normalize_path(path)

        if self.thread_safe and self._lock is not None:
            with self._lock:
                current = self.registry.get(path)
                if not current:
                    raise FileAccessError(f"No metadata found for: {path}")

                # Update user metadata
                current["user"].update(metadata)

                # Save updated metadata
                self.registry.update(path, current)
                self.storage.save(path, current)

                return current
        else:
            current = self.registry.get(path)
            if not current:
                raise FileAccessError(f"No metadata found for: {path}")

            # Update user metadata
            current["user"].update(metadata)

            # Save updated metadata
            self.registry.update(path, current)
            self.storage.save(path, current)

            return current

    def replace_metadata(self, path: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Replace all user metadata for a file.

        Args:
            path: Path to the file.
            metadata: New user metadata.

        Returns:
            Updated complete metadata.

        Raises:
            FileAccessError: If the file has no metadata.
        """
        path = normalize_path(path)

        if self.thread_safe and self._lock is not None:
            with self._lock:
                current = self.registry.get(path)
                if not current:
                    raise FileAccessError(f"No metadata found for: {path}")

                # Replace user metadata
                current["user"] = metadata

                # Save updated metadata
                self.registry.update(path, current)
                self.storage.save(path, current)

                return current
        else:
            current = self.registry.get(path)
            if not current:
                raise FileAccessError(f"No metadata found for: {path}")

            # Replace user metadata
            current["user"] = metadata

            # Save updated metadata
            self.registry.update(path, current)
            self.storage.save(path, current)

            return current

    def delete_metadata(self, path: str) -> None:
        """
        Remove all metadata for a file.

        Args:
            path: Path to the file.
        """
        path = normalize_path(path)

        if self.thread_safe and self._lock is not None:
            with self._lock:
                self.registry.remove(path)
                self.storage.delete(path)
        else:
            self.registry.remove(path)
            self.storage.delete(path)

    def search(self, query: Dict[str, Any]) -> Iterable[str]:
        """
        Search for files matching the query.

        Args:
            query: Query dictionary with search criteria.

        Returns:
            Iterable of file paths matching the query.
        """
        return self.query_engine.execute(query)

    def sync(self) -> Dict[str, int]:
        """
        Synchronize with the file system.

        Detects changes in the file system and updates metadata accordingly.

        Returns:
            Dictionary with counts of added, updated, and removed files.
        """
        if self.thread_safe and self._lock is not None:
            with self._lock:
                return self._do_sync()
        else:
            return self._do_sync()

    def cleanup_orphaned(self) -> int:
        """
        Remove metadata for files that no longer exist.

        Returns:
            Number of orphaned entries removed.
        """
        if self.thread_safe and self._lock is not None:
            with self._lock:
                return self._do_cleanup()
        else:
            return self._do_cleanup()

    def register_plugin(self, plugin) -> None:
        """
        Register a file plugin.

        Args:
            plugin: Plugin instance to register.
        """
        self.plugins.register(plugin)

    def export_metadata(self, output_path: str) -> int:
        """
        Export all metadata to a file.

        Args:
            output_path: Path to export to.

        Returns:
            Number of entries exported.
        """
        if self.thread_safe and self._lock is not None:
            with self._lock:
                all_metadata = {
                    path: self.registry.get(path)
                    for path in self.registry.get_all_paths()
                }

                with open(output_path, "w") as f:
                    import json

                    json.dump(all_metadata, f, indent=2)

                return len(all_metadata)
        else:
            all_metadata = {
                path: self.registry.get(path) for path in self.registry.get_all_paths()
            }

            with open(output_path, "w") as f:
                import json

                json.dump(all_metadata, f, indent=2)

            return len(all_metadata)

    def import_metadata(
        self, input_path: str, conflict_strategy: str = "replace"
    ) -> int:
        """
        Import metadata from a file.

        Args:
            input_path: Path to import from.
            conflict_strategy: Strategy for handling conflicts ('replace', 'merge', 'skip').

        Returns:
            Number of entries imported.
        """
        with open(input_path, "r") as f:
            import json

            imported_data = json.load(f)

        count = 0

        if self.thread_safe and self._lock is not None:
            with self._lock:
                for path, metadata in imported_data.items():
                    if self._import_entry(path, metadata, conflict_strategy):
                        count += 1
        else:
            for path, metadata in imported_data.items():
                if self._import_entry(path, metadata, conflict_strategy):
                    count += 1

        return count

    def _import_entry(
        self, path: str, metadata: Dict[str, Any], conflict_strategy: str
    ) -> bool:
        """
        Import a single metadata entry.

        Args:
            path: File path.
            metadata: Metadata to import.
            conflict_strategy: Strategy for handling conflicts.

        Returns:
            Whether the entry was imported.
        """
        existing = self.registry.get(path)

        if existing:
            if conflict_strategy == "skip":
                return False
            elif conflict_strategy == "merge":
                existing["user"].update(metadata.get("user", {}))
                if "plugin" in metadata:
                    existing.setdefault("plugin", {}).update(metadata["plugin"])
                self.registry.update(path, existing)
                self.storage.save(path, existing)
            else:  # replace
                self.registry.update(path, metadata)
                self.storage.save(path, metadata)
        else:
            self.registry.add(path, metadata)
            self.storage.save(path, metadata)

        return True

    def _load_from_storage(self) -> None:
        """Load existing metadata from storage into the registry."""
        for path, metadata in self.storage.load_all():
            self.registry.add(path, metadata)

    def _start_auto_sync(self) -> None:
        """Start the auto sync thread."""

        def sync_thread():
            while self.auto_sync:
                self.sync()
                time.sleep(self.sync_interval)

        thread = threading.Thread(target=sync_thread, daemon=True)
        thread.start()

    def _run_plugins(self, path: str) -> Dict[str, Any]:
        """
        Run plugins on a file to extract metadata.
        
        Args:
            path: Path to the file.
            
        Returns:
            Metadata extracted by plugins.
        """
        try:
            return self.plugins.process_file(path)
        except PluginError as e:
            # Log error but don't propagate
            print(f"Plugin error for {path}: {e}")
            return {}

    def _do_sync(self) -> Dict[str, int]:
        """
        Perform the actual synchronization.

        Returns:
            Dictionary with counts of added, updated, and removed files.
        """
        result = {"added": 0, "updated": 0, "removed": 0}

        # Get all registered paths
        registered_paths = set(self.registry.get_all_paths())
        existing_paths = set()

        # Check each registered path
        for path in registered_paths:
            if os.path.exists(path):
                existing_paths.add(path)

                # Check if file was modified
                system_meta = get_system_metadata(path)
                current_meta = self.registry.get(path)

                if current_meta["system"]["modified"] != system_meta["modified"]:
                    # File was modified, update metadata
                    current_meta["system"] = system_meta

                    # Run plugins again
                    try:
                        plugin_metadata = self._run_plugins(path)
                        if plugin_metadata:
                            current_meta["plugin"] = plugin_metadata
                    except PluginError:
                        pass

                    self.registry.update(path, current_meta)
                    self.storage.save(path, current_meta)
                    result["updated"] += 1
            else:
                # File no longer exists
                self.registry.remove(path)
                self.storage.delete(path)
                result["removed"] += 1

        return result

    def _do_cleanup(self) -> int:
        """
        Perform the actual cleanup of orphaned entries.

        Returns:
            Number of orphaned entries removed.
        """
        count = 0

        for path in self.registry.get_all_paths():
            if not os.path.exists(path):
                self.registry.remove(path)
                self.storage.delete(path)
                count += 1

        return count
