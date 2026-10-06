"""
Daily Habit Tracker for JARVIS - Phase 2
Tracks daily habits with streak calculation and 8 PM notifier daemon.
"""
import sqlite3
import threading
import time
from datetime import datetime, timedelta, date
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Habit:
    """Data class for habit objects."""
    id: int
    name: str
    created_date: str
    streak_count: int
    completed_today: bool


class HabitTracker:
    """Manages daily habit tracking with streak calculation."""
    
    def __init__(self, db_path="./jarvis.db"):
        """Initialize connection to habits tables."""
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
    
    def add_habit(self, name: str) -> int:
        """
        Create new habit.
        
        Args:
            name: Habit name
            
        Returns:
            Habit ID
        """
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO habits (name, created_date, streak_count)
                VALUES (?, ?, 0)
            """, (name, date.today().isoformat()))
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            raise ValueError(f"Habit '{name}' already exists, sir.")
    
    def complete_habit(self, name: str) -> bool:
        """
        Mark habit complete for today.
        
        Args:
            name: Habit name
            
        Returns:
            True if completed, False if already done today
        """
        cursor = self.conn.cursor()
        
        # Get habit ID
        cursor.execute("SELECT id FROM habits WHERE name = ?", (name,))
        row = cursor.fetchone()
        if not row:
            raise ValueError(f"Habit '{name}' not found, sir.")
        
        habit_id = row['id']
        today = date.today().isoformat()
        
        # Check if already completed today
        cursor.execute("""
            SELECT COUNT(*) as count FROM habit_completions
            WHERE habit_id = ? AND completion_date = ?
        """, (habit_id, today))
        
        if cursor.fetchone()['count'] > 0:
            return False  # Already completed today
        
        # Insert completion
        cursor.execute("""
            INSERT INTO habit_completions (habit_id, completion_date)
            VALUES (?, ?)
        """, (habit_id, today))
        
        # Update streak
        new_streak = self.calculate_streak(habit_id)
        cursor.execute("""
            UPDATE habits SET streak_count = ? WHERE id = ?
        """, (new_streak, habit_id))
        
        self.conn.commit()
        return True
    
    def list_habits(self) -> List[Habit]:
        """Get all habits with completion status and streaks."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, name, created_date, streak_count
            FROM habits
            ORDER BY name ASC
        """)
        
        today = date.today().isoformat()
        habits = []
        
        for row in cursor.fetchall():
            # Check if completed today
            cursor.execute("""
                SELECT COUNT(*) as count FROM habit_completions
                WHERE habit_id = ? AND completion_date = ?
            """, (row['id'], today))
            completed_today = cursor.fetchone()['count'] > 0
            
            habits.append(Habit(
                id=row['id'],
                name=row['name'],
                created_date=row['created_date'],
                streak_count=row['streak_count'],
                completed_today=completed_today
            ))
        
        return habits
    
    def calculate_streak(self, habit_id: int) -> int:
        """
        Calculate current streak length.
        
        Counts consecutive days with completions, working backwards from today.
        
        Args:
            habit_id: Habit ID
            
        Returns:
            Streak count
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT completion_date FROM habit_completions
            WHERE habit_id = ?
            ORDER BY completion_date DESC
        """, (habit_id,))
        
        completion_dates = [datetime.fromisoformat(row['completion_date']).date() 
                          for row in cursor.fetchall()]
        
        if not completion_dates:
            return 0
        
        today = date.today()
        streak = 0
        
        for i in range(365):  # Max 1 year lookback
            check_date = today - timedelta(days=i)
            if check_date in completion_dates:
                streak += 1
            else:
                break
        
        return streak


def habit_notifier_daemon(habit_tracker, tts=None):
    """
    Background daemon that sends 8 PM reminders for incomplete habits.
    
    Args:
        habit_tracker: HabitTracker instance
        tts: TTS module for spoken notifications (optional)
    """
    last_notification_date = None
    
    while True:
        try:
            now = datetime.now()
            today = date.today()
            
            # Check if it's 8:00 PM and we haven't notified today
            if now.hour == 20 and now.minute == 0 and last_notification_date != today:
                habits = habit_tracker.list_habits()
                incomplete = [h for h in habits if not h.completed_today]
                
                if incomplete:
                    habit_names = ", ".join(h.name for h in incomplete)
                    message = f"Sir, {len(incomplete)} habits remain incomplete today: {habit_names}"
                    print(f"\n[HABIT REMINDER] {message}")
                    
                    # Speak if TTS available
                    if tts and hasattr(tts, 'speak_async'):
                        tts.speak_async(f"Sir, {len(incomplete)} habits remain incomplete today.")
                    
                    last_notification_date = today
            
            time.sleep(60)  # Check every 60 seconds
        except Exception as e:
            # Log error but keep daemon running
            print(f"[HABIT DAEMON ERROR] {e}")
            time.sleep(60)


def start_habit_notifier(habit_tracker, tts=None):
    """
    Start habit notifier daemon as a background thread.
    
    Args:
        habit_tracker: HabitTracker instance
        tts: TTS module (optional)
        
    Returns:
        Thread object
    """
    thread = threading.Thread(
        target=habit_notifier_daemon,
        args=(habit_tracker, tts),
        daemon=True
    )
    thread.start()
    return thread
