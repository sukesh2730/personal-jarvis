"""
REST API Server for JARVIS - Phase 5
FastAPI REST API for external integrations.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
from datetime import datetime


app = FastAPI(
    title="JARVIS API",
    description="REST API for ROME JARVIS Personal AI Assistant",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models
class Memory(BaseModel):
    content: str
    category: str = "general"


class Note(BaseModel):
    content: str


class Reminder(BaseModel):
    time: str
    message: str


class Habit(BaseModel):
    name: str


class QueryRequest(BaseModel):
    query: str
    top_k: int = 3


# Database helper
def get_db():
    conn = sqlite3.connect('./jarvis.db')
    conn.row_factory = sqlite3.Row
    return conn


@app.get("/")
def root():
    """API root endpoint."""
    return {
        "message": "JARVIS API is operational, sir.",
        "version": "1.0.0",
        "endpoints": {
            "memories": "/api/memories",
            "notes": "/api/notes",
            "reminders": "/api/reminders",
            "habits": "/api/habits",
            "search": "/api/search"
        }
    }


@app.get("/api/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


# Memory endpoints
@app.get("/api/memories")
def get_memories(limit: int = 10):
    """Get stored memories."""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, timestamp, category, content, source
            FROM memories
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))
        
        memories = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return {"memories": memories}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/memories")
def create_memory(memory: Memory):
    """Create a new memory."""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO memories (timestamp, category, content, source)
            VALUES (?, ?, ?, ?)
        """, (datetime.now().isoformat(), memory.category, memory.content, "api"))
        
        memory_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {"id": memory_id, "message": "Memory stored successfully, sir."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Note endpoints
@app.get("/api/notes")
def get_notes(limit: int = 10):
    """Get notes."""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, timestamp, content, tags
            FROM notes
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))
        
        notes = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return {"notes": notes}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/notes")
def create_note(note: Note):
    """Create a new note."""
    try:
        # Extract tags
        import re
        tags = ",".join(re.findall(r'#(\w+)', note.content))
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO notes (timestamp, content, tags)
            VALUES (?, ?, ?)
        """, (datetime.now().isoformat(), note.content, tags))
        
        note_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {"id": note_id, "message": "Note saved, sir."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Reminder endpoints
@app.get("/api/reminders")
def get_reminders(completed: Optional[bool] = None):
    """Get reminders."""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        if completed is None:
            cursor.execute("""
                SELECT id, timestamp_created, reminder_time, message, completed
                FROM reminders
                ORDER BY reminder_time DESC
            """)
        else:
            cursor.execute("""
                SELECT id, timestamp_created, reminder_time, message, completed
                FROM reminders
                WHERE completed = ?
                ORDER BY reminder_time DESC
            """, (1 if completed else 0,))
        
        reminders = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return {"reminders": reminders}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Habit endpoints
@app.get("/api/habits")
def get_habits():
    """Get habits with streaks."""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, name, created_date, streak_count
            FROM habits
            ORDER BY streak_count DESC
        """)
        
        habits = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return {"habits": habits}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/habits")
def create_habit(habit: Habit):
    """Create a new habit."""
    try:
        from datetime import date
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO habits (name, created_date, streak_count)
            VALUES (?, ?, 0)
        """, (habit.name, date.today().isoformat()))
        
        habit_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {"id": habit_id, "message": f"Habit '{habit.name}' created, sir."}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Habit already exists")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Statistics endpoint
@app.get("/api/stats")
def get_stats():
    """Get overall statistics."""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Count memories
        cursor.execute("SELECT COUNT(*) FROM memories")
        memory_count = cursor.fetchone()[0]
        
        # Count notes
        cursor.execute("SELECT COUNT(*) FROM notes")
        notes_count = cursor.fetchone()[0]
        
        # Count pending reminders
        cursor.execute("SELECT COUNT(*) FROM reminders WHERE completed = 0")
        pending_reminders = cursor.fetchone()[0]
        
        # Count habits
        cursor.execute("SELECT COUNT(*) FROM habits")
        habit_count = cursor.fetchone()[0]
        
        # Focus sessions today
        from datetime import date
        today = date.today().isoformat()
        cursor.execute("""
            SELECT COUNT(*), SUM(duration_minutes)
            FROM focus_sessions
            WHERE start_time LIKE ?
        """, (f"{today}%",))
        focus_result = cursor.fetchone()
        
        conn.close()
        
        return {
            "memory_count": memory_count,
            "notes_count": notes_count,
            "pending_reminders": pending_reminders,
            "habit_count": habit_count,
            "focus_sessions_today": focus_result[0] or 0,
            "focus_minutes_today": focus_result[1] or 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def start_api_server(port: int = 8000):
    """
    Start FastAPI server.
    
    Args:
        port: Port to run on (default: 8000)
    """
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
