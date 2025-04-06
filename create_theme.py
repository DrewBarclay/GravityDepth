import wave
import math
import struct
import os
import random

def create_sine_wave(frequency, duration, sample_rate=44100, amplitude=0.5, wave_type="sine"):
    """Create a wave with the given frequency and duration"""
    n_samples = int(sample_rate * duration)
    data = []

    # Different wave shapes for different timbres
    for i in range(n_samples):
        t = i / sample_rate  # time in seconds

        if wave_type == "sine":
            # Pure sine wave
            sample = amplitude * math.sin(2 * math.pi * frequency * t)
        elif wave_type == "organ":
            # Organ-like timbre (fundamental + harmonics)
            # Base fundamental
            sample = amplitude * 0.7 * math.sin(2 * math.pi * frequency * t)
            # First harmonic (octave) with reduced amplitude
            sample += amplitude * 0.3 * math.sin(2 * math.pi * frequency * 2 * t)
            # Second harmonic with even less amplitude
            sample += amplitude * 0.1 * math.sin(2 * math.pi * frequency * 3 * t)
            # Some sub-harmonic for depth
            sample += amplitude * 0.1 * math.sin(2 * math.pi * frequency * 0.5 * t)
        elif wave_type == "dark_pad":
            # Darker pad sound with detuned oscillators
            # Main tone
            sample = amplitude * 0.5 * math.sin(2 * math.pi * frequency * t)
            # Slightly detuned for dissonance
            sample += amplitude * 0.3 * math.sin(2 * math.pi * (frequency * 1.01) * t)
            # Lower octave for depth
            sample += amplitude * 0.4 * math.sin(2 * math.pi * (frequency * 0.5) * t)
            # Add some subtle distortion
            if sample > 0.8 * amplitude:
                sample = 0.8 * amplitude + (sample - 0.8 * amplitude) * 0.5
            elif sample < -0.8 * amplitude:
                sample = -0.8 * amplitude + (sample + 0.8 * amplitude) * 0.5

        # Avoid clipping
        sample = max(min(sample, 1.0), -1.0)
        data.append(sample)

    return data

def create_note(note_freq, duration, sample_rate=44100, amplitude=0.5, wave_type="sine"):
    """Create a note with the given frequency, duration and timbre"""
    # Create the main tone
    samples = create_sine_wave(note_freq, duration, sample_rate, amplitude, wave_type)

    # Add a simple envelope (attack, decay, sustain, release)
    attack_duration = min(0.1, duration / 5)
    attack_samples = int(attack_duration * sample_rate)

    decay_duration = min(0.15, duration / 4)
    decay_samples = int(decay_duration * sample_rate)

    release_duration = min(0.2, duration / 3)
    release_samples = int(release_duration * sample_rate)

    sustain_level = 0.7  # Sustain level (percentage of peak amplitude)

    # Apply attack (fade in)
    for i in range(min(attack_samples, len(samples))):
        samples[i] *= i / attack_samples

    # Apply decay (to sustain level)
    decay_start = attack_samples
    decay_end = decay_start + decay_samples
    for i in range(decay_start, min(decay_end, len(samples))):
        decay_progress = (i - decay_start) / decay_samples
        samples[i] *= 1.0 - ((1.0 - sustain_level) * decay_progress)

    # Apply release (fade out)
    release_start = len(samples) - release_samples
    for i in range(max(0, release_start), len(samples)):
        release_progress = (i - release_start) / release_samples
        samples[i] *= 1.0 - release_progress

    return samples

def create_dissonant_chord(base_freq, duration, sample_rate=44100, amplitude=0.3):
    """Create a dissonant chord based on a base frequency"""
    # Base note
    samples = create_note(base_freq, duration, sample_rate, amplitude, "organ")

    # Add dissonant intervals - minor 2nd and tritone
    samples2 = create_note(base_freq * 1.05, duration, sample_rate, amplitude * 0.6, "dark_pad")
    samples3 = create_note(base_freq * 1.414, duration, sample_rate, amplitude * 0.5, "organ")

    # Mix the samples
    result = []
    for i in range(min(len(samples), len(samples2), len(samples3))):
        result.append(samples[i] + samples2[i] + samples3[i])

    return result

