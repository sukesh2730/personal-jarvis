"""
ROME JARVIS - Personal AI Coding Assistant
Main entry point with terminal chat interface
"""
import os
import sys
import json
from dotenv import load_dotenv
from rich.console import Console
from api_router import get_completion, validate_keys, get_stats
from indexer import scan_codebase
from memory import CodeMemory
from pathlib import Path
from tools import read_file, write_file, run_file, list_files, explain_file
from context import save_message, load_today, load_last_session, build_history_prompt, get_session_summary
from config import get_project_context, get_project_path, list_projects, build_project_prompt, PROJECTS
from voice import listen, is_voice_available, load_whisper
from tts import speak_async, enable_tts, disable_tts, is_tts_available, is_enabled as tts_is_enabled

# Import Phase 1 foundation modules
try:
    from db_init import init_database
    from long_memory import LongMemory
    from corrections import CorrectionLearner
    from notes import NotesSystem
    PHASE1_AVAILABLE = True
except ImportError:
    PHASE1_AVAILABLE = False

# Import Phase 2 productivity modules
try:
    from reminders import ReminderSystem, start_reminder_daemon
    from habits import HabitTracker, start_habit_notifier
    from focus import FocusMode
    from daily_summary import generate_summary, save_summary, start_summary_daemon
    PHASE2_AVAILABLE = True
except ImportError:
    PHASE2_AVAILABLE = False

# Import Phase 3 developer tools
try:
    from git_ops import GitOps
    from error_explainer import extract_traceback, explain_error
    from pr_writer import generate_pr_description, save_pr_description
    from dep_scanner import scan_dependencies, format_scan_results
    PHASE3_AVAILABLE = True
except ImportError:
    PHASE3_AVAILABLE = False

# Import Phase 4 intelligence and immersion modules
try:
    from web_search import search_web, format_search_results, is_online
    from emotion import detect_emotion, modify_system_prompt
    from sounds import AudioFeedback, create_sound_placeholders
    from briefing import generate_briefing, should_auto_trigger
    PHASE4_AVAILABLE = True
except ImportError:
    PHASE4_AVAILABLE = False

# Import Agent-Reach integration module
try:
    from agent_reach_ops import AgentReachOps, format_search_results_ar
    AGENT_REACH_AVAILABLE = True
except ImportError:
    AGENT_REACH_AVAILABLE = False

# Import APILayer integration module
try:
    from apilayer_ops import APILayerOps, format_exchange_rates, format_ip_location, format_weather
    APILAYER_AVAILABLE = True
except ImportError:
    APILAYER_AVAILABLE = False

# Initialize Rich console for formatted output
console = Console()


def format_context(results):
    """Format search results for LLM context."""
    lines = ["Here is relevant code from the project:\n"]
    for result in results:
        lines.append(f"--- File: {result.file_path} (lines {result.start_line}-{result.end_line}) ---")
        lines.append(result.content)
        lines.append("")
    return "\n".join(lines)


def index_project():
    """Index the codebase."""
    project_path = os.getenv("PROJECT_PATH", "./projects")
    console.print("[cyan]Indexing: Scanning files...[/cyan]")
    chunks = scan_codebase(project_path)
    memory = CodeMemory()
    stored = memory.add_chunks(chunks)
    console.print(f"[green]Done: {stored} chunks indexed.[/green]")


def show_startup_banner():
    """Display the startup banner with Rich formatting."""
    console.print("\n[bold cyan]═══════════════════════════════════════════════════[/bold cyan]")
    console.print("[bold cyan]   ROME JARVIS - Personal AI Coding Assistant[/bold cyan]")
    console.print("[bold cyan]═══════════════════════════════════════════════════[/bold cyan]\n")
    console.print("[dim]Type /help for available commands[/dim]\n")


