"""
Daily Summary Generation for JARVIS - Phase 2
Generates markdown summaries from session logs with auto-trigger at 11 PM.
"""
import os
import json
import threading
import time
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import Optional


def generate_summary(session_log_path: str, api_router) -> Optional[str]:
    """
    Generate markdown summary from session log.
    
    Args:
        session_log_path: Path to today's session JSON log
        api_router: API router instance for LLM call
        
    Returns:
        Markdown-formatted summary or None if no activity
    """
    # Check if log file exists
    if not os.path.exists(session_log_path):
        return None
    
    # Load session log
    try:
        with open(session_log_path, 'r', encoding='utf-8') as f:
            messages = json.load(f)
    except:
        return None
    
    if not messages or len(messages) == 0:
        return None
    
    # Build conversation text
    conversation_text = []
    for msg in messages:
        role = "User" if msg.get("role") == "user" else "JARVIS"
        content = msg.get("content", "")
        time_str = msg.get("time", "")
        conversation_text.append(f"[{time_str}] {role}: {content}")
    
    conversation = "\n".join(conversation_text)
    
    # Build prompt for LLM
    prompt = f"""Based on the following conversation log, create a concise daily summary in markdown format.

Conversation Log:
{conversation}

Generate a summary with these sections:
- **Tasks Completed**: List major tasks accomplished
- **Key Decisions**: Important decisions or choices made
- **Topics Discussed**: Main topics or themes
- **Tomorrow's Priorities**: Suggested priorities for tomorrow

Keep it concise and actionable. Format in markdown."""
    
    try:
        # Get completion from API router
        from api_router import get_completion
        summary = get_completion(prompt)
        return summary
    except Exception as e:
        return f"# Daily Summary - {date.today().isoformat()}\n\nError generating summary: {e}"


def save_summary(summary: str, output_dir: str = "./logs/summaries"):
    """
    Save summary to markdown file.
    
    Args:
        summary: Markdown summary text
        output_dir: Output directory for summaries
        
    Returns:
        Path to saved file
    """
    # Ensure directory exists
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Generate filename
    today = date.today().isoformat()
    filename = f"{today}_summary.md"
    filepath = os.path.join(output_dir, filename)
    
    # Add header if not present
    if not summary.startswith("#"):
        summary = f"# Daily Summary - {today}\n\n{summary}"
    
    # Save to file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(summary)
    
    return filepath


def auto_summary_daemon(tts=None):
    """
    Background daemon that checks time every 5 minutes.
    Triggers summary at 11 PM if user active in last hour.
    
    Args:
        tts: TTS module for spoken notification (optional)
    """
    last_summary_date = None
    
    while True:
        try:
            now = datetime.now()
            today = date.today()
            
            # Check if it's 11:00 PM and we haven't generated summary today
            if now.hour == 23 and now.minute < 5 and last_summary_date != today:
                # Check if user was active in last hour
                session_log_path = f"./logs/{today.isoformat()}_session.json"
                
                if os.path.exists(session_log_path):
                    # Check last message time
                    try:
                        with open(session_log_path, 'r', encoding='utf-8') as f:
                            messages = json.load(f)
                        
                        if messages:
                            # Get last message time
                            last_msg = messages[-1]
                            last_time_str = last_msg.get("time", "00:00")
                            last_hour = int(last_time_str.split(":")[0])
                            
                            # If active in last hour (after 10 PM)
                            if last_hour >= 22:
                                print("\n[DAILY SUMMARY] Generating daily summary, sir...")
                                
                                from api_router import get_completion
                                summary = generate_summary(session_log_path, get_completion)
                                
                                if summary:
                                    filepath = save_summary(summary)
                                    message = f"Daily summary saved to {filepath}, sir."
                                    print(f"[DAILY SUMMARY] {message}")
                                    
                                    if tts and hasattr(tts, 'speak_async'):
                                        try:
                                            tts.speak_async("Daily summary generated, sir.")
                                        except:
                                            pass
                                
                                last_summary_date = today
                    except:
                        pass
            
            time.sleep(300)  # Check every 5 minutes
        except Exception as e:
            # Log error but keep daemon running
            print(f"[SUMMARY DAEMON ERROR] {e}")
            time.sleep(300)


def start_summary_daemon(tts=None):
    """
    Start summary daemon as a background thread.
    
    Args:
        tts: TTS module (optional)
        
    Returns:
        Thread object
    """
    thread = threading.Thread(
        target=auto_summary_daemon,
        args=(tts,),
        daemon=True
    )
    thread.start()
    return thread
