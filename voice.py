"""Voice input for ROME JARVIS using Whisper."""
import os
import tempfile
import wave
import pyaudio
import whisper
from pathlib import Path
from rich.console import Console

console = Console()

# Configuration
WHISPER_MODEL = "base"
RECORD_SECONDS_MAX = 15
SAMPLE_RATE = 16000
CHANNELS = 1
CHUNK = 1024

# Cache model globally
_model = None


def load_whisper():
    """Load Whisper model once, reuse it."""
    global _model
    if _model is None:
        console.print("[dim]Loading Whisper model...[/dim]")
        _model = whisper.load_model(WHISPER_MODEL)
        console.print("[green][Voice] Ready.[/green]")
    return _model


def record_audio(seconds=5):
    """Record audio from microphone."""
    try:
        p = pyaudio.PyAudio()
        stream = p.open(
            format=pyaudio.paInt16,
            channels=CHANNELS,
            rate=SAMPLE_RATE,
            input=True,
            frames_per_buffer=CHUNK
        )
        
        console.print(f"[yellow][Recording] Speak now... ({seconds} seconds)[/yellow]")
        frames = []
        
        for _ in range(0, int(SAMPLE_RATE / CHUNK * seconds)):
            data = stream.read(CHUNK)
            frames.append(data)
        
        stream.stop_stream()
        stream.close()
        p.terminate()
        
        # Save to temp file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        temp_path = temp_file.name
        temp_file.close()
        
        wf = wave.open(temp_path, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        
        return temp_path
    except Exception as e:
        console.print(f"[red][Voice Error] {str(e)}[/red]")
        return None


def transcribe(audio_path):
    """Convert audio file to text using Whisper."""
    try:
        model = load_whisper()
        result = model.transcribe(audio_path)
        text = result["text"].strip()
        
        if text:
            console.print(f"[green][Heard][/green] {text}")
        
        # Delete temp file
        try:
            os.remove(audio_path)
        except:
            pass
        
        return text if text else None
    except Exception as e:
        console.print(f"[red][Voice Error] {str(e)}[/red]")
        return None


def listen(seconds=5):
    """Full pipeline — record then transcribe."""
    audio_path = record_audio(seconds)
    if audio_path is None:
        return None
    return transcribe(audio_path)


def is_voice_available():
    """Check if mic and dependencies exist."""
    try:
        import pyaudio
        import whisper
        p = pyaudio.PyAudio()
        p.terminate()
        return True
    except:
        return False
