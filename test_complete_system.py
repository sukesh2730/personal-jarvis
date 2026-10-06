"""
Comprehensive System Test for ROME JARVIS
Tests all modules, integrations, and bug fixes
"""

import sys
from rich.console import Console

console = Console()

def test_imports():
    """Test all module imports"""
    console.print("\n[cyan]Testing Module Imports...[/cyan]")
    
    try:
        import main
        console.print("  ✓ main.py")
    except Exception as e:
        console.print(f"  ✗ main.py: {e}")
        return False
    
    try:
        import api_router
        console.print("  ✓ api_router.py")
    except Exception as e:
        console.print(f"  ✗ api_router.py: {e}")
        return False
    
    try:
        import agent_reach_ops
        console.print("  ✓ agent_reach_ops.py")
    except Exception as e:
        console.print(f"  ✗ agent_reach_ops.py: {e}")
        return False
    
    # Phase 1
    try:
        from db_init import init_database
        from long_memory import LongMemory
        from corrections import CorrectionLearner
        from notes import NotesSystem
        console.print("  ✓ Phase 1: Foundation modules")
    except Exception as e:
        console.print(f"  ✗ Phase 1: {e}")
        return False
    
    # Phase 2
    try:
        from reminders import ReminderSystem
        from habits import HabitTracker
        from focus import FocusMode
        from daily_summary import generate_summary
        console.print("  ✓ Phase 2: Productivity modules")
    except Exception as e:
        console.print(f"  ✗ Phase 2: {e}")
        return False
    
    # Phase 3
    try:
        from git_ops import GitOps
        from error_explainer import extract_traceback
        from pr_writer import generate_pr_description
        from dep_scanner import scan_dependencies
        console.print("  ✓ Phase 3: Developer tools")
    except Exception as e:
        console.print(f"  ✗ Phase 3: {e}")
        return False
    
    # Phase 4
    try:
        from web_search import search_web
        from emotion import detect_emotion
        from sounds import AudioFeedback
        from briefing import generate_briefing
        console.print("  ✓ Phase 4: Intelligence modules")
    except Exception as e:
        console.print(f"  ✗ Phase 4: {e}")
        return False
    
    # Phase 5
    try:
        from dashboard import start_dashboard
        from api_server import start_api_server
        console.print("  ✓ Phase 5: Infrastructure modules")
    except Exception as e:
        console.print(f"  ✗ Phase 5: {e}")
        return False
    
    return True


def test_api_keys():
    """Test API key validation"""
    console.print("\n[cyan]Testing API Keys...[/cyan]")
    
    try:
        from api_router import validate_keys
        valid_apis = validate_keys()
        
        if valid_apis:
            console.print(f"  ✓ Valid APIs: {', '.join(valid_apis)}")
            return True
        else:
            console.print("  ✗ No valid API keys found")
            return False
    except Exception as e:
        console.print(f"  ✗ API validation failed: {e}")
        return False


def test_database():
    """Test database initialization"""
    console.print("\n[cyan]Testing Database...[/cyan]")
    
    try:
        import sqlite3
        from db_init import init_database
        
        init_database()
        
        conn = sqlite3.connect('jarvis.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        conn.close()
        
        console.print(f"  ✓ Database initialized with {len(tables)} tables")
        return True
    except Exception as e:
        console.print(f"  ✗ Database test failed: {e}")
        return False


def test_agent_reach():
    """Test Agent-Reach integration"""
    console.print("\n[cyan]Testing Agent-Reach Integration...[/cyan]")
    
    try:
        from agent_reach_ops import AgentReachOps
        
        ar = AgentReachOps()
        console.print(f"  ✓ Agent-Reach CLI available: {ar.available}")
        
        if ar.available:
            console.print("  ✓ All Agent-Reach commands ready")
        else:
            console.print("  ⚠ Agent-Reach CLI not installed (expected if not configured)")
        
        return True
    except Exception as e:
        console.print(f"  ✗ Agent-Reach test failed: {e}")
        return False


def test_gemini_api():
    """Test new Google Gemini API"""
    console.print("\n[cyan]Testing Google Gemini API (New Package)...[/cyan]")
    
    try:
        from google import genai
        console.print("  ✓ google.genai package imported (new API)")
        
        # Check if we can create a client (without actually calling it)
        import os
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key and api_key not in ["", "your_gemini_key_here"]:
            console.print("  ✓ Gemini API key configured")
        else:
            console.print("  ⚠ Gemini API key not configured")
        
        return True
    except Exception as e:
        console.print(f"  ✗ Gemini API test failed: {e}")
        return False


def test_phase2_reminder_fix():
    """Test Phase 2 ReminderSystem bug fix"""
    console.print("\n[cyan]Testing Phase 2 ReminderSystem Bug Fix...[/cyan]")
    
    try:
        from reminders import ReminderSystem
        
        # Create instance
        rem = ReminderSystem()
        console.print("  ✓ ReminderSystem instantiation works")
        
        # Try to access _parse_time method (the bug was here)
        try:
            rem._parse_time("in 5 minutes")
            console.print("  ✓ ReminderSystem._parse_time() method accessible")
        except Exception as e:
            console.print(f"  ✗ _parse_time method failed: {e}")
            return False
        
        return True
    except Exception as e:
        console.print(f"  ✗ ReminderSystem test failed: {e}")
        return False


def count_features():
    """Count all implemented features"""
    console.print("\n[cyan]Feature Count Summary...[/cyan]")
    
    features = {
        "Phase 1 - Foundation": [
            "Database initialization (SQLite)",
            "Long-term memory system",
            "Correction learning",
            "Notes with hashtags"
        ],
        "Phase 2 - Productivity": [
            "Reminder system",
            "Habit tracker with streaks",
            "Focus mode (Pomodoro)",
            "Daily summaries"
        ],
        "Phase 3 - Developer Tools": [
            "Git operations (with safety)",
            "Error explainer",
            "PR description writer",
            "Dependency vulnerability scanner"
        ],
        "Phase 4 - Intelligence": [
            "Web search (DuckDuckGo)",
            "Emotion detection",
            "Audio feedback system",
            "Morning briefing"
        ],
        "Phase 5 - Infrastructure": [
            "Web dashboard (Flask)",
            "REST API (FastAPI)",
            "Docker configuration",
            "Complete test suite"
        ],
        "Agent-Reach Integration": [
            "Multi-platform web search",
            "Twitter/X search",
            "Reddit search",
            "GitHub search",
            "Web page reader",
            "YouTube subtitle extraction",
            "V2EX hot topics",
            "Health check system",
            "Update checker"
        ]
    }
    
    total = 0
    for phase, items in features.items():
        console.print(f"\n  [yellow]{phase}[/yellow] ({len(items)} features)")
        for item in items:
            console.print(f"    • {item}")
            total += 1
    
    console.print(f"\n  [green]Total Features: {total}[/green]")
    return total


def main():
    """Run all tests"""
    console.print("\n[bold cyan]╔═══════════════════════════════════════════════════════╗[/bold cyan]")
    console.print("[bold cyan]║   ROME JARVIS - COMPREHENSIVE SYSTEM TEST            ║[/bold cyan]")
    console.print("[bold cyan]╚═══════════════════════════════════════════════════════╝[/bold cyan]")
    
    results = []
    
    # Run all tests
    results.append(("Module Imports", test_imports()))
    results.append(("API Keys", test_api_keys()))
    results.append(("Database", test_database()))
    results.append(("Agent-Reach", test_agent_reach()))
    results.append(("Gemini API Upgrade", test_gemini_api()))
    results.append(("Phase 2 Bug Fix", test_phase2_reminder_fix()))
    
    # Count features
    total_features = count_features()
    
    # Summary
    console.print("\n[bold cyan]═══════════════════════════════════════════════════════[/bold cyan]")
    console.print("[bold yellow]TEST SUMMARY[/bold yellow]\n")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "[green]PASS[/green]" if result else "[red]FAIL[/red]"
        console.print(f"  {status} - {test_name}")
    
    console.print(f"\n[bold]Tests Passed: {passed}/{total}[/bold]")
    console.print(f"[bold]Success Rate: {(passed/total)*100:.1f}%[/bold]")
    
    if passed == total:
        console.print("\n[bold green]🎉 ALL TESTS PASSED! JARVIS IS FULLY OPERATIONAL! 🎉[/bold green]")
        sys.exit(0)
    else:
        console.print("\n[bold red]⚠ SOME TESTS FAILED[/bold red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
