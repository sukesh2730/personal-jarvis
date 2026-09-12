"""
ROME JARVIS - Personal AI Coding Assistant
Main entry point with terminal chat interface
"""
import os
from dotenv import load_dotenv
from rich.console import Console
from api_router import get_completion
from indexer import scan_codebase
from memory import CodeMemory
from pathlib import Path
from tools import read_file, write_file, run_file, list_files, explain_file
from context import save_message, load_today, load_last_session, build_history_prompt, get_session_summary
from config import get_project_context, get_project_path, list_projects, build_project_prompt, PROJECTS
from voice import listen, is_voice_available, load_whisper
from tts import speak_async, enable_tts, disable_tts, is_tts_available, is_enabled as tts_is_enabled

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
    console.print("  [cyan]/projects[/cyan]       - List all your projects")
    console.print("  [cyan]/project[/cyan]        - Show active project")
    console.print("  [cyan]/sales[/cyan]          - Switch to sales platform context")
    console.print("  [cyan]/leads[/cyan]          - Switch to lead gen context")
    console.print("  [cyan]/jarvis[/cyan]         - Switch to JARVIS context")
    console.print("  [cyan]/clear[/cyan]          - Clear the screen")
    console.print("  [cyan]/quit[/cyan]           - Exit the assistant\n")


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
                else:
                    console.print(f"[red]Unknown command: {user_input}[/red]")
                    console.print("[dim]Type /help for available commands[/dim]")
                
                # Skip to next iteration unless /listen was used
                if not user_input.startswith("/listen"):
                    continue
            
            # Send to API router with context
            try:
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
                
                # Add code context from semantic search
                if results:
                    context = format_context(results)
                    parts.append(context)
                    console.print(f"[dim]Referenced: {', '.join(r.file_path for r in results)}[/dim]")
                
                parts.append("My question: " + user_input)
                prompt = "\n\n".join(parts)
                
                response = get_completion(prompt)
                console.print(f"[green]AI:[/green] {response}\n")
                
                # Speak response if TTS is enabled
                if tts_is_enabled():
                    speak_async(response)
                
                # Save to session log
                save_message("user", user_input)
                save_message("jarvis", response)
            except Exception as e:
                console.print(f"[red]Error:[/red] {str(e)}\n")
            
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
