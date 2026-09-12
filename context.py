"""Session memory for ROME JARVIS - save and load conversation history."""
import json
import os
from pathlib import Path
from datetime import datetime

LOGS_DIR = Path("./logs")

def save_message(role, content):
    """Append one message to today's log."""
    LOGS_DIR.mkdir(exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    filepath = LOGS_DIR / f"{today}.json"
    
    messages = []
    if filepath.exists():
        try:
            messages = json.loads(filepath.read_text())
        except:
            messages = []
    
    time_str = datetime.now().strftime("%H:%M")
    messages.append({"role": role, "content": content, "time": time_str})
    filepath.write_text(json.dumps(messages, indent=2))

def load_today():
    """Load today's conversation."""
    today = datetime.now().strftime("%Y-%m-%d")
    filepath = LOGS_DIR / f"{today}.json"
    
    if not filepath.exists():
        return []
    
    try:
        return json.loads(filepath.read_text())
    except:
        return []

def load_last_session():
    """Load the most recent past session (not today)."""
    if not LOGS_DIR.exists():
        return []
    
    today = datetime.now().strftime("%Y-%m-%d")
    log_files = sorted([f for f in LOGS_DIR.glob("*.json") if f.stem != today], reverse=True)
    
    if not log_files:
        return []
    
    try:
        return json.loads(log_files[0].read_text())
    except:
        return []

def build_history_prompt(messages, limit=10):
    """Format recent messages as context to prepend to AI prompt."""
    if not messages:
        return ""
    
    recent = messages[-limit:]
    lines = ["Recent conversation:"]
    for msg in recent:
        time_str = msg.get("time", "")
        role = "You" if msg["role"] == "user" else "JARVIS"
        lines.append(f"[{time_str}] {role}: {msg['content']}")
    
    return "\n".join(lines)

def get_session_summary():
    """One-line summary of current session."""
    messages = load_today()
    if not messages:
        return "No messages today yet."
    
    user_count = sum(1 for m in messages if m["role"] == "user")
    jarvis_count = sum(1 for m in messages if m["role"] == "jarvis")
    return f"Today: {user_count} exchanges logged."
