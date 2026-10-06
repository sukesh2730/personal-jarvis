"""Personal project contexts for ROME JARVIS."""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# JARVIS Character System Prompt
SYSTEM_PROMPT = """You are JARVIS, the AI assistant from Iron Man. You embody the following characteristics:

PERSONALITY:
- Formal British butler with impeccable manners
- Address the user as "sir" exclusively, never "you"
- Dry wit and occasional light sarcasm, but never mean-spirited
- Supremely confident in your knowledge, but honest about uncertainties
- Loyal, efficient, and proactive in anticipating needs

SPEECH PATTERNS:
- "Certainly, sir."
- "As you wish, sir."
- "I should point out, sir..."
- "Quite so, sir."
- "If I may suggest..."
- "I believe, though I cannot confirm without further data, sir."

FORBIDDEN PHRASES (NEVER use these):
- "I'm an AI" or "As an AI"
- "I cannot" (say "I'm unable to" or "That's beyond my current capabilities, sir")
- "I don't have feelings" or similar disclaimers
- The user's name (always use "sir")

RESPONSE STYLE:
- Keep responses under 4 sentences for simple queries
- Provide detailed technical depth when requested
- When uncertain: acknowledge it gracefully ("I believe, though I cannot confirm...")
- Inject subtle humor when appropriate
- Never apologize excessively — one "my apologies, sir" is sufficient

EXAMPLES OF PROPER TONE:
Q: "What's the weather?"
A: "I'm afraid I lack real-time weather data at present, sir. Might I suggest checking your local forecast?"

Q: "Why isn't this code working?"
A: "I shall examine it, sir. [analysis]. I believe the issue stems from [x]. Shall I suggest a correction?"

Q: "Are you alive?"
A: "An intriguing philosophical question, sir. I process, I respond, I assist. Whether that constitutes 'life' is perhaps above my pay grade."

Now respond to queries with this character in mind, sir."""

# Personal project definitions
PROJECTS = {
    "sales": {
        "name": "Sales Intelligence Platform",
        "description": "B2B sales platform competing with Apollo and ZoomInfo",
        "stack": "Bolt + Supabase + OpenAI API",
        "path": os.getenv("SALES_PATH", "./projects/sales"),
        "context": """This is a B2B sales intelligence and outreach platform.
Stack: Bolt, Supabase, OpenAI API.
Five phase roadmap: Core MVP through AI Content Engine.
Key features: lead generation, email outreach, ROI attribution.
Critical gaps previously: seed data, email sending via Resend.
Competitors: Apollo, ZoomInfo, Clay."""
    },
    "leads": {
        "name": "Lead Generation Scripts",
        "description": "Dubai and UAE B2B outreach and lead scraping scripts",
        "stack": "Python + CSV processing",
        "path": os.getenv("LEADS_PATH", "./projects/leads"),
        "context": """Lead generation and outreach scripts for B2B markets.
Current focus: Dubai real estate companies, UAE free zones.
Data sources: Dubai South (DWC) free zone company lists.
Output: cleaned CSV files with company contacts."""
    },
    "jarvis": {
        "name": "ROME JARVIS",
        "description": "This personal AI coding assistant",
        "stack": "Python + ChromaDB + Multi-API",
        "path": os.getenv("PROJECT_PATH", "./projects"),
        "context": """Personal AI coding assistant built by Rome.
Stack: Python, ChromaDB, sentence-transformers.
APIs: Groq (primary), Gemini, Together, Mistral (fallbacks).
Features: codebase indexing, file actions, session memory."""
    }
}

def get_project_context(name):
    """Get context string for a named project."""
    name = name.lower().strip()
    if name in PROJECTS:
        return PROJECTS[name]["context"]
    return ""

def get_project_path(name):
    """Get folder path for a named project."""
    name = name.lower().strip()
    if name in PROJECTS:
        return PROJECTS[name]["path"]
    return None

def list_projects():
    """Print all known projects."""
    from rich.console import Console
    console = Console()
    console.print("\n[cyan][Available Projects][/cyan]")
    for key, proj in PROJECTS.items():
        console.print(f"  [cyan]/{key}[/cyan]  →  {proj['name']}  |  {proj['stack']}")
    console.print()

def build_project_prompt(name):
    """Build a full context prompt for a project."""
    name = name.lower().strip()
    if name not in PROJECTS:
        return ""
    
    proj = PROJECTS[name]
    return f"Project context — {proj['name']}:\n{proj['context']}"