def show_help():
    """Display available commands."""
    console.print("\n[bold yellow]Available Commands:[/bold yellow]")
    console.print("  [cyan]/help[/cyan]           - Show available commands")
    console.print("  [cyan]/index[/cyan]          - Index the codebase for semantic search")
    console.print("  [cyan]/voice[/cyan]          - Toggle voice input mode on/off")
    console.print("  [cyan]/listen[/cyan]         - Single voice input (5 seconds)")
    console.print("  [cyan]/listen [secs][/cyan]  - Single voice input (custom seconds)")
    console.print("  [cyan]/speak[/cyan]          - Toggle text-to-speech mode on/off")
    console.print("  [cyan]/read [file][/cyan]    - Read and display a file")
    console.print("  [cyan]/run [file][/cyan]     - Execute a Python file")
    console.print("  [cyan]/ls [dir][/cyan]       - List files in directory")
    console.print("  [cyan]/explain [file][/cyan] - AI explains a file")
    console.print("  [cyan]/history[/cyan]        - Show today's conversation")
    console.print("  [cyan]/session[/cyan]        - Show session summary")
    console.print("  [cyan]/stats[/cyan]          - Show token usage statistics")
    console.print("  [cyan]/projects[/cyan]       - List all your projects")
    console.print("  [cyan]/project[/cyan]        - Show active project")
    console.print("  [cyan]/sales[/cyan]          - Switch to sales platform context")
    console.print("  [cyan]/leads[/cyan]          - Switch to lead gen context")
    console.print("  [cyan]/jarvis[/cyan]         - Switch to JARVIS context")
    console.print("\n[bold yellow]Developer Tools:[/bold yellow]")
    console.print("  [cyan]/git status[/cyan]     - Show git repository status")
    console.print("  [cyan]/git commit [msg][/cyan] - Stage all and commit")
    console.print("  [cyan]/git push[/cyan]       - Push current branch")
    console.print("  [cyan]/git branch[/cyan]     - List branches")
    console.print("  [cyan]/git log[/cyan]        - Show recent commits")
    console.print("  [cyan]/explain-error[/cyan]  - Analyze Python error from clipboard")
    console.print("  [cyan]/explain-error [file][/cyan] - Analyze error from file")
    console.print("  [cyan]/write-pr[/cyan]       - Generate PR description")
    console.print("  [cyan]/write-pr [branch][/cyan] - Generate PR vs branch")
    console.print("  [cyan]/check-deps[/cyan]     - Scan dependencies for vulnerabilities")
    console.print("\n[bold yellow]Intelligence:[/bold yellow]")
    console.print("  [cyan]/search [query][/cyan] - Search the web with DuckDuckGo")
    console.print("  [cyan]/briefing[/cyan]       - Generate morning briefing")
    console.print("\n[bold yellow]Audio:[/bold yellow]")
    console.print("  [cyan]/sounds[/cyan]         - Toggle audio feedback on/off")
    console.print("  [cyan]/volume [0-100][/cyan] - Set audio volume")
    console.print("  [cyan]/audio-status[/cyan]   - Show audio system status")
    console.print("\n[bold yellow]Infrastructure:[/bold yellow]")
    console.print("  [cyan]/dashboard[/cyan]      - Start web dashboard (port 5000)")
    console.print("  [cyan]/api-server[/cyan]     - Start REST API server (port 8000)")
    console.print("\n[bold yellow]Memory & Learning:[/bold yellow]")
    console.print("  [cyan]/remember [fact][/cyan] - Store a fact or preference")
    console.print("  [cyan]/recall [query][/cyan]  - Search stored memories")
    console.print("  [cyan]/forget [id][/cyan]     - Delete a memory by ID")
    console.print("  [cyan]/corrections[/cyan]     - View recent corrections")
    console.print("\n[bold yellow]Notes:[/bold yellow]")
    console.print("  [cyan]/note [text][/cyan]     - Capture a quick note (use #tags)")
    console.print("  [cyan]/notes[/cyan]           - Show recent notes")
    console.print("  [cyan]/notes [query][/cyan]   - Search notes")
    console.print("  [cyan]/note-export [date][/cyan] - Export notes to markdown")
    console.print("\n[bold yellow]Productivity:[/bold yellow]")
    console.print("  [cyan]/remind [time] [msg][/cyan] - Set a reminder")
    console.print("  [cyan]/reminders[/cyan]       - List pending reminders")
    console.print("  [cyan]/done [id][/cyan]       - Mark reminder complete")
    console.print("  [cyan]/habit-add [name][/cyan] - Create new habit")
    console.print("  [cyan]/habit [name][/cyan]    - Mark habit complete today")
    console.print("  [cyan]/habits[/cyan]          - Show all habits with streaks")
    console.print("  [cyan]/focus[/cyan]           - Start 25-min focus session")
    console.print("  [cyan]/focus [mins][/cyan]    - Start custom focus session")
    console.print("  [cyan]/focus-stats[/cyan]     - Show focus statistics")
    console.print("  [cyan]/summary[/cyan]         - Generate daily summary")
    console.print("\n[bold yellow]Agent-Reach (Multi-Platform Internet):[/bold yellow]")
    console.print("  [cyan]/ar-doctor[/cyan]       - Check Agent-Reach health status")
    console.print("  [cyan]/ar-web [query][/cyan]  - Web search via Exa")
    console.print("  [cyan]/ar-twitter [query][/cyan] - Search Twitter/X")
    console.print("  [cyan]/ar-reddit [query][/cyan] - Search Reddit")
    console.print("  [cyan]/ar-github [query][/cyan] - Search GitHub repos")
    console.print("  [cyan]/ar-read [url][/cyan]   - Read web page (clean text)")
    console.print("  [cyan]/ar-youtube [url][/cyan] - Get YouTube subtitles")
    console.print("  [cyan]/ar-v2ex[/cyan]         - V2EX hot topics")
    console.print("  [cyan]/ar-update[/cyan]       - Check for updates")
    console.print("\n[bold yellow]APILayer (30+ Production APIs):[/bold yellow]")
    console.print("  [cyan]/api-currency [base] [symbols][/cyan] - Exchange rates")
    console.print("  [cyan]/api-convert [from] [to] [amt][/cyan] - Convert currency")
    console.print("  [cyan]/api-geoip [ip][/cyan]  - Geolocate IP address")
    console.print("  [cyan]/api-myip[/cyan]        - Get your IP location")
    console.print("  [cyan]/api-email [email][/cyan] - Validate email")
    console.print("  [cyan]/api-phone [number][/cyan] - Validate phone")
    console.print("  [cyan]/api-weather [loc][/cyan] - Current weather")
    console.print("  [cyan]/api-geocode [addr][/cyan] - Address to coords")
    console.print("  [cyan]/api-flight [code][/cyan] - Flight info")
    console.print("  [cyan]/api-lang [text][/cyan] - Detect language")
    console.print("\n[bold yellow]System:[/bold yellow]")
    console.print("  [cyan]/clear[/cyan]          - Clear the screen")
    console.print("  [cyan]/quit[/cyan]           - Exit the assistant\n")
    console.print("[dim]Aliases: /v=/voice, /s=/speak, /l=/listen, /h=/help, /q=/quit, /r=/read, /e=/explain[/dim]\n")


def clear_screen():
    """Clear the terminal screen."""
    console.clear()


