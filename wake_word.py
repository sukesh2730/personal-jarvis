"""
Wake word detection for ROME JARVIS using Picovoice Porcupine.
Listens passively for "Hey JARVIS" trigger phrase.
"""
import os
import struct
import pyaudio
import threading
from rich.console import Console

console = Console()

# Global flag to control wake word detection
_detection_active = False
_detection_thread = None


def init_porcupine():
    """
    Initialize Porcupine wake word engine.
    Returns porcupine instance and audio stream, or None if failed.
    """
    try:
        import pvporcupine
        
        access_key = os.getenv("PICOVOICE_ACCESS_KEY")
        if not access_key or access_key == "your_picovoice_key_here":
            console.print("[yellow]Warning: PICOVOICE_ACCESS_KEY not set. Wake word disabled.[/yellow]")
            console.print("[dim]Get free key at: https://console.picovoice.ai/[/dim]")
            return None, None
        
        # Initialize Porcupine with "jarvis" keyword
        porcupine = pvporcupine.create(
            access_key=access_key,
            keywords=["jarvis"]  # Built-in wake word
        )
        
        # Initialize audio stream
        pa = pyaudio.PyAudio()
        audio_stream = pa.open(
            rate=porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=porcupine.frame_length
        )
        
        console.print("[dim]Wake word: Listening for 'Hey JARVIS'...[/dim]")
        return porcupine, audio_stream
        
    except ImportError:
        console.print("[yellow]pvporcupine not installed. Wake word disabled.[/yellow]")
        console.print("[dim]Install: pip install pvporcupine[/dim]")
        return None, None
    except Exception as e:
        console.print(f"[yellow]Wake word init failed: {e}[/yellow]")
        return None, None


def listen_for_wake_word(on_wake_callback):
    """
    Background thread that listens for wake word.
    
    Args:
        on_wake_callback: Function to call when wake word detected
    """
    global _detection_active
    
    porcupine, audio_stream = init_porcupine()
    if not porcupine or not audio_stream:
        return
    
    _detection_active = True
    
    try:
        while _detection_active:
            # Read audio frame
            pcm = audio_stream.read(porcupine.frame_length, exception_on_overflow=False)
            pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)
            
            # Check for wake word
            keyword_index = porcupine.process(pcm)
            
            if keyword_index >= 0:
                # Wake word detected!
                console.print("[green]Wake word detected![/green]")
                on_wake_callback()
                
    except KeyboardInterrupt:
        pass
    except Exception as e:
        console.print(f"[red]Wake word error: {e}[/red]")
    finally:
        if audio_stream:
            audio_stream.close()
        if porcupine:
            porcupine.delete()


def start_wake_word_detection(on_wake_callback):
    """
    Start wake word detection in background thread.
    
    Args:
        on_wake_callback: Function to call when "Hey JARVIS" is detected
    """
    global _detection_thread
    
    if _detection_thread and _detection_thread.is_alive():
        return
    
    _detection_thread = threading.Thread(
        target=listen_for_wake_word,
        args=(on_wake_callback,),
        daemon=True
    )
    _detection_thread.start()


def stop_wake_word_detection():
    """Stop wake word detection."""
    global _detection_active
    _detection_active = False


def is_wake_word_active():
    """Check if wake word detection is running."""
    return _detection_active
