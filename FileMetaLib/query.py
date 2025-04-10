# query.py
"""
Query engine for FileMetaLib.
"""

import re
from typing import Dict, List, Any, Set, Callable, Iterable

from .registry import MetadataRegistry


class QueryEngine:
    """
    Query engine for searching metadata.

    This class processes queries and returns matching files.
    """

    def __init__(self, registry: MetadataRegistry):
        """
        Initialize a new QueryEngine.

        Args:
            registry: Metadata registry to query.
        """
        self.registry = registry

        # Register operators
        self._operators = {
            "$eq": self._op_eq,
            "$ne": self._op_ne,
            "$gt": self._op_gt,
            "$gte": self._op_gte,
            "$lt": self._op_lt,
            "$lte": self._op_lte,
            "$in": self._op_in,
            "$nin": self._op_nin,
            "$contains": self._op_contains,
            "$startswith": self._op_startswith,
            "$endswith": self._op_endswith,
            "$regex": self._op_regex,
            "$exists": self._op_exists,
            "$type": self._op_type,
            "$and": self._op_and,
            "$or": self._op_or,
            "$not": self._op_not,
        }

    def execute(self, query: Dict[str, Any]) -> Iterable[str]:
        """
        Execute a query.

        Args:
            query: Query dictionary.

        Returns:
            Iterable of file paths matching the query.
        """
        # Get all paths
        all_paths = set(self.registry.get_all_paths())

        # Apply filters
        result_paths = self._apply_filters(all_paths, query)

        return result_paths

    def _apply_filters(self, paths: Set[str], query: Dict[str, Any]) -> Set[str]:
        """
        Apply filters to paths.

        Args:
            paths: Set of paths to filter.
            query: Query dictionary.

        Returns:
            Filtered set of paths.
        """
        result = paths.copy()

        for key, value in query.items():
            if key.startswith("$"):
                # Operator at top level
                if key in self._operators:
                    result = self._operators[key](result, value)
            else:
                # Field query
                section, field = self._parse_field(key)

                if isinstance(value, dict) and all(
                    k.startswith("$") for k in value.keys()
                ):
                    # Operator query
                    for op, op_value in value.items():
                        if op in self._operators:
                            result = self._filter_by_field_op(
                                result, section, field, op, op_value
                            )
                else:
                    # Simple equality query
                    result = self._filter_by_field_eq(result, section, field, value)

        return result

    def _parse_field(self, key: str) -> tuple:
        """
        Parse a field key into section and field.

        Args:
            key: Field key.

        Returns:
            Tuple of (section, field).
        """
        if "." in key:
            section, field = key.split(".", 1)
        else:
            section, field = "user", key

        return section, field

    def _filter_by_field_eq(
        self, paths: Set[str], section: str, field: str, value: Any
    ) -> Set[str]:
        """
        Filter paths by field equality.

        Args:
            paths: Set of paths to filter.
            section: Metadata section.
            field: Field name.
            value: Field value.

        Returns:
            Filtered set of paths.
        """
        # Try to use index if available
        if isinstance(value, (str, int, float, bool)) or value is None:
            indexed_paths = self.registry.find_by_field(section, field, value)
            if indexed_paths:
                return paths.intersection(indexed_paths)

        # Fall back to manual filtering
        result = set()

        for path in paths:
            metadata = self.registry.get(path)
            if not metadata or section not in metadata:
                continue

            section_data = metadata[section]
            if field not in section_data:
                continue

            if section_data[field] == value:
                result.add(path)

        return result

    def _filter_by_field_op(
        self, paths: Set[str], section: str, field: str, op: str, value: Any
    ) -> Set[str]:
        """
        Filter paths by field operation.

        Args:
            paths: Set of paths to filter.
            section: Metadata section.
            field: Field name.
            op: Operation.
            value: Operation value.

        Returns:
            Filtered set of paths.
        """
        result = set()

        for path in paths:
            metadata = self.registry.get(path)
            if not metadata or section not in metadata:
                continue

            section_data = metadata[section]
            if field not in section_data:
                continue

            field_value = section_data[field]

            if self._operators[op]([field_value], value):
                result.add(path)

        return result

    # Operator implementations

    def _op_eq(self, values: Any, value: Any) -> bool:
        """Equal operator."""
        if isinstance(values, set):
            return {
                path
                for path in values
                if self.registry.get(path) is not None
                and self._compare_eq(self.registry.get(path), value)
            }
        return values == value

    def _op_ne(self, values: Any, value: Any) -> bool:
        """Not equal operator."""
        if isinstance(values, set):
            return {
                path
                for path in values
                if self.registry.get(path) is not None
                and self._compare_ne(self.registry.get(path), value)
            }
        return values != value

    def _op_gt(self, values: Any, value: Any) -> bool:
        """Greater than operator."""
        if isinstance(values, set):
            return {
                path
                for path in values
                if self.registry.get(path) is not None
                and self._compare_gt(self.registry.get(path), value)
            }
        return values > value

    def _op_gte(self, values: Any, value: Any) -> bool:
        """Greater than or equal operator."""
        if isinstance(values, set):
            return {
                path
                for path in values
                if self.registry.get(path) is not None
                and self._compare_gte(self.registry.get(path), value)
            }
        return values >= value

    def _op_lt(self, values: Any, value: Any) -> bool:
        """Less than operator."""
        if isinstance(values, set):
            return {
                path
                for path in values
                if self.registry.get(path) is not None
                and self._compare_lt(self.registry.get(path), value)
            }
        return values < value

    def _op_lte(self, values: Any, value: Any) -> bool:
        """Less than or equal operator."""
        if isinstance(values, set):
            return {
                path
                for path in values
                if self.registry.get(path) is not None
                and self._compare_lte(self.registry.get(path), value)
            }
        return values <= value

    def _op_in(self, values: Any, value: Any) -> bool:
        """In operator."""
        if isinstance(values, set):
            return {
                path
                for path in values
                if self.registry.get(path) is not None
                and self._compare_in(self.registry.get(path), value)
            }
        return values in value

    def _op_nin(self, values: Any, value: Any) -> bool:
        """Not in operator."""
        if isinstance(values, set):
            return {
                path
                for path in values
                if self.registry.get(path) is not None
                and self._compare_nin(self.registry.get(path), value)
            }
        return values not in value

    def _op_contains(self, values: Any, value: Any) -> bool:
        """Contains operator."""
        if isinstance(values, set):
            return {
                path
                for path in values
                if self.registry.get(path) is not None
                and self._compare_contains(self.registry.get(path), value)
            }
        return value in values

    def _op_startswith(self, values: Any, value: Any) -> bool:
        """Starts with operator."""
        if isinstance(values, set):
            return {
                path
                for path in values
                if self.registry.get(path) is not None
                and self._compare_startswith(self.registry.get(path), value)
            }
        return isinstance(values, str) and values.startswith(value)

    def _op_endswith(self, values: Any, value: Any) -> bool:
        """Ends with operator."""
        if isinstance(values, set):
            return {
                path
                for path in values
                if self.registry.get(path) is not None
                and self._compare_endswith(self.registry.get(path), value)
            }
        return isinstance(values, str) and values.endswith(value)

    def _op_regex(self, values: Any, value: Any) -> bool:
        """Regex operator."""
        if isinstance(values, set):
            return {
                path
                for path in values
                if self.registry.get(path) is not None
                and self._compare_regex(self.registry.get(path), value)
            }
        return isinstance(values, str) and re.search(value, values) is not None

    def _op_exists(self, values: Any, value: Any) -> bool:
        """Exists operator."""
        if isinstance(values, set):
            return {
                path
                for path in values
                if self.registry.get(path) is not None
                and self._compare_exists(self.registry.get(path), value)
            }
        return (values is not None) == value

    def _op_type(self, values: Any, value: Any) -> bool:
        """Type operator."""
        if isinstance(values, set):
            return {
                path
                for path in values
                if self.registry.get(path) is not None
                and self._compare_type(self.registry.get(path), value)
            }
        return value == type(values).__name__

    def _op_and(self, paths: Set[str], value: List[Dict[str, Any]]) -> Set[str]:
        """And operator."""
        result = paths
        for condition in value:
            result = self._apply_filters(result, condition)
        return result

    def _op_or(self, paths: Set[str], value: List[Dict[str, Any]]) -> Set[str]:
        """Or operator."""
        result = set()
        for condition in value:
            result.update(self._apply_filters(paths, condition))
        return result

    def _op_not(self, paths: Set[str], value: Dict[str, Any]) -> Set[str]:
        """Not operator."""
        excluded = self._apply_filters(paths, value)
        return paths - excluded

    # Comparison helpers

    def _compare_eq(self, metadata: Dict[str, Any], value: Any) -> bool:
        """Compare metadata for equality."""
        for section, section_data in metadata.items():
            for field_value in section_data.values():
                if field_value == value:
                    return True
        return False

    def _compare_ne(self, metadata: Dict[str, Any], value: Any) -> bool:
        """Compare metadata for inequality."""
        for section, section_data in metadata.items():
            for field_value in section_data.values():
                if field_value != value:
                    return True
        return False

    def _compare_gt(self, metadata: Dict[str, Any], value: Any) -> bool:
        """Compare metadata for greater than."""
        for section, section_data in metadata.items():
            for field_value in section_data.values():
                if isinstance(field_value, (int, float)) and field_value > value:
                    return True
        return False

    def _compare_gte(self, metadata: Dict[str, Any], value: Any) -> bool:
        """Compare metadata for greater than or equal."""
        for section, section_data in metadata.items():
            for field_value in section_data.values():
                if isinstance(field_value, (int, float)) and field_value >= value:
                    return True
        return False

    def _compare_lt(self, metadata: Dict[str, Any], value: Any) -> bool:
        """Compare metadata for less than."""
        for section, section_data in metadata.items():
            for field_value in section_data.values():
                if isinstance(field_value, (int, float)) and field_value < value:
                    return True
        return False

    def _compare_lte(self, metadata: Dict[str, Any], value: Any) -> bool:
        """Compare metadata for less than or equal."""
        for section, section_data in metadata.items():
            for field_value in section_data.values():
                if isinstance(field_value, (int, float)) and field_value <= value:
                    return True
        return False

    def _compare_in(self, metadata: Dict[str, Any], value: Any) -> bool:
        """Compare metadata for in."""
        for section, section_data in metadata.items():
            for field_value in section_data.values():
                if field_value in value:
                    return True
        return False

    def _compare_nin(self, metadata: Dict[str, Any], value: Any) -> bool:
        """Compare metadata for not in."""
        for section, section_data in metadata.items():
            for field_value in section_data.values():
                if field_value not in value:
                    return True
        return False

    def _compare_contains(self, metadata: Dict[str, Any], value: Any) -> bool:
        """Compare metadata for contains."""
        for section, section_data in metadata.items():
            for field_value in section_data.values():
                if isinstance(field_value, (str, list, dict)) and value in field_value:
                    return True
        return False

    def _compare_startswith(self, metadata: Dict[str, Any], value: Any) -> bool:
        """Compare metadata for starts with."""
        for section, section_data in metadata.items():
            for field_value in section_data.values():
                if isinstance(field_value, str) and field_value.startswith(value):
                    return True
        return False

    def _compare_endswith(self, metadata: Dict[str, Any], value: Any) -> bool:
        """Compare metadata for ends with."""
        for section, section_data in metadata.items():
            for field_value in section_data.values():
                if isinstance(field_value, str) and field_value.endswith(value):
                    return True
        return False

    def _compare_regex(self, metadata: Dict[str, Any], value: Any) -> bool:
        """Compare metadata for regex."""
        for section, section_data in metadata.items():
            for field_value in section_data.values():
                if (
                    isinstance(field_value, str)
                    and re.search(value, field_value) is not None
                ):
                    return True
        return False

    def _compare_exists(self, metadata: Dict[str, Any], value: Any) -> bool:
        """Compare metadata for exists."""
        for section, section_data in metadata.items():
            for field_value in section_data.values():
                if (field_value is not None) == value:
                    return True
        return False

    def _compare_type(self, metadata: Dict[str, Any], value: Any) -> bool:
        """Compare metadata for type."""
        for section, section_data in metadata.items():
            for field_value in section_data.values():
                if value == type(field_value).__name__:
                    return True
        return False
