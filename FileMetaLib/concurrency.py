# concurrency.py
"""
Concurrency utilities for FileMetaLib.
"""

import threading
import time
from typing import Dict, Any, Callable, Optional, TypeVar, Generic

T = TypeVar("T")


class ReadWriteLock:
    """
    A lock object that allows many simultaneous "read locks", but only one "write lock."

    This is useful for protecting data structures that are frequently read but seldom modified.
    """

    def __init__(self):
        """Initialize a new ReadWriteLock."""
        self._read_ready = threading.Condition(threading.RLock())
        self._readers = 0
        self._writers = 0
        self._write_waiting = 0
        self._promote_waiting = 0

    def acquire_read(self):
        """
        Acquire a read lock.

        Blocks only if a thread has acquired or is waiting for the write lock.
        """
        with self._read_ready:
            while self._writers > 0 or self._write_waiting > 0:
                self._read_ready.wait()
            self._readers += 1

    def release_read(self):
        """Release a read lock."""
        with self._read_ready:
            self._readers -= 1
            if self._readers == 0:
                self._read_ready.notify_all()

    def acquire_write(self):
        """
        Acquire a write lock.

        Blocks until there are no active readers or writers.
        """
        with self._read_ready:
            self._write_waiting += 1
            while self._readers > 0 or self._writers > 0:
                self._read_ready.wait()
            self._write_waiting -= 1
            self._writers += 1

    def release_write(self):
        """Release a write lock."""
        with self._read_ready:
            self._writers -= 1
            self._read_ready.notify_all()

    def __enter__(self):
        """Enter context manager for write lock."""
        self.acquire_write()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager for write lock."""
        self.release_write()


class ReadLock:
    """Context manager for read locks."""

    def __init__(self, lock: ReadWriteLock):
        """
        Initialize a new ReadLock.

        Args:
            lock: ReadWriteLock to use.
        """
        self.lock = lock

    def __enter__(self):
        """Enter context manager."""
        self.lock.acquire_read()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager."""
        self.lock.release_read()


class WriteLock:
    """Context manager for write locks."""

    def __init__(self, lock: ReadWriteLock):
        """
        Initialize a new WriteLock.

        Args:
            lock: ReadWriteLock to use.
        """
        self.lock = lock

    def __enter__(self):
        """Enter context manager."""
        self.lock.acquire_write()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager."""
        self.lock.release_write()


class Transaction:
    """
    Transaction manager for atomic operations.

    This class provides a way to perform multiple operations atomically.
    """

    def __init__(self, commit_func: Callable, rollback_func: Callable):
        """
        Initialize a new Transaction.

        Args:
            commit_func: Function to call on commit.
            rollback_func: Function to call on rollback.
        """
        self.commit_func = commit_func
        self.rollback_func = rollback_func
        self.operations = []
        self.committed = False
        self.rolled_back = False

    def add_operation(self, operation: Callable, undo_operation: Callable):
        """
        Add an operation to the transaction.

        Args:
            operation: Operation to perform.
            undo_operation: Operation to undo the operation.
        """
        if self.committed or self.rolled_back:
            raise ValueError("Transaction already committed or rolled back")

        self.operations.append((operation, undo_operation))

    def commit(self):
        """
        Commit the transaction.

        Raises:
            Exception: If an operation fails.
        """
        if self.committed or self.rolled_back:
            raise ValueError("Transaction already committed or rolled back")

        try:
            # Execute all operations
            for operation, _ in self.operations:
                operation()

            # Call commit function
            self.commit_func()

            self.committed = True
        except Exception as e:
            # Rollback on failure
            self.rollback()
            raise e

    def rollback(self):
        """Roll back the transaction."""
        if self.committed or self.rolled_back:
            raise ValueError("Transaction already committed or rolled back")

        # Execute undo operations in reverse order
        for _, undo_operation in reversed(self.operations):
            try:
                undo_operation()
            except Exception:
                # Ignore errors in undo operations
                pass

        # Call rollback function
        self.rollback_func()

        self.rolled_back = True

    def __enter__(self):
        """Enter context manager."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager."""
        if exc_type is None:
            # No exception, commit
            self.commit()
        else:
            # Exception, rollback
            self.rollback()
            return False


