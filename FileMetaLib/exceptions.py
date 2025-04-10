# exceptions.py
"""
Exceptions for FileMetaLib.
"""


class FileMetaError(Exception):
    """Base exception for FileMetaLib."""

    pass


class FileAccessError(FileMetaError):
    """Exception raised when a file cannot be accessed."""

    pass


class PluginError(FileMetaError):
    """Exception raised when a plugin fails."""

    pass


class StorageError(FileMetaError):
    """Exception raised when storage fails."""

    pass


class QueryError(FileMetaError):
    """Exception raised when a query is invalid."""

    pass
