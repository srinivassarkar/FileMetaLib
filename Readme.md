# 🔍 FileMetaLib

A developer-first Python library for attaching, indexing, and querying metadata on any file — with plugin support, customizable schemas, and clean APIs to build automation or search workflows over files.

## 📦 Installation

```bash
pip install filemetalib
```

## 🚀 Quick Start

```python
from filemetalib import FileMetaManager

# Initialize the manager
manager = FileMetaManager()

# Add file with custom metadata
manager.add_file("design.png", metadata={
    "tags": ["design", "UI"],
    "project": "website-redesign",
    "owner": "design-team"
})

# Search files by metadata
results = manager.search({"tags": "design"})
for file in results:
    print(f"Found: {file.path}")
    # Do something with the file: open, move, delete, etc.
    
# Get metadata for a specific file
meta = manager.get_metadata("design.png")
print(meta)
# Output includes both system metadata and user-defined metadata

# Update metadata
manager.update_metadata("design.png", {"status": "approved"})

# Register a custom plugin for deeper file inspection
manager.register_plugin(MyImagePlugin())
```

## 🧠 Why FileMetaLib?

Most file systems are limited in how you can organize and query files:

- **File names and directories** are your only organizational tools
- **File-type specific metadata** is locked in proprietary formats
- **Searching across files** requires building custom indexers

FileMetaLib solves these problems by providing:

1. A unified metadata layer for **any file type**
2. **Automatic system metadata** extraction (size, dates, etc.)
3. **Custom user-defined metadata** (tags, owners, projects, etc.)
4. A **plugin system** to extract domain-specific metadata
5. **Simple, intuitive APIs** to add, search, and manage metadata

## 📚 Core Features

### Two-tier Metadata Model

#### 1. System Metadata (Automatic)

For every file, the system automatically captures:

```python
{
  "path": "/home/user/files/document.pdf",  # Full file path
  "filename": "document.pdf",               # File name
  "extension": "pdf",                       # File extension
  "size": 4096,                             # Size in bytes
  "created_at": "2025-06-15T10:30:00",      # Creation timestamp
  "modified_at": "2025-06-16T14:22:35"      # Last modified timestamp
}
```

#### 2. User-defined Metadata (Custom)

Add any metadata that makes sense for your workflow:

```python
{
  "tags": ["important", "project-x", "2025"],
  "owner": "marketing-team",
  "status": "in-review",
  "priority": "high",
  "version": "v2.1",
  # ...any key-value pairs you need
}
```

### Search API

Find files based on any combination of metadata:

```python
# Simple key-value search
docs = manager.search({"tags": "important"})

# Multiple criteria
results = manager.search({
    "tags": "report",
    "owner": "finance-team",
    "status": "approved"
})

# Advanced searching with operators
monthly_reports = manager.search({
    "tags": {"$contains": "monthly-report"},
    "created_at": {"$gt": "2025-01-01"},
    "size": {"$lt": 1000000}
})
```

### File Operations

Act on your search results directly:

```python
# Find and process files
for file in manager.search({"project": "website", "status": "pending"}):
    # file.path contains the full path to work with
    print(f"Processing {file.path}")
    
    # Example operations
    import shutil, os
    
    # Copy to a different location
    shutil.copy(file.path, "/path/to/backup/")
    
    # Open file for reading
    with open(file.path, 'r') as f:
        content = f.read()
        
    # Move file
    shutil.move(file.path, "/path/to/new/location/")
    
    # Delete file
    # os.remove(file.path)
```

## 🔌 Plugin Architecture

Extend FileMetaLib to understand specific file types:

```python
from filemetalib import FilePlugin

class PDFPlugin(FilePlugin):
    def supports(self, file_path):
        return file_path.lower().endswith(".pdf")

    def extract(self, file_path):
        # Use a PDF library to extract metadata
        import PyPDF2
        
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfFileReader(f)
            info = reader.getDocumentInfo()
            
        return {
            "title": info.title,
            "author": info.author,
            "pages": reader.getNumPages(),
            "encrypted": reader.isEncrypted
        }

# Register the plugin
manager.register_plugin(PDFPlugin())
```

Now when you add a PDF file, this metadata is automatically extracted:

```python
manager.add_file("document.pdf")
meta = manager.get_metadata("document.pdf")

print(meta["pages"])  # Output: 42
print(meta["author"])  # Output: "Jane Smith"
```

## 📋 Detailed Usage Guide

### Managing Files and Metadata

