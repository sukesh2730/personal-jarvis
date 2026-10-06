"""
Audio Feedback System for JARVIS - Phase 4
Sound effect system for key events using pygame mixer.
"""
import os
from pathlib import Path
from typing import Optional


class AudioFeedback:
    """Manages audio feedback for system events."""
    
    def __init__(self, sounds_dir: str = "./sounds"):
        """
        Initialize pygame mixer.
        
        Args:
            sounds_dir: Directory containing sound files
        """
        self.sounds_dir = sounds_dir
        self.enabled = True
        self.volume = 70  # 0-100
        self.mixer_initialized = False
        
        # Try to initialize pygame mixer
        try:
            import pygame
            pygame.mixer.init()
            self.mixer_initialized = True
            self.pygame = pygame
        except ImportError:
            # pygame not available
            self.enabled = False
        except Exception:
            # Mixer initialization failed (no audio device, etc.)
            self.enabled = False
        
        # Create sounds directory if it doesn't exist
        Path(sounds_dir).mkdir(parents=True, exist_ok=True)
    
    def play(self, sound_name: str) -> bool:
        """
        Play a sound file.
        
        Args:
            sound_name: Name of sound file (without extension)
            
        Returns:
            True if played successfully, False otherwise
        """
        if not self.enabled or not self.mixer_initialized:
            return False
        
        # Try different audio formats
        formats = ['.wav', '.mp3', '.ogg']
        sound_path = None
        
        for fmt in formats:
            test_path = os.path.join(self.sounds_dir, f"{sound_name}{fmt}")
            if os.path.exists(test_path):
                sound_path = test_path
                break
        
        if not sound_path:
            # Sound file doesn't exist, fail silently
            return False
        
        try:
            # Load and play sound
            sound = self.pygame.mixer.Sound(sound_path)
            sound.set_volume(self.volume / 100.0)
            sound.play()
            return True
        except Exception:
            # Failed to play, fail silently
            return False
    
    def set_volume(self, level: int) -> bool:
        """
        Set volume (0-100).
        
        Args:
            level: Volume level (0-100)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            return False
        
        # Clamp volume to 0-100
        self.volume = max(0, min(100, level))
        return True
    
    def toggle(self) -> bool:
        """
        Toggle audio on/off.
        
        Returns:
            New enabled state
        """
        if self.mixer_initialized:
            self.enabled = not self.enabled
        return self.enabled
    
    def get_status(self) -> str:
        """
        Get audio system status.
        
        Returns:
            Status message
        """
        if not self.mixer_initialized:
            return "Audio system unavailable (pygame not installed or no audio device)"
        elif self.enabled:
            return f"Audio enabled, volume: {self.volume}%"
        else:
            return "Audio disabled"


# Sound file placeholders - these should be replaced with actual audio files
SOUND_DESCRIPTIONS = {
    "startup": "Power-up chime (1 sec) - plays when JARVIS initializes",
    "command": "Acknowledgment beep (0.3 sec) - plays when command recognized",
    "error": "Warning tone (0.5 sec) - plays on exceptions",
    "notification": "Gentle ping (0.4 sec) - plays for background task completions",
    "focus_start": "Focus begin tone - plays when focus mode starts",
    "focus_end": "Focus complete tone - plays when focus mode completes"
}


def create_sound_placeholders(sounds_dir: str = "./sounds"):
    """
    Create placeholder text files for sound effects.
    
    Args:
        sounds_dir: Directory to create placeholders in
    """
    Path(sounds_dir).mkdir(parents=True, exist_ok=True)
    
    readme_path = os.path.join(sounds_dir, "README.txt")
    
    with open(readme_path, 'w') as f:
        f.write("JARVIS Audio Feedback System\n")
        f.write("=" * 50 + "\n\n")
        f.write("Place audio files in this directory:\n\n")
        
        for sound_name, description in SOUND_DESCRIPTIONS.items():
            f.write(f"{sound_name}.wav - {description}\n")
        
        f.write("\n" + "=" * 50 + "\n")
        f.write("Supported formats: .wav, .mp3, .ogg\n")
        f.write("Audio files are optional. JARVIS will work without them.\n")
        f.write("\nFree sound effects can be found at:\n")
        f.write("- https://freesound.org/\n")
        f.write("- https://mixkit.co/free-sound-effects/\n")
        f.write("- https://soundbible.com/\n")


def check_audio_available() -> bool:
    """
    Check if audio system is available.
    
    Returns:
        True if pygame and audio device available
    """
    try:
        import pygame
        pygame.mixer.init()
        return True
    except:
        return False
