"""
Focus Mode Timer for JARVIS - Phase 2
Pomodoro-style focus timer with command blocking and countdown warnings.
"""
import sqlite3
import threading
import time
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Dict, Optional


class FocusMode:
    """Manages Pomodoro-style focus sessions with command blocking."""
    
    def __init__(self, db_path="./jarvis.db"):
        """Initialize focus_sessions table."""
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        
        self.active = False
        self.start_time = None
        self.end_time = None
        self.duration_minutes = 0
        self.interruptions = 0
        self.timer_thread = None
        
        # Tracking for warnings
        self.five_minute_warning_spoken = False
        self.one_minute_warning_spoken = False
        
        # External callbacks
        self.tts = None
        self.audio = None
    
    def start(self, duration_minutes: int = 25, tts=None, audio=None):
        """
        Start focus session.
        
        Args:
            duration_minutes: Focus session duration (default: 25)
            tts: TTS module for warnings
            audio: AudioFeedback for completion sound
        """
        if self.active:
            remaining = (self.end_time - datetime.now()).total_seconds() / 60
            return f"Focus mode already active, sir. {remaining:.0f} minutes remaining."
        
        self.active = True
        self.start_time = datetime.now()
        self.end_time = self.start_time + timedelta(minutes=duration_minutes)
        self.duration_minutes = duration_minutes
        self.interruptions = 0
        self.tts = tts
        self.audio = audio
        
        # Reset warning flags
        self.five_minute_warning_spoken = False
        self.one_minute_warning_spoken = False
        
        # Start timer thread
        self.timer_thread = threading.Thread(
            target=self._focus_timer_thread,
            daemon=True
        )
        self.timer_thread.start()
        
        return f"Focus mode active for {duration_minutes} minutes, sir. I shall block distracting commands."
    
    def _focus_timer_thread(self):
        """Background thread that monitors focus timer."""
        while self.active:
            try:
                now = datetime.now()
                
                # Check for warnings
                remaining_seconds = (self.end_time - now).total_seconds()
                remaining_minutes = remaining_seconds / 60
                
                # 5-minute warning
                if remaining_minutes <= 5 and remaining_minutes > 4.5 and not self.five_minute_warning_spoken:
                    self._speak_warning("Five minutes remaining, sir.")
                    self.five_minute_warning_spoken = True
                
                # 1-minute warning
                if remaining_minutes <= 1 and remaining_minutes > 0.5 and not self.one_minute_warning_spoken:
                    self._speak_warning("One minute remaining, sir.")
                    self.one_minute_warning_spoken = True
                
                # Check if time is up
                if now >= self.end_time:
                    self._complete_session()
                    break
                
                time.sleep(10)  # Check every 10 seconds
            except Exception as e:
                print(f"[FOCUS TIMER ERROR] {e}")
                time.sleep(10)
    
    def _speak_warning(self, message: str):
        """Speak countdown warning."""
        print(f"\n[FOCUS] {message}")
        if self.tts and hasattr(self.tts, 'speak_async'):
            try:
                self.tts.speak_async(message)
            except:
                pass
    
    def _complete_session(self):
        """Complete focus session and log to database."""
        self.active = False
        
        # Log to database
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO focus_sessions (start_time, duration_minutes, interruptions_count)
            VALUES (?, ?, ?)
        """, (self.start_time.isoformat(), self.duration_minutes, self.interruptions))
        self.conn.commit()
        
        # Notify completion
        message = "Focus session complete, sir. Well done."
        print(f"\n[FOCUS] {message}")
        
        if self.tts and hasattr(self.tts, 'speak_async'):
            try:
                self.tts.speak_async(message)
            except:
                pass
        
        # Play completion sound
        if self.audio and hasattr(self.audio, 'play'):
            try:
                self.audio.play("notification")
            except:
                pass
    
    def is_command_allowed(self, command: str) -> bool:
        """
        Check if command allowed during focus.
        
        Only /help, /quit, and /focus commands are allowed.
        
        Args:
            command: Command string
            
        Returns:
            True if allowed, False if blocked
        """
        if not self.active:
            return True
        
        allowed_commands = ["/help", "/quit", "/exit", "/focus", "/focus-stats"]
        
        # Check if command starts with any allowed command
        for allowed in allowed_commands:
            if command.startswith(allowed):
                return True
        
        return False
    
    def get_remaining_time(self) -> Optional[str]:
        """Get remaining time in focus session."""
        if not self.active:
            return None
        
        remaining = (self.end_time - datetime.now()).total_seconds() / 60
        if remaining < 0:
            return "Session ending..."
        return f"{remaining:.0f} minutes remaining"
    
    def end_early(self):
        """End focus session early."""
        if not self.active:
            return "No focus session active, sir."
        
        self.interruptions += 1
        self._complete_session()
        return "Focus session ended early, sir."
    
    def get_stats(self, days: int = 1) -> Dict:
        """
        Get focus session statistics.
        
        Args:
            days: Number of days to look back (1=today, 7=this week)
            
        Returns:
            Dict with stats
        """
        cursor = self.conn.cursor()
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        
        # Total sessions
        cursor.execute("""
            SELECT COUNT(*) as count FROM focus_sessions
            WHERE start_time >= ?
        """, (cutoff,))
        total_sessions = cursor.fetchone()['count']
        
        # Total minutes
        cursor.execute("""
            SELECT SUM(duration_minutes) as total FROM focus_sessions
            WHERE start_time >= ?
        """, (cutoff,))
        total_minutes = cursor.fetchone()['total'] or 0
        
        # Average session length
        if total_sessions > 0:
            avg_session = total_minutes / total_sessions
        else:
            avg_session = 0
        
        period = "today" if days == 1 else f"last {days} days"
        
        return {
            "total_sessions": total_sessions,
            "total_minutes": total_minutes,
            "avg_session_minutes": round(avg_session, 1),
            "period": period
        }
