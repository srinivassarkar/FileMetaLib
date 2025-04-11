# 🔍 FileMetaLib

A developer-first Python library for attaching, indexing, and querying metadata on any file — with plugin support, customizable schemas, and clean APIs to build automation or search workflows over files.

## 📦 Installation

```bash
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple FileMetaLib
```
## 🚀 Quick Start

```python
from filemetalib import FileMetaManager

# Initialize the manager
manager = FileMetaManager()

# Add file with custom metadata
manager.add_file("design.png", {
    "tags": ["design", "UI"],
    "project": "website-redesign",
    "owner": "design-team"
})

# Search files by metadata
results = manager.search({"user.tags": {"$contains": "design"}})
for file in results:
    print(f"Found: {file}")
    # Do something with the file: open, move, delete, etc.

# Expected output:
# Found: design.png
    
# Get metadata for a specific file
meta = manager.get_metadata("design.png")
print(meta)
# Expected output:
# {
#   'system': {
#     'path': '/path/to/design.png',
#     'filename': 'design.png',
#     'extension': 'png',
#     'size': 12345,
#     'created': 1712345678.0,
#     'modified': 1712345678.0,
#     'accessed': 1712345678.0
#   },
#   'user': {
#     'tags': ['design', 'UI'],
#     'project': 'website-redesign',
#     'owner': 'design-team'
#   }
# }

# Update metadata
manager.update_metadata("design.png", {"status": "approved"})

# Register a custom plugin for deeper file inspection
from filemetalib.plugins import FilePlugin

class MyImagePlugin(FilePlugin):
    def supports(self, path):
        return path.lower().endswith(('.png', '.jpg', '.jpeg'))
        
    def extract(self, path):
        # Simple example - in real use, you'd use PIL or another library
        return {"image_type": "png", "has_transparency": True}

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
  'created': '2025-04-11 15:47:54',          # Creationtimestamp
  "modified": '2025-04-11 15:47:54',         # Last modified timestamp
  "accessed": '2025-04-11 15:47:54',         # Last accessed timestamp
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
docs = manager.search({"user.tags": {"$contains": "important"}})
# Expected output: List of file paths with the "important" tag

# Multiple criteria
results = manager.search({
    "user.tags": {"$contains": "report"},
    "user.owner": "finance-team",
    "user.status": "approved"
})
# Expected output: List of file paths matching all criteria

# Advanced searching with operators
monthly_reports = manager.search({
    "user.tags": {"$contains": "monthly-report"},
    "system.created": {"$gt": 1712345678.0},  # Unix timestamp
    "system.size": {"$lt": 1000000}
})
# Expected output: List of file paths matching all criteria
```

### File Operations

Act on your search results directly:

```python
# Find and process files
for file in manager.search({"user.project": "website", "user.status": "pending"}):
    # file contains the full path to work with
    print(f"Processing {file}")
    
    # Example operations
    import shutil, os
    
    # Copy to a different location
    shutil.copy(file, "/path/to/backup/")
    
    # Open file for reading
    with open(file, 'r') as f:
        content = f.read()
        
    # Move file
    shutil.move(file, "/path/to/new/location/")
    
    # Delete file
    # os.remove(file)
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
        # This is a simplified example
        return {
            "title": "Sample PDF",
            "author": "John Doe",
            "pages": 42,
            "encrypted": False
        }

# Register the plugin
manager.register_plugin(PDFPlugin())
```

Now when you add a PDF file, this metadata is automatically extracted:

```python
manager.add_file("document.pdf")
meta = manager.get_metadata("document.pdf")

print(meta["plugin"]["pages"])  # Output: 42
print(meta["plugin"]["author"])  # Output: "John Doe"
```

## 📋 Detailed Usage Guide

### Managing Files and Metadata

```python
# Add a file with metadata
manager.add_file("report.xlsx", {
    "department": "finance",
    "quarter": "Q2",
    "year": 2025
})

# Expected output: None (successful operation)

# Get all metadata for a file
metadata = manager.get_metadata("report.xlsx")
print(metadata)
# Expected output:
# {
#   'system': {
#     'path': '/path/to/report.xlsx',
#     'filename': 'report.xlsx',
#     'extension': 'xlsx',
#     'size': 12345,
#     'created': 1712345678.0,
#     'modified': 1712345678.0,
#     'accessed': 1712345678.0
#   },
#   'user': {
#     'department': 'finance',
#     'quarter': 'Q2',
#     'year': 2025
#   }
# }

# Update specific metadata fields
manager.update_metadata("report.xlsx", {
    "status": "final",
    "reviewed_by": "CFO"
})
# Expected output: None (successful operation)

# Get updated metadata
updated_metadata = manager.get_metadata("report.xlsx")
print(updated_metadata["user"])
# Expected output:
# {
#   'department': 'finance',
#   'quarter': 'Q2',
#   'year': 2025,
#   'status': 'final',
#   'reviewed_by': 'CFO'
# }

# Replace all user metadata
manager.replace_metadata("report.xlsx", {
    "archived": True,
    "archive_date": "2025-07-01"
})
# Expected output: None (successful operation)

# Get replaced metadata
replaced_metadata = manager.get_metadata("report.xlsx")
print(replaced_metadata["user"])
# Expected output:
# {
#   'archived': True,
#   'archive_date': '2025-07-01'
# }

# Remove all metadata
manager.delete_metadata("report.xlsx")
# Expected output: None (successful operation)
```