def chat_loop():
    """
    Main chat loop: input → api_router → display response.
    Handles user input, commands, and AI responses.
    """
    active_project = None
    voice_mode = False
    voice_available = is_voice_available()
    
    # Initialize database
    if PHASE1_AVAILABLE:
        try:
            init_database()
        except Exception as e:
            console.print(f"[yellow]Database initialization skipped: {e}[/yellow]")
    
    # Initialize Phase 1 modules
    long_mem = None
    corrections = None
    notes = None
    
    if PHASE1_AVAILABLE:
        try:
            long_mem = LongMemory()
            corrections = CorrectionLearner()
            notes = NotesSystem()
        except Exception as e:
            console.print(f"[yellow]Phase 1 modules unavailable: {e}[/yellow]")
    
    # Initialize Phase 2 modules
    reminders = None
    habits = None
    focus = None
    
    if PHASE2_AVAILABLE:
        try:
            reminders = ReminderSystem()
            habits = HabitTracker()
            focus = FocusMode()
            
            # Start background daemons
            import tts as tts_module
            start_reminder_daemon(reminders, tts=tts_module)
            start_habit_notifier(habits, tts=tts_module)
            start_summary_daemon(tts=tts_module)
            
            console.print("[dim]Phase 2: Productivity daemons started[/dim]")
        except Exception as e:
            console.print(f"[yellow]Phase 2 modules unavailable: {e}[/yellow]")
    
    # Initialize Phase 4 modules
    audio = None
    briefing_shown = False
    
    if PHASE4_AVAILABLE:
        try:
            # Initialize audio feedback
            audio = AudioFeedback()
            if audio.enabled:
                # Create sound placeholder files
                create_sound_placeholders()
                # Play startup sound
                audio.play("startup")
            
            # Show morning briefing if first launch of the day
            if should_auto_trigger():
                console.print("\n[cyan]" + "=" * 60 + "[/cyan]")
                briefing_text = generate_briefing()
                console.print(f"[cyan]{briefing_text}[/cyan]")
                console.print("[cyan]" + "=" * 60 + "[/cyan]\n")
                briefing_shown = True
                
                # Speak briefing if TTS enabled
                if tts_is_enabled():
                    speak_async(briefing_text)
            
            console.print("[dim]Phase 4: Intelligence modules initialized[/dim]")
        except Exception as e:
            console.print(f"[yellow]Phase 4 modules unavailable: {e}[/yellow]")
    
    # Initialize Agent-Reach module
    agent_reach = None
    if AGENT_REACH_AVAILABLE:
        try:
            agent_reach = AgentReachOps()
            console.print("[dim]Agent-Reach: Content tools ready[/dim]")
        except Exception as e:
            console.print(f"[yellow]Agent-Reach unavailable: {e}[/yellow]")
    
    # Initialize APILayer module
    apilayer = None
    if APILAYER_AVAILABLE:
        try:
            apilayer = APILayerOps()
            if apilayer.available:
                console.print("[dim]APILayer: 30+ APIs ready[/dim]")
            else:
                console.print("[dim]APILayer: Not configured (get key at https://app.apilayer.com/)[/dim]")
        except Exception as e:
            console.print(f"[yellow]APILayer unavailable: {e}[/yellow]")
    
    # Track last response for corrections
    last_query = ""
    last_response = ""
    
    while True:
        try:
            # Get user input (text or voice)
            if voice_mode:
                console.print("[cyan]You (press Enter to speak):[/cyan] ", end="")
                input()  # wait for Enter keypress
                user_input = listen(seconds=5)
                if user_input is None:
                    console.print("[yellow]Nothing heard. Try again.[/yellow]")
                    continue
                console.print(f"[cyan]You said:[/cyan] {user_input}")
            else:
                user_input = console.input("[cyan]You:[/cyan] ").strip()
            
            # Skip empty input
            if not user_input:
                continue
            
            # Check focus mode command blocking
            if focus and focus.active and not focus.is_command_allowed(user_input):
                remaining = focus.get_remaining_time()
                console.print(f"[yellow]Focus mode active, sir. {remaining}[/yellow]")
                console.print("[dim]Only /help, /quit, and /focus commands available during focus.[/dim]")
                continue
            
            # Resolve command aliases FIRST
            ALIASES = {
                "/v": "/voice",
                "/s": "/speak", 
                "/l": "/listen",
                "/h": "/help",
                "/q": "/quit",
                "/r": "/read",
                "/e": "/explain"
            }
            
            # Check if input is an alias or starts with an alias
            if user_input in ALIASES:
                user_input = ALIASES[user_input]
            elif " " in user_input:
                # Handle aliases with arguments like "/r main.py"
                cmd_part = user_input.split()[0]
                if cmd_part in ALIASES:
                    user_input = user_input.replace(cmd_part, ALIASES[cmd_part], 1)
            
            # Handle quit commands
            if user_input in ["/quit", "/exit"]:
                console.print("[yellow]Goodbye![/yellow]")
                break
            
            # Process other commands
            if user_input.startswith("/"):
                if user_input == "/help":
                    show_help()
                elif user_input == "/clear":
                    clear_screen()
                elif user_input == "/index":
                    index_project()
                elif user_input == "/stats":
                    stats = get_stats()
                    console.print(f"[cyan]{stats}[/cyan]")
                elif user_input == "/speak":
                    if not is_tts_available():
                        console.print("[red][TTS] Text-to-speech not available.[/red]")
                    else:
                        if tts_is_enabled():
                            disable_tts()
                            console.print("[yellow][TTS] Speech mode OFF.[/yellow]")
                        else:
                            if enable_tts():
                                console.print("[green][TTS] Speech mode ON. JARVIS will speak responses.[/green]")
                            else:
                                console.print("[red][TTS] Could not enable speech mode.[/red]")
                elif user_input == "/voice":
                    if not voice_available:
                        console.print("[red][Voice] Microphone not available. Voice disabled.[/red]")
                    else:
                        voice_mode = not voice_mode
                        if voice_mode:
                            load_whisper()  # preload model
                            console.print("[green][Voice] Voice mode ON. Press Enter to speak.[/green]")
                        else:
                            console.print("[yellow][Voice] Voice mode OFF.[/yellow]")
                elif user_input.startswith("/listen"):
                    if not voice_available:
                        console.print("[red][Voice] Microphone not available.[/red]")
                    else:
                        # Parse seconds from command
                        parts = user_input.split()
                        seconds = 5
                        if len(parts) > 1:
                            try:
                                seconds = int(parts[1])
                            except:
                                seconds = 5
                        
                        transcribed = listen(seconds=seconds)
                        if transcribed:
                            user_input = transcribed
                            console.print(f"[cyan]You said:[/cyan] {user_input}")
                            # Process as normal message below
                        else:
                            console.print("[yellow][Voice] Nothing heard. Try again.[/yellow]")
                            continue
                elif user_input.startswith("/read "):
                    filepath = user_input[6:].strip()
                    read_file(filepath)
                elif user_input.startswith("/run "):
                    filepath = user_input[5:].strip()
                    run_file(filepath)
                elif user_input.startswith("/ls"):
                    dirpath = user_input[3:].strip() or "."
                    list_files(dirpath)
                elif user_input.startswith("/explain "):
                    filepath = user_input[9:].strip()
                    explain_file(filepath, get_completion)
                elif user_input == "/history":
                    messages = load_today()
                    if not messages:
                        console.print("[dim]No messages today yet.[/dim]")
                    else:
                        console.print("\n[cyan][Today's Conversation][/cyan]")
                        for msg in messages:
                            role = "You" if msg["role"] == "user" else "JARVIS"
                            console.print(f"[{msg['time']}] {role}: {msg['content']}")
                        console.print()
                elif user_input == "/session":
                    summary = get_session_summary()
                    console.print(f"[cyan]{summary}[/cyan]")
                elif user_input == "/projects":
                    list_projects()
                elif user_input == "/project":
                    if active_project:
                        console.print(f"[cyan]Active project: {PROJECTS[active_project]['name']}[/cyan]")
                    else:
                        console.print("[dim]No project active. Use /projects to see options.[/dim]")
                elif user_input == "/sales":
                    active_project = "sales"
                    console.print(f"[green][Project] Switched to: {PROJECTS['sales']['name']}[/green]")
                elif user_input == "/leads":
                    active_project = "leads"
                    console.print(f"[green][Project] Switched to: {PROJECTS['leads']['name']}[/green]")
                elif user_input == "/jarvis":
                    active_project = "jarvis"
                    console.print(f"[green][Project] Switched to: {PROJECTS['jarvis']['name']}[/green]")
                
                # Phase 1: Long-Term Memory Commands
                elif user_input.startswith("/remember ") and long_mem:
                    fact = user_input[10:].strip()
                    if fact:
                        mem_id = long_mem.remember(fact)
                        console.print(f"[green]Memory stored, sir (ID: {mem_id}).[/green]")
                    else:
                        console.print("[yellow]Please provide something to remember, sir.[/yellow]")
                
                elif user_input.startswith("/recall") and long_mem:
                    query = user_input[7:].strip()
                    if query:
                        memories = long_mem.recall(query, limit=5)
                    else:
                        memories = long_mem.recall_all(limit=10)
                    
                    if memories:
                        console.print("\n[cyan][Stored Memories][/cyan]")
                        for mem in memories:
                            time_str = mem.timestamp.split('T')[0] if 'T' in mem.timestamp else mem.timestamp
                            console.print(f"[dim][{mem.id}][/dim] [{time_str}] {mem.content}")
                            console.print(f"    [dim]Category: {mem.category} | Source: {mem.source}[/dim]")
                        console.print()
                    else:
                        console.print("[dim]No matching memories found, sir.[/dim]")
                
                elif user_input.startswith("/forget ") and long_mem:
                    try:
                        mem_id = int(user_input[8:].strip())
                        if long_mem.forget(mem_id):
                            console.print(f"[green]Memory {mem_id} forgotten, sir.[/green]")
                        else:
                            console.print(f"[yellow]Memory {mem_id} not found, sir.[/yellow]")
                    except ValueError:
                        console.print("[yellow]Please provide a valid memory ID, sir.[/yellow]")
                
                # Phase 1: Corrections Commands
                elif user_input == "/corrections" and corrections:
                    corr_list = corrections.get_corrections(limit=10)
                    if corr_list:
                        console.print("\n[cyan][Recent Corrections][/cyan]")
                        for corr in corr_list:
                            time_str = corr.timestamp.split('T')[0] if 'T' in corr.timestamp else corr.timestamp
                            console.print(f"\n[dim][{corr.id}][/dim] [{time_str}]")
                            console.print(f"  [yellow]Original:[/yellow] {corr.original_response[:100]}...")
                            console.print(f"  [green]Correction:[/green] {corr.correction[:100]}...")
                            console.print(f"  [dim]Context: {corr.query_context[:80]}...[/dim]")
                        console.print()
                    else:
                        console.print("[dim]No corrections recorded yet, sir.[/dim]")
                
                # Phase 1: Notes Commands
                elif user_input.startswith("/note ") and notes:
                    content = user_input[6:].strip()
                    if content:
                        note_id = notes.add_note(content)
                        # Extract and display tags
                        tags = [tag for tag in content.split() if tag.startswith('#')]
                        if tags:
                            console.print(f"[green]Note saved, sir (ID: {note_id}). Tags: {' '.join(tags)}[/green]")
                        else:
                            console.print(f"[green]Note saved, sir (ID: {note_id}).[/green]")
                    else:
                        console.print("[yellow]Please provide note content, sir.[/yellow]")
                
                elif user_input.startswith("/notes") and notes:
                    query = user_input[6:].strip() if len(user_input) > 6 else None
                    note_list = notes.search_notes(query, limit=10)
                    
                    if note_list:
                        console.print("\n[cyan][Notes][/cyan]")
                        for note in note_list:
                            time_str = note.timestamp.split('T')[1][:5] if 'T' in note.timestamp else note.timestamp
                            console.print(f"\n[dim][{note.id}][/dim] [{time_str}] {note.content}")
                            if note.tags:
                                tags_formatted = " ".join(f"#{tag}" for tag in note.tags.split(','))
                                console.print(f"  [dim]{tags_formatted}[/dim]")
                        console.print()
                    else:
                        console.print("[dim]No notes found, sir.[/dim]")
                
                elif user_input.startswith("/note-export ") and notes:
                    date = user_input[13:].strip()
                    try:
                        export_path = notes.export_notes(date)
                        if export_path:
                            console.print(f"[green]Notes exported to {export_path}, sir.[/green]")
                        else:
                            console.print(f"[yellow]No notes found for {date}, sir.[/yellow]")
                    except Exception as e:
                        console.print(f"[red]Export failed: {str(e)}[/red]")
                
                # Phase 2: Reminder Commands
                elif user_input.startswith("/remind ") and reminders:
                    parts = user_input[8:].strip().split(maxsplit=1)
                    if len(parts) < 2:
                        console.print("[yellow]Usage: /remind [time] [message], sir.[/yellow]")
                        console.print("[dim]Examples: /remind in 30 minutes Check email[/dim]")
                        console.print("[dim]          /remind tomorrow 9am Team meeting[/dim]")
                    else:
                        # Parse time and message - time can be multiple words
                        # Strategy: try parsing progressively longer time strings
                        time_str = ""
                        message = ""
                        words = parts[0].split() + parts[1].split()
                        
                        for i in range(1, len(words) + 1):
                            try:
                                test_time = " ".join(words[:i])
                                # Try to parse time - if it fails, continue
                                reminders._parse_time(test_time)
                                time_str = test_time
                                message = " ".join(words[i:])
                            except:
                                if time_str:  # We found a valid time already
                                    break
                        
                        if not time_str or not message:
                            console.print("[yellow]Could not parse time, sir. Try: 'in 30 minutes' or 'tomorrow 9am'[/yellow]")
                        else:
                            try:
                                reminder_id = reminders.create_reminder(time_str, message)
                                console.print(f"[green]Reminder set, sir (ID: {reminder_id}).[/green]")
                            except ValueError as e:
                                console.print(f"[yellow]{str(e)}[/yellow]")
                
                elif user_input == "/reminders" and reminders:
                    reminder_list = reminders.list_reminders()
                    if reminder_list:
                        console.print("\n[cyan][Pending Reminders][/cyan]")
                        for rem in reminder_list:
                            time_str = rem.reminder_time.split('T')[1][:5] if 'T' in rem.reminder_time else rem.reminder_time
                            date_str = rem.reminder_time.split('T')[0] if 'T' in rem.reminder_time else ""
                            console.print(f"[dim][{rem.id}][/dim] [{date_str} {time_str}] {rem.message}")
                        console.print()
                    else:
                        console.print("[dim]No pending reminders, sir.[/dim]")
                
                elif user_input.startswith("/done ") and reminders:
                    try:
                        reminder_id = int(user_input[6:].strip())
                        if reminders.mark_done(reminder_id):
                            console.print(f"[green]Reminder {reminder_id} marked complete, sir.[/green]")
                        else:
                            console.print(f"[yellow]Reminder {reminder_id} not found, sir.[/yellow]")
                    except ValueError:
                        console.print("[yellow]Please provide a valid reminder ID, sir.[/yellow]")
                
                # Phase 2: Habit Commands
                elif user_input.startswith("/habit-add ") and habits:
                    name = user_input[11:].strip()
                    if name:
                        try:
                            habit_id = habits.add_habit(name)
                            console.print(f"[green]Habit '{name}' created, sir (ID: {habit_id}).[/green]")
                        except ValueError as e:
                            console.print(f"[yellow]{str(e)}[/yellow]")
                    else:
                        console.print("[yellow]Please provide a habit name, sir.[/yellow]")
                
                elif user_input.startswith("/habit ") and habits:
                    name = user_input[7:].strip()
                    if name:
                        try:
                            completed = habits.complete_habit(name)
                            if completed:
                                habit_list = habits.list_habits()
                                habit = next((h for h in habit_list if h.name == name), None)
                                if habit:
                                    console.print(f"[green]✓ Habit '{name}' completed, sir. Streak: {habit.streak_count} days![/green]")
                                else:
                                    console.print(f"[green]✓ Habit '{name}' completed, sir.[/green]")
                            else:
                                console.print(f"[yellow]Habit '{name}' already completed today, sir.[/yellow]")
                        except ValueError as e:
                            console.print(f"[yellow]{str(e)}[/yellow]")
                    else:
                        console.print("[yellow]Please provide a habit name, sir.[/yellow]")
                
                elif user_input == "/habits" and habits:
                    habit_list = habits.list_habits()
                    if habit_list:
                        console.print("\n[cyan][Daily Habits][/cyan]")
                        for habit in habit_list:
                            status = "✓" if habit.completed_today else "✗"
                            status_color = "green" if habit.completed_today else "yellow"
                            console.print(f"[{status_color}]{status}[/{status_color}] {habit.name} - [cyan]{habit.streak_count} day streak[/cyan]")
                        console.print()
                    else:
                        console.print("[dim]No habits tracked yet, sir. Use /habit-add to create one.[/dim]")
                
                # Phase 2: Focus Commands
                elif user_input.startswith("/focus") and focus:
                    parts = user_input.split()
                    if len(parts) == 1:
                        if focus.active:
                            # Show status or end early
                            remaining = focus.get_remaining_time()
                            console.print(f"[cyan]Focus mode active: {remaining}[/cyan]")
                            console.print("[dim]Type /focus end to stop early[/dim]")
                        else:
                            # Start default 25-minute session
                            import tts as tts_module
                            result = focus.start(25, tts=tts_module)
                            console.print(f"[cyan]{result}[/cyan]")
                    elif len(parts) == 2:
                        if parts[1] == "end":
                            result = focus.end_early()
                            console.print(f"[yellow]{result}[/yellow]")
                        else:
                            try:
                                minutes = int(parts[1])
                                import tts as tts_module
                                result = focus.start(minutes, tts=tts_module)
                                console.print(f"[cyan]{result}[/cyan]")
                            except ValueError:
                                console.print("[yellow]Please provide a valid number of minutes, sir.[/yellow]")
                
                elif user_input == "/focus-stats" and focus:
                    stats_today = focus.get_stats(days=1)
                    stats_week = focus.get_stats(days=7)
                    
                    console.print("\n[cyan][Focus Statistics][/cyan]")
                    console.print(f"[bold]Today:[/bold]")
                    console.print(f"  Sessions: {stats_today['total_sessions']}")
                    console.print(f"  Total minutes: {stats_today['total_minutes']}")
                    console.print(f"  Avg session: {stats_today['avg_session_minutes']} min")
                    console.print(f"\n[bold]This week:[/bold]")
                    console.print(f"  Sessions: {stats_week['total_sessions']}")
                    console.print(f"  Total minutes: {stats_week['total_minutes']}")
                    console.print(f"  Avg session: {stats_week['avg_session_minutes']} min\n")
                
                # Phase 2: Summary Command
                elif user_input == "/summary":
                    from datetime import date
                    import os
                    today = date.today().isoformat()
                    session_log_path = f"./logs/{today}_session.json"
                    
                    if not os.path.exists(session_log_path):
                        console.print("[dim]No activity to summarize today, sir.[/dim]")
                    else:
                        console.print("[cyan]Generating daily summary, sir...[/cyan]")
                        try:
                            summary = generate_summary(session_log_path, get_completion)
                            if summary:
                                filepath = save_summary(summary)
                                console.print(f"[green]Summary saved to {filepath}, sir.[/green]")
                                console.print(f"\n{summary}\n")
                            else:
                                console.print("[dim]No activity to summarize today, sir.[/dim]")
                        except Exception as e:
                            console.print(f"[red]Summary generation failed: {str(e)}[/red]")
                
                # Phase 3: Git Operations
                elif user_input.startswith("/git") and PHASE3_AVAILABLE:
                    parts = user_input.split(maxsplit=2)
                    if len(parts) < 2:
                        console.print("[yellow]Usage: /git [command], sir.[/yellow]")
                        console.print("[dim]Commands: status, commit, push, branch, log, pull, diff[/dim]")
                    else:
                        try:
                            git = GitOps()
                            command = parts[1].lower()
                            
                            if command == "status":
                                result = git.status()
                                console.print(result)
                            elif command == "commit":
                                if len(parts) < 3:
                                    console.print("[yellow]Commit message required, sir.[/yellow]")
                                else:
                                    message = parts[2]
                                    result = git.commit(message)
                                    console.print(f"[green]{result}[/green]")
                            elif command == "push":
                                if len(parts) >= 3 and parts[2] == "confirm":
                                    result = git.push_confirm()
                                else:
                                    result = git.push()
                                console.print(f"[cyan]{result}[/cyan]")
                            elif command == "branch":
                                result = git.branch()
                                console.print(result)
                            elif command == "log":
                                result = git.log()
                                console.print(result)
                            elif command == "pull":
                                result = git.pull()
                                console.print(f"[green]{result}[/green]")
                            elif command == "diff":
                                result = git.diff()
                                console.print(result)
                            else:
                                console.print(f"[yellow]Unknown git command: {command}[/yellow]")
                        except ValueError as e:
                            console.print(f"[red]{str(e)}[/red]")
                        except Exception as e:
                            console.print(f"[red]Git error: {str(e)}[/red]")
                
                # Phase 3: Error Explainer
                elif user_input.startswith("/explain-error") and PHASE3_AVAILABLE:
                    parts = user_input.split(maxsplit=1)
                    traceback_text = None
                    
                    if len(parts) == 1:
                        # Read from clipboard
                        try:
                            import pyperclip
                            clipboard_content = pyperclip.paste()
                            traceback_text = extract_traceback(clipboard_content)
                            if not traceback_text:
                                console.print("[yellow]No Python traceback found in clipboard, sir.[/yellow]")
                                continue
                        except ImportError:
                            console.print("[yellow]Clipboard support requires: pip install pyperclip[/yellow]")
                            continue
                    else:
                        # Read from file
                        filepath = parts[1].strip()
                        try:
                            with open(filepath, 'r', encoding='utf-8') as f:
                                file_content = f.read()
                            traceback_text = extract_traceback(file_content)
                            if not traceback_text:
                                console.print(f"[yellow]No Python traceback found in {filepath}, sir.[/yellow]")
                                continue
                        except Exception as e:
                            console.print(f"[red]Could not read file: {str(e)}[/red]")
                            continue
                    
                    if traceback_text:
                        console.print("[cyan]Analyzing error, sir...[/cyan]")
                        explanation = explain_error(traceback_text, api_router=get_completion)
                        console.print(explanation)
                
                # Phase 3: PR Writer
                elif user_input.startswith("/write-pr") and PHASE3_AVAILABLE:
                    parts = user_input.split(maxsplit=1)
                    target_branch = parts[1].strip() if len(parts) > 1 else "main"
                    
                    console.print(f"[cyan]Generating PR description against '{target_branch}', sir...[/cyan]")
                    try:
                        description = generate_pr_description(branch_to=target_branch, api_router=get_completion)
                        if "Error" in description or "error" in description:
                            console.print(f"[yellow]{description}[/yellow]")
                        else:
                            filepath = save_pr_description(description)
                            console.print(f"[green]PR description saved to {filepath}, sir.[/green]")
                            console.print(f"\n{description}\n")
                    except Exception as e:
                        console.print(f"[red]PR generation failed: {str(e)}[/red]")
                
                # Phase 3: Dependency Scanner
                elif user_input == "/check-deps" and PHASE3_AVAILABLE:
                    console.print("[cyan]Scanning dependencies for vulnerabilities, sir...[/cyan]")
                    try:
                        results = scan_dependencies()
                        formatted = format_scan_results(results)
                        console.print(formatted)
                    except Exception as e:
                        console.print(f"[red]Dependency scan failed: {str(e)}[/red]")
                
                # Phase 4: Web Search
                elif user_input.startswith("/search ") and PHASE4_AVAILABLE:
                    query = user_input[8:].strip()
                    if query:
                        if not is_online():
                            console.print("[yellow]Web search unavailable offline, sir.[/yellow]")
                        else:
                            console.print(f"[cyan]Searching for: {query}[/cyan]")
                            try:
                                results = search_web(query)
                                if results:
                                    formatted = format_search_results(results)
                                    console.print(formatted)
                                else:
                                    console.print("[yellow]No results found, sir.[/yellow]")
                            except Exception as e:
                                console.print(f"[red]Search failed: {str(e)}[/red]")
                    else:
                        console.print("[yellow]Please provide a search query, sir.[/yellow]")
                
                # Phase 4: Audio Controls
                elif user_input == "/sounds" and PHASE4_AVAILABLE and audio:
                    new_state = audio.toggle()
                    if new_state:
                        console.print("[green]Audio feedback enabled, sir.[/green]")
                        audio.play("command")
                    else:
                        console.print("[yellow]Audio feedback disabled, sir.[/yellow]")
                
                elif user_input.startswith("/volume ") and PHASE4_AVAILABLE and audio:
                    try:
                        level = int(user_input[8:].strip())
                        if audio.set_volume(level):
                            console.print(f"[green]Volume set to {level}%, sir.[/green]")
                            audio.play("command")
                        else:
                            console.print("[yellow]Audio system unavailable, sir.[/yellow]")
                    except ValueError:
                        console.print("[yellow]Please provide a valid volume level (0-100), sir.[/yellow]")
                
                elif user_input == "/audio-status" and PHASE4_AVAILABLE and audio:
                    status = audio.get_status()
                    console.print(f"[cyan]{status}[/cyan]")
                
                # Phase 4: Briefing
                elif user_input == "/briefing" and PHASE4_AVAILABLE:
                    console.print("[cyan]Generating briefing, sir...[/cyan]")
                    try:
                        briefing_text = generate_briefing()
                        console.print("\n" + briefing_text + "\n")
                        
                        # Speak if TTS enabled
                        if tts_is_enabled():
                            speak_async(briefing_text)
                    except Exception as e:
                        console.print(f"[red]Briefing generation failed: {str(e)}[/red]")
                
                # Phase 5: Dashboard
                elif user_input == "/dashboard":
                    try:
                        from dashboard import start_dashboard, create_dashboard_html
                        import threading
                        
                        # Create HTML template if doesn't exist
                        create_dashboard_html()
                        
                        # Start dashboard in background thread
                        dashboard_thread = threading.Thread(
                            target=start_dashboard,
                            args=(5000,),
                            daemon=True
                        )
                        dashboard_thread.start()
                        
                        console.print("[green]Dashboard running at http://localhost:5000, sir.[/green]")
                        console.print("[dim]Dashboard will run until JARVIS exits.[/dim]")
                    except Exception as e:
                        console.print(f"[red]Dashboard failed to start: {str(e)}[/red]")
                
                # Phase 5: API Server
                elif user_input == "/api-server":
                    try:
                        from api_server import start_api_server
                        import threading
                        
                        # Start API server in background thread
                        api_thread = threading.Thread(
                            target=start_api_server,
                            args=(8000,),
                            daemon=True
                        )
                        api_thread.start()
                        
                        console.print("[green]API server running at http://localhost:8000, sir.[/green]")
                        console.print("[dim]API documentation at http://localhost:8000/docs[/dim]")
                        console.print("[dim]API will run until JARVIS exits.[/dim]")
                    except Exception as e:
                        console.print(f"[red]API server failed to start: {str(e)}[/red]")
                
                # Agent-Reach: Health Check
                elif user_input == "/ar-doctor" and agent_reach:
                    console.print("[cyan]Checking Agent-Reach health...[/cyan]")
                    try:
                        info = agent_reach.doctor_check()
                        if 'error' in info:
                            console.print(f"[red]{info['error']}[/red]")
                        else:
                            console.print("[green]Agent-Reach Status:[/green]")
                            console.print(json.dumps(info, indent=2))
                    except Exception as e:
                        console.print(f"[red]Health check failed: {str(e)}[/red]")
                
                # Agent-Reach: Web Search
                elif user_input.startswith("/ar-web ") and agent_reach:
                    query = user_input[8:].strip()
                    if query:
                        console.print(f"[cyan]Searching web for: {query}...[/cyan]")
                        try:
                            results = agent_reach.web_search(query, num_results=5)
                            if results:
                                formatted = format_search_results_ar(results)
                                console.print(f"\n{formatted}")
                            else:
                                console.print("[yellow]No results found, sir.[/yellow]")
                        except Exception as e:
                            console.print(f"[red]Search failed: {str(e)}[/red]")
                    else:
                        console.print("[yellow]Please provide a search query, sir.[/yellow]")
                
                # Agent-Reach: Twitter Search
                elif user_input.startswith("/ar-twitter ") and agent_reach:
                    query = user_input[12:].strip()
                    if query:
                        console.print(f"[cyan]Searching Twitter for: {query}...[/cyan]")
                        try:
                            results = agent_reach.twitter_search(query, limit=10)
                            console.print(f"\n{results}\n")
                        except Exception as e:
                            console.print(f"[red]Twitter search failed: {str(e)}[/red]")
                    else:
                        console.print("[yellow]Please provide a search query, sir.[/yellow]")
                
                # Agent-Reach: Reddit Search
                elif user_input.startswith("/ar-reddit ") and agent_reach:
                    query = user_input[11:].strip()
                    if query:
                        console.print(f"[cyan]Searching Reddit for: {query}...[/cyan]")
                        try:
                            results = agent_reach.reddit_search(query, limit=10)
                            console.print(f"\n{results}\n")
                        except Exception as e:
                            console.print(f"[red]Reddit search failed: {str(e)}[/red]")
                    else:
                        console.print("[yellow]Please provide a search query, sir.[/yellow]")
                
                # Agent-Reach: GitHub Search
                elif user_input.startswith("/ar-github ") and agent_reach:
                    query = user_input[11:].strip()
                    if query:
                        console.print(f"[cyan]Searching GitHub for: {query}...[/cyan]")
                        try:
                            results = agent_reach.github_search_repos(query, limit=10)
                            console.print(f"\n{results}\n")
                        except Exception as e:
                            console.print(f"[red]GitHub search failed: {str(e)}[/red]")
                    else:
                        console.print("[yellow]Please provide a search query, sir.[/yellow]")
                
                # Agent-Reach: Read Webpage
                elif user_input.startswith("/ar-read ") and agent_reach:
                    url = user_input[9:].strip()
                    if url:
                        console.print(f"[cyan]Reading: {url}...[/cyan]")
                        console.print("[dim]This may take a moment...[/dim]")
                        try:
                            content = agent_reach.read_webpage(url)
                            console.print("\n[cyan]Content:[/cyan]")
                            # Show first 1000 characters
                            preview = content[:1000] + "..." if len(content) > 1000 else content
                            console.print(preview)
                            console.print(f"\n[dim]Total length: {len(content)} characters[/dim]")
                        except Exception as e:
                            console.print(f"[red]Failed to read page: {str(e)}[/red]")
                    else:
                        console.print("[yellow]Please provide a URL, sir.[/yellow]")
                
                # Agent-Reach: YouTube Subtitles
                elif user_input.startswith("/ar-youtube ") and agent_reach:
                    url = user_input[12:].strip()
                    if url:
                        console.print(f"[cyan]Fetching subtitles from: {url}...[/cyan]")
                        console.print("[dim]This may take a while...[/dim]")
                        try:
                            result = agent_reach.youtube_subtitles(url)
                            console.print(f"\n{result}\n")
                        except Exception as e:
                            console.print(f"[red]Failed to get subtitles: {str(e)}[/red]")
                    else:
                        console.print("[yellow]Please provide a YouTube URL, sir.[/yellow]")
                
                # Agent-Reach: V2EX Hot Topics
                elif user_input == "/ar-v2ex" and agent_reach:
                    console.print("[cyan]Fetching V2EX hot topics...[/cyan]")
                    try:
                        topics = agent_reach.v2ex_hot_topics()
                        console.print(f"\n{topics}\n")
                    except Exception as e:
                        console.print(f"[red]Failed to get V2EX topics: {str(e)}[/red]")
                
                # Agent-Reach: Check Update
                elif user_input == "/ar-update" and agent_reach:
                    console.print("[cyan]Checking for Agent-Reach updates...[/cyan]")
                    try:
                        result = agent_reach.check_update()
                        console.print(f"{result['message']}")
                    except Exception as e:
                        console.print(f"[red]Update check failed: {str(e)}[/red]")
                
                # APILayer: Currency Exchange Rates
                elif user_input.startswith("/api-currency") and apilayer:
                    parts = user_input[13:].strip().split()
                    base = parts[0] if parts else "USD"
                    symbols = parts[1] if len(parts) > 1 else None
                    
                    console.print(f"[cyan]Fetching exchange rates (base: {base})...[/cyan]")
                    try:
                        result = apilayer.get_exchange_rates(base, symbols)
                        formatted = format_exchange_rates(result)
                        console.print(formatted)
                    except Exception as e:
                        console.print(f"[red]Failed: {str(e)}[/red]")
                
                # APILayer: Currency Conversion
                elif user_input.startswith("/api-convert ") and apilayer:
                    parts = user_input[13:].strip().split()
                    if len(parts) < 3:
                        console.print("[yellow]Usage: /api-convert [from] [to] [amount], sir.[/yellow]")
                        console.print("[dim]Example: /api-convert USD EUR 100[/dim]")
                    else:
                        from_curr, to_curr, amount = parts[0], parts[1], float(parts[2])
                        console.print(f"[cyan]Converting {amount} {from_curr} to {to_curr}...[/cyan]")
                        try:
                            result = apilayer.convert_currency(from_curr, to_curr, amount)
                            if result.success:
                                data = result.data
                                converted = data.get('result', 'N/A')
                                rate = data.get('info', {}).get('rate', 'N/A')
                                console.print(f"\n  {amount} {from_curr} = [green]{converted:.2f} {to_curr}[/green]")
                                console.print(f"  Exchange rate: {rate}")
                            else:
                                console.print(f"[red]{result.error.get('message', 'Conversion failed')}[/red]")
                        except Exception as e:
                            console.print(f"[red]Failed: {str(e)}[/red]")
                
                # APILayer: IP Geolocation
                elif user_input.startswith("/api-geoip ") and apilayer:
                    ip = user_input[11:].strip()
                    console.print(f"[cyan]Geolocating IP: {ip}...[/cyan]")
                    try:
                        result = apilayer.geolocate_ip(ip)
                        formatted = format_ip_location(result)
                        console.print(formatted)
                    except Exception as e:
                        console.print(f"[red]Failed: {str(e)}[/red]")
                
                # APILayer: Own IP Location
                elif user_input == "/api-myip" and apilayer:
                    console.print("[cyan]Getting your IP location...[/cyan]")
                    try:
                        result = apilayer.get_own_ip_location()
                        formatted = format_ip_location(result)
                        console.print(formatted)
                    except Exception as e:
                        console.print(f"[red]Failed: {str(e)}[/red]")
                
                # APILayer: Email Validation
                elif user_input.startswith("/api-email ") and apilayer:
                    email = user_input[11:].strip()
                    console.print(f"[cyan]Validating email: {email}...[/cyan]")
                    try:
                        result = apilayer.validate_email(email)
                        if result.success:
                            data = result.data
                            valid = "✓ VALID" if data.get('format_valid') and data.get('mx_found') else "✗ INVALID"
                            console.print(f"\n  Email: {email}")
                            console.print(f"  Status: [green]{valid}[/green]" if "VALID" in valid else f"  Status: [red]{valid}[/red]")
                            console.print(f"  Format: {'Valid' if data.get('format_valid') else 'Invalid'}")
                            console.print(f"  MX Records: {'Found' if data.get('mx_found') else 'Not found'}")
                            console.print(f"  SMTP: {'Valid' if data.get('smtp_check') else 'Not checked'}")
                            console.print(f"  Disposable: {'Yes' if data.get('disposable') else 'No'}")
                        else:
                            console.print(f"[red]{result.error.get('message', 'Validation failed')}[/red]")
                    except Exception as e:
                        console.print(f"[red]Failed: {str(e)}[/red]")
                
                # APILayer: Phone Validation
                elif user_input.startswith("/api-phone ") and apilayer:
                    number = user_input[11:].strip()
                    console.print(f"[cyan]Validating phone: {number}...[/cyan]")
                    try:
                        result = apilayer.validate_phone(number)
                        if result.success:
                            data = result.data
                            valid = "✓ VALID" if data.get('valid') else "✗ INVALID"
                            console.print(f"\n  Number: {data.get('number', 'N/A')}")
                            console.print(f"  Status: [green]{valid}[/green]" if "VALID" in valid else f"  Status: [red]{valid}[/red]")
                            console.print(f"  Country: {data.get('country_name', 'N/A')} ({data.get('country_code', 'N/A')})")
                            console.print(f"  Location: {data.get('location', 'N/A')}")
                            console.print(f"  Carrier: {data.get('carrier', 'N/A')}")
                            console.print(f"  Line Type: {data.get('line_type', 'N/A')}")
                        else:
                            console.print(f"[red]{result.error.get('message', 'Validation failed')}[/red]")
                    except Exception as e:
                        console.print(f"[red]Failed: {str(e)}[/red]")
                
                # APILayer: Weather
                elif user_input.startswith("/api-weather ") and apilayer:
                    location = user_input[13:].strip()
                    console.print(f"[cyan]Getting weather for: {location}...[/cyan]")
                    try:
                        result = apilayer.get_current_weather(location)
                        formatted = format_weather(result)
                        console.print(formatted)
                    except Exception as e:
                        console.print(f"[red]Failed: {str(e)}[/red]")
                
                # APILayer: Geocoding
                elif user_input.startswith("/api-geocode ") and apilayer:
                    address = user_input[13:].strip()
                    console.print(f"[cyan]Geocoding address: {address}...[/cyan]")
                    try:
                        result = apilayer.geocode_address(address, limit=3)
                        if result.success:
                            data = result.data.get('data', [])
                            if data:
                                console.print("\n[cyan]Results:[/cyan]")
                                for i, loc in enumerate(data, 1):
                                    console.print(f"\n  [{i}] {loc.get('label', 'N/A')}")
                                    console.print(f"      Coordinates: {loc.get('latitude', 'N/A')}, {loc.get('longitude', 'N/A')}")
                                    console.print(f"      Type: {loc.get('type', 'N/A')}")
                            else:
                                console.print("[yellow]No results found, sir.[/yellow]")
                        else:
                            console.print(f"[red]{result.error.get('message', 'Geocoding failed')}[/red]")
                    except Exception as e:
                        console.print(f"[red]Failed: {str(e)}[/red]")
                
                # APILayer: Flight Info
                elif user_input.startswith("/api-flight ") and apilayer:
                    flight_code = user_input[12:].strip()
                    console.print(f"[cyan]Looking up flight: {flight_code}...[/cyan]")
                    try:
                        result = apilayer.get_flights(flight_iata=flight_code)
                        if result.success:
                            data = result.data.get('data', [])
                            if data:
                                for flight in data[:3]:  # Show first 3 results
                                    console.print(f"\n  Flight: {flight.get('flight', {}).get('iata', 'N/A')}")
                                    console.print(f"  Status: {flight.get('flight_status', 'N/A')}")
                                    dep = flight.get('departure', {})
                                    arr = flight.get('arrival', {})
                                    console.print(f"  From: {dep.get('airport', 'N/A')} ({dep.get('iata', 'N/A')})")
                                    console.print(f"  To: {arr.get('airport', 'N/A')} ({arr.get('iata', 'N/A')})")
                                    console.print(f"  Departure: {dep.get('scheduled', 'N/A')}")
                                    console.print(f"  Arrival: {arr.get('scheduled', 'N/A')}")
                            else:
                                console.print("[yellow]No flight data found, sir.[/yellow]")
                        else:
                            console.print(f"[red]{result.error.get('message', 'Flight lookup failed')}[/red]")
                    except Exception as e:
                        console.print(f"[red]Failed: {str(e)}[/red]")
                
                # APILayer: Language Detection
                elif user_input.startswith("/api-lang ") and apilayer:
                    text = user_input[10:].strip()
                    console.print(f"[cyan]Detecting language...[/cyan]")
                    try:
                        result = apilayer.detect_language(text)
                        if result.success:
                            results = result.data.get('results', [])
                            if results:
                                console.print("\n[cyan]Detected Languages:[/cyan]")
                                for lang in results[:3]:
                                    console.print(f"  {lang.get('language_name', 'N/A')} ({lang.get('language_code', 'N/A')})")
                                    console.print(f"  Confidence: {lang.get('confidence', 0):.1f}%")
                            else:
                                console.print("[yellow]Could not detect language, sir.[/yellow]")
                        else:
                            console.print(f"[red]{result.error.get('message', 'Detection failed')}[/red]")
                    except Exception as e:
                        console.print(f"[red]Failed: {str(e)}[/red]")
                
                else:
                    console.print(f"[red]Unknown command: {user_input}[/red]")
                    console.print("[dim]Type /help for available commands[/dim]")
                
                # Skip to next iteration unless /listen was used
                if not user_input.startswith("/listen"):
                    continue
            
            # Send to API router with context
            try:
                # Play command sound if audio enabled
                if audio and audio.enabled:
                    audio.play("command")
                
                # Check if this is a correction
                if corrections and corrections.is_correction(user_input):
                    if last_response:
                        # Record the correction
                        corr_id = corrections.record_correction(
                            last_response,
                            user_input,
                            last_query
                        )
                        console.print(f"[green]Correction recorded, sir (ID: {corr_id}). I shall learn from this.[/green]")
                        # Continue to process normally
                
                # Detect user emotion and modify system prompt
                user_emotion = "neutral"
                if PHASE4_AVAILABLE:
                    user_emotion = detect_emotion(user_input)
                
                # Build prompt with project, history and context
                memory = CodeMemory()
                results = memory.search(user_input, top_k=3)
                
                parts = []
                
                # Add project context if active
                if active_project:
                    proj_context = build_project_prompt(active_project)
                    if proj_context:
                        parts.append(proj_context)
                
                # Add conversation history
                history = build_history_prompt(load_today())
                if history:
                    parts.append(history)
                
                # Add learned corrections context
                if corrections:
                    corr_context = corrections.build_correction_context(user_input)
                    if corr_context:
                        parts.append(corr_context)
                
                # Add code context from semantic search
                if results:
                    context = format_context(results)
                    parts.append(context)
                    console.print(f"[dim]Referenced: {', '.join(r.file_path for r in results)}[/dim]")
                
                parts.append("My question: " + user_input)
                prompt = "\n\n".join(parts)
                
                # Store query for potential correction
                last_query = user_input
                
                # Apply emotion-based prompt modification
                if PHASE4_AVAILABLE and user_emotion != "neutral":
                    # Note: This is a simplified implementation
                    # Full implementation would modify the system prompt in api_router
                    pass
                
                response = get_completion(prompt)
                console.print(f"[green]AI:[/green] {response}\n")
                
                # Store response for potential correction
                last_response = response
                
                # Auto-extract memorable information
                if long_mem:
                    extracted = long_mem.auto_extract(user_input, response)
                    if extracted:
                        console.print(f"[dim][Memory auto-saved: {extracted[:50]}...][/dim]")
                
                # Speak response if TTS is enabled
                if tts_is_enabled():
                    speak_async(response)
                
                # Save to session log
                save_message("user", user_input)
                save_message("jarvis", response)
            except Exception as e:
                console.print(f"[red]Error:[/red] {str(e)}\n")
                # Play error sound if audio enabled
                if audio and audio.enabled:
                    audio.play("error")
            
        except KeyboardInterrupt:
            console.print("\n[yellow]Goodbye![/yellow]")
            break
        except Exception as e:
            console.print(f"[red]Error:[/red] {str(e)}\n")


