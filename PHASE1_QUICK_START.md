# Phase 1 Quick Start Guide

## 🚀 Getting Started

Phase 1 adds memory, learning, and note-taking capabilities to JARVIS. Start using the new features immediately:

```bash
cd "C:\Users\User\Desktop\personal arvis\rome-jarvis"
python main.py
```

---

## 📝 New Commands

### Memory Commands

**Store a fact or preference:**
```
/remember Python is my favorite language
/remember I prefer dark mode when coding
```

**Search your memories:**
```
/recall Python          # Search for "Python"
/recall                 # Show recent memories
```

**Delete a memory:**
```
/forget 3              # Delete memory with ID 3
```

**Auto-Learning:**
JARVIS now automatically remembers when you say:
- "Remember that..."
- "I prefer..."
- "My favorite X is Y"
- "Always..." / "Never..."

---

### Correction Learning

**Correct JARVIS:**
Just start your message with correction keywords:
```
You: What's the capital of France?
JARVIS: The capital is Lyon.

You: actually, the capital of France is Paris
JARVIS: Correction recorded, sir. I shall learn from this.
```

**View correction history:**
```
/corrections           # See last 10 corrections
```

**Correction Keywords:**
- "actually"
- "correction:"
- "that's wrong"
- "incorrect"
- "no, it's"

---

### Quick Notes

**Capture a note:**
```
/note Meeting with client tomorrow #work #important
/note Buy groceries #personal
/note Research ML frameworks #project #ai
```

**View notes:**
```
/notes                 # Last 10 notes
/notes work           # Search for "work"
/notes #important     # Search by tag
```

**Export notes:**
```
/note-export 2024-01-15    # Export specific date
```

---

## 💡 Usage Examples

### Example 1: Building a Memory Base
```
You: Remember that I work on the rome-jarvis project
JARVIS: Memory stored, sir (ID: 1).

You: I prefer using Python over JavaScript
JARVIS: <response>
[Memory auto-saved: I prefer using Python over JavaScript...]

You: /recall Python
JARVIS: [Stored Memories]
[1] I work on the rome-jarvis project
[2] I prefer using Python over JavaScript
```

### Example 2: Teaching JARVIS
```
You: What framework should I use for web APIs?
JARVIS: I recommend Flask for Python web APIs.

You: actually, I prefer FastAPI for async support
JARVIS: Correction recorded, sir (ID: 1). I shall learn from this.

[Later in a new session...]
You: Help me build a REST API
JARVIS: [Uses learned correction about FastAPI preference]
```

### Example 3: Taking Notes
```
You: /note Review Phase 2 implementation tasks #jarvis #todo
JARVIS: Note saved, sir (ID: 1). Tags: #jarvis #todo

You: /note Research Coqui TTS installation #jarvis #phase4
JARVIS: Note saved, sir (ID: 2). Tags: #jarvis #phase4

You: /notes jarvis
JARVIS: [Notes]
[1] [14:30] Review Phase 2 implementation tasks #jarvis #todo
[2] [14:32] Research Coqui TTS installation #jarvis #phase4

You: /note-export 2024-01-15
JARVIS: Notes exported to ./logs/notes/2024-01-15_notes.md, sir.
```

---

## 🗂️ Where Data is Stored

All Phase 1 data is stored in **`jarvis.db`** SQLite database:
- **memories** table - Your stored facts and preferences
- **corrections** table - Learning history
- **notes** table - Quick notes with tags

Exported notes: `./logs/notes/YYYY-MM-DD_notes.md`

---

## 🔍 Behind the Scenes

### Auto-Extraction
Every time you chat with JARVIS, he analyzes your message for memorable information:
```
You: I always test my code before committing
# Auto-extracted: "test my code before committing" (preference)
```

### Context Injection
JARVIS automatically includes relevant memories in prompts:
```
You: Should I use tabs or spaces?
# JARVIS searches memories for preferences about coding style
# Injects remembered preferences into the prompt
JARVIS: Based on your preference for PEP 8...
```

### Correction Application
When JARVIS encounters a similar query to a past correction:
```
# Correction stored: "Use FastAPI, not Flask"
# Similar query: "Help me build an API"
# JARVIS injects: "User previously corrected: prefer FastAPI over Flask"
```

---

## 🎯 Tips & Best Practices

### Memory System
- ✅ **DO**: Store facts you want JARVIS to remember long-term
- ✅ **DO**: Use `/recall` to verify memories are stored
- ❌ **DON'T**: Store temporary information (use notes instead)

### Corrections
- ✅ **DO**: Correct JARVIS immediately when he makes mistakes
- ✅ **DO**: Use clear correction keywords ("actually", "correction:")
- ❌ **DON'T**: Expect corrections to apply to completely different topics

### Notes
- ✅ **DO**: Use hashtags for organization (#project, #work, #ideas)
- ✅ **DO**: Export notes regularly for backup
- ✅ **DO**: Search by tags or content
- ❌ **DON'T**: Use notes for long-term facts (use `/remember` instead)

---

## 🔧 Troubleshooting

### Database Issues
If you encounter database errors, reinitialize:
```bash
python db_init.py
```

### Memory Not Found
Check the database exists:
```bash
# Should show jarvis.db file
ls jarvis.db
```

### Commands Not Working
Verify you're using the correct syntax:
```
/remember [fact]     # ✅ Correct
/remember            # ❌ Missing argument
```

---

## 📊 Viewing Your Data

### Memory Statistics
```python
# Run in Python REPL
from long_memory import LongMemory
mem = LongMemory()
print(mem.recall_all(limit=100))
```

### Notes Statistics
```python
# Run in Python REPL
from notes import NotesSystem
notes = NotesSystem()
stats = notes.get_stats()
print(stats)
```

---

## ⏭️ What's Next?

Phase 1 provides the foundation. Upcoming phases will add:

**Phase 2 (Productivity):**
- ⏰ Reminders with `/remind` command
- 📊 Daily habit tracking
- 🎯 Pomodoro focus timer
- 📋 Daily summary generation

**Phase 3 (Developer Tools):**
- 🔧 Git integration
- 🐛 Error explainer
- 📝 PR description generator
- 🔒 Dependency vulnerability scanner

**Phase 4 (Iron Man Experience):**
- 🗣️ Neural voice (Coqui TTS)
- 🔊 Sound effects
- 🌅 Morning briefing
- 😊 Emotional response adjustment

**Phase 5 (Infrastructure):**
- 🌐 Web dashboard
- 🔌 REST API
- 🐳 Docker deployment
- ✅ Comprehensive tests

---

## 🆘 Getting Help

View all commands:
```
/help
```

Check JARVIS status:
```
/stats
```

View conversation history:
```
/history
```

---

**Enjoy your enhanced JARVIS! 🤖**
