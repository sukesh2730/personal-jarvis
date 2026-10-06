"""
Hands-free conversation loop for ROME JARVIS.
Uses Voice Activity Detection (VAD) for natural turn-taking.
"""
import wave
import struct
import pyaudio
import webrtcvad
from rich.console import Console

console = Console()

# Conversation state
_in_conversation = False


def detect_speech_end(audio_stream, vad, sample_rate=16000, frame_duration=30):
    """
    Listen for speech and detect when user stops talking.
    Uses WebRTC VAD with 1.5s silence threshold.
    
    Args:
        audio_stream: PyAudio stream
        vad: webrtcvad.Vad instance
        sample_rate: Audio sample rate (16kHz for VAD)
        frame_duration: Frame duration in ms (10, 20, or 30)
    
    Returns:
        bytes: Recorded audio data, or None if cancelled
    """
    frame_size = int(sample_rate * frame_duration / 1000)
    silence_threshold = 1.5  # seconds of silence = user finished
    silence_frames_needed = int(silence_threshold * 1000 / frame_duration)
    
    frames = []
    silence_count = 0
    speech_started = False
    
    console.print("[cyan]Listening... (speak now)[/cyan]")
    
    try:
        while True:
            # Read audio frame
            frame = audio_stream.read(frame_size, exception_on_overflow=False)
            frames.append(frame)
            
            # Check if frame contains speech
            is_speech = vad.is_speech(frame, sample_rate)
            
            if is_speech:
                speech_started = True
                silence_count = 0
            elif speech_started:
                silence_count += 1
                
                # User stopped talking
                if silence_count >= silence_frames_needed:
                    console.print("[dim]Processing...[/dim]")
                    return b''.join(frames)
    
    except KeyboardInterrupt:
        return None
    except Exception as e:
        console.print(f"[red]VAD error: {e}[/red]")
        return None


def transcribe_audio(audio_data, sample_rate=16000):
    """
    Transcribe audio using Whisper.
    
    Args:
        audio_data: Raw audio bytes
        sample_rate: Sample rate
    
    Returns:
        str: Transcribed text, or None if failed
    """
    try:
        import whisper
        import tempfile
        import numpy as np
        
        # Convert bytes to numpy array
        audio_array = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
        
        # Load Whisper model (cached after first load)
        model = whisper.load_model("base")
        
        # Transcribe
        result = model.transcribe(audio_array, fp16=False)
        text = result["text"].strip()
        
        if text:
            console.print(f"[green][Heard][/green] {text}")
            return text
        return None
        
    except Exception as e:
        console.print(f"[red]Transcription error: {e}[/red]")
        return None


def check_exit_phrase(text):
    """
    Check if user wants to exit conversation.
    
    Args:
        text: Transcribed text
    
    Returns:
        bool: True if exit phrase detected
    """
    text_lower = text.lower()
    exit_phrases = [
        "goodbye jarvis",
        "that's all",
        "that is all",
        "thanks jarvis",
        "thank you jarvis",
        "exit conversation",
        "stop conversation"
    ]
    
    return any(phrase in text_lower for phrase in exit_phrases)


def start_conversation():
    """
    Enter hands-free conversation loop.
    Uses VAD to detect when user stops speaking.
    """
    global _in_conversation
    
    try:
        # Initialize VAD
        vad = webrtcvad.Vad(3)  # Aggressiveness 0-3, 3 = most aggressive
        
        # Initialize audio
        pa = pyaudio.PyAudio()
        sample_rate = 16000
        audio_stream = pa.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=sample_rate,
            input=True,
            frames_per_buffer=480  # 30ms at 16kHz
        )
        
        _in_conversation = True
        console.print("[bold green]Conversation mode activated, sir.[/bold green]")
        console.print("[dim]Say 'goodbye JARVIS' or 'that's all' to exit[/dim]\n")
        
        # Import here to avoid circular dependency
        from api_router import get_completion
        from tts import speak
        
        while _in_conversation:
            # Listen with VAD
            audio_data = detect_speech_end(audio_stream, vad, sample_rate)
            
            if not audio_data:
                break
            
            # Transcribe
            text = transcribe_audio(audio_data, sample_rate)
            
            if not text:
                continue
            
            # Check for exit
            if check_exit_phrase(text):
                console.print("[yellow]Ending conversation...[/yellow]")
                speak("Of course, sir. Standing by.")
                break
            
            # Get AI response
            try:
                response = get_completion(text)
                console.print(f"[green]JARVIS:[/green] {response}\n")
                
                # Speak response
                speak(response)
                
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
                speak("My apologies, sir. I encountered an error processing that request.")
        
        # Cleanup
        audio_stream.stop_stream()
        audio_stream.close()
        pa.terminate()
        _in_conversation = False
        
        console.print("[dim]Conversation mode deactivated.[/dim]")
        
    except ImportError:
        console.print("[red]webrtcvad not installed. Cannot start conversation mode.[/red]")
        console.print("[dim]Install: pip install webrtcvad[/dim]")
    except Exception as e:
        console.print(f"[red]Conversation error: {e}[/red]")
        _in_conversation = False


def stop_conversation():
    """Stop conversation loop."""
    global _in_conversation
    _in_conversation = False


def is_in_conversation():
    """Check if currently in conversation mode."""
    return _in_conversation