def main():
    """
    Main entry point.
    Load environment variables and start the chat interface.
    """
    # Load .env file FIRST
    load_dotenv()
    
    # Initialize database if Phase 1 available
    if PHASE1_AVAILABLE:
        try:
            from db_init import init_database
            init_database()
            console.print("[dim]Database: jarvis.db initialized[/dim]")
        except Exception as e:
            console.print(f"[yellow]Database initialization warning: {e}[/yellow]")
    
    # Validate API keys - exit if none are valid
    valid_apis = validate_keys()
    if not valid_apis:
        console.print("[red]ERROR: No valid API keys found in .env file.[/red]")
        console.print("[yellow]Please add at least one API key to .env:[/yellow]")
        console.print("  - GROQ_API_KEY (recommended, get from https://console.groq.com)")
        console.print("  - GEMINI_API_KEY (get from https://aistudio.google.com/app/apikey)")
        console.print("  - TOGETHER_API_KEY or MISTRAL_API_KEY")
        sys.exit(1)
    
    console.print(f"[dim]APIs: {', '.join(valid_apis)} ready[/dim]")
    
    # Check if memory index exists
    db_path = Path("./chroma_db")
    if db_path.exists():
        console.print("[dim]Memory: Index loaded.[/dim]")
    else:
        console.print("[dim]Memory: No index. Type /index to scan your projects.[/dim]")
    
    # Load last session
    last_session = load_last_session()
    if last_session:
        console.print("[dim]Memory: Last session loaded. Type /history to see it.[/dim]")
    else:
        console.print("[dim]Memory: No past sessions found.[/dim]")
    
    # Check voice availability
    if is_voice_available():
        console.print("[dim]Voice: Microphone available. Type /voice to enable.[/dim]")
    else:
        console.print("[dim]Voice: No microphone detected. Voice disabled.[/dim]")
    
    # Check TTS availability
    if is_tts_available():
        console.print("[dim]Speech: Text-to-speech ready. Type /speak to enable.[/dim]")
    else:
        console.print("[dim]Speech: TTS not available.[/dim]")
    
    # Display startup banner
    show_startup_banner()
    
    # Start chat loop
    chat_loop()


if __name__ == "__main__":
    main()
