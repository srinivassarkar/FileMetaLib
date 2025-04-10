# storage.py
"""
Storage backends for FileMetaLib.
"""

import os
import json
import sqlite3
from typing import Dict, List, Any, Tuple, Iterator
from abc import ABC, abstractmethod


class StorageBackend(ABC):
    """
    Abstract base class for storage backends.

    Storage backends are responsible for persisting metadata.
    """

    @abstractmethod
    def save(self, path: str, metadata: Dict[str, Any]) -> None:
        """
        Save metadata for a file.

        Args:
            path: Path to the file.
            metadata: Metadata to save.
        """
        pass

    @abstractmethod
    def load(self, path: str) -> Dict[str, Any]:
        """
        Load metadata for a file.

        Args:
            path: Path to the file.

        Returns:
            Metadata for the file, or None if not found.
        """
        pass

    @abstractmethod
    def delete(self, path: str) -> None:
        """
        Delete metadata for a file.

        Args:
            path: Path to the file.
        """
        pass

    @abstractmethod
    def load_all(self) -> Iterator[Tuple[str, Dict[str, Any]]]:
        """
        Load all metadata.

        Returns:
            Iterator of (path, metadata) tuples.
        """
        pass


class MemoryDB(StorageBackend):
    """
    In-memory storage backend.

    This backend stores metadata in memory and does not persist it.
    """

    def __init__(self):
        """Initialize a new MemoryDB."""
        self._data = {}

    def save(self, path: str, metadata: Dict[str, Any]) -> None:
        """
        Save metadata for a file.

        Args:
            path: Path to the file.
            metadata: Metadata to save.
        """
        self._data[path] = metadata

    def load(self, path: str) -> Dict[str, Any]:
        """
        Load metadata for a file.

        Args:
            path: Path to the file.

        Returns:
            Metadata for the file, or None if not found.
        """
        return self._data.get(path)

    def delete(self, path: str) -> None:
        """
        Delete metadata for a file.

        Args:
            path: Path to the file.
        """
        if path in self._data:
            del self._data[path]

    def load_all(self) -> Iterator[Tuple[str, Dict[str, Any]]]:
        """
        Load all metadata.

        Returns:
            Iterator of (path, metadata) tuples.
        """
        for path, metadata in self._data.items():
            yield path, metadata


class JsonDB(StorageBackend):
    """
    JSON file storage backend.

    This backend stores metadata in a JSON file.
    """

    def __init__(self, file_path: str):
        """
        Initialize a new JsonDB.

        Args:
            file_path: Path to the JSON file.
        """
        self.file_path = file_path
        self._data = {}

        # Load existing data if file exists
        if os.path.exists(file_path):
            try:
                with open(file_path, "r") as f:
                    self._data = json.load(f)
            except json.JSONDecodeError:
                # File exists but is not valid JSON
                self._data = {}

    def save(self, path: str, metadata: Dict[str, Any]) -> None:
        """
        Save metadata for a file.

        Args:
            path: Path to the file.
            metadata: Metadata to save.
        """
        self._data[path] = metadata
        self._write_to_disk()

    def load(self, path: str) -> Dict[str, Any]:
        """
        Load metadata for a file.

        Args:
            path: Path to the file.

        Returns:
            Metadata for the file, or None if not found.
        """
        return self._data.get(path)

    def delete(self, path: str) -> None:
        """
        Delete metadata for a file.

        Args:
            path: Path to the file.
        """
        if path in self._data:
            del self._data[path]
            self._write_to_disk()

    def load_all(self) -> Iterator[Tuple[str, Dict[str, Any]]]:
        """
        Load all metadata.

        Returns:
            Iterator of (path, metadata) tuples.
        """
        for path, metadata in self._data.items():
            yield path, metadata

    def _write_to_disk(self) -> None:
        """Write data to disk."""
        with open(self.file_path, "w") as f:
            json.dump(self._data, f, indent=2)


class SQLiteDB(StorageBackend):
    """
    SQLite storage backend.

    This backend stores metadata in a SQLite database.
    """

    def __init__(self, db_path: str):
        """
        Initialize a new SQLiteDB.

        Args:
            db_path: Path to the SQLite database.
        """
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        """Initialize the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create table if it doesn't exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS metadata (
            path TEXT PRIMARY KEY,
            data TEXT NOT NULL
        )
        """)

        conn.commit()
        conn.close()

    def save(self, path: str, metadata: Dict[str, Any]) -> None:
        """
        Save metadata for a file.

        Args:
            path: Path to the file.
            metadata: Metadata to save.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Convert metadata to JSON
        data_json = json.dumps(metadata)

        # Insert or replace
        cursor.execute(
            "INSERT OR REPLACE INTO metadata (path, data) VALUES (?, ?)",
            (path, data_json),
        )

        conn.commit()
        conn.close()

    def load(self, path: str) -> Dict[str, Any]:
        """
        Load metadata for a file.

        Args:
            path: Path to the file.

        Returns:
            Metadata for the file, or None if not found.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT data FROM metadata WHERE path = ?", (path,))
        row = cursor.fetchone()

        conn.close()

        if row:
            return json.loads(row[0])
        return None

    def delete(self, path: str) -> None:
        """
        Delete metadata for a file.

        Args:
            path: Path to the file.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM metadata WHERE path = ?", (path,))

        conn.commit()
        conn.close()

    def load_all(self) -> Iterator[Tuple[str, Dict[str, Any]]]:
        """
        Load all metadata.

        Returns:
            Iterator of (path, metadata) tuples.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT path, data FROM metadata")

        for path, data_json in cursor.fetchall():
            yield path, json.loads(data_json)

        conn.close()
