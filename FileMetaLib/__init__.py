# __init__.py 
"""
FileMetaLib: A library for attaching, indexing, and querying file metadata.

This library provides a comprehensive solution for managing metadata associated with files,
including automatic extraction of system metadata, custom user-defined metadata,
and powerful search capabilities.
"""

from .manager import FileMetaManager
from .plugins  import FilePlugin, PluginRegistry  
from .exceptions import FileMetaError, FileAccessError, PluginError
from .storage import StorageBackend, MemoryDB, JsonDB, SQLiteDB  

__version__ = "0.1.0"
__all__ = [
    "FileMetaManager", 
    "FilePlugin", 
    "PluginRegistry",
    "FileMetaError", 
    "FileAccessError", 
    "PluginError",
    "StorageBackend",
    "MemoryDB",
    "JsonDB",
    "SQLiteDB"
]