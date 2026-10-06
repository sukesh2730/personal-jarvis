"""
System monitoring daemon for ROME JARVIS.
Proactive alerts for CPU, RAM, battery, and log cleanup.
"""
import os
import time
import threading
import psutil
from pathlib import Path
from datetime import datetime, timedelta
from rich.console import Console

console = Console()

# Alert flags to prevent repeat nagging
_alerts_fired = {
    "cpu": False,
    "ram": False,
    "battery": False,
    "logs": False
}

_monitoring_active = False
_monitor_thread = None


def check_cpu():
    """
    Check CPU usage. Alert if > 85% for 3 consecutive checks.
    Returns True if alert should fire.
    """
    if _alerts_fired["cpu"]:
        return False
    
    # Check 3 times over 30 seconds
    high_count = 0
    for _ in range(3):
        cpu = psutil.cpu_percent(interval=1)
        if cpu > 85:
            high_count += 1
        time.sleep(9)  # Total 10s between checks
    
    if high_count >= 3:
        return True
    return False


def check_ram():
    """
    Check RAM usage. Alert if > 90%.
    Returns True if alert should fire.
    """
    if _alerts_fired["ram"]:
        return False
    
    memory = psutil.virtual_memory()
    if memory.percent > 90:
        return True
    return False


def check_battery():
    """
    Check battery level. Alert if < 20%.
    Returns True if alert should fire. Fails gracefully if no battery.
    """
    if _alerts_fired["battery"]:
        return False
    
    try:
        battery = psutil.sensors_battery()
        if battery is None:
            return False  # No battery detected (desktop)
        
        if battery.percent < 20 and not battery.power_plugged:
            return True
    except Exception:
        # Platform doesn't support battery monitoring
        pass
    
    return False


def check_old_logs():
    """
    Check for log files older than 7 days.
    Returns True if alert should fire.
    """
    if _alerts_fired["logs"]:
        return False
    
    try:
        logs_dir = Path("./logs")
        if not logs_dir.exists():
            return False
        
        cutoff_date = datetime.now() - timedelta(days=7)
        
        for log_file in logs_dir.glob("*.json"):
            file_date = datetime.fromtimestamp(log_file.stat().st_mtime)
            if file_date < cutoff_date:
                return True
    except Exception:
        pass
    
    return False


def fire_alert(alert_type, message):
    """
    Fire an alert using TTS and mark it as fired.
    
    Args:
        alert_type: One of "cpu", "ram", "battery", "logs"
        message: TTS message to speak
    """
    try:
        from tts import speak
        console.print(f"[yellow][System Alert] {message}[/yellow]")
        speak(message)
        _alerts_fired[alert_type] = True
    except Exception as e:
        console.print(f"[red]Alert TTS failed: {e}[/red]")


def monitor_system():
    """
    Background monitoring loop. Checks every 10 seconds.
    """
    global _monitoring_active
    _monitoring_active = True
    
    console.print("[dim]System monitor: Active[/dim]")
    
    while _monitoring_active:
        try:
            # Check CPU (this takes ~30s due to 3 consecutive checks)
            if check_cpu():
                fire_alert("cpu", "Sir, CPU usage is critical. You may want to close some processes.")
            
            # Check RAM
            if check_ram():
                fire_alert("ram", "Memory pressure detected, sir. Available RAM is critically low.")
            
            # Check battery
            if check_battery():
                fire_alert("battery", "Battery reserves are low, sir. I recommend connecting to power.")
            
            # Check logs
            if check_old_logs():
                fire_alert("logs", "Log cleanup is overdue, sir. Shall I handle it?")
            
            # Wait 10 seconds before next check cycle
            time.sleep(10)
            
        except Exception as e:
            console.print(f"[red]Monitor error: {e}[/red]")
            time.sleep(10)


def start_system_monitor():
    """Start system monitoring in background thread."""
    global _monitor_thread
    
    if _monitor_thread and _monitor_thread.is_alive():
        return
    
    _monitor_thread = threading.Thread(
        target=monitor_system,
        daemon=True
    )
    _monitor_thread.start()


def stop_system_monitor():
    """Stop system monitoring."""
    global _monitoring_active
    _monitoring_active = False


def is_monitoring_active():
    """Check if system monitoring is running."""
    return _monitoring_active


def reset_alerts():
    """Reset all alert flags (useful for testing)."""
    global _alerts_fired
    _alerts_fired = {
        "cpu": False,
        "ram": False,
        "battery": False,
        "logs": False
    }
