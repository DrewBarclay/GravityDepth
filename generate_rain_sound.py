#!/usr/bin/env python3
"""
Script to generate a high-quality rain sound file.
Run this once to create the file, which will then be loaded by the game.
"""

import os
import random
import math
import pygame
import tempfile
import time
import wave
import struct
import array

def main():
    print("Generating high-quality rain sound...")
    start_time = time.time()

    # Initialize pygame mixer
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

    # Create the audio directory if it doesn't exist
    audio_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'audio')
    os.makedirs(audio_dir, exist_ok=True)

    # Output file path
    rain_path = os.path.join(audio_dir, 'rain_ambient.wav')

    # Generate the rain sound data
    sound_buffer = generate_rain_ambience_sound()

    # Save sound data to WAV file
    try:
        # Convert buffer to proper format for WAV file
        sample_rate = 44100
        save_wav_file(rain_path, sound_buffer, sample_rate)

        end_time = time.time()
        print(f"Rain sound saved to {rain_path}")
        print(f"Generation took {end_time - start_time:.2f} seconds")
    except Exception as e:
        print(f"Error saving rain sound: {e}")

def save_wav_file(filename, sound_buffer, sample_rate):
    """Save sound buffer to WAV file"""
    # Each sample in sound_buffer is two bytes (16-bit)
    # Extract samples as 16-bit integers
    samples = []
    for i in range(0, len(sound_buffer), 2):
        sample = sound_buffer[i] | (sound_buffer[i+1] << 8)
        # Convert from unsigned to signed
        if sample > 32767:
            sample -= 65536
        samples.append(sample)

    # Create WAV file
    with wave.open(filename, 'wb') as wav_file:
        # Set parameters: nchannels, sampwidth, framerate, nframes, comptype, compname
        wav_file.setparams((1, 2, sample_rate, len(samples), 'NONE', 'not compressed'))

        # Convert samples to bytes
        sample_data = array.array('h', samples)
        wav_file.writeframes(sample_data.tobytes())

def generate_rain_ambience_sound() -> bytes:
    """Generate a realistic rain ambience sound"""
    print("Generating high-quality rain sound - this may take a moment...")
    sample_rate = 44100  # Higher sample rate for better quality
    # Create a longer sound for better looping
    duration = 10.0  # seconds
    samples = int(sample_rate * duration)

    # Create a buffer with signed 16-bit samples
    buffer = bytearray(samples * 2)

    # For a realistic rain sound, we need several components:
    # 1. Constant background patter (white noise with filtering)
    # 2. Individual raindrop impacts at different rates/volumes
    # 3. Subtle variations over time to avoid repetition

    # Pre-calculate some elements for efficiency
    time_array = [i / sample_rate for i in range(samples)]

    # Create a more realistic rain by simulating multiple raindrops
    # and filtering white noise

    # Set up low-pass filtered noise parameters
    noise_buffer = []
    # Use a simple low-pass filter
    alpha = 0.15  # Filter constant (smaller = more filtering)
    last_value = 0

    print("Generating filtered noise...")
    # Generate filtered noise first for efficiency
    for _ in range(samples):
        # Random white noise
        noise = random.uniform(-1, 1)
        # Apply low-pass filter to smooth the noise (makes it more like rain)
        filtered = alpha * noise + (1 - alpha) * last_value
        last_value = filtered
        noise_buffer.append(filtered)

    # Track a moving average for broader filtering
    moving_avg_size = 32
    moving_avg_buffer = [0] * moving_avg_size
    moving_avg_index = 0

    # Create a base "patter" of rain by layering multiple droplet patterns
    droplet_layers = 4
    droplet_buffers = []

    print("Generating droplet layers...")
    # Create several droplet patterns with different characteristics
    for layer in range(droplet_layers):
        print(f"  Layer {layer+1}/{droplet_layers}...")
        layer_buffer = [0] * samples

        # Each layer has different droplet density and characteristics
        droplet_count = int(duration * (150 + layer * 100))  # More droplets in higher layers

        # Generate random droplets for this layer
        for _ in range(droplet_count):
            # Random position in the buffer
            pos = random.randint(0, samples - 1)

            # Random droplet characteristics
            size = random.uniform(0.01, 0.1) * (0.7 + 0.3 * layer / droplet_layers)
            decay = random.uniform(50, 200) * (1.0 + 0.5 * layer / droplet_layers)

            # Create a droplet (exponential decay from the impact point)
            for i in range(min(int(sample_rate * 0.1), samples - pos)):  # Maximum 100ms droplet
                # Exponential decay from the impact point
                amplitude = size * math.exp(-i * decay / sample_rate)

                # The sound of a droplet is a mix of filtered noise and a slight "ping"
                if i < int(sample_rate * 0.005):  # First 5ms has more "impact" sound
                    # The impact has a bit of a tone to it (higher for smaller droplets)
                    tone_freq = 2000 + random.uniform(-500, 500) * (1.0 - size * 5)
                    impact = amplitude * 1.5 * (
                        0.7 * random.uniform(-1, 1) +
                        0.3 * math.sin(2 * math.pi * tone_freq * (i / sample_rate))
                    )
                else:
                    # After the impact, it's mostly noise
                    impact = amplitude * random.uniform(-1, 1)

                # Add to the layer buffer if within bounds
                if pos + i < samples:
                    layer_buffer[pos + i] += impact

        # Apply some broader filtering to the layer
        last_value = 0
        alpha_layer = 0.1 + 0.1 * layer / droplet_layers  # Different filtering per layer

        for i in range(samples):
            layer_buffer[i] = alpha_layer * layer_buffer[i] + (1 - alpha_layer) * last_value
            last_value = layer_buffer[i]

        droplet_buffers.append(layer_buffer)

    print("Combining layers and finalizing output...")
    # Now combine all elements into the final buffer
    for i in range(samples):
        # Update moving average buffer
        moving_avg_buffer[moving_avg_index] = noise_buffer[i]
        moving_avg_index = (moving_avg_index + 1) % moving_avg_size
        moving_avg = sum(moving_avg_buffer) / moving_avg_size

        # Base background rain patter (filtered noise)
        rain_background = 0.4 * noise_buffer[i]

        # Add subtle dynamics over time
        intensity_variation = 1.0 + 0.1 * math.sin(2 * math.pi * 0.05 * time_array[i])

        # Combine droplet layers
        droplet_mix = 0
        for j, layer_buffer in enumerate(droplet_buffers):
            # Different weights for different layers
            layer_weight = 0.15 + 0.05 * j
            droplet_mix += layer_weight * layer_buffer[i]

        # Final mix: filtered background + droplet layers with dynamics
        final_mix = (
            (0.6 * rain_background + 0.4 * droplet_mix) *
            intensity_variation
        )

        # Add a subtle low-frequency rumble for depth
        rumble = 0.05 * math.sin(2 * math.pi * 30 * time_array[i]) * math.sin(2 * math.pi * 0.2 * time_array[i])
        final_mix += rumble

        # Apply overall envelope
        envelope = 1.0
        if time_array[i] < 0.5:
            # Fade in
            envelope = time_array[i] * 2
        elif time_array[i] > duration - 0.5:
            # Fade out
            envelope = (duration - time_array[i]) * 2

        # Scale to 16-bit range and apply envelope
        value = int(32767 * 0.8 * final_mix * envelope)

        # Convert to 16-bit signed PCM
        buffer[i*2] = value & 0xFF
        buffer[i*2+1] = (value >> 8) & 0xFF

    print("Rain sound generation completed!")
    return bytes(buffer)

if __name__ == "__main__":
    main()