```python
# Add a file with metadata
manager.add_file("report.xlsx", metadata={
    "department": "finance",
    "quarter": "Q2",
    "year": 2025
})

# Get all metadata for a file
metadata = manager.get_metadata("report.xlsx")

# Update specific metadata fields
manager.update_metadata("report.xlsx", {
    "status": "final",
    "reviewed_by": "CFO"
})

# Replace all user metadata
manager.replace_metadata("report.xlsx", {
    "archived": True,
    "archive_date": "2025-07-01"
})

# Remove all metadata
manager.delete_metadata("report.xlsx")
```

### Bulk Operations

Process multiple files efficiently:

```python
# Add multiple files
files_to_add = [
    ("doc1.pdf", {"project": "alpha"}),
    ("doc2.pdf", {"project": "alpha"}),
    ("image.png", {"project": "beta"})
]

manager.add_files(files_to_add)

# Bulk update
manager.update_many(
    query={"project": "alpha"},
    update={"status": "review"}
)

# Add all files in a directory (with recursive option)
manager.add_directory(
    "/path/to/project/",
    recursive=True,
    metadata={"project": "alpha"},
    exclude_patterns=["*.tmp", ".*"]
)
```

### Storage Options

Choose where your metadata is stored:

```python
# In-memory storage (default)
manager = FileMetaManager()

# SQLite backend
manager = FileMetaManager(storage="sqlite:///path/to/metadata.db")

# JSON file storage
manager = FileMetaManager(storage="json:///path/to/metadata.json")

# Custom storage
from filemetalib import StorageBackend

class MyCustomStorage(StorageBackend):
    # Implement required methods
    pass
    
manager = FileMetaManager(storage=MyCustomStorage())
```

## 🛡️ Advanced Usage & Edge Cases

### File System Synchronization

Keep metadata in sync with file system changes:

```python
# Detect file system changes and update metadata accordingly
manager.sync()

# Configure automatic sync interval (in seconds)
manager = FileMetaManager(auto_sync=300)  # Sync every 5 minutes

# Check for and clean up orphaned metadata (files that no longer exist)
orphaned = manager.cleanup_orphaned()
print(f"Removed metadata for {len(orphaned)} deleted files")
```

### Error Handling

```python
from filemetalib import FileAccessError, PluginError

try:
    manager.add_file("locked_file.pdf")
except FileAccessError as e:
    print(f"Cannot access file: {e}")

# Configure plugin error behavior
manager = FileMetaManager(
    # Options: 'ignore', 'warn', 'raise'
    plugin_error_mode='warn'
)
```

### Plugin Conflict Resolution

Control how conflicts between plugins are handled:

```python
# Register plugin with priority (higher number = higher priority)
manager.register_plugin(PDFPlugin(), priority=100)
manager.register_plugin(DocumentPlugin(), priority=50)

# Configure conflict resolution strategy
manager = FileMetaManager(
    # Options: 'priority', 'merge', 'first_only', 'last_only'
    plugin_conflict_mode='merge'
)
```

### Performance Optimization

For large file systems:

```python
# Enable incremental indexing
manager = FileMetaManager(
    incremental_indexing=True,
    index_batch_size=1000
)

# Create indexes for faster searching
manager.create_index("tags")
manager.create_index("owner")

# Limit memory usage
manager = FileMetaManager(
    max_cache_size=10000,  # Maximum files to keep in memory
    cache_policy='lru'     # Least Recently Used eviction
)
```

### Cross-Platform Compatibility

```python
# Normalize paths for cross-platform compatibility
manager = FileMetaManager(normalize_paths=True)

# Configure path handling for specific OS
manager = FileMetaManager(
    path_separator='auto',  # 'auto', '/', or '\'
    case_sensitive=None     # None (auto-detect), True, or False
)
```

### Concurrency Support

Thread and process-safe operations:

```python
# Thread-safe manager
manager = FileMetaManager(thread_safe=True)

# Use context manager for safe concurrent access
with manager.transaction() as txn:
    txn.add_file("doc1.txt", {"status": "processing"})
    txn.update_metadata("doc2.txt", {"status": "complete"})
    # Changes applied atomically at context exit
```

### Metadata Size Management

```python
# Set metadata size limits
manager = FileMetaManager(
    max_metadata_size=1024 * 1024,  # 1MB per file
    compress_large_metadata=True
)

# Check current metadata size
size_info = manager.get_metadata_size("large_file.psd")
print(f"Metadata size: {size_info['bytes']} bytes")
```

### Data Migration & Backup

```python
# Export metadata to file
manager.export_metadata("/path/to/backup.json")

# Import metadata from file
manager.import_metadata("/path/to/backup.json", 
                       conflict_mode="newer")  # Use newer timestamps on conflict

# Migrate between storage backends
manager.migrate_storage("sqlite:///new_database.db")
```

## 🔧 System Architecture & Design

FileMetaLib is designed with several key architectural principles to ensure it's robust, extensible, and efficient. This section explains how the system works under the hood.

