# Isogrid Sequencer

The Isogrid Sequencer is an innovative MIDI sequencer application built with Kivy for Android. Inspired by the Make Noise René sequencer, it implements a unique "Cartesian Split" approach where X and Y axes operate independently to create complex rhythmic patterns.

## Features

- 4x4 grid sequencer with independent X and Y clock drivers
- Multiple playback modes: Forward, Backward, Pendulum, Random, Euclidean
- Real-time MIDI output for controlling external synthesizers (especially designed for Arturia MicroFreak)
- Visual feedback with crosshair highlighting active positions
- Support for Control Change (CC) automation
- Works natively on Android with USB MIDI support

## Technical Architecture

The application consists of:
- `main.py`: The Kivy UI and sequencer logic
- `midi_manager.py`: Handles MIDI communication with Android native MIDI or mock simulation
- `buildozer.spec`: Configuration for building Android APK
- `.github/workflows/build.yml`: CI/CD pipeline for automated APK building

## Development Workflow

1. **Test locally in Termux:**
   ```bash
   export DISPLAY=:0
   python main.py
   ```

2. **Push to GitHub to trigger APK build:**
   ```bash
   git add .
   git commit -m "Your changes"
   git push origin main
   ```

3. **Download APK from GitHub Actions workflow**

## MicroFreak Integration

The sequencer is optimized for the Arturia MicroFreak with predefined CC mappings:
- Cutoff: CC 23
- Resonance: CC 83
- Oscillator Type: CC 9
- Wave: CC 10
- Timbre: CC 12
- Shape: CC 13
- Glide: CC 5

## Modes

### Driver Modes
- Forward: Sequential progression
- Backward: Reverse progression
- Pendulum: Alternating direction
- Random: Random step selection
- Euclidean: Euclidean rhythm pattern

### Special Features
- Parameter Lock: Lock specific CC values to individual steps
- Wormhole Mode: Teleport between steps for glitchy effects

## Building for Android

The project uses Buildozer to package the application for Android. The build process runs automatically via GitHub Actions when changes are pushed to the repository.

## License

MIT License - See LICENSE file for details.