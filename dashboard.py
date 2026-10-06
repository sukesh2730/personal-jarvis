"""
Web Dashboard for JARVIS - Phase 5
Flask web dashboard for monitoring and statistics.
"""
from flask import Flask, render_template, jsonify
import threading
import os
import json
from datetime import datetime, date


app = Flask(__name__, template_folder='templates')


@app.route("/")
def index():
    """Serve dashboard HTML."""
    return render_template("dashboard.html")


@app.route("/api/stats")
def get_stats():
    """Return JSON stats for dashboard."""
    try:
        stats = {
            "timestamp": datetime.now().isoformat(),
            "active_sessions": get_session_count(),
            "indexed_chunks": get_chunk_count(),
            "memory_usage_mb": get_memory_usage(),
            "recent_commands": get_recent_commands(20),
            "habit_streaks": get_habit_streaks(),
            "focus_stats": get_focus_stats(),
            "memory_count": get_memory_count(),
            "notes_count": get_notes_count(),
            "pending_reminders": get_pending_reminders_count()
        }
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def get_session_count() -> int:
    """Get count of active sessions today."""
    today = date.today().isoformat()
    log_path = f"./logs/{today}_session.json"
    if os.path.exists(log_path):
        try:
            with open(log_path, 'r') as f:
                messages = json.load(f)
            return len(messages)
        except:
            return 0
    return 0


def get_chunk_count() -> int:
    """Get count of indexed code chunks."""
    try:
        from memory import CodeMemory
        memory = CodeMemory()
        # This is approximate - ChromaDB doesn't expose exact count easily
        return memory.collection.count()
    except:
        return 0


def get_memory_usage() -> float:
    """Get memory usage in MB."""
    try:
        import psutil
        process = psutil.Process()
        return round(process.memory_info().rss / 1024 / 1024, 2)
    except:
        return 0.0


def get_recent_commands(limit: int = 20) -> list:
    """Get recent commands from today's session."""
    today = date.today().isoformat()
    log_path = f"./logs/{today}_session.json"
    commands = []
    
    if os.path.exists(log_path):
        try:
            with open(log_path, 'r') as f:
                messages = json.load(f)
            
            for msg in messages[-limit:]:
                if msg.get('role') == 'user' and msg.get('content', '').startswith('/'):
                    commands.append({
                        'time': msg.get('time', ''),
                        'command': msg.get('content', '')[:50]
                    })
        except:
            pass
    
    return commands


