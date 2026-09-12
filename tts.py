"""Local text-to-speech for ROME JARVIS using pyttsx3."""
import re
import threading
import pyttsx3
from rich.console import Console

console = Console()

# Global TTS engine (initialized once)
_engine = None
_tts_enabled = False


def init_tts():
    """Initialize pyttsx3 engine once."""
    global _engine
    if _engine is None:
        try:
            _engine = pyttsx3.init()
            _engine.setProperty('rate', 175)  # Speed (words per minute)
            _engine.setProperty('volume', 0.9)  # Volume (0.0 to 1.0)
            return True
        except Exception as e:
            console.print(f"[red][TTS Error] Could not initialize: {e}[/red]")
            return False
    return True


def is_tts_available():
    """Check if TTS engine can be initialized."""
    try:
        engine = pyttsx3.init()
        engine.stop()
        del engine
        return True
    except:
        return False


def strip_markdown(text):
    """Remove markdown syntax from text before speaking."""
    # Remove bold/italic markers
    text = re.sub(r'\*\*\*(.+?)\*\*\*', r'\1', text)  # ***bold italic***
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)      # **bold**
    text = re.sub(r'\*(.+?)\*', r'\1', text)          # *italic*
    text = re.sub(r'__(.+?)__', r'\1', text)          # __bold__
    text = re.sub(r'_(.+?)_', r'\1', text)            # _italic_
    
    # Remove headers
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    
    # Remove code blocks
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    text = re.sub(r'`(.+?)`', r'\1', text)
    
    # Remove links [text](url)
    text = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', text)
    
    # Remove bullet points
    text = re.sub(r'^[\-\*\+]\s+', '', text, flags=re.MULTILINE)
    
    # Remove extra whitespace
    text = re.sub(r'\n+', '. ', text)
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()


def speak_async(text):
    """Speak text asynchronously without blocking."""
    def _speak():
        try:
            if _engine and _tts_enabled:
                clean_text = strip_markdown(text)
                if clean_text:
                    _engine.say(clean_text)
                    _engine.runAndWait()
        except Exception as e:
            console.print(f"[red][TTS Error] {e}[/red]")
    
    # Run in separate thread to avoid blocking
    thread = threading.Thread(target=_speak, daemon=True)
    thread.start()


def speak(text):
    """Speak text synchronously (blocking)."""
    try:
        if _engine:
            clean_text = strip_markdown(text)
            if clean_text:
                _engine.say(clean_text)
                _engine.runAndWait()
    except Exception as e:
        console.print(f"[red][TTS Error] {e}[/red]")


def enable_tts():
    """Enable TTS mode."""
    global _tts_enabled
    if init_tts():
        _tts_enabled = True
        return True
    return False


def disable_tts():
    """Disable TTS mode."""
    global _tts_enabled
    _tts_enabled = False


def is_enabled():
    """Check if TTS is currently enabled."""
    return _tts_enabled


def stop():
    """Stop any ongoing speech."""
    try:
        if _engine:
            _engine.stop()
    except:
        pass
