"""
Database Manager for JARVIS
Provides connection pooling and thread-safe database operations
"""
import sqlite3
import threading
from contextlib import contextmanager
from pathlib import Path


class DatabaseManager:
    """Thread-safe SQLite database manager with connection pooling."""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, db_path: str = "./jarvis.db"):
        """Singleton pattern to ensure single database manager instance."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, db_path: str = "./jarvis.db"):
        """Initialize database manager with connection pooling."""
        if self._initialized:
            return
        
        self.db_path = Path(db_path)
        self._local = threading.local()
        self._initialized = True
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get thread-local database connection."""
        if not hasattr(self._local, 'connection'):
            self._local.connection = sqlite3.connect(
                str(self.db_path),
                check_same_thread=False
            )
            self._local.connection.row_factory = sqlite3.Row
            # Enable foreign keys
            self._local.connection.execute("PRAGMA foreign_keys = ON")
        return self._local.connection
    
    @contextmanager
    def get_cursor(self):
        """Context manager for database operations."""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
    
    def execute(self, query: str, params: tuple = ()):
        """Execute a single query and commit."""
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
    
    def execute_many(self, query: str, params_list: list):
        """Execute multiple queries with different parameters."""
        with self.get_cursor() as cursor:
            cursor.executemany(query, params_list)
    
    def fetch_one(self, query: str, params: tuple = ()):
        """Fetch a single row."""
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchone()
    
    def fetch_all(self, query: str, params: tuple = ()):
        """Fetch all rows."""
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()
    
    def close(self):
        """Close database connection for current thread."""
        if hasattr(self._local, 'connection'):
            self._local.connection.close()
            delattr(self._local, 'connection')


# Global database manager instance
_db_manager = None


def get_db() -> DatabaseManager:
    """Get or create global database manager instance."""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager
