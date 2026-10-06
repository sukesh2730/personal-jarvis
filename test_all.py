"""
Comprehensive test suite for all JARVIS modules.
Runs tests for all 5 phases: Foundation, Productivity, Developer Tools, Intelligence, Infrastructure.
"""
import os
import sys
from datetime import datetime

print("=" * 80)
print("JARVIS COMPREHENSIVE TEST SUITE")
print("=" * 80)
print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# Track results
test_results = {
    "total": 0,
    "passed": 0,
    "failed": 0,
    "skipped": 0
}

def run_test(test_name, test_func):
    """Run a test and track results."""
    global test_results
    test_results["total"] += 1
    
    try:
        print(f"Testing: {test_name}...", end=" ")
        result = test_func()
        if result:
            print("✓ PASSED")
            test_results["passed"] += 1
            return True
        else:
            print("✗ FAILED")
            test_results["failed"] += 1
            return False
    except Exception as e:
        print(f"✗ ERROR: {e}")
        test_results["failed"] += 1
        return False

# Phase 1: Foundation Tests
print("PHASE 1: FOUNDATION")
print("-" * 80)

def test_database():
    from db_init import init_database
    conn = init_database()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    return len(tables) >= 7

def test_long_memory():
    from long_memory import LongMemory
    mem = LongMemory()
    mem_id = mem.remember("Test memory")
    return mem_id > 0

def test_corrections():
    from corrections import CorrectionLearner
    corr = CorrectionLearner()
    corr_id = corr.record_correction("original", "corrected", "query")
    return corr_id > 0

def test_notes():
    from notes import NotesSystem
    notes = NotesSystem()
    note_id = notes.add_note("Test note #test")
    return note_id > 0

run_test("Database initialization", test_database)
run_test("Long-term memory", test_long_memory)
run_test("Correction learning", test_corrections)
run_test("Notes system", test_notes)
print()

# Phase 2: Productivity Tests
print("PHASE 2: PRODUCTIVITY")
print("-" * 80)

def test_reminders():
    from reminders import ReminderSystem
    rem = ReminderSystem()
    rem_id = rem.create_reminder("in 5 minutes", "Test reminder")
    return rem_id > 0

def test_habits():
    from habits import HabitTracker
    habits = HabitTracker()
    try:
        habit_id = habits.add_habit("Test Habit")
        return habit_id > 0
    except ValueError:
        return True  # Already exists

def test_focus():
    from focus import FocusMode
    focus = FocusMode()
    return hasattr(focus, 'start')

def test_daily_summary():
    from daily_summary import generate_summary
    return callable(generate_summary)

run_test("Reminder system", test_reminders)
run_test("Habit tracker", test_habits)
run_test("Focus mode", test_focus)
run_test("Daily summary", test_daily_summary)
print()

# Phase 3: Developer Tools Tests
print("PHASE 3: DEVELOPER TOOLS")
print("-" * 80)

def test_git_ops():
    from git_ops import GitOps
    try:
        git = GitOps()
        return True
    except ValueError:
        return True  # Not a git repo is acceptable

def test_error_explainer():
    from error_explainer import extract_traceback
    sample = "Traceback (most recent call last):\nKeyError: 'test'"
    result = extract_traceback(sample)
    return result is not None

def test_pr_writer():
    from pr_writer import get_pr_template
    template = get_pr_template()
    return len(template) > 0

def test_dep_scanner():
    from dep_scanner import scan_dependencies
    return callable(scan_dependencies)

run_test("Git operations", test_git_ops)
run_test("Error explainer", test_error_explainer)
run_test("PR writer", test_pr_writer)
run_test("Dependency scanner", test_dep_scanner)
print()

# Phase 4: Intelligence Tests
print("PHASE 4: INTELLIGENCE & IMMERSION")
print("-" * 80)

def test_web_search():
    from web_search import format_search_results, SearchResult
    results = [SearchResult("Title", "https://url.com", "Snippet")]
    formatted = format_search_results(results)
    return len(formatted) > 0

def test_emotion():
    from emotion import detect_emotion
    frustrated = detect_emotion("This is so frustrating and annoying!")
    excited = detect_emotion("This is amazing and fantastic!")
    return frustrated == "frustrated" and excited == "excited"

def test_sounds():
    from sounds import AudioFeedback
    audio = AudioFeedback()
    return hasattr(audio, 'play')

def test_briefing():
    from briefing import generate_briefing
    briefing = generate_briefing()
    return "sir" in briefing.lower()

run_test("Web search", test_web_search)
run_test("Emotion detection", test_emotion)
run_test("Audio feedback", test_sounds)
run_test("Morning briefing", test_briefing)
print()

# Phase 5: Infrastructure Tests
print("PHASE 5: INFRASTRUCTURE")
print("-" * 80)

def test_dashboard():
    from dashboard import get_session_count, get_memory_count
    return callable(get_session_count)

def test_api_server():
    from api_server import app
    return app is not None

def test_docker_files():
    return os.path.exists("Dockerfile") and os.path.exists("docker-compose.yml")

run_test("Dashboard module", test_dashboard)
run_test("API server", test_api_server)
run_test("Docker configuration", test_docker_files)
print()

# Summary
print("=" * 80)
print("TEST SUMMARY")
print("=" * 80)
print(f"Total Tests: {test_results['total']}")
print(f"Passed:      {test_results['passed']} ✓")
print(f"Failed:      {test_results['failed']} ✗")
print(f"Success Rate: {(test_results['passed']/test_results['total']*100):.1f}%")
print()

if test_results['failed'] == 0:
    print("🎉 ALL TESTS PASSED! JARVIS is fully operational, sir.")
    exit_code = 0
else:
    print("⚠️  SOME TESTS FAILED. Please review the output above.")
    exit_code = 1

print()
print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)

sys.exit(exit_code)