### Working with Multiple Files

Process multiple files efficiently:

```python
import os

# Create test files
with open("doc1.txt", "w") as f:
    f.write("Test document 1")
with open("doc2.txt", "w") as f:
    f.write("Test document 2")
with open("image.png", "w") as f:
    f.write("Fake image file for testing")

# Add files with metadata
manager.add_file("doc1.txt", {"project": "alpha", "status": "draft"})
manager.add_file("doc2.txt", {"project": "alpha", "status": "draft"})
manager.add_file("image.png", {"project": "beta", "status": "draft"})

# Search for all files in project alpha
alpha_files = manager.search({"user.project": "alpha"})
print("Alpha project files:", list(alpha_files))
# Expected output:
# Alpha project files: ['doc1.txt', 'doc2.txt']

# Search for all draft files
draft_files = manager.search({"user.status": "draft"})
print("Draft files:", list(draft_files))
# Expected output:
# Draft files: ['doc1.txt', 'doc2.txt', 'image.png']

# Clean up
os.remove("doc1.txt")
os.remove("doc2.txt")
os.remove("image.png")
```

### Storage Options

Choose where your metadata is stored:

```python
from filemetalib import FileMetaManager
from filemetalib.storage import MemoryDB, JsonDB, SQLiteDB

# In-memory storage (default)
manager = FileMetaManager()

# SQLite backend
sqlite_manager = FileMetaManager(storage_backend=SQLiteDB("metadata.db"))

# JSON file storage
json_manager = FileMetaManager(storage_backend=JsonDB("metadata.json"))

# Example with JSON storage
json_manager.add_file("test.txt", {"tags": ["example"]})
metadata = json_manager.get_metadata("test.txt")
print(metadata["user"])
# Expected output:
# {'tags': ['example']}
```

## 🛡️ Advanced Usage & Edge Cases

### File System Synchronization

Keep metadata in sync with file system changes:

```python
import os

# Create test files
with open("sync_test1.txt", "w") as f:
    f.write("Test file 1")
with open("sync_test2.txt", "w") as f:
    f.write("Test file 2")

# Add files to manager
manager = FileMetaManager()
manager.add_file("sync_test1.txt", {"status": "active"})
manager.add_file("sync_test2.txt", {"status": "active"})

# Delete a file outside the manager
os.remove("sync_test1.txt")

# Sync to detect changes
result = manager.sync()
print(f"Sync results: {result}")
# Expected output:
# Sync results: {'added': 0, 'updated': 0, 'removed': 1}

# Check if metadata was removed
try:
    manager.get_metadata("sync_test1.txt")
    print("Metadata still exists")
except:
    print("Metadata was removed")
# Expected output:
# Metadata was removed

# Clean up
os.remove("sync_test2.txt")
```

### Error Handling

```python
from filemetalib import FileMetaManager
from filemetalib.exceptions import FileAccessError, PluginError

manager = FileMetaManager()

# Try to access a non-existent file
try:
    manager.add_file("non_existent_file.txt")
except FileAccessError as e:
    print(f"File access error: {e}")
# Expected output:
# File access error: File not found: non_existent_file.txt

# Try to get metadata for a file that hasn't been added
try:
    manager.get_metadata("unknown_file.txt")
except FileAccessError as e:
    print(f"File access error: {e}")
# Expected output:
# File access error: No metadata found for: unknown_file.txt
```

### Plugin Example with Image Files

```python
import os
from filemetalib import FileMetaManager
from filemetalib.plugins import FilePlugin

# Create a simple image plugin
class SimpleImagePlugin(FilePlugin):
    def supports(self, path):
        return path.lower().endswith(('.png', '.jpg', '.jpeg'))
        
    def extract(self, path):
        # In a real plugin, you'd use PIL or another library to get actual metadata
        ext = os.path.splitext(path)[1].lower()
        return {
            "format": ext[1:].upper(),
            "dimensions": "800x600",  # Placeholder
            "color_mode": "RGB"
        }

# Create a manager and register the plugin
manager = FileMetaManager()
manager.register_plugin(SimpleImagePlugin())

# Create a test image file
with open("test_image.png", "w") as f:
    f.write("Fake image data")

# Add the file and get metadata
manager.add_file("test_image.png", {"tags": ["test"]})
metadata = manager.get_metadata("test_image.png")

# Print the plugin-extracted metadata
print("Plugin metadata:", metadata.get("plugin", {}))
# Expected output:
# Plugin metadata: {'format': 'PNG', 'dimensions': '800x600', 'color_mode': 'RGB'}

# Clean up
os.remove("test_image.png")
```

