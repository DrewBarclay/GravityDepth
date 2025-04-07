import pygame
import os
import random
import math
import tempfile
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

        # Rain sound path - will be generated at startup
        self.rain_path = os.path.join(self.audio_dir, 'rain_ambient.wav')

        # State tracking
        self.music_playing = False
        self.rain_ambience_playing = False
        self.rain_ambience_channel = None

        # Sound effect cache
        self.sound_effects: Dict[str, pygame.mixer.Sound] = {}

        # Initialize sound effects
        self._initialize_sound_effects()

        # Cooldown timers for sound effects (to prevent sound spam)
        self.sound_cooldowns = {
            'player_hit': 0,
            'enemy_hit': 0,
            'env_collision': 0,
            'portal': 0,
            'game_over': 0
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
        env_collision.set_volume(0.2)  # Increased from 0.05 to be more noticeable
        self.sound_effects['env_collision'] = env_collision

        # 4. Portal transition sound - magical ascending tone
        portal_sound = pygame.mixer.Sound(buffer=self._generate_portal_sound())
        portal_sound.set_volume(0.4)
        self.sound_effects['portal'] = portal_sound

        # 5. Game over sound - dramatic downward sweep
        game_over_sound = pygame.mixer.Sound(buffer=self._generate_game_over_sound())
        game_over_sound.set_volume(0.5)
        self.sound_effects['game_over'] = game_over_sound

        # 6. Rain ambience sound - load/generate once at startup
        self._initialize_rain_ambience()

    def _initialize_rain_ambience(self) -> None:
        """Initialize rain ambience by loading from file or using a simple fallback"""
        # Try to load the rain sound file
        try:
            if os.path.exists(self.rain_path):
                rain_ambience = pygame.mixer.Sound(self.rain_path)
                rain_ambience.set_volume(0.25)
                self.sound_effects['rain_ambience'] = rain_ambience
                print("Rain ambience sound loaded from file")
            else:
                # If file doesn't exist, use the simple fallback
                print("Rain sound file not found, using fallback sound")
                rain_ambience = pygame.mixer.Sound(buffer=self._generate_simple_rain_sound())
                rain_ambience.set_volume(0.25)
                self.sound_effects['rain_ambience'] = rain_ambience
        except pygame.error as e:
            print(f"Error loading rain sound: {e}")
            # Fallback to simpler rain sound if loading fails
            print("Using fallback simple rain sound")
            rain_ambience = pygame.mixer.Sound(buffer=self._generate_simple_rain_sound())
            rain_ambience.set_volume(0.25)
            self.sound_effects['rain_ambience'] = rain_ambience

    def _generate_simple_rain_sound(self) -> bytes:
        """Generate a simple version of rain sound for fallback"""
        sample_rate = 22050  # Lower sample rate for faster generation
        duration = 5.0
        samples = int(sample_rate * duration)

        # Create a buffer with signed 16-bit samples
        buffer = bytearray(samples * 2)

        # Simple filtered noise for rain
        last_value = 0
        alpha = 0.1  # Simple low-pass filter constant

        for i in range(samples):
            t = i / sample_rate

            # Simple noise with filtering
            noise = random.uniform(-1, 1)
            filtered = alpha * noise + (1 - alpha) * last_value
            last_value = filtered

            # Add some variations
            intensity = 0.7 + 0.3 * math.sin(2 * math.pi * 0.2 * t)
            value = int(32767 * 0.7 * filtered * intensity)

            # Apply fade in/out
            if t < 0.3:
                value = int(value * (t / 0.3))
            elif t > duration - 0.3:
                value = int(value * ((duration - t) / 0.3))

            # Convert to 16-bit signed PCM
            buffer[i*2] = value & 0xFF
            buffer[i*2+1] = (value >> 8) & 0xFF

        return bytes(buffer)

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
        """Generate a distinctive sound for projectile deflection/destruction"""
        sample_rate = 22050
        duration = 0.2  # slightly longer for more presence
        samples = int(sample_rate * duration)

        # Create a buffer with signed 16-bit samples
        buffer = bytearray(samples * 2)

        # Generate a distinctive "zap/ping" sound for projectile deflection
        for i in range(samples):
            t = i / sample_rate
            # Start with higher frequency and descend quickly for a "ping" effect
            freq = 600 + 400 * math.exp(-8 * t / duration)

            # Add harmonics and slight phase modulation for more character
            value = int(32767 * 0.7 * (
                0.7 * math.sin(2 * math.pi * freq * t) +
                0.2 * math.sin(2 * math.pi * freq * 2 * t + 0.5 * math.sin(10 * t)) +
                0.1 * math.sin(2 * math.pi * freq * 3 * t)
            ))

            # Apply envelope - quick attack, longer decay for more presence
            envelope = min(t * 40, 1.0) * math.exp(-5 * t / duration)
            value = int(value * envelope)

            # Convert to 16-bit signed PCM
            buffer[i*2] = value & 0xFF
            buffer[i*2+1] = (value >> 8) & 0xFF

        return bytes(buffer)

    def _generate_portal_sound(self) -> bytes:
        """Generate a magical portal transition sound"""
        sample_rate = 22050
        duration = 0.75  # seconds - medium length
        samples = int(sample_rate * duration)

        # Create a buffer with signed 16-bit samples
        buffer = bytearray(samples * 2)

        # Generate an ascending magical tone
        for i in range(samples):
            t = i / sample_rate

            # Start at 300Hz and rise to 2000Hz with a slight curve
            freq = 300 + 1700 * (t / duration)**1.5

            # Mix three harmonics with phasing
            value = int(32767 * 0.7 * (
                0.6 * math.sin(2 * math.pi * freq * t) +
                0.3 * math.sin(2 * math.pi * freq * 1.5 * t) +
                0.1 * math.sin(2 * math.pi * freq * 2 * t + 0.5 * math.sin(3 * t))
            ))

            # Apply bell-shaped envelope
            envelope = math.sin(math.pi * t / duration)
            value = int(value * envelope)

            # Convert to 16-bit signed PCM
            buffer[i*2] = value & 0xFF
            buffer[i*2+1] = (value >> 8) & 0xFF

        return bytes(buffer)

    def _generate_game_over_sound(self) -> bytes:
        """Generate a dramatic game over sound"""
        sample_rate = 22050
        duration = 1.2  # seconds - longer for dramatic effect
        samples = int(sample_rate * duration)

        # Create a buffer with signed 16-bit samples
        buffer = bytearray(samples * 2)

        # Generate a dramatic descending sound
        for i in range(samples):
            t = i / sample_rate

            # Dramatic descending frequency sweep
            freq = 800 - 700 * (t / duration)**0.6

            # Add intensity with harmonics and noise
            primary = math.sin(2 * math.pi * freq * t)
            harmonic1 = 0.3 * math.sin(2 * math.pi * freq * 0.5 * t)
            harmonic2 = 0.2 * math.sin(2 * math.pi * freq * 0.25 * t)

            # Add some noise that increases over time for dramatic effect
            noise_amount = 0.1 * (t / duration)**2
            noise = noise_amount * random.uniform(-1, 1)

            # Combine components
            combined = 0.8 * primary + harmonic1 + harmonic2 + noise

            # Start loud and then fade
            envelope = 1.0 if t < 0.1 else math.pow(1.0 - ((t - 0.1) / (duration - 0.1)), 1.2)

            value = int(32767 * combined * envelope)

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

        # Start rain ambience on a different channel
        self.play_rain_ambience()

    def stop_music(self) -> None:
        """Stop the currently playing music"""
        pygame.mixer.music.stop()
        self.music_playing = False
        self.stop_rain_ambience()

    def is_music_playing(self) -> bool:
        """Check if music is currently playing"""
        return pygame.mixer.music.get_busy()

    def set_music_volume(self, volume: float) -> None:
        """Set the music volume (0.0 to 1.0)"""
        pygame.mixer.music.set_volume(volume)

    def play_rain_ambience(self, loops: int = -1) -> None:
        """Play the rain ambience sound on a separate channel"""
        if 'rain_ambience' not in self.sound_effects:
            return

        # Use a dedicated channel for the rain sound
        try:
            self.rain_ambience_channel = pygame.mixer.Channel(7)  # Use channel 7 for rain (0-7 available by default)

            if self.rain_ambience_channel and not self.rain_ambience_playing:
                print("Starting rain ambience...")
                self.rain_ambience_channel.play(self.sound_effects['rain_ambience'], loops=loops)
                self.rain_ambience_playing = True
        except pygame.error as e:
            print(f"Error playing rain ambience: {e}")
            # Try to use a different channel if channel 7 is not available
            try:
                fallback_channel = pygame.mixer.find_channel()
                if fallback_channel:
                    fallback_channel.play(self.sound_effects['rain_ambience'], loops=loops)
                    self.rain_ambience_channel = fallback_channel
                    self.rain_ambience_playing = True
            except:
                print("Could not find any available channel for rain ambience.")

    def stop_rain_ambience(self) -> None:
        """Stop the rain ambience sound"""
        if self.rain_ambience_channel:
            self.rain_ambience_channel.stop()
            self.rain_ambience_playing = False

    def set_rain_ambience_volume(self, volume: float) -> None:
        """Set the rain ambience volume (0.0 to 1.0)"""
        if self.rain_ambience_channel:
            self.rain_ambience_channel.set_volume(volume)

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

    def play_portal_sound(self) -> None:
        """Play sound for portal transition"""
        # Check cooldown to prevent sound spam
        current_time = pygame.time.get_ticks()
        if current_time - self.sound_cooldowns['portal'] > 500:  # 500ms cooldown
            self.sound_effects['portal'].play()
            self.sound_cooldowns['portal'] = current_time

    def play_game_over_sound(self) -> None:
        """Play sound for game over"""
        # Check cooldown to prevent sound spam
        current_time = pygame.time.get_ticks()
        if current_time - self.sound_cooldowns['game_over'] > 1000:  # 1000ms cooldown
            self.sound_effects['game_over'].play()
            self.sound_cooldowns['game_over'] = current_time