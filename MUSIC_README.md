# Dark, Brooding Game Music

This game includes a background music system that plays a procedurally generated dark organ theme to match the game's brooding atmosphere.

## How It Works

The theme music is generated using advanced sound synthesis techniques that create a haunting, dissonant organ sound with ambient drones. The audio file is created in the `assets` directory, and the game plays this theme music on loop while you navigate through the blood rain and void.

## Sound Design

The dark theme features:
- Organ-like timbres using harmonic synthesis
- Atmospheric drones and pads for depth
- Dissonant chords that create tension
- A minor key for a somber mood
- Reverb for an echoing, distant feel
- Random elements of dissonance for an unsettling atmosphere

## Generating a New Theme

If you want to create a new variation of the dark theme:

1. Run the theme generator script:
   ```
   python create_theme.py
   ```

2. This will generate a new `theme.wav` file in the `assets` directory.

3. When you start the game, it will automatically use this new theme.

## Technical Details

- The theme uses multiple waveform types to create complex timbres:
  - Organ sounds with multiple harmonics
  - Dark pads with subtle detuning for dissonance
  - Ambient drones with slow modulation
- Advanced ADSR envelopes create natural-sounding note shapes
- Reverb effects add spatial depth to the soundscape
- Randomized elements ensure each generated theme is unique

## Future Audio Enhancements

Future work could include adding sound effects for:
- Player damage and death
- Environmental hazards
- Enemy encounters
- Portal activation and level transitions

These could be implemented by extending the AudioSystem class with additional sound playback methods.