class Cache(Generic[T]):
    """
    Thread-safe cache with expiration.

    This class provides a thread-safe cache with expiration.
    """

    def __init__(self, max_size: int = 100, ttl: int = 300):
        """
        Initialize a new Cache.

        Args:
            max_size: Maximum number of items in the cache.
            ttl: Time to live in seconds.
        """
        self.max_size = max_size
        self.ttl = ttl
        self.cache = {}
        self.timestamps = {}
        self.lock = threading.RLock()

        # Start cleanup thread
        self.running = True
        self.cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self.cleanup_thread.start()

    def get(self, key: str) -> Optional[T]:
        """
        Get an item from the cache.

        Args:
            key: Key to get.

        Returns:
            Item, or None if not found or expired.
        """
        with self.lock:
            if key not in self.cache:
                return None

            # Check if expired
            timestamp = self.timestamps[key]
            if self.ttl > 0 and time.time() - timestamp > self.ttl:
                # Expired, remove
                del self.cache[key]
                del self.timestamps[key]
                return None

            # Update timestamp
            self.timestamps[key] = time.time()

            return self.cache[key]

    def set(self, key: str, value: T) -> None:
        """
        Set an item in the cache.

        Args:
            key: Key to set.
            value: Value to set.
        """
        with self.lock:
            # Check if cache is full
            if len(self.cache) >= self.max_size and key not in self.cache:
                # Remove oldest item
                oldest_key = min(self.timestamps, key=lambda k: self.timestamps[k])
                del self.cache[oldest_key]
                del self.timestamps[oldest_key]

            # Set item
            self.cache[key] = value
            self.timestamps[key] = time.time()

    def delete(self, key: str) -> None:
        """
        Delete an item from the cache.

        Args:
            key: Key to delete.
        """
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                del self.timestamps[key]

    def clear(self) -> None:
        """Clear the cache."""
        with self.lock:
            self.cache.clear()
            self.timestamps.clear()

    def stop(self) -> None:
        """Stop the cleanup thread."""
        self.running = False
        self.cleanup_thread.join(timeout=1)

    def _cleanup_loop(self) -> None:
        """Cleanup loop for expired items."""
        while self.running:
            time.sleep(min(self.ttl / 2, 60) if self.ttl > 0 else 60)
            self._cleanup()

    def _cleanup(self) -> None:
        """Clean up expired items."""
        if self.ttl <= 0:
            return

        with self.lock:
            now = time.time()
            expired_keys = [
                key
                for key, timestamp in self.timestamps.items()
                if now - timestamp > self.ttl
            ]

            for key in expired_keys:
                del self.cache[key]
                del self.timestamps[key]


class BackgroundTask:
    """
    Background task manager.

    This class provides a way to run tasks in the background.
    """

    def __init__(self, interval: int = 0, daemon: bool = True):
        """
        Initialize a new BackgroundTask.

        Args:
            interval: Interval in seconds between runs, or 0 for one-time tasks.
            daemon: Whether the thread should be a daemon thread.
        """
        self.interval = interval
        self.daemon = daemon
        self.running = False
        self.thread = None

    def start(self, task: Callable, *args, **kwargs) -> None:
        """
        Start the task.

        Args:
            task: Task to run.
            *args: Arguments to pass to the task.
            **kwargs: Keyword arguments to pass to the task.
        """
        if self.running:
            raise ValueError("Task already running")

        self.running = True

        def run():
            while self.running:
                try:
                    task(*args, **kwargs)
                except Exception as e:
                    print(f"Error in background task: {e}")

                if self.interval <= 0:
                    # One-time task
                    self.running = False
                    break

                time.sleep(self.interval)

        self.thread = threading.Thread(target=run, daemon=self.daemon)
        self.thread.start()

    def stop(self) -> None:
        """Stop the task."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1)
            self.thread = None
