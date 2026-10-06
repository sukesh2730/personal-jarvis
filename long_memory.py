"""
Long-term memory system for JARVIS.
Stores user facts, preferences, and decisions across sessions.
"""
import sqlite3
import re
from datetime import datetime
from dataclasses import dataclass
from typing import List, Optional
from db_init import get_connection


@dataclass
class Memory:
    """Represents a stored memory."""
    id: int
    timestamp: str
    category: str
    content: str
    source: str


class LongMemory:
    """Manages persistent long-term memories across JARVIS sessions."""
    
    def __init__(self, db_path="./jarvis.db"):
        """Initialize connection to memories table."""
        self.db_path = db_path
        self.conn = get_connection(db_path)
    
    def remember(self, content: str, category: str = "general", source: str = "manual") -> int:
        """
        Store a memory.
        
        Args:
            content: The fact or information to remember
            category: Category (general, preference, decision, fact)
            source: How memory was created (manual, auto)
            
        Returns:
            ID of stored memory
        """
        cursor = self.conn.cursor()
        timestamp = datetime.now().isoformat()
        
        cursor.execute("""
            INSERT INTO memories (timestamp, category, content, source)
            VALUES (?, ?, ?, ?)
        """, (timestamp, category, content, source))
        
        self.conn.commit()
        return cursor.lastrowid
    
    def recall(self, query: str, limit: int = 5) -> List[Memory]:
        """
        Search memories using full-text search.
        
        Args:
            query: Search query
            limit: Maximum results to return
            
        Returns:
            List of matching Memory objects
        """
        cursor = self.conn.cursor()
        
        # Simple LIKE search (SQLite FTS would require separate setup)
        cursor.execute("""
            SELECT id, timestamp, category, content, source
            FROM memories
            WHERE content LIKE ? OR category LIKE ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (f"%{query}%", f"%{query}%", limit))
        
        results = []
        for row in cursor.fetchall():
            results.append(Memory(
                id=row[0],
                timestamp=row[1],
                category=row[2],
                content=row[3],
                source=row[4]
            ))
        
        return results
    
    def recall_all(self, limit: int = 10) -> List[Memory]:
        """
        Get all recent memories.
        
        Args:
            limit: Maximum results to return
            
        Returns:
            List of Memory objects
        """
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT id, timestamp, category, content, source
            FROM memories
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))
        
        results = []
        for row in cursor.fetchall():
            results.append(Memory(
                id=row[0],
                timestamp=row[1],
                category=row[2],
                content=row[3],
                source=row[4]
            ))
        
        return results
    
    def forget(self, memory_id: int) -> bool:
        """
        Delete a memory by ID.
        
        Args:
            memory_id: ID of memory to delete
            
        Returns:
            True if deleted, False if not found
        """
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
        self.conn.commit()
        return cursor.rowcount > 0
    
    def auto_extract(self, user_message: str, assistant_response: str = "") -> Optional[str]:
        """
        Extract memorable facts from conversation using pattern matching.
        
        Args:
            user_message: User's message
            assistant_response: JARVIS's response (optional)
            
        Returns:
            Extracted memory content or None
        """
        # Pattern matching for memorable statements
        patterns = [
            (r"(?:remember|recall|keep in mind) (?:that )?(.+)", "general"),
            (r"I prefer (.+)", "preference"),
            (r"my favorite (.+) is (.+)", "preference"),
            (r"always (.+)", "preference"),
            (r"never (.+)", "preference"),
        ]
        
        for pattern, category in patterns:
            match = re.search(pattern, user_message, re.IGNORECASE)
            if match:
                content = match.group(1).strip()
                if content:
                    # Store the memory
                    self.remember(content, category=category, source="auto")
                    return content
        
        return None
    
    def get_all_categories(self) -> List[str]:
        """Get list of all memory categories."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT DISTINCT category FROM memories")
        return [row[0] for row in cursor.fetchall()]
    
    def close(self):
        """Close database connection."""
        self.conn.close()
