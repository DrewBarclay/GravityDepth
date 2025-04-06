import pygame
import os
import random
import math
from typing import List, Optional, Dict

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

        # Sound effect cache
        self.sound_effects: Dict[str, pygame.mixer.Sound] = {}

        # Initialize sound effects
        self._initialize_sound_effects()

        # Cooldown timers for sound effects (to prevent sound spam)
        self.sound_cooldowns = {
            'player_hit': 0,
            'enemy_hit': 0,
            'env_collision': 0
        }

    def _initialize_sound_effects(self) -> None:
        """Initialize sound effects - create them programmatically"""
        # 1. Player hit sound - a medium pitched "ouch" sound
        player_hit = pygame.mixer.Sound(buffer=self._generate_player_hit_sound())
        player_hit.set_volume(0.3)
        self.sound_effects['player_hit'] = player_hit

        # 2. Enemy hit sound - higher pitched "splat" sound
        enemy_hit = pygame.mixer.Sound(buffer=self._generate_enemy_hit_sound())
        enemy_hit.set_volume(0.3)
        self.sound_effects['enemy_hit'] = enemy_hit

        # 3. Environment collision - low "thud" sound
        env_collision = pygame.mixer.Sound(buffer=self._generate_env_collision_sound())
        env_collision.set_volume(0.1)  # Very quiet
        self.sound_effects['env_collision'] = env_collision

    def _generate_player_hit_sound(self) -> bytes:
        """Generate a sound for when player gets hit"""
        sample_rate = 22050
        duration = 0.3  # seconds
        samples = int(sample_rate * duration)

        # Create a buffer with signed 16-bit samples
        buffer = bytearray(samples * 2)

        # Generate a medium-pitched descending tone with some distortion
        for i in range(samples):
            t = i / sample_rate
            # Start at 440Hz and go down to 220Hz
            freq = 440 - (220 * t / duration)
            # Add some distortion for "pain" effect
            value = int(32767 * 0.8 * (
                0.7 * math.sin(2 * math.pi * freq * t) +
                0.3 * math.sin(2 * math.pi * freq * 1.5 * t * (1 - t * 2))
            ))
            # Apply envelope
            envelope = 1.0 if t < 0.05 else 1.0 - (t - 0.05) / (duration - 0.05)
            value = int(value * envelope)

            # Convert to 16-bit signed PCM
            buffer[i*2] = value & 0xFF
            buffer[i*2+1] = (value >> 8) & 0xFF

        return bytes(buffer)

    def _generate_enemy_hit_sound(self) -> bytes:
        """Generate a sound for when an enemy gets hit"""
        sample_rate = 22050
        duration = 0.25  # seconds
        samples = int(sample_rate * duration)

        # Create a buffer with signed 16-bit samples
        buffer = bytearray(samples * 2)

        # Generate a high-pitched "splat" sound
        for i in range(samples):
            t = i / sample_rate
            # Higher frequency for enemy hit
            freq = 880 - (700 * t / duration)
            # More chaotic sound for destruction effect
            value = int(32767 * 0.8 * (
                0.5 * math.sin(2 * math.pi * freq * t) +
                0.3 * math.sin(4 * math.pi * freq * t) +
                0.2 * random.uniform(-1, 1) * (1 - t/duration)  # Noise that fades out
            ))
            # Apply envelope - quick attack, medium decay
            envelope = min(t * 20, 1.0) * (1.0 - t/duration)
            value = int(value * envelope)

            # Convert to 16-bit signed PCM
            buffer[i*2] = value & 0xFF
            buffer[i*2+1] = (value >> 8) & 0xFF

        return bytes(buffer)

    def _generate_env_collision_sound(self) -> bytes:
        """Generate a subtle sound for environment object collisions"""
        sample_rate = 22050
        duration = 0.15  # seconds - very short
        samples = int(sample_rate * duration)

        # Create a buffer with signed 16-bit samples
        buffer = bytearray(samples * 2)

        # Generate a low "thud" sound
        for i in range(samples):
            t = i / sample_rate
            # Low frequency for thud
            freq = 80 + (30 * t / duration)
            # Simple sine wave with slight distortion
            value = int(32767 * 0.5 * (
                0.9 * math.sin(2 * math.pi * freq * t) +
                0.1 * math.sin(2 * math.pi * freq * 2 * t)
            ))
            # Apply envelope - fast attack, quick decay
            envelope = min(t * 30, 1.0) * (1.0 - t/duration)**2
            value = int(value * envelope)

            # Convert to 16-bit signed PCM
            buffer[i*2] = value & 0xFF
            buffer[i*2+1] = (value >> 8) & 0xFF

        return bytes(buffer)

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
                self.set_music_volume(0.2)
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

    def play_player_hit_sound(self) -> None:
        """Play sound for when player gets hit"""
        # Check cooldown to prevent sound spam
        current_time = pygame.time.get_ticks()
        if current_time - self.sound_cooldowns['player_hit'] > 300:  # 300ms cooldown
            self.sound_effects['player_hit'].play()
            self.sound_cooldowns['player_hit'] = current_time

    def play_enemy_hit_sound(self) -> None:
        """Play sound for when enemy gets hit"""
        # Check cooldown to prevent sound spam
        current_time = pygame.time.get_ticks()
        if current_time - self.sound_cooldowns['enemy_hit'] > 200:  # 200ms cooldown
            self.sound_effects['enemy_hit'].play()
            self.sound_cooldowns['enemy_hit'] = current_time

    def play_env_collision_sound(self) -> None:
        """Play sound for environment object collisions"""
        # Check cooldown to prevent sound spam
        current_time = pygame.time.get_ticks()
        if current_time - self.sound_cooldowns['env_collision'] > 100:  # 100ms cooldown
            self.sound_effects['env_collision'].play()
            self.sound_cooldowns['env_collision'] = current_time