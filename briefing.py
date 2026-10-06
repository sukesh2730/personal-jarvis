"""
Morning Briefing for JARVIS - Phase 4
Generates morning briefing with weather, calendar, and productivity stats.
"""
import os
import json
from datetime import datetime, date
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class Event:
    """Calendar event data class."""
    time: str
    title: str
    description: Optional[str] = None


def generate_briefing(db_path: str = "./jarvis.db", 
                     calendar_path: str = "./calendar.json") -> str:
    """
    Generate morning briefing text.
    
    Args:
        db_path: Path to JARVIS database
        calendar_path: Path to calendar JSON file
        
    Returns:
        Formatted briefing text
    """
    lines = []
    
    # Greeting
    now = datetime.now()
    hour = now.hour
    
    if hour < 12:
        greeting = "Good morning, sir."
    elif hour < 18:
        greeting = "Good afternoon, sir."
    else:
        greeting = "Good evening, sir."
    
    lines.append(greeting)
    lines.append(f"{now.strftime('%A, %B %d, %Y')} - {now.strftime('%I:%M %p')}")
    lines.append("")
    
    # Weather
    weather_info = get_weather()
    if weather_info:
        lines.append(f"Weather: {weather_info}")
        lines.append("")
    
    # Calendar events
    events = get_calendar_summary(calendar_path)
    if events:
        lines.append(f"Your calendar shows {len(events)} event{'s' if len(events) != 1 else ''} today:")
        for event in events:
            lines.append(f"  - {event.time}: {event.title}")
        lines.append("")
    else:
        lines.append("No calendar events scheduled today.")
        lines.append("")
    
    # Productivity stats
    stats = get_productivity_stats(db_path)
    if stats:
        lines.append("Productivity overview:")
        if stats.get('pending_reminders', 0) > 0:
            lines.append(f"  - {stats['pending_reminders']} pending reminder{'s' if stats['pending_reminders'] != 1 else ''}")
        if stats.get('incomplete_habits', 0) > 0:
            lines.append(f"  - {stats['incomplete_habits']} habit{'s' if stats['incomplete_habits'] != 1 else ''} to complete today")
        if stats.get('notes_yesterday', 0) > 0:
            lines.append(f"  - {stats['notes_yesterday']} note{'s' if stats['notes_yesterday'] != 1 else ''} captured yesterday")
        lines.append("")
    
    # Closing
    lines.append("Shall we begin, sir?")
    
    return "\n".join(lines)


def get_weather() -> Optional[str]:
    """
    Fetch weather from wttr.in (simple, no API key needed).
    
    Returns:
        Weather string or None if unavailable
    """
    try:
        import requests
        
        # Use wttr.in for simple weather without API key
        response = requests.get("https://wttr.in/?format=%C+%t", timeout=5)
        
        if response.status_code == 200:
            weather = response.text.strip()
            return weather
        return None
    except ImportError:
        # requests not available
        return None
    except Exception:
        # Network error or timeout
        return None


def get_calendar_summary(calendar_path: str = "./calendar.json") -> List[Event]:
    """
    Read calendar.json and get today's events.
    
    Args:
        calendar_path: Path to calendar JSON file
        
    Returns:
        List of Event objects for today
    """
    if not os.path.exists(calendar_path):
        return []
    
    try:
        with open(calendar_path, 'r', encoding='utf-8') as f:
            calendar_data = json.load(f)
        
        today = date.today().isoformat()
        events = []
        
        # Look for today's events
        for event_data in calendar_data.get('events', []):
            event_date = event_data.get('date', '')
            if event_date == today:
                events.append(Event(
                    time=event_data.get('time', ''),
                    title=event_data.get('title', 'Untitled'),
                    description=event_data.get('description')
                ))
        
        # Sort by time
        events.sort(key=lambda e: e.time)
        return events
    
    except Exception:
        return []


def get_productivity_stats(db_path: str = "./jarvis.db") -> Dict:
    """
    Get productivity statistics from database.
    
    Args:
        db_path: Path to JARVIS database
        
    Returns:
        Dict with stats
    """
    if not os.path.exists(db_path):
        return {}
    
    try:
        import sqlite3
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # Count pending reminders
        cursor.execute("SELECT COUNT(*) FROM reminders WHERE completed = 0")
        stats['pending_reminders'] = cursor.fetchone()[0]
        
        # Count incomplete habits for today
        today = date.today().isoformat()
        cursor.execute("""
            SELECT COUNT(*) FROM habits h
            WHERE NOT EXISTS (
                SELECT 1 FROM habit_completions hc
                WHERE hc.habit_id = h.id AND hc.completion_date = ?
            )
        """, (today,))
        stats['incomplete_habits'] = cursor.fetchone()[0]
        
        # Count notes from yesterday
        yesterday = datetime.now().date()
        yesterday = yesterday.replace(day=yesterday.day - 1).isoformat()
        cursor.execute("SELECT COUNT(*) FROM notes WHERE timestamp LIKE ?", (f"{yesterday}%",))
        stats['notes_yesterday'] = cursor.fetchone()[0]
        
        conn.close()
        return stats
    
    except Exception:
        return {}


def should_auto_trigger() -> bool:
    """
    Check if briefing should auto-trigger (first launch of the day).
    
    Returns:
        True if should trigger, False otherwise
    """
    # Check if today's session log exists
    today = date.today().isoformat()
    session_log = f"./logs/{today}_session.json"
    
    # If no session log exists, this is the first launch today
    return not os.path.exists(session_log)


def create_sample_calendar(calendar_path: str = "./calendar.json"):
    """
    Create a sample calendar.json file.
    
    Args:
        calendar_path: Path for calendar file
    """
    sample_calendar = {
        "events": [
            {
                "date": date.today().isoformat(),
                "time": "09:00",
                "title": "Team Standup",
                "description": "Daily team sync meeting"
            },
            {
                "date": date.today().isoformat(),
                "time": "14:00",
                "title": "Code Review",
                "description": "Review PR #123"
            }
        ]
    }
    
    with open(calendar_path, 'w', encoding='utf-8') as f:
        json.dump(sample_calendar, f, indent=2)