def get_habit_streaks() -> list:
    """Get habit streaks from database."""
    try:
        import sqlite3
        conn = sqlite3.connect('./jarvis.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name, streak_count FROM habits ORDER BY streak_count DESC LIMIT 5")
        habits = [{'name': row[0], 'streak': row[1]} for row in cursor.fetchall()]
        conn.close()
        return habits
    except:
        return []


def get_focus_stats() -> dict:
    """Get focus session statistics."""
    try:
        import sqlite3
        from datetime import timedelta
        
        conn = sqlite3.connect('./jarvis.db')
        cursor = conn.cursor()
        
        # Today's focus sessions
        today = date.today().isoformat()
        cursor.execute("""
            SELECT COUNT(*), SUM(duration_minutes)
            FROM focus_sessions
            WHERE start_time LIKE ?
        """, (f"{today}%",))
        
        result = cursor.fetchone()
        conn.close()
        
        return {
            'sessions_today': result[0] or 0,
            'minutes_today': result[1] or 0
        }
    except:
        return {'sessions_today': 0, 'minutes_today': 0}


def get_memory_count() -> int:
    """Get count of stored memories."""
    try:
        import sqlite3
        conn = sqlite3.connect('./jarvis.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM memories")
        count = cursor.fetchone()[0]
        conn.close()
        return count
    except:
        return 0


def get_notes_count() -> int:
    """Get count of notes."""
    try:
        import sqlite3
        conn = sqlite3.connect('./jarvis.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM notes")
        count = cursor.fetchone()[0]
        conn.close()
        return count
    except:
        return 0


def get_pending_reminders_count() -> int:
    """Get count of pending reminders."""
    try:
        import sqlite3
        conn = sqlite3.connect('./jarvis.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM reminders WHERE completed = 0")
        count = cursor.fetchone()[0]
        conn.close()
        return count
    except:
        return 0


def start_dashboard(port: int = 5000, debug: bool = False):
    """
    Start Flask server in daemon thread.
    
    Args:
        port: Port to run on (default: 5000)
        debug: Debug mode (default: False)
    """
    app.run(host='0.0.0.0', port=port, debug=debug, use_reloader=False)


def create_dashboard_html():
    """Create dashboard HTML template."""
    os.makedirs('templates', exist_ok=True)
    
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JARVIS System Monitor</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            background: #0a0a0a;
            color: #00ffff;
            font-family: 'Courier New', monospace;
            padding: 20px;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            border-bottom: 2px solid #00ffff;
        }
        
        .header h1 {
            font-size: 2.5em;
            text-shadow: 0 0 10px #00ffff;
            margin-bottom: 10px;
        }
        
        .timestamp {
            color: #666;
            font-size: 0.9em;
        }
        
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-box {
            border: 2px solid #00ffff;
            padding: 20px;
            background: rgba(0, 255, 255, 0.05);
            transition: all 0.3s;
        }
        
        .stat-box:hover {
            background: rgba(0, 255, 255, 0.1);
            box-shadow: 0 0 20px rgba(0, 255, 255, 0.3);
        }
        
        .stat-box h2 {
            margin-bottom: 15px;
            font-size: 1.2em;
            border-bottom: 1px solid #00ffff;
            padding-bottom: 10px;
        }
        
        .stat-value {
            font-size: 2em;
            font-weight: bold;
            color: #00ff00;
        }
        
        .stat-label {
            color: #666;
            font-size: 0.9em;
        }
        
        .command-log {
            border: 2px solid #00ffff;
            padding: 20px;
            background: rgba(0, 255, 255, 0.05);
            max-height: 300px;
            overflow-y: auto;
        }
        
        .command-log h2 {
            margin-bottom: 15px;
            border-bottom: 1px solid #00ffff;
            padding-bottom: 10px;
        }
        
        .command-item {
            padding: 5px;
            margin: 5px 0;
            border-left: 3px solid #00ffff;
            padding-left: 10px;
        }
        
        .command-time {
            color: #666;
            font-size: 0.8em;
            margin-right: 10px;
        }
        
        .habit-list {
            list-style: none;
        }
        
        .habit-item {
            padding: 8px;
            margin: 5px 0;
            background: rgba(0, 255, 255, 0.1);
            display: flex;
            justify-content: space-between;
        }
        
        .streak {
            color: #00ff00;
            font-weight: bold;
        }
        
        .loading {
            text-align: center;
            padding: 40px;
            font-size: 1.5em;
            color: #00ffff;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        ::-webkit-scrollbar {
            width: 10px;
        }
        
        ::-webkit-scrollbar-track {
            background: #0a0a0a;
        }
        
        ::-webkit-scrollbar-thumb {
            background: #00ffff;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>JARVIS SYSTEM MONITOR</h1>
        <div class="timestamp" id="timestamp">Loading...</div>
    </div>
    
    <div id="stats-container">
        <div class="loading">Initializing systems...</div>
    </div>
    
    <script>
        async function updateStats() {
            try {
                const response = await fetch('/api/stats');
                const data = await response.json();
                
                if (data.error) {
                    document.getElementById('stats-container').innerHTML = 
                        '<div class="loading">Error loading data: ' + data.error + '</div>';
                    return;
                }
                
                // Update timestamp
                const timestamp = new Date(data.timestamp).toLocaleString();
                document.getElementById('timestamp').textContent = 'Last updated: ' + timestamp;
                
                // Build stats HTML
                let html = '<div class="grid">';
                
                html += `
                    <div class="stat-box">
                        <h2>Session Activity</h2>
                        <div class="stat-value">${data.active_sessions}</div>
                        <div class="stat-label">Messages Today</div>
                    </div>
                    
                    <div class="stat-box">
                        <h2>Code Index</h2>
                        <div class="stat-value">${data.indexed_chunks}</div>
                        <div class="stat-label">Indexed Chunks</div>
                    </div>
                    
                    <div class="stat-box">
                        <h2>Memory Usage</h2>
                        <div class="stat-value">${data.memory_usage_mb}</div>
                        <div class="stat-label">MB</div>
                    </div>
                    
                    <div class="stat-box">
                        <h2>Focus Sessions</h2>
                        <div class="stat-value">${data.focus_stats.sessions_today}</div>
                        <div class="stat-label">${data.focus_stats.minutes_today} minutes today</div>
                    </div>
                    
                    <div class="stat-box">
                        <h2>Stored Memories</h2>
                        <div class="stat-value">${data.memory_count}</div>
                        <div class="stat-label">Long-term memories</div>
                    </div>
                    
                    <div class="stat-box">
                        <h2>Notes</h2>
                        <div class="stat-value">${data.notes_count}</div>
                        <div class="stat-label">Captured notes</div>
                    </div>
                    
                    <div class="stat-box">
                        <h2>Pending Reminders</h2>
                        <div class="stat-value">${data.pending_reminders}</div>
                        <div class="stat-label">Active reminders</div>
                    </div>
                    
                    <div class="stat-box">
                        <h2>Top Habit</h2>
                        <div class="stat-value">${data.habit_streaks[0]?.streak || 0}</div>
                        <div class="stat-label">${data.habit_streaks[0]?.name || 'No habits'} streak</div>
                    </div>
                `;
                
                html += '</div>';
                
                // Recent commands
                if (data.recent_commands.length > 0) {
                    html += '<div class="command-log"><h2>Recent Commands</h2>';
                    data.recent_commands.forEach(cmd => {
                        html += `
                            <div class="command-item">
                                <span class="command-time">${cmd.time}</span>
                                <span>${cmd.command}</span>
                            </div>
                        `;
                    });
                    html += '</div>';
                }
                
                document.getElementById('stats-container').innerHTML = html;
                
            } catch (error) {
                document.getElementById('stats-container').innerHTML = 
                    '<div class="loading">Failed to fetch data. Is JARVIS running?</div>';
            }
        }
        
        // Update every 5 seconds
        updateStats();
        setInterval(updateStats, 5000);
    </script>
</body>
</html>
"""
    
    with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