def add_reverb(samples, sample_rate, reverb_time=1.0, delay=0.1, decay=0.5):
    """Add a simple reverb effect to the samples"""
    delay_samples = int(delay * sample_rate)
    result = samples.copy()

    # Multiple delayed echoes with decay
    for i in range(len(samples)):
        # Skip if too early for reverb
        if i < delay_samples:
            continue

        # Add decayed version of earlier sample
        result[i] += samples[i - delay_samples] * decay

    # Normalize to avoid clipping
    max_val = max(abs(s) for s in result)
    if max_val > 1.0:
        result = [s / max_val for s in result]

    return result

def create_ambient_drone(freq, duration, sample_rate=44100, amplitude=0.3):
    """Create an ambient drone sound"""
    samples = create_sine_wave(freq, duration, sample_rate, amplitude, "dark_pad")

    # Add subtle modulation for movement
    modulation_freq = 0.5  # 0.5 Hz (slow modulation)
    modulation_depth = 0.1

    for i in range(len(samples)):
        t = i / sample_rate
        mod = modulation_depth * math.sin(2 * math.pi * modulation_freq * t)
        samples[i] *= (1.0 + mod)

    return samples

def create_brooding_theme():
    """Create a dark, brooding theme song"""
    sample_rate = 44100
    output_file = os.path.join("assets", "theme.wav")

    # Define musical notes in a minor scale
    # A minor: A, B, C, D, E, F, G
    # Frequencies: A3=220Hz, C4=261.63Hz, D4=293.66Hz, E4=329.63Hz, G4=392Hz
    A3 = 220.00
    C4 = 261.63
    D4 = 293.66
    E4 = 329.63
    F4 = 349.23
    G4 = 392.00

    # Dark organ theme in A minor with longer, sustained notes
    melody = [
        (A3, 1.2, "organ"),       # A3 - long, establishing the root
        (C4, 0.8, "organ"),       # C4 - minor third, establishing the mood
        (E4, 1.0, "organ"),       # E4 - creating a minor chord

        (D4, 0.7, "dark_pad"),    # D4 - creating tension
        (C4, 0.7, "dark_pad"),    # C4 - resolving slightly
        (A3, 1.4, "organ"),       # A3 - back to root

        (F4, 0.9, "dark_pad"),    # F4 - adding darkness
        (E4, 0.9, "dark_pad"),    # E4 - slight resolution
        (C4, 0.9, "organ"),       # C4 - furthering the resolution
        (D4, 1.2, "organ"),       # D4 - tension

        (A3, 1.0, "organ"),       # A3 - final resolution to root
        (A3 * 0.5, 2.0, "organ"), # A2 - octave down, final dark note
    ]

    # Atmospheric drones and pads for background
    drone_a = create_ambient_drone(A3 * 0.5, sum(d for _, d, _ in melody), sample_rate, 0.1)

    # Build the main melody with organ-like sounds
    melody_samples = []
    for freq, duration, wave_type in melody:
        # Add some randomness to durations for a more human feel
        actual_duration = duration * random.uniform(0.95, 1.05)

        # Create the note with the specified timbre
        note_samples = create_note(freq, actual_duration, sample_rate, 0.4, wave_type)

        # Add some dissonance for certain notes
        if random.random() < 0.3:  # 30% chance of dissonance
            dissonant_samples = create_dissonant_chord(freq, actual_duration, sample_rate, 0.2)
            # Mix with the main note
            for i in range(min(len(note_samples), len(dissonant_samples))):
                note_samples[i] = note_samples[i] * 0.7 + dissonant_samples[i] * 0.3

        melody_samples.extend(note_samples)

    # Add the drone as a background layer
    combined_samples = []
    for i in range(min(len(melody_samples), len(drone_a))):
        combined_samples.append(melody_samples[i] + drone_a[i])

    # Add reverb for atmosphere
    reverb_samples = add_reverb(combined_samples, sample_rate, 2.0, 0.15, 0.4)

    # Create space for repeating the theme
    full_theme = reverb_samples * 2

    # Normalize samples to stay within (-32767, 32767)
    max_amplitude = max(abs(sample) for sample in full_theme)
    normalizer = 32767 / max_amplitude
    normalized_samples = [int(sample * normalizer) for sample in full_theme]

    # Write to WAV file
    with wave.open(output_file, 'w') as wf:
        wf.setnchannels(1)  # Mono
        wf.setsampwidth(2)  # 2 bytes (16 bits) per sample
        wf.setframerate(sample_rate)

        # Convert samples to binary data
        for sample in normalized_samples:
            wf.writeframes(struct.pack('h', sample))

    print(f"Created dark, brooding theme at {output_file}")

if __name__ == "__main__":
    os.makedirs("assets", exist_ok=True)
    create_brooding_theme()