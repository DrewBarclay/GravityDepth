import pygame
import os
import random
from typing import List, Optional

class AudioSystem:
    """Audio system for handling music and sound effects"""

    def __init__(self):
        """Initialize the audio system"""
        # Make sure pygame mixer is initialized
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

        # Create a directory for audio files if it doesn't exist
        self.audio_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'audio')
        os.makedirs(self.audio_dir, exist_ok=True)

        # Path to the assets directory
        self.assets_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets')

        # Theme music path
        self.theme_path = os.path.join(self.assets_dir, 'theme.wav')

        # State tracking
        self.music_playing = False

    def generate_theme(self) -> None:
        """This method is kept for compatibility, but now we use a pre-generated theme"""
        # Check if theme file exists
        if not os.path.exists(self.theme_path):
            print(f"Warning: Theme file not found at {self.theme_path}")

    def play_music(self, loops: int = -1) -> None:
        """Play background music on loop"""
        try:
            # Don't restart if music is already playing
            if pygame.mixer.music.get_busy():
                return

            print("Starting background music...")

            # Load and play the pre-generated theme music
            if os.path.exists(self.theme_path):
                pygame.mixer.music.load(self.theme_path)
                pygame.mixer.music.play(loops=loops)
                self.music_playing = True
            else:
                print(f"Error: Theme file not found at {self.theme_path}")
        except pygame.error as e:
            print(f"Error playing music: {e}")

    def stop_music(self) -> None:
        """Stop the currently playing music"""
        pygame.mixer.music.stop()
        self.music_playing = False

    def is_music_playing(self) -> bool:
        """Check if music is currently playing"""
        return pygame.mixer.music.get_busy()

    def set_music_volume(self, volume: float) -> None:
        """Set the music volume (0.0 to 1.0)"""
        pygame.mixer.music.set_volume(volume)