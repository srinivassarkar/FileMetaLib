# query.py 
"""
Query engine for FileMetaLib.
"""

import re
from typing import Dict, List, Any, Set, Callable, Iterable, Optional

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
            "$not": self._op_not
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
                
                if isinstance(value, dict) and all(k.startswith("$") for k in value.keys()):
                    # Operator query
                    for op, op_value in value.items():
                        if op in self._operators:
                            result = self._filter_by_field_op(result, section, field, op, op_value)
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
    
    def _filter_by_field_eq(self, paths: Set[str], section: str, field: str, value: Any) -> Set[str]:
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
    
    def _filter_by_field_op(self, paths: Set[str], section: str, field: str, op: str, value: Any) -> Set[str]:
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
            
            if self._apply_operator(op, field_value, value):
                result.add(path)
        
        return result
    
    def _apply_operator(self, op: str, field_value: Any, value: Any) -> bool:
        """
        Apply an operator to a field value.
        
        Args:
            op: Operator.
            field_value: Field value.
            value: Value to compare with.
            
        Returns:
            Whether the operator matches.
        """
        if op not in self._operators:
            return False
        
        # Special handling for logical operators
        if op in ["$and", "$or", "$not"]:
            return False  # These should be handled at the top level
        
        # Apply the operator
        return self._operators[op]([field_value], value)
    
    # Operator implementations
    
    def _op_eq(self, values: Any, value: Any) -> Any:
        """Equal operator."""
        if isinstance(values, set):
            return {path for path in values if self._get_field_value(path, value) == value}
        return values[0] == value if values else False
    
    def _op_ne(self, values: Any, value: Any) -> Any:
        """Not equal operator."""
        if isinstance(values, set):
            return {path for path in values if self._get_field_value(path, value) != value}
        return values[0] != value if values else False
    
    def _op_gt(self, values: Any, value: Any) -> Any:
        """Greater than operator."""
        if isinstance(values, set):
            return {path for path in values if self._compare_numeric(self._get_field_value(path, value), value, lambda a, b: a > b)}
        return self._compare_numeric(values[0], value, lambda a, b: a > b) if values else False
    
    def _op_gte(self, values: Any, value: Any) -> Any:
        """Greater than or equal operator."""
        if isinstance(values, set):
            return {path for path in values if self._compare_numeric(self._get_field_value(path, value), value, lambda a, b: a >= b)}
        return self._compare_numeric(values[0], value, lambda a, b: a >= b) if values else False
    
    def _op_lt(self, values: Any, value: Any) -> Any:
        """Less than operator."""
        if isinstance(values, set):
            return {path for path in values if self._compare_numeric(self._get_field_value(path, value), value, lambda a, b: a < b)}
        return self._compare_numeric(values[0], value, lambda a, b: a < b) if values else False
    
    def _op_lte(self, values: Any, value: Any) -> Any:
        """Less than or equal operator."""
        if isinstance(values, set):
            return {path for path in values if self._compare_numeric(self._get_field_value(path, value), value, lambda a, b: a <= b)}
        return self._compare_numeric(values[0], value, lambda a, b: a <= b) if values else False
    
    def _op_in(self, values: Any, value: Any) -> Any:
        """In operator."""
        if isinstance(values, set):
            return {path for path in values if self._get_field_value(path, value) in value}
        return values[0] in value if values else False
    
    def _op_nin(self, values: Any, value: Any) -> Any:
        """Not in operator."""
        if isinstance(values, set):
            return {path for path in values if self._get_field_value(path, value) not in value}
        return values[0] not in value if values else False
    
    def _op_contains(self, values: Any, value: Any) -> Any:
        """Contains operator."""
        if isinstance(values, set):
            return {path for path in values if self._check_contains(self._get_field_value(path, value), value)}
        return self._check_contains(values[0], value) if values else False
    
    def _op_startswith(self, values: Any, value: Any) -> Any:
        """Starts with operator."""
        if isinstance(values, set):
            return {path for path in values if self._check_startswith(self._get_field_value(path, value), value)}
        return self._check_startswith(values[0], value) if values else False
    
    def _op_endswith(self, values: Any, value: Any) -> Any:
        """Ends with operator."""
        if isinstance(values, set):
            return {path for path in values if self._check_endswith(self._get_field_value(path, value), value)}
        return self._check_endswith(values[0], value) if values else False
    
    def _op_regex(self, values: Any, value: Any) -> Any:
        """Regex operator."""
        if isinstance(values, set):
            return {path for path in values if self._check_regex(self._get_field_value(path, value), value)}
        return self._check_regex(values[0], value) if values else False
    
    def _op_exists(self, values: Any, value: Any) -> Any:
        """Exists operator."""
        if isinstance(values, set):
            return {path for path in values if (self._get_field_value(path, value) is not None) == value}
        return (values[0] is not None) == value if values else False
    
    def _op_type(self, values: Any, value: Any) -> Any:
        """Type operator."""
        if isinstance(values, set):
            return {path for path in values if self._check_type(self._get_field_value(path, value), value)}
        return self._check_type(values[0], value) if values else False
    
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
    
    # Helper methods
    
    def _get_field_value(self, path: str, default: Any = None) -> Any:
        """
        Get a field value from metadata.
        
        Args:
            path: Path to the file.
            default: Default value if not found.
            
        Returns:
            Field value.
        """
        metadata = self.registry.get(path)
        if not metadata:
            return default
        
        return metadata
    
    def _compare_numeric(self, a: Any, b: Any, op: Callable[[Any, Any], bool]) -> bool:
        """
        Compare two values numerically.
        
        Args:
            a: First value.
            b: Second value.
            op: Comparison operator.
            
        Returns:
            Whether the comparison is true.
        """
        if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
            return False
        
        return op(a, b)
    
    def _check_contains(self, a: Any, b: Any) -> bool:
        """
        Check if a contains b.
        
        Args:
            a: Container.
            b: Value.
            
        Returns:
            Whether a contains b.
        """
        if isinstance(a, (str, list, tuple, set)):
            return b in a
        if isinstance(a, dict):
            return b in a or b in a.values()
        return False
    
    def _check_startswith(self, a: Any, b: Any) -> bool:
        """
        Check if a starts with b.
        
        Args:
            a: String.
            b: Prefix.
            
        Returns:
            Whether a starts with b.
        """
        return isinstance(a, str) and a.startswith(b)
    
    def _check_endswith(self, a: Any, b: Any) -> bool:
        """
        Check if a ends with b.
        
        Args:
            a: String.
            b: Suffix.
            
        Returns:
            Whether a ends with b.
        """
        return isinstance(a, str) and a.endswith(b)
    
    def _check_regex(self, a: Any, b: Any) -> bool:
        """
        Check if a matches regex b.
        
        Args:
            a: String.
            b: Regex pattern.
            
        Returns:
            Whether a matches b.
        """
        if not isinstance(a, str):
            return False
        
        try:
            return re.search(b, a) is not None
        except:
            return False
    
    def _check_type(self, a: Any, b: Any) -> bool:
        """
        Check if a is of type b.
        
        Args:
            a: Value.
            b: Type name.
            
        Returns:
            Whether a is of type b.
        """
        return b == type(a).__name__