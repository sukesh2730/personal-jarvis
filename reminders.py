"""
Reminder System for JARVIS - Phase 2
Time-based reminder system with natural language parsing and background daemon.
"""
import sqlite3
import threading
import time
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Optional
from dateutil import parser as date_parser
import re


@dataclass
class Reminder:
    """Data class for reminder objects."""
    id: int
    timestamp_created: str
    reminder_time: str
    message: str
    completed: bool


class ReminderSystem:
    """Manages time-based reminders with natural language parsing."""
    
    def __init__(self, db_path="./jarvis.db"):
        """Initialize connection to reminders table."""
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
    
    def create_reminder(self, time_str: str, message: str) -> int:
        """
        Parse time string and create reminder.
        
        Args:
            time_str: Natural language time expression
            message: Reminder message
            
        Returns:
            Reminder ID
        """
        try:
            reminder_time = self._parse_time(time_str)
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO reminders (timestamp_created, reminder_time, message, completed)
                VALUES (?, ?, ?, 0)
            """, (datetime.now().isoformat(), reminder_time.isoformat(), message))
            self.conn.commit()
            return cursor.lastrowid
        except Exception as e:
            raise ValueError(f"Could not parse time '{time_str}', sir. Please use formats like: 'in 30 minutes', 'tomorrow 9am', '2024-12-25 10:00'")
    
    def _parse_time(self, time_str: str) -> datetime:
        """
        Parse natural language time expressions.
        
        Supported formats:
        - "in X minutes"
        - "in X hours"
        - "tomorrow HH:MM"
        - "YYYY-MM-DD HH:MM"
        - Natural language via dateutil
        """
        time_str = time_str.lower().strip()
        now = datetime.now()
        
        # Pattern: "in X minutes"
        match = re.match(r'in (\d+) minute[s]?', time_str)
        if match:
            minutes = int(match.group(1))
            return now + timedelta(minutes=minutes)
        
        # Pattern: "in X hours"
        match = re.match(r'in (\d+) hour[s]?', time_str)
        if match:
            hours = int(match.group(1))
            return now + timedelta(hours=hours)
        
        # Pattern: "tomorrow HH:MM"
        if time_str.startswith("tomorrow "):
            time_part = time_str.replace("tomorrow ", "").strip()
            parsed_time = date_parser.parse(time_part, fuzzy=True)
            tomorrow = now + timedelta(days=1)
            return tomorrow.replace(hour=parsed_time.hour, minute=parsed_time.minute, second=0, microsecond=0)
        
        # Try dateutil parser for other formats
        try:
            parsed = date_parser.parse(time_str, fuzzy=True)
            # If no date specified, assume today if time is in future, otherwise tomorrow
            if parsed.date() == datetime(1900, 1, 1).date():
                target = now.replace(hour=parsed.hour, minute=parsed.minute, second=0, microsecond=0)
                if target <= now:
                    target += timedelta(days=1)
                return target
            return parsed
        except:
            raise ValueError("Invalid time format")
    
    def list_reminders(self) -> List[Reminder]:
        """Get all pending reminders."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, timestamp_created, reminder_time, message, completed
            FROM reminders
            WHERE completed = 0
            ORDER BY reminder_time ASC
        """)
        
        reminders = []
        for row in cursor.fetchall():
            reminders.append(Reminder(
                id=row['id'],
                timestamp_created=row['timestamp_created'],
                reminder_time=row['reminder_time'],
                message=row['message'],
                completed=bool(row['completed'])
            ))
        return reminders
    
    def mark_done(self, reminder_id: int) -> bool:
        """Mark reminder as completed."""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE reminders SET completed = 1 WHERE id = ?
        """, (reminder_id,))
        self.conn.commit()
        return cursor.rowcount > 0
    
    def check_due_reminders(self) -> List[Reminder]:
        """Check for reminders due now."""
        cursor = self.conn.cursor()
        now = datetime.now().isoformat()
        cursor.execute("""
            SELECT id, timestamp_created, reminder_time, message, completed
            FROM reminders
            WHERE completed = 0 AND reminder_time <= ?
            ORDER BY reminder_time ASC
        """, (now,))
        
        reminders = []
        for row in cursor.fetchall():
            reminders.append(Reminder(
                id=row['id'],
                timestamp_created=row['timestamp_created'],
                reminder_time=row['reminder_time'],
                message=row['message'],
                completed=bool(row['completed'])
            ))
        return reminders


def reminder_daemon(reminder_system, tts=None, audio=None):
    """
    Background daemon that checks for due reminders every 60 seconds.
    
    Args:
        reminder_system: ReminderSystem instance
        tts: TTS module for spoken reminders (optional)
        audio: AudioFeedback for notification sounds (optional)
    """
    while True:
        try:
            due_reminders = reminder_system.check_due_reminders()
            for reminder in due_reminders:
                # Format reminder message
                message = f"Reminder, sir: {reminder.message}"
                print(f"\n[REMINDER] {message}")
                
                # Speak if TTS available
                if tts and hasattr(tts, 'speak_async'):
                    tts.speak_async(message)
                
                # Play notification sound if audio available
                if audio and hasattr(audio, 'play'):
                    try:
                        audio.play("notification")
                    except:
                        pass
                
                # Mark as completed
                reminder_system.mark_done(reminder.id)
            
            time.sleep(60)  # Check every 60 seconds
        except Exception as e:
            # Log error but keep daemon running
            print(f"[REMINDER DAEMON ERROR] {e}")
            time.sleep(60)


def start_reminder_daemon(reminder_system, tts=None, audio=None):
    """
    Start reminder daemon as a background thread.
    
    Args:
        reminder_system: ReminderSystem instance
        tts: TTS module (optional)
        audio: AudioFeedback module (optional)
        
    Returns:
        Thread object
    """
    thread = threading.Thread(
        target=reminder_daemon,
        args=(reminder_system, tts, audio),
        daemon=True
    )
    thread.start()
    return thread
