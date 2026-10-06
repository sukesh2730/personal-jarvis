"""
Correction learning system for JARVIS.
Tracks user corrections and applies learnings to future similar queries.
"""
import sqlite3
from datetime import datetime
from dataclasses import dataclass
from typing import List
from db_init import get_connection


@dataclass
class Correction:
    """Represents a correction pair."""
    id: int
    timestamp: str
    original_response: str
    correction: str
    query_context: str


class CorrectionLearner:
    """Manages correction learning from user feedback."""
    
    def __init__(self, db_path="./jarvis.db"):
        """Initialize corrections table."""
        self.db_path = db_path
        self.conn = get_connection(db_path)
    
    def record_correction(self, original: str, correction: str, query: str) -> int:
        """
        Store a correction pair.
        
        Args:
            original: JARVIS's original (incorrect) response
            correction: User's correction
            query: Original query context
            
        Returns:
            ID of stored correction
        """
        cursor = self.conn.cursor()
        timestamp = datetime.now().isoformat()
        
        cursor.execute("""
            INSERT INTO corrections (timestamp, original_response, correction, query_context)
            VALUES (?, ?, ?, ?)
        """, (timestamp, original, correction, query))
        
        self.conn.commit()
        return cursor.lastrowid
    
    def get_corrections(self, limit: int = 10) -> List[Correction]:
        """
        Retrieve recent corrections.
        
        Args:
            limit: Maximum results to return
            
        Returns:
            List of Correction objects
        """
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT id, timestamp, original_response, correction, query_context
            FROM corrections
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))
        
        results = []
        for row in cursor.fetchall():
            results.append(Correction(
                id=row[0],
                timestamp=row[1],
                original_response=row[2],
                correction=row[3],
                query_context=row[4]
            ))
        
        return results
    
    def find_similar_queries(self, query: str, threshold: int = 3) -> List[Correction]:
        """
        Find corrections for similar past queries using keyword overlap.
        
        Args:
            query: Current query
            threshold: Minimum matching words (default: 3)
            
        Returns:
            List of relevant Correction objects
        """
        # Extract keywords from query (lowercase, remove common words)
        stop_words = {'a', 'an', 'the', 'is', 'are', 'was', 'were', 'be', 'been', 
                     'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 
                     'would', 'could', 'should', 'can', 'may', 'might', 'to', 'of', 
                     'in', 'on', 'at', 'for', 'with', 'by', 'from'}
        
        query_words = set(query.lower().split()) - stop_words
        
        if len(query_words) < threshold:
            return []
        
        # Get all corrections and check similarity
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, timestamp, original_response, correction, query_context
            FROM corrections
            ORDER BY timestamp DESC
        """)
        
        similar = []
        for row in cursor.fetchall():
            context_words = set(row[4].lower().split()) - stop_words
            overlap = len(query_words & context_words)
            
            if overlap >= threshold:
                similar.append(Correction(
                    id=row[0],
                    timestamp=row[1],
                    original_response=row[2],
                    correction=row[3],
                    query_context=row[4]
                ))
        
        return similar
    
    def build_correction_context(self, query: str) -> str:
        """
        Build correction context to prepend to system prompt.
        
        Args:
            query: User's query
            
        Returns:
            Formatted correction context string
        """
        similar = self.find_similar_queries(query, threshold=3)
        
        if not similar:
            return ""
        
        context_lines = ["IMPORTANT: Apply these learned corrections:\n"]
        for corr in similar[:3]:  # Limit to top 3
            context_lines.append(f"- When asked about similar topics, note: {corr.correction}")
        
        return "\n".join(context_lines) + "\n\n"
    
    def is_correction(self, user_message: str) -> bool:
        """
        Check if user message is a correction.
        
        Args:
            user_message: User's message
            
        Returns:
            True if message appears to be a correction
        """
        correction_keywords = [
            "actually",
            "correction:",
            "that's wrong",
            "incorrect",
            "no, it's",
            "no it's",
            "you're wrong",
            "that's not right"
        ]
        
        message_lower = user_message.lower()
        return any(keyword in message_lower for keyword in correction_keywords)
    
    def close(self):
        """Close database connection."""
        self.conn.close()