### Metadata Export and Import

```python
import os
from filemetalib import FileMetaManager

# Create a manager and add some files
manager = FileMetaManager()

# Create test files
with open("export_test1.txt", "w") as f:
    f.write("Test file 1")
with open("export_test2.txt", "w") as f:
    f.write("Test file 2")

# Add files with metadata
manager.add_file("export_test1.txt", {"category": "document", "status": "active"})
manager.add_file("export_test2.txt", {"category": "document", "status": "archived"})

# Export metadata to a file
manager.export_metadata("metadata_backup.json")
print("Metadata exported")
# Expected output:
# Metadata exported

# Create a new manager and import the metadata
new_manager = FileMetaManager()
count = new_manager.import_metadata("metadata_backup.json")
print(f"Imported {count} entries")
# Expected output:
# Imported 2 entries

# Verify the imported metadata
metadata = new_manager.get_metadata("export_test1.txt")
print("Imported metadata:", metadata["user"])
# Expected output:
# Imported metadata: {'category': 'document', 'status': 'active'}

# Clean up
os.remove("export_test1.txt")
os.remove("export_test2.txt")
os.remove("metadata_backup.json")
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
import os
from filemetalib import FileMetaManager

# Create a manager
manager = FileMetaManager()

# Create test files
os.makedirs("project/src", exist_ok=True)
os.makedirs("project/tests", exist_ok=True)

with open("project/src/main.py", "w") as f:
    f.write("# Main module")
with open("project/src/utils.py", "w") as f:
    f.write("# Utilities module")
with open("project/tests/test_main.py", "w") as f:
    f.write("# Tests for main module")

# Add project files with metadata
manager.add_file("project/src/main.py", {
    "module": "core", 
    "author": "dev1",
    "status": "in progress"
})
manager.add_file("project/src/utils.py", {
    "module": "utils", 
    "author": "dev2",
    "status": "complete"
})
manager.add_file("project/tests/test_main.py", {
    "test_for": "main.py", 
    "author": "dev1",
    "status": "passing"
})

# Find files by author
dev1_files = manager.search({"user.author": "dev1"})
print("Files by dev1:", list(dev1_files))
# Expected output:
# Files by dev1: ['project/src/main.py', 'project/tests/test_main.py']

# Find files needing review (in progress)
in_progress = manager.search({"user.status": "in progress"})
print("Files in progress:", list(in_progress))
# Expected output:
# Files in progress: ['project/src/main.py']

# Find test files
test_files = manager.search({"user.test_for": {"$exists": True}})
print("Test files:", list(test_files))
# Expected output:
# Test files: ['project/tests/test_main.py']

# Clean up
import shutil
shutil.rmtree("project")
```

### Media Library Organization

```python
import os
from filemetalib import FileMetaManager

# Create a manager
manager = FileMetaManager()

# Create test directory
os.makedirs("media", exist_ok=True)

# Create some dummy media files
with open("media/movie1.mp4", "w") as f:
    f.write("Fake movie file")
with open("media/movie2.mp4", "w") as f:
    f.write("Another fake movie file")
with open("media/song.mp3", "w") as f:
    f.write("Fake audio file")

# Add media files with metadata
manager.add_file("media/movie1.mp4", {
    "type": "movie",
    "genre": ["sci-fi", "action"],
    "director": "Christopher Nolan",
    "year": 2010,
    "rating": 5
})

manager.add_file("media/movie2.mp4", {
    "type": "movie",
    "genre": ["comedy", "drama"],
    "director": "Wes Anderson",
    "year": 2018,
    "rating": 4
})

manager.add_file("media/song.mp3", {
    "type": "audio",
    "genre": ["rock"],
    "artist": "The Beatles",
    "year": 1969,
    "rating": 5
})

# Find all movies
movies = manager.search({"user.type": "movie"})
print("Movies:", list(movies))
# Expected output:
# Movies: ['media/movie1.mp4', 'media/movie2.mp4']

# Find sci-fi content
scifi = manager.search({"user.genre": {"$contains": "sci-fi"}})
print("Sci-fi content:", list(scifi))
# Expected output:
# Sci-fi content: ['media/movie1.mp4']

# Find highly rated content (rating >= 5)
top_rated = manager.search({"user.rating": 5})
print("Top rated content:", list(top_rated))
# Expected output:
# Top rated content: ['media/movie1.mp4', 'media/song.mp3']

# Find content from before 2015
old_content = manager.search({"user.year": {"$lt": 2015}})
print("Pre-2015 content:", list(old_content))
# Expected output:
# Pre-2015 content: ['media/movie1.mp4', 'media/song.mp3']

# Clean up
shutil.rmtree("media")
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
