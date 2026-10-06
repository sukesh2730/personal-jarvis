"""
Database initialization for JARVIS 20-Feature Extension.
Creates SQLite database with all required tables and indexes.
"""
import sqlite3
import os
from datetime import datetime
from pathlib import Path


def init_database(db_path="./jarvis.db"):
    """
    Initialize the JARVIS database with all required tables.
    
    Creates 7 tables for:
    - Long-term memories
    - Correction learning
    - Reminders
    - Notes
    - Habits
    - Focus sessions
    
    Args:
        db_path: Path to SQLite database file (default: ./jarvis.db)
        
    Returns:
        Connection object
    """
    # Ensure directory exists
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(db_path, check_same_thread=False)
    cursor = conn.cursor()
    
    # Enable foreign key constraints
    cursor.execute("PRAGMA foreign_keys = ON")
    
    # Long-term memory storage
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            category TEXT NOT NULL,
            content TEXT NOT NULL,
            source TEXT NOT NULL
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_memories_category ON memories(category)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_memories_timestamp ON memories(timestamp)")
    
    # Correction learning
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS corrections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            original_response TEXT NOT NULL,
            correction TEXT NOT NULL,
            query_context TEXT NOT NULL
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_corrections_timestamp ON corrections(timestamp DESC)")
    
    # Reminder system
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp_created TEXT NOT NULL,
            reminder_time TEXT NOT NULL,
            message TEXT NOT NULL,
            completed INTEGER DEFAULT 0
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_reminders_time ON reminders(reminder_time)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_reminders_completed ON reminders(completed)")
    
    # Note capture
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            content TEXT NOT NULL,
            tags TEXT
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_notes_timestamp ON notes(timestamp DESC)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_notes_tags ON notes(tags)")
    
    # Habit tracking
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS habits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            created_date TEXT NOT NULL,
            streak_count INTEGER DEFAULT 0
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS habit_completions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            habit_id INTEGER NOT NULL,
            completion_date TEXT NOT NULL,
            FOREIGN KEY (habit_id) REFERENCES habits(id),
            UNIQUE(habit_id, completion_date)
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_habit_completions_date ON habit_completions(completion_date)")
    
    # Focus sessions
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS focus_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            start_time TEXT NOT NULL,
            duration_minutes INTEGER NOT NULL,
            interruptions_count INTEGER DEFAULT 0
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_focus_sessions_start ON focus_sessions(start_time DESC)")
    
    # Database version tracking
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS db_version (
            version INTEGER PRIMARY KEY,
            applied_at TEXT
        )
    """)
    
    # Insert initial version if not exists
    cursor.execute("SELECT COUNT(*) FROM db_version WHERE version = 1")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO db_version (version, applied_at) VALUES (1, ?)", 
                      (datetime.now().isoformat(),))
    
    conn.commit()
    return conn


def get_connection(db_path="./jarvis.db"):
    """
    Get database connection with connection pooling support.
    
    Args:
        db_path: Path to SQLite database file
        
    Returns:
        SQLite connection object
    """
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row  # Enable dict-like access to rows
    return conn


if __name__ == "__main__":
    # Initialize database when run directly
    conn = init_database()
    print("✓ Database initialized: jarvis.db")
    print("✓ All tables and indexes created")
    conn.close()