### Core Architecture Components

![FileMetaLib Architecture](https://placeholder-for-architecture-diagram.png)

#### 1. Manager Layer

The `FileMetaManager` class serves as the primary interface for developers. It coordinates between:

- **Metadata Registry**: In-memory index of all file metadata
- **Storage Backend**: Persistence layer for metadata
- **Plugin Registry**: Collection of file type handlers
- **Query Engine**: Processes search requests

#### 2. Storage Backend System

FileMetaLib employs a modular storage system:

```
┌─────────────────┐
│ StorageBackend  │  ← Abstract base class
└─────────────────┘
        ↑
        ├────────┬─────────┬──────────┐
        │        │         │          │
┌───────┴──┐ ┌───┴───┐ ┌───┴────┐ ┌───┴───────┐
│ MemoryDB │ │ SQLite │ │ JsonDB │ │ CustomDB  │
└──────────┘ └───────┘ └────────┘ └───────────┘
```

Each backend implements:
- `save(filepath, metadata)`
- `get(filepath)`
- `delete(filepath)`
- `query(criteria)`
- `bulk_operation(operations)`

The storage system uses a transaction log to ensure atomicity and durability of operations.

#### 3. Metadata Registry

The registry maintains an in-memory index optimized for fast queries:

- **Primary index**: Path → Metadata mapping
- **Secondary indexes**: Field → Paths mappings for fast searching
- **Cache management**: LRU/LFU eviction for memory efficiency

Data structure:
```python
{
  "file_index": {
    "/path/to/file1.txt": {
      "system": { /* system metadata */ },
      "user": { /* user metadata */ },
      "plugin": { /* plugin-extracted metadata */ }
    },
    # ...more files
  },
  "field_indexes": {
    "tags": {
      "important": ["/path/to/file1.txt", "/path/to/file2.pdf"],
      # ...more tag values
    },
    # ...more indexed fields
  }
}
```

#### 4. Query Engine

The query engine uses a processing pipeline:

1. **Query parsing**: Converts query dict to filter operations
2. **Index utilization**: Uses field indexes when available
3. **Filter chaining**: Applies filters in order of selectivity
4. **Lazy evaluation**: Processes results as a generator when possible

For complex queries, the engine builds an execution plan to minimize processing:
```
Query: {"tags": "report", "size": {"$gt": 1000000}}
Plan:
  1. Get file paths from "tags" index where value = "report"
  2. For each path, check if size > 1000000
```

#### 5. Plugin System

Plugins follow a registry pattern with these internal processes:

1. **Registration**: Plugins added to registry with priority
2. **Dispatch**: File type determined via `supports()` method
3. **Execution**: Matching plugins called to extract metadata
4. **Conflict Resolution**: Results combined per configured strategy

Plugin execution is done in a background thread pool to prevent blocking on slow plugins.

### Performance Considerations

#### Indexing Strategy

For large file systems, FileMetaLib uses:

- **Incremental indexing**: Only process changed files
- **Batched operations**: Process files in configurable chunks
- **Worker pools**: Parallel plugin execution
- **Lazy metadata extraction**: Extract only when needed

#### Memory Management

To handle large metadata collections:

- **Partial loading**: Load only necessary fields into memory
- **Eviction policies**: LRU/LFU for in-memory cache
- **Compression**: Optional compression for large metadata objects
- **Field selectivity**: Only store and index useful fields

#### Concurrency Control

Thread and process safety is managed through:

- **Read-write locks**: Allow concurrent reads, exclusive writes
- **Transaction system**: Group operations into atomic units
- **Change journal**: Record modifications for rollback

### File System Integration

FileMetaLib integrates with the file system in several ways:

- **File watchers**: Optional monitoring for live changes (using `watchdog`)
- **Path normalization**: Handle OS-specific path formats
- **Permission checking**: Verify file access before operations
- **Stats caching**: Cache file stats to reduce syscalls

### Data Flow

A typical metadata operation flows through the system as follows:

1. **API Call**: Developer invokes a method on `FileMetaManager`
2. **Validation**: Input parameters are validated
3. **System metadata**: Extracted automatically from file 
4. **Plugin dispatch**: Applicable plugins are called
5. **Metadata merged**: System, user, and plugin data combined
6. **Indexing**: Metadata indexed for fast retrieval
7. **Storage**: Data persisted to configured backend
8. **Events**: Listeners notified of changes

### Serialization Format

Metadata is stored in a normalized format:

```json
{
  "system": {
    "path": "/absolute/path/to/file.ext",
    "filename": "file.ext",
    "extension": "ext",
    "size": 12345,
    "created_at": "2025-06-15T10:30:00",
    "modified_at": "2025-06-16T14:22:35"
  },
  "user": {
    "tags": ["report", "2025", "finance"],
    "owner": "accounting-team",
    "priority": "high"
  },
  "plugin": {
    "image": {
      "dimensions": "1920x1080",
      "format": "PNG"
    },
    "document": {
      "pages": 42,
      "author": "Jane Smith"
    }
  }
}
```

## 🏗️ Extension and Customization

### Creating Custom Plugins

Plugins follow a simple interface:

```python
class ImagePlugin:
    def supports(self, file_path):
        """Return True if this plugin can handle the file type"""
        return file_path.lower().endswith((".jpg", ".jpeg", ".png", ".gif"))

    def extract(self, file_path):
        """Extract and return metadata as a dictionary"""
        from PIL import Image
        
        img = Image.open(file_path)
        
        return {
            "dimensions": f"{img.width}x{img.height}",
            "format": img.format,
            "mode": img.mode,
            "has_exif": hasattr(img, "_getexif") and img._getexif() is not None
        }
```

### Custom Search Query Handlers

Extend the search capabilities:

```python
from filemetalib import QueryHandler

class FuzzyTextQueryHandler(QueryHandler):
    def can_handle(self, field, value):
        return isinstance(value, dict) and "$fuzzy" in value
    
    def process(self, items, field, value):
        from fuzzywuzzy import fuzz
        threshold = value.get("$threshold", 80)
        pattern = value["$fuzzy"]
        
        return [item for item in items 
                if field in item.metadata and 
                fuzz.ratio(pattern, str(item.metadata[field])) >= threshold]

# Register the handler
manager.register_query_handler(FuzzyTextQueryHandler())

# Use in queries
results = manager.search({
    "description": {"$fuzzy": "annual report", "$threshold": 75}
})
```

### Custom Storage Backends

Create your own storage system:

```python
from filemetalib import StorageBackend

class RedisStorageBackend(StorageBackend):
    def __init__(self, redis_url):
        import redis
        self.client = redis.from_url(redis_url)
        
    def save(self, file_path, metadata):
        import json
        key = f"filemetalib:metadata:{file_path}"
        self.client.set(key, json.dumps(metadata))
        
    def get(self, file_path):
        import json
        key = f"filemetalib:metadata:{file_path}"
        data = self.client.get(key)
        return json.loads(data) if data else None
        
    def delete(self, file_path):
        key = f"filemetalib:metadata:{file_path}"
        self.client.delete(key)
        
    def query(self, criteria):
        # Implement query logic (will require additional indexes in Redis)
        pass
```

### Event Listeners

React to metadata changes:

```python
def on_metadata_changed(file_path, old_meta, new_meta):
    print(f"Metadata changed for {file_path}")
    
manager.add_listener("metadata_changed", on_metadata_changed)

# Other events: 'file_added', 'file_removed', 'sync_complete'
```

## 📚 Examples

### Project File Management

```python
# Add project files with metadata
manager.add_file("src/main.py", metadata={"module": "core", "author": "dev1"})
manager.add_file("src/utils.py", metadata={"module": "utils", "author": "dev2"})
manager.add_file("tests/test_main.py", metadata={"test_for": "main.py", "status": "passing"})

# Find files needing review
for file in manager.search({"author": "dev1", "status": {"$ne": "reviewed"}}):
    print(f"Needs review: {file.path}")
```

### Media Library Organization

```python
# Add media files
manager.add_file("movies/inception.mp4", metadata={
    "type": "movie",
    "genre": ["sci-fi", "action"],
    "director": "Christopher Nolan",
    "year": 2010
})

# Register media plugins for auto-extraction
manager.register_plugin(VideoMetadataPlugin())
manager.register_plugin(AudioMetadataPlugin())

# Find all sci-fi movies
sci_fi = manager.search({"type": "movie", "genre": "sci-fi"})
```

## 🔄 Troubleshooting

### Common Issues and Solutions

| Issue | Solution |
|-------|----------|
| Files moved outside library | Use `manager.sync()` or `manager.reconcile_paths()` |
| Slow search performance | Create indexes on frequently searched fields |
| Large memory usage | Configure `max_cache_size` and `cache_policy` |
| Plugin failures | Set `plugin_error_mode='warn'` and check logs |
| Metadata not persisting | Verify storage backend configuration |
| Path separator issues | Set `normalize_paths=True` |

### Logging and Debugging

```python
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("filemetalib")
logger.setLevel(logging.DEBUG)

# Enable debug mode
manager = FileMetaManager(debug=True)

# Get performance statistics
stats = manager.get_stats()
print(f"Indexed files: {stats['file_count']}")
print(f"Average search time: {stats['avg_search_time']}ms")
```

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

---

Built with ❤️ for developers who value organization and efficiency.