# registry.py
"""
Metadata registry for FileMetaLib.
"""

from typing import Dict, List, Any, Set, Optional


class MetadataRegistry:
    """
    In-memory index for metadata.

    This class maintains primary and secondary indexes for fast access to metadata.
    """

    def __init__(self):
        """Initialize a new MetadataRegistry."""
        # Primary index: path -> metadata
        self._primary_index = {}

        # Secondary indexes: field -> paths
        self._secondary_indexes = {"system": {}, "user": {}, "plugin": {}}

    def add(self, path: str, metadata: Dict[str, Any]) -> None:
        """
        Add metadata for a file.

        Args:
            path: Path to the file.
            metadata: Metadata to add.
        """
        # Add to primary index
        self._primary_index[path] = metadata

        # Add to secondary indexes
        self._index_metadata(path, metadata)

    def get(self, path: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a file.

        Args:
            path: Path to the file.

        Returns:
            Metadata for the file, or None if not found.
        """
        return self._primary_index.get(path)

    def update(self, path: str, metadata: Dict[str, Any]) -> None:
        """
        Update metadata for a file.

        Args:
            path: Path to the file.
            metadata: New metadata.
        """
        # Remove old secondary indexes
        if path in self._primary_index:
            self._remove_from_secondary_indexes(path, self._primary_index[path])

        # Update primary index
        self._primary_index[path] = metadata

        # Update secondary indexes
        self._index_metadata(path, metadata)

    def remove(self, path: str) -> None:
        """
        Remove metadata for a file.

        Args:
            path: Path to the file.
        """
        # Remove from secondary indexes
        if path in self._primary_index:
            self._remove_from_secondary_indexes(path, self._primary_index[path])

        # Remove from primary index
        if path in self._primary_index:
            del self._primary_index[path]

    def get_all_paths(self) -> List[str]:
        """
        Get all paths in the registry.

        Returns:
            List of all paths.
        """
        return list(self._primary_index.keys())

    def find_by_field(self, section: str, field: str, value: Any) -> Set[str]:
        """
        Find paths by field value.

        Args:
            section: Metadata section ('system', 'user', or 'plugin').
            field: Field name.
            value: Field value.

        Returns:
            Set of paths with matching field value.
        """
        if section not in self._secondary_indexes:
            return set()

        section_index = self._secondary_indexes[section]
        if field not in section_index:
            return set()

        field_index = section_index[field]
        if value not in field_index:
            return set()

        return field_index[value].copy()

    def _index_metadata(self, path: str, metadata: Dict[str, Any]) -> None:
        """
        Index metadata in secondary indexes.

        Args:
            path: Path to the file.
            metadata: Metadata to index.
        """
        for section, section_data in metadata.items():
            if section not in self._secondary_indexes:
                continue

            section_index = self._secondary_indexes[section]

            for field, value in section_data.items():
                # Skip non-indexable values
                if not self._is_indexable(value):
                    continue

                # Create field index if it doesn't exist
                if field not in section_index:
                    section_index[field] = {}

                field_index = section_index[field]

                # Create value index if it doesn't exist
                if value not in field_index:
                    field_index[value] = set()

                # Add path to value index
                field_index[value].add(path)

    def _remove_from_secondary_indexes(
        self, path: str, metadata: Dict[str, Any]
    ) -> None:
        """
        Remove path from secondary indexes.

        Args:
            path: Path to the file.
            metadata: Metadata to remove.
        """
        for section, section_data in metadata.items():
            if section not in self._secondary_indexes:
                continue

            section_index = self._secondary_indexes[section]

            for field, value in section_data.items():
                # Skip non-indexable values
                if not self._is_indexable(value):
                    continue

                # Skip if field index doesn't exist
                if field not in section_index:
                    continue

                field_index = section_index[field]

                # Skip if value index doesn't exist
                if value not in field_index:
                    continue

                # Remove path from value index
                field_index[value].discard(path)

                # Clean up empty indexes
                if not field_index[value]:
                    del field_index[value]

                if not field_index:
                    del section_index[field]

    def _is_indexable(self, value: Any) -> bool:
        """
        Check if a value is indexable.

        Args:
            value: Value to check.

        Returns:
            Whether the value is indexable.
        """
        return isinstance(value, (str, int, float, bool)) or value is None
