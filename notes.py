"""
Quick note capture system for JARVIS.
Stores notes with hashtag tagging, full-text search, and markdown export.
"""
import sqlite3
import re
from datetime import datetime
from dataclasses import dataclass
from typing import List, Optional
from pathlib import Path
from db_init import get_connection


@dataclass
class Note:
    """Represents a captured note."""
    id: int
    timestamp: str
    content: str
    tags: str


class NotesSystem:
    """Manages quick note capture with tagging and search."""
    
    def __init__(self, db_path="./jarvis.db"):
        """Initialize notes table."""
        self.db_path = db_path
        self.conn = get_connection(db_path)
    
    def add_note(self, content: str) -> int:
        """
        Add a note and extract tags.
        
        Args:
            content: Note content (can include #hashtags)
            
        Returns:
            ID of stored note
        """
        cursor = self.conn.cursor()
        timestamp = datetime.now().isoformat()
        
        # Extract hashtags
        tags = self._extract_tags(content)
        tags_str = ",".join(tags) if tags else ""
        
        cursor.execute("""
            INSERT INTO notes (timestamp, content, tags)
            VALUES (?, ?, ?)
        """, (timestamp, content, tags_str))
        
        self.conn.commit()
        return cursor.lastrowid
    
    def search_notes(self, query: Optional[str] = None, limit: int = 10) -> List[Note]:
        """
        Search notes by content or tags.
        
        Args:
            query: Search query (None = show recent)
            limit: Maximum results
            
        Returns:
            List of Note objects
        """
        cursor = self.conn.cursor()
        
        if query is None:
            # Show recent notes
            cursor.execute("""
                SELECT id, timestamp, content, tags
                FROM notes
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))
        else:
            # Full-text search on content and tags
            cursor.execute("""
                SELECT id, timestamp, content, tags
                FROM notes
                WHERE content LIKE ? OR tags LIKE ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (f"%{query}%", f"%{query}%", limit))
        
        results = []
        for row in cursor.fetchall():
            results.append(Note(
                id=row[0],
                timestamp=row[1],
                content=row[2],
                tags=row[3]
            ))
        
        return results
    
    def export_notes(self, date: str) -> str:
        """
        Export notes for a specific date to markdown.
        
        Args:
            date: Date in YYYY-MM-DD format
            
        Returns:
            Path to exported markdown file
        """
        cursor = self.conn.cursor()
        
        # Query notes for the date
        cursor.execute("""
            SELECT timestamp, content, tags
            FROM notes
            WHERE date(timestamp) = ?
            ORDER BY timestamp ASC
        """, (date,))
        
        notes = cursor.fetchall()
        
        if not notes:
            return None
        
        # Create export directory
        export_dir = Path("./logs/notes")
        export_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate markdown
        filepath = export_dir / f"{date}_notes.md"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# Notes - {date}\n\n")
            
            for timestamp, content, tags in notes:
                time_str = timestamp.split('T')[1].split('.')[0]  # Extract HH:MM:SS
                f.write(f"## {time_str}\n\n")
                f.write(f"{content}\n\n")
                
                if tags:
                    f.write(f"*Tags: {tags}*\n\n")
                
                f.write("---\n\n")
        
        return str(filepath)
    
    def _extract_tags(self, content: str) -> List[str]:
        """
        Extract hashtags from content.
        
        Args:
            content: Note content
            
        Returns:
            List of tag strings (without #)
        """
        tags = re.findall(r'#(\w+)', content)
        return list(set(tags))  # Remove duplicates
    
    def delete_note(self, note_id: int) -> bool:
        """
        Delete a note by ID.
        
        Args:
            note_id: ID of note to delete
            
        Returns:
            True if deleted, False if not found
        """
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        self.conn.commit()
        return cursor.rowcount > 0
    
    def close(self):
        """Close database connection."""
        self.conn.close()
