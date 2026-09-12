# 🤖 ROME JARVIS - Personal AI Coding Assistant

Your personal AI assistant with voice input, text-to-speech, codebase memory, and project context awareness. Built for developers who want a truly personalized AI companion.

## ✨ Features

### 🎤 Voice & Speech
- **Voice Input**: Speak to JARVIS using OpenAI Whisper (offline transcription)
- **Text-to-Speech**: JARVIS speaks responses using local TTS (no API needed)
- **Full Voice Conversation**: Hands-free interaction mode

### 🧠 Smart Memory
- **Codebase Indexing**: Semantic search through your projects using ChromaDB
- **Session Memory**: Remembers all conversations across sessions
- **Context-Aware**: Automatically retrieves relevant code when answering

### 🎯 Personal Intelligence
- **Project Contexts**: Pre-configured knowledge about your projects
- **Context Switching**: `/sales`, `/leads`, `/jarvis` commands for instant context
- **Personalized Responses**: AI knows your tech stack and preferences

### 🛠️ Developer Tools
- **File Operations**: Read, run, explain code files
- **Multi-API Fallback**: 4-tier system (Groq → Gemini → Together.ai → Mistral)
- **19 Commands**: Complete terminal-based interface

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Microphone (for voice input)
- At least ONE API key (free tier works):
  - [Groq](https://console.groq.com) (Recommended - fastest)
  - [Google Gemini](https://aistudio.google.com/app/apikey)
  - [Together.ai](https://api.together.xyz)
  - [Mistral AI](https://console.mistral.ai)

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/rome-jarvis.git
cd rome-jarvis
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure API keys:**
Create a `.env` file (copy from `.env.example`):
```bash
cp .env.example .env
```

Edit `.env` and add at least one API key:
```env
GROQ_API_KEY=your_key_here
# or
GEMINI_API_KEY=your_key_here
```

4. **Run JARVIS:**
```bash
python main.py
```

---

## 📋 Commands

### Basic
- `/help` - Show all commands
- `/clear` - Clear screen
- `/quit` - Exit

### Memory & Indexing
- `/index` - Index your codebase for semantic search

### Voice & Speech
- `/voice` - Toggle voice input mode
- `/listen` - Single voice input (5 seconds)
- `/listen [secs]` - Custom duration voice input
- `/speak` - Toggle text-to-speech mode

### File Operations
- `/read [file]` - Display file contents
- `/run [file]` - Execute Python file
- `/ls [dir]` - List directory contents
- `/explain [file]` - AI explains a file

### Session
- `/history` - Show today's conversation
- `/session` - Show session summary

### Projects
- `/projects` - List all configured projects
- `/project` - Show active project
- `/sales` - Switch to sales platform context
- `/leads` - Switch to lead generation context
- `/jarvis` - Switch to JARVIS project context

---

## 🎯 Usage Examples

### Basic Chat
```
You: what is a vector database
AI: [explains with context from your codebase]
```

### Voice Conversation
```
You: /voice
[Voice mode ON]
You: [press Enter, speak]
AI: [transcribes, responds, and speaks answer]
```

### Code Assistance
```
You: /index
[Indexes codebase]
You: how does the API fallback work?
AI: [explains using YOUR actual api_router.py code]
```

### Project Context
```
You: /sales
You: what are the critical gaps in this project?
AI: [responds with knowledge of YOUR sales platform]
```

---

## 🏗️ Project Structure

```
rome-jarvis/
├── main.py              # Entry point + chat loop
├── api_router.py        # Multi-API fallback system
├── voice.py             # Voice input (Whisper)
├── tts.py               # Text-to-speech (pyttsx3)
├── memory.py            # Vector store (ChromaDB)
├── indexer.py           # Codebase scanner
├── tools.py             # File operations
├── context.py           # Session memory
├── config.py            # Project contexts
├── requirements.txt     # Dependencies
├── .env.example         # Config template
├── projects/            # Your project files
├── logs/                # Conversation logs
└── chroma_db/           # Vector database (auto-created)
```

---

## 🔧 Configuration

### Project Contexts

Edit `config.py` to add your own projects:

```python
PROJECTS = {
    "myproject": {
        "name": "My Awesome Project",
        "description": "Brief description",
        "stack": "Tech stack used",
        "path": "./projects/myproject",
        "context": """Detailed context that AI will use"""
    }
}
```

Then use `/myproject` to switch context.

### TTS Settings

Adjust speech speed and volume in `tts.py`:

```python
_engine.setProperty('rate', 175)    # Words per minute
_engine.setProperty('volume', 0.9)   # 0.0 to 1.0
```

---

## 🎨 Customization

### Add New Commands

Edit `main.py` chat loop to add custom commands:

```python
elif user_input == "/mycommand":
    # Your logic here
    console.print("[cyan]Command executed![/cyan]")
```

### Change Whisper Model

Edit `voice.py` to use different models:

```python
WHISPER_MODEL = "base"  # Options: tiny, base, small, medium, large
```

Larger models = better accuracy but slower.

---

## 🐛 Troubleshooting

### "No API key found"
- Check `.env` file exists in project root
- Verify at least one API key is set
- Restart after adding keys

### "Microphone not available"
- Check microphone permissions
- Test mic in other apps first
- On Windows: Check Privacy Settings → Microphone

### "TTS not working"
- pyttsx3 should work by default on Windows
- On Linux: `sudo apt-get install espeak`
- On Mac: Built-in TTS should work

### "Import errors"
- Run: `pip install -r requirements.txt`
- On Windows: pyaudio may need: `pip install pipwin && pipwin install pyaudio`

---

## 📦 Dependencies

- **AI APIs**: groq, google-generativeai, together, mistralai
- **Voice**: openai-whisper, pyaudio
- **TTS**: pyttsx3
- **Memory**: chromadb, sentence-transformers
- **UI**: rich
- **Utils**: python-dotenv, tiktoken

---

## 🔒 Privacy

- **Local First**: Voice transcription, TTS, and vector DB run locally
- **No Data Collection**: Conversation logs stay on your machine
- **API Keys**: Only used for LLM inference (Groq/Gemini/etc)
- **Offline Capable**: Everything works offline except AI responses

---

## 🛣️ Roadmap

- [ ] Daily journal system
- [ ] Personal knowledge base
- [ ] Learning companion with quizzes
- [ ] Task/reminder system
- [ ] Telegram bot integration
- [ ] Web search integration
- [ ] Multi-language support

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repo
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📄 License

MIT License - feel free to use, modify, and distribute.

---

## 🙏 Acknowledgments

Built with:
- [OpenAI Whisper](https://github.com/openai/whisper) - Voice transcription
- [ChromaDB](https://www.trychroma.com/) - Vector database
- [pyttsx3](https://github.com/nateshmbhat/pyttsx3) - Text-to-speech
- [Rich](https://github.com/Textualize/rich) - Terminal UI

---

## 📧 Support

Issues? Questions? Open an issue on GitHub or reach out!

---

**Built with ❤️ for developers who want a truly personal AI assistant.